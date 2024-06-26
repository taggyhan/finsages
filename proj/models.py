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
    
    CATEGORY_CHOICES = (
        ('auto', 'Auto'),
        ('baby', 'Baby'),
        ('clothes', 'Clothes'),
        ('electronics', 'Electronics'),
        ('entertainment', 'Entertainment'),
        ('food', 'Food'),
        ('home', 'Home'),
        ('kids', 'Kids'),  # Note: You might want to remove or handle this category differently due to having very few entries
        ('medical', 'Medical'),
        ('personal_care', 'Personal Care'),
        ('pets', 'Pets'),  # Assuming you want to include Pets based on your truncated list
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions")
    type = models.CharField(max_length=7, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField()

    def __str__(self):
        return f"{self.type} transaction of {self.amount} in category '{self.category}' on {self.date}"
