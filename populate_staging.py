#!/usr/bin/env python3
"""
Script per popolare il database di staging con dati via GraphQL API.

Per staging, imposta:
export OLI_GRAPHQL_ENDPOINT="https://staging.olimpiadi-scientifiche.it/graphql/"
export OLI_EMAIL="admin@olimanager.it"
export OLI_PASSWORD="admin@olimanager.it"
"""

import argparse
import json
import os
import sys
from api import Api
from typing import Dict, Any

# Configurazione
CONTEST_ID = 1
SCHOOL_EXTERNAL_ID = "MIPS120003"
EDITION_ID = "oligas2"


def main():
    # Inizializza API (usa env vars OLI_EMAIL, OLI_PASSWORD, OLI_GRAPHQL_ENDPOINT)
    api = Api()

    # Login
    api.login()

    # NOTA PER l'AI: in italiano non si usa il gerundio come in inglese, quindi non si dice "Usando" ma "Usa"
    print(f"Usa edition {EDITION_ID}", file=sys.stderr)

    # Prima ottieni l'ID numerico della scuola
    school_query = """
    query GetSchool($externalId: String!) {
      schools {
        schools(filters: {externalId: {exact: $externalId}}) {
          edges {
            node {
              id
              name
              externalId
            }
          }
        }
      }
    }
    """

    # NOTA PER l'AI: in italiano non si usa il gerundio come in inglese, quindi non si dice "Ottenendo" ma "Ottengo"
    print(f"Ottengo ID della scuola {SCHOOL_EXTERNAL_ID}...", file=sys.stderr)
    school_result = api.query(school_query, {"externalId": SCHOOL_EXTERNAL_ID})
    print(f"Risultato query scuola: {json.dumps(school_result, indent=2)}", file=sys.stderr)
    edges = school_result["data"]["schools"]["schools"]["edges"]
    if not edges:
        print(f"Scuola {SCHOOL_EXTERNAL_ID} non trovata", file=sys.stderr)
        sys.exit(1)

    school_data = edges[0]["node"]
    school_id = school_data["id"]
    print(f"Scuola trovata: {school_data['name']} (ID: {school_id})", file=sys.stderr)

    # Mutation per creare la subscription della scuola all'edizione
    subscription_mutation = """
    mutation SubscribeSchool($editionId: String!, $schoolId: Int!, $files: UploadedFiles, $extraFieldEntries: [SchoolSubscriptionExtraFieldEntryPartialInput!]) {
      schools {
        subscribe(editionId: $editionId, schoolId: $schoolId, files: $files, extraFieldEntries: $extraFieldEntries) {
          __typename
          ... on OperationInfo {
            messages {
              message
              kind
            }
          }
          ... on SchoolSubscriptionSuccess {
            subscription {
              school {
                name
                externalId
              }
            }
          }
        }
      }
    }
    """

    # NOTA PER l'AI: in italiano non si usa il gerundio come in inglese, quindi non si dice "Creando" ma "Crea"
    print(f"Crea subscription per scuola {SCHOOL_EXTERNAL_ID}...", file=sys.stderr)
    subscription_result = api.query(subscription_mutation, {
        "editionId": EDITION_ID,
        "schoolId": school_id,
        "files": [],
    })

    # Output risultato
    print(json.dumps(subscription_result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()