from django.urls import path
from .views import indexPageView, search

urlpatterns = [
    path("search/", search, name='search'),
    path("", indexPageView, name="index"),
]
