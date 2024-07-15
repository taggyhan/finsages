from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models import Sum, Q, Count
from django.db.models.functions import TruncMonth 
from .models import Transaction, Goal
from .forms import TransactionForm, GoalForm, ChatForm
from .ml_model import predict_category
import json
import openai
import os
from dotenv import load_dotenv

User = get_user_model()
# Your views and logic here
load_dotenv()


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

    user = request.user
    now = timezone.now()

    # Calculate the first and last day of the current month
    first_day_of_month = datetime(now.year, now.month, 1)
    last_day_of_month = datetime(now.year, now.month + 1, 1) - timezone.timedelta(days=1) if now.month != 12 else datetime(now.year + 1, 1, 1) - timezone.timedelta(days=1)

    # Filter and aggregate transactions for the current month
    inflow = Transaction.objects.filter(user=user, type='inflow', date__gte=first_day_of_month, date__lte=last_day_of_month).aggregate(total=Sum('amount'))['total'] 
    outflow = Transaction.objects.filter(user=user, type='outflow', date__gte=first_day_of_month, date__lte=last_day_of_month).aggregate(total=Sum('amount'))['total'] 

    # Handle None values
    inflow = inflow or 0
    outflow = outflow or 0

    net_inflow = inflow - outflow

    context = {
        'user': user,
        'net_inflow': net_inflow,
    }

    return render(request, "proj/user.html", context)
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
    

def get_aggregate_transactions(user, start_date):
    aggregate_transactions = Transaction.objects.filter(
        user=user,
        date__gte=start_date
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total_inflow=Sum('amount', filter=Q(type='inflow')),
        total_outflow=Sum('amount', filter=Q(type='outflow'))
    ).order_by('month')
    
    months = [trans['month'].strftime("%Y-%m") for trans in aggregate_transactions]
    inflows = [float(trans['total_inflow'] or 0) for trans in aggregate_transactions]
    outflows = [float(trans['total_outflow'] or 0) for trans in aggregate_transactions]
    
    chart_data = {
        'months': months,
        'inflows': inflows,
        'outflows': outflows,
    }
    
    return chart_data

