from api import Api
from mycsv import  csv_header, csv_row

api = Api(requireEdition=True)
api.login()

query = """query Zones($EDITION: String!) {
  zones {
    zones(
      filters: {olympiad: {editions: {id: {exact: $EDITION}}}, 
      provinces: {name: {}}}
    ) {
      id
      name
      provinces {
        id
        name
      }
    }
  }
}"""

fields = [
    "id",
    "name",
    "provinces.id",
    "provinces.name",
]

if __name__ == "__main__":
    r = api.query(query)
    zones = r["data"]["zones"]["zones"]
    fields = ["zone.id", "zone.name", "province.name", "province.id"]
    print(csv_header(fields))
    for zone in zones:
        for province in zone["provinces"]:
            row = {
                "zone": zone,
                "province": province,
            }
            print(csv_row(row, fields))
