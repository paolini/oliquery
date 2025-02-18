from api import Api
from mycsv import sanitize, csv_row, csv_header

query = """query Prova($CURSOR: String, $EDITION: String!) {
  olympiads{
    edition(id: $EDITION) {
      subscriptions(after: $CURSOR) {
        edges {
          node {
            status
            isValid
            invalidatedAt
            donation
            contact {
              id
              fullName
              isActive
              user {
                email
              }
            }
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
  }
}"""

api=Api(requireEdition=True)
api.login()
cursor = ""
fields = ["status", "isValid", "invalidatedAt", "donation", "contact.id", "contact.fullName", "contact.isActive", "contact.user.email"]
print(csv_header(fields))
while True:
    r = api.query(query, {"CURSOR": cursor})
    if "errors" in r:
        raise Exception(r["errors"])
    subscriptions = r["data"]["olympiads"]["edition"]["subscriptions"]
    hasNextPage = subscriptions["pageInfo"]["hasNextPage"]
    cursor = subscriptions["pageInfo"]["endCursor"]
    for subscription in subscriptions["edges"]:
        node = subscription["node"]
        print(csv_row(node, fields))
    if not hasNextPage:
        break