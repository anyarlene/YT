import pandas as pd
import requests
import os
from dotenv import load_dotenv

# Load the API keys and Airtable credentials from the .env file
load_dotenv()

# Constants
AIRTABLE_ACCESS_TOKEN = os.getenv('AIRTABLE_ACCESS_TOKEN')
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
ENDPOINT_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/Table 1 copy 6"
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

MIN_CPM = 0.25 / 1000  
MAX_CPM = 4.00 / 1000  

# Read the CSV into a DataFrame
df = pd.read_csv('/Users/any-arleneniyubahwe/Desktop/private2/my-git/ejo/YT/airtable-data-for-adjustments/Table 1-Grid view.csv')

# Convert the 'creation_timestamp' column to datetime format for calculations
df['creation_timestamp'] = pd.to_datetime(df['creation_timestamp'])

# Compute views_difference for each artist based on creation_timestamp
df['previous_video_views'] = df.groupby('artist')['video_views'].shift(1).fillna(df['video_views'])
df['views_difference'] = df['video_views'] - df['previous_video_views']

# Special handling for '2023-08-03' timestamps
df.loc[df['creation_timestamp'] == '2023-08-03', 'views_difference'] = df['video_views']

# Calculate estimated_earnings
df['min_earnings'] = df['views_difference'] * MIN_CPM
df['max_earnings'] = df['views_difference'] * MAX_CPM
df['Estimated Earnings'] = df.apply(lambda x: f"${round(x['min_earnings'])} - ${round(x['max_earnings'])}", axis=1)

# Patch the new estimated_earnings values back to Airtable using record_id_ref
for index, row in df.iterrows():
    record_id = row['record_id_ref']
    payload = {
        "fields": {
            "estimated_earnings": row['Estimated Earnings']
        }
    }
    response = requests.patch(f"{ENDPOINT_URL}/{record_id}", headers=HEADERS, json=payload)
    if response.status_code != 200:
        print(f"Failed to update record for artist {row['artist']}: {response.text}")

print("Data updated successfully!")
