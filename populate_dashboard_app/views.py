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
        'contentType': 'image/jpeg',
    })

# ------------------------------ Personal Bests ------------------------------
