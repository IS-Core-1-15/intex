from django.urls import path
from .views import *

urlpatterns = [
    path("search/", searchPageView, name='search'),
    path("learn/", learnPageView, name='learn'),
    path("about/", aboutPageView, name='about'),
    path("detail/person/<int:id>", personDetailPageView, name='detailPerson'),
    path("detail/drug/<int:id>", drugDetailPageView, name='detailDrug'),
    path("addPrescriber/", addPrescriberPageView, name='addPrescriber'),
    path("deletePrescriber/<int:id>",
         deletePrescriberPageView, name='deletePrescriber'),
    path("success/", successPageView, name='success'),
    path("editPrescriber/", editPrescriberPageView, name='editPrescriber'),
    path("", indexPageView, name="index"),
]
