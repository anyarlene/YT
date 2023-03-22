import pandas as pd
from googleapiclient.discovery import build

# Define your API key
API_KEY = 'your_api_key_here'

# Define a list of channel IDs for the singers you are interested in
channel_ids = ['channel_id_1', 'channel_id_2', 'channel_id_3']

# Define a list to store the data for each channel
data = []

# Create a YouTube API client
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Loop through each channel ID and retrieve the statistics
for channel_id in channel_ids:
    channel_response = youtube.channels().list(
        part='statistics',
        id=channel_id
    ).execute()
    
    # Extract the statistics from the API response
    channel_stats = channel_response['items'][0]['statistics']
    
    # Add the statistics to the data list
    data.append(channel_stats)
    
# Convert the data to a DataFrame
df = pd.DataFrame(data)

# Print the DataFrame
print(df)
