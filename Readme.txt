Little Lemon Django REST Framework API
======================================

Project: littlelemon
Application: restaurant

SETUP
-----
Requirements: Python 3.13, Pipenv, and a running MySQL server.

1. Create a MySQL database named littlelemon.
2. From this directory, run:

   pipenv install
   pipenv run python manage.py migrate
   pipenv run python manage.py runserver

The database defaults can be overridden with MYSQL_DATABASE, MYSQL_USER,
MYSQL_PASSWORD, MYSQL_HOST, and MYSQL_PORT. The default database engine is
MySQL. Set LITTLELEMON_DB_ENGINE=sqlite3 to use the local SQLite database for
development or tests.

Run the test suite with SQLite:

   $env:LITTLELEMON_DB_ENGINE='sqlite3'
   pipenv run python manage.py test

HTML PAGES
----------
GET /                 Booking form
GET /menu/            Menu page, populated from menu records

API PATHS
---------
GET, POST       /api/bookings/
GET, PUT, PATCH, DELETE /api/bookings/{id}/
GET             /api/menu-items/
POST            /api/menu-items/ (admin token required)
GET             /api/menu-items/{id}/
PUT, PATCH, DELETE /api/menu-items/{id}/ (admin token required)
GET             /api/categories/
POST             /api/registration/
POST             /api/token/login/
POST             /api/token/logout/

Booking and menu write operations require a token. Menu reads and registration
are public. Registration and token endpoints are provided by Djoser. The
standard Djoser registration endpoint /auth/users/ and token endpoint
/auth/token/login/ are also available.

INSOMNIA EXAMPLES
-----------------
Register a user:
POST http://127.0.0.1:8000/api/registration/
Content-Type: application/json

{"username":"reviewer","password":"StrongPass123!"}

Log in to receive a token:
POST http://127.0.0.1:8000/api/token/login/
Content-Type: application/json

{"username":"reviewer","password":"StrongPass123!"}

The response contains auth_token. For protected requests, set the header:
Authorization: Token <auth_token>

Create a booking:
POST http://127.0.0.1:8000/api/bookings/
Content-Type: application/json
Authorization: Token <auth_token>

{"first_name":"Ari","reservation_date":"2026-10-21","reservation_slot":"10:00"}

Example response (201 Created):
{"id":1,"first_name":"Ari","reservation_date":"2026-10-21","reservation_slot":"10:00"}

Create a menu item (admin token required):
POST http://127.0.0.1:8000/api/menu-items/
Content-Type: application/json
Authorization: Token <admin_auth_token>

{"title":"Lemon Pasta","price":"12.50","category":1,"featured":false}

Example response (201 Created):
{"id":1,"title":"Lemon Pasta","price":"12.50","category":1,"featured":false}

For CRUD requests, send PUT with the complete resource fields to
/api/bookings/{id}/ or /api/menu-items/{id}/, and DELETE to the same path.
Only one booking can use a given date and reservation slot; a duplicate is
rejected with HTTP 400 by the API.