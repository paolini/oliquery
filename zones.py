from api import Api
from mycsv import csv_header, csv_row

query = """query Zones($EDITION: String!) {
  zones {
    zones(filters: {olympiad: {editions: {id: {exact: $EDITION}}}}) {
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
          }
        }
      }
      extraSchools {
        name
        externalId
      }
    }
  }
}"""

if __name__ == "__main__":
    api = Api(requireEdition=True)
    api.login()
    r = api.query(query)
    zones = r["data"]["zones"]["zones"]
    fields = ["zone.name", "school.location.name", "school.externalId", "isExtra"]
    fields_extra = ["zone.name", "extra.name", "extra.externalId", "isExtra"]
    print(csv_header(fields)) 
    for zone in zones:
        for subscription in zone["subscriptions"]["edges"]:
            row = {
               "zone": zone,
               "school": subscription["node"]["school"],
               "isExtra": 0,
            }
            print(csv_row(row, fields))
        for extra in zone["extraSchools"]:
            row = {
                "zone": zone,
                "extra": extra,
                "isExtra": 1,
            }
            print(csv_row(row, fields_extra))
