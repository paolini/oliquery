from api import Api

api = Api()
api.login()

def sanitize(s):
    return s.replace("\n", " ").replace("\r", " ").replace("\t", " ")

cursor = ""
print("\t".join(["id","name","isActive","email","type"]))
while True:
    r = api.query("""{
    schools {
        schools(after:"$$") {
        totalCount
        pageInfo {
            hasNextPage
            endCursor
        }
        edges {
            node {
            id
            name
            isActive
            email
            type
            }
        }
        }
    }
    }""".replace("$$", cursor))

    schools = r["data"]["schools"]["schools"]
    edges = schools["edges"]
    for edge in edges:
        node = edge["node"]
        row = [
            str(node["id"]),
            sanitize(node["name"]), 
            str(1 if node["isActive"] else 0), 
            sanitize(node["email"]), 
            sanitize(node["type"])
        ]
        print("\t".join(row))
    cursor = schools["pageInfo"]["endCursor"]
    hasNextPage = schools["pageInfo"]["hasNextPage"]
    if not hasNextPage:
        break
