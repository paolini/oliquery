# Script per unire school_subscriptions_25.csv e venues_14.csv sulle colonne school_external_id/school.externalId
# e aggiungere venue.name e coordinatori (admin.email separati da virgola) al file di output
import csv
import sys
from collections import defaultdict

if len(sys.argv) != 3:
    print("Usage: python merge_schools_coordinators.py <school_file> <venue_file>", file=sys.stderr)
    print("Example: python merge_schools_coordinators.py school_subscriptions_25.csv venues_14.csv > school_subscriptions_25_with_venue.csv", file=sys.stderr)
    sys.exit(1)

SCHOOL_FILE = sys.argv[1]
VENUE_FILE = sys.argv[2]

# Leggi venues_14.csv e costruisci un dizionario: school_external_id -> (venue_id, venue_name, set(admin.email))
venue_info = {}
coordinators = defaultdict(set)
with open(VENUE_FILE, newline='', encoding='utf-8') as f:
	reader = csv.DictReader(f)
	for row in reader:
		school_id = row['school.externalId']
		venue_id = row['venue.id']
		venue_name = row['venue.name']
		email = row['admin.email']
		venue_info[school_id] = (venue_id, venue_name)  # garantito che sono sempre uguali
		coordinators[school_id].add(email)

# Leggi school_subscriptions_25.csv, aggiungi le colonne richieste e scrivi il nuovo file
with open(SCHOOL_FILE, newline='', encoding='utf-8') as fin:
	reader = csv.DictReader(fin)
	fieldnames = reader.fieldnames + ['venue.id', 'venue.name', 'coordinatori']
	writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
	writer.writeheader()
	for row in reader:
		school_id = row['school_external_id']
		venue_id, venue_name = venue_info.get(school_id, ("", ""))
		emails = sorted(coordinators.get(school_id, []))
		row['venue.id'] = venue_id
		row['venue.name'] = venue_name
		row['coordinatori'] = ",".join(emails)
		writer.writerow(row)
