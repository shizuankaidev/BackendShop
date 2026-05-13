from django.urls import path
from .views import AdminUsersListView

urlpatterns = [
    path("users/", AdminUsersListView.as_view()),
]