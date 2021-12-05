from django.db.models import Avg, Sum
import random
from django.shortcuts import redirect, render
from .models import *
import math
from .staticQueries.intex_questions import *
from .api.intexPredictorAPI import predictPrescript
from .api.intexRecommenderAPI import recommendPrescriber

# Create your views here.


def indexPageView(request):
    """
    Name : indexPageView
    Description : Returns the landing page
    Paramaters: None
    """

    return render(request, 'DrugApp/index.html')


def searchPageView(request):
    """
    Name : searchPageView
    Description : 
        GET: Returns the search page view on a get request
        POST: Queries the databse based a search key from user
    Paramaters: 
        POST: 
            key : The search key
    """

    if request.method == 'POST':
        # get the search key and title case it (*data is case sensitive)
        key = request.POST['key'].title()

        # validate key entry
        if key == '' or key == " ":
            context = {
                'msg': 'Please enter a value'
            }
            return render(request, 'DrugApp/search.html', context)
        
        # if search is for a prescriber
        if request.POST['choice'] == 'Prescriber':
            #query first OR last name
            try:
                # if no space in seach key
                if " " not in key:
                    data = PdPrescriber.objects.filter(
                        fname__contains=key) | PdPrescriber.objects.filter(lname__contains=key)

                # if space in search key
                elif " " in key:
                    key = key.split(' ')
                    data = PdPrescriber.objects.filter(
                        fname__contains=key[0]) | PdPrescriber.objects.filter(lname__contains=key[1])
                
                context = {
                    'prescriber': True,
                }
            except:
                return redirect('error', type=500)

        # if search is for a drug
        elif request.POST['choice'] == 'Drug':
            #drug data is all upper case
            try:
                data = PdDrugs.objects.filter(
                    drugname__contains=key.upper())
                context = {
                    'drug': True,
                }
            except:
                return redirect('error', type=500)

        # if choice is not prescriber or drug
        else:
            return redirect('error', type=404)

        #set output message if the results returned anything
        if len(data) > 0:
            msg = f'We found {len(data)} results'
        else:
            msg = f'Sorry we could not find anything with the value'

        context['data'] = data
        context['msg'] = msg

        return render(request, 'DrugApp/search.html', context)
    # GET Request
    elif request.method == 'GET':
        return render(request, 'DrugApp/search.html')
    # Error
    else: 
        return redirect('error', type=404)


def learnPageView(request):
    """
    Name : learnPageView
    Description : Returns the learn more page
    Paramaters: None
    """

    return render(request, 'DrugApp/learn.html')


def aboutPageView(request):
    """
    Name : aboutPageView
    Description : Returns the about page
    Paramaters: None
    """

    return render(request, 'DrugApp/about.html')


def personDetailPageView(request, id):
    """
    Name : personDetailPageView
    Description : Returns the p_detail template with data for a single prescriber
    Paramaters: 
        id : the prescribers npi
    """

    # get the person and all their drugs
    try:
        person = PdPrescriber.objects.get(npi=id)
        creds = person.credentials.all()
        drugs = person.drugs.all()
    except Exception as e:
        print(e)

    # try hitting the prediction endpoint
    try:
        prediction = predictPrescript(
            person.fname, 
            person.specialty, 
            person.totalprescriptions,
            person.state.state,
            )
    # if it reaches the timeout (2 sec) then the endpoint if off, continue
    except:
        prediction = False

    # for each drug of the prescriber
    for drug in drugs:
        try:
            drugQty = PdTriple.objects.get(prescriberid=id, drugname=drug.drugname)

            # sum the total prescribed by prescriber
            mymax = PdTriple.objects.filter(prescriberid=id).aggregate(Sum('qty'))
            drug.sum = mymax['qty__sum']

            # get the individual qty
            drug.qty = drugQty.qty

            # calculate the average of the individual drug across all prescribers
            avg = PdTriple.objects.filter(
                drugname=drug.drugname).aggregate(Avg('qty'))
            drug.avg = round(avg['qty__avg'], 2)

            # calculate the percent that this drug is of the individuals prescibers total
            drug.percent = math.floor((drug.qty / drug.sum) * 100)
        except:
            # error logging
            pass

    context = {
        'person': person,
        'drugs': drugs,
    }

    if len(creds) > 0:
        context['creds'] = creds

    # if the prediction endpoint was on add to context
    if prediction:
        context['prediction'] = prediction

    return render(request, 'DrugApp/details/p_detail.html', context)


