import os
import requests
from operator import itemgetter

# Set up your Airtable API key and base ID
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_YT_TABLE_NAME = os.getenv('AIRTABLE_YT_TABLE__NAME')

# Set up your Airtable access token
AIRTABLE_ACCESS_TOKEN = os.getenv('AIRTABLE_ACCESS_TOKEN')

# Define the URL for the Airtable API
url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_YT_TABLE_NAME}'

# Define the parameters for the Airtable API request
params = {
    'fields': ['Rank', 'Thumbnail'],
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
        # Create a list of thumbnail URLs sorted by rank
        thumbnail_urls = []
        for record in data['records']:
            thumbnail_url = record['fields']['Thumbnail'][0]['url']
            rank = record['fields']['Rank']
            thumbnail_urls.append({'rank': rank, 'thumbnail_url': thumbnail_url})

        thumbnail_urls_sorted = sorted(thumbnail_urls, key=itemgetter('rank'))

        # Print the sorted list of thumbnail URLs
        for thumbnail in thumbnail_urls_sorted:
            print(thumbnail['thumbnail_url'])
