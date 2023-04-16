import io
import os
import requests
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# Set up your Airtable API key and base ID
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_YT_TABLE_NAME = os.getenv('AIRTABLE_YT_TABLE__NAME')

# Set up your Airtable access token
AIRTABLE_ACCESS_TOKEN = os.getenv('AIRTABLE_ACCESS_TOKEN')

# Define the URL for the Airtable API
url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_YT_TABLE_NAME}'

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
response = requests.get(url, params=params, headers=headers)

# Check if the request was successful
if response.status_code != 200:
    print(f'Request failed with status code {response.status_code}')
else:
    # Parse the JSON response from the Airtable API
    data = response.json()

    # Check if the response contains the expected data
    if 'records' not in data:
        print('Response does not contain records')
    else:
        # Loop through the records and display the thumbnail image and the other fields
        for record in data['records']:
            rank = record['fields']['Rank']
            artist = record['fields']['Artist']
            thumbnail_url = record['fields']['Thumbnail'][0]['url']
            subscribers = record['fields']['Subscribers']
            views = record['fields']['Views']
            videos = record['fields']['Videos']
            published_time = record['fields']['PublishedTime']

            # Send a GET request to retrieve the thumbnail image
            response = requests.get(thumbnail_url)

            # Load the image using matplotlib
            image = plt.imread(io.BytesIO(response.content))

            # Display the image using matplotlib
            plt.imshow(image)
            plt.axis('off')
            plt.show()

            # Print the other fields
            print(f'Rank: {rank}')
            print(f'Artist: {artist}')
            print(f'Subscribers: {subscribers}')
            print(f'Views: {views}')
            print(f'Videos: {videos}')
            print(f'Published Time: {published_time}')
            print('---')
