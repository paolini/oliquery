import sys
import os
from api import Api
from mycsv import csv_header, csv_row

query = """query SubscriptionsTable($editionId: String!, $after: String, $filter: SchoolSubscriptionFilter, $order: SchoolSubscriptionOrder) {
  olympiads {
    edition(id: $editionId) {
      subscriptions(after: $after, filters: $filter, order: $order) {
        ...SubscriptionTableFragment
        edges {
          node {
            status
            donation
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
}

fragment SubscriptionTableFragment on SchoolSubscriptionTypeConnection {
  pageInfo {
    hasNextPage
    endCursor
    __typename
  }
  totalCount
  edges {
    node {
      isValid
      school {
        ...SchoolFragment
        location {
          city {
            province {
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

fragment SchoolFragment on SchoolType {
  id
  externalId
  name
  type {
    name
    isLower
    isMiddle
    isHigher
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
}"""

if __name__ == "__main__":
    if len(sys.argv) > 1:
        edition_id = sys.argv[1]
    else:
        edition_id = os.environ.get("OLI_EDITION", "olimat25")
    
    api = Api()
    api.login()
    
    filter = None  # Filter criteria, if needed
    order = None  # Order criteria, if needed

    fields = [
        "school_id", "school_external_id", "school_name", "school_type", "school_email", 
        "school_is_active", "school_game_only", "address", "postal_code", 
        "city_id", "city_name", "province_id", "province_name", "region_name",
        "contact_name", "contact_surname", "contact_email", "contact_phone",
        "is_valid", "status", "donation"
    ]
    
    cursor = None
    hasNextPage = True
    print(f"Using editionId={edition_id}", file=sys.stderr)
    print(csv_header(fields))
    
    while hasNextPage:
        response = api.query(query, {
            "editionId": edition_id,
            "after": cursor,
            "filter": filter,
            "order": order
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
            user = contact['user']
            
            # Create a flat row object for csv_row function with all available data
            row_data = {
                'school_id': school['id'],
                'school_external_id': school['externalId'],
                'school_name': school['name'],
                'school_type': school_type['name'],
                'school_email': school['email'],
                'school_is_active': school['isActive'],
                'school_game_only': school['gameOnly'],
                'address': location['address'],
                'postal_code': location['postalCode'],
                'city_id': city['id'],
                'city_name': city['name'],
                'province_id': province['id'],
                'province_name': province['name'],
                'region_name': region['name'],
                'contact_name': user['name'],
                'contact_surname': user['surname'],
                'contact_email': user['email'],
                'contact_phone': user['phoneNumber'],
                'is_valid': node['isValid'],
                'status': node['status'],
                'donation': node['donation']
            }
            print(csv_row(row_data, fields))