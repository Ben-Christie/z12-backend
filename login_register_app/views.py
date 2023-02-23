from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import get_user_model
from .models import User, UserRowingInfo
from .serializers import RegisterSerializer, LoginSerializer, CoreDetailsSerializer, AthleteDetailsSerializer
import re, datetime, jwt, os
from dotenv import load_dotenv
from django.shortcuts import get_object_or_404
from get_dropdown_data_app.models import ClubInfo, RaceCategory
from get_dropdown_data_app.serializers import RaceCategorySerializer

# load .env file to access variables
load_dotenv()
jwt_secret_key = os.getenv('JWT_SECRET_KEY')

User = get_user_model()

# ------------------------------ Create New Account ------------------------------

@api_view(['POST'])
def create_login(request):
    # parse json
    serializer = RegisterSerializer(data = request.data)
    
    email_is_valid = False;
    password_is_valid = False;
    error = '';
    token = '';

    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        confirm_password = serializer.validated_data['confirm_password']

        # verify email does not already exist in the database
        if User.objects.filter(email = email).exists():
            error = 'email already exists'
        else:
            email_is_valid = True

        # password must be at least 8 characters and contain digit 0 - 9, Uppercase, Lowercase and Special
        # character from list (#?!@$%^&*-)
        password_validation_pattern = re.compile('^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$')

        # compare password to confirm password and regex pattern
        if password == confirm_password and re.match(password_validation_pattern, password):
            password_is_valid = True
        elif password == confirm_password:
            error = 'password is not valid, must contain at least one upper and lower case letter, digit and special character [#?!@$%^&*-]'
        else:
            error = 'passwords do not match'
        
        # hash password and save to database if credentials are valid
        if email_is_valid and password_is_valid:
            # hash password
            hashed_password = make_password(password)

            # save to database
            user = User.objects.create(email = email, password = hashed_password)

            # create JWT authentication token
            token = create_jwt_token(user)
    else:
        print(serializer.errors)

    return JsonResponse(
        {
            'emailIsValid': email_is_valid,
            'passwordIsValid': password_is_valid,
            'errorMessage': error,
            'token': token
        }
    )  

# ------------------------------ Login Existing Account ------------------------------

@api_view(['POST'])
def verify_credentials(request):   
    # parse json
    serializer = LoginSerializer(data = request.data)

    user_exists = False
    password_is_correct = False
    error = ''
    token = ''

    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        # try to access entry with inputted email
        try:
            user = User.objects.get(email = email)

            user_exists = True

            # confirm password is correct
            if check_password(password, user.password):
                password_is_correct = True
            else:
                error = 'Incorrect password'

            # complete login action if valid
            if user_exists and password_is_correct:
                token = create_jwt_token(user)

        except User.DoesNotExist:
            error = 'Invalid email address'
    else:
        print(serializer.errors)
    
    return JsonResponse({
        'userExists': user_exists,
        'passwordIsCorrect': password_is_correct,
        'errorMessage': error,
        'token': token
    })

# ------------------------------ User Details ------------------------------

@api_view(['POST'])
def core_details(request):
    # parse json
    serializer = CoreDetailsSerializer(data = request.data)

    user_id = None
    errorMessage = ''
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
            errorMessage = 'Invalid First Name'
            culprit = 'firstName'
        elif not re.match(name_pattern, last_name):
            errorMessage = 'Invalid Last Name'
            culprit = 'lastName'

        # implement validation
        date_of_birth = datetime.datetime.strptime(date_of_birth, '%d/%m/%Y').date()

        # validate gender
        if not gender in ['Male', 'Female']:
            errorMessage = 'Invalid Gender'
            culprit = 'gender'

        # validate phone_number

        # (ASCII) 32 = space, 40 = (, 41 = ), 43 = +, 45 = -
        removable_chars = {32: None, 40: None, 41: None, 43: None, 45: None}
        phone_number = phone_number.translate(removable_chars)

        if not (phone_number.isdigit() and len(phone_number) in [9, 10]):
            errorMessage = 'Invalid Phone Number'
            culprit = 'phoneNumber'
    else:
        print(serializer.errors)

    # get token
    user_id = get_jwt_token(request)
    
    # use token to update user if errorMessage and culprit = ''
    if errorMessage == '' and culprit == '' and user_id != None:
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
        'errorMessage': errorMessage,
        'culprit':culprit,
        'isAthlete': is_athlete,
    })

# ------------------------------ Athlete Details ------------------------------

@api_view(['Post'])
def athlete_details(request):
    serializer = AthleteDetailsSerializer(data = request.data)

    user_id = None
    errorMessage = ''
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
        errorMessage, culprit = less_than_zero(height, 'Height', errorMessage, culprit)
        errorMessage, culprit = less_than_zero(weight, 'Weight', errorMessage, culprit)
        errorMessage, culprit = less_than_zero(wingspan, 'Wingspan', errorMessage, culprit)

        # get race category max_weight, max_age and required_gender
        category_object = RaceCategory.objects.filter(category=race_category).first()
        serializer = RaceCategorySerializer(category_object)

        max_weight = convert_none_to_99(serializer.data['max_weight'])
        max_age = convert_none_to_99(serializer.data['max_age'])
        required_gender = serializer.data['required_gender']

        # get User with user_id from JWT token
        user_id = get_jwt_token(request)

        # get user
        user = get_object_or_404(User, user_id = user_id)

        user_age = get_user_age(user.date_of_birth)
        user_gender = user.gender 

        if user_age > max_age or user_gender != required_gender or  weight > max_weight:
            errorMessage = 'You cannot race in this category'
            culprit = 'Race Category'
        
        if errorMessage == '' and culprit == '' and user_id != None:
            # save to database
            UserRowingInfo.objects.create(user = user, race_category = race_category, club_names = clubs, coaches = coaches, height = height, weight = weight, wingspan = wingspan)

    else:
        print(serializer.errors)


    return JsonResponse({
        'success': True
    })




# ------------------------------ Helper Functions ------------------------------

# create jwt token
def create_jwt_token(user):
    # exp = expiry time, iat = issued at time
    payload = {
        'id': user.user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=120),
        'iat': datetime.datetime.utcnow()
    }

    token = jwt.encode(payload, jwt_secret_key, algorithm='HS256')

    return token

def less_than_zero(value, rep, errorMessage, culprit):
    if value < 0:
        errorMessage = 'Cannot be less than 0'
        culprit = rep
    
    return [errorMessage, culprit]

def get_jwt_token(request):
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