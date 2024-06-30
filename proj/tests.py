from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Asset, Transaction, Goal
from datetime import date

User = get_user_model()

class UserModelTest(TestCase):

    def test_user_time_zone_set_based_on_country(self):
        user = User.objects.create_user(username='testuser', password='12345', country='IN')
        user.save()
        self.assertEqual(user.time_zone, 'Asia/Kolkata')
        
    def test_user_time_zone_defaults_to_UTC(self):
        user = User.objects.create_user(username='testuser', password='12345')
        user.save()
        self.assertEqual(user.time_zone, 'UTC')

class AssetModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='assetowner', password='12345')

    def test_asset_creation(self):
        asset = Asset.objects.create(
            user=self.user,
            asset_type='Stock',
            description='Tech stock',
            value=10000.00,
            acquisition_date=date.today()
        )
        self.assertEqual(asset.asset_type, 'Stock')
        self.assertEqual(asset.user.username, 'assetowner')
        self.assertEqual(str(asset), f"Stock owned by {self.user.username} valued at 10000.0")

class TransactionModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='transactionuser', password='12345')

    def test_transaction_creation(self):
        transaction = Transaction.objects.create(
            user=self.user,
            type='inflow',
            category='food',
            amount=100.00,
            description='Grocery shopping',
            date=date.today()
        )
        self.assertEqual(transaction.type, 'inflow')
        self.assertEqual(transaction.category, 'food')
        self.assertEqual(transaction.amount, 100.00)
        self.assertEqual(str(transaction), f"inflow transaction of 100.0 in category 'food' on {transaction.date}")

class GoalModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='goaluser', password='12345')

    def test_goal_creation(self):
        goal = Goal.objects.create(
            user=self.user,
            name='Car',
            target_amount=5000.00,
            months_to_save=12,
            amount_saved=500.00
        )
        self.assertEqual(goal.name, 'Car')
        self.assertEqual(goal.target_amount, 5000.00)
        self.assertEqual(goal.amount_saved, 500.00)
        self.assertEqual(str(goal), 'Car - Target: 5000.0 - Saved: 500.0')
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Transaction, Goal
from datetime import datetime, timedelta
import json

User = get_user_model()

class ViewsTestCase(TestCase):

    def setUp(self):
        # Set up a test client
        self.client = Client()
        
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='12345', email='testuser@example.com', country='US')
        
        # Log in the test user
        self.client.login(username='testuser', password='12345')
        
        # Create test transactions
        self.transaction1 = Transaction.objects.create(
            user=self.user,
            type='inflow',
            category='Salary',
            amount=1000.00,
            description='Monthly salary',
            date=datetime.now()
        )
        
        self.transaction2 = Transaction.objects.create(
            user=self.user,
            type='outflow',
            category='Groceries',
            amount=200.00,
            description='Grocery shopping',
            date=datetime.now()
        )
        
        # Create a test goal
        self.goal = Goal.objects.create(
            user=self.user,
            name='Car',
            target_amount=5000.00,
            months_to_save=12,
            amount_saved=100.00
        )

    def test_index_view(self):
        self.client.logout()
        response = self.client.get(reverse('index'))
        #checks for redirect when logged out
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('index'))
        # Check for successful response and correct template when logged in
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'proj/user.html')

    def test_login_view(self):
        response = self.client.get(reverse('login'))
        # Check for successful response and correct template on GET request
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'proj/login.html')
        
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': '12345'})
        # Check for redirect after successful login
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))

    def test_logout_view(self):
        response = self.client.get(reverse('logout'))
        # Check for redirect after logout
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('index'))
        # Check for redirect to login page when accessing index after logout
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

    def test_register_view(self):
        response = self.client.get(reverse('register'))
        # Check for successful response and correct template on GET request
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'proj/register.html')
        
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'confirmation': 'password123',
            'country': 'US'
        })
        # Check for redirect after successful registration
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))

    def test_list_transactions_view(self):
        response = self.client.get(reverse('list_transactions'))
        # Check for successful response and correct template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'proj/list.html')
        # Check for expected context variables
        self.assertIn('transactions', response.context)
        self.assertIn('currency_symbol', response.context)
        self.assertIn('chart_data', response.context)

    def test_update_transaction_view(self):
        response = self.client.post(reverse('update_transaction'), {
            'id': self.transaction1.id,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'amount': 1500.00,
            'description': 'Updated description'
        })
        # Check for successful response
        self.assertEqual(response.status_code, 200)
        # Check for expected JSON response content
        self.assertJSONEqual(response.content, {
            'success': True,
            'transaction': {
                'id': (self.transaction1.id),
                'date': datetime.now().strftime('%Y-%m-%d'),
                'amount': '1500.0',  # Expect amount as string
                'description': 'Updated description'
            }
        })

    def test_delete_transaction_view(self):
        response = self.client.post(reverse('delete_transaction', args=[self.transaction1.id]))
        # Check for successful response
        self.assertEqual(response.status_code, 200)
        # Check for expected JSON response content
        self.assertJSONEqual(response.content, {'success': True})

    def test_analysis_view(self):
        response = self.client.get(reverse('analysis'))
        # Check for successful response and correct template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'proj/analysis.html')

    def test_goals_view(self):
        response = self.client.get(reverse('goals_view'))
        # Check for successful response and correct template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'proj/goals.html')
        # Check for expected context variables
        self.assertIn('goals', response.context)

    def test_add_goal_view(self):
        response = self.client.get(reverse('add_goal'))
        # Check for successful response and correct template on GET request
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'proj/add_goal.html')

        response = self.client.post(reverse('add_goal'), {
            'name': 'Vacation',
            'target_amount': 2000.00,
            'months_to_save': 6,
            'amount_saved': 100.00
        })
        # Check for redirect after successful goal addition
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('goals_view'))

    def test_update_goal_view(self):
        response = self.client.get(reverse('update_goal', args=[self.goal.id]))
        # Check for successful response and correct template on GET request
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'proj/update_goal.html')

        response = self.client.post(reverse('update_goal', args=[self.goal.id]), {
            'name': 'Updated Goal',
            'target_amount': 3000.00,
            'months_to_save': 12,
            'amount_saved': 200.00
        })
        # Check for redirect after successful goal update
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('goals_view'))

    def test_update_goal_amount_view(self):
        response = self.client.post(reverse('update_goal_amount', args=[self.goal.id]), {'amount': 200.00})
        # Check for redirect after successful goal amount update
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('goals_view'))

    def test_delete_goal_view(self):
        response = self.client.post(reverse('delete_goal', args=[self.goal.id]))
        # Check for redirect after successful goal deletion
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('goals_view'))   