import json
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load the API key from the .env file
load_dotenv()
YT_API_KEY = os.getenv('YT_API_KEY')

# Define a function to get the YouTube channel ID for a given singer name
def get_channel_id(singer_name):
    youtube = build('youtube', 'v3', developerKey=YT_API_KEY)

    # Search for the singer's channel using their name as the query
    request = youtube.search().list(
        q=singer_name,
        type='channel',
        part='id'
    )
    response = request.execute()

    # Get the ID of the first channel in the response
    channel_id = response['items'][0]['id']['channelId']

    return channel_id

# Open the singers JSON file and load the data
with open('bdi_singers.json', 'r') as f:
    data = json.load(f)

# Get the list of singers from the data
singers = data['singers']

# Create a new dictionary to store the channel IDs
channels = {}

# Get the YouTube channel ID for each singer and add it to the channels dictionary
for singer in singers:
    try:
        channel_id = get_channel_id(singer)
        channels[singer] = channel_id
    except HttpError as e:
        print(f'Error getting channel ID for {singer}: {e}')

# Save the channels dictionary to a new JSON file
with open('burundian_singer_channel_ids.json', 'w') as f:
    json.dump(channels, f)
