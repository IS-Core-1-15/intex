from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(PdDrugs)
admin.site.register(PdPrescriber)
admin.site.register(PdTriple)
admin.site.register(PdStatedata)