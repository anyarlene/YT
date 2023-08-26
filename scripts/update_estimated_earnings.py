import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Load the API keys and Airtable credentials from the .env file
load_dotenv()

# Constants
AIRTABLE_ACCESS_TOKEN = os.getenv('AIRTABLE_ACCESS_TOKEN')
TARGET_AIRTABLE_ACCESS_TOKEN = os.getenv('TARGET_AIRTABLE_ACCESS_TOKEN')
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
TARGET_AIRTABLE_BASE_ID = os.getenv("TARGET_AIRTABLE_BASE_ID")
SOURCE_TABLE_NAME = os.getenv("SOURCE_TABLE_NAME")
TARGET_TABLE_NAME = os.getenv("TARGET_TABLE_NAME")
SOURCE_ENDPOINT_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{SOURCE_TABLE_NAME}"
TARGET_ENDPOINT_URL = f"https://api.airtable.com/v0/{TARGET_AIRTABLE_BASE_ID}/{TARGET_TABLE_NAME}"
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

# Fetch records from the source table
all_records = []
offset = None
while True:
    params = {}
    if offset:
        params["offset"] = offset

    response = requests.get(SOURCE_ENDPOINT_URL, headers=HEADERS, params=params)
    data = response.json()
    if 'records' not in data:
        print("Error fetching from source table:", data)
        break

    all_records.extend(data['records'])
    offset = data.get('offset')
    if not offset:
        break

# Fetch all records from the target table
target_records = []
offset = None
while True:
    params = {}
    if offset:
        params["offset"] = offset

    response = requests.get(TARGET_ENDPOINT_URL, headers=TARGET_HEADERS, params=params)
    data = response.json()
    if 'records' not in data:
        print("Error fetching from target table:", data)
        break

    target_records.extend(data['records'])
    offset = data.get('offset')
    if not offset:
        break

# Process the source data
df = pd.DataFrame([record['fields'] for record in all_records])

if 'creation_timestamp' in df.columns:
    df['creation_timestamp'] = pd.to_datetime(df['creation_timestamp'])
else:
    df['creation_timestamp'] = pd.NaT

df.sort_values(by=['artist', 'creation_timestamp'], inplace=True)
df['previous_video_views'] = df.groupby('artist')['video_views'].shift(1).fillna(0)
df['views_difference'] = df['video_views'] - df['previous_video_views']
df.loc[df.groupby('artist')['creation_timestamp'].idxmin(), 'views_difference'] = 0

df['min_earnings'] = df['views_difference'] * MIN_CPM
df['max_earnings'] = df['views_difference'] * MAX_CPM
df['estimated_earnings'] = df.apply(lambda x: f"${round(x['min_earnings'])} - ${round(x['max_earnings'])}", axis=1)
df = df.sort_values(by=['creation_timestamp', 'subscribers', 'rank'], ascending=[True, False, True])

# Convert the target data to DataFrame for easy lookup
target_df = pd.DataFrame([{'id': record['id'], **record['fields']} for record in target_records])
target_ids_set = set(target_df['record_id_ref'].tolist())

# Iterate over the processed records and update or create in the target table
for _, row in df.iterrows():
    payload = {
        "fields": {
            "record_id_ref": row.get('record_id_ref', None),
            "rank": row.get('rank', None),
            "artist": row.get('artist', None),
            "subscribers": row.get('subscribers', None),
            "video_views": row.get('video_views', None),
            "video_count": row.get('video_count', None),
            "published_date": row.get('published_date', None),
            "creation_timestamp": str(row.get('creation_timestamp', None)),
            "estimated_earnings": row['estimated_earnings']
        }
    }

    # Check if the record exists in the target table
    if row['record_id_ref'] in target_ids_set:
        record_id = target_df[target_df['record_id_ref'] == row['record_id_ref']].iloc[0]['id']
        response = requests.patch(f"{TARGET_ENDPOINT_URL}/{record_id}", headers=TARGET_HEADERS, json=payload)
        if response.status_code != 200:
            print(f"Failed to update record for artist {row['artist']}: {response.text}")
    else:
        response = requests.post(TARGET_ENDPOINT_URL, headers=TARGET_HEADERS, json=payload)
        if response.status_code != 200:
            print(f"Failed to add record for artist {row['artist']}: {response.text}")