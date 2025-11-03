#!/usr/bin/env python3
"""
Script per creare una venue per un contest.

Usage:
    python create_venue.py --contest-id 1 --name "Sede Test"
"""

import argparse
import sys
import json
from api import Api


def create_venue(contest_id: int, name: str):
    """
    Crea una venue per un contest.
    
    Args:
        contest_id: ID del contest
        name: Nome della venue
    
    Returns:
        dict: Risposta della mutation
    """
    api = Api()
    
    # Login
    print("Login in corso...", file=sys.stderr)
    api.login()
    
    # Mutation per creare una venue
    mutation = """
    mutation CreateVenue($contestId: Int!, $name: String!) {
        venues {
            createVenue(contestId: $contestId, name: $name) {
                __typename
                ... on VenueType {
                    id
                    name
                    contest {
                        id
                        name
                    }
                }
                ... on OperationInfo {
                    messages {
                        message
                        kind
                    }
                }
            }
        }
    }
    """
    
    variables = {
        "contestId": contest_id,
        "name": name,
    }
    
    print(f"Creazione venue '{name}' per contest {contest_id}...", file=sys.stderr)
    result = api.query(mutation, variables)
    
    # Debug: stampa la risposta completa
    print("Risposta:", json.dumps(result, indent=2), file=sys.stderr)
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Crea una venue per un contest"
    )
    
    parser.add_argument(
        "--contest-id",
        type=int,
        required=True,
        help="ID del contest"
    )
    
    parser.add_argument(
        "--name",
        required=True,
        help="Nome della venue"
    )
    
    args = parser.parse_args()
    
    try:
        result = create_venue(
            contest_id=args.contest_id,
            name=args.name
        )
        
        # Analizza il risultato
        data = result.get("data", {}).get("venues", {}).get("createVenue", {})
        typename = data.get("__typename")
        
        if typename == "VenueType":
            print("\n✅ Venue creata con successo!", file=sys.stderr)
            print(f"Venue ID: {data.get('id')}", file=sys.stderr)
            print(f"Nome: {data.get('name')}", file=sys.stderr)
            print(f"Contest: {data.get('contest', {}).get('name')}", file=sys.stderr)
            
            # Output JSON completo
            print(json.dumps(result, indent=2))
            
        elif typename == "OperationInfo":
            messages = data.get("messages", [])
            print("\n❌ Operazione fallita:", file=sys.stderr)
            for msg in messages:
                kind = msg.get("kind", "ERROR")
                message = msg.get("message", "")
                print(f"  [{kind}] {message}", file=sys.stderr)
            
            print(json.dumps(result, indent=2))
            sys.exit(1)
        else:
            print(f"\n⚠️  Risposta inattesa: {typename}", file=sys.stderr)
            print(json.dumps(result, indent=2))
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Errore: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
