#!/usr/bin/env python3
"""
Script per fare introspection dello schema GraphQL e vedere le mutations disponibili.
"""

import json
import os
import sys
from api import Api


def main():
    # Inizializza API
    api = Api()

    # Login
    api.login()

    # Query di introspection completa
    query = """
    query IntrospectionQuery {
      __schema {
        types {
          kind
          name
          fields(includeDeprecated: true) {
            name
            args {
              name
              type {
                name
                kind
                ofType {
                  name
                  kind
                }
              }
            }
            type {
              name
              kind
            }
          }
        }
      }
    }
    """

    print("Facendo introspection completa...", file=sys.stderr)
    result = api.query(query)

    if "errors" in result:
        print("Errori:", json.dumps(result["errors"], indent=2), file=sys.stderr)
        sys.exit(1)

    types = result["data"]["__schema"]["types"]

    # Trova SchoolsMutation
    schools_mutation = next((t for t in types if t["name"] == "SchoolsMutation"), None)

    if not schools_mutation:
        print("SchoolsMutation non trovato", file=sys.stderr)
        # Mostra tutti i tipi OBJECT che potrebbero essere mutations
        mutation_types = [t["name"] for t in types if t["kind"] == "OBJECT" and "Mutation" in t["name"]]
        print(f"Tipi Mutation trovati: {mutation_types}", file=sys.stderr)
        sys.exit(1)

    fields = schools_mutation["fields"]
    if not fields:
        print("Nessun field in SchoolsMutation", file=sys.stderr)
        sys.exit(1)

    print(f"Mutations in SchoolsMutation ({len(fields)}):")
    for f in fields:
        print(f"- {f['name']}")
        if f["args"]:
            args_str = ", ".join(f"{arg['name']}: {arg['type']['name'] or arg['type'].get('ofType', {}).get('name', 'Unknown')}" for arg in f["args"])
            print(f"  Args: {args_str}")
        print(f"  Returns: {f['type']['name']}")
        print()


if __name__ == "__main__":
    main()