import os
import requests
from datetime import datetime
from dotenv import load_dotenv

class AirtableDataModel:
    def __init__(self):
        load_dotenv()
        self.airtable_access_token = os.getenv('AIRTABLE_ACCESS_TOKEN')
        self.airtable_base_id = os.getenv('AIRTABLE_BASE_ID')
        self.headers = {
            'Authorization': f'Bearer {self.airtable_access_token}',
            'Content-Type': 'application/json'
        }

    def post_record(self, data):
        url = f'https://api.airtable.com/v0/{self.airtable_base_id}/Table%201'
        response = requests.post(url, headers=self.headers, json=data)
        return response

    def update_record(self, record_id, data):
        url = f'https://api.airtable.com/v0/{self.airtable_base_id}/Table%201/{record_id}'
        response = requests.patch(url, headers=self.headers, json=data)
        return response
