import requests
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from io import BytesIO
import os

# Airtable settings
AIRTABLE_ACCESS_TOKEN = os.getenv('TARGET_AIRTABLE_ACCESS_TOKEN')
AIRTABLE_BASE_ID = os.getenv('TARGET_AIRTABLE_BASE_ID')
LATEST_RELEASE_TABLE_NAME = os.getenv('LATEST_RELEASE_TABLE_NAME')

# Define the Airtable endpoint and headers
url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{LATEST_RELEASE_TABLE_NAME}"
headers = {
    "Authorization": f"Bearer {AIRTABLE_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# Fetch the data from Airtable
response = requests.get(url, headers=headers)
data = response.json().get('records')

# Extract artist names, video views, and thumbnails
artists = [record['fields']['artist'] for record in data]
views = [int(record['fields']['latest_video_views']) for record in data]
thumbnails = [record['fields']['channel_thumbnail'] for record in data]

# Plotting
fig, ax = plt.subplots(figsize=(10, len(artists) * 2))

# Display bar chart
y_positions = range(len(artists))
ax.barh(y_positions, views, color='blue', align='center')

# Display artist thumbnails next to each bar
for i, thumbnail_url in enumerate(thumbnails):
    response = requests.get(thumbnail_url)
    img = mpimg.imread(BytesIO(response.content))
    ax.imshow(img, aspect='auto', extent=[views[i]-max(views)*0.1, views[i], i-0.4, i+0.4])

ax.set_yticks(y_positions)
ax.set_yticklabels(artists)
ax.set_xlabel('Video Views')
ax.set_title('Latest Video Views by Artist')

plt.tight_layout()
plt.show()
