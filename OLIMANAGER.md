# Olimanager - Guida all'uso delle API GraphQL e OAuth2

## Indice
- [API GraphQL](#api-graphql)
- [Autenticazione](#autenticazione)
- [OAuth2 e Access Token](#oauth2-e-access-token)
- [Scope OAuth2](#scope-oauth2)
- [Come ottenere un Access Token](#come-ottenere-un-access-token)
- [Esempi di utilizzo](#esempi-di-utilizzo)

---

## API GraphQL

### Endpoint
L'API GraphQL di Olimanager è accessibile all'endpoint:
- **Produzione**: `https://olimpiadi-scientifiche.it/graphql/`
- **Staging**: `https://staging.olimpiadi-scientifiche.it/graphql/`
- **Sviluppo locale**: `http://localhost:8000/graphql/`

### Schema GraphQL
Lo schema GraphQL è generato automaticamente dalle definizioni dei tipi Python utilizzando Strawberry GraphQL. I tipi principali sono definiti nei moduli `schema.py` di ciascuna app Django.

#### Modelli Principali e Relazioni

##### 1. **Olympiad** (Olimpiade)
Rappresenta un'olimpiade o gara scientifica (es: Olimpiadi di Matematica).

**Campi principali:**
- `id` - Identificatore univoco (es: "olifis", "olimat")
- `name` - Nome completo dell'olimpiade
- `kind` - Tipo: "Olympiad" o "Game"
- `contact_email` - Email di contatto ufficiale
- `website` - Sito web ufficiale
- `logo_path` - Path del logo

**Relazioni:**
- Ha molte **OlympiadEdition** (edizioni dell'olimpiade)
- Ha molti **OlympiadAdmin** (amministratori dell'olimpiade)
- Ha molte **Zone** (zone geografiche per l'organizzazione)

##### 2. **OlympiadEdition** (Edizione dell'Olimpiade)
Rappresenta una specifica edizione di un'olimpiade in un determinato anno scolastico.

**Campi principali:**
- `id` - Identificatore univoco (es: "olimat2023")
- `name` - Nome dell'edizione
- `year` - Anno di conclusione dell'anno scolastico
- `ordinal_number` - Numero ordinale dell'edizione
- `competitor_kind` - Tipo di competitor: "STUDENT" (individuale) o "TEAM" (squadra)
- `school_registration_start/stop` - Periodo di iscrizione scuole
- `student_registration_start/stop` - Periodo di iscrizione studenti
- `allow_automatic_competitor_verification` - Verifica automatica dei competitor

**Relazioni:**
- Appartiene a una **Olympiad**
- Ha molti **Contest** (fasi della competizione)
- Ha molti **SchoolSubscription** (iscrizioni di scuole)
- Ha molti **Competitor** (partecipanti individuali o squadre)
- Ha molti **OlympiadEditionConsentFile** (file di consenso richiesti)
- Ha molti **OlympiadEditionEligibilityRequirement** (requisiti di eligibilità)
- Ha molti **OlympiadEditionExtraField** (campi extra per le iscrizioni)
- Ha molte **SchoolCategory** (tipi di scuola ammessi)

##### 3. **User** (Utente)
Rappresenta un utente registrato nel sistema.

**Campi principali:**
- `id` - ID numerico
- `email` / `normalized_email` - Email dell'utente
- `name` / `surname` - Nome e cognome
- `birth_date` - Data di nascita
- `phone_number` - Numero di telefono
- `fiscal_code` - Codice fiscale
- `gender` - Genere (M/F/O)
- `is_staff` - Se è amministratore di sistema
- `email_verified` - Se l'email è verificata
- `gdpr_consent_*` - Consensi GDPR

**Relazioni:**
- Può avere un **Student** (se è uno studente)
- Può avere molti **Teacher** (se è insegnante di scuole diverse)
- Può essere **OlympiadAdmin** di olimpiadi
- Può essere **ZoneAdmin** di zone
- Può essere **VenueAdmin** di sedi

##### 4. **School** (Scuola)
Rappresenta una scuola registrata nel sistema.

**Campi principali:**
- `id` - ID numerico
- `external_id` - Codice ministeriale
- `name` - Nome della scuola
- `email` - Email ufficiale
- `website` - Sito web
- `is_active` - Se la scuola è attiva
- `game_only` - Se può partecipare solo a "giochi"

**Relazioni:**
- Appartiene a una **SchoolCategory** (tipo di scuola: liceo, istituto, ecc.)
- Ha una **Location** (posizione geografica)
- Ha molti **Teacher** (insegnanti registrati)
- Ha molti **Student** (studenti registrati)
- Ha molti **SchoolSubscription** (iscrizioni a edizioni)
- Ha molti **Competitor** (competitor iscritti per l'edizione)

##### 5. **SchoolCategory** (Categoria Scuola)
Tipi di scuola (es: Liceo Scientifico, Istituto Tecnico, ecc.)

**Campi:**
- `name` - Nome della categoria
- `is_lower` / `is_middle` / `is_higher` - Livello scolastico

##### 6. **Teacher** (Insegnante)
Collega un utente a una scuola come insegnante.

**Campi principali:**
- `id` - ID numerico
- `name` / `surname` - Nome e cognome (copiati dall'utente)
- `verified_at` - Quando è stato verificato
- `is_verified` - Se è stato verificato
- `is_active` - Se è attivo (verificato e non disattivato)

**Relazioni:**
- Appartiene a un **User**
- Appartiene a una **School**
- Può essere verificato da un **User** (admin)

##### 7. **Student** (Studente)
Collega un utente a una scuola come studente.

**Campi principali:**
- `id` - ID numerico
- `class_year` - Anno di corso (1-13)
- `section` - Sezione (es: "A", "B")
- `is_verified` - Stato di verifica (true/false/null)
- `verified_at` - Quando è stato verificato

**Relazioni:**
- Appartiene a un **User** (one-to-one)
- Appartiene a una **School**
- Può essere verificato da un **User** (teacher/admin)

##### 8. **SchoolSubscription** (Iscrizione Scuola)
Iscrizione di una scuola a un'edizione dell'olimpiade.

**Campi principali:**
- `id` - ID numerico
- `donation` - Importo donato
- `automatic_competitor_verification` - Verifica automatica competitor
- `is_valid` - Se l'iscrizione è valida
- `invalidated_at` - Quando è stata invalidata

**Relazioni:**
- Appartiene a una **School**
- Appartiene a una **OlympiadEdition**
- Ha un **Teacher** come contatto
- Ha molti **SchoolSubscriptionConsentFile** (file di consenso caricati)
- Ha molti **SchoolSubscriptionExtraFieldEntry** (campi extra compilati)

##### 9. **Competitor** (Competitore)
Rappresenta un singolo studente o una squadra iscritta a un'edizione.

**Campi principali:**
- `id` - ID numerico
- `name` - Nome del competitor (nome studente o nome squadra)
- `competitor_kind` - "STUDENT" o "TEAM"
- `is_eligible` - Se soddisfa i requisiti di eligibilità
- `is_approved` - Stato di approvazione (true/false/null)
- `approved_at` - Quando è stato approvato
- `invite_token` - Token per invitare membri (per team)

**Relazioni:**
- Appartiene a una **OlympiadEdition**
- Appartiene a una **School**
- Ha molti **CompetitorMember** (membri: 1 per studenti, N per team)
- Ha molti **Participant** (partecipazioni a contest/venue)
- Ha molti **CompetitorExtraFieldEntry** (campi extra compilati)

##### 10. **CompetitorMember** (Membro Competitor)
Rappresenta un singolo membro di un competitor (studente singolo o membro di squadra).

**Campi principali:**
- `id` - ID numerico
- `name` / `surname` - Nome e cognome
- `birth_date` - Data di nascita
- `class_year` - Anno di corso (1-13)
- `section` - Sezione

**Relazioni:**
- Appartiene a un **Competitor**
- Può essere collegato a un **User** (se l'utente si è registrato)
- Può avere un **OlympiadEditionRole** (es: capitano)
- Ha molti **CompetitorMemberConsentFile** (file di consenso caricati)

##### 11. **Contest** (Gara/Fase)
Rappresenta una fase della competizione (es: fase scolastica, regionale, nazionale).

**Campi principali:**
- `id` - ID numerico
- `name` - Nome del contest (es: "Fase Scolastica")
- `start_time` / `end_time` - Periodo della gara
- `scope` - Ambito: "SCHOOL", "ZONE", o "NATIONAL"
- `state` - Stato: "DRAFT", "SCHEDULED", "PUBLIC", "FROZEN", "FINALIZED"
- `allow_online` - Se permette partecipanti online
- `allow_result_upload` - Se i VenueAdmin possono caricare risultati
- `max_venue_depth` - Numero di livelli di subvenue permessi

**Relazioni:**
- Appartiene a una **OlympiadEdition**
- Ha molti **Venue** (sedi della gara)
- Ha molti **ContestProblem** (problemi/prove della gara)
- Ha molti **ContestParticipantExtraField** (campi extra per i partecipanti)

##### 12. **ContestProblem** (Problema/Prova)
Rappresenta un singolo problema o prova di una gara.

**Campi principali:**
- `id` - ID numerico
- `codename` - Nome in codice del problema
- `title` - Titolo del problema
- `index` - Posizione nell'ordine dei problemi
- `group_name` - Gruppo (es: "Giornata 1")
- `min_score` / `max_score` - Punteggio minimo e massimo
- `website` - Link al problema

**Relazioni:**
- Appartiene a un **Contest**
- Ha molti **ParticipantProblemResult** (risultati dei partecipanti)

##### 13. **Venue** (Sede)
Rappresenta una sede fisica in cui si svolge un contest.

**Campi principali:**
- `id` - ID numerico
- `name` - Nome della sede
- `quota` - Numero massimo di qualificati
- `subvenue_level` - Livello di annidamento (0 = sede principale)

**Relazioni:**
- Appartiene a un **Contest**
- Può avere un **Venue** parent (per subvenue)
- Ha molte **Venue** children (subvenue)
- Ha una **Location** (posizione fisica)
- Ha molte **Province** (province associate)
- Ha molti **School** come `extra_schools` (scuole assegnate manualmente)
- Ha molti **School** come `subvenue_schools` (per subvenue)
- Ha molti **VenueAdmin** (amministratori della sede)
- Ha molti **Participant** (partecipanti iscritti)

##### 14. **Participant** (Partecipante)
Rappresenta la partecipazione di un competitor a un contest in una specifica sede.

**Campi principali:**
- `id` - ID numerico
- `online` - Se partecipa online

**Relazioni:**
- Appartiene a un **Competitor**
- Appartiene a una **Venue** (`official_venue` - sede ufficiale)
- Appartiene a una **Venue** (`competing_venue` - sede effettiva di gara)
- Ha un **ParticipantResult** (risultato complessivo)
- Ha molti **ParticipantProblemResult** (risultati per problema)
- Ha molti **ParticipantExtraFieldEntry** (campi extra compilati)

##### 15. **ParticipantResult** (Risultato Partecipante)
Rappresenta il risultato complessivo di un partecipante.

**Campi principali:**
- `total_score` - Punteggio totale
- `ranking_position` - Posizione in classifica
- `disqualified` - Se è stato squalificato
- `qualified` - Se è qualificato per la fase successiva

**Relazioni:**
- Appartiene a un **Participant** (one-to-one)

##### 16. **Zone** (Zona)
Rappresenta una zona geografica per l'organizzazione delle gare.

**Campi principali:**
- `id` - ID numerico
- `name` - Nome della zona

**Relazioni:**
- Appartiene a una **Olympiad**
- Ha una **Location** (posizione di riferimento)
- Ha molte **Province** (province incluse)
- Ha molti **School** come `extra_schools` (scuole aggiunte manualmente)
- Ha molti **ZoneAdmin** (amministratori della zona)

##### 17. **Location** (Posizione Geografica)
Rappresenta un indirizzo fisico.

**Campi principali:**
- `name` - Nome del luogo
- `address` - Via e numero civico
- `postal_code` - CAP

**Relazioni:**
- Appartiene a una **City** (città)

**Gerarchia geografica:**
- **Country** → **Region** → **Province** → **City** → **Location**

#### Schema delle App

I tipi GraphQL sono organizzati nei seguenti moduli:
- `olympiads/schema.py` - Olimpiadi, edizioni, admin
- `users/schema.py` - Utenti e autenticazione
- `schools/schema.py` - Scuole, categorie, iscrizioni
- `teachers/schema.py` - Insegnanti
- `students/schema.py` - Studenti
- `competitors/schema.py` - Competitori e membri
- `contests/schema.py` - Contest, problemi
- `venues/schema.py` - Sedi, venue admin
- `participants/schema.py` - Partecipanti e risultati
- `zones/schema.py` - Zone, zone admin
- `locations/schema.py` - Posizioni geografiche (città, province, regioni)

### Root Types
Il root type `Query` e `Mutation` sono definiti in `api/olimanager/config/schema.py`:

**Query principali:**
```graphql
query {
  healthCheck      # Controllo di salute dell'API
  config { ... }   # Configurazione del sistema
  users { ... }    # Utenti
  olympiads { ... } # Olimpiadi
  schools { ... }   # Scuole
  teachers { ... }  # Insegnanti
  students { ... }  # Studenti
  competitors { ... } # Competitori
  contests { ... }  # Contest
  venues { ... }    # Sedi
  participants { ... } # Partecipanti
  zones { ... }     # Zone
  emails { ... }    # Email
}
```

### Esempio di Query
```graphql
query {
  users {
    me {
      email
      name
      surname
      isStaff
      student {
        school {
          name
        }
        classYear
        section
      }
    }
  }
}
```

### Mutation Importanti

#### `participants.matchOrCreateParticipant`

Questa mutation permette di trovare o creare un partecipante (participant) per un contest di tipo scolastico, cercando di abbinare automaticamente i dati forniti a un competitor esistente.

**Parametri:**
- `contestId` (Int!) - ID del contest
- `schoolExternalId` (String!) - Codice ministeriale della scuola
- `name` (String!) - Nome del partecipante
- `surname` (String!) - Cognome del partecipante
- `classYear` (Int!) - Anno di corso (1-13)
- `section` (String!) - Sezione (es: "A", "B")
- `birthDate` (Date) - Data di nascita (opzionale)

**Restrizioni:**
- Funziona solo per olimpiadi individuali (`competitor_kind == STUDENT`)
- Funziona solo per contest di tipo scolastico (`scope == SCHOOL`)
- L'anno di corso deve essere valido per il tipo di scuola (1-5 elementari, 6-8 medie, 9-13 superiori)

**Logica di matching:**

La mutation cerca un `CompetitorMember` esistente che corrisponda ai seguenti criteri:
1. Stessa edizione e scuola
2. Stesso anno di corso (`class_year`)
3. Nome e cognome corrispondenti (ignora maiuscole/minuscole e accenti, permette inversione nome/cognome)
4. Se `birthDate` è fornita: la sezione O la data di nascita devono corrispondere
5. Se `birthDate` non è fornita: la sezione deve corrispondere
6. La sezione può anche essere preceduta dall'anno di corso (es: "3A" matcha con sezione "A" e anno 3)

Se viene trovato un competitor esistente, viene usato quello (priorità a chi ha effettuato login più recentemente).
Se non viene trovato, viene creato un nuovo competitor e un nuovo member.

In entrambi i casi, viene creato un participant se non esiste già per quel contest.

**Risposta:**
```graphql
type ParticipantMatchSuccess {
  participant: ParticipantType!
  competitorCreated: Boolean!      # true se è stato creato un nuovo competitor
  participantCreated: Boolean!     # true se è stato creato un nuovo participant
  multipleCompetitorsMatched: Boolean!  # true se più competitor corrispondono ai criteri
}
```

**Esempio:**
```graphql
mutation {
  participants {
    matchOrCreateParticipant(
      contestId: 123
      schoolExternalId: "RMPC01000A"
      name: "Mario"
      surname: "Rossi"
      classYear: 10
      section: "A"
      birthDate: "2008-05-15"
    ) {
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
```

**Caso d'uso:**

Questa mutation è particolarmente utile per:
- Importare liste di partecipanti da fonti esterne
- Registrare automaticamente partecipanti a contest scolastici
- Evitare duplicati cercando di abbinare i dati a competitor già esistenti

---

## Autenticazione

### Autenticazione tramite Sessione (Frontend)
Il frontend di Olimanager utilizza l'autenticazione basata su **sessione Django** e **CSRF token**:

1. L'utente effettua il login tramite mutation GraphQL `users.login(email, password)`
2. Django crea una sessione e imposta il cookie `sessionid`
3. Tutte le richieste successive includono il cookie di sessione e l'header `X-CSRFToken`

**Esempio di login:**
```graphql
mutation {
  users {
    login(email: "user@example.com", password: "password") {
      __typename
      ... on LoginSuccess {
        user {
          email
        }
      }
      ... on OperationInfo {
        messages {
          message
        }
      }
    }
  }
}
```

### Autenticazione tramite Bearer Token (OAuth2)
Il server di **staging** supporta l'autenticazione tramite Bearer token OAuth2 per le API GraphQL. Gli access token OAuth2 possono essere utilizzati per:
- API GraphQL (staging)
- OpenID Connect (OIDC)
- Endpoint `/o/userinfo/`
- Integrazioni SSO (Single Sign-On)

Per utilizzare l'autenticazione Bearer token, includi l'header `Authorization: Bearer <token>` nelle richieste HTTP.

**Nota**: Il server di produzione potrebbe non supportare ancora questa funzionalità. Verifica la configurazione del deployment prima di utilizzare Bearer token in produzione.

---

## OAuth2 e Access Token

Olimanager utilizza **django-oauth-toolkit** per implementare OAuth2. La configurazione si trova in `api/olimanager/config/settings.py`:

```python
OAUTH2_PROVIDER = {
    "OIDC_ENABLED": True,
    "SCOPES": {
        "openid": "OpenID Connect",
        "profile": "Read your name, role and school",
        "email": "Read your email",
        "birthdate": "Read your birth date",
    },
    "OAUTH2_VALIDATOR_CLASS": "olimanager.oauth.validators.CustomOAuth2Validator",
    "SCOPES_BACKEND_CLASS": "olimanager.oauth.backend_scope.CustomSettingsScopes",
}
```

### Endpoint OAuth2
Gli endpoint OAuth2 standard sono disponibili sotto `/o/`:
- `/o/authorize/` - Autorizzazione OAuth2
- `/o/token/` - Richiesta token
- `/o/revoke_token/` - Revoca token
- `/o/introspect/` - Introspezione token
- `/o/userinfo/` - Informazioni utente (OIDC)

---

## Scope OAuth2

### Scope Statici
Gli scope statici configurati in `settings.py`:

| Scope | Descrizione | Dati restituiti |
|-------|-------------|-----------------|
| `openid` | OpenID Connect | ID token per OIDC |
| `profile` | Profilo utente | Nome, cognome, scuola, classe, ruolo (student/teacher/staff) |
| `email` | Email utente | Email e stato di verifica |
| `birthdate` | Data di nascita | Data di nascita |

### Scope Dinamici
La classe `CustomSettingsScopes` in `api/olimanager/oauth/backend_scope.py` aggiunge dinamicamente scope del tipo:
- `contest<ID>` - Permesso di accesso a informazioni specifiche di un contest (es: `contest123`)

### Claims nei Token
Il validatore custom `CustomOAuth2Validator` in `api/olimanager/oauth/validators.py` determina quali informazioni (claims) vengono incluse nel token in base agli scope richiesti:

**Scope `profile`:**
```json
{
  "name": "Mario Rossi",
  "given_name": "Mario",
  "family_name": "Rossi",
  "school": [{
    "external_id": "ABC123",
    "name": "Liceo Scientifico",
    "type": "Liceo"
  }],
  "class_year": 4,
  "section": "A",
  "roles": ["student"]
}
```

**Scope `email`:**
```json
{
  "email": "mario.rossi@example.com",
  "email_verified": true
}
```

**Scope `contest123`:**
```json
{
  "contests": {
    "123": ["olympiad_admin", "venue_admin_456"]
  }
}
```

---

## Come ottenere un Access Token

### 1. Via Django Admin (Manuale)

1. Accedi all'admin Django: `/admin/`
2. Vai su **Django OAuth Toolkit** → **Applications**
3. Crea una nuova Application:
   - **Client type**: Confidential
   - **Authorization grant type**: Resource owner password-based
   - **User**: seleziona l'utente proprietario (opzionale)
   - Salva e annota `client_id` e `client_secret`

4. Vai su **Django OAuth Toolkit** → **Access tokens**
5. Crea un nuovo Access token:
   - **Token**: genera un token casuale (es: con Python `from oauthlib.common import generate_token; print(generate_token())`)
   - **User**: seleziona l'utente per cui creare il token
   - **Application**: seleziona l'Application creata sopra
   - **Expires**: imposta la data di scadenza
   - **Scope**: inserisci gli scope desiderati separati da spazio (es: `profile email`)
   - Salva

6. Il campo **Token** contiene l'access token da utilizzare

### 2. Via Endpoint `/o/token/` (Programmatico)

#### Grant Type: Password
Ottieni un token fornendo username e password:

```bash
curl -X POST https://staging.olimpiadi-scientifiche.it/o/token/ \
  -d "grant_type=password" \
  -d "username=user@example.com" \
  -d "password=your_password" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "scope=profile email"
```

**Risposta:**
```json
{
  "access_token": "AbCdEf123456...",
  "expires_in": 36000,
  "token_type": "Bearer",
  "scope": "profile email",
  "refresh_token": "XyZ789..."
}
```

#### Grant Type: Client Credentials
Token senza utente associato (solo per operazioni "di sistema"):

```bash
curl -X POST https://staging.olimpiadi-scientifiche.it/o/token/ \
  -d "grant_type=client_credentials" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "scope=profile"
```

**Nota**: Con `client_credentials`, il token **non** è associato a nessun utente e quindi non ha privilegi utente.

### 3. Via Shell Django

Genera un token manualmente dalla shell Django:

```bash
cd api
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
from oauth2_provider.models import get_application_model, AccessToken
from oauthlib.common import generate_token
from django.utils import timezone
from datetime import timedelta

User = get_user_model()
Application = get_application_model()

# Sostituisci con i dati reali
user = User.objects.get(email="user@example.com")
app = Application.objects.get(client_id="YOUR_CLIENT_ID")

# Genera access token valido 1 ora
access_token = generate_token()
expires = timezone.now() + timedelta(hours=1)
scope = "profile email"

token = AccessToken.objects.create(
    user=user,
    application=app,
    token=access_token,
    expires=expires,
    scope=scope,
)

print("Access token:", token.token)
```

---

## Esempi di utilizzo

### Utilizzo dell'Access Token con le API GraphQL

**Nota**: Gli esempi seguenti funzionano sul server di **staging**. Verifica che il server di produzione supporti l'autenticazione Bearer token prima di utilizzarli in produzione.

#### Con curl
```bash
curl -X POST https://staging.olimpiadi-scientifiche.it/graphql/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ users { me { email name } } }"
  }'
```

#### Con Python (requests)
```python
import requests

url = "https://staging.olimpiadi-scientifiche.it/graphql/"
headers = {
    "Authorization": "Bearer YOUR_ACCESS_TOKEN",
    "Content-Type": "application/json"
}
query = """
query {
  users {
    me {
      email
      name
      surname
      student {
        school {
          name
        }
      }
    }
  }
}
"""

response = requests.post(url, json={"query": query}, headers=headers)
print(response.json())
```

#### Con JavaScript (fetch)
```javascript
const url = "https://staging.olimpiadi-scientifiche.it/graphql/";
const token = "YOUR_ACCESS_TOKEN";

const query = `
  query {
    users {
      me {
        email
        name
      }
    }
  }
`;

fetch(url, {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json"
  },
  body: JSON.stringify({ query })
})
.then(res => res.json())
.then(data => console.log(data));
```

### Utilizzo dell'Endpoint `/o/userinfo/`
L'endpoint OIDC `/o/userinfo/` **supporta** nativamente i Bearer token:

```bash
curl -X GET https://staging.olimpiadi-scientifiche.it/o/userinfo/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Risposta:**
```json
{
  "sub": "123",
  "email": "user@example.com",
  "email_verified": true,
  "name": "Mario Rossi",
  "given_name": "Mario",
  "family_name": "Rossi",
  "school": [{
    "external_id": "ABC123",
    "name": "Liceo Scientifico",
    "type": "Liceo"
  }],
  "roles": ["student"]
}
```

---

## Note Importanti

1. **Le API GraphQL sul server di staging supportano Bearer token OAuth2** per l'autenticazione. Il server di produzione potrebbe non supportare ancora questa funzionalità.

2. L'autenticazione può avvenire in due modi:
   - **Sessione Django + CSRF token**: metodo predefinito utilizzato dal frontend
   - **Bearer token OAuth2**: per accesso programmatico alle API (disponibile su staging)

3. Gli **scope OAuth2** determinano quali informazioni sono incluse nei claims del token, ma **non limitano automaticamente** l'accesso alle API GraphQL. Per implementare controlli di permesso basati su scope, è necessario verificare manualmente gli scope nei resolver GraphQL.

4. Il campo `user` della **Application** indica solo il proprietario dell'application, **non** l'utente a cui saranno associati i token generati.

5. Con `grant_type=client_credentials`, il token **non** è associato a nessun utente e quindi non ha privilegi utente.

---

## Risorse Utili

- **Admin Django**: `/admin/`
- **GraphQL Playground**: `/graphql/` (in modalità sviluppo)
- **Schema GraphQL generato**: `api/schema.graphql`
- **Documentazione django-oauth-toolkit**: https://django-oauth-toolkit.readthedocs.io/
- **Documentazione Strawberry GraphQL**: https://strawberry.rocks/

---

## Credenziali di Test (Staging)

Sul server di staging (`https://staging.olimpiadi-scientifiche.it/`), puoi usare questi utenti di test:

- `admin@olimanager.it` - Admin con superpowers
- `admin.oligas@olimanager.it` - Admin Olimpiade per `oligas`
- `t1@olimanager.it` - Insegnante
- `s1@olimanager.it` - Studente

**Password**: per tutti gli utenti la password è uguale all'email.
