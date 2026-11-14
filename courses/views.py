from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.decorators import teacher_required

from .forms import AnswerForm, CourseForm, LessonForm, QuestionForm
from .models import Course, Enrollment, Lesson, Question


def home(request):
    featured = Course.objects.filter(is_approved=True).select_related("teacher")[:3]
    return render(request, "home.html", {"featured": featured})


@login_required
def dashboard(request):
    """Send each role to its own landing page."""
    if request.user.is_teacher:
        return redirect("courses:teacher_dashboard")
    if request.user.is_staff:
        return redirect("admin:index")
    return redirect("courses:my_courses")


# ---------- catalog (Buy Courses) ----------

def course_list(request):
    courses = Course.objects.filter(is_approved=True).select_related("teacher")
    query = request.GET.get("q", "").strip()
    if query:
        courses = courses.filter(Q(title__icontains=query) | Q(description__icontains=query))
    enrolled_ids = set()
    if request.user.is_authenticated:
        enrolled_ids = set(request.user.enrollments.values_list("course_id", flat=True))
    return render(
        request,
        "courses/course_list.html",
        {"courses": courses, "query": query, "enrolled_ids": enrolled_ids},
    )


def course_detail(request, pk):
    course = get_object_or_404(Course.objects.select_related("teacher"), pk=pk)
    user = request.user
    is_owner = user.is_authenticated and course.teacher_id == user.id
    if not course.is_approved and not (is_owner or user.is_staff):
        raise Http404

    enrolled = user.is_authenticated and Enrollment.objects.filter(student=user, course=course).exists()
    has_access = is_owner or user.is_staff or enrolled
    context = {
        "course": course,
        "is_owner": is_owner,
        "enrolled": enrolled,
        "has_access": has_access,
        "lesson_count": course.lessons.count(),
    }
    if has_access:
        context["lessons"] = course.lessons.all()
        context["questions"] = course.questions.select_related("student")
    if enrolled and user.is_student:
        context["question_form"] = QuestionForm()
    if is_owner:
        context["answer_form"] = AnswerForm()
    return render(request, "courses/course_detail.html", context)


@login_required
@require_POST
def enroll(request, pk):
    course = get_object_or_404(Course, pk=pk, is_approved=True)
    if not request.user.is_student:
        messages.error(request, "Only student accounts can enroll in courses.")
        return redirect(course)
    _, created = Enrollment.objects.get_or_create(student=request.user, course=course)
    if created:
        messages.success(request, f"You are enrolled in {course.title}.")
    else:
        messages.info(request, "You are already enrolled in this course.")
    return redirect(course)


# ---------- student ----------

@login_required
def my_courses(request):
    enrollments = request.user.enrollments.select_related("course", "course__teacher")
    return render(request, "courses/my_courses.html", {"enrollments": enrollments})


@login_required
@require_POST
def ask_question(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        raise PermissionDenied
    form = QuestionForm(request.POST)
    if form.is_valid():
        question = form.save(commit=False)
        question.course = course
        question.student = request.user
        question.save()
        messages.success(request, "Question sent. Your teacher will reply here.")
    else:
        messages.error(request, "Write your question before sending it.")
    return redirect(course)


# ---------- teacher ----------

@teacher_required
def teacher_dashboard(request):
    courses = request.user.courses_taught.all()
    pending = Question.objects.filter(course__teacher=request.user, answer="").count()
    return render(request, "courses/teacher_dashboard.html", {"courses": courses, "pending": pending})


@teacher_required
def course_create(request):
    form = CourseForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        course = form.save(commit=False)
        course.teacher = request.user
        course.save()
        messages.success(request, "Course saved. It appears in the catalog once an admin approves it.")
        return redirect("courses:manage", pk=course.pk)
    return render(request, "courses/course_form.html", {"form": form, "heading": "New course"})


@teacher_required
def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk, teacher=request.user)
    form = CourseForm(request.POST or None, instance=course)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Course updated.")
        return redirect("courses:manage", pk=course.pk)
    return render(request, "courses/course_form.html", {"form": form, "heading": "Edit course"})


@teacher_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk, teacher=request.user)
    if request.method == "POST":
        course.delete()
        messages.success(request, "Course deleted.")
        return redirect("courses:teacher_dashboard")
    return render(
        request,
        "courses/confirm_delete.html",
        {"what": f"the course “{course.title}”", "note": "Its lessons, enrollments and questions will be deleted too.", "cancel": course.get_absolute_url()},
    )


@teacher_required
def course_manage(request, pk):
    course = get_object_or_404(Course, pk=pk, teacher=request.user)
    return render(
        request,
        "courses/course_manage.html",
        {
            "course": course,
            "lessons": course.lessons.all(),
            "questions": course.questions.select_related("student"),
            "answer_form": AnswerForm(),
            "student_count": course.enrollments.count(),
        },
    )


@teacher_required
def lesson_create(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk, teacher=request.user)
    next_order = course.lessons.count() + 1
    form = LessonForm(request.POST or None, initial={"order": next_order})
    if request.method == "POST" and form.is_valid():
        lesson = form.save(commit=False)
        lesson.course = course
        lesson.save()
        messages.success(request, "Lesson added.")
        return redirect("courses:manage", pk=course.pk)
    return render(request, "courses/lesson_form.html", {"form": form, "course": course, "heading": "New lesson"})


@teacher_required
def lesson_update(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk, course__teacher=request.user)
    form = LessonForm(request.POST or None, instance=lesson)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Lesson updated.")
        return redirect("courses:manage", pk=lesson.course_id)
    return render(
        request, "courses/lesson_form.html", {"form": form, "course": lesson.course, "heading": "Edit lesson"}
    )


@teacher_required
def lesson_delete(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk, course__teacher=request.user)
    course_id = lesson.course_id
    if request.method == "POST":
        lesson.delete()
        messages.success(request, "Lesson deleted.")
        return redirect("courses:manage", pk=course_id)
    return render(
        request,
        "courses/confirm_delete.html",
        {"what": f"the lesson “{lesson.title}”", "note": "", "cancel": lesson.course.get_absolute_url()},
    )


@teacher_required
@require_POST
def answer_question(request, pk):
    question = get_object_or_404(Question, pk=pk, course__teacher=request.user)
    form = AnswerForm(request.POST)
    if form.is_valid():
        question.answer = form.cleaned_data["answer"]
        question.answered_at = timezone.now()
        question.save()
        messages.success(request, "Answer posted.")
    else:
        messages.error(request, "Write an answer before posting.")
    return redirect("courses:manage", pk=question.course_id)
