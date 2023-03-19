from rest_framework.decorators import api_view
from django.http import JsonResponse
from login_register_app.models import User
import os
from django.shortcuts import get_object_or_404
from user_details_app.views import get_jwt_token_user_id
from dotenv import load_dotenv
from user_details_app.models import UserPersonalBests
from user_details_app.serializers import PersonalBestsSerializer 
from populate_dashboard_app.views import calculate_split, adjust_decimal_places
from metric_gathering_app.models import UserErgMetrics
from metric_gathering_app.serializers import ErgMetricsSerializer
from metric_gathering_app.views import add_erg_data, get_time_in_seconds

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
    add_erg_data(distance, time_in_seconds, time, user, None)

    success = True

  return JsonResponse({
      'success': success
    })

