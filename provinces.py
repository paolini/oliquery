from api import Api, csv_header, csv_row, sanitize

api = Api()
api.login()

query = """{
  zones {
    zones(
      filters: {olympiad: {editions: {id: {exact: "${EDITION}"}}}, 
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
    print(csv_header(fields))
    r = api.query(query)
    zones = r["data"]["zones"]["zones"]
    for zone in zones:
        for province in zone["provinces"]:
            row = []
            row.append(sanitize(zone["id"]))
            row.append(sanitize(zone["name"]))
            row.append(sanitize(province["name"]))
            row.append(sanitize(province["id"]))
            print("\t".join(row))
