import os
import json
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv() # load the environment variables from the .env file


# Define your API key
YT_API_KEY = os.getenv('YT_API_KEY')

# Define a list of Burundian singer names to search for
singer_names = ['Kidum Kibido']

# Create a YouTube API client
youtube = build('youtube', 'v3', developerKey=YT_API_KEY)

# Retrieve the channel ID for each singer
channel_ids = {}
for singer in singer_names:
    search_response = youtube.search().list(
        q=singer + ' Burundi',
        type='channel',
        part='id,snippet',
        maxResults=1
    ).execute()
    channel_id = search_response['items'][0]['id']['channelId']
    channel_ids[singer] = channel_id

# Save the channel IDs to a JSON file
with open('burundian_singer_channel_ids.json', 'w') as f:
    json.dump(channel_ids, f)


