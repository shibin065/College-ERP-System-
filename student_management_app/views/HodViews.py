from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import json

from ..forms import AddStudentForm, EditStudentForm
from ..models import (
    CustomUser, Staff, Student, Courses, Subjects,
    SessionYearModel, Attendance, AttendanceReport,
    LeaveReportStudent, LeaveReportStaff,
    FeedBackStudent, FeedBackStaff
)

# ==============================
# ADMIN DASHBOARD
# ==============================
def admin_home(request):
    all_student_count = Student.objects.count()
    staff_count = Staff.objects.count()
    subject_count = Subjects.objects.count()
    course_count = Courses.objects.count()

    course_name_list = []
    subject_count_list = []
    student_count_list = []

    for course in Courses.objects.all():
        course_name_list.append(course.course_name)
        subject_count_list.append(Subjects.objects.filter(course=course).count())
        student_count_list.append(Student.objects.filter(course=course).count())

    context = {
        "all_student_count": all_student_count,
        "staff_count": staff_count,
        "subject_count": subject_count,
        "course_count": course_count,
        "course_name_list": course_name_list,
        "subject_count_list": subject_count_list,
        "student_count_list": student_count_list,
    }
    return render(request, "hod_template/home_content.html", context)

# ==============================
# STAFF MANAGEMENT
# ==============================
def add_staff(request):
    return render(request, "hod_template/add_staff_template.html")


def add_staff_save(request):
    if request.method != "POST":
        return redirect("add_staff")

    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")
    username = request.POST.get("username")
    email = request.POST.get("email")
    password = request.POST.get("password")
    address = request.POST.get("address")

    try:
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=CustomUser.Roles.STAFF
        )
        Staff.objects.create(user=user, address=address)
        messages.success(request, "Staff added successfully")
    except:
        messages.error(request, "Failed to add staff")

    return redirect("add_staff")


def manage_staff(request):
    return render(
        request,
        "hod_template/manage_staff_template.html",
        {"staffs": Staff.objects.all()}
    )


def delete_staff(request, staff_id):
    try:
        Staff.objects.get(user__id=staff_id).delete()
        messages.success(request, "Staff deleted")
    except:
        messages.error(request, "Failed to delete staff")
    return redirect("manage_staff")

# ==============================
# COURSE MANAGEMENT
# ==============================
def add_course(request):
    return render(request, "hod_template/add_course_template.html")


def add_course_save(request):
    if request.method == "POST":
        Courses.objects.create(course_name=request.POST.get("course"))
        messages.success(request, "Course added")
    return redirect("add_course")


def manage_course(request):
    return render(
        request,
        "hod_template/manage_course_template.html",
        {"courses": Courses.objects.all()}
    )


def delete_course(request, course_id):
    Courses.objects.filter(id=course_id).delete()
    return redirect("manage_course")

# ==============================
# SESSION YEAR
# ==============================
def add_session(request):
    return render(request, "hod_template/add_session_template.html")


def add_session_save(request):
    SessionYearModel.objects.create(
        session_start_year=request.POST.get("session_start_year"),
        session_end_year=request.POST.get("session_end_year")
    )
    return redirect("add_session")


def manage_session(request):
    return render(
        request,
        "hod_template/manage_session_template.html",
        {"session_years": SessionYearModel.objects.all()}
    )

# ==============================
# STUDENT MANAGEMENT
# ==============================
def add_student(request):
    return render(
        request,
        "hod_template/add_student_template.html",
        {"form": AddStudentForm()}
    )


def add_student_save(request):
    form = AddStudentForm(request.POST, request.FILES)
    if not form.is_valid():
        return redirect("add_student")

    profile_pic = None
    if request.FILES.get("profile_pic"):
        fs = FileSystemStorage()
        profile_pic = fs.save(
            request.FILES["profile_pic"].name,
            request.FILES["profile_pic"]
        )

    user = CustomUser.objects.create_user(
        username=form.cleaned_data["username"],
        email=form.cleaned_data["email"],
        password=form.cleaned_data["password"],
        first_name=form.cleaned_data["first_name"],
        last_name=form.cleaned_data["last_name"],
        role=CustomUser.Roles.STUDENT
    )

    Student.objects.create(
        user=user,
        address=form.cleaned_data["address"],
        gender=form.cleaned_data["gender"],
        course=form.cleaned_data["course"],
        session_year=form.cleaned_data["session_year"],
        profile_pic=profile_pic
    )

    messages.success(request, "Student added successfully")
    return redirect("add_student")


def manage_student(request):
    return render(
        request,
        "hod_template/manage_student_template.html",
        {"students": Student.objects.all()}
    )

# ==============================
# SUBJECT MANAGEMENT
# ==============================
def add_subject(request):
    return render(
        request,
        "hod_template/add_subject_template.html",
        {
            "courses": Courses.objects.all(),
            "staffs": Staff.objects.all()
        }
    )


def add_subject_save(request):
    Subjects.objects.create(
        subject_name=request.POST.get("subject"),
        course=Courses.objects.get(id=request.POST.get("course")),
        staff=Staff.objects.get(user__id=request.POST.get("staff"))
    )
    messages.success(request, "Subject added")
    return redirect("add_subject")


def manage_subject(request):
    return render(
        request,
        "hod_template/manage_subject_template.html",
        {"subjects": Subjects.objects.all()}
    )

# ==============================
# FEEDBACK
# ==============================
def student_feedback_message(request):
    return render(
        request,
        "hod_template/student_feedback_template.html",
        {"feedbacks": FeedBackStudent.objects.all()}
    )


def staff_feedback_message(request):
    return render(
        request,
        "hod_template/staff_feedback_template.html",
        {"feedbacks": FeedBackStaff.objects.all()}
    )

# ==============================
# LEAVE MANAGEMENT
# ==============================
def student_leave_view(request):
    return render(
        request,
        "hod_template/student_leave_view.html",
        {"leaves": LeaveReportStudent.objects.all()}
    )


def staff_leave_view(request):
    return render(
        request,
        "hod_template/staff_leave_view.html",
        {"leaves": LeaveReportStaff.objects.all()}
    )

# ==============================
# ATTENDANCE (ADMIN VIEW)
# ==============================
def admin_view_attendance(request):
    return render(
        request,
        "hod_template/admin_view_attendance.html",
        {
            "subjects": Subjects.objects.all(),
            "session_years": SessionYearModel.objects.all()
        }
    )


@csrf_exempt
def admin_get_attendance_dates(request):
    subject = Subjects.objects.get(id=request.POST.get("subject"))
    session_year = SessionYearModel.objects.get(id=request.POST.get("session_year_id"))

    attendance = Attendance.objects.filter(
        subject=subject,
        session_year=session_year
    )

    data = [
        {
            "id": att.id,
            "attendance_date": str(att.attendance_date)
        }
        for att in attendance
    ]

    return JsonResponse(json.dumps(data), safe=False)

