from django.urls import path
from .views import indexPageView, search

urlpatterns = [
    path("", indexPageView, name="index"),
    path("", search, name='search')
]
