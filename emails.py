from api import Api, sanitize

api = Api({"EDITION": "olimat24"})
api.login()

r = api.query("""query MyQuery {
  emails {
    emails(editionId: "olimat25") {
      totalCount
      pageInfo {
        hasNextPage
        endCursor
      }
      edges {
        node {
          subject
          deliveryStatus
        }
      }
    }
  }
}""")
emails = r["data"]["emails"]["emails"]
edges = emails["edges"]
count = 0
for edge in edges:
    node = edge["node"]
    print("{}\t{}\t{}".format(count,sanitize(node["subject"]), node["deliveryStatus"]))