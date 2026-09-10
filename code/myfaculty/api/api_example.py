import os

import requests


BASE_URL = os.environ.get('MYFACULTY_API_BASE_URL', 'http://localhost:30082/api')
USERNAME = os.environ.get('MYFACULTY_API_USERNAME', 'admin')
PASSWORD = os.environ.get('MYFACULTY_API_PASSWORD')

if not PASSWORD:
    raise RuntimeError('Set MYFACULTY_API_PASSWORD before running this example.')

response = requests.post(
    f'{BASE_URL}/auth/',
    data={
        'username': USERNAME,
        'password': PASSWORD,
    },
)
response.raise_for_status()
token = response.json()['token']

headers = {'Authorization': 'Token ' + token}

staff_response = requests.get(
    f'{BASE_URL}/staff',
    headers=headers,
    params={'email': os.environ.get('MYFACULTY_STAFF_EMAIL', 'user@example.com')},
)
print(staff_response.text)

associate_response = requests.get(
    f'{BASE_URL}/associates',
    headers=headers,
    params={'card_no': os.environ.get('MYFACULTY_ASSOCIATE_CARD_NO', '00000000000000')},
)
print(associate_response.text)


