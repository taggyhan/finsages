# Generated by Django 3.2.25 on 2024-06-17 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proj', '0006_auto_20240514_0048'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='category',
            field=models.CharField(blank=True, choices=[('auto', 'Auto'), ('baby', 'Baby'), ('clothes', 'Clothes'), ('electronics', 'Electronics'), ('entertainment', 'Entertainment'), ('food', 'Food'), ('home', 'Home'), ('kids', 'Kids'), ('medical', 'Medical'), ('personal_care', 'Personal Care'), ('pets', 'Pets')], max_length=20, null=True),
        ),
    ]