import unittest
from yt_data_model import YouTubeDataModel
from unittest.mock import patch

class TestYouTubeDataModel(unittest.TestCase):
    
    @patch('yt_data_model.build')
    def test_get_channel_data(self, mock_build):
        # Setup mock response
        mock_response = {
            'items': [
                {
                    'snippet': {'publishedAt': '2023-01-01T00:00:00Z'},
                    'statistics': {
                        'subscriberCount': '1000',
                        'viewCount': '5000',
                        'videoCount': '100'
                    }
                }
            ]
        }
        mock_service = mock_build.return_value
        mock_service.channels().list().execute.return_value = mock_response

        # Test
        yt_data_model = YouTubeDataModel()
        data = yt_data_model.get_channel_data('channel_id')
        self.assertEqual(data['subscriber_count'], '1000')
        self.assertEqual(data['view_count'], '5000')
        self.assertEqual(data['video_count'], '100')
        self.assertEqual(data['published_at'], '2023-01-01')

    # Add more tests as needed

if __name__ == '__main__':
    unittest.main()
