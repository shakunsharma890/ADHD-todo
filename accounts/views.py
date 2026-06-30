from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile 
from django.http import HttpResponse
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
def home(request):

    if request.user.is_authenticated:

        return redirect("dashboard")  # or profile/dashboard

    return redirect("login")
# =========================
# LOGIN
# =========================
def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            Profile.objects.get_or_create(user=user)

            return redirect("dashboard")   # ✅ direct to dashboard

        return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")


# =========================
# REGISTER
# =========================
def register(request):

    if request.method == "POST":

        username = request.POST.get("username")

        email = request.POST.get("email")

        password = request.POST.get("password")

        # ❌ check duplicate username

        if User.objects.filter(username=username).exists():

            messages.error(request, "Username already exists")

            return redirect("register")
        if User.objects.filter(email=email).exists():

            messages.error(request, "Email already exists")

            return redirect("register")
        # ✔ create user
        try:
        
            validate_password(password)

        except ValidationError as e:
        
            messages.error(request, e.messages[0])

            return redirect("register")
        user = User.objects.create_user(

            username=username,

            email=email,

            password=password

        )

        # ✔ login immediately

        login(request, user)

        # ✔ create profile safely

        Profile.objects.get_or_create(user=user)

        # ✔ first-time onboarding

        return redirect("dashboard")

    return render(request, "register.html")


# =========================
# PROFILE
# =========================
@login_required
def profile(request):

    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        bio = request.POST.get("bio")

        # update user table
        request.user.first_name = name
        request.user.email = email
        request.user.save()

        # update profile table
        profile.bio = bio
        profile.save()

        return redirect("profile")

    return render(request, "profile.html", {
        "profile": profile
    })


# =========================
# LOGOUT
# =========================
@login_required
def logout_view(request):
    logout(request)
    return redirect("login")

def forgot_password(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")

        user = User.objects.filter(
            username=username,
            email=email
        ).first()

        if user:
            request.session["reset_user_id"] = user.id

            return redirect("reset_password")   # 🔥 THIS IS THE FIX
        else:
            return render(request,"forgot_password.html",{"error": "Invalid username or email"})
    return render(request, "forgot_password.html")

def reset_password(request):

    user_id = request.session.get("reset_user_id")

    if not user_id:

        return redirect("forgot_password")

    user = User.objects.get(id=user_id)

    if request.method == "POST":

        new_password = request.POST.get("password")
        try:

            validate_password(new_password, user)

        except ValidationError as e:
        
            return render(
            
                request,

                "reset_password.html",

                {"error": e.messages[0]}

            )
        user.set_password(new_password)

        user.save()

        # clear session after reset
        messages.success(request, "Password updated successfully")
        request.session.pop("reset_user_id", None)

        return redirect("login")

    return render(request, "reset_password.html")

