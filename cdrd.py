from api import Api
from mycsv import csv_header, csv_row

query3 = """query CdRd($EDITION: String!) {
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

queryCDRD = """query CdRd($EDITION: String!) {
  zones {
    zones(filters: {olympiad: {editions: {id: {exact: $EDITION}}}}) {
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

api = Api(requireEdition=True)
api.login()

if __name__ == "__main__":
  data = api.query(queryCDRD)
  if "errors" in data:
     raise Exception(data["errors"])
  zones = data["data"]["zones"]["zones"]
  fields = ["zone", "isPrimary", "user.name", "user.surname", "user.email", "user.phoneNumber", "school.name", "school.address", "school.postalCode", "school.city.name"]
  print(csv_header(fields))
  for zone in zones:
    for row in zone["admins"]:
      row["zone"] = zone["name"]
      teachers = row["user"]["teachers"]
      if len(teachers) == 1:
          row["school"] = teachers[0]["school"]["location"]
      elif len(teachers) > 1:
          row["school"] = {
             "name": "<multiple schools>",
          }
      print(csv_row(row, fields))
