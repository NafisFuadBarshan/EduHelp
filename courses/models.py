from django.conf import settings
from django.db import models
from django.urls import reverse


class Course(models.Model):
    """Created by a teacher; only visible in the catalog once an admin approves it."""

    title = models.CharField(max_length=160)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses_taught",
        limit_choices_to={"role": "teacher"},
    )
    is_approved = models.BooleanField(default=False, help_text="Only approved courses appear in the catalog.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("courses:detail", args=[self.pk])

    @property
    def is_free(self):
        return self.price == 0


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=160)
    content = models.TextField(blank=True)
    video_url = models.URLField(blank=True, help_text="Optional link to a video for this lesson.")
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.course.title}: {self.title}"


class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-enrolled_at"]
        constraints = [
            models.UniqueConstraint(fields=["student", "course"], name="unique_enrollment"),
        ]

    def __str__(self):
        return f"{self.student} in {self.course}"


class Question(models.Model):
    """A student asks, the course's teacher answers."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="questions")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    answer = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student}: {self.text[:50]}"

    @property
    def is_answered(self):
        return bool(self.answer)