def drugDetailPageView(request, id):
    """
    Name : drugDetailPageView
    Description : Returns the d_detail template with data for a single drug
        GET : Get the drug info and the top ten prescribers
        POST : Get the GET info and hit the recommender endpoint to get ten recommended prescribers
    Paramaters: 
        id : the drugid
    """

    # get the drug and the top ten prescribers
    try:
        drug = PdDrugs.objects.get(drugid=id)
        # top ten is just the first ten prescribers who have the highest qty for the drug
        ten = PdTriple.objects.filter(drugname=drug.drugname).order_by('-qty')[:10]
    except:
        return redirect('error', type=500)

    context = {
    'drug': drug,
    'persons': ten,
    }
    
    # if post request hit endpoint
    if request.method == 'POST':
        try:
            rec = recommendPrescriber(
                drug.drugname, 
                drug.drugid, 
                drug.isopioid, 
                ten[0].prescriberid.npi, 
                ten[0].qty,
                ten[0].prescriberid.totalprescriptions,
                ten[0].prescriberid.specialty,
                ten[0].prescriberid.state.population)
            rec_ten = PdPrescriber.objects.filter(npi__in=rec)

            context['rec'] = rec_ten
        except:
            # error logging
            context['msg'] = 'Sorry, the recommender prescibers functionality is not available right now'

    return render(request, 'DrugApp/details/d_detail.html', context)


def addPrescriberPageView(request):
    """
    Name : addPrescriberPageView
    Description : Add a new prescriber to the database
        GET : Get a list of all state to populate the dropdown
        POST : handle the form data, create a new prescriber and 
            return the new prescriber detail page
    Paramaters: None
    """
    print(request.method)
    # if a GET request
    if request.method == 'GET':

        # get all the states
        states = PdStatedata.objects.all()

        context = {
            'states': states
        }
        return render(request, 'DrugApp/prescriber/addPrescriber.html', context)
    elif request.method == 'POST':
        # create the new prescriber
        try:
            # view classmethod in model to see creation proccess
            person = PdPrescriber.create(request.POST)
            person.save()
        except:
            return redirect('error', type=500)

        return redirect('detailPerson', id=person.npi)
    else:
        return redirect('error', type=404)


def deletePrescriberPageView(request, id):
    """
    Name : deletePrescriberPageView
    Description : delete prescriber from database
    Paramaters: 
        id : prescriber npi
    """

    #delete prescriber
    try:
        person = PdPrescriber.objects.get(npi=id)
        person.delete()
    except:
        return redirect('error', type=500)

    return redirect('success')


def addDrugPageView(request, id):
    """
    Name : addDrugPageView
    Description : Add a drug to a prescriber in pd_triple
        GET : Get a list of all drugs to populate the dropdown
        POST : handle the form data, create a new drug-prescriber relationship and 
            return the updated prescriber detail page
    Note : We do not allow users to add new drugs to the database, only drug-prescriber relationships
    Paramaters : 
        id : the prescriber npi
    """

    # get the person and all their current drugs
    try:
        person = PdPrescriber.objects.get(npi=id)
        triple = PdTriple.objects.filter(prescriberid=id)

        # exclude all drugs that the prescriber already prescribes
        excludes = []
        for t in triple:
            excludes.append(t.drugname)
    except:
        # if the above failed try the next section with all drugs
        excludes = []

    # GET request
    if request.method == 'GET':
        # get all drugs except those already prescribed by prescriber
        try:
            drugs = PdDrugs.objects.all().exclude(drugname__in=excludes)
        except:
            return redirect('error', type=500)

        context = {
            'person': person,
            'drugs': drugs,
        }

        return render(request, 'DrugApp/drug/addDrug.html', context)
    
    # POST request
    elif request.method == 'POST':
        # make a random id for new triple
        tripleID = random.randint(0, 999999)

        # create new triple
        try:
            triple = PdTriple.create(tripleID, person, request.POST)
            triple.save()
            person.totalprescriptions = person.totalprescriptions + int(request.POST['qty'])
            person.save()
        except:
            return redirect('error', type=500)

        return redirect('detailPerson', id=id)
    else:
        return redirect('error', type=404)


