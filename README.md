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
