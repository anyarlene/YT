import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from datetime import datetime

class YouTubeDataModel:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('YT_API_KEY')
        self.api_service_name = "youtube"
        self.api_version = "v3"

    def get_channel_data(self, channel_id):
        youtube = build(self.api_service_name, self.api_version, developerKey=self.api_key)
        try:
            request = youtube.channels().list(
                id=channel_id,
                part='snippet, statistics'
            )
            response = request.execute()
            return self._extract_data(response)
        except HttpError as e:
            print(f'Error getting statistics for {channel_id}: {e}')
            return None

    def _extract_data(self, response):
        published_date = datetime.fromisoformat(response['items'][0]['snippet']['publishedAt'].rstrip('Z')).strftime('%Y-%m-%d')
        return {
            'subscriber_count': response['items'][0]['statistics']['subscriberCount'],
            'view_count': response['items'][0]['statistics']['viewCount'],
            'video_count': response['items'][0]['statistics']['videoCount'],
            'published_at': published_date
        }
