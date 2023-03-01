from django.db import models
from login_register_app.models import User

class Payments(models.Model):
    payment_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    payment_amount = models.CharField(max_length=10)
    transaction_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'
