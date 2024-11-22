import json
import os

from api import Api

api=Api({"EDITION_ID":"olimat24"})
api.login()

query = """query MyQuery {
  emails {
    emails(editionId:"olimat25",after:"$CURSOR") {
      totalCount
      pageInfo {
        hasNextPage
        endCursor
      }
      edges {
        node {
          subject
          to
        }
      }
    }
  }
}"""

cursor = ""

while True:
    r = api.query(query.replace("$CURSOR", cursor))
    emails = r["data"]["emails"]["emails"]
    hasNextPage = emails["pageInfo"]["hasNextPage"]
    cursor = emails["pageInfo"]["endCursor"]
    for email in emails["edges"]:
        print("{}\t{}".format(email["node"]["to"], email["node"]["subject"]))