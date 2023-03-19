from rest_framework.decorators import api_view
from django.http import JsonResponse
from .models import Payments
from login_register_app.models import User
from .serializers import PaymentSerializer
import re, datetime, jwt, os
from django.shortcuts import get_object_or_404
from dotenv import load_dotenv
from user_details_app.views import get_jwt_token_user_id
import stripe
from django.core.mail import send_mail
from django.conf import settings
from user_details_app.models import UserPersonalBests, UserRowingInfo, UserProfilePicture

# load .env file to access variables
load_dotenv()
jwt_secret_key = os.getenv('JWT_SECRET_KEY')
stripe_secret_key = os.getenv('STRIPE_SECRET_KEY')

stripe.api_key = stripe_secret_key

# ------------------------------ Process Payments ------------------------------

@api_view(['POST'])
def payment_processing(request):
    serializer = PaymentSerializer(data = request.data)

    user_id = None
    payment_id = None
    error_message = ''
    culprit = ''
    total_amount = '0'

    for key, value in request.data.items():
        if not value:
            key = key.replace('_',  ' ')

            error_message = f'Missing {key}'
            culprit = key
            
            return JsonResponse({
                'errorMessage': error_message,
                'culprit': culprit
            })

    if serializer.is_valid():
        # get jwt token
        user_id = get_jwt_token_user_id(request)

        data = serializer.validated_data

        full_name = data['full_name']
        card_number = data['card_number']
        expiry_date = data['expiry_date']
        cvv = data['cvv']
        title = data['title']
        total_amount = data['total_amount']

        # verify first name only contains letters or valid symbols 
        name_pattern = re.compile(r'^[a-zA-Z\' -]+$')

        if not re.match(name_pattern, full_name):
            error_message = 'Invalid name'
            culprit = 'full name'
        
        # remove any spaces from card_number and cvv
        card_number = card_number.replace(' ', '')
        cvv = cvv.replace(' ', '')

        # verify cvv and card_number only consist of digits
        if verify_content_and_length(card_number, 14, 16) == False:
            error_message = 'Invalid card number'
            culprit = 'card number'

        if verify_content_and_length(cvv, 3, 4) == False:
            error_message = 'Invalid cvv number'
            culprit = 'cvv'
        
        # parse date and convert to ints
        date_list = expiry_date.split('/')
        expiry_month = date_list[0]
        expiry_year = date_list[1]

        # convert to date and see if date has passed
        now = datetime.datetime.now()
        expiry_date = datetime.datetime.strptime(expiry_date, '%m/%Y')

        if expiry_date.year < now.year or (expiry_date.year == now.year and expiry_date.month < now.month):
            error_message = 'expired date'
            culprit = 'expiry_date'



        # parse total_amount. Stripe expects us to pass an integer value. 
        # For Stripe, 100 = 10.0, therefore we're passing a string that looks like 10.0, removing 
        # the '.' and casting to int. This will improve readability whilst maintaining compatibility
        total_amount_as_int = int(total_amount.replace('.', ''))
    
    else:
        print(serializer.errors)
    
    # execute transaction and save details to database
    if error_message == '' and culprit == '' and user_id != None:

        # use stripe api to complete transaction

        # create stripe payment token
        stripe_token = stripe.Token.create(card = {
            'number': card_number,
            'exp_month': expiry_month,
            'exp_year': expiry_year,
            'cvc': cvv
        })

        try:
            charge = stripe.Charge.create(
                amount = total_amount_as_int,
                currency = 'eur',
                description = title,
                source = stripe_token.id
            )
            payment_id = charge.id
        except Exception as e:
            print('Error: ', e)

        # save payment details

        # get user
        user = get_object_or_404(User, user_id = user_id)

        Payments.objects.create(
            user = user,
            full_name = full_name,
            title = title,
            payment_amount = total_amount,
        )

        # send confirmation email to user
        if payment_id:
            send_mail(
                'Z12 Performance: Confirmation of Payment',
                f'Dear {user.first_name} {user.last_name}\n\nThis email is to confirm your payment of {total_amount} euro for: Z12 Performance Subscription.\n\nIf you have any issues, please contact z12performance@gmail.com\n\nThanks for being a member of our community!\n\nThe Z12 Performance Team',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently = False
            )
        
        # as this is the final step in setting up the profile, we want to prepare for updating not 
        # creations so we will create empty data rows associated with the user if they don't exist

        try:
            UserRowingInfo.objects.get_or_create(user_id = user.user_id)
            UserPersonalBests.objects.get_or_create(user_id = user.user_id)
        except Exception as e:
            print(e)

    
    return JsonResponse({
        'errorMessage': error_message,
        'culprit': culprit
    })

# ------------------------------ Helper Functions ------------------------------

def verify_content_and_length(data, min_length, max_length):
    pattern = re.compile(r'^[0-9]+$')
    return re.match(pattern, data) and min_length <= len(data) and len(data) <= max_length
