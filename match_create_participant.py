#!/usr/bin/env python3
"""
Script per eseguire la mutation matchOrCreateParticipant.

Questa mutation permette di trovare o creare un partecipante (participant) 
per un contest di tipo scolastico, cercando di abbinare automaticamente 
i dati forniti a un competitor esistente.

Usage:
    python match_or_create_participant.py --contest-id 123 --school-code RMPC01000A \
        --name Mario --surname Rossi --class-year 10 --section A \
        --birth-date 2008-05-15

    # Senza data di nascita
    python match_or_create_participant.py --contest-id 123 --school-code RMPC01000A \
        --name Mario --surname Rossi --class-year 10 --section A
    
    # Output CSV
    python match_or_create_participant.py --contest-id 123 --school-code RMPC01000A \
        --name Mario --surname Rossi --class-year 10 --section A --format csv
"""

import argparse
import sys
from api import Api


def match_or_create_participant(
    contest_id: int,
    school_external_id: str,
    name: str,
    surname: str,
    class_year: int,
    section: str,
    birth_date: str = None
):
    """
    Esegue la mutation matchOrCreateParticipant.
    
    Args:
        contest_id: ID del contest
        school_external_id: Codice ministeriale della scuola
        name: Nome del partecipante
        surname: Cognome del partecipante
        class_year: Anno di corso (1-13)
        section: Sezione (es: "A", "B")
        birth_date: Data di nascita (opzionale, formato: YYYY-MM-DD)
    
    Returns:
        dict: Risposta della mutation
    """
    api = Api()
    
    # Login
    print("Login in corso...", file=sys.stderr)
    api.login()
    
    # Costruisci la mutation
    mutation = """
    mutation MatchOrCreateParticipant(
        $contestId: Int!
        $schoolExternalId: String!
        $name: String!
        $surname: String!
        $classYear: Int!
        $section: String!
        $birthDate: Date
    ) {
        participants {
            matchOrCreateParticipant(
                contestId: $contestId
                schoolExternalId: $schoolExternalId
                name: $name
                surname: $surname
                classYear: $classYear
                section: $section
                birthDate: $birthDate
            ) {
                __typename
                ... on ParticipantMatchSuccess {
                    participant {
                        id
                        online
                        competitor {
                            id
                            name
                            competitorKind
                            isEligible
                            isApproved
                            school {
                                name
                                externalId
                            }
                        }
                    }
                    competitorCreated
                    participantCreated
                    multipleCompetitorsMatched
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
    
    # Prepara le variabili
    variables = {
        "contestId": contest_id,
        "schoolExternalId": school_external_id,
        "name": name,
        "surname": surname,
        "classYear": class_year,
        "section": section,
    }
    
    # Aggiungi birth_date solo se fornita
    if birth_date:
        variables["birthDate"] = birth_date
    
    # Esegui la mutation
    print(f"Esecuzione mutation per {name} {surname}...", file=sys.stderr)
    result = api.query(mutation, variables)
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Trova o crea un partecipante per un contest scolastico"
    )
    
    parser.add_argument(
        "--contest-id",
        type=int,
        required=True,
        help="ID del contest"
    )
    
    parser.add_argument(
        "--school-code",
        "--school-external-id",
        dest="school_external_id",
        required=True,
        help="Codice ministeriale della scuola (es: RMPC01000A)"
    )
    
    parser.add_argument(
        "--name",
        required=True,
        help="Nome del partecipante"
    )
    
    parser.add_argument(
        "--surname",
        required=True,
        help="Cognome del partecipante"
    )
    
    parser.add_argument(
        "--class-year",
        type=int,
        required=True,
        help="Anno di corso (1-13: 1-5 elementari, 6-8 medie, 9-13 superiori)"
    )
    
    parser.add_argument(
        "--section",
        required=True,
        help="Sezione (es: A, B, C)"
    )
    
    parser.add_argument(
        "--birth-date",
        help="Data di nascita (formato: YYYY-MM-DD, opzionale)"
    )
    
    parser.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Formato di output: json (default) o csv"
    )
    
    args = parser.parse_args()
    
    # Validazione anno di corso
    if args.class_year < 1 or args.class_year > 13:
        print("Errore: class_year deve essere tra 1 e 13", file=sys.stderr)
        sys.exit(1)
    
    try:
        result = match_or_create_participant(
            contest_id=args.contest_id,
            school_external_id=args.school_external_id,
            name=args.name,
            surname=args.surname,
            class_year=args.class_year,
            section=args.section,
            birth_date=args.birth_date
        )
        
        # Verifica che result non sia None
        if result is None:
            print("\n❌ Errore: Nessuna risposta dal server", file=sys.stderr)
            sys.exit(1)
        
        # Analizza il risultato
        data = result.get("data", {}).get("participants", {}).get("matchOrCreateParticipant", {})
        typename = data.get("__typename")
        
        if typename == "ParticipantMatchSuccess":
            participant = data.get("participant", {})
            competitor = participant.get("competitor", {})
            
            print("\n✅ Operazione completata con successo!", file=sys.stderr)
            print(f"\nPartecipante ID: {participant.get('id')}", file=sys.stderr)
            print(f"Competitor ID: {competitor.get('id')}", file=sys.stderr)
            print(f"Nome competitor: {competitor.get('name')}", file=sys.stderr)
            print(f"Scuola: {competitor.get('school', {}).get('name')}", file=sys.stderr)
            print(f"\nCompetitor creato: {'Sì' if data.get('competitorCreated') else 'No'}", file=sys.stderr)
            print(f"Participant creato: {'Sì' if data.get('participantCreated') else 'No'}", file=sys.stderr)
            
            if data.get('multipleCompetitorsMatched'):
                print("\n⚠️  ATTENZIONE: Più competitor corrispondono ai criteri!", file=sys.stderr)
            
            # Output secondo il formato richiesto
            if args.format == "csv":
                import csv
                import io
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow([
                    "participant_id",
                    "competitor_id",
                    "competitor_name",
                    "school_code",
                    "school_name",
                    "competitor_created",
                    "participant_created",
                    "multiple_competitors_matched"
                ])
                writer.writerow([
                    participant.get('id'),
                    competitor.get('id'),
                    competitor.get('name'),
                    competitor.get('school', {}).get('externalId'),
                    competitor.get('school', {}).get('name'),
                    '1' if data.get('competitorCreated') else '0',
                    '1' if data.get('participantCreated') else '0',
                    '1' if data.get('multipleCompetitorsMatched') else '0'
                ])
                print(output.getvalue().rstrip())
            else:
                # Output JSON completo per elaborazione programmatica
                import json
                print(json.dumps(result, indent=2))
            
        elif typename == "OperationInfo":
            messages = data.get("messages", [])
            print("\n❌ Operazione fallita:", file=sys.stderr)
            for msg in messages:
                kind = msg.get("kind", "ERROR")
                message = msg.get("message", "")
                print(f"  [{kind}] {message}", file=sys.stderr)
            
            import json
            print(json.dumps(result, indent=2))
            sys.exit(1)
        else:
            print(f"\n⚠️  Risposta inattesa: {typename}", file=sys.stderr)
            import json
            print(json.dumps(result, indent=2))
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Errore: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
