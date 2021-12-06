# intex
Repo for Django web app for index

Authors: Kalvin Wettstein, Zachary Heaton, Stephen Williams, Spencer Jackson.

Steps to get set up:

1. Clone Repository
3. In postgres create a "opioid" database
5. Run the sql scripts (given separately) to populate the tables and data in the database
4. Change the password in "settings.py" for the database

5. Create a virtual env if you want.
6. Run the following (on windows replace psycopg2-binary with psycopg)
```
pip install django psycopg2-binary pillow requests dj-database-url django-heroku gunicorn whitenoise python-dotenv
```
7. Run this to create a login
```
python manage.py createsuperuser
```
8. Run this to start server
```
python manage.py runserver
```
10. Visit the [homepage](localhost:8000) to see the site locally

