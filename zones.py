from api import Api, sanitize

query = """query {
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
    api = Api()
    api.login()
    r = api.query(query)
    zones = r["data"]["zones"]["zones"]
    print("Zona\tSede\tCodice\textra?")
    for zone in zones:
        for subscription in zone["subscriptions"]["edges"]:
            row = []
            row.append(sanitize(zone["name"]))
            row.append(sanitize(subscription["node"]["school"]["location"]["name"]))
            row.append(sanitize(subscription["node"]["school"]["externalId"]))
            row.append("0")
            print("\t".join(row))
        for extra in zone["extraSchools"]:
            row = []
            row.append(sanitize(zone["name"]))
            row.append(sanitize(extra["name"]))
            row.append(sanitize(extra["externalId"]))
            row.append("1")
            print("\t".join(row))