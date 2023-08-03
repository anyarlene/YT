from unittest.mock import patch
import pytest
from test_*.py import get_channel_data  # replace 'your_script' with the name of your Python file

@patch('your_script.build')  # replace 'your_script' with the name of your Python file
def test_get_channel_data(mock_build):
    # Mock the response from the YouTube API
    mock_build.return_value.channels.return_value.list.return_value.execute.return_value = {
        'items': [
            {
                'snippet': {
                    'publishedAt': '2023-07-01T00:00:00Z',
                    'thumbnails': {
                        'default': {
                            'url': 'http://example.com/image.jpg'
                        }
                    }
                },
                'statistics': {
                    'subscriberCount': '1000',
                    'viewCount': '10000',
                    'videoCount': '100'
                }
            }
        ]
    }

    # Call the function with a sample channel ID
    data = get_channel_data('UC_x5XG1OV2P6uZZ5FSM9Ttw')

    # Check that the returned data is correct
    assert data == {
        'subscriber_count': '1000',
        'profile_picture': 'http://example.com/image.jpg',
        'view_count': '10000',
        'video_count': '100',
        'published_at': '2023-07-01'
    }
