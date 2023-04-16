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
    youtube = build(API_SERVICE_NAME, API_VERSION , developerKey=YT_API_KEY)

    # Get the channel statistics using the channel ID
    request = youtube.channels().list(
        id=channel_id,
        part='snippet, statistics'
    )
    response = request.execute()

    # Return the data as a dictionary
    data = {
        'subscriber_count': response['items'][0]['statistics']['subscriberCount'],
        'profile_picture': response['items'][0]['snippet']['thumbnails']['default']['url'],
        'view_count': response['items'][0]['statistics']['viewCount'],
        'video_count': response['items'][0]['statistics']['videoCount'],
        'published_at': response['items'][0]['snippet']['publishedAt']
    }
    return data

# Open the channels JSON file and load the data
with open('burundian_singer_channel_ids.json', 'r') as f:
    channels = json.load(f)

# Create a list of tuples with singer name and subscriber count
channel_list = [(singer, int(get_channel_data(channel_id)['subscriber_count'])) for singer, channel_id in channels.items()]

# Sort the list by subscriber count in descending order
channel_list.sort(key=lambda x: x[1], reverse=True)

# Add rank to each tuple
ranked_list = [(i+1, singer, subs) for i, (singer, subs) in enumerate(channel_list)]

# Loop through each channel and add the data to the Airtable base
for rank, singer, subs in ranked_list:
    try:
        # Prepare the data for the Airtable API
        data = {
            'fields': {
                'Rank': rank,
                'Artist': singer,
                'Thumbnail': [{'url': get_channel_data(channels[singer])['profile_picture']}],
                'Subscribers': subs,
                'Views': int(get_channel_data(channels[singer])['view_count']),
                'Videos': int(get_channel_data(channels[singer])['video_count']),
                'PublishedTime': get_channel_data(channels[singer])['published_at']
                ##'CreatedTime': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            }
        }

        # Make a POST request to the Airtable API to add the data to the base
        url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/Table%201'
        headers = {
            'Authorization': f'Bearer {AIRTABLE_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, json=data)

        # Print the response status code and text
        print(response.status_code)
        print(response.text)

    except HttpError as e:
        print(f'Error getting statistics for {singer}: {e}')
