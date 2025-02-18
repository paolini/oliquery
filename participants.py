from api import Api
from mycsv import csv_header, csv_row

query = """
query ParticipantResultsTable($contestId: Int, $venueId: Int, $competingVenueId: Int, $schoolId: Int, $after: String, $filter: ParticipantFilter, $order: ParticipantOrder) {
  participants {
    participants(
      contestId: $contestId
      venueId: $venueId
      competingVenueId: $competingVenueId
      schoolId: $schoolId
      after: $after
      filters: $filter
      order: $order
    ) {
      totalCount
      pageInfo {
        hasNextPage
        endCursor
      }
      edges {
        node {
          id
          result {
            qualified
            totalScore
            rankingPosition
            disqualified
            __typename
          }
          competitor {
            id
            competitorKind
            name
            school {
              id
              externalId
              name
              type {
                name
                __typename
              }
              location {
                city {
                  name
                  province {
                    id
                    __typename
                  }
                  __typename
                }
                __typename
              }
              __typename
            }
            members {
              id
              classYear
              name
              surname
              user {
                email
                name
                surname
                __typename
              }
              role {
                role
                __typename
              }
              __typename
            }
            __typename
          }
          __typename
        }
        __typename
      }
      pageInfo {
        hasNextPage
        endCursor
        __typename
      }
      totalCount
      __typename
    }
    __typename
  }
}"""

o = {
    "operationName":"ParticipantResultsTable",
    "variables":{
        "contestId":14,
        "after":None,
        "filter":{},
        "order":{}
        },
    "query": query
}

variables = {
    "contestId":14,
    "after":None,
    "filter":{},
    "order":{}
}

api = Api(variables)
api.login()

fields = ['id', 'competitor.name', 'competitor.school.externalId', 'competitor.school.name', 'competitor.school.location.city.name', 'competitor.school.location.city.province.id', 'member.name', 'member.surname']

if __name__ == "__main__":
  cursor = None
  hasNextPage = True
  print(csv_header(fields))
  while hasNextPage:
    r = api.query(query,{"after": cursor})
    hasNextPage = r["data"]["participants"]["participants"]["pageInfo"]["hasNextPage"]
    cursor = r["data"]["participants"]["participants"]["pageInfo"]["endCursor"]
    edges = r["data"]["participants"]["participants"]["edges"]
    results = [{"id": node["id"], "result": node["result"], "competitor": node["competitor"], "member": node["competitor"]["members"][0]} for node in [edge["node"] for edge in edges]]
    for row in results:
        print(csv_row(row, fields))
