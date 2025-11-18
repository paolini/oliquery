Estrai l'elenco delle scuole che si sono iscritte all'edizione di quest'anno
```
python school_subscriptions.py olimat26 > school_subscriptions_26.csv
```

Determina il codice della gara di febbraio le cui `venue` corrispondono
ai distretti:
```
python contests.py
```

Estrai l'elenco dei distretti e delle loro scuole
```
python venues.py 27 > venues_27.csv
```

Unisci le informazioni in un unico file:
```
python merge_schools_coordinators.py school_subscriptions_26.csv venues_27.csv > school_subscriptions_26_with_venue.csv
```

Importa l'ultimo file ottenuto su olifogli.
Il foglio deve avere schema: "schools". Una volta creato il foglio scuole selezionandolo compare il pulsante [crea fogli scuole] che fa una anteprima degli aggiornamenti necessari. Si può confermare e procedere con l'aggiornamento.

