from django.http import JsonResponse
from rest_framework.decorators import api_view
from login_register_app.models import User
from user_details_app.models import UserRowingInfo, UserProfilePicture, UserPersonalBests
from login_register_app.serializers import UserDashboardSerializer, UserDetailsModalSerializer
from user_details_app.serializers import PersonalBestsSerializer, AthleteDetailsSerializer
from get_dropdown_data_app.models import RaceCategory
from get_dropdown_data_app.serializers import RaceCategorySerializer
from user_details_app.views import get_jwt_token_user_id, get_user_age
import datetime, mimetypes, base64, math
import numpy as np
import scipy.stats as stats
from scipy.stats import norm

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
    height = ''
    weight = ''
    wingspan = ''
    clubs = []
    coaches = []
    category = ''

    if athlete.data['height'] != None:
        height = athlete.data['height'] + ' cm'

    if athlete.data['weight'] != None:
        weight = athlete.data['weight'] + ' kg'

    if athlete.data['wingspan'] != None:
        wingspan = athlete.data['wingspan'] + ' cm'

    if athlete.data['clubs'] != None:
        clubs = athlete.data['clubs']
    
    if athlete.data['coaches'] != None:
        coaches = athlete.data['coaches']
    
    if race_category.data['category_nickname'] != None:
        category = race_category.data['category_nickname']

    return JsonResponse({
        'fullName': full_name,
        'ageDob': age_dob,
        'height': height,
        'weight': weight,
        'wingspan': wingspan,
        'clubs': clubs,
        'coaches': coaches,
        'raceCategory': category
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
        
        if value != None:
            # parse string into hours, minutes, seconds
            time_segments = value.split(':')
            
            hours = int(time_segments[0])
            minutes = int(time_segments[1])
            seconds = float(time_segments[2])

            # convert to seconds
            total_seconds = (hours * 3600) + (minutes * 60) + seconds

            split = calculate_split(distance, total_seconds)

            # format value to round to 1 decimal point
            results.append(adjust_decimal_places(value, split))
        else:
            results.append({
                'time': '00:00:00.0',
                'split': '00:00.0'
            })
        

    return JsonResponse({
        'pb100': results[0],
        'pb500': results[1],
        'pb1000': results[2],
        'pb2000': results[3],
        'pb6000': results[4],
        'pb10000': results[5]
    })

# ------------------------------ Personal Best Percentiles ------------------------------

@api_view(['POST'])
def calculate_pb_rating(request):
    my_user_id = get_jwt_token_user_id(request)

    # get the race category for the athlete
    athlete_details_object = UserRowingInfo.objects.filter(user_id = my_user_id).values('race_category').first()
    athlete_race_category = AthleteDetailsSerializer(athlete_details_object).data['race_category']

    users_id_objects = UserRowingInfo.objects.filter(race_category = athlete_race_category).all()

    # all the athletes in the race category of the user
    athletes = AthleteDetailsSerializer(users_id_objects, many = True).data

    all_pbs = []
    my_personal_bests = {}

    for athlete in athletes:
        user_id = athlete['user_id']

        personal_bests_object = UserPersonalBests.objects.filter(user_id = user_id).first()
        personal_best = PersonalBestsSerializer(personal_bests_object).data
        all_pbs.append(personal_best)

        if user_id == my_user_id:
            my_personal_bests['pb_times'] = personal_best

    time_keys = []

    for key, _ in my_personal_bests['pb_times'].items():
        time_keys.append(key)
    
    means, my_ratings = calculate_user_ratings(all_pbs, my_personal_bests['pb_times'], time_keys)

    return JsonResponse({
        'myPBRatings': my_ratings,
    })

# ------------------------------ Populate Details Modal ------------------------------

@api_view(['POST'])
def populate_details_modal(request):
    my_user_id = get_jwt_token_user_id(request)

    user_details_object = User.objects.get(user_id = my_user_id)
    athletic_details_objects = UserRowingInfo.objects.get(user_id = my_user_id)

    user_details = UserDetailsModalSerializer(user_details_object)
    athletic_details = AthleteDetailsSerializer(athletic_details_objects)

    first_name = user_details.data['first_name']
    last_name = user_details.data['last_name']
    dob = user_details.data['date_of_birth']
    gender = user_details.data['gender']
    is_athlete = user_details.data['is_athlete']
    is_coach = user_details.data['is_coach']
    phone_number = user_details.data['phone_number']
    athlete_or_coach = ''

    if is_athlete == True and is_coach == False:
        athlete_or_coach = 'Athlete'
    elif is_athlete == False and is_coach == True:
        athlete_or_coach = 'Coach'
    else:
        athlete_or_coach = 'Both'

    clubs = athletic_details.data['clubs']
    coaches = athletic_details.data['coaches']
    race_category = athletic_details.data['race_category']
    weight = athletic_details.data['weight']
    height = athletic_details.data['height']
    wingspan = athletic_details.data['wingspan']


    return JsonResponse({
        'firstName': first_name,
        'lastName': last_name,
        'dateOfBirth': dob,
        'gender': gender,
        'phoneNumber': phone_number,
        'athleteOrCoach': athlete_or_coach,
        'clubs': clubs,
        'coaches': coaches,
        'raceCategory': race_category,
        'weight': weight,
        'height': height,
        'wingspan': wingspan
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

def adjust_decimal_places(value, split):
    if '.' in value:
        time_object = datetime.datetime.strptime(value, "%H:%M:%S.%f").time()
        rounded_milliseconds = int(round(time_object.microsecond / 100000.0, 1))
        time = time_object.strftime('%H:%M:%S')
        value = f'{time}.{rounded_milliseconds:1}'
    else:
        value = f'{value}.0'

    return {
        'time': value,
        'split': split
    }

def get_time_in_seconds(time):
    time_segments = time.split(':')

    hours = int(time_segments[0])
    minutes = int(time_segments[1])
    seconds = float(time_segments[2])

    return (hours * 3600) + (minutes * 60) + seconds

def calculate_user_ratings(all_pbs, my_pbs, time_categories):
    # z = (X – μ) / σ
    # X = a single data point, μ = mean and σ = standard deviation

    means = []
    my_ratings = []
    all_personal_bests = []

    for set_of_pbs in all_pbs:
        all_personal_bests.append({k: v for k, v in set_of_pbs.items() if v != '00:00:00'})

    # loop through for the number of time categories to get
    for i in range(len(time_categories)):
        time_category = time_categories[i]

        new_time_list = []
        my_data_index = None
        my_time = None

        for i, pb_times in enumerate(all_personal_bests):
            if time_category in pb_times:
                pb_time = pb_times[time_category]
                user_time = my_pbs[time_category]
                
                if pb_time != None and user_time != None:
                    time = get_time_in_seconds(pb_time)
                    my_time = get_time_in_seconds(user_time)
                    new_time_list.append(time)

        # calculate my_index
        if my_time != None and my_time != '00:00:00':
            for i, time in enumerate(new_time_list):
                if my_data_index == None and time == my_time:
                    my_data_index = i

        # calculate mean and standard deviation
        mean = np.mean(new_time_list)
        
        data = np.array(new_time_list)
        
        z_scores = stats.zscore(data)

        # as we're dealing with times, and less is more, we need to reverse the z scores
        reversed_z_scores = [round(-z, 2) for z in z_scores]

        percentiles = [round(norm.cdf(z), 2) * 100 if not math.isnan(z) else 0 for z in reversed_z_scores]

        percentile = 0

        for i, _ in enumerate(percentiles):
            if my_data_index != None and i == my_data_index:
                percentile = percentiles[i]

        means.append(round(mean, 2))
        my_ratings.append(str(int(percentile)))

    return means, my_ratings