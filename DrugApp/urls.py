from django.urls import path
from .views import *

urlpatterns = [
    path("search/", searchPageView, name='search'),
    path("learn/", learnPageView, name='learn'),
    path("about/", aboutPageView, name='about'),
    path("", indexPageView, name="index"),
]