def editDrugPageView(request, drugid, personid):
    """
    Name : editDrugPageView
    Description : edit a drug for a prescriber in pd_triple
        GET : Get the drug-prescriber information
        POST : handle the form data, update the drug-prescriber relationship and 
            return the updated prescriber detail page
    Paramaters : 
        id : the drugid
    """

    # get the drug-prescriber relationshhip info
    try:
        # get the drug name
        drug = PdDrugs.objects.get(drugid=drugid)
        # get relaitonship info
        triple = PdTriple.objects.get(
            prescriberid=personid, drugname=drug.drugname)
        # get person information
        person = PdPrescriber.objects.get(npi=personid)
    except:
        return redirect('error', type=500)

    # GET request
    if request.method == "GET":

        context = {
            'person': person,
            'drug': drug,
            'triple': triple,
        }

        return render(request, 'DrugApp/drug/editDrug.html', context)
    
    # POST request
    elif request.method == "POST":
        try:
            # get the new qty
            qty = int(request.POST['qty'])

            # find the difference
            dif = qty - triple.qty

            # set qty
            triple.qty = qty

            # update the totalprescriptions by adding the differnce
            person.totalprescriptions = person.totalprescriptions + dif
            person.save()
            triple.save()
        except:
            return redirect('error', type=500)

        return redirect('detailPerson', id=person.npi)
    else:
        return redirect('error', type=404)


def deleteDrugPageView(request, drugid, personid):
    """
    Name : deleteDrugPageView
    Description : delete drug-prescriber relationship from database
    Paramaters: 
        drugid : the drugid
        personid : the prescriber npi
    """

    # get the relationship info
    try:
        # get the drug name
        drug = PdDrugs.objects.get(drugid=drugid)

        # get the relationship info
        triple = PdTriple.objects.get(
            drugname=drug.drugname, prescriberid=personid)
        
        # get person info
        person = triple.prescriberid

        #update totalprescriptions
        person.totalprescriptions = person.totalprescriptions - triple.qty

        # save and delete
        person.save()
        triple.delete()
    except:
        return redirect('error', type=500)

    return redirect('detailPerson', id=personid)


def successPageView(request):
    """
    Name : successPageView
    Description : Inform user that the process was a sucess
    Note : currently only called after delete prescriber function
    Paramaters : None
    """

    return render(request, 'DrugApp/success.html')


def editPrescriberPageView(request, id):
    """
    Name : editPrescriberPageView
    Description : edit a prescibers information
        GET : Get person information and 
            handle gender information for easier reading 
        POST : Get all the new information and update the prescriber
    Paramaters: 
        id : the prescriber npi
    """

    # get person information
    try:
        person = PdPrescriber.objects.get(npi=id)
    except:
        return redirect('error', type=500)

    # GET request
    if request.method == "GET":
        # handle gender manipulation
        if person.gender == "M":
            person.displaygender = "Male"
        else:
            person.displaygender = "Female"

        # get all the states to populate the dropdown
        try:
            states = PdStatedata.objects.all()
        except:
            return redirect('error', type=500)

        context = {
            "states": states,
            "person": person
        }

        return render(request, 'DrugApp/prescriber/editPrescriber.html', context)
    
    # POST request
    elif request.method == "POST":
        # set all the fields
        try:
            person.fname = request.POST["fname"]
            person.lname = request.POST["lname"]
            person.credentials1 = request.POST["credentials1"]
            person.credentials2 = request.POST["credentials2"]
            person.credentials3 = request.POST["credentials3"]
            person.credentials4 = request.POST["credentials4"]
            person.specialty = request.POST["specialty"]
            person.totalprescriptions = person.totalprescriptions
            person.gender = request.POST["gender"]
            state = PdStatedata.objects.get(stateabbrev=request.POST["state"])
            person.state = state
            person.isopioidprescriber = request.POST["isopioidprescriber"]
            person.save()
        except:
            return redirect('error', type=500)

        return redirect('detailPerson', id=person.npi)


