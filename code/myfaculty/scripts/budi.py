#URL = 'https://mydepartment.ditapps.hua.gr/api/public/v1'
URL = 'https://onestop.ditapps.hua.gr/api/public/v1'
APP_MAP = {
    'ects' : 'app_0be1cab594104a3186e5531a15028971',
    'projects' : 'app_24141cc430384eebab23880fa845832e',
    'leaves' : 'app_25a7063c1c5a41a8acb8ec69e582c953',
    'timesheets' : 'app_5727bdec64aa4673b4f18a0109dc5d5c',
    'theses'  : 'app_69659300bcaf49628e9ee23522b7917f'

}
TABLE_IDS = {
    'courses' : 'ta_efd528d97e924312bf3c3bc119f86825',
    'projects' : 'ta_328b533cb858413da1172e6898e69cf8',
    'leaves' : 'ta_44242b5260ab48c9a2bd120123e8f9ab',
    'timesheets' : 'ta_14436c43e09c400c862dd617cef54ae1',
    'theses' : 'ta_0437b1b8241644e1a35e965adf999965'
}

import requests
import json

class budiapi:

    def __init__(self, api_key = None, master_url = URL, app_map = APP_MAP, table_ids = TABLE_IDS):
        self.api_key = api_key
        self.master_url = master_url
        self.app_map = app_map
        self.table_ids = table_ids

    def post_headers(self, app_id = None):
        headers = {"Accept": "application/json",
                   "Content-Type": "application/json",
                   "x-budibase-api-key" : self.api_key }
        if app_id is not None:
            headers['x-budibase-app-id'] = app_id

        return headers

    def get_table_info(self, table_name, app_name):
        table_id = self.table_ids[ table_name ]
        app_id = self.app_map[ app_name ]
        url = self.master_url + '/tables/' + table_id
        headers = self.post_headers( app_id = app_id )
        response = requests.get(url, headers = headers)
        return json.loads(response.text)[ 'data' ]

    def get_table_data(self, table_name, app_name):
        table_id = self.table_ids[ table_name ]
        app_id = self.app_map[ app_name ]
        url = self.master_url + '/tables/' + table_id + '/rows/search'
        headers = self.post_headers( app_id = app_id )
        response = requests.post(url, headers = headers)
        return json.loads(response.text)[ 'data' ]

    def create_row(self, table_name, app_name, value_dict):
        table_id = self.table_ids[ table_name ]
        app_id = self.app_map[ app_name ]
        url = self.master_url + '/tables/' + table_id + '/rows'
        headers = self.post_headers( app_id = app_id )
        response = requests.post(url, headers = headers, json = value_dict)
        return json.loads(response.text)[ 'data' ]

    def search_rows(self, table_name, app_name, query_dict):
        table_id = self.table_ids[ table_name ]
        app_id = self.app_map[ app_name ]
        url = self.master_url + '/tables/' + table_id + '/rows/search'
        headers = self.post_headers( app_id = app_id )
        payload = {'query' : {'string' : query_dict} }
        response = requests.post(url, headers = headers, json = payload )
        return json.loads(response.text)[ 'data' ]

    def update_row(self, table_name, app_name, query_dict, value_dict):

        rows = self.search_rows(table_name, app_name, query_dict)
        if len(rows) == 1:
            table_id = self.table_ids[ table_name ]
            app_id = self.app_map[ app_name ]
            row_id = rows[0]['_id']
            url = self.master_url + '/tables/' + table_id + '/rows/' + row_id
            headers = self.post_headers( app_id = app_id )
            response = requests.put(url, headers = headers, json = value_dict)
            return json.loads(response.text)[ 'data' ]
        else:
            raise ValueError('Number of matching rows must be exactly 1 not ' + str(len(rows)) + '.')