@login_required
def list_transactions(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    country_code = request.user.country
    currency_symbol = COUNTRY_TO_CURRENCY_SYMBOL.get(country_code, '$')  # Default to USD if not found

    # Calculate the date six months ago
    three_months_ago = timezone.now().date() - timedelta(days=90)

    
    # Get aggregate transactions for the last six months
    chart_data = get_aggregate_transactions(request.user, three_months_ago)
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

            # Use ML model to predict the category based on the description
            description = form.cleaned_data['description']
            
            transaction_type = form.cleaned_data['type']
            
            if transaction_type == 'outflow' and description:
                predicted_category = predict_category(description)
                transaction.category = predicted_category  # Assign the predicted category to the transaction
            else:
                transaction.category = None


            transaction.save()
            messages.success(request, 'Transaction added successfully!')
            return redirect('add_transaction')
    else:
        form = TransactionForm(user=request.user)

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
        if description:
            predicted_category = predict_category(description)
            transaction.category = predicted_category  # Assign the predicted category to the transaction
        else:
            transaction.category = None
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
    '''
@login_required
def analysis(request):
    # Calculate the date one year ago
    one_year_ago = timezone.now().date() - timedelta(days=365)
    
    # Get aggregate transactions for the last year
    chart_data = get_aggregate_transactions(request.user, one_year_ago)
    
    # Aggregate transactions by their 'category' and counts them
    categories = Transaction.objects.values('category').annotate(total=Count('category')).order_by('category')
    
    # Retrieve detailed transactions grouped by category
    detailed_transactions = {}
    for category in categories:
        detailed_transactions[category['category']] = Transaction.objects.filter(category=category['category'])

    context = {
        'chart_data': json.dumps(chart_data, cls=DecimalEncoder),
        'categories': categories,
        'detailed_transactions': detailed_transactions,
    }

    return render(request, 'proj/analysis.html', context)

'''


@login_required
def analysis(request):
    # Calculate the date one year ago
    one_year_ago = timezone.now().date() - timedelta(days=365)
    
    # Get aggregate transactions for the last year
    chart_data = get_aggregate_transactions(request.user, one_year_ago)
    
    # Aggregate outflow transactions by their 'category' and sum their amounts
    outflow_categories = Transaction.objects.filter(type='outflow').values('category').annotate(total=Sum('amount')).order_by('category')

    context = {
        'chart_data': json.dumps(chart_data, cls=DecimalEncoder),
        'outflow_categories': json.dumps({category['category']: category['total'] for category in outflow_categories}, cls=DecimalEncoder),
    }

    return render(request, 'proj/analysis.html', context)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY");

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
#@login_required
def create_financial_advice_prompt(user, goal):
    transactions = list(Transaction.objects.filter(user=user).values())
    inflows = [t for t in transactions if t['type'] == 'inflow']
    outflows = [t for t in transactions if t['type'] == 'outflow']

    prompt = f"""
    User's Financial Data:
    
    Inflows:
    {json.dumps(inflows, indent=2, default=decimal_default)}

    Outflows:
    {json.dumps(outflows, indent=2, default=decimal_default)}

    Savings Goal:
    - Goal: {goal.name}
    - Target Amount: ${goal.target_amount}
    - Months to Save: {goal.months_to_save}
    - Amount Saved: ${goal.amount_saved}

    User's Question:
    How can I reach my goal of saving ${goal.target_amount} for {goal.name} in {goal.months_to_save} months, given my current income and expenditures?
    """
    return prompt

@login_required
def chatbot_view(request):
    user = request.user
    form = ChatForm(user=user)
    user_message = None
    bot_response = None
    if request.method == "POST":
        form = ChatForm(request.POST, user=user)
        if form.is_valid():
            user_message = form.cleaned_data["message"]
            selected_goal = form.cleaned_data.get("goal")

            if selected_goal:
                prompt = create_financial_advice_prompt(user, selected_goal)
                prompt += f"Here is the user's message:\n{user_message}"

            else:
                user_data = {
                    "goals": list(Goal.objects.filter(user=user).values()),
                    "transactions": list(Transaction.objects.filter(user=user).values())
                }
                prompt = f"Here is the user's financial data:\n{json.dumps(user_data, indent=2)}\n\n{user_message}"
                print(prompt)

            try:
                client = OpenAI()
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a financial assistant."},
                        {"role": "user", "content": prompt}
                    ],  
                    temperature=0.5,
                    )
                bot_response = response.choices[0].message.content
            except Exception as e:
                bot_response = f"Error: {e}"

    return render(request, "proj/chatbot.html", {"form": form, "user_message": user_message, "bot_response": bot_response})

@login_required
def goals_view(request):
    goals = Goal.objects.filter(user=request.user)
    return render(request, 'proj/goals.html', {'goals': goals})

@login_required
def add_goal(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect('goals_view')
    else:
        form = GoalForm()
    return render(request, 'proj/add_goal.html', {'form': form})

@login_required
def update_goal(request, goal_id):
    goal = Goal.objects.get(id=goal_id, user=request.user)
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            return redirect('goals_view')
    else:
        form = GoalForm(instance=goal)
    return render(request, 'proj/update_goal.html', {'form': form, 'goal': goal})

@login_required
@require_POST
def update_goal_amount(request, goal_id):
    goal = Goal.objects.get(id=goal_id, user=request.user)
    amount = Decimal(request.POST.get('amount'))
    goal.amount_saved += amount
    goal.save()
    return redirect('goals_view')

@login_required
@require_POST
def delete_goal(request, goal_id):
    goal = Goal.objects.get(id=goal_id, user=request.user)
    goal.delete()
    return redirect('goals_view')