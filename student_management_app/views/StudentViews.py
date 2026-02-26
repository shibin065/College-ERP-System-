from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import datetime

from ..models import (
    CustomUser, Courses, Subjects, Student,
    Attendance, AttendanceReport,
    LeaveReportStudent, FeedBackStudent, StudentResult
)


from django.contrib.auth.decorators import login_required

@login_required
def student_home(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found")
        return redirect("/")

    return render(request, "student_template/student_home_template.html", {
        "student": student
    })


@login_required(login_url='/')
def student_view_attendance_post(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect("student_view_attendance")

    subject_id = request.POST.get("subject")
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")

    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

    subject = Subjects.objects.get(id=subject_id)
    student = Student.objects.get(user=request.user)

    attendance = Attendance.objects.filter(
        subject=subject,
        attendance_date__range=(start_date, end_date)
    )

    attendance_reports = AttendanceReport.objects.filter(
        attendance__in=attendance,
        student=student
    )

    context = {
        "subject_obj": subject,
        "attendance_reports": attendance_reports,
    }

    return render(request, "student_template/student_attendance_data.html", context)


@login_required(login_url='/')
def student_apply_leave(request):
    student = Student.objects.get(user=request.user)
    leave_data = LeaveReportStudent.objects.filter(student=student)

    return render(
        request,
        "student_template/student_apply_leave.html",
        {"leave_data": leave_data},
    )


@login_required(login_url='/')
def student_apply_leave_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect("student_apply_leave")

    leave_date = request.POST.get("leave_date")
    leave_message = request.POST.get("leave_message")

    student = Student.objects.get(user=request.user)

    LeaveReportStudent.objects.create(
        student=student,
        leave_date=leave_date,
        leave_message=leave_message,
        leave_status=0,
    )

    messages.success(request, "Applied for Leave")
    return redirect("student_apply_leave")


@login_required(login_url='/')
def student_feedback(request):
    student = Student.objects.get(user=request.user)
    feedback_data = FeedBackStudent.objects.filter(student=student)

    return render(
        request,
        "student_template/student_feedback.html",
        {"feedback_data": feedback_data},
    )


@login_required(login_url='/')
def student_feedback_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect("student_feedback")

    feedback = request.POST.get("feedback_message")
    student = Student.objects.get(user=request.user)

    FeedBackStudent.objects.create(
        student=student,
        feedback=feedback,
        feedback_reply="",
    )

    messages.success(request, "Feedback Sent")
    return redirect("student_feedback")


@login_required(login_url='/')
def student_profile(request):
    student = Student.objects.get(user=request.user)

    return render(
        request,
        "student_template/student_profile.html",
        {"user": request.user, "student": student},
    )


@login_required(login_url='/')
def student_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect("student_profile")

    request.user.first_name = request.POST.get("first_name")
    request.user.last_name = request.POST.get("last_name")

    password = request.POST.get("password")
    if password:
        request.user.set_password(password)

    request.user.save()

    student = Student.objects.get(user=request.user)
    student.address = request.POST.get("address")
    student.save()

    messages.success(request, "Profile Updated Successfully")
    return redirect("student_profile")


@login_required(login_url='/')
def student_view_result(request):
    student = Student.objects.get(user=request.user)
    student_result = StudentResult.objects.filter(student=student)

    return render(
        request,
        "student_template/student_view_result.html",
        {"student_result": student_result},
    )
