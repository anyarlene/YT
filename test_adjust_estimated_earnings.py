import pandas as pd

# Constants
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
df['estimated_earnings'] = df.apply(lambda x: f"${round(x['min_earnings'])} - ${round(x['max_earnings'])}", axis=1)

# Drop intermediate columns and display the results
df.drop(columns=['min_earnings', 'max_earnings'], inplace=True)
print(df)
# Filter the DataFrame for artist "Sat-B" and display
#sat_b_df = df[df['artist'] == 'Sat-B']
#print(sat_b_df)

#berry_music_df = df[df['artist'] == 'Berry Music']
#print(berry_music_df)


#ester_nish_df = df[df['artist'] == 'Esther Nish Official']
#print(ester_nish_df)
