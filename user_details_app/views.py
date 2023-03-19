from rest_framework.decorators import api_view, parser_classes
from django.http import JsonResponse
from .models import UserRowingInfo, UserPersonalBests, UserProfilePicture
from login_register_app.models import User
from .serializers import CoreDetailsSerializer, AthleteDetailsSerializer, PersonalBestsSerializer, ProfilePictureSerializer
import re, datetime, jwt, os
from django.shortcuts import get_object_or_404
from get_dropdown_data_app.models import RaceCategory
from get_dropdown_data_app.serializers import RaceCategorySerializer
from dotenv import load_dotenv
from rest_framework.parsers import MultiPartParser, FormParser

# load .env file to access variables
load_dotenv()
jwt_secret_key = os.getenv('JWT_SECRET_KEY')

# ------------------------------ User Details ------------------------------

@api_view(['POST'])
def core_details(request):
    # serialize data
    serializer = CoreDetailsSerializer(data = request.data)

    user_id = None
    error_message = ''
    culprit = ''

    if serializer.is_valid():
        data = serializer.validated_data

        first_name = data['first_name']
        last_name = data['last_name']
        date_of_birth = data['date_of_birth']
        gender = data['gender']
        phone_number = data['phone_number']
        athlete_or_coach = data['athlete_or_coach']
        is_athlete = data['is_athlete']
        is_coach = data['is_coach']

        # adjust default values to prevent incorrect value stored
        if athlete_or_coach == 'Coach' and is_coach == False:
            is_coach = True
            is_athlete = False
        elif athlete_or_coach == 'Both' and is_coach == False:
            is_coach = True

        # validate first_name and last_name

        # regex pattern to ensure only letters, or valid special characters ['-]
        name_pattern = re.compile(r'^[a-zA-Z\' -]+$')

        if not re.match(name_pattern, first_name):
            error_message = 'Invalid First Name'
            culprit = 'firstName'
        elif not re.match(name_pattern, last_name):
            error_message = 'Invalid Last Name'
            culprit = 'lastName'

        # implement validation
        date_of_birth = datetime.datetime.strptime(date_of_birth, '%d/%m/%Y').date()

        # validate gender
        if not gender in ['Male', 'Female']:
            error_message = 'Invalid Gender'
            culprit = 'gender'

        # validate phone_number

        # (ASCII) 32 = space, 40 = (, 41 = ), 43 = +, 45 = -
        removable_chars = {32: None, 40: None, 41: None, 43: None, 45: None}
        phone_number = phone_number.translate(removable_chars)

        if not (phone_number.isdigit() and len(phone_number) in [9, 10]):
            error_message = 'Invalid Phone Number'
            culprit = 'phoneNumber'
    else:
        print(serializer.errors)

    # get token
    user_id = get_jwt_token_user_id(request)
    
    # use token to update user if errorMessage and culprit = ''
    if error_message == '' and culprit == '' and user_id != None:
        # use user_id to update existing entry in the database
        user = get_object_or_404(User, user_id = user_id)

        #update
        user.first_name = first_name
        user.last_name = last_name
        user.date_of_birth = date_of_birth
        user.gender = gender
        user.phone_number = phone_number
        user.is_athlete = is_athlete
        user.is_coach = is_coach

        # save
        user.save()
    
    return JsonResponse({
        'errorMessage': error_message,
        'culprit':culprit,
        'isAthlete': is_athlete,
    })

# ------------------------------ Athlete Details ------------------------------

@api_view(['POST'])
def athlete_details(request):
    # serialize data
    serializer = AthleteDetailsSerializer(data = request.data)

    user_id = None
    error_message = ''
    culprit = ''

    if serializer.is_valid():
        data = serializer.validated_data

        race_category = data['race_category']
        clubs = data['clubs']
        coaches = data['coaches']
        height = float(data['height'])
        weight = float(data['weight'])
        wingspan = float(data['wingspan'])

        # verify that height, weight and wingspan are not less than zero
        error_message, culprit = less_than_zero(height, 'height', error_message, culprit)
        error_message, culprit = less_than_zero(weight, 'weight', error_message, culprit)
        error_message, culprit = less_than_zero(wingspan, 'wingspan', error_message, culprit)

        # get race category max_weight, max_age and required_gender
        category_object = RaceCategory.objects.filter(category=race_category).first()
        serializer = RaceCategorySerializer(category_object)

        max_weight = convert_none_to_99(serializer.data['max_weight'])
        max_age = convert_none_to_99(serializer.data['max_age'])
        required_gender = serializer.data['required_gender']

        # get User with user_id from JWT token
        user_id = get_jwt_token_user_id(request)

        # get user
        user = get_object_or_404(User, user_id = user_id)

        user_age = get_user_age(user.date_of_birth)
        user_gender = user.gender 

        if user_age > max_age or user_gender != required_gender or  weight > max_weight:
            error_message = 'Entry forbidden'
            culprit = 'race category'
        
        if error_message == '' and culprit == '' and user_id != None:
            # save to database
            UserRowingInfo.objects.create(user = user, race_category = race_category, clubs = clubs, coaches = coaches, height = height, weight = weight, wingspan = wingspan)

    else:
        print(serializer.errors)


    return JsonResponse({
        'errorMessage': error_message,
        'culprit': culprit
    })

