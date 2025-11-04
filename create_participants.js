#!/usr/bin/env node
/**
 * Script per leggere i dati dei partecipanti da un file JSONL e creare/abbinare i partecipanti (versione Node.js).
 * 
 * Uso:
 *   cat participants.jsonl | node create_participants.js CONTEST_ID > results.jsonl
 * 
 * Esempio:
 *   echo '{"schoolExternalId": "AORA025009", "name": "Mario", "surname": "Rossi", "classYear": 13, "section": "A", "birthDate": "2007-05-15"}' | node create_participants.js 1
 * 
 * Variabili d'ambiente richieste per l'autenticazione:
 *   - OLI_EMAIL
 *   - OLI_PASSWORD
 *   - OLI_GRAPHQL_ENDPOINT (opzionale, default: https://olimpiadi-scientifiche.it/graphql/)
 *   - OLI_CONTEST_ID (alternativa all'argomento da riga di comando)
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

// Usa la fetch built-in di Node 18+ (undici)
const fetch = global.fetch || require('node-fetch');

// Caricamento molto semplice di un file .env se presente (senza dipendenze)
function loadDotEnvIfPresent() {
  const envPath = path.resolve(process.cwd(), '.env');
  if (fs.existsSync(envPath)) {
    const content = fs.readFileSync(envPath, 'utf-8');
    content.split(/\r?\n/).forEach((line) => {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) return;
      const eq = trimmed.indexOf('=');
      if (eq === -1) return;
      const key = trimmed.slice(0, eq).trim();
      let value = trimmed.slice(eq + 1).trim();
      if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith('\'') && value.endsWith('\''))) {
        value = value.slice(1, -1);
      }
      if (!(key in process.env)) {
        process.env[key] = value;
      }
    });
  }
}

loadDotEnvIfPresent();

class Api {
  constructor({ requireEdition = false } = {}) {
    this.endpoint = process.env.OLI_GRAPHQL_ENDPOINT || 'https://olimpiadi-scientifiche.it/graphql/';
    this.EMAIL = process.env.OLI_EMAIL;
    this.PASSWORD = process.env.OLI_PASSWORD;
    this.EDITION = requireEdition ? (process.env.OLI_EDITION || null) : null;

    this.cookies = {}; // cookieName -> value
    this.headers = { 'Content-Type': 'application/json' };

    process.stderr.write(`Using endpoint: ${this.endpoint}\n`);
    if (requireEdition && !this.EDITION) {
      throw new Error('OLI_EDITION required in environment variables');
    }
  }

  // Estrae i cookie da un array di header Set-Cookie
  static parseSetCookie(setCookieArray) {
    const jar = {};
    (setCookieArray || []).forEach((c) => {
      if (!c) return;
      const parts = c.split(';');
      if (parts.length > 0) {
        const [name, ...rest] = parts[0].split('=');
        const value = rest.join('=');
        if (name && value) jar[name.trim()] = value.trim();
      }
    });
    return jar;
  }

  // Converte i cookie in header "Cookie"
  cookieHeader() {
    const entries = Object.entries(this.cookies).filter(([k, v]) => k && v);
    return entries.map(([k, v]) => `${k}=${v}`).join('; ');
  }

  // Effettua una richiesta grezza, mantenendo il jar dei cookie e il token CSRF
  async rawRequest(body) {
    // Se non abbiamo ancora un csrftoken, effettuiamo una primissima chiamata per riceverlo
    if (!this.cookies.csrftoken) {
      process.stderr.write('Creating session\n');
      const r0 = await fetch(this.endpoint, { method: 'POST' });
      const setCookies = typeof r0.headers.getSetCookie === 'function'
        ? r0.headers.getSetCookie()
        : (r0.headers.get('set-cookie') ? [r0.headers.get('set-cookie')] : []);
      Object.assign(this.cookies, Api.parseSetCookie(setCookies));
      if (this.cookies.csrftoken) {
        this.headers['X-CsrfToken'] = this.cookies.csrftoken;
      }
    }

    const headers = { ...this.headers };
    const cookieStr = this.cookieHeader();
    if (cookieStr) headers['Cookie'] = cookieStr;

    const resp = await fetch(this.endpoint, {
      method: 'POST',
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });

    // Aggiorna eventuali cookie e csrf
    const setCookies = typeof resp.headers.getSetCookie === 'function'
      ? resp.headers.getSetCookie()
      : (resp.headers.get('set-cookie') ? [resp.headers.get('set-cookie')] : []);
    const parsed = Api.parseSetCookie(setCookies);
    Object.assign(this.cookies, parsed);
    if (this.cookies.csrftoken) {
      this.headers['X-CsrfToken'] = this.cookies.csrftoken;
    }

    const text = await resp.text();
    let json;
    try { json = text ? JSON.parse(text) : {}; } catch (e) { json = { parseError: e.message, raw: text }; }

    if (resp.status !== 200) {
      process.stderr.write(JSON.stringify(json, null, 2) + '\n');
      throw new Error(`Query failed to run with a ${resp.status}.`);
    }
    return json;
  }

  async query(query, vars = {}) {
    const variables = this.EDITION ? { ...vars, EDITION: this.EDITION } : vars;
    return this.rawRequest({ query, variables });
  }

  async login() {
    process.stderr.write('Logging in\n');
    if (!this.EMAIL) {
      throw new Error('Email non specificata!\nPer risolvere:\nesportare OLI_EMAIL=my-email');
    }
    if (!this.PASSWORD) {
      throw new Error('Password non specificata!\nPer risolvere:\nesportare OLI_PASSWORD=my-secret-password');
    }
    const r = await this.query(
      `mutation ($EMAIL: String!, $PASSWORD: String!) {\n        users{\n          login(email: $EMAIL, password: $PASSWORD){\n            __typename\n            ...on OperationInfo{\n              messages{\n                message\n                kind\n              }\n            }\n            ...on LoginSuccess{\n              user{\n                email\n              }\n            }\n          }\n        }\n      }`,
      { EMAIL: this.EMAIL, PASSWORD: this.PASSWORD }
    );
    const login = r?.data?.users?.login;
    const typename = login?.__typename;
    if (typename === 'OperationInfo') {
      const msg = (login.messages || []).map((x) => x.message).join(', ');
      throw new Error('OperationInfo: ' + msg);
    }
    return r;
  }
}

const mutation_match_or_create = `
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
`;

async function matchOrCreateParticipant(api, contestId, participantData) {
  try {
    const variables = {
      contestId: Number(contestId),
      schoolExternalId: participantData.schoolExternalId,
      name: participantData.name,
      surname: participantData.surname,
      classYear: participantData.classYear,
      section: participantData.section,
    };
    if (participantData.birthDate) {
      variables.birthDate = participantData.birthDate;
    }

    const response = await api.query(mutation_match_or_create, variables);

    if (response.errors) {
      return { success: false, error: response.errors, input: participantData };
    }

    const result = response?.data?.participants?.matchOrCreateParticipant;
    const typename = result?.__typename;

    if (typename === 'OperationInfo') {
      return { success: false, messages: result.messages, input: participantData };
    } else if (typename === 'ParticipantMatchSuccess') {
      return {
        success: true,
        participant: result.participant,
        competitorCreated: result.competitorCreated,
        participantCreated: result.participantCreated,
        multipleCompetitorsMatched: result.multipleCompetitorsMatched,
        input: participantData,
      };
    }

    return { success: false, error: `Unknown typename: ${typename}` , input: participantData };
  } catch (e) {
    return { success: false, error: String(e && e.message ? e.message : e), input: participantData };
  }
}

async function main() {
  const args = process.argv.slice(2);
  let contestId = null;
  if (args.length > 0) {
    contestId = parseInt(args[0], 10);
  } else if (process.env.OLI_CONTEST_ID) {
    contestId = parseInt(process.env.OLI_CONTEST_ID, 10);
  }
  if (!contestId || Number.isNaN(contestId)) {
    process.stderr.write('Errore: specificare contestId come argomento o impostare OLI_CONTEST_ID\n');
    process.stderr.write(`Usage: ${path.basename(process.argv[1])} CONTEST_ID < input.jsonl > output.jsonl\n`);
    process.exit(1);
  }

  const api = new Api();
  await api.login();

  process.stderr.write(`Uso contestId=${contestId}\n`);
  process.stderr.write('Leggo partecipanti da stdin...\n');

  const rl = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });

  let count = 0;
  let errorCount = 0;

  for await (const line of rl) {
    if (!line || !line.trim()) continue;
    count += 1;

    let participantData;
    try {
      participantData = JSON.parse(line);
    } catch (e) {
      errorCount += 1;
      const err = { success: false, error: `JSON parse error: ${e.message}`, input: line };
      process.stderr.write(`Processo partecipante ${count}: ERRORE parse JSON\n`);
      process.stdout.write(JSON.stringify(err) + '\n');
      continue;
    }

    process.stderr.write(`Processo partecipante ${count}: ${participantData.name} ${participantData.surname}...\n`);

    const result = await matchOrCreateParticipant(api, contestId, participantData);
    const success = !!result.success;
    if (!success) {
      errorCount += 1;
      const errMsg = result.error || result.messages || 'Unknown error';
      process.stderr.write(`  Errore: ${typeof errMsg === 'string' ? errMsg : JSON.stringify(errMsg)}\n`);
    }

    process.stdout.write(JSON.stringify(result) + '\n');
  }

  process.stderr.write(`Processati ${count} partecipanti con ${errorCount} errori\n`);
}

if (require.main === module) {
  main().catch((e) => {
    process.stderr.write((e && e.stack) ? e.stack + '\n' : (String(e) + '\n'));
    process.exit(1);
  });
}
