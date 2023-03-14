from django.http import JsonResponse
from rest_framework.decorators import api_view
from login_register_app.models import User
from user_details_app.models import UserRowingInfo, UserProfilePicture, UserPersonalBests
from login_register_app.serializers import UserDashboardSerializer
from user_details_app.serializers import ProfilePictureSerializer, PersonalBestsSerializer, AthleteDetailsSerializer
from get_dropdown_data_app.models import RaceCategory
from get_dropdown_data_app.serializers import RaceCategorySerializer
from user_details_app.views import get_jwt_token_user_id, get_user_age
import datetime, mimetypes, base64
from datetime import timedelta

# ------------------------------ User Dashboard Details ------------------------------

@api_view(['POST'])
def get_user_details(request):
    # get user_id from jwt token
    user_id = get_jwt_token_user_id(request)

    user_object = User.objects.filter(user_id = user_id).values('email', 'first_name', 'last_name', 'date_of_birth').first()
    user = UserDashboardSerializer(user_object)

    # determine age from date of birth
    date_object = datetime.datetime.strptime(user.data['date_of_birth'], '%Y-%m-%d')
    age = get_user_age(date_object)

    athlete_object = UserRowingInfo.objects.filter(user_id = user_id).values('height', 'weight', 'wingspan', 'clubs', 'coaches', 'race_category').first()

    athlete = AthleteDetailsSerializer(athlete_object)

    race_category_object = RaceCategory.objects.filter(category = athlete.data['race_category']).values('category', 'category_nickname').first()

    race_category = RaceCategorySerializer(race_category_object)

    # manipulate values
    full_name = user.data['first_name'] + ' ' + user.data['last_name']
    converted_date = str(date_object.day) + '/' + str(date_object.month) + '/' + str(date_object.year)
    age_dob = str(age) + ' (' + converted_date + ')'
    height = athlete.data['height'] + ' cm'
    weight = athlete.data['weight'] + ' kg'
    wingspan = athlete.data['wingspan'] + ' cm'

    return JsonResponse({
        'fullName': full_name,
        'ageDob': age_dob,
        'height': height,
        'weight': weight,
        'wingspan': wingspan,
        'clubs': athlete.data['clubs'],
        'coaches': athlete.data['coaches'],
        'raceCategory': race_category.data['category_nickname']
    })

# ------------------------------ Profile Picture ------------------------------

@api_view(['POST'])
def get_user_picture(request):
    # get user_id from jwt token
    user_id = get_jwt_token_user_id(request)

    profile_picture_object = UserProfilePicture.objects.filter(user_id = user_id).first()

    image_data = profile_picture_object.profile_picture.read()
    content_type = mimetypes.guess_type(profile_picture_object.profile_picture.name)[0]

    base64_encoded = base64.b64encode(image_data).decode('utf-8')

    return JsonResponse({
        'imageData': base64_encoded,
        'contentType': content_type,
    })

# ------------------------------ Personal Bests ------------------------------

@api_view(['POST'])
def get_personal_bests(request):
    #get user_id from JWT token
    user_id = get_jwt_token_user_id(request)

    personal_bests_object = UserPersonalBests.objects.filter(user_id = user_id).first()

    personal_bests = PersonalBestsSerializer(personal_bests_object)

    results = []

    for key, value in personal_bests.data.items():
        distance = int(key.split('_')[1])
        
        # parse string into hours, minutes, seconds
        time_segments = value.split(':')
        
        hours = int(time_segments[0])
        minutes = int(time_segments[1])
        seconds = float(time_segments[2])

        # convert to seconds
        total_seconds = (hours * 3600) + (minutes * 60) + seconds

        split = calculate_split(distance, total_seconds)

        # format value to round to 1 decimal point
        if '.' in value:
            time_object = datetime.datetime.strptime(value, "%H:%M:%S.%f").time()
            rounded_milliseconds = int(round(time_object.microsecond / 100000.0, 1))
            time = time_object.strftime('%H:%M:%S')
            value = f'{time}.{rounded_milliseconds:1}'
        else:
            value = f'{value}.0'

        results.append({
            'time': value,
            'split': split
        })
    
    print(results)

    return JsonResponse({
        'pb100': results[0],
        'pb500': results[1],
        'pb1000': results[2],
        'pb2000': results[3],
        'pb6000': results[4],
        'pb10000': results[5]
    })

# ------------------------------ Helper Functions ------------------------------

def calculate_split(distance, time_in_seconds):

    split_in_seconds = 0

    if (not time_in_seconds == 0) and distance == 100:
        split_in_seconds = time_in_seconds * 5
    elif not time_in_seconds == 0:
        split_in_seconds = get_split_in_seconds(distance, time_in_seconds)
    else:
        return '00:00.0'
    
    minutes, seconds = get_minutes_and_seconds(split_in_seconds)
    return format_time(minutes, seconds)

def get_split_in_seconds(distance, time_in_seconds):
    return 500 / (distance / time_in_seconds)
        
def get_minutes_and_seconds(time_in_seconds):
    # get number of minutes
    minutes = int(time_in_seconds // 60)

    # get number of seconds
    seconds = round(time_in_seconds - (minutes * 60), 1)

    return minutes, seconds

def format_time(minutes, seconds):
    if minutes < 10:
        if seconds < 10:
            return f'0{minutes}:0{seconds}'
        else:
            return f'0{minutes}:{seconds}'
    else:
        if seconds < 10:
            return f'{minutes}:0{seconds}'
        else:
            return f'{minutes}:{seconds}'