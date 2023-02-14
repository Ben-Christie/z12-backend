from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import get_user_model
from .models import User
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework.authtoken.models import Token
import re

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
        
        # verify email does not already exist in the database
        if User.objects.filter(email = email).exists():
            error = 'email already exists'
        else:
            email_is_valid = True
        
        # hash password and save to database if credentials are valid
        if email_is_valid and password_is_valid:
            # hash password
            hashed_password = make_password(password)

            # save to database
            user = User.objects.create(email = email, password = hashed_password)

            # create authentication token
            token = Token.objects.create(user = user).key

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
            user = get_user_model().objects.get(email = email)

            user_exists = True

            # confirm password is correct
            if check_password(password, user.password):
                password_is_correct = True
            else:
                error = 'Incorrect password'

            # complete login action if valid
            if user_exists and password_is_correct:
                token = Token.objects.create(user = user).key

        except User.DoesNotExist:
            error = 'Invalid email address'
    
    return JsonResponse({
        'userExists': user_exists,
        'passwordIsCorrect': password_is_correct,
        'errorMessage': error,
        'token': token
    })