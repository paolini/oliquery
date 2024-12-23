from api import Api, sanitize

query3 = """query {
  zones {
    zones(filters: {olympiad: {editions: {id: {exact: "${EDITION}"}}}}) {
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

queryCDRD = """query {
  zones {
    zones(filters: {olympiad: {editions: {id: {exact: "${EDITION}"}}}}) {
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
  CDRD = api.query(queryCDRD)
  zones = CDRD["data"]["zones"]["zones"]
  print("\t".join(["zona", "CD/RD", "nome", "cognome", "email", "telefono", "scuola", "indirizzo", "CAP", "città"]))
  for z in zones:
    for a in z["admins"]:
      riga = [] 
      riga.append(sanitize(z["name"]))
      riga.append("CD" if a["isPrimary"] else "RD")
      user = a["user"]
      riga.append(sanitize(user["name"]))
      riga.append(sanitize(user["surname"]))
      riga.append(sanitize(user["email"]))
      riga.append(sanitize(user["phoneNumber"]))
      teachers = user["teachers"]
      if teachers:
          scuo = teachers[0]["school"]["location"]
          riga.append(sanitize(scuo["name"])) 
          riga.append(sanitize(scuo["address"]))
          riga.append(sanitize(scuo["postalCode"]))
          riga.append(sanitize(scuo["city"]["name"]))
      else:
          riga.extend(["","","",""])
      print("\t".join(riga))