def analyticsPageView(request):
    """
    Name : analyticsPageView
    Description : run static sql queries and display the analyitcs page
    Paramaters : None
    """

    # run the static queries (see staticQueries/intex_questions.py)
    try:
        q1 = query1()
        q2 = query2()
        q3 = query3()

        # q4: What state has the most opioid related deaths?
        states = PdStatedata.objects.all().order_by('-deaths')
        max = states[0].deaths
        q4 = []
        for i in range(0, len(states)):
            if states[i].deaths < max:
                i = len(states)
            elif states[i].deaths == max:
                q4.append(states[i])

        context = {
            'q1': q1,
            'q2': q2,
            'q3': q3,
            'q4': q4,
        }

        return render(request, 'DrugApp/analytics.html', context)
    except:
        return redirect('error', type=404)


def advsearchPageView(request):
    """
    Name : advsearchPageView
    Description : A more advance search page with extra filters
        GET : Get all states to populate the dropdown 
        POST : for each field dyanmically query the information
    Paramaters: None
    """

    # Get all state data
    try:
        states = PdStatedata.objects.all()
    except:
        return redirect('error', type=500)

    # GET request
    if request.method == 'GET':

        context = {
            'states': states
        }

        return render(request, 'DrugApp/advsearch.html', context)

    # POST request
    elif request.method == 'POST':
        # get the forms data
        form = request.POST
        
        # handle prescriber search
        if form['choice'] == 'Prescriber':
            # get all the prescribers to start
            try:
                result = PdPrescriber.objects.all()
            except:
                return redirect('error', type=500)
            
            # if they typed a name
            if form['key']:
                try:
                    # if no space in seach key
                    if " " not in form['key']:
                        result = result.filter(
                            fname__contains=form['key'].title()) | result.filter(lname__contains=form['key'].title())

                    # if space in search key
                    elif " " in form['key']:
                        key = form['key'].split(' ')
                        result = result.filter(
                            fname__contains=key[0]) | result.filter(lname__contains=key[1])
                except:
                    return redirect('error', type=500)

            try:
                # if specialty
                if form['specialty']:
                    result = result.filter(specialty=form['specialty'])

                # if credentials
                if form['credentials']:
                    # a bunch of ORs strung together
                    result = result.filter(
                        credentials1=form['credentials']
                        ) | result.filter(
                        credentials2=form['credentials']
                        ) | result.filter(
                        credentials3=form['credentials']
                        ) | result.filter(
                        credentials4=form['credentials']
                        )
                
                # gender
                if form['gender'] != 'hide':
                    result = result.filter(gender=form['gender'])

                # state
                if form['state'] != 'hide':
                    result = result.filter(state=form['state'])
            except:
                return redirect('error', type=500)
            
            context = {
                'prescriber': True
            }

        # handle drug search
        elif form['choice'] == 'Drug':
            # get all drug info to start
            try:
                result = PdDrugs.objects.all()
            except:
                return redirect('error', type=500)
            
            try:
                # if drug name
                if form['key']:
                    result = result.filter(
                        drugname__contains=form['key'].upper())

                # if isopioid
                if form['isopioid'] != 'hide':
                    result = result.filter(isopioid=form['isopioid'].title())
            except:
                return redirect('error', type=500)

            context = {
                'drug': True,
            }
        
        # set the rest of the context
        context['data'] = result
        context['msg'] = f'We found {len(result)} results'
        context['states'] = states
        
        return render(request, 'DrugApp/advsearch.html', context)


def e(request, type):
    """
    Name : e
    Description : return the error page
    Paramaters: 
        type : the type of error (currently 500 or 404)
    """

    # set words for page based on type
    if type == 404:
        title = 'Page not found'
        msg = 'Uh-oh, it seems the page you\'re looking for doesn\'t exist'

    elif type == 500:
        title = 'Internal server error'
        msg = 'So sorry, but we were not able to process your request'

    context = {
        'error_code': type,
        'title': title,
        'msg': msg ,
    }

    return render(request, 'DrugApp/404.html', context)