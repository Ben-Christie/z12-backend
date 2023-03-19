from rest_framework.decorators import api_view
from django.http import JsonResponse
import os, math
from dotenv import load_dotenv
from user_details_app.views import get_jwt_token_user_id
from metric_gathering_app.models import UserErgMetrics, UserSAndCMetrics
from metric_gathering_app.serializers import ErgMetricsSerializer, SAndCMetricsSerializer


# load .env file to access variables
load_dotenv()
jwt_secret_key = os.getenv('JWT_SECRET_KEY')

# pi
pi = math.pi

# ------------------------------ Erg Analysis Chart Data ------------------------------

@api_view(['POST'])
def populate_erg_chart(request):
    user_id = get_jwt_token_user_id(request)
    distance = request.query_params['distance']

    erg_data_object = UserErgMetrics.objects.filter(user_id = user_id, distance = distance).all()
    erg_data = ErgMetricsSerializer(erg_data_object, many = True)

    return JsonResponse(erg_data.data, safe = False)

# ------------------------------ S&C Analysis Chart Data ------------------------------

@api_view(['POST'])
def populate_s_and_c_chart(request):
    user_id = get_jwt_token_user_id(request)
    exercise = request.query_params['exercise']

    # parse exercise to look like database config
    exercise = exercise.replace('_', ' ')

    s_and_c_data_object = UserSAndCMetrics.objects.filter(user_id = user_id, exercise = exercise).all()
    s_and_c_data = SAndCMetricsSerializer(s_and_c_data_object, many = True)

    return JsonResponse(s_and_c_data.data, safe = False)






