# intex
Repo for Django web app for index

Authors: Kalvin Wettstein, Zachary Heaton, Stephen Williams, Spencer Jackson.

Steps to get set up:

1. Clone Repository
3. In postgres create a "opioid" database
5. Run the sql scripts (given separately) to populate the tables and data in the database
4. Change the password in "settings.py" for the database
5. Create a .env file with the following secrets
    - AZUREDBPASSWORD
    - AZUREHOST
    - AZUREUSER
    - ENV=Dev
    - DJANGOKEY
    
    These will be the values for your local environment to connect to your local database

6. Create a virtual environment if you want
7. Run the following (on windows replace psycopg2-binary with psycopg)
```
pip install django psycopg2-binary pillow requests dj-database-url django-heroku gunicorn whitenoise python-dotenv
```
8. Run this to create a login
```
python manage.py createsuperuser
```
9. Run this to start server
```
python manage.py runserver
```
11. Visit the [homepage](localhost:8000) to see the site locally

