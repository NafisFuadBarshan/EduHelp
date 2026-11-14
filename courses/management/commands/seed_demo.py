from django.core.management.base import BaseCommand

from accounts.models import User
from courses.models import Course, Enrollment, Lesson, Question

DEMO_PASSWORD = "eduhelp-demo-123"


class Command(BaseCommand):
    help = "Create demo users (admin, teacher, student) and a few approved courses."

    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(
            username="admin", defaults={"email": "admin@example.com", "is_staff": True, "is_superuser": True}
        )
        teacher, _ = User.objects.get_or_create(
            username="teacher", defaults={"email": "teacher@example.com", "role": User.Role.TEACHER}
        )
        student, _ = User.objects.get_or_create(
            username="student", defaults={"email": "student@example.com", "role": User.Role.STUDENT}
        )
        for user in (admin, teacher, student):
            user.set_password(DEMO_PASSWORD)
            user.save()

        catalog = [
            ("Python for Beginners", "Variables, loops, functions and small projects, taught step by step.", 0,
             ["Setting up Python", "Variables and types", "Loops and conditions", "Writing functions"]),
            ("Web Development with Django", "Build and deploy a database-backed website with authentication.", 29,
             ["Project layout", "Models and the admin", "Views and templates", "User accounts"]),
            ("Data Analysis Basics", "Clean, explore and chart real datasets using pandas.", 19,
             ["Loading data", "Cleaning messy columns", "Grouping and summaries", "Making charts"]),
        ]
        for title, description, price, lessons in catalog:
            course, created = Course.objects.get_or_create(
                title=title,
                defaults={"description": description, "price": price, "teacher": teacher, "is_approved": True},
            )
            if created:
                for number, lesson_title in enumerate(lessons, start=1):
                    Lesson.objects.create(
                        course=course,
                        title=lesson_title,
                        order=number,
                        content=f"Notes for “{lesson_title}” go here. Edit this lesson from the teacher dashboard.",
                    )

        first = Course.objects.filter(teacher=teacher).first()
        if first:
            Enrollment.objects.get_or_create(student=student, course=first)
            Question.objects.get_or_create(
                course=first, student=student, text="Which Python version should I install?"
            )

        self.stdout.write(self.style.SUCCESS("Demo data ready."))
        self.stdout.write(f"  admin / teacher / student  (password: {DEMO_PASSWORD})")
