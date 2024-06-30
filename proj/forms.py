from django import forms
from django.utils import timezone
import pytz
from .models import Transaction, User, Goal
        

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['type', 'amount', 'description', 'date', 'category']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'autocomplete': 'off', 'id': 'amount-input'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off', 'placeholder': 'Optional'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'category': forms.HiddenInput()  # Category field is hidden as it is determined by the ML model
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TransactionForm, self).__init__(*args, **kwargs)
        if user and user.time_zone:
            user_tz = pytz.timezone(user.time_zone)
            localized_date = timezone.now().astimezone(user_tz).date()
            self.fields['date'].widget.attrs['value'] = localized_date
        self.fields['description'].required = False
        self.fields['category'].required = False  # Making category non-mandatory in form
class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['name', 'target_amount', 'months_to_save', 'amount_saved']
from django import forms
from .models import Goal

class ChatForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(attrs={"rows": 3, "cols": 50, "class": "form-control"}))
    goal = forms.ModelChoiceField(queryset=Goal.objects.none(), required=False, widget=forms.Select(attrs={"class": "form-control"}))

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ChatForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['goal'].queryset = Goal.objects.filter(user=user)