# ------------------------------ Personal Bests ------------------------------

@api_view(['POST'])
def personal_bests(request):
    serializer = PersonalBestsSerializer(data = request.data)

    user_id = None
    error_message = ''
    culprit = ''

    if serializer.is_valid():
        data = serializer.validated_data
        
        pb_100 = data['pb_100']
        pb_500 = data['pb_500']
        pb_1000 = data['pb_1000']
        pb_2000 = data['pb_2000']
        pb_6000 = data['pb_6000']
        pb_10000 = data['pb_10000']

        user_id = get_jwt_token_user_id(request)

        # get user
        user = get_object_or_404(User, user_id = user_id)

        # create new entry in database
        # values stored as timedelta objects that will need to be parsed to display
        UserPersonalBests.objects.create(user = user, pb_100 = pb_100, pb_500 = pb_500, pb_1000 = pb_1000, pb_2000 = pb_2000, pb_6000 = pb_6000, pb_10000 = pb_10000)

    else:
        error = serializer.errors

        error_message = 'Invalid time'

        culprit_list = (list(error.keys())[0]).split('_')
        culprit = f'{culprit_list[0]} {culprit_list[1]}'

        print(serializer.errors)

    return JsonResponse({
        'errorMessage': error_message,
        'culprit': culprit
    })

# ------------------------------ Profile Picture ------------------------------

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def update_profile_picture(request):
    
    profile_picture_file = request.FILES.get('profile_picture')
    file_name = profile_picture_file.name
    content_type = profile_picture_file.content_type
    allowed_content_types = ['image/bmp', 'image/gif', 'image/tiff', 'image/jpeg', 'image/png']

    if content_type in allowed_content_types:
        file_extension = content_type.split('/')[1]
        profile_picture_file.name = file_name + '.' + file_extension

    serializer = ProfilePictureSerializer(data = request.data)

    user_id = None
    error_message = ''
    culprit = ''

    if serializer.is_valid():
        profile_picture = request.FILES.get('profile_picture')

        # get User with user_id from JWT token
        user_id = get_jwt_token_user_id(request)

        # get user
        user = get_object_or_404(User, user_id=user_id)

        # save to database
        user_profile_picture = UserProfilePicture.objects.create(user=user, profile_picture=profile_picture)
    else:
        print(serializer.errors)

    return JsonResponse({
        'errorMessage': error_message,
        'culprit': culprit,
    })



# ------------------------------ Helper Functions ------------------------------

def less_than_zero(value, rep, errorMessage, culprit):
    if value < 0:
        errorMessage = 'Cannot be less than 0'
        culprit = rep
    
    return [errorMessage, culprit]

def get_jwt_token_user_id(request):
    # get JWT token
    token = ''
    auth_header = request.headers.get('Authorization')

    # verify existence of JWT token
    if auth_header:
        token = auth_header.split(' ')[1]
    else:
        return JsonResponse({
            'error': 'JWT token not found'
        }, status = 401)
    
    # decode token to extract user id
    if token:
        try:
            decoded_token = jwt.decode(token, jwt_secret_key, algorithms=['HS256'])
            user_id = decoded_token['id']
            return user_id
        except jwt.ExpiredSignatureError:
            return JsonResponse({
                'error': 'token has expired'
            }, status = 401)
        except jwt.InvalidTokenError:
            return JsonResponse({
                'error': 'invalid token'
            }, status = 401)

def get_user_age(date):
    today = datetime.date.today()
    age = today.year - date.year - ((today.month, today.day) < (date.month, date.day))
    return age

def convert_none_to_99(value):
    if value is None:
        value = 99
    return value
