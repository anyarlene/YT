import json
import os
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load the API keys and Airtable credentials from the .env file
load_dotenv()
API_KEY = os.getenv('API_KEY')
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')

# Define a function to get the YouTube channel statistics for a given channel ID
def get_channel_data(channel_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    # Get the channel statistics using the channel ID
    request = youtube.channels().list(
        id=channel_id,
        part='snippet, statistics'
    )
    response = request.execute()

    # Return the data as a dictionary
    data = {
        'profile_picture': response['items'][0]['snippet']['thumbnails']['default']['url'],
        'subscriber_count': response['items'][0]['statistics']['subscriberCount'],
        'view_count': response['items'][0]['statistics']['viewCount'],
        'video_count': response['items'][0]['statistics']['videoCount']
    }
    return data

# Open the channels JSON file and load the data
with open('channels.json', 'r') as f:
    channels = json.load(f)

# Loop through each channel and get the statistics
for singer, channel_id in channels.items():
    try:
        # Get the channel data
        channel_data = get_channel_data(channel_id)

        # Prepare the data for the Airtable API
        data = {
            'fields': {
                'Singer': singer,
                'Profile Picture': [{'url': channel_data['profile_picture']}],
                'Subscribers': int(channel_data['subscriber_count']),
                'Views': int(channel_data['view_count']),
                'Videos': int(channel_data['video_count'])
            }
        }

        # Make a POST request to the Airtable API to add the data to the base
        url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/Table%201'
        headers = {
            'Authorization': f'Bearer {AIRTABLE_API_KEY}',
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, json=data)

        # Print the response status code and text
        print(response.status_code)
        print(response.text)

    except HttpError as e:
        print(f'Error getting statistics for {singer}: {e}')
