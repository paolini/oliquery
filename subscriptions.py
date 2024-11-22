import json
import os

from api import Api, sanitize

api=Api({"EDITION_ID":"olimat24"})
api.login()

query = """query Prova {
  olympiads{
    edition(id:"olimat25") {
      subscriptions(after: "$CURSOR") {
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

cursor = ""
print("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(
    "Status", 
    "IsValid", 
    "InvalidatedAt", 
    "Donation", 
    "ContactID", 
    "FullName",
    "IsActive", 
    "Email"))
while True:
    r = api.query(query.replace("$CURSOR", cursor))
    subscriptions = r["data"]["olympiads"]["edition"]["subscriptions"]
    hasNextPage = subscriptions["pageInfo"]["hasNextPage"]
    cursor = subscriptions["pageInfo"]["endCursor"]
    for subscription in subscriptions["edges"]:
        node = subscription["node"]
        contact = node["contact"]
        user = contact["user"]
        print("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(
            node["status"], 
            node["isValid"], 
            sanitize(node["invalidatedAt"]), 
            sanitize(node["donation"]), 
            contact["id"], 
            sanitize(contact["fullName"]),
            1 if contact["isActive"] else 0, 
            sanitize(user["email"])))
    if not hasNextPage:
        break