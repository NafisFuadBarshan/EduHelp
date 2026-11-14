from django.contrib import admin, messages

from .models import Course, Enrollment, Lesson, Question


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher", "price", "is_approved", "created_at")
    list_filter = ("is_approved", "teacher")
    list_editable = ("is_approved",)
    search_fields = ("title", "description", "teacher__username")
    inlines = [LessonInline]
    actions = ["approve_courses", "unapprove_courses"]

    @admin.action(description="Approve selected courses")
    def approve_courses(self, request, queryset):
        count = queryset.update(is_approved=True)
        self.message_user(request, f"{count} course(s) approved.", messages.SUCCESS)

    @admin.action(description="Remove selected courses from the catalog")
    def unapprove_courses(self, request, queryset):
        count = queryset.update(is_approved=False)
        self.message_user(request, f"{count} course(s) hidden from the catalog.", messages.SUCCESS)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "enrolled_at")
    list_filter = ("course",)
    search_fields = ("student__username", "course__title")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "student", "course", "created_at", "is_answered")
    list_filter = ("course",)
