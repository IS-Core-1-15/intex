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
            # query first OR last name
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
            except Exception as e:
                return redirect('error', type=500, e=e)

        # if search is for a drug
        elif request.POST['choice'] == 'Drug':
            # drug data is all upper case
            try:
                data = PdDrugs.objects.filter(
                    drugname__contains=key.upper())
                context = {
                    'drug': True,
                }
            except Exception as e:
                return redirect('error', type=500, e=e)

        # if choice is not prescriber or drug
        else:
            return redirect('error', type=404, e='No Method')

        # set output message if the results returned anything
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
        return redirect('error', type=404, e='No Method')


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
        print(prediction)
    # if it reaches the timeout (2 sec) then the endpoint if off, continue
    except Exception as e:
        prediction = 'x'
        pass

    # for each drug of the prescriber
    for drug in drugs:
        try:
            drugQty = PdTriple.objects.get(
                prescriberid=id, drugname=drug.drugname)

            # sum the total prescribed by prescriber
            mymax = PdTriple.objects.filter(
                prescriberid=id).aggregate(Sum('qty'))
            drug.sum = mymax['qty__sum']

            # get the individual qty
            drug.qty = drugQty.qty

            # calculate the average of the individual drug across all prescribers
            avg = PdTriple.objects.filter(
                drugname=drug.drugname).aggregate(Avg('qty'))
            drug.avg = round(avg['qty__avg'], 2)

            # calculate the percent that this drug is of the individuals prescibers total
            drug.percent = math.floor((drug.qty / drug.sum) * 100)
        except Exception as e:
            # error logging
            pass

    context = {
        'person': person,
        'drugs': drugs,
    }

    if len(creds) > 0:
        context['creds'] = creds

    # if the prediction endpoint was on add to context
    print(prediction)
    if prediction == 'FALSE':
        context['prediction'] = 'Will not prescriber opioids'
    elif prediction == 'TRUE':
        context['prediction'] = 'Will prescriber opioids'
    else:
        context['prediction'] = 'This function is not working right now'

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
        ten = PdTriple.objects.filter(
            drugname=drug.drugname).order_by('-qty')[:10]
    except Exception as e:
        return redirect('error', type=500, e=e)

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
        except Exception as e:
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
        try:
            states = PdStatedata.objects.all()
        except Exception as e:
            return redirect('error', type=500, e=e)

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
        except Exception as e:
            return redirect('error', type=500, e=e)

        return redirect('detailPerson', id=person.npi)
    else:
        return redirect('error', type=404, e='No Method')


def deletePrescriberPageView(request, id):
    """
    Name : deletePrescriberPageView
    Description : delete prescriber from database
    Paramaters: 
        id : prescriber npi
    """

    # delete prescriber
    try:
        person = PdPrescriber.objects.get(npi=id)
        person.delete()
    except Exception as e:
        return redirect('error', type=500, e=e)

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
    except Exception as e:
        # if the above failed try the next section with all drugs
        excludes = []

    # GET request
    if request.method == 'GET':
        # get all drugs except those already prescribed by prescriber
        try:
            drugs = PdDrugs.objects.all().exclude(drugname__in=excludes)
        except Exception as e:
            return redirect('error', type=500, e=e)

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
            person.totalprescriptions = person.totalprescriptions + \
                int(request.POST['qty'])
            person.save()
        except Exception as e:
            return redirect('error', type=500, e=e)

        return redirect('detailPerson', id=id)
    else:
        return redirect('error', type=404, e=e)


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
    except Exception as e:
        return redirect('error', type=500, e=e)

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
        except Exception as e:
            return redirect('error', type=500, e=e)

        return redirect('detailPerson', id=person.npi)
    else:
        return redirect('error', type=404, e='No Method')


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

        # update totalprescriptions
        person.totalprescriptions = person.totalprescriptions - triple.qty

        # save and delete
        person.save()
        triple.delete()
    except Exception as e:
        return redirect('error', type=500, e=e)

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
    except Exception as e:
        return redirect('error', type=500, e=e)

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
        except Exception as e:
            return redirect('error', type=500, e=e)

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
            person.specialty = request.POST["specialty"]
            person.totalprescriptions = person.totalprescriptions
            person.gender = request.POST["gender"]
            state = PdStatedata.objects.get(stateabbrev=request.POST["state"])
            person.state = state
            person.isopioidprescriber = request.POST["isopioidprescriber"]
            person.save()
        except Exception as e:
            return redirect('error', type=500, e=e)

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
        states = PdStatedata.objects.all().order_by('deaths')
        for i in range(0, len(states)):
            if states[i].deaths is not None:
                max = states[i].deaths
                i = len(states)
        q4 = []
        for i in range(0, len(states)):
            if states[i].deaths is not None:
                if (states[i].deaths < max):
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
    except Exception as e:
        return redirect('error', type=404, e=e)


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
        creds = PdCredential.objects.all()
    except Exception as e:
        return redirect('error', type=500, e=e)

    # GET request
    if request.method == 'GET':

        context = {
            'states': states,
            'all_creds': creds,
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
            except Exception as e:
                return redirect('error', type=500, e=e)

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
                except Exception as e:
                    return redirect('error', type=500, e=e)

            try:
                # if specialty
                if form['specialty']:
                    result = result.filter(specialty=form['specialty'])

                # if credentials
                if form['cred'] != '':
                    # a bunch of ORs strung together
                    result = result.filter(credentials=form['cred'])

                # gender
                if form['gender'] != '':
                    result = result.filter(gender=form['gender'])

                # state
                if form['state'] != '':
                    result = result.filter(state=form['state'])
            except Exception as e:
                return redirect('error', type=500, e=e)

            context = {
                'prescriber': True,
            }

        # handle drug search
        elif form['choice'] == 'Drug':
            # get all drug info to start
            try:
                result = PdDrugs.objects.all()
            except Exception as e:
                return redirect('error', type=500, e=e)

            try:
                # if drug name
                if form['key']:
                    result = result.filter(
                        drugname__contains=form['key'].upper())

                # if isopioid
                if form['isopioid'] != '':
                    result = result.filter(isopioid=form['isopioid'].title())
            except Exception as e:
                return redirect('error', type=500, e=e)

            context = {
                'drug': True,
            }

        # set the rest of the context
        context['data'] = result
        context['msg'] = f'We found {len(result)} results'
        context['states'] = states
        context['all_creds'] = creds

        return render(request, 'DrugApp/advsearch.html', context)


def addCredPageView(request, id):
    """
    Name : addCredPageView
    Description : Add a credential to a prescriber in pd_prescriber_credential
        GET : Get a list of all creds to populate the dropdown
        POST : handle the form data, create a new relationship and 
            return the updated prescriber detail page
    Paramaters : 
        id : the prescriber npi
    """

    # get the person and all their current drugs
    try:
        person = PdPrescriber.objects.get(npi=id)
        creds = PdPrescriberCredential.objects.filter(prescriberid=id)

        # exclude all drugs that the prescriber already prescribes
        excludes = []
        for t in creds:
            excludes.append(t.credential)
    except Exception as e:
        # if the above failed try the next section with all drugs
        excludes = []

    # GET request
    if request.method == 'GET':
        # get all creds except those already prescribed by prescriber
        try:
            creds = PdCredential.objects.all().exclude(credentialcode__in=excludes)
        except Exception as e:
            return redirect('error', type=500, e=e)

        context = {
            'person': person,
            'all_creds': creds,
            'creds': person.credentials.all()
        }

        return render(request, 'DrugApp/prescriber/addCred.html', context)

    # POST request
    elif request.method == 'POST':
        # make a random id for new relationship
        relid = random.randint(0, 999)

        # create new triple
        try:
            rel = PdPrescriberCredential.create(relid, person, request.POST)
            rel.save()
        except Exception as e:
            return redirect('error', type=500, e=e)

        return redirect('detailPerson', id=id)
    else:
        return redirect('error', type=404, e=e)


def deleteCredPageView(request, id, cred):
    """
    Name : deleteCredPageView
    Description : Allows you to delete a credential for a prescriber
    Paramaters: 
        id : the prescriber npi
        cred : the credential code
    """


    # get the person and all their current drugs
    try:
        cred = PdPrescriberCredential.objects.get(prescriberid=id, credential=cred)
  
    except Exception as e:
        # if the above failed try the next section with all drugs
        return redirect('error', type=500, e=e)

    # get all creds except those already prescribed by prescriber
    try:
        cred.delete()
    except Exception as e:
        return redirect('error', type=500, e=e)

    return redirect('detailPerson', id=id)
    

def errorPageView(request, type):
    """
    Name : e
    Description : return the error page
    Paramaters: 
        type : the type of error (currently 500 or 404)
        e : the error that was raised
    """

    # Print the error
    # print(e)

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
        'msg': msg,
    }

    return render(request, 'DrugApp/404.html', context)
