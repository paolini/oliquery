Copia il codice:
```
git clone https://github.com/paolini/oliquery.git
cd oliquery
```

Prima di iniziare servono le credenziali. Crea un file `.env`
con queste righe (inserisci le tue credenziali):
```
OLI_EMAIL=<my@email.com>
OLI_PASSWORD=<my_secret_password>
OLI_EDITION=olimat25
OLI_GRAPHQL_ENDPOINT=https://olimpiadi-scientifiche.it/graphql/
```


Test di funzionamento del login:
```
python api.py
```

Elenco CDRD:
```
python cdrd.py
```

Elenco scuole:
```
python schools.py
```

Elenco distretti:
```
python zones.py
```

Elenco sottoscrizioni scuole:
```
python school_subscriptions.py olimat25
```

# importazione dati per gara di Archimede

Estrai l'elenco delle scuole che si sono iscritte all'edizione di quest'anno
```
python school_subscriptions.py olimat25 > school_subscriptions_25.csv
```

Determina il codice della gara di febbraio le cui `venue` corrispondono
ai distretti:
```
python contests.py
```

Estrai l'elenco dei distretti e delle loro scuole
```
python venues.py 14 > venues_14.csv
```

Unisci le informazioni in un unico file:
```
python merge_schools_coordinators.py school_subscriptions_25.csv venues_14.csv > school_subscriptions_25_with_venue.csv
```

Importa l'ultimo file ottenuto su olifogli.

# Importazione partecipanti (match_or_create_participant)

Crea/trova partecipanti per contest scolastici usando la mutation `matchOrCreateParticipant`:

**Singolo partecipante:**
```bash
python match_create_participant.py \
    --contest-id 1 \
    --school-code BIPS01000N \
    --name Mario --surname Rossi \
    --class-year 10 --section A \
    --birth-date 2008-05-15 \
    --format csv
```

**Batch da CSV:**
```bash
python match_create_participant_batch.py \
    --contest-id 1 \
    --input partecipanti.csv \
    --output-format csv > risultati.csv
```

Il file CSV di input deve avere le colonne: `name`, `surname`, `class_year`, `section`, `school_code`, `birth_date` (opzionale). Se presenti le colonne `id` o `_id` vengono riportate nell'output.

Output: CSV con `participant_id` (ID del participant creato/trovato) e stato dell'operazione.

Performance: ~220ms per riga (100 righe in ~22 secondi).

Vedi [MATCH_PARTICIPANT_README.md](MATCH_PARTICIPANT_README.md) per dettagli completi.
````