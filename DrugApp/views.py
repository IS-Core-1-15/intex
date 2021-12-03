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
    print(id)
    person = PdPrescriber.objects.get(npi=id)
    drugs = person.drugs.all()

    for drug in drugs:
        drugQty = PdTriple.objects.get(prescriberid=id, drugname=drug.drugname)
        mymax = PdTriple.objects.filter(prescriberid=id).aggregate(Sum('qty'))
        drug.sum = mymax['qty__sum']
        drug.qty = drugQty.qty
        avg = PdTriple.objects.filter(
            drugname=drug.drugname).aggregate(Avg('qty'))
        drug.avg = round(avg['qty__avg'], 2)
        drug.percent = math.floor((drug.qty / drug.sum) * 100)

    context = {
        'person': person,
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
        return render(request, 'DrugApp/prescriber/addPrescriber.html', context)
    elif request.method == 'POST':
        person = PdPrescriber.create(request.POST)
        person.save()
        return redirect('detailPerson', id=person.npi)
    else:
        return render(request, 'DrugApp/error', {'msg': 'There was an error'})


def deletePrescriberPageView(request, id):
    person = PdPrescriber.objects.get(npi=id)
    # TODO: add in a validator
    person.delete()
    return redirect('success')


def addDrugPageView(request, id):
    person = PdPrescriber.objects.get(npi=id)
    triple = PdTriple.objects.filter(prescriberid=id)
    excludes = []
    for t in triple:
        excludes.append(t.drugname)

    if request.method == 'GET':
        drugs = PdDrugs.objects.all().exclude(drugname__in=excludes)
        context = {
            'person': person,
            'drugs': drugs,
        }
        return render(request, 'DrugApp/drug/addDrug.html', context)
    elif request.method == 'POST':
        tripleID = random.randint(0, 999999)
        triple = PdTriple.create(tripleID, person, request.POST)
        triple.save()
        return redirect('detailPerson', id=id)

def editDrugPageView(request, drugid, personid):
    drug = PdDrugs.objects.get(drugid=drugid)
    triple = PdTriple.objects.get(prescriberid=personid, drugname=drug.drugname)        
    person = triple.prescriberid

    if request.method == "GET":
        context = {
            'person': person,
            'drug': drug,
            'triple': triple,
        }
        return render(request, 'DrugApp/drug/editDrug.html', context)
    elif request.method == "POST":
        triple.qty = request.POST['qty']
        triple.save()
        return redirect('detailPerson', id=person.npi)

def deleteDrugPageView(request, drugid, personid):
    drug = PdDrugs.objects.get(drugid=drugid)
    triple = PdTriple.objects.get(drugname=drug.drugname, prescriberid=personid)
    triple.delete()
    return redirect('detailPerson', id=personid)


def successPageView(request):
    return render(request, 'DrugApp/success.html')


def editPrescriberPageView(request, id):
    person = PdPrescriber.objects.get(npi=id)
    if request.method == "GET":
        if person.gender == "M":
            person.displaygender = "Male"
        else:
            person.displaygender = "Female"
        states = PdStatedata.objects.all()
        context = {
            "states": states,
            "person": person
        }
        return render(request, 'DrugApp/prescriber/editPrescriber.html', context)
    elif request.method == "POST":
        person.fname = request.POST["fname"]
        person.lname = request.POST["lname"]
        person.credentials1 = request.POST["credentials1"]
        person.credentials2 = request.POST["credentials2"]
        person.credentials3 = request.POST["credentials3"]
        person.credentials4 = request.POST["credentials4"]
        person.specialty = request.POST["specialty"]
        person.totalprescriptions = request.POST["totalprescriptions"]
        person.gender = request.POST["gender"]
        state = PdStatedata.objects.get(stateabbrev=request.POST["state"])
        person.state = state
        person.isopioidprescriber = request.POST["isopioidprescriber"]
        person.save()
        return redirect('detailPerson', id=person.npi)


def analyticsPageView(request):
    return render(request, 'DrugApp/analytics.html')
