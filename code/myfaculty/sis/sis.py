import csv
import requests
from django.conf import settings

def get_token():

    # build payload
    data = {
        "client_id": settings.SIS_CLIENT_ID,
        "username": settings.SIS_USER_NAME,
        "password": settings.SIS_PASSWD,
        "grant_type": "password"
    }

    # Request token
    response = requests.post(settings.SIS_KEYCLOAK_TOKEN_URL, data=data)

    # Parse token
    if response.status_code == 200:
        bearer_token = response.json()["access_token"]
        return bearer_token
    else:
        error = "ERROR CODE: " + str(response.status_code) + " | " +  str(response.text)
        return error

def get_students(prog, token):
    url_get = f"""
    https://api.sis.hua.gr/api/Students?$top=2000&$skip=0&$filter=(department eq {prog} 
    and studentStatus/alternateName eq 'active')&$count=true&$select=person/familyName as familyName,person/givenName as givenName,
    studentStatus/alternateName as studentStatus,user/name as username,
    semester as semester, inscriptionYear/name as inscriptionYear,
    specialty as specialty,person/email as masterMail, 
    person/alternateEmail as secondaryMail
    """.replace('\n','')

    headers_get = {
        'Authorization': f'Bearer {token}'
        }
    payload_get = {}
    response_get = requests.request("GET", url_get, headers=headers_get, data=payload_get).json()
    values = response_get["value"]
    return values

def sis_to_csv():
    token = get_token()

    program_codes = [550, 1550, 1556, 1557, 1560]

    students = []

    for prog in program_codes:
        students_prog = get_students(prog, token)
        for s in students_prog:
            s['program'] = prog
        
        students += students_prog

    with open('students.csv', 'w') as f:
        fieldnames = students[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        for s in students:
            writer.writerow(s)

    
