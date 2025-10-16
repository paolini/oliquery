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