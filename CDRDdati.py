import requests
import json
import datetime
import os

def sanitize(a):
    if isinstance(a, str):
        return (a.replace(";",""))
    elif isinstance(a, int):
        return(a)
    else:
        return ("")

s = requests.Session()
session = requests.Session()

endpoint = f"https://olimpiadi-scientifiche.it/graphql/"
headers = {}

def make_query(query, session=None):
  r = session.post(endpoint, json={"query": query}, headers=headers)
  headers.update({"X-CsrfToken": r.cookies.get_dict()['csrftoken']})
  if r.status_code != 200:
      print(json.dumps(r.json(), indent=2))
      raise Exception(f"Query failed to run with a {r.status_code}.")

EMAIL = "emanuele.paolini@unipi.it"
PASSWORD = os.environ["OLI_PASSWORD"]

query1 = """mutation {
  users{
    login(email: "$EMAIL", password: "$PASSWORD"){
      __typename
      ...on OperationInfo{
        messages{
          message
          kind
        }
      }
      ...on LoginSuccess{
        user{
          email
        }
      }
    }
  }
}""".replace("$EMAIL", EMAIL).replace("$PASSWORD", PASSWORD)

query2 = """query {
  olympiads{
    edition(id:"olimat24"){
      numSubscriptions{
        total
      }
    }
  }
}"""

query3 = """query {
  zones {
    zones(filters: {olympiad: {editions: {id: {exact: "olimat24"}}}}) {
      name
      subscriptions {
        totalCount
        edges {
          node {
            school {
              externalId
              location {
                name
              }
            }
            donation
          }
        }
      }
    }
  }
}"""

query4 = """ query {
  users {
    me {
      email
    }
  }
}"""

queryCDdati = """query {
  zones {
    zones(filters: {olympiad: {editions: {id: {exact: "olimat24"}}}}) {
      name
      admins {
        user {
          name
          surname
          email
          phoneNumber
          teachers {
            school {
              name
              location {
                name
                address
                postalCode
                city {
                  name
                }
              }
            }
          }
        }
        isPrimary
      }
    }
  }
}"""

query = query1

r = s.post(endpoint, json={"query": query}, headers=headers)
headers.update({"X-CsrfToken": r.cookies.get_dict()['csrftoken']})

query = query1

r = s.post(endpoint, json={"query": query}, headers=headers)
headers.update({"X-CsrfToken": r.cookies.get_dict()['csrftoken']})
if r.status_code != 200:
    print(json.dumps(r.json(), indent=2))
    raise Exception(f"Query failed to run with a {r.status_code}.")

query = queryCDdati

r = s.post(endpoint, json={"query": query}, headers=headers)
if r.status_code == 200:
    print(datetime.datetime.now())
    CDRD = r.json()
    #print(json.dumps(r.json(), indent=2))
    for z in CDRD["data"]["zones"]["zones"]:
        #print(z["name"])
        for a in z["admins"]:
            riga = ""
            riga += sanitize(z["name"]) 
            riga += ";"
            if a["isPrimary"]:
                riga += "CD;"
            else:
                riga += "RD;"
        #print(json.dumps(r.json(), indent=2))
        #print(t + a["user"]["name"] + " " + a["user"]["surname"] + " <" + a["user"]["email"] + ">")
            riga += sanitize(a["user"]["name"]) 
            riga += ";"
            riga += sanitize(a["user"]["surname"])
            riga += ";"
            riga += sanitize(a["user"]["email"])
            riga += ";"
            if isinstance(a["user"]["phoneNumber"], str):
                riga += sanitize(a["user"]["phoneNumber"])
            riga += ";"
            if len(a["user"]["teachers"]) > 0:
                scuo = a["user"]["teachers"][0]["school"]["location"]
                riga += sanitize(scuo["name"]) 
                riga += ";"
                riga += sanitize(scuo["address"])
                riga += ";"
                riga += sanitize(scuo["postalCode"])
                riga += ";"
                riga += sanitize(scuo["city"]["name"])
            else:
                riga += ";;;"
            print(riga)
            #print("")
    print("")
    #for z in CDRD["data"]["zones"]["zones"]:
    #    for a in z["admins"]:
    #     print(a["user"]["name"] + " " + a["user"]["surname"] + " <" + a["user"]["email"] + ">")
        #print(nd)

