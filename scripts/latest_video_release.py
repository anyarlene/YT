import json
import os
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
YT_API_KEY = os.getenv('YT_API_KEY')
TARGET_AIRTABLE_ACCESS_TOKEN = os.getenv('TARGET_AIRTABLE_ACCESS_TOKEN')
TARGET_AIRTABLE_BASE_ID = os.getenv('TARGET_AIRTABLE_BASE_ID')
LATEST_RELEASE_TABLE_NAME = os.getenv('LATEST_RELEASE_TABLE_NAME')

# Define the Airtable endpoint and headers
url = f"https://api.airtable.com/v0/{TARGET_AIRTABLE_BASE_ID}/{LATEST_RELEASE_TABLE_NAME}"
headers = {
    "Authorization": f"Bearer {TARGET_AIRTABLE_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def get_channel_id(singer_name):
    youtube = build('youtube', 'v3', developerKey=YT_API_KEY)
    request = youtube.search().list(q=singer_name, type='channel', part='id,snippet')
    response = request.execute()
    channel_id = response['items'][0]['id']['channelId']
    channel_thumbnail = response['items'][0]['snippet']['thumbnails']['default']['url']
    return channel_id, channel_thumbnail

def get_latest_video(channel_id):
    youtube = build('youtube', 'v3', developerKey=YT_API_KEY)
    date_one_month_ago = (datetime.now() - timedelta(days=30)).isoformat() + "Z"
    
    request = youtube.search().list(
        channelId=channel_id,
        order="date",
        type="video",
        publishedAfter=date_one_month_ago,
        maxResults=1,
        part="snippet"
    )
    response = request.execute()
    if response['items']:
        video = response['items'][0]
        video_id = video['id']['videoId']
        video_details = youtube.videos().list(
            id=video_id,
            part="statistics,snippet"
        ).execute()
        
        views = video_details['items'][0]['statistics']['viewCount']
        video_thumbnail = video_details['items'][0]['snippet']['thumbnails']['default']['url']
        
        return {
            'video_id': video_id,
            'title': video['snippet']['title'],
            'published_at': video['snippet']['publishedAt'],
            'video_views': views,
            'thumbnail': video_thumbnail
        }
    return None

def get_existing_record_id(singer):
    query_url = f"{url}?filterByFormula=({{{'artist'}}}='{singer}')"
    response = requests.get(query_url, headers=headers)
    records = response.json().get('records')
    return records[0]['id'] if records else None

# Load singer data from JSON file
with open('bdi_singers.json', 'r') as f:
    data = json.load(f)
singers = data['singers']

# Process each singer
for singer in singers:
    try:
        channel_id, channel_thumbnail = get_channel_id(singer)
        latest_video = get_latest_video(channel_id)
        
        if latest_video:
            current_timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')  # ISO 8601 format
            data = {
                "fields": {
                    "channel_id": channel_id,
                    "video_id": latest_video['video_id'],
                    "latest_video": latest_video['title'],
                    "latest_video_views": latest_video['video_views'],
                    "published_date_latest_video": latest_video['published_at'],
                    "artist": singer,
                    "channel_thumbnail": channel_thumbnail,
                    "video_thumbnail": latest_video['thumbnail'],
                    "creation_timestamp": current_timestamp
                }
            }

            existing_record_id = get_existing_record_id(singer)
            
            if existing_record_id:
                patch_url = f"{url}/{existing_record_id}"
                response = requests.patch(patch_url, headers=headers, json=data)
            else:
                response = requests.post(url, headers=headers, json=data)

                if response.status_code == 200:
                    record_id = response.json()['id']
                    patch_data = {
                        "fields": {
                            "record_id_ref": record_id
                        }
                    }
                    patch_url = f"{url}/{record_id}"
                    patch_response = requests.patch(patch_url, headers=headers, json=patch_data)
                    
                    if patch_response.status_code == 200:
                        print(f"Record for singer {singer} was created and updated successfully.")
                    else:
                        print(f"Failed to update record_id_ref for singer {singer}: {patch_response.text}")
                else:
                    print(f"Failed to create record for singer {singer}: {response.text}")

    except HttpError as e:
        print(f"Error processing {singer}: {e}")
