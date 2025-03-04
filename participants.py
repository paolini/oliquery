import sys, os
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

"""
o = {
    "operationName":"ParticipantResultsTable",
    "variables":{
        "contestId": CONTEST_ID,
        "after":None,
        "filter":{},
        "order":{}
        },
    "query": query
}
"""

if __name__ == "__main__":
  if len(sys.argv) > 1:
    contestId = int(sys.argv[1])
  else:
    contestId = os.environ.get("OLI_CONTEST_ID", 14)

  api = Api()
  api.login()
  
  fields = ['id', 'competitor.name', 'competitor.school.externalId', 'competitor.school.name', 'competitor.school.location.city.name', 'competitor.school.location.city.province.id', 'member.name', 'member.surname']

  cursor = None
  hasNextPage = True
  print(f"Using contestId={contestId}", file=sys.stderr)
  print(csv_header(fields))
  while hasNextPage:
    r = api.query(query,{"contestId": contestId, "after": cursor})
    errors = r.get("errors")
    if errors:
        print(errors, file=sys.stderr)
        exit(1)
    totalCount = r["data"]["participants"]["participants"]["totalCount"]
    if cursor is None:
       print(f"Total count: {totalCount}", file=sys.stderr)
    hasNextPage = r["data"]["participants"]["participants"]["pageInfo"]["hasNextPage"]
    cursor = r["data"]["participants"]["participants"]["pageInfo"]["endCursor"]
    edges = r["data"]["participants"]["participants"]["edges"]
    results = [{"id": node["id"], "result": node["result"], "competitor": node["competitor"], "member": node["competitor"]["members"][0]} for node in [edge["node"] for edge in edges]]
    for row in results:
        print(csv_row(row, fields))
