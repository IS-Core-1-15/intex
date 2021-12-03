from django.db.models import Avg, Sum
from django.db.models.aggregates import Max
import random
from django.shortcuts import redirect, render
from .models import *
import math

# Create your views here.


def indexPageView(request):
    return render(request, 'DrugApp/index.html')


def searchPageView(request):
    if request.method == 'POST':
        # get the search key
        key = request.POST['key'].title()
        if key == '' or key == " ":
            context = {
                'msg': 'Please enter a value'
            }
            return render(request, 'DrugApp/search.html', context)
        if request.POST['choice'] == 'Prescriber':
            data = PdPrescriber.objects.filter(
                fname__contains=key) | PdPrescriber.objects.filter(lname__contains=key)
            context = {
                'prescriber': True,
            }
        else:
            data = PdDrugs.objects.filter(
                drugname__contains=key.upper())
            context = {
                'drug': True,
            }

        if len(data) > 0:
            msg = f'We found {len(data)} results'
        else:
            msg = f'Sorry we could not find anything with the value'

        context['data'] = data
        context['msg'] = msg

        return render(request, 'DrugApp/search.html', context)
    else:
        return render(request, 'DrugApp/search.html')


def learnPageView(request):
    return render(request, 'DrugApp/learn.html')


def aboutPageView(request):
    return render(request, 'DrugApp/about.html')

def personDetailPageView(request, id):
    person = PdPrescriber.objects.get(npi=id)
    # creds = f''
    # print(person.credentials2 == None)
    # print(type(person.credentials2))
    # if person.credentials1 != None:
    #     creds += f'{person.credentials1}'
    # if person.credentials2 != None:
    #     creds += f', {person.credentials2}'
    # if person.credentials3 != None:
    #     creds += f', {person.credentials3}'
    # if person.credentials4 != None:
    #     creds += f', {person.credentials4}'

    # creds = f'{person.credentials1}, {person.credentials2}, {person.credentials3}, {person.credentials4}'
    # person.credentials = creds

    drugs = person.drugs.all()

    for drug in drugs:
        drugQty = PdTriple.objects.get(prescriberid=id, drugname=drug.drugname)
        mymax = PdTriple.objects.filter(prescriberid=id).aggregate(Sum('qty'))
        drug.sum = mymax['qty__sum']
        drug.qty = drugQty.qty
        avg = PdTriple.objects.filter(drugname=drug.drugname).aggregate(Avg('qty'))
        drug.avg = round(avg['qty__avg'], 2)
        drug.percent = math.floor((drug.qty / drug.sum) * 100)

    context = {
        'info': person,
        'drugs': drugs,
    }

    return render(request, 'DrugApp/details/p_detail.html', context)

def drugDetailPageView(request, id):
    drug = PdDrugs.objects.get(drugid=id)
    ten = PdTriple.objects.filter(drugname=drug.drugname).order_by('-qty')[:10]
    
    context = {
        'drug': drug,
        'persons': ten
    }
    return render(request, 'DrugApp/details/d_detail.html', context)

def addPrescriberPageView(request):
    print(request.method)
    if request.method == 'GET':
        states = PdStatedata.objects.all()

        context = {
            'states': states
        }
        return render(request, 'DrugApp/addPrescriber.html', context)
    elif request.method == 'POST':
        person = PdPrescriber.create(request.POST)
        person.save()
        print(person)
 
        return redirect('detailPerson', id=person.npi)
    else:
        return render(request, 'DrugApp/error', {'msg': 'There was an error'})

def deletePrescriberPageView(request, id):
    person = PdPrescriber.objects.get(npi=id)
    if len(person) < 1 or len(person) > 1:
        context = {
            'msg': 'Sorry there was an error handling your request',
        }
        return render(request, 'DrugApp/error.html', context)
    person.delete()
    return render(request, 'DrugApp/search.html')
