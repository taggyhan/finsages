from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("transactions/", views.list_transactions, name="list_transactions"),
    path("transactions/add/", views.add_transaction, name="add_transaction"),
    path(
        "delete_transaction/<int:transaction_id>/",
        views.delete_transaction,
        name="delete_transaction",
    ),
    path("update-transaction/", views.update_transaction, name="update_transaction"),
    path(
        "delete-transaction/<int:transaction_id>/",
        views.delete_transaction,
        name="delete_transaction",
    ),
    path("analysis/", views.analysis, name="analysis"),
    path("chatbot/", views.chatbot_view, name="chatbot"),
    path("goals/", views.goals_view, name="goals_view"),
    path("goals/add/", views.add_goal, name="add_goal"),
    path("goals/update/<int:goal_id>/", views.update_goal, name="update_goal"),
    path(
        "goals/update_amount/<int:goal_id>/",
        views.update_goal_amount,
        name="update_goal_amount",
    ),
    path("goal/delete/<int:goal_id>/", views.delete_goal, name="delete_goal"),
    path(
        "transactions-by-category/",
        views.transactions_by_category,
        name="transactions_by_category",
    ),
]
