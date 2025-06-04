from django.db import models
import uuid
# Create your models here.

class MomoPayment(models.Model):
    order_id = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    order_info = models.CharField(max_length=255)
    request_id = models.CharField(max_length=50, unique=True)
    transaction_id = models.CharField(max_length=50, blank=True, null=True)
    message = models.CharField(max_length=255, blank=True, null=True)
    response_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order_id} - {self.amount}"

    @staticmethod
    def generate_order_id():
        return str(uuid.uuid4())

    @staticmethod
    def generate_request_id():
        return str(uuid.uuid4())