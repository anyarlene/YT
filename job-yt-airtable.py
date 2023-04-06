import os
import json
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import requests
from datetime import datetime

# Airtable API credentials
AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_NAME = 'Singers'

# YouTube API credentials
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
CLIENT_SECRETS_FILE = "client_secret.json"


def get_channel_id(singer):
    # Build the credentials object
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_console()

    # Build the YouTube API client
    youtube = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

    # Search for the singer's channel ID
    request = youtube.search().list(
        q=singer,
        type='channel',
        part='id',
        maxResults=1
    )
    response = request.execute()

    # Extract the channel ID
    channel_id = response['items'][0]['id']['channelId']

    return channel_id


def get_channel_statistics(channel_id):
    # Build the YouTube API client
    youtube = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

    # Retrieve the channel statistics
    request = youtube.channels().list(
        id=channel_id,
        part='snippet, statistics'
    )
    response = request.execute()

    # Extract the channel statistics
    statistics = response['items'][0]['statistics']
    profile = response['items'][0]['snippet']
    return statistics, profile

# Open the singers JSON file and load the data
with open('bdi_singers.json', 'r') as f:
    data = json.load(f)

# Get the channel ID and statistics for each singer
singers = data['singers']
for singer in singers:
    channel_id = get_channel_id(singer)
    statistics = get_channel_statistics(channel_id)
    profile = get_channel_statistics(channel_id)
    # Build the Airtable record
    record = {
        'Name': singer,
        'Thumbnail' : profile['thumbnails']['default']['url'],
        'Channel ID': channel_id,
        'Subscribers': statistics['subscriberCount'],
        'Views': statistics['viewCount'],
        'Videos': statistics['videoCount'],
        'CreationTime': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }

    # Insert the record into the Airtable table
    url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}'
    headers = {
        'Authorization': f'Bearer {AIRTABLE_API_KEY}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, json={'records': [{'fields': record}]}, headers=headers)

    # Print the response status code
    print(response.status_code)
