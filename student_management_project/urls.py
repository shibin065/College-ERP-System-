from django.contrib import admin
from django.urls import path

from student_management_app import views
from student_management_app.HodViews import *
from student_management_app.StaffViews import *
from student_management_app.StudentViews import *

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Authentication
    path('', views.login_page, name='login'),
    path('doLogin/', views.doLogin, name='doLogin'),
    path('logout/', views.logout_user, name='logout'),

    # Dashboards
    path('admin_home/', admin_home, name='admin_home'),
    path('hod_home/', admin_home, name='hod_home'),
    path('staff_home/', staff_home, name='staff_home'),
    path('student_home/', student_home, name='student_home'),
]
