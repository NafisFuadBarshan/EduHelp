# EduHelp: Student-Teacher Support Platform

A Django e-learning platform for course creation, enrollment and content management,
with secure authentication and admin-controlled course operations.

## Roles

| Role | What they can do |
|------|------------------|
| Student | Register, browse and enroll in approved courses, read lessons, ask the teacher questions |
| Teacher | Register, create/edit/delete their own courses and lessons, answer student questions |
| Admin | Approve or hide courses, manage users, enrollments and questions in `/admin/` |

New courses stay hidden until an admin approves them (tick **Is approved** in the admin list,
or use the "Approve selected courses" action).

## Run it

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py makemigrations accounts courses
python manage.py migrate
python manage.py seed_demo        # optional: demo users + 3 courses
python manage.py runserver
```

Open http://127.0.0.1:8000/

Demo logins after `seed_demo` (password `eduhelp-demo-123`): `admin`, `teacher`, `student`.
For a real admin account use `python manage.py createsuperuser` instead and delete the demo users.

## Project layout

```
eduhelp/     settings, root urls
accounts/    custom User (student/teacher role), register, login, logout
courses/     Course, Lesson, Enrollment, Question; views, forms, admin, seed command
templates/   base layout, home, catalog, dashboards, forms
static/css/  eduhelp.css (dark theme, green About band, blue buttons)
```

## Before deploying

Set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0` and `DJANGO_ALLOWED_HOSTS`, then run
`python manage.py collectstatic`. Enrolling is a simple one-click action; connect a payment
provider in `courses.views.enroll` if you want real purchases.
