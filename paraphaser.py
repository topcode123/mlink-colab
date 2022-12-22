import requests
import json

def paraphase_vi(paragraph):
    url = "https://api.momd.vn/paraphaser/paraphase-vi"

    payload = json.dumps({
    "paragraph": paragraph
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return json.loads(response.text)