from rest_framework.decorators import api_view
from django.http import JsonResponse
from .models import UserErgMetrics, UserSAndCMetrics
from login_register_app.models import User
from .serializers import ErgMetricsSerializer, SAndCMetricsSerializer
import os
from django.shortcuts import get_object_or_404
from user_details_app.views import get_jwt_token_user_id
from dotenv import load_dotenv
from populate_dashboard_app.views import calculate_split, adjust_decimal_places
from user_details_app.models import UserPersonalBests
from user_details_app.serializers import PersonalBestsSerializer
from populate_dashboard_app.views import get_time_in_seconds

# load .env file to access variables
load_dotenv()
jwt_secret_key = os.getenv('JWT_SECRET_KEY')

# ------------------------------ Add Erg Metric Data ------------------------------


@api_view(['POST'])
def add_erg_metric(request):
    serializer = ErgMetricsSerializer(data=request.data)

    user_id = None
    error_message = ''
    culprit = ''

    if serializer.is_valid():
        # get jwt token
        user_id = get_jwt_token_user_id(request)

        data = serializer.validated_data

        distance = data['distance']
        strokes_per_minute = data['strokes_per_minute']
        time = data['time']

        if not distance in ['100m', '500m', '1000m', '2000m', '6000m', '10000m']:
            error_message = 'Invalid distance'
            culprit = 'distance'

        if not strokes_per_minute:
            error_message = 'No s/m provided'
            culprit = 'strokesPerMinute'

        if not time:
            error_message = 'No time provided'
            culprit = 'time'

        if error_message == '' and culprit == '':
            # get user
            user = get_object_or_404(User, user_id=user_id)

            # parse string into hours, minutes, seconds
            total_seconds = get_time_in_seconds(time)

            # check if faster than pb
            updated_distance = f"pb_{distance.replace('m', '')}"

            personal_best_object = UserPersonalBests.objects.filter(
                user_id=user.user_id).first()

            personal_best = PersonalBestsSerializer(personal_best_object)

            pb_in_seconds = get_time_in_seconds(
                personal_best.data[updated_distance])

            # add to database
            formatted_values = add_erg_data(
                distance, total_seconds, time, user, strokes_per_minute, pb_in_seconds)

            if pb_in_seconds > total_seconds or pb_in_seconds == 0:
                setattr(personal_best_object, updated_distance,
                        formatted_values['time'])
                serializer = PersonalBestsSerializer(personal_best_object)
                personal_best_object.save()

    else:
        print(serializer.errors)

    return JsonResponse({
        'errorMessage': error_message,
        'culprit': culprit
    })


# ------------------------------ Add S&C Metric Data ------------------------------

@api_view(['POST'])
def add_s_and_c_metric(request):
    serializer = SAndCMetricsSerializer(data=request.data)

    user_id = None
    error_message = ''
    culprit = ''

    for key, value in request.data.items():
        if not value:
            key = key.replace('_',  ' ')

            error_message = f'Missing {key}'
            culprit = key

            return JsonResponse({
                'errorMessage': error_message,
                'culprit': culprit
            })

    if serializer.is_valid():
        # get jwt token
        user_id = get_jwt_token_user_id(request)

        data = serializer.validated_data

        exercise = data['exercise']
        weight = int(data['weight'])
        reps = int(data['reps'])
        exercise_list = data['exercise_list']

        # fallback -> shouldn't be necessary
        if len(exercise_list) <= 0:
            exercise_list = ['Bench Press', 'Bicep Curl', 'Deadlift', 'Squat']

        if exercise not in exercise_list:
            error_message = 'Invalid exercise'
            culprit = exercise

        if not weight:
            error_message = 'No weight provided'
            culprit = 'weight'

        if not reps:
            error_message = 'No reps provided'
            culprit = 'reps'

        if error_message == '' and culprit == '':
            # get user
            user = get_object_or_404(User, user_id=user_id)

            # create new entry in database
            UserSAndCMetrics.objects.create(
                user=user, exercise=exercise.lower(), weight=weight, reps=reps)

    else:
        print(serializer.errors)

    return JsonResponse({
        'errorMessage': error_message,
        'culprit': culprit
    })

# ------------------------------ Helper Functions ------------------------------

def add_erg_data(distance, total_seconds, time, user, strokes_per_minute, pb_in_seconds):
    # convert distance to number
    new_distance = distance.replace('m', '')

    # calculate split
    split = calculate_split(float(new_distance), total_seconds)

    # format
    formatted_values = adjust_decimal_places(time, split)

    # generate intensity metric for the period that the session occurs

    # calculate wattage generated from personal best 500m split
    pb_split = calculate_split(float(new_distance), pb_in_seconds)

    pb_watts = calculate_watts(convert_to_seconds(pb_split))
    session_watts = calculate_watts(convert_to_seconds(split))

    intensity = 0

    if pb_watts != 0:
        intensity = int((session_watts / pb_watts) * 100)
    else:
        intensity = 100

    # create new entry in database
    UserErgMetrics.objects.create(user=user, distance=distance, strokes_per_minute=strokes_per_minute,
                                  split_500m=formatted_values['split'], time=formatted_values['time'], time_in_seconds=total_seconds, intensity_percentage=intensity)

    return formatted_values


def calculate_watts(split):
    if split != 0:
        return 2.8 / (split ** 3)
    else:
        return 0


def convert_to_seconds(time):
    time_segments = time.split(':')

    minutes = int(time_segments[0])
    seconds = float(time_segments[1])

    return (minutes * 60) + seconds
