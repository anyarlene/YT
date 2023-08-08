import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Load the API keys and Airtable credentials from the .env file
load_dotenv()

# Constants
AIRTABLE_ACCESS_TOKEN = os.getenv('AIRTABLE_ACCESS_TOKEN')
TARGET_AIRTABLE_ACCESS_TOKEN = os.getenv('TARGET_AIRTABLE_ACCESS_TOKEN')
TARGET_AIRTABLE_BASE_ID = os.getenv('TARGET_AIRTABLE_BASE_ID')
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
SOURCE_ENDPOINT_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/Table 1 copy 2"
TARGET_ENDPOINT_URL = f"https://api.airtable.com/v0/{TARGET_AIRTABLE_BASE_ID}/Table 1"
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}
TARGET_HEADERS = {
    "Authorization": f"Bearer {TARGET_AIRTABLE_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}
MIN_CPM = 0.25 / 1000  
MAX_CPM = 4.00 / 1000  

# Fetch data from Airtable
response = requests.get(SOURCE_ENDPOINT_URL, headers=HEADERS)
data = response.json()['records']

# After converting the data to a pandas DataFrame
df = pd.DataFrame([record['fields'] for record in data])

# Sort the DataFrame by creation_timestamp, then by subscribers (in descending order) per artist, and finally by rank
df = df.sort_values(by=['creation_timestamp', 'subscribers', 'rank'], ascending=[True, False, True])



# Process the data as per the provided logic
df['creation_timestamp'] = pd.to_datetime(df['creation_timestamp'])
df['previous_video_views'] = df.groupby('artist')['video_views'].shift(1).fillna(df['video_views'])
df['views_difference'] = df['video_views'] - df['previous_video_views']
df.loc[df['creation_timestamp'] == '2023-08-03', 'views_difference'] = df['video_views']
df['min_earnings'] = df['views_difference'] * MIN_CPM
df['max_earnings'] = df['views_difference'] * MAX_CPM
df['estimated_earnings'] = df.apply(lambda x: f"${round(x['min_earnings'])} - ${round(x['max_earnings'])}", axis=1)


# Post the results to the new Airtable
for _, row in df.iterrows():
    # Extracting the URL from the thumbnail data, assuming it's a list of dictionaries with a 'url' key
    thumbnail_url = row.get('thumbnail', [{}])[0].get('url') if row.get('thumbnail', None) else None

    payload = {
        "fields": {
            "record_id_ref": row.get('record_id_ref', None),
            "rank": row.get('rank', None),
            "artist": row.get('artist', None),
            "thumbnail": [{"url": thumbnail_url}] if thumbnail_url else [],
            "subscribers": row.get('subscribers', None),
            "video_views": row.get('video_views', None),
            "video_count": row.get('video_count', None),
            "published_date": row.get('published_date', None),
            "creation_timestamp": str(row.get('creation_timestamp', None)),
            "estimated_earnings": row['estimated_earnings']
        }
    }
    response = requests.post(TARGET_ENDPOINT_URL, headers=TARGET_HEADERS, json=payload)
    if response.status_code != 200:
        print(f"Failed to add record for artist {row['artist']}: {response.text}")
