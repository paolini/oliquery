"""
Script per leggere i dati dei partecipanti da un file JSONL e creare/abbinare i partecipanti.

Uso:
    cat participants.jsonl | python create_participant.py CONTEST_ID > results.jsonl
    
Esempio:
    echo '{"schoolExternalId": "AORA025009", "name": "Mario", "surname": "Rossi", "classYear": 3, "section": "A", "birthDate": "2007-05-15"}' | python create.py 1

Il file JSONL in input deve contenere per ogni riga:
    - schoolExternalId: codice meccanografico della scuola (es. "AORA025009")
    - name: nome dello studente
    - surname: cognome dello studente
    - classYear: anno di corso (1-5 per elementari, 6-8 per medie, 9-13 per superiori)
    - section: sezione (es. "A", "B", etc.)
    - birthDate: data di nascita (opzionale, formato "YYYY-MM-DD")

mutations da usare:

bulkUpdateResults(
    contestId: Int!
    problemResults: [ParticipantProblemResultInput!]!
): BulkUpdateResultsPayload!

matchOrCreateParticipant(
    contestId: Int!
    schoolExternalId: String!
    name: String!
    surname: String!
    classYear: Int!
    section: String!
    birthDate: Date
): MatchOrCreateParticipantPayload!

ParticipantMatchSuccess(participant: olimanager.participants.schema.ParticipantType, 
    competitor_created: bool, participant_created: bool, multiple_competitors_matched: bool)
messages: [OperationMessage!]!
"""

import sys
import json
import os
from api import Api

# Mutation per creare/abbinare un partecipante
mutation_match_or_create = """
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
      ... on OperationInfo {
        messages {
          message
          kind
        }
      }
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
    }
  }
}
"""

def match_or_create_participant(api, contest_id, participant_data):
    """Chiama la mutation per creare/abbinare un partecipante"""
    try:
        variables = {
            "contestId": contest_id,
            "schoolExternalId": participant_data["schoolExternalId"],
            "name": participant_data["name"],
            "surname": participant_data["surname"],
            "classYear": participant_data["classYear"],
            "section": participant_data["section"],
        }
        
        # birthDate è opzionale
        if "birthDate" in participant_data and participant_data["birthDate"]:
            variables["birthDate"] = participant_data["birthDate"]
        
        response = api.query(mutation_match_or_create, variables)
        
        if "errors" in response:
            return {
                "success": False,
                "error": response["errors"],
                "input": participant_data
            }
        
        result = response["data"]["participants"]["matchOrCreateParticipant"]
        typename = result["__typename"]
        
        if typename == "OperationInfo":
            return {
                "success": False,
                "messages": result["messages"],
                "input": participant_data
            }
        elif typename == "ParticipantMatchSuccess":
            return {
                "success": True,
                "participant": result["participant"],
                "competitorCreated": result["competitorCreated"],
                "participantCreated": result["participantCreated"],
                "multipleCompetitorsMatched": result["multipleCompetitorsMatched"],
                "input": participant_data
            }
        else:
            return {
                "success": False,
                "error": f"Unknown typename: {typename}",
                "input": participant_data
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "input": participant_data
        }

if __name__ == "__main__":
    # Legge il contestId dall'ambiente o dagli argomenti
    if len(sys.argv) > 1:
        contest_id = int(sys.argv[1])
    else:
        contest_id = int(os.environ.get("OLI_CONTEST_ID", 0))
        if contest_id == 0:
            print("Errore: specificare contestId come argomento o impostare OLI_CONTEST_ID", file=sys.stderr)
            print(f"Usage: {sys.argv[0]} CONTEST_ID < input.jsonl > output.jsonl", file=sys.stderr)
            sys.exit(1)
    
    # Inizializza API e login
    api = Api()
    api.login()
    
    print(f"Usando contestId={contest_id}", file=sys.stderr)
    print("Leggendo partecipanti da stdin...", file=sys.stderr)
    
    # Processa ogni riga del file JSONL
    count = 0
    for line in sys.stdin:
        if not line.strip():
            continue
        
        count += 1
        participant_data = json.loads(line)
        
        print(f"Processando partecipante {count}: {participant_data.get('name')} {participant_data.get('surname')}...", file=sys.stderr)
        
        result = match_or_create_participant(api, contest_id, participant_data)
        
        # Scrive il risultato su stdout
        print(json.dumps(result))
    
    print(f"Completato! Processati {count} partecipanti", file=sys.stderr)

