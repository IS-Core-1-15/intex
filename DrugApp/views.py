from django.shortcuts import render
from .models import *

# Create your views here.
def indexPageView(request):
    return render(request, 'DrugApp/search.html')

def search(request):
    key = request.POST['key']
    print(key)
    q = f"select fname, lname from pd_prescriber where fname like '%{key}%';"
    prescibers = PdPrescriber.objects.raw(q)
    context = {
        'data': prescibers,
    }
    return render(request, 'DrugApp/search.html', context)