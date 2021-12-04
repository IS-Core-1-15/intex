import requests
import json

def predictPrescript(sFirstName, sSpecialty, iPrescriptions, sState):        
    url = "http://313dcb6b-65f0-41ae-be7d-c7c8214c3f0f.eastus2.azurecontainer.io/score"

    payload = json.dumps({
    "Inputs": {
        "WebServiceInput1": [
        {
            "fname": sFirstName,
            "specialty": sSpecialty,
            "totalprescriptions": iPrescriptions,
            "state_R": sState
        }
        ]
    },
    "GlobalParameters": {}
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer IEPgIaIfhIk4R2fvIhsn6uAcqzGZNC6O'
    }
    response = requests.request("POST", url, headers=headers, data=payload, timeout=1)

    data = json.loads(response.text)

    sData = data["Results"]["WebServiceOutput0"][0]["Scored Labels"]

    return(sData)