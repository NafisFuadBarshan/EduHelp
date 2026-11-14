from django.urls import path

from . import views

app_name = "courses"

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("courses/", views.course_list, name="list"),
    path("courses/<int:pk>/", views.course_detail, name="detail"),
    path("courses/<int:pk>/enroll/", views.enroll, name="enroll"),
    path("courses/<int:pk>/ask/", views.ask_question, name="ask"),
    path("my-courses/", views.my_courses, name="my_courses"),
    # teacher
    path("teach/", views.teacher_dashboard, name="teacher_dashboard"),
    path("teach/new/", views.course_create, name="create"),
    path("teach/<int:pk>/", views.course_manage, name="manage"),
    path("teach/<int:pk>/edit/", views.course_update, name="update"),
    path("teach/<int:pk>/delete/", views.course_delete, name="delete"),
    path("teach/<int:course_pk>/lessons/new/", views.lesson_create, name="lesson_create"),
    path("lessons/<int:pk>/edit/", views.lesson_update, name="lesson_update"),
    path("lessons/<int:pk>/delete/", views.lesson_delete, name="lesson_delete"),
    path("questions/<int:pk>/answer/", views.answer_question, name="answer"),
]
