from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

from ..models import (
    CustomUser, Staff, Courses, Subjects, Student,
    SessionYearModel, Attendance, AttendanceReport,
    LeaveReportStaff, FeedBackStaff, StudentResult
)


@login_required(login_url='/')
def staff_home(request):
    staff = Staff.objects.get(user=request.user)

    subjects = Subjects.objects.filter(staff=staff)

    courses = Courses.objects.filter(subjects__in=subjects).distinct()
    student_count = Student.objects.filter(course__in=courses).count()
    subject_count = subjects.count()

    attendance_count = Attendance.objects.filter(subject__in=subjects).count()
    leave_count = LeaveReportStaff.objects.filter(staff=staff, leave_status=1).count()

    subject_list = []
    attendance_list = []

    for subject in subjects:
        subject_list.append(subject.subject_name)
        attendance_list.append(
            Attendance.objects.filter(subject=subject).count()
        )

    students = Student.objects.filter(course__in=courses)

    student_names = []
    present_list = []
    absent_list = []

    for student in students:
        present = AttendanceReport.objects.filter(student=student, status=True).count()
        absent = AttendanceReport.objects.filter(student=student, status=False).count()

        student_names.append(student.user.first_name + " " + student.user.last_name)
        present_list.append(present)
        absent_list.append(absent)

    context = {
        "student_count": student_count,
        "attendance_count": attendance_count,
        "leave_count": leave_count,
        "subject_count": subject_count,
        "subject_list": subject_list,
        "attendance_list": attendance_list,
        "student_list": student_names,
        "attendance_present_list": present_list,
        "attendance_absent_list": absent_list,
    }

    return render(request, "staff_template/staff_home_template.html", context)


@login_required(login_url='/')
def staff_take_attendance(request):
    staff = Staff.objects.get(user=request.user)
    subjects = Subjects.objects.filter(staff=staff)
    session_years = SessionYearModel.objects.all()

    return render(
        request,
        "staff_template/take_attendance_template.html",
        {"subjects": subjects, "session_years": session_years},
    )


@login_required(login_url='/')
def staff_apply_leave(request):
    staff = Staff.objects.get(user=request.user)
    leave_data = LeaveReportStaff.objects.filter(staff=staff)

    return render(
        request,
        "staff_template/staff_apply_leave_template.html",
        {"leave_data": leave_data},
    )


@login_required(login_url='/')
def staff_apply_leave_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect("staff_apply_leave")

    staff = Staff.objects.get(user=request.user)

    LeaveReportStaff.objects.create(
        staff=staff,
        leave_date=request.POST.get("leave_date"),
        leave_message=request.POST.get("leave_message"),
        leave_status=0,
    )

    messages.success(request, "Applied for Leave")
    return redirect("staff_apply_leave")


@login_required(login_url='/')
def staff_feedback(request):
    return render(request, "staff_template/staff_feedback_template.html")


@login_required(login_url='/')
def staff_feedback_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect("staff_feedback")

    staff = Staff.objects.get(user=request.user)

    FeedBackStaff.objects.create(
        staff=staff,
        feedback=request.POST.get("feedback_message"),
        feedback_reply="",
    )

    messages.success(request, "Feedback Sent")
    return redirect("staff_feedback")


@csrf_exempt
def get_student(request):
    subject = Subjects.objects.get(id=request.POST.get("subject"))
    session_year = SessionYearModel.objects.get(id=request.POST.get("session_year"))

    students = Student.objects.filter(
        course=subject.course,
        session_year=session_year,
    )

    data = [
        {"id": student.user.id,
         "name": student.user.first_name + " " + student.user.last_name}
        for student in students
    ]

    return JsonResponse(json.dumps(data), safe=False, content_type="application/json")


@csrf_exempt
def save_attendance_data(request):
    students = json.loads(request.POST.get("student_ids"))
    subject = Subjects.objects.get(id=request.POST.get("subject_id"))
    session_year = SessionYearModel.objects.get(id=request.POST.get("session_year_id"))

    attendance = Attendance.objects.create(
        subject=subject,
        attendance_date=request.POST.get("attendance_date"),
        session_year=session_year,
    )

    for stud in students:
        student = Student.objects.get(user__id=stud["id"])
        AttendanceReport.objects.create(
            student=student,
            attendance=attendance,
            status=stud["status"],
        )

    return HttpResponse("OK")


@login_required(login_url='/')
def staff_profile(request):
    staff = Staff.objects.get(user=request.user)

    return render(
        request,
        "staff_template/staff_profile.html",
        {"user": request.user, "staff": staff},
    )


@login_required(login_url='/')
def staff_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect("staff_profile")

    request.user.first_name = request.POST.get("first_name")
    request.user.last_name = request.POST.get("last_name")

    password = request.POST.get("password")
    if password:
        request.user.set_password(password)

    request.user.save()

    staff = Staff.objects.get(user=request.user)
    staff.address = request.POST.get("address")
    staff.save()

    messages.success(request, "Profile Updated Successfully")
    return redirect("staff_profile")


@login_required(login_url='/')
def staff_add_result(request):
    staff = Staff.objects.get(user=request.user)
    subjects = Subjects.objects.filter(staff=staff)
    session_years = SessionYearModel.objects.all()

    return render(
        request,
        "staff_template/add_result_template.html",
        {"subjects": subjects, "session_years": session_years},
    )


@login_required(login_url='/')
def staff_add_result_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect("staff_add_result")

    student = Student.objects.get(user__id=request.POST.get("student_list"))
    subject = Subjects.objects.get(id=request.POST.get("subject"))

    result, _ = StudentResult.objects.get_or_create(
        student=student,
        subject=subject,
    )

    result.subject_assignment_marks = request.POST.get("assignment_marks")
    result.subject_exam_marks = request.POST.get("exam_marks")
    result.save()

    messages.success(request, "Result Saved Successfully")
    return redirect("staff_add_result")
