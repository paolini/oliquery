"""
query {
  olympiads {
    edition(id: "olimat25") {
      subscriptions(first: 100) {
        pageInfo {
          hasNextPage
          endCursor
        }
        edges {
          node {
            status
            invalidatedAt
            school {
              id
              name
              email
              type
              location {
                city {
                  name
                }
              }
            }
          }
        }
      }
    }
  }
}
"""
import json

# Replace 'file.json' with the path to your JSON file
with open('data.json', 'r') as file:
    data = json.load(file)

# Access the JSON data as a Python dictionary
edges = data["data"]["olympiads"]["edition"]["subscriptions"]["edges"]
print(len(edges))