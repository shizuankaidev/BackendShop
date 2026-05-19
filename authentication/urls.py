from django.urls import path

from .views import (
    LoginView,
    RegisterView,
    ProfileView,
    RefreshView,
    UserListView,
    MeView,
)

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("me/", MeView.as_view(), name="me"),
    path("users/", UserListView.as_view(), name="users"),
]