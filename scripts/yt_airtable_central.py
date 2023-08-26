import json
import os
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from datetime import datetime

# Load the API keys and Airtable credentials from the .env file
load_dotenv()
YT_API_KEY = os.getenv('YT_API_KEY')
AIRTABLE_ACCESS_TOKEN = os.getenv('AIRTABLE_ACCESS_TOKEN')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
CENTRAL_TABLE_NAME = os.getenv('CENTRAL_TABLE_NAME')
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

def get_channel_data(channel_id):
    data = {}
    youtube = build(API_SERVICE_NAME, API_VERSION, developerKey=YT_API_KEY)
    try:
        request = youtube.channels().list(
            id=channel_id,
            part='snippet, statistics'
        )
        response = request.execute()
        
        published_date = datetime.fromisoformat(response['items'][0]['snippet']['publishedAt'].rstrip('Z')).strftime('%Y-%m-%d')
        data = {
            'record_id_ref': None,  # This will be filled after creating the record
            'artist': response['items'][0]['snippet']['title'],
            'thumbnail': [{'url': response['items'][0]['snippet']['thumbnails']['default']['url']}],
            'channel_id': channel_id,
            'published_date': published_date,
            'creation_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except HttpError as e:
        print(f'Error getting statistics for {channel_id}: {e}')
    return data

headers = {
    'Authorization': f'Bearer {AIRTABLE_ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

def overwrite_airtable(data):
    # Fetch all records from Airtable
    url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{CENTRAL_TABLE_NAME}'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch records from Airtable: {response.text}")
        return

    existing_records = response.json().get('records', {})
    artist_to_record_map = {record['fields'].get('artist'): record for record in existing_records}

    for record_data in data:
        artist_name = record_data['artist']
        # If artist exists in Airtable, update the record using PATCH
        if artist_name in artist_to_record_map:
            record_id = artist_to_record_map[artist_name]['id']
            record_data['record_id_ref'] = record_id  # Ensure the record_id_ref is consistent
            patch_url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{CENTRAL_TABLE_NAME}/{record_id}'
            response = requests.patch(patch_url, headers=headers, json={'fields': record_data})
            if response.status_code != 200:
                print(f"Failed to update record for artist {artist_name}: {response.text}")
        else:
            # If artist doesn't exist in Airtable, create a new record using POST
            response = requests.post(url, headers=headers, json={'fields': record_data})
            if response.status_code == 200:
                new_record_id = response.json()['id']
                record_data['record_id_ref'] = new_record_id
                patch_url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{CENTRAL_TABLE_NAME}/{new_record_id}'
                response = requests.patch(patch_url, headers=headers, json={'fields': {'record_id_ref': new_record_id}})
                if response.status_code != 200:
                    print(f"Failed to update record_id_ref for artist {artist_name}: {response.text}")
            else:
                print(f"Failed to create record for artist {artist_name}: {response.text}")

with open('channel-id-data/burundian_singer_channel_ids.json', 'r') as f:
    channels = json.load(f)

data_to_upload = [get_channel_data(channel_id) for _, channel_id in channels.items()]

overwrite_airtable(data_to_upload)
