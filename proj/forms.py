from django import forms
from django.utils import timezone
import pytz
from .models import Transaction, User

from django import forms
from django.utils import timezone
import pytz
from .models import Transaction,User

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['type', 'amount', 'description', 'date']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'autocomplete': 'off', 'id': 'amount-input'}),
            'description': forms.TextInput(attrs={
                'class': 'form-control', 
                'autocomplete': 'off', 
                'placeholder': 'Optional'
            }),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TransactionForm, self).__init__(*args, **kwargs)
        if user and user.time_zone:
            user_tz = pytz.timezone(user.time_zone)
            localized_date = timezone.now().astimezone(user_tz).date()
            self.fields['date'].widget.attrs['value'] = localized_date
        self.fields['description'].required = False
