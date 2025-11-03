#!/usr/bin/env python3
"""
Script per importare partecipanti in batch da un file CSV o JSONL.

Il file CSV deve avere le seguenti colonne:
- name: Nome del partecipante
- surname: Cognome del partecipante
- class_year: Anno di corso (1-13)
- section: Sezione (es: A, B, C)
- school_code: Codice ministeriale della scuola
- birth_date: Data di nascita (opzionale, formato: YYYY-MM-DD)

Esempio CSV:
```
name,surname,class_year,section,school_code,birth_date
Mario,Rossi,10,A,RMPC01000A,2008-05-15
Luigi,Bianchi,10,B,RMPC01000A,2008-03-22
Giovanni,Verdi,11,A,RMPC01000A,
```

Esempio JSONL:
```
{"name": "Mario", "surname": "Rossi", "class_year": "10", "section": "A", "school_code": "RMPC01000A", "birth_date": "2008-05-15"}
{"name": "Luigi", "surname": "Bianchi", "class_year": "10", "section": "B", "school_code": "RMPC01000A", "birth_date": "2008-03-22"}
{"name": "Giovanni", "surname": "Verdi", "class_year": "11", "section": "A", "school_code": "RMPC01000A"}
```

Usage:
    python match_create_participant_batch.py --contest-id 123 --input participants.csv
    
    # Con file di log dettagliato
    python match_create_participant_batch.py --contest-id 123 --input participants.csv --log results.json
"""

import argparse
import csv
import sys
import json
from typing import List, Dict, Any
from api import Api


def process_participant(
    api: Api,
    contest_id: int,
    row: Dict[str, str],
    row_number: int
) -> Dict[str, Any]:
    """
    Processa un singolo partecipante.
    
    Args:
        api: Istanza Api già autenticata
        contest_id: ID del contest
        row: Riga del CSV con i dati del partecipante
        row_number: Numero della riga (per logging)
    
    Returns:
        dict: Risultato dell'operazione
    """
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
                        competitor {
                            id
                            name
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
        "schoolExternalId": row["school_code"],
        "name": row["name"],
        "surname": row["surname"],
        "classYear": int(row["class_year"]),
        "section": row["section"],
    }
    
    # Aggiungi birth_date solo se fornita
    if row.get("birth_date") and row["birth_date"].strip():
        variables["birthDate"] = row["birth_date"]
    
    print(f"[Riga {row_number}] Processando {row['name']} {row['surname']}...", file=sys.stderr)
    
    try:
        result = api.query(mutation, variables)
        data = result.get("data", {}).get("participants", {}).get("matchOrCreateParticipant", {})
        typename = data.get("__typename")
        
        if typename == "ParticipantMatchSuccess":
            participant = data.get("participant", {})
            print(f"  ✅ Successo - Participant ID: {participant.get('id')}", file=sys.stderr)
            if data.get("multipleCompetitorsMatched"):
                print(f"  ⚠️  Più competitor corrispondono!", file=sys.stderr)
            
            return {
                "row": row_number,
                "status": "success",
                "data": row,
                "result": data
            }
        elif typename == "OperationInfo":
            messages = data.get("messages", [])
            error_msg = "; ".join([m.get("message", "") for m in messages])
            print(f"  ❌ Errore: {error_msg}", file=sys.stderr)
            
            return {
                "row": row_number,
                "status": "error",
                "data": row,
                "error": error_msg,
                "messages": messages
            }
        else:
            print(f"  ⚠️  Risposta inattesa: {typename}", file=sys.stderr)
            return {
                "row": row_number,
                "status": "unknown",
                "data": row,
                "result": data
            }
    except Exception as e:
        print(f"  ❌ Eccezione: {e}", file=sys.stderr)
        return {
            "row": row_number,
            "status": "exception",
            "data": row,
            "error": str(e)
        }


