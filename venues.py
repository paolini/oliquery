import sys
from api import Api
from mycsv import csv_header, csv_row

query = """query Venues($CONTEST_ID: Int!, $after: String) {
  venues {
    venues(filters: {contest: {id: $CONTEST_ID}}) {
      id
      name
      admins {
        name
        surname
        user {
          email
        }
      }
      subscriptions(after: $after) {
        edges {
          node {
            school {
              externalId
            }
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
  }
}"""

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} CONTEST_ID")
        sys.exit(1)
    CONTEST_ID = int(sys.argv[1])
    api = Api()
    api.login()
    
    # Prima query per ottenere la lista dei venues
    try:
        r = api.query(query, {"CONTEST_ID": CONTEST_ID, "after": None})
    except Exception as e:
        import traceback
        with open('log.json', 'w') as f:
            f.write("Exception: " + str(e) + "\n")
            traceback.print_exc(file=f)
        print("Errore durante la query. Vedi log.json per dettagli.", file=sys.stderr)
        sys.exit(1)
    if "errors" in r:
        raise Exception(r["errors"])
    
    venues = r["data"]["venues"]["venues"]
    fields = ["venue.id", "venue.name", "school.externalId", "admin.email", "admin.name", "admin.surname"]
    print(csv_header(fields))
    
    # Per ogni venue, gestisci la paginazione delle subscriptions
    for venue in venues:
        print(f"Processing venue {venue['id']}: {venue['name']}", file=sys.stderr )
        venue_id = venue["id"]
        venue_name = venue["name"]
        admins = venue["admins"]
        
        # Raccogli tutte le subscriptions per questo venue
        all_subscriptions = []
        subscriptions_data = venue["subscriptions"]
        all_subscriptions.extend(subscriptions_data["edges"])
        
        # Se ci sono più pagine, continua a richiedere
        while subscriptions_data["pageInfo"]["hasNextPage"]:
            cursor = subscriptions_data["pageInfo"]["endCursor"]
            print(f"Fetching more subscriptions for venue {venue_id} (cursor: {cursor})", file=sys.stderr)
            
            # Query per ottenere la prossima pagina di questo specifico venue
            # Nota: potrebbe essere necessario una query diversa se l'API non supporta
            # la paginazione per singolo venue. In tal caso, dobbiamo richiedere tutti i venues
            # ogni volta con il cursore.
            r = api.query(query, {"CONTEST_ID": CONTEST_ID, "after": cursor})
            if "errors" in r:
                raise Exception(r["errors"])
            
            # Trova il venue corrispondente nella risposta
            venues_page = r["data"]["venues"]["venues"]
            current_venue = next((v for v in venues_page if v["id"] == venue_id), None)
            if not current_venue:
                break
            
            subscriptions_data = current_venue["subscriptions"]
            all_subscriptions.extend(subscriptions_data["edges"])
        
        # Stampa tutte le righe per questo venue
        for subscription in all_subscriptions:
            for admin in admins:
                row = {
                    "venue": {
                        "id": venue_id,
                        "name": venue_name
                    },
                    "school": {
                        "externalId": subscription["node"]["school"]["externalId"]
                    },
                    "admin": {
                        "email": admin["user"]["email"],
                        "name": admin["name"],
                        "surname": admin["surname"]
                    }
                }
                print(csv_row(row, fields))
