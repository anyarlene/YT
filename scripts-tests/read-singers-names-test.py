import json

# Open the singers JSON file and load the data
with open('bdi-singers.json', 'r') as f:
    data = json.load(f)

# Get the list of singers from the data
singers = data['singers']

# Print the names of the singers
for singer in singers:
    print(singer)