def import_from_file(
    contest_id: int,
    input_file: str,
    input_format: str = "csv",
    output_format: str = "csv",
    log_file: str = None
) -> List[Dict[str, Any]]:
    """
    Importa partecipanti da un file CSV o JSONL.
    
    Args:
        contest_id: ID del contest
        input_file: Path del file di input (CSV o JSONL)
        input_format: Formato del file di input (csv o jsonl)
        output_format: Formato di output (csv o jsonl)
        log_file: Path del file di log (opzionale)
    
    Returns:
        list: Lista dei risultati per ogni riga
    """
    api = Api()
    
    # Login
    print("Login in corso...", file=sys.stderr)
    api.login()
    
    results = []
    rows = []
    
    # Lettura input
    if input_format == "csv":
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    elif input_format == "jsonl":
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))
    else:
        print(f"Formato input non supportato: {input_format}", file=sys.stderr)
        sys.exit(1)
    
    total = len(rows)
    print(f"Trovate {total} righe da processare\n", file=sys.stderr)
    
    # Processa ogni riga
    for idx, row in enumerate(rows, start=2):  # Start from 2 (1 is header)
        result = process_participant(api, contest_id, row, idx)
        results.append(result)
    
    # Output
    if output_format == "csv":
        # Determina se ci sono colonne id o _id nell'input
        has_id = any("id" in r["data"] for r in results)
        has_underscore_id = any("_id" in r["data"] for r in results)
        
        output_fields = ["row","status"]
        if has_id:
            output_fields.append("id")
        if has_underscore_id:
            output_fields.append("_id")
        output_fields.extend([
            "participant_id","competitor_id","competitor_name","school_code","school_name","competitor_created","participant_created","multiple_competitors_matched","error"
        ])
        
        writer = csv.writer(sys.stdout)
        writer.writerow(output_fields)
        for r in results:
            data = r.get("result", {}) if r["status"] == "success" else {}
            participant = data.get("participant", {}) if data else {}
            competitor = participant.get("competitor", {}) if participant else {}
            # participant_id: sempre l'id del participant creato o trovato
            row_data = [
                r["row"],
                r["status"]
            ]
            if has_id:
                row_data.append(r["data"].get("id", ""))
            if has_underscore_id:
                row_data.append(r["data"].get("_id", ""))
            row_data.extend([
                participant.get("id", r.get("participant_id", "")),
                competitor.get("id", ""),
                competitor.get("name", ""),
                competitor.get("school", {}).get("externalId", r["data"].get("school_code", "")),
                competitor.get("school", {}).get("name", ""),
                '1' if data.get("competitorCreated") else '0',
                '1' if data.get("participantCreated") else '0',
                '1' if data.get("multipleCompetitorsMatched") else '0',
                r.get("error", "")
            ])
            writer.writerow(row_data)
    elif output_format == "jsonl":
        for r in results:
            print(json.dumps(r, ensure_ascii=False))
    else:
        print(f"Formato output non supportato: {output_format}", file=sys.stderr)
        sys.exit(1)
    
    # Log file
    if log_file:
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Importa partecipanti in batch da un file CSV o JSONL"
    )
    
    parser.add_argument(
        "--contest-id",
        type=int,
        required=True,
        help="ID del contest"
    )
    
    parser.add_argument(
        "--input",
        required=True,
        help="Path del file di input (CSV o JSONL)"
    )
    
    parser.add_argument(
        "--input-format",
        choices=["csv", "jsonl"],
        default="csv",
        help="Formato del file di input (csv o jsonl)"
    )
    
    parser.add_argument(
        "--output-format",
        choices=["csv", "jsonl"],
        default="csv",
        help="Formato di output (csv o jsonl)"
    )
    
    parser.add_argument(
        "--log",
        help="Path del file JSON di log dei risultati (opzionale)"
    )
    
    args = parser.parse_args()
    
    try:
        results = import_from_file(
            contest_id=args.contest_id,
            input_file=args.input,
            input_format=args.input_format,
            output_format=args.output_format,
            log_file=args.log
        )
        
        # Exit con codice 1 se ci sono errori
        errors = sum(1 for r in results if r["status"] in ["error", "exception"])
        if errors > 0:
            sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Errore fatale: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
