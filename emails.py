import sys
from api import Api
from mycsv import csv_header, csv_row

query = """query MyQuery($EDITION: String!, $CURSOR: String) {
  emails {
    emails(editionId:$EDITION,after:$CURSOR) {
      totalCount
      pageInfo {
        hasNextPage
        endCursor
      }
      edges {
        node {
          subject
          to
          deliveryStatus
        }
      }
    }
  }
}"""

api=Api(requireEdition=True)
api.login()

cursor = ""

fields = ["subject", "to", "deliveryStatus"]
print(csv_header(fields))
hasNextPage = True
while hasNextPage:
    r = api.query(query,{"CURSOR": cursor})
    if not cursor:
        print("Total emails: {}".format(r["data"]["emails"]["emails"]["totalCount"]), file=sys.stderr)
    emails = r["data"]["emails"]["emails"]
    cursor = emails["pageInfo"]["endCursor"]
    for email in emails["edges"]:
        print(csv_row(email["node"], fields))
    hasNextPage = emails["pageInfo"]["hasNextPage"]
