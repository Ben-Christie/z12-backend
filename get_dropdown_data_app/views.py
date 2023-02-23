from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import ClubInfo, RaceCategory
from login_register_app.models import User
from .serializers import ClubInfoSerializer, RaceCategorySerializer

# ------------------------------ Get Club Names ------------------------------

@api_view(['GET'])
def get_club_names(request):
  clubs = ClubInfo.objects.all()
  serializer = ClubInfoSerializer(clubs, many = True)

  club_names = [club['club_name'] for club in serializer.data]

  return JsonResponse(club_names, safe = False)

# ------------------------------ Get Race Category Names ------------------------------

@api_view(['GET'])
def get_race_category_names(request):
  race_categories = RaceCategory.objects.all()
  serializer = RaceCategorySerializer(race_categories, many = True)

  race_category_names = [race_category['category'] for race_category in serializer.data]

  return JsonResponse(race_category_names, safe = False)

# ------------------------------ Get Coach Names ------------------------------

@api_view(['GET'])
def get_coach_names(request):
  coaches = User.objects.filter(is_coach=True)
  coach_first_names = [coach.first_name for coach in coaches]
  coach_last_names = [coach.last_name for coach in coaches]

  coach_full_names = []

  for x in range(len(coach_first_names)):
    full_name = f'{coach_first_names[x]} {coach_last_names[x]}'
    coach_full_names.append(full_name)
  
  return JsonResponse(coach_full_names, safe = False)