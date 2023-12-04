import json
from datetime import datetime
from yt_data_model import YouTubeDataModel  # Import YouTubeDataModel from its file
from airtable_data_model import AirtableDataModel  # Import AirtableDataModel from its file

def main():
    # Instantiate the data model classes
    yt_data_model = YouTubeDataModel()
    airtable_data_model = AirtableDataModel()

    with open('channel-id-data/burundian_singer_channel_ids.json', 'r') as f:
        channels = json.load(f)

    channel_list = [(singer, int(yt_data_model.get_channel_data(channel_id)['subscriber_count'])) for singer, channel_id in channels.items()]
    channel_list.sort(key=lambda x: x[1], reverse=True)
    ranked_list = [(i+1, singer, subs) for i, (singer, subs) in enumerate(channel_list)]

    for rank, singer, subs in ranked_list:
        channel_data = yt_data_model.get_channel_data(channels[singer])
        creation_timestamp = datetime.now()
        published_date = datetime.strptime(channel_data['published_at'], '%Y-%m-%d')
        days = (creation_timestamp - published_date).days
        data = {
            'fields': {
                'rank': rank,
                'artist': singer,
                'subscribers': subs,
                'video_views': int(channel_data['view_count']),
                'video_count': int(channel_data['video_count']),
                'published_date': channel_data['published_at'],
                'creation_timestamp': creation_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            }
        }

        post_response = airtable_data_model.post_record(data)
        if post_response.status_code == 200:
            record_id = post_response.json()['id']
            update_data = {'fields': {'record_id_ref': record_id}}
            update_response = airtable_data_model.update_record(record_id, update_data)
            if update_response.status_code == 200:
                print(f"Record for singer {singer} was created and updated successfully.")
            else:
                print(f"Failed to update record for singer {singer}: {update_response.text}")
        else:
            print(f"Failed to create record for singer {singer}: {post_response.text}")

if __name__ == "__main__":
    main()
