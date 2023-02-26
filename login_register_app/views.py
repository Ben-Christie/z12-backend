from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import get_user_model
from .models import User
from .serializers import RegisterSerializer, LoginSerializer
import re, datetime, jwt, os
from dotenv import load_dotenv

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