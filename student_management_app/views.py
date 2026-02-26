from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser


# =========================
# LOGIN PAGE
# =========================
def login_page(request):
    return render(request, "login_page.html")


# =========================
# LOGIN LOGIC (USERNAME OR EMAIL)
# =========================
def doLogin(request):
    if request.method != "POST":
        return redirect("/")

    login_input = request.POST.get("email")   # can be email OR username
    password = request.POST.get("password")

    user = None

    # 1️⃣ Try username login
    user = authenticate(request, username=login_input, password=password)

    # 2️⃣ If failed, try email login
    if user is None:
        try:
            user_obj = CustomUser.objects.get(email=login_input)
            user = authenticate(
                request,
                username=user_obj.username,
                password=password
            )
        except CustomUser.DoesNotExist:
            user = None

    if user:
        if not user.is_active:
            messages.error(request, "Account is inactive. Contact admin.")
            return redirect("/")

        login(request, user)

        # ✅ SUPERUSER → ADMIN (HOD)
        if user.is_superuser:
            return redirect("admin_home")

        # Role-based redirect
        if user.role == CustomUser.Roles.HOD:
            return redirect("admin_home")

        elif user.role == CustomUser.Roles.STAFF:
            return redirect("staff_home")

        elif user.role == CustomUser.Roles.STUDENT:
            return redirect("student_home")

        # Safety fallback
        logout(request)
        messages.error(request, "Role not assigned. Contact admin.")
        return redirect("/")

    messages.error(request, "Invalid username/email or password")
    return redirect("/")


# =========================
# LOGOUT
# =========================
def logout_user(request):
    logout(request)
    return redirect("/")


# =========================
# ADMIN (HOD) DASHBOARD
# =========================
@login_required(login_url="/")
def admin_home(request):
    if not request.user.is_superuser and request.user.role != CustomUser.Roles.HOD:
        messages.error(request, "Unauthorized access.")
        return redirect("/")
    return render(request, "hod_template/home_content.html")


# =========================
# STAFF DASHBOARD
# =========================
@login_required(login_url="/")
def staff_home(request):
    if request.user.role != CustomUser.Roles.STAFF:
        messages.error(request, "Unauthorized access.")
        return redirect("/")
    return render(request, "staff_template/home_content.html")


# =========================
# STUDENT DASHBOARD
# =========================
@login_required(login_url="/")
def student_home(request):
    if request.user.role != CustomUser.Roles.STUDENT:
        messages.error(request, "Unauthorized access.")
        return redirect("/")
    return render(request, "student_template/home_content.html")


# =========================
# STAFF-ONLY TEST VIEW
# =========================
@login_required(login_url="/")
def staff_only_view(request):
    if request.user.role != CustomUser.Roles.STAFF:
        messages.error(request, "Unauthorized access.")
        return redirect("/")
    return render(request, "staff_template/example.html")
