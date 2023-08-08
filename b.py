import json
import os
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from datetime import datetime

# Load the API keys and Airtable credentials from the .env file
load_dotenv()

# Constants
YT_API_KEY = os.getenv('YT_API_KEY')
AIRTABLE_ACCESS_TOKEN = os.getenv('AIRTABLE_ACCESS_TOKEN')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
MIN_CPM = 0.25 / 1000
MAX_CPM = 4.00 / 1000
ENDPOINT_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/Table 1 copy copy"
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

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
            'subscriber_count': response['items'][0]['statistics']['subscriberCount'],
            'profile_picture': response['items'][0]['snippet']['thumbnails']['default']['url'],
            'view_count': response['items'][0]['statistics']['viewCount'],
            'video_count': response['items'][0]['statistics']['videoCount'],
            'published_at': published_date
        }
    except HttpError as e:
        print(f'Error getting statistics for {channel_id}: {e}')

    return data

def calculate_earnings_range(view_count, days):
    min_earnings = int(view_count) * MIN_CPM / days
    max_earnings = int(view_count) * MAX_CPM / days
    return min_earnings, max_earnings

with open('channel-id-data/burundian_singer_channel_ids.json', 'r') as f:
    channels = json.load(f)

channel_list = [(singer, int(get_channel_data(channel_id)['subscriber_count'])) for singer, channel_id in channels.items()]
channel_list.sort(key=lambda x: x[1], reverse=True)
ranked_list = [(i+1, singer, subs) for i, (singer, subs) in enumerate(channel_list)]

for rank, singer, subs in ranked_list:
    channel_data = get_channel_data(channels[singer])
    creation_timestamp = datetime.now()
    published_date = datetime.strptime(channel_data['published_at'], '%Y-%m-%d')
    days = (creation_timestamp - published_date).days
    min_earnings, max_earnings = calculate_earnings_range(channel_data['view_count'], days)
    earnings_estimate = f"${round(min_earnings)} - ${round(max_earnings)}"

    # Logic for new_estimated_earnings
    views_difference = int(channel_data['view_count']) 
    min_earnings_new = views_difference * MIN_CPM
    max_earnings_new = views_difference * MAX_CPM
    new_earnings_estimate = f"${round(min_earnings_new)} - ${round(max_earnings_new)}"

    data = {
        'fields': {
            'rank': rank,
            'artist': singer,
            'thumbnail': [{'url': channel_data['profile_picture']}],
            'subscribers': subs,
            'video_views': int(channel_data['view_count']),
            'video_count': int(channel_data['video_count']),
            'published_date': channel_data['published_at'],
            'creation_timestamp': creation_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'estimated_earnings': earnings_estimate,
            'new_estimated_earnings': new_earnings_estimate
        }
    }

    response = requests.post(ENDPOINT_URL, headers=HEADERS, json=data)
    if response.status_code == 200:
        record_id = response.json()['id']
        url = f"{ENDPOINT_URL}/{record_id}"
        data = {
            'fields': {
                'record_id_ref': record_id
            }
        }
        response = requests.patch(url, headers=HEADERS, json=data)
        if response.status_code == 200:
            print(f"Record for singer {singer} was created and updated successfully.")
        else:
            print(f"Failed to update record for singer {singer}: {response.text}")
    else:
        print(f"Failed to create record for singer {singer}: {response.text}")
