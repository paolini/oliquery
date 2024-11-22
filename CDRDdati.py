import json
import os

from api import Api

def sanitize(a):
    if isinstance(a, str):
        return (a.replace(";",""))
    elif isinstance(a, int):
        return(a)
    else:
        return ("")

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

api = Api()
api.login()

if True:
#r = s.post(endpoint, json={"query": queryCDdati}, headers=headers)
#if r.status_code == 200:
#    print(datetime.datetime.now())
    CDRD = api.query(queryCDdati)
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

