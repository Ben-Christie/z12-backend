from rest_framework.decorators import api_view
from django.http import JsonResponse
from get_dropdown_data_app.models import RaceCategory
from get_dropdown_data_app.serializers import RaceCategorySerializer
from login_register_app.models import User
import os, re, datetime
from django.shortcuts import get_object_or_404
from user_details_app.views import convert_none_to_99, get_jwt_token_user_id, get_user_age, less_than_zero
from dotenv import load_dotenv
from user_details_app.models import UserPersonalBests, UserRowingInfo
from user_details_app.serializers import PersonalBestsSerializer 
from metric_gathering_app.views import add_erg_data, get_time_in_seconds
from .serializers import DetailsModalSerializer

# load .env file to access variables
load_dotenv()
jwt_secret_key = os.getenv('JWT_SECRET_KEY')

# ------------------------------ Update Personal Best ------------------------------

@api_view(['POST'])
def update_pb(request):
  # get user id from JWT token
  user_id = get_jwt_token_user_id(request)
  success = False

  # extract fields from the request
  distance = request.data.get('distance')
  time = request.data.get('time')

  if distance and time:
    # update distance to match expected syntax
    updated_distance = f"pb_{distance.replace('m', '')}"

    # get object from personal bests table using user id
    personal_best_object = get_object_or_404(UserPersonalBests, user_id = user_id)

    # update column with new time
    setattr(personal_best_object, updated_distance, time)

    # serialize the data
    PersonalBestsSerializer(personal_best_object)

    # save to database
    personal_best_object.save()

    # get user
    user = get_object_or_404(User, user_id = user_id)

    # add to relevant chart
    time_in_seconds = get_time_in_seconds(time)
    converted_distance = int(distance.replace('m', ''))

    add_erg_data(distance, time_in_seconds, time, user, None, time_in_seconds)

    success = True

  return JsonResponse({
      'success': success
    })
  
# ------------------------------ Update User Details ------------------------------

@api_view(['POST'])
def update_user_details(request):
  serializer = DetailsModalSerializer(data = request.data)

  user_id = get_jwt_token_user_id(request)
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
    weight = float(data['weight'])
    height = float(data['height'])
    wingspan = float(data['wingspan'])
    race_category = data['race_category']
    clubs = data['clubs']
    coaches = data['coaches']

    # verify account type
    is_athlete = True
    is_coach = False

    if athlete_or_coach == 'Coach':
      is_athlete = False
      is_coach = True
    elif athlete_or_coach == 'Both':
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

    # date_of_birth
    euro_date_format = re.compile(r'^(0[1-9]|[1-2][0-9]|3[0-1])\/(0[1-9]|1[0-2])\/\d{4}$')
    sql_date_format = re.compile(r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])$')


    if re.match(euro_date_format, date_of_birth):
        date_of_birth = datetime.datetime.strptime(date_of_birth, '%d/%m/%Y').date()
    elif re.match(sql_date_format, date_of_birth):
        date_of_birth = datetime.datetime.strptime(date_of_birth, '%Y-%m-%d').date()

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

    # get user
    user = get_object_or_404(User, user_id = user_id)

    user_age = get_user_age(user.date_of_birth)
    user_gender = user.gender 

    if user_age > max_age or user_gender != required_gender or  weight > max_weight:
        error_message = 'Entry forbidden'
        culprit = 'race category'

    # use token to update user if errorMessage and culprit = ''
    if error_message == '' and culprit == '' and user_id != None:
        # use user_id to update existing entry in the database
        user = get_object_or_404(User, user_id = user_id)
        athlete_details = get_object_or_404(UserRowingInfo, user_id = user_id)

        #update
        user.first_name = first_name
        user.last_name = last_name
        user.date_of_birth = date_of_birth
        user.gender = gender
        user.phone_number = phone_number
        user.is_athlete = is_athlete
        user.is_coach = is_coach
        athlete_details.height = height
        athlete_details.weight = weight
        athlete_details.wingspan = wingspan
        athlete_details.race_category = race_category
        athlete_details.clubs = clubs
        athlete_details.coaches = coaches

        # save
        user.save()
        athlete_details.save()
  
  else:
    print(serializer.errors)

  return JsonResponse({
    'errorMessage': error_message,
    'culprit': culprit
  });
