from api import Api, csv_header, csv_row

api = Api()
api.login()

query = """
query Schools($after: String) {
    schools {
        schools(after: $after) {
            totalCount
            pageInfo {
                hasNextPage
                endCursor
            }
            edges {
                node {
                    email
                    externalId
                    gameOnly
                    globalId
                    id
                    isActive
                    location {
                        address
                        city {
                            name
                            province {
                                name
                            }
                        }
                        postalCode
                        name
                    }
                    name
                    numUnverified
                    parentExternalId
                    website
                    type {
                        name
                    }
                }
            }
        }
    }
}"""

fields = [
    "id",
    "name",
    "isActive",
    "email",
    "type.name",
    "externalId",
    "gameOnly",
    "globalId",
    "numUnverified",
    "parentExternalId",
    "website",
    "location.city.name",
    "location.city.province.name",
    "location.postalCode",
    "location.address",
    "location.name",
    ]

print(csv_header(fields))
cursor = ""
while True:
    r = api.query(query, {"after": cursor})
    if r.get("errors"):
        raise Exception(r["errors"])
    schools = r["data"]["schools"]["schools"]
    edges = schools["edges"]
    for edge in edges:
        node = edge["node"]
        print(csv_row(node, fields))
    cursor = schools["pageInfo"]["endCursor"]
    hasNextPage = schools["pageInfo"]["hasNextPage"]
    if not hasNextPage:
        break

"""
    @cached_property
    def schools(self) -> List[int]:
        schools_in_province = list(
            # Fetch the schools that are in the provinces of this zone...
            School.objects.filter(location__city__province__zones__id=self.id)
            # ...excluding the schools that have been moved...
            .filter(~Q(zones_exceptions__olympiad__id=self.olympiad.id))
            # ...keeping only the ids.
            .values_list("id", flat=True)
        )
        extra_schools = list(self.extra_schools.values_list("id", flat=True))
        return schools_in_province + extra_schools
"""