from rest_framework.decorators import api_view
from django.http import JsonResponse
from .models import UserErgMetrics, UserSAndCMetrics
from login_register_app.models import User
from .serializers import ErgMetricsSerializer, SAndCMetricsSerializer
import re, datetime, jwt, os
from django.shortcuts import get_object_or_404
from user_details_app.views import get_jwt_token_user_id
from dotenv import load_dotenv

# load .env file to access variables
load_dotenv()
jwt_secret_key = os.getenv('JWT_SECRET_KEY')

# ------------------------------ Add Erg Metric Data ------------------------------

@api_view(['POST'])
def add_erg_metric(request):
    serializer = ErgMetricsSerializer(data = request.data)

    user_id = None
    error_message = ''
    culprit = ''

    if serializer.is_valid():
        # get jwt token
        user_id = get_jwt_token_user_id(request)

        data = serializer.validated_data

        distance = data['distance']
        strokes_per_minute = data['strokes_per_minute']
        split_500m = data['split_500m']
        time = data['time']

        if not distance in ['100m', '500m', '1000m', '2000m', '6000m', '10000m']:
            error_message = 'Invalid distance'
            culprit = 'distance'

        if not strokes_per_minute:
            error_message = 'No s/m provided'
            culprit = 'strokesPerMinute'
        
        if not split_500m:
            error_message = 'No split provided'
            culprit = 'split500m'
        
        if not time:
            error_message = 'No time provided'
            culprit = 'time'
        
        if error_message == '' and culprit == '':
            # get user
            user = get_object_or_404(User, user_id = user_id)

            # create new entry in database
            UserErgMetrics.objects.create(user = user, distance = distance, strokes_per_minute = strokes_per_minute, split_500m = split_500m, time = time)
    else:
        print(serializer.errors)
            
    return JsonResponse({
        'errorMessage': error_message,
        'culprit': culprit
    })



# ------------------------------ Add S&C Metric Data ------------------------------

@api_view(['POST'])
def add_s_and_c_metric(request):
    serializer = SAndCMetricsSerializer(data = request.data)

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
            user = get_object_or_404(User, user_id = user_id)

            # create new entry in database
            UserSAndCMetrics.objects.create(user = user, exercise = exercise, weight = weight, reps = reps)


    else:
        print(serializer.errors)

    return JsonResponse({
        'errorMessage': error_message,
        'culprit': culprit
    })