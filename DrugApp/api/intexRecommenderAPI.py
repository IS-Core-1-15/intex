import requests
import json

def recommendPrescriber(drugName, drugID, isOpioid, prescriberID, qty, totalPrescriptions, specialty, population):

    url = "http://c2d11085-92ef-4dc7-8552-800256d076c8.eastus2.azurecontainer.io/score"

    payload = json.dumps({
    "Inputs": {
        "WebServiceInput1": [
        {
            "npi": prescriberID,
            "totalprescriptions": totalPrescriptions,
            "specialty": specialty,
            "population": population
        }
        ],
        "WebServiceInput0": [
        {
            "drugid": drugID,
            "drugname": drugName,
            "isopioid": isOpioid
        }
        ],
        "WebServiceInput4": [
        {
            "drugid": drugID,
            "prescriberid": prescriberID,
            "qty": qty
        }
        ]
    },
    "GlobalParameters": {}
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer NaPkDaH48HMj3VIH59Lkc1pEfp12sxQt'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    data = json.loads(response.text)

    dataDict = data['Results']['WebServiceOutput0'][0]

    aResults = []
    
    for dictItem in dataDict :
        aResults.append(dataDict[dictItem])

    return aResults
# order of parameters: drugName, drugID, isOpioid, prescriberID, qty, totalPrescriptions, specialty, population