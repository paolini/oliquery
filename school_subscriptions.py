import sys
import os
from api import Api
from mycsv import csv_header, csv_row

query = """query Subscriptions($editionId: String!, $after: String, $filter: SchoolSubscriptionFilter, $order: SchoolSubscriptionOrder) {
  olympiads {
    edition(id: $editionId) {
      olympiad {
        id
        name
        __typename
      }
      subscriptions(after: $after, filters: $filter, order: $order) {
        pageInfo {
          hasNextPage
          endCursor
          __typename
        }
        totalCount
        edges {
          node {
            isValid
            status
            donation
            school {
              id
              externalId
              name
              type {
                name
                __typename
              }
              email
              isActive
              gameOnly
              location {
                address
                postalCode
                city {
                  id
                  name
                  province {
                    id
                    name
                    region {
                      name
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
            contact {
              user {
                name
                surname
                email
                phoneNumber
                __typename
              }
              name
              surname
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
    __typename
  }
}"""

if __name__ == "__main__":
    if len(sys.argv) > 1:
        edition_id = sys.argv[1]
    else:
        edition_id = os.environ.get("OLI_EDITION", "olimat25")
    
    api = Api()
    api.login()
    
    fields = [
        "school_id", "school_external_id", "school_name", "school_type", "school_email", 
        "school_is_active", "school_game_only", "address", "postal_code", 
        "city_id", "city_name", "province_id", "province_name", "region_name",
        "contact_name", "contact_surname", "contact_email", "contact_phone",
        "is_valid", "status", "donation"
    ]
    
    print(f"Using editionId={edition_id}", file=sys.stderr)
    print(csv_header(fields))
    
    cursor = None
    hasNextPage = True
    total_schools = 0
    
    while hasNextPage:
        response = api.query(query, {
            "editionId": edition_id,
            "after": cursor,
            "filter": None,
            "order": None
        })
        
        errors = response.get("errors")
        if errors:
            print(errors, file=sys.stderr)
            exit(1)
            
        subscriptions = response['data']['olympiads']['edition']['subscriptions']
        totalCount = subscriptions["totalCount"]
        
        if cursor is None:
            print(f"Total count: {totalCount}", file=sys.stderr)
            
        hasNextPage = subscriptions["pageInfo"]["hasNextPage"]
        cursor = subscriptions["pageInfo"]["endCursor"]
        
        for edge in subscriptions['edges']:
            node = edge['node']
            school = node['school']
            contact = node['contact']
            location = school['location']
            city = location['city']
            province = city['province']
            region = province['region']
            school_type = school['type']
            user = contact['user'] if contact else None

            # Create a flat row object for csv_row function with all available data
            row_data = {
                'school_id': school['id'],
                'school_external_id': school['externalId'],
                'school_name': school['name'],
                'school_type': school_type['name'] if school_type else None,
                'school_email': school['email'],
                'school_is_active': school['isActive'],
                'school_game_only': school['gameOnly'],
                'address': location['address'] if location else None,
                'postal_code': location['postalCode'] if location else None,
                'city_id': city['id'] if city else None,
                'city_name': city['name'] if city else None,
                'province_id': province['id'] if province else None,
                'province_name': province['name'] if province else None,
                'region_name': region['name'] if region else None,
                'contact_name': user['name'] if user else None,
                'contact_surname': user['surname'] if user else None,
                'contact_email': user['email'] if user else None,
                'contact_phone': user['phoneNumber'] if user else None,
                'is_valid': node['isValid'],
                'status': node['status'],
                'donation': node['donation']
            }
            print(csv_row(row_data, fields))
            total_schools += 1
    
    print(f"Total schools found: {total_schools}", file=sys.stderr)