from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.contrib.auth.models import User
from .models import User,Transaction
from django.contrib.auth.views import LogoutView
from .forms import TransactionForm
from django.contrib import messages

 # Create your views here.
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
COUNTRY_TO_CURRENCY_SYMBOL = {
    'US': '$',       # United States
    'IN': '₹',       # India
    'DE': '€',       # Germany
    'GB': '£',       # United Kingdom
    'JP': '¥',       # Japan
    'BR': 'R$',      # Brazil
    'SG': '$'        # Singapore
}

def index(request):
    # If no user is signed in, return to login page:
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    return render(request, "proj/user.html")

def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]  # Use username to authenticate
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "proj/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "proj/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        country = request.POST.get("country", None)  # Use None as a default value to clearly identify unset fields

        if password != confirmation:
            return render(request, "proj/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.country = country  # Set the country attribute
            if country:
                user.time_zone = COUNTRY_TO_TIMEZONE.get(country, 'UTC')  # Set time zone based on country
            else:
                user.time_zone = 'UTC'  # Default time zone if no country provided
            user.save()  # Make sure to save after setting all attributes
            login(request, user)  # Log in the new user
            return HttpResponseRedirect(reverse("index"))
        except IntegrityError:
            return render(request, "proj/register.html", {
                "message": "Username or email address already taken. Please try a different one."
            })
    else:
        return render(request, "proj/register.html")
    
@login_required
def list_transactions(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    # Assuming `country` is a field on the user model:
    country_code = request.user.country
    currency_symbol = COUNTRY_TO_CURRENCY_SYMBOL.get(country_code, '$')  # Default to USD if not found
    context = {
        'transactions': transactions,
        'currency_symbol': currency_symbol
    }
    return render(request, 'proj/list.html', context)

@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, 'Transaction added successfully!')  # Adding success message
            return redirect('add_transaction')  # Redirect back to the same page to clear the form
    else:
        form = TransactionForm(user=request.user)  # Initialize form with user

    return render(request, 'proj/add_transaction.html', {'form': form})

@login_required
def delete_transaction(request, transaction_id):
    if request.method == "POST":
        try:
            transaction = Transaction.objects.get(id=transaction_id, user=request.user)
            transaction.delete()
            return JsonResponse({"success": True})
        except Transaction.DoesNotExist:
            return JsonResponse({"success": False, "error": "Transaction not found."})
    else:
        return JsonResponse({"success": False, "error": "Invalid request"})