from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import get_user_model
from .models import User
from .serializers import RegisterSerializer, LoginSerializer, CoreDetailsSerializer
import re, datetime, jwt, os
from dotenv import load_dotenv
from django.shortcuts import get_object_or_404

# load .env file to access variables
load_dotenv()
jwt_secret_key = os.getenv('JWT_SECRET_KEY')

User = get_user_model()

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

    return JsonResponse(
        {
            'emailIsValid': email_is_valid,
            'passwordIsValid': password_is_valid,
            'errorMessage': error,
            'token': token
        }
    )  

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
    
    return JsonResponse({
        'userExists': user_exists,
        'passwordIsCorrect': password_is_correct,
        'errorMessage': error,
        'token': token
    })

@api_view(['POST'])
def core_details(request):
    # parse json
    serializer = CoreDetailsSerializer(data = request.data)

    token = None
    user_id = None
    errorMessage = ''
    culprit = ''

    if serializer.is_valid():
        first_name = serializer.validated_data['first_name']
        last_name = serializer.validated_data['last_name']
        date_of_birth = serializer.validated_data['date_of_birth']
        gender = serializer.validated_data['gender']
        phone_number = serializer.validated_data['phone_number']
        is_athlete = serializer.validated_data['is_athlete']
        is_coach = serializer.validated_data['is_coach']

        # validate first_name and last_name
        print(first_name, last_name, date_of_birth, gender, phone_number, is_athlete, is_coach)

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

    # get JWT token
    auth_header = request.headers.get('Authorization')

    # verify existance of JWT token
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
        except jwt.ExpiredSignatureError:
            return JsonResponse({
                'error': 'token has expired'
            }, status = 401)
        except jwt.InvalidTokenError:
            return JsonResponse({
                'error': 'invalid token'
            }, status = 401)
    else:
        errorMessage = 'Invalid token'
        culprit = 'token'
    
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
    })


# ---------------------------------- Helper Functions --------------------------------

# create jwt token
def create_jwt_token(user):
    payload = {
        'id': user.user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=120),
        'iat': datetime.datetime.utcnow()
    }

    token = jwt.encode(payload, jwt_secret_key, algorithm='HS256')

    return token