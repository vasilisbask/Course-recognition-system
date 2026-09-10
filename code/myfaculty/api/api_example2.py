import os

import requests


BASE_URL = os.environ.get('MYFACULTY_API_BASE_URL', 'https://mydep.ditapps.hua.gr/api')
TOKEN = os.environ.get('MYFACULTY_API_TOKEN')

if not TOKEN:
    raise RuntimeError('Set MYFACULTY_API_TOKEN before running this example.')

headers = {'Authorization': 'Token ' + TOKEN}
payload = {'id': os.environ.get('MYFACULTY_COURSE_ID', '331')}
response = requests.get(f'{BASE_URL}/course', headers=headers, params=payload)
response.raise_for_status()
print(response.text)



