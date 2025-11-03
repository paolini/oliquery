import sys
from api import Api
from mycsv import csv_header, csv_row

query = """query Venues($CONTEST_ID: Int!) {
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
      subscriptions {
        edges {
          node {
            school {
              externalId
            }
          }
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
    try:
        r = api.query(query, {"CONTEST_ID": CONTEST_ID})
    except Exception as e:
        # Prova a loggare la risposta grezza se disponibile
        import traceback
        with open('log.json', 'w') as f:
            f.write("Exception: " + str(e) + "\n")
            traceback.print_exc(file=f)
        print("Errore durante la query. Vedi log.json per dettagli.", file=sys.stderr)
        sys.exit(1)
    if "errors" in r:
        raise Exception(r["errors"])
    print(r, file=open('log.json', 'w'))
    venues = r["data"]["venues"]["venues"]
    fields = ["venue.id", "venue.name", "school.externalId", "admin.email", "admin.name", "admin.surname"]
    print(csv_header(fields))
    for venue in venues:
        for subscription in venue["subscriptions"]["edges"]:
            for admin in venue["admins"]:
              row = {
                  "venue": {
                      "id": venue["id"],
                      "name": venue["name"]
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
