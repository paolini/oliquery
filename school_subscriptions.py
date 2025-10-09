import sys
import os
from api import Api
from mycsv import csv_header, csv_row

query = """query SubscriptionsWithZones($editionId: String!, $after: String, $filter: SchoolSubscriptionFilter, $order: SchoolSubscriptionOrder) {
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
    
    # First, get the olympiad ID from the edition
    edition_query = """query GetEditionOlympiad($editionId: String!) {
      olympiads {
        edition(id: $editionId) {
          id
          olympiad {
            id
            name
          }
        }
      }
    }"""
    
    edition_response = api.query(edition_query, {"editionId": edition_id})
    
    errors = edition_response.get("errors")
    if errors:
        print(f"Error getting edition info: {errors}", file=sys.stderr)
        exit(1)
    
    edition_data = edition_response['data']['olympiads']['edition']
    if not edition_data:
        print(f"Edition {edition_id} not found", file=sys.stderr)
        exit(1)
    
    olympiad_id = edition_data['olympiad']['id']
    olympiad_name = edition_data['olympiad']['name']
    
    # Get all zones for this olympiad to create a mapping
    zones_query = """query GetZones($olympiadId: String!) {
      zones {
        zones(filters: { olympiad: { id: { exact: $olympiadId } } }) {
          id
          name
          provinces {
            id
          }
          admins {
            isPrimary
            user {
              name
              surname
              email
              phoneNumber
            }
          }
        }
      }
    }"""
    
    zones_response = api.query(zones_query, {"olympiadId": olympiad_id})
    
    errors = zones_response.get("errors")
    if errors:
        print(f"Error getting zones info: {errors}", file=sys.stderr)
        exit(1)
    
    # Create a mapping from province_id to zone info
    province_to_zone = {}
    zones_data = zones_response['data']['zones']['zones']
    
    for zone in zones_data:
        zone_id = zone['id']
        zone_name = zone['name']
        zone_admins = zone['admins']
        
        # Find primary admin
        primary_admin = None
        for admin in zone_admins:
            if admin['isPrimary']:
                primary_admin = admin
                break
        
        # If no primary admin, take the first one
        if not primary_admin and zone_admins:
            primary_admin = zone_admins[0]
        
        zone_info = {
            'id': zone_id,
            'name': zone_name,
            'admin_name': primary_admin['user']['name'] + ' ' + primary_admin['user']['surname'] if primary_admin else None,
            'admin_email': primary_admin['user']['email'] if primary_admin else None,
            'admin_phone': primary_admin['user']['phoneNumber'] if primary_admin else None
        }
        
        # Map each province to this zone
        for province in zone['provinces']:
            province_to_zone[province['id']] = zone_info

    fields = [
        "zone_id", "zone_name", 
        "zone_admin_primary_name", "zone_admin_primary_email", "zone_admin_primary_phone",
        "school_id", "school_external_id", "school_name", "school_type", "school_email", 
        "school_is_active", "school_game_only", "address", "postal_code", 
        "city_id", "city_name", "province_id", "province_name", "region_name",
        "contact_name", "contact_surname", "contact_email", "contact_phone",
        "is_valid", "status", "donation"
    ]
    
    print(f"Using editionId={edition_id}, olympiadId={olympiad_id} ({olympiad_name})", file=sys.stderr)
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
            
            # Get zone info from the mapping
            zone_info = province_to_zone.get(province['id'])
            zone_id = zone_info['id'] if zone_info else None
            zone_name = zone_info['name'] if zone_info else None
            zone_admin_name = zone_info['admin_name'] if zone_info else None
            zone_admin_email = zone_info['admin_email'] if zone_info else None
            zone_admin_phone = zone_info['admin_phone'] if zone_info else None
            
            # Create a flat row object for csv_row function with all available data
            row_data = {
                'zone_id': zone_id,
                'zone_name': zone_name,
                'zone_admin_primary_name': zone_admin_name,
                'zone_admin_primary_email': zone_admin_email,
                'zone_admin_primary_phone': zone_admin_phone,
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