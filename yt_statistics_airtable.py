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
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

# Define a function to get the YouTube channel statistics for a given channel ID
def get_channel_data(channel_id):
    # Initialize dictionary to store data
    data = {}
    youtube = build(API_SERVICE_NAME, API_VERSION, developerKey=YT_API_KEY)

    try:
        request = youtube.channels().list(
            id=channel_id,
            part='snippet, statistics'
        )
        response = request.execute()

        # Get the publishedAt string from the response and format it to 'YYYY-MM-DD'
        published_date = datetime.fromisoformat(response['items'][0]['snippet']['publishedAt'].rstrip('Z')).strftime('%Y-%m-%d')

        data = {
            'subscriber_count': response['items'][0]['statistics']['subscriberCount'],
            'profile_picture': response['items'][0]['snippet']['thumbnails']['default']['url'],
            'view_count': response['items'][0]['statistics']['viewCount'],
            'video_count': response['items'][0]['statistics']['videoCount'],
            'published_at': published_date
        }
    except HttpError as e:
        print(f'Error getting statistics for {channel_id}: {e}')

    return data

with open('channel-id-data/burundian_singer_channel_ids.json', 'r') as f:
    channels = json.load(f)

channel_list = [(singer, int(get_channel_data(channel_id)['subscriber_count'])) for singer, channel_id in channels.items()]
channel_list.sort(key=lambda x: x[1], reverse=True)
ranked_list = [(i+1, singer, subs) for i, (singer, subs) in enumerate(channel_list)]

record_ids = {}

for rank, singer, subs in ranked_list:
    channel_data = get_channel_data(channels[singer])
    creation_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = {
        'fields': {
            'rank': rank,
            'artist': singer,
            'thumbnail': [{'url': channel_data['profile_picture']}],
            'subscribers': subs,
            'video_views': int(channel_data['view_count']),
            'video_count': int(channel_data['video_count']),
            'published_date': channel_data['published_at'],
            'creation_timestamp': creation_timestamp  
        }
    }

    # Make a POST request to the Airtable API to add the data to the base
    url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/Table%201'
    headers = {
        'Authorization': f'Bearer {AIRTABLE_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200: # successful creation
        record_id = response.json()['id']
        # Update the new field 'Record_ID_Ref' with the generated record_id
        url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/Table%201/{record_id}'
        data = {
            'fields': {
                'record_id_ref': record_id
            }
        }
        response = requests.patch(url, headers=headers, json=data)
        if response.status_code == 200: # successful update
            print(f"Record for singer {singer} was created and updated successfully.")
        else:
            print(f"Failed to update record for singer {singer}: {response.text}")
    else:
        print(f"Failed to create record for singer {singer}: {response.text}")
