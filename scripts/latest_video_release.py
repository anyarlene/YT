import json
import os
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
YT_API_KEY = os.getenv('YT_API_KEY')
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
LATEST_RELEASE_TABLE_NAME = os.getenv('LATEST_RELEASE_TABLE_NAME')

def get_channel_id(singer_name):
    youtube = build('youtube', 'v3', developerKey=YT_API_KEY)
    request = youtube.search().list(q=singer_name, type='channel', part='id')
    response = request.execute()
    channel_id = response['items'][0]['id']['channelId']
    return channel_id

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
            part="statistics"
        ).execute()
        
        views = video_details['items'][0]['statistics']['viewCount']
        
        return {
            'video_id': video_id,
            'title': video['snippet']['title'],
            'published_at': video['snippet']['publishedAt'],
            'video_views': views
        }
    return None

with open('bdi_singers.json', 'r') as f:
    data = json.load(f)

singers = data['singers']

for singer in singers:
    try:
        channel_id = get_channel_id(singer)
        latest_video = get_latest_video(channel_id)
        
        if latest_video:
            # Prepare the data for Airtable
            data = {
                "fields": {
                    "channel_id": channel_id,
                    "video_id": latest_video['video_id'],
                    "latest_video": latest_video['title'],
                    "latest_video_views": latest_video['video_views'],
                    "published_date_latest_video": latest_video['published_at'],
                    "artist": singer
                }
            }

            # Send the data to Airtable
            url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{LATEST_RELEASE_TABLE_NAME}"
            headers = {
                "Authorization": f"Bearer {AIRTABLE_API_KEY}",
                "Content-Type": "application/json"
            }
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                print(f"Data for {singer} uploaded successfully!")
            else:
                print(f"Failed to upload data for {singer}: {response.text}")
    except HttpError as e:
        print(f"Error processing {singer}: {e}")
