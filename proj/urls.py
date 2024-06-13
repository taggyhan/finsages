from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('transactions/', views.list_transactions, name='list_transactions'),
    path('transactions/add/', views.add_transaction, name='add_transaction'),
    path('delete_transaction/<int:transaction_id>/', views.delete_transaction, name='delete_transaction'),
    path('update-transaction/', views.update_transaction, name='update_transaction'),
    path('delete-transaction/<int:transaction_id>/', views.delete_transaction, name='delete_transaction'),
    path('analysis/', views.analysis, name='analysis'),
    path('chatbot/', views.chatbot_view, name='chatbot'),
]

