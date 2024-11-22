import requests
import json
import os
import sys

def sanitize(s):
    if not hasattr(s, "replace"):
        s = str(s)
    return s.replace("\n", " ").replace("\r", " ").replace("\t", " ")

class Api:
  def __init__(self, vars={}):
    self.session = None
    self.endpoint = "https://olimpiadi-scientifiche.it/graphql/"
    self.headers = {}

    self.EMAIL = os.environ.get("OLI_EMAIL")
    self.PASSWORD = os.environ.get("OLI_PASSWORD")
    self.vars = vars
    if not self.vars.get("EDITION"):
      self.vars["EDITION"] = os.environ.get("OLI_EDITION", "olimat25")

  def query(self, query):
    for key in self.vars:
      query = query.replace("${" + key + "}", self.vars[key])
#    print("Making query", query)
    if not self.session:
      print("Creating session", file=sys.stderr)
      self.session = requests.Session()
      r = self.session.post(self.endpoint)
      csrf_token = r.cookies.get_dict().get('csrftoken')
      self.headers.update({"X-CsrfToken": csrf_token})
    r = self.session.post(self.endpoint, json={"query": query}, headers=self.headers)
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
    r = self.query("""mutation {
      users{
        login(email: "$EMAIL", password: "$PASSWORD"){
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
    }""".replace("$EMAIL", self.EMAIL).replace("$PASSWORD", self.PASSWORD))
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
  print("Running test")
  api = Api()

  api.login()

  print(api.me())

  query = """query {
    olympiads{
      edition(id:"olimat24"){
        numSubscriptions{
          total
        }
      }
    }
  }"""

  print(api.query(query))