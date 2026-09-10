# Course Recognition System

A Django-based thesis project for managing course recognition requests. The system supports a complete workflow between students, professors, secretariats, and administrators.

## Overview

The application allows students to submit course recognition requests for courses in their study program. Professors can review requests for the courses they are responsible for and submit recommendations. Secretariats manage protocol numbers, course-professor assignments, final decisions, inactive requests, and exports. Administrators can create student and secretariat users and manage all course recognition requests.

## Roles

- Student: creates course recognition requests, views their own requests, and edits requests only while they are under review and have no pending professor recommendation.
- Professor: views only requests related to courses they are responsible for and submits recommendations.
- Secretariat: manages requests for its study program, assigns professors to courses, registers protocol numbers, submits or manages recommendations, marks requests as inactive, restores inactive requests, and exports requests.
- Administrator: creates student and secretariat users, views all requests, and has management actions similar to the secretariat.

## Main Features

- Role-based dashboards.
- Course recognition request form for students.
- Course selection filtered by the student's study program and semester.
- Autocomplete dropdowns for courses and professors.
- PDF-only file uploads for required documents.
- Manual protocol number registration.
- Professor recommendations.
- Secretariat and administrator recommendations.
- Secretariat or administrator approval/rejection of professor recommendations.
- Request status workflow: under review, approved, rejected, inactive.
- Inactive request justification and restoration.
- Excel export for visible/filtered requests.
- CSV import for bulk course-professor assignments.
- Email notifications through Celery tasks.
- Greek and English interface.
- Light and dark mode.

## Technologies

- Django
- Django Auth LDAP
- Django Crispy Forms with Bootstrap 5
- Server-side rendering with Django templates
- Django Autocomplete Light
- Celery
- Redis
- django-celery-results
- django-import-export
- OpenPyXL
- PostgreSQL
- Docker and Docker Compose

## Run With Docker

From the project directory:

```powershell
docker compose up -d --build
```

Run database migrations:

```powershell
docker compose exec web python manage.py migrate
```

Open the application:

```text
http://localhost:30100/
```

## Useful Pages

- Login: `http://localhost:30100/en/accounts/login/`
- Student dashboard: `http://localhost:30100/en/student/dashboard/`
- Professor dashboard: `http://localhost:30100/en/professor/dashboard/`
- Secretariat dashboard: `http://localhost:30100/en/secretariat/dashboard/`
- Administrator dashboard: `http://localhost:30100/en/admin/dashboard/`

Greek pages are available by replacing `/en/` with `/el/`.

## Checks And Tests

Run the Django system check:

```powershell
docker compose exec web python manage.py check
```

Run the course recognition tests:

```powershell
docker compose exec web python manage.py test course_recognition
```

Compile English translations:

```powershell
docker compose exec web python manage.py compilemessages -l en
```

## Email Notifications

The application uses Celery tasks for email notifications. During development, `DUMMY_EMAILS=True` can be used so that email messages are printed to the terminal instead of being sent.

For real email delivery, SMTP settings must be configured in the `.env` file.

## LDAP Authentication

The project includes Django Auth LDAP configuration. Real institutional login requires the university LDAP settings and access to the university network, for example through VPN.

## Notes

This project is based on the original `myfaculty` application, which includes additional department-related modules. This thesis implementation focuses on the course recognition workflow and the pages related to it.
