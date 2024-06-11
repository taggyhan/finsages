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
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
import json
from django.db.models.functions import TruncMonth 
from django.db.models import Sum, Q
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

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
    country_code = request.user.country
    currency_symbol = COUNTRY_TO_CURRENCY_SYMBOL.get(country_code, '$')  # Default to USD if not found

    # Calculate the date six months ago
    six_months_ago = timezone.now().date() - timedelta(days=180)

    # Filter and aggregate transactions from the last six months, grouping by month, specific to the user
    aggregate_transactions = Transaction.objects.filter(user=request.user, date__gte=six_months_ago).annotate(
        month=TruncMonth('date')  # Correct usage
    ).values('month').annotate(
        total_inflow=Sum('amount', filter=Q(type='inflow')),
        total_outflow=Sum('amount', filter=Q(type='outflow'))
    ).order_by('month')
    
    # Prepare data for the chart
    months = [trans['month'].strftime("%Y-%m") for trans in aggregate_transactions]
    inflows = [float(trans['total_inflow'] or 0) for trans in aggregate_transactions]
    outflows = [float(trans['total_outflow'] or 0) for trans in aggregate_transactions]

    # Convert lists to JSON for JavaScript consumption
    chart_data = {
        'months': json.dumps(months),
        'inflows': json.dumps(inflows),
        'outflows': json.dumps(outflows),
    }

    # Add to the existing context
    chart_data = {
    'months': months,
    'inflows': inflows,
    'outflows': outflows,
}

    context = {
        'transactions': transactions,
        'currency_symbol': currency_symbol,
        'chart_data': json.dumps(chart_data, cls=DecimalEncoder),
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

    

@csrf_exempt
@require_POST
def delete_transaction(request, transaction_id):
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        transaction.delete()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
@csrf_exempt
@require_POST
def update_transaction(request):
    try:
        transaction_id = request.POST.get('id')
        date = request.POST.get('date')
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        
        transaction = Transaction.objects.get(id=transaction_id)
        transaction.date = date
        transaction.amount = amount
        transaction.description = description
        transaction.save()
        
        return JsonResponse({
            'success': True,
            'transaction': {
                'id': transaction.id,
                'date': transaction.date,
                'amount': transaction.amount,
                'description': transaction.description,
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })