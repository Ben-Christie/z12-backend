from database_connection import db
from rest_framework import status
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
import json
import re

# ----------database connection------------
import sys
sys.path.insert(1, '../database_connection')
# -----------------------------------------

users_collection = db['users']


@api_view(['POST'])
def create_login(request):
    # parse json
    body = json.loads(request.body)

    # get email and password and confirm password
    email = body['email']
    password = body['password']
    confirm_password = body['confirm_password']

    print(email, password, confirm_password)

    email_is_valid = False
    password_is_valid = False
    error = ''

    # password must be at least 8 characters and contain digit 0 - 9, Uppercase, Lowercase and Special
    # character from list (#?!@$%^&*-)
    password_validation_pattern = '^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$'

    # compare password to confirm password and regex pattern
    if password == confirm_password and re.match(password_validation_pattern, password):
        password_is_valid = True
    elif password == confirm_password:
        error = 'password is not valid. Requires at least one uppercase, lowercase, digit and special character [#?!@$%^&*-]'
    else:
        error = 'passwords do not match'
        
    # verify email does not already exist in the database
    if not users_collection.find_one({'email': email}):
        email_is_valid = True
    else:
        error = 'email already exists'


    # hash password before storing in database
    hashed_password = make_password(password)

    # # save to database
    # if email_is_valid and password_is_valid:
    #     users_collection.insert_one({
    #         'email': email,
    #         'password': hashed_password,
    #     })

    return JsonResponse(
        {
            'emailIsValid': email_is_valid,
            'passwordIsValid': password_is_valid,
            'errorMessage': error
        }
    )


@api_view(['POST'])
def verify_credentials(request):
    # parse json
    body = json.loads(request.body)

    email = body['email']
    password = body['password']

    user_exists = False
    password_is_correct = False

    users_collection = db['users']

    user_document = users_collection.find_one({'email': email})

    # verify email exists in database
    if user_document:
        user_exists = True
    else:
        return JsonResponse({'error': 'Email does not exist'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    # verify password is correct
    if check_password(password, user_document['password']):
        password_is_correct = True
    else:
        return JsonResponse({'error': 'Password is incorrect'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    if user_exists and password_is_correct:
        return JsonResponse({
            'userExists': user_exists,
            'passwordIsCorrect': password_is_correct
        }, status=status.HTTP_200_OK)
