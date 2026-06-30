from django.urls import path

from .views import *

urlpatterns = [
    path("", home, name="home"),  # 🔥 ADD THIS

    path("login/", login_view, name="login"),

    path("register/", register, name="register"),

    path("profile/", profile, name="profile"),

    path("logout/", logout_view, name="logout"),
    path("forgot-password/",forgot_password,name="forgot_password"),
    path("reset-password/", reset_password, name="reset_password"),
]