import os
from googleapiclient.discovery import build
from airtable import Airtable

# Define your API keys
YT_API_KEY = 'your_youtube_api_key_here'
AIRTABLE_API_KEY = 'your_airtable_api_key_here'
AIRTABLE_BASE_ID = 'your_airtable_base_id_here'

# Define a list of channel IDs for the singers you are interested in
channel_ids = ['channel_id_1', 'channel_id_2', 'channel_id_3']

# Create a YouTube API client
youtube = build('youtube', 'v3', developerKey=YT_API_KEY)

# Retrieve the channel statistics for each channel ID
data = []
for channel_id in channel_ids:
    channel_response = youtube.channels().list(
        part='statistics',
        id=channel_id
    ).execute()
    channel_stats = channel_response['items'][0]['statistics']
    channel_stats['channel_id'] = channel_id  # Add the channel ID to the data
    data.append(channel_stats)

# Initialize the Airtable client
# 'Table Name' = table created in Airtable
airtable = Airtable(AIRTABLE_BASE_ID, 'Table Name', api_key=AIRTABLE_API_KEY)

# Insert the data into Airtable
for row in data:
    airtable.insert(row, typecast=True)
