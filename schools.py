from api import Api

api = Api({"EDITION": "olimat24"})
api.login()

def sanitize(s):
    return s.replace("\n", " ").replace("\r", " ").replace("\t", " ")

cursor = ""
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
        print("{}\t{}\t{}\t{}\t{}".format(node["id"],sanitize(node["name"]), 1 if node["isActive"] else 0, sanitize(node["email"]), sanitize(node["type"])))
    cursor = schools["pageInfo"]["endCursor"]
    hasNextPage = schools["pageInfo"]["hasNextPage"]
    if not hasNextPage:
        break
