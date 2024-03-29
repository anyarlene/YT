# YouTube Channel Stats and Earnings Estimator
This script fetches, calculates, and records the statistics and potential earnings of specified YouTube channels (burundian singers specifically) based on an assumed CPM.

# Features
- Fetch YouTube channel statistics including subscriber count, view count, video count, and more.
- Calculate an estimate of the channel's potential earnings based on view count and a presumed CPM.
- Sort the channels based on subscriber count.
- Save all information, including earnings estimates, in Airtable using Airtable's API.

# Setup & Usage
## Prerequisites

- Python 3.6 or higher
- Required Python packages: json, os, requests, googleapiclient, dotenv, datetime
To install these packages, use pip:

```pip install requests google-auth google-auth-httplib2 google-auth-oauthlib google-api-python-client oauthlib six python-dotenv```

# Configuration
1. Clone this repository to your local machine.
2. Create a .env file in your project root and add your YouTube API Key, Airtable Access Token and Airtable Base ID as shown below:

```
YT_API_KEY='Your YouTube API Key'
AIRTABLE_ACCESS_TOKEN='Your Airtable Access Token'
AIRTABLE_BASE_ID='Your Airtable Base ID'
```
1. In the 'channel-id-data' folder, add a JSON file named 'burundian_singer_channel_ids.json' which contains a dictionary where the keys are the names of the channels you are interested in and the values are the corresponding channel IDs. The format should look like this:

```
{
    "Channel Name 1": "Channel ID 1",
    "Channel Name 2": "Channel ID 2",
    ...
}
```
# Scheduled Jobs
#### YouTube Statistics Job
The main script `yt_statistics_airtable.py` is automated to run periodically (every day at midnight) using a scheduler. The schedule for this job is defined in the yt_stats.job.yml. This ensures that the Airtable data is consistently updated without manual intervention.

#### Estimated Earnings Update Job
The `update_estimated_earnings.py` script is scheduled to run every day at 6 a.m. to ensure that the earnings estimates are consistently updated. This job fetches the new records from the source and processes them to update or add new records to the target Airtable base. The schedule for this job is defined in the `estimated_earnings.job.yml`.

Both jobs work in tandem to ensure the data remains up-to-date and accurate in the target Airtable.

# Earnings Estimation
The potential earnings of a channel are estimated based on the channel's view count and a given range for the CPM (Cost Per Mille). The CPM represents how much money an advertiser is willing to pay for a thousand views of their advertisement.

In this script, we estimate earnings using an average CPM of $1.00 (or $0.001 per view). This is a conservative estimate and the actual CPM can range widely from $0.25 to $4.00 and even higher. The exact CPM depends on many factors including video content, viewer demographics, individual contract terms, etc. Please note that these estimates are potential earnings and actual earnings can vary significantly based on the factors mentioned above.

The script `update_estimated_earnings.py` calculates the estimated earnings for the YouTube channels, considering the difference in video views between the current and previous timestamps. The earnings are calculated per artist based on this difference.

The script follows a methodology of fetching records from a source Airtable, processing the data, and then updating or adding new records to a target Airtable. The process ensures that new records added to the source are reflected in the target, and existing records are updated as necessary.

