from django.contrib.auth.models import AbstractUser
from django.db import models


# ==============================
# Session Year
# ==============================
class SessionYearModel(models.Model):
    session_start_year = models.DateField()
    session_end_year = models.DateField()

    def __str__(self):
        return f"{self.session_start_year} - {self.session_end_year}"


# ==============================
# Custom User Model
# ==============================
class CustomUser(AbstractUser):

    class Roles(models.TextChoices):
        HOD = "HOD", "HOD"
        STAFF = "STAFF", "Staff"
        STUDENT = "STUDENT", "Student"

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.STUDENT
    )

    def __str__(self):
        return self.email


# ==============================
# Admin Profile
# ==============================
class AdminHOD(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email


# ==============================
# Staff Profile
# ==============================
class Staff(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.user.email


# ==============================
# Courses
# ==============================
class Courses(models.Model):
    course_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.course_name


# ==============================
# Subjects
# ==============================
class Subjects(models.Model):
    subject_name = models.CharField(max_length=255)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)

    def __str__(self):
        return self.subject_name


# ==============================
# Student Profile
# ==============================
class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    gender = models.CharField(max_length=20, blank=True)
    profile_pic = models.ImageField(upload_to="student/", blank=True)
    address = models.TextField(blank=True)
    course = models.ForeignKey(Courses, on_delete=models.SET_NULL, null=True)
    session_year = models.ForeignKey(SessionYearModel, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.email


# ==============================
# Attendance
# ==============================
class Attendance(models.Model):
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    attendance_date = models.DateField()
    session_year = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.subject} - {self.attendance_date}"


class AttendanceReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)


# ==============================
# Leave System
# ==============================
class LeaveReportStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    leave_date = models.DateField()
    leave_message = models.TextField()
    leave_status = models.IntegerField(default=0)


class LeaveReportStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    leave_date = models.DateField()
    leave_message = models.TextField()
    leave_status = models.IntegerField(default=0)


# ==============================
# Feedback System
# ==============================
class FeedBackStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField(blank=True)


class FeedBackStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField(blank=True)


# ==============================
# Notifications
# ==============================
class NotificationStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class NotificationStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


# ==============================
# Student Results
# ==============================
class StudentResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    subject_exam_marks = models.FloatField(default=0)
    subject_assignment_marks = models.FloatField(default=0)

    def total_marks(self):
        return self.subject_exam_marks + self.subject_assignment_marks
