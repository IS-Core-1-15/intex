from django.shortcuts import render
from .models import *

# Create your views here.


def indexPageView(request):
    return render(request, 'DrugApp/index.html')


def searchPageView(request):
    print(request.method)
    if request.method == 'POST':
        # get the search key
        key = request.POST['key'].title()

        prescribers = PdPrescriber.objects.filter(
            fname__contains=key) | PdPrescriber.objects.filter(lname__contains=key)
        if len(prescribers) > 0:
            msg = f'We found {len(prescribers)} results'
        else:
            msg = f'Sorry we could not find that'
        context = {
            'data': prescribers,
            'msg': msg,
        }
        return render(request, 'DrugApp/search.html', context)
    else:
        return render(request, 'DrugApp/search.html')


def learnPageView(request):
    return render(request, 'DrugApp/learn.html')
