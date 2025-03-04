import sys
from api import Api
from mycsv import csv_header, csv_row

query = """
query MyQuery($EDITION: String) {
  contests {
    contests(filters: {edition: {id: {exact: $EDITION}}}) {
      id
      name
      edition {
        id
      }
      studentRegistrationStart
      studentRegistrationStop
    }
  }
}
"""

api = Api()
api.login()

fields = ['id', 'name', 'edition.id', 'studentRegistrationStart', 'studentRegistrationStop']

if __name__ == "__main__":
    print(csv_header(fields))
    r = api.query(query)
    errors = r.get("errors")
    if errors:
        raise Exception(errors)
    contests = r["data"]["contests"]["contests"]
    for contest in contests:
        print(csv_row(contest, fields))
