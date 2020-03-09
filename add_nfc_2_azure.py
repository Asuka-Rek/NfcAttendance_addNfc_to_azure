import requests
import json

def add_crew(name, birthday, tourokubi, card_hash):
    payload = {
    "name":name,
    "birthday":birthday,
    "tourokubi":tourokubi,
    "card_hash":card_hash
    }
    url, headers = init_request("add_crew")
    print("adding new crew...")
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    print(r)
    return r.status_code

def resolve_crew(card_hash):
    payload = {
    "card_hash":card_hash
    }
    url, headers = init_request("resolve_name")
    print("resolving crew name...")
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    print(r)
    try:
        crew_data = r.json()["ResultSets"]['Table1'][0]
    except KeyError:
        return None
    else:
        return crew_data

def init_request(command_name):
    with open('azure_endpoint.json') as az_json:
        url = json.load(az_json)[command_name]
    headers = {"content-type":"application/json"}
    return url, headers