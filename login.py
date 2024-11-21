import requests

# Define the GraphQL endpoint
url = 'https://olimpiadi-scientifiche.it/graphql'

# Define the mutation query
mutation = """
mutation {
  users {
    login(email: "emanuele.paolini@unipi.it", password: "password") {
  }
}
"""

# Set up the headers (add the CSRF token)
headers = {
    'Content-Type': 'application/json',
    'X-CSRFToken': '2v5o7uIiH8R33g7PTSkkgvhPdpYiIDJs'  # CSRF token from the response
}


# Set up the request body
data = {
    'query': mutation
}

# Send the POST request to the GraphQL endpoint
response = requests.post(url, json=data, headers=headers, cookies=response.cookies)

# Check the response JSON
print("Response JSON:")
print(response.json())

# Check for cookies in the response
print("\nCookies Set by the Server:")
for cookie in response.cookies:
    print(f"{cookie.name} = {cookie.value}")

# Optionally: check the headers for 'Set-Cookie' (for direct inspection)
print("\nResponse Headers:")
for header, value in response.headers.items():
    if 'Set-Cookie' in header:
        print(f"{header}: {value}")