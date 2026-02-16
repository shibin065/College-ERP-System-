from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser


def login_page(request):
    return render(request, "login_page.html")


def doLogin(request):
    if request.method != "POST":
        return redirect("/")

    email = request.POST.get("email")
    password = request.POST.get("password")

    try:
        user_obj = CustomUser.objects.get(email=email)
        user = authenticate(
            request,
            username=user_obj.username,
            password=password
        )
    except CustomUser.DoesNotExist:
        user = None

    if user:
        login(request, user)

        if user.role == CustomUser.Roles.HOD:
            return redirect("admin_home")

        elif user.role == CustomUser.Roles.STAFF:
            return redirect("staff_home")

        elif user.role == CustomUser.Roles.STUDENT:
            return redirect("student_home")

        else:
            logout(request)
            messages.error(request, "Role not assigned")
            return redirect("/")

    messages.error(request, "Invalid email or password")
    return redirect("/")



def logout_user(request):
    logout(request)
    return redirect("/")


@login_required(login_url='/')
def admin_home(request):
    return render(request, "hod_template/home_content.html")


@login_required(login_url='/')
def staff_home(request):
    return render(request, "staff_template/home_content.html")


@login_required(login_url='/')
def student_home(request):
    return render(request, "student_template/home_content.html")


@login_required(login_url='/')
def staff_only_view(request):
    if request.user.role != CustomUser.Roles.STAFF:
        return redirect("/")
    return render(request, "staff_template/example.html")

