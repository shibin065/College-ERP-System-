from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import transaction

from .models import CustomUser, Student


# ==============================
# Home & Contact
# ==============================
def home(request):
    return render(request, "home.html")


def contact(request):
    return render(request, "contact.html")


# ==============================
# Login
# ==============================
def login_view(request):

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            messages.error(request, "All fields are required.")
            return redirect("login")

        user = authenticate(request, username=email, password=password)

        if user is None:
            messages.error(request, "Invalid credentials.")
            return redirect("login")

        login(request, user)

        # Role-based redirect
        if user.role == CustomUser.Roles.STUDENT:
            return redirect("student_home")

        elif user.role == CustomUser.Roles.STAFF:
            return redirect("staff_home")

        elif user.role == CustomUser.Roles.HOD:
            return redirect("admin_home")

        return redirect("home")

    return render(request, "login_page.html")


# ==============================
# Registration (Student)
# ==============================
@transaction.atomic
def registration(request):

    if request.method == "POST":

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirmPassword")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("registration")

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("registration")

        # Create User
        user = CustomUser.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=CustomUser.Roles.STUDENT
        )

        # Create Student Profile
        Student.objects.create(user=user)

        messages.success(request, "Account created successfully.")
        return redirect("login")

    return render(request, "registration.html")


# ==============================
# Logout
# ==============================
def logout_user(request):
    logout(request)
    return redirect("home")
