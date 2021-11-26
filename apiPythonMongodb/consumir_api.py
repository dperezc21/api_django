import json
from decouple import config
import requests
def api():

    API=config('API')
    response = requests.get(API)
    paises = json.loads(response.text)
    return paises
