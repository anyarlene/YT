import os
from PIL import Image
import io
import requests
from dotenv import load_dotenv

# Set up your Airtable API key and base ID
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_YT_TABLE_NAME = os.getenv('AIRTABLE_YT_TABLE__NAME')

# Set up your Airtable access token
AIRTABLE_ACCESS_TOKEN = os.getenv('AIRTABLE_ACCESS_TOKEN')

# Define the URL for the Airtable API
url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_YT_TABLE_NAME}/Table%201'

# Define the parameters for the Airtable API request
params = {
    'fields': ['Rank', 'Artist', 'Thumbnail', 'Subscribers', 'Views', 'Videos', 'PublishedTime'],
    'sort': [{'field': 'Rank', 'direction': 'asc'}]
}

# Define the headers for the Airtable API request
headers = {
    'Authorization': f'Bearer {AIRTABLE_ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

# Send a GET request to the Airtable API
try:
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status() # Raise an exception for 4xx or 5xx status codes
except requests.exceptions.RequestException as e:
    print(f"Error occurred: {e}")
    # You can choose to exit the program or try again later
    exit()

# Parse the JSON response from the Airtable API
try:
    data = response.json()
    records = data.get('records', [])
except KeyError:
    print("Error: 'records' key not found in response")
    exit()

# Loop through the records and print the values for each field
for record in records:
    rank = record['fields']['Rank']
    artist = record['fields']['Artist']
    thumbnail_url = record['fields']['Thumbnail'][0]['url']
    subscribers = record['fields']['Subscribers']
    views = record['fields']['Views']
    videos = record['fields']['Videos']
    published_time = record['fields']['PublishedTime']

    # Send a GET request to retrieve the thumbnail image
    try:
        response = requests.get(thumbnail_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        continue

    # Load the image using Pillow
    try:
        image = Image.open(io.BytesIO(response.content))
    except IOError as e:
        print(f"Error occurred: {e}")
        continue

    # Display the image and the other fields
    image.show()
    print(f'Rank: {rank}')
    print(f'Artist: {artist}')
    print(f'Subscribers: {subscribers}')
    print(f'Views: {views}')
    print(f'Videos: {videos}')
    print(f'Published Time: {published_time}')
    print('---')
