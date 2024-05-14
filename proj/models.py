from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

# Dictionary mapping ISO country codes to time zones
COUNTRY_TO_TIMEZONE = {
    'US': 'America/New_York',    # United States
    'IN': 'Asia/Kolkata',        # India
    'DE': 'Europe/Berlin',       # Germany
    'GB': 'Europe/London',       # United Kingdom
    'JP': 'Asia/Tokyo',          # Japan
    'BR': 'America/Sao_Paulo',   # Brazil
    'SG': 'Asia/Singapore'       # Singapore
}

class User(AbstractUser):
    date_of_birth = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    time_zone = models.CharField(max_length=50, default='UTC')

    def save(self, *args, **kwargs):
        # Set time_zone based on country
        self.time_zone = COUNTRY_TO_TIMEZONE.get(self.country, 'UTC')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.email})"
    
class Asset(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assets')
    asset_type = models.CharField(max_length=100)
    description = models.CharField(max_length=255, null=True, blank=True)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    acquisition_date = models.DateField()

    def __str__(self):
        return f"{self.asset_type} owned by {self.user.username} valued at {self.value}"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('inflow', 'Inflow'),
        ('outflow', 'Outflow'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions")
    type = models.CharField(max_length=7, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField()

    def __str__(self):
        return f"{self.type} transaction of {self.amount} on {self.date}"
