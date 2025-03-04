import requests
import json
import os
import sys
import dotenv

dotenv.load_dotenv()

class Api:
  def __init__(self, requireEdition=False):
    self.session = None
    self.endpoint = "https://olimpiadi-scientifiche.it/graphql/"
    self.headers = {}

    self.EMAIL = os.environ.get("OLI_EMAIL")
    self.PASSWORD = os.environ.get("OLI_PASSWORD")
    if requireEdition:
      self.requireEdition()
    else:
      self.EDITION = None
  
  def requireEdition(self):
    try:
      self.EDITION = os.environ["OLI_EDITION"]
      print("using EDITION", self.EDITION, file=sys.stderr)
    except KeyError:
      raise Exception("OLI_EDITION required in environment variables")

  def query(self, query, vars={}):
    if self.EDITION:
      vars = {**vars, "EDITION": self.EDITION}
    if not self.session:
      print("Creating session", file=sys.stderr)
      self.session = requests.Session()
      r = self.session.post(self.endpoint)
      csrf_token = r.cookies.get_dict().get('csrftoken')
      self.headers.update({"X-CsrfToken": csrf_token})
    r = self.session.post(self.endpoint, json={"query": query, "variables": vars}, headers=self.headers)
    csrf_token = r.cookies.get_dict().get('csrftoken')
    if csrf_token:
      self.headers.update({"X-CsrfToken": csrf_token})
    if r.status_code != 200:
        print(json.dumps(r.json(), indent=2), file=sys.stderr)
        raise Exception("Query failed to run with a {r.status_code}.", r.status_code)
    return r.json()

  def login(self):
    print("Logging in", file=sys.stderr)
    if not self.EMAIL:
      raise Exception("Email non specificata!\nPer risolvere:\nexport OLI_EMAIL=my-email")
    if not self.PASSWORD:
      raise Exception("Password non specificata!\nPer risolvere:\nexport OLI_PASSWORD=my-secret-password")
    r = self.query("""mutation ($EMAIL: String!, $PASSWORD: String!) {
      users{
        login(email: $EMAIL, password: $PASSWORD){
          __typename
          ...on OperationInfo{
            messages{
              message
              kind
            }
          }
          ...on LoginSuccess{
            user{
              email
            }
          }
        }
      }
    }""", {"EMAIL": self.EMAIL,"PASSWORD": self.PASSWORD})
    login = r["data"]["users"]["login"]
    typename = login["__typename"]
    if typename == "OperationInfo":
        raise Exception("OperationInfo: " + ", ".join([x["message"] for x in login["messages"]]))
    return r
  
  def me(self): 
    return self.query(""" query {
        users {
          me {
            email
          }
        }
      }""")


if __name__ == "__main__":
  print("Running connection test")
  api = Api()

  print("Health check (no password needed)")
  query = """query MyQuery {
    healthCheck
  }"""
  print(api.query(query))

  print("Trying to login")
  api.login()

  print(api.me())

  api.requireEdition()

  try:
    EDITION = os.environ["OLI_EDITION"]
  except:
    raise Exception("OLI_EDITION not set")

  query = """query MyQuery($EDITION: String!) {
    olympiads{
      edition(id:$EDITION){
        id
        numSubscriptions{
          total
        }
      }
    }
  }"""
  print(api.query(query, {"EDITION": EDITION}))