from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth import logout, login
from .models import CustomUser, Staffs, Students, AdminHOD
from django.contrib import messages
from django.contrib.auth.hashers import check_password,make_password

def home(request):
    print("hi")
    return render(request, 'home.html')

def contact(request):
    return render(request, 'contact.html')

def get_user_type_from_email(email_id):
    try:
        print("entered")
        email_user_type = email_id.split('@')[0].split('.')[1]
        return CustomUser.EMAIL_TO_USER_TYPE_MAP[email_user_type]
    except:
        return None
def doLogin(request):
    if request.method == "POST":
        email_id = request.POST.get('email')
        password = request.POST.get('password')

        if not (email_id and password):
            messages.error(request, "Please provide all the details!!")
            return render(request, 'login_page.html')

        user = CustomUser.objects.filter(email=email_id).last()

        if not user or not check_password(password, user.password):
            messages.error(request, 'Invalid Login Credentials!!')
            return render(request, 'login_page.html')

        login(request, user)

        if user.user_type == CustomUser.STUDENT:
            return redirect('student_home/')
        elif user.user_type == CustomUser.STAFF:
            return redirect('staff_home/')
        elif user.user_type == CustomUser.HOD:
            return redirect('admin_home/')

        return render(request, 'home.html')
    return render(request,'login_page.html')


from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password

def doRegistration(request):
    if request.method == "POST":
        print(request.POST)
        first_name = request.POST.get('first_name')
        print(first_name)
        last_name = request.POST.get('last_name')
        email_id = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')
        print("hello")
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('doRegistration')

        if CustomUser.objects.filter(email=email_id).exists():
            messages.error(request, "Email already exists.")
            return redirect('doRegistration')

        username = email_id   # safer approach

        user = CustomUser(
            username=username,
            email=email_id,
            first_name=first_name,
            last_name=last_name,
            user_type=CustomUser.STUDENT,  # assuming constant defined
        )
        user.password = make_password(password)
        user.save()
        print("done")

        messages.success(request, "Registration successful. Please log in.")
        return redirect('doLogin')

    return render(request, 'registration.html')


def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')
