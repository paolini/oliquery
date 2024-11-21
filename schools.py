import json

filename="~/Downloads/scuole-olimat25.json"

# Replace 'file.json' with the path to your JSON file
with open('data.json', 'r') as file:
    data = json.load(file)

edges = data["data"]["olympiads"]["edition"]["subscriptions"]["edges"]
print(len(edges))

