from django.urls import path
from .views import AdminUsersListView, AdminUserUpdateView

urlpatterns = [
    path("users/", AdminUsersListView.as_view()),
    path("users/<int:pk>/", AdminUserUpdateView.as_view())
]