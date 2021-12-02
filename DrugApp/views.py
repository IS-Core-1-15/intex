from django.shortcuts import render
from .models import *

# Create your views here.


def indexPageView(request):
    return render(request, 'DrugApp/index.html')


def searchPageView(request):
    if request.method == 'POST':
        # get the search key
        key = request.POST['key'].title()

        if request.POST['choice'] == 'Prescriber':
            data = PdPrescriber.objects.filter(
                fname__contains=key) | PdPrescriber.objects.filter(lname__contains=key)
        else:
            data = PdDrugs.objects.filter(
                drugname__contains=key)

        if len(data) > 0:
            msg = f'We found {len(data)} results'
        else:
            msg = f'Sorry we could not find that'
        context = {
            'data': data,
            'msg': msg,
        }

        return render(request, 'DrugApp/search.html', context)
    else:
        return render(request, 'DrugApp/search.html')


def learnPageView(request):
    return render(request, 'DrugApp/learn.html')
