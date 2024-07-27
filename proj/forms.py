import pytz
from django import forms
from django.utils import timezone

from .models import Goal, Transaction, User


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["type", "amount", "description", "date", "category"]
        widgets = {
            "type": forms.Select(attrs={"class": "form-control"}),
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "off",
                    "id": "amount-input",
                }
            ),
            "description": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "off",
                    "placeholder": "Optional",
                }
            ),
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "category": forms.HiddenInput(),  # Category field is hidden as it is determined by the ML model
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(TransactionForm, self).__init__(*args, **kwargs)
        if user and user.time_zone:
            user_tz = pytz.timezone(user.time_zone)
            localized_date = timezone.now().astimezone(user_tz).date()
            self.fields["date"].widget.attrs["value"] = localized_date
        self.fields["description"].required = False
        self.fields[
            "category"
        ].required = False  # Making category non-mandatory in form


class ChatForm(forms.Form):
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "cols": 50,
                "class": "form-input bg-white p-4 border border-gray-300 rounded-md",
            }
        )
    )
    goal = forms.ModelChoiceField(
        queryset=Goal.objects.none(),
        required=False,
        widget=forms.Select(
            attrs={"class": "form-input bg-white p-2 border border-gray-300 rounded-md"}
        ),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(ChatForm, self).__init__(*args, **kwargs)
        if user:
            self.fields["goal"].queryset = Goal.objects.filter(user=user)


from django import forms
from .models import Goal

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['name', 'target_amount', 'months_to_save', 'amount_saved']

    def clean(self):
        cleaned_data = super().clean()
        target_amount = cleaned_data.get('target_amount')
        amount_saved = cleaned_data.get('amount_saved')
        months_to_save = cleaned_data.get('months_to_save')
        # Ensure target amount is greater than amount saved
        if target_amount < amount_saved:
            self.add_error('target_amount', 'Target amount must be greater than amount saved.')

        # Ensure neither target amount nor amount saved are negative
        if target_amount < 0:
            self.add_error('target_amount', 'Target amount must be non-negative.')
        if amount_saved < 0:
            self.add_error('amount_saved', 'Amount saved must be non-negative.')
        if months_to_save < 0:
            self.add_error('months_to_save', 'Months to save must be non-negative.')
        return cleaned_data
