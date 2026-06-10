```markdown
# ReadyGen (DocPilot)

ReadyGen, precedentemente conosciuto come DocPilot, è una piattaforma innovativa che sfrutta la potenza dell'intelligenza artificiale per generare automaticamente documentazione tecnica per i tuoi repository di codice. Sia che tu abbia bisogno di un README accattivante, di API complete, di un changelog aggiornato o di una panoramica architetturale, ReadyGen si integra con le tue piattaforme Git preferite (GitHub, GitLab, Bitbucket) per semplificare e velocizzare il processo di documentazione.

Il progetto si compone di un backend FastAPI per la logica di business e l'interazione con le API Git e AI, e un frontend HTML/CSS/JS reattivo e intuitivo che offre un'esperienza utente fluida.

## Funzionalità principali

*   **Generazione automatica di documentazione:** Crea diversi tipi di documentazione (README, API Docs, Changelog, Project Overview, OpenAPI, SDK, Commenti inline) in base al codice del tuo repository.
*   **Supporto multi-provider Git:** Si integra con GitHub, GitLab e Bitbucket per recuperare repository e gestire le operazioni di push.
*   **Integrazione AI avanzata:** Utilizza modelli di intelligenza artificiale (es. Gemini 2.0 Flash) per analizzare il codice e produrre documentazione di alta qualità.
*   **Dashboard utente:** Una dashboard intuitiva per visualizzare i tuoi repository, selezionare il tipo di documentazione da generare e gestirne lo storico.
*   **Funzionalità di copia e download:** Copia facilmente la documentazione generata o scaricala come file.
*   **Push diretto nel repository:** Opzione per effettuare il push della documentazione generata direttamente nel tuo repository.
*   **Sistema di autenticazione:** Accesso sicuro tramite OAuth con i provider Git.
*   **Piani di abbonamento:** Supporto per piani "Free", "Pro" e "Team" con funzionalità e limiti variabili, gestiti tramite Stripe.
*   **Notifiche email:** Invia notifiche email all'utente quando una documentazione è pronta.
*   **Localizzazione (i18n):** Interfaccia utente disponibile in più lingue (italiano, inglese, spagnolo, francese, tedesco).

## Requisiti e dipendenze

### Backend

*   **Python 3.9+**
*   **PIP** per la gestione dei pacchetti.
*   **Variabili d'ambiente:** Un file `.env` con le configurazioni necessarie (vedi `.env.example`).
    *   `SECRET_KEY`: Chiave segreta per la firma dei token JWT.
    *   `FRONTEND_URL`: URL del frontend (es. `http://localhost:3000`).
    *   `SUPABASE_URL`, `SUPABASE_ANON_KEY`: Credenziali Supabase.
    *   `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `GITHUB_REDIRECT_URI`: Credenziali per l'API GitHub OAuth.
    *   `GITLAB_CLIENT_ID`, `GITLAB_CLIENT_SECRET`, `GITLAB_REDIRECT_URI`: Credenziali per l'API GitLab OAuth.
    *   `BITBUCKET_CLIENT_ID`, `BITBUCKET_CLIENT_SECRET`, `BITBUCKET_REDIRECT_URI`: Credenziali per l'API Bitbucket OAuth.
    *   `GEMINI_API_KEY` o `OPENAI_API_KEY`: Chiave API per il servizio di intelligenza artificiale.
    *   `RESEND_API_KEY`, `FROM_EMAIL`: Credenziali per il servizio di invio email (Resend).
    *   `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRO_PRICE_ID`, `STRIPE_TEAM_PRICE_ID`: Credenziali e ID prezzi per l'integrazione Stripe.

### Frontend

*   Un browser web moderno.
*   `npx serve` o un server web statico per servire i file statici del frontend.

### Database

*   **Supabase:** Utilizzato come database PostgreSQL e per l'autenticazione. Sono forniti script di migrazione per la configurazione del database.

## Istruzioni di installazione

Le istruzioni seguenti assumono che tu stia eseguendo il setup su un ambiente Linux/macOS.

### 1. Clonare il repository

```bash
git clone https://github.com/paulnatan/docpilot.git
cd docpilot
```

### 2. Configurazione del Backend

#### 2.1. Ambiente virtuale e dipendenze

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 2.2. Variabili d'ambiente

Crea un file `.env` nella cartella `backend/` basandoti su `.env.example` e compilalo con le tue credenziali.

```ini
# Esempio di .env
SECRET_KEY="la_tua_chiave_segreta_jwt"
FRONTEND_URL="http://localhost:3000"

SUPABASE_URL="https://il_tuo_supabase_project.supabase.co"
SUPABASE_ANON_KEY="il_tuo_anon_key"
SUPABASE_SERVICE_ROLE_KEY="il_tuo_service_role_key" # Richiesto per alcuni webhook o operazioni backend

GITHUB_CLIENT_ID="il_tuo_github_client_id"
GITHUB_CLIENT_SECRET="il_tuo_github_client_secret"
GITHUB_REDIRECT_URI="http://localhost:8000/auth/callback/github"

# ... (simili per GitLab e Bitbucket)

GEMINI_API_KEY="la_tua_gemini_api_key"
# OPENAI_API_KEY="la_tua_openai_api_key" # In alternativa a Gemini

RESEND_API_KEY="la_tua_resend_api_key"
FROM_EMAIL="noreply@tuo_dominio.com"

STRIPE_SECRET_KEY="sk_test_..."
STRIPE_WEBHOOK_SECRET="whsec_..."
STRIPE_PRO_PRICE_ID="price_..."
STRIPE_TEAM_PRICE_ID="price_..."
```

#### 2.3. Avvio del Backend

```bash
uvicorn main:app --reload --port 8000 --host 0.0.0.0
```
Il backend sarà disponibile su `http://localhost:8000`. Le API Docs saranno su `http://localhost:8000/docs`.

### 3. Configurazione del Frontend

#### 3.1. Installazione di `serve`

Se non lo hai già installato globalmente:
```bash
npm install -g serve
```

#### 3.2. Avvio del Frontend

Torna nella directory principale del progetto e poi entra in `frontend`:

```bash
cd .. # dalla cartella backend
cd frontend
npx serve . -p 3000 -c serve.json
```
Il frontend sarà disponibile su `http://localhost:3000`.

### 4. Configurazione del Database (Supabase)

1.  Crea un nuovo progetto Supabase.
2.  Nel pannello SQL Editor di Supabase, esegui i seguenti script nell'ordine:
    *   `supabase_schema.sql` (crea le tabelle `users` e `docs`).
    *   `supabase_migration_v2_multiprovider.sql` (aggiunge il supporto per GitLab e Bitbucket).
    *   `supabase_migration_v3_payments.sql` (aggiunge il supporto per i piani di abbonamento e Stripe).

### 5. Avvio Completo con `start.sh` (solo macOS)

Lo script `start.sh` è progettato per avviare l'intero stack localmente su macOS, aprendo diverse finestre di Terminale. Potrebbe essere necessario modificare `PROJECT_DIR` al percorso assoluto del tuo progetto.
Esegue anche un tentativo di avviare un container Docker chiamato `n8n` (presumendo che tu stia usando n8n per webhook o automazioni, anche se non strettamente essenziale per il core dell'app) e Cloudflare Tunnel.

```bash
chmod +x start.sh
./start.sh
```

## Come usare il progetto

ReadyGen è un'applicazione web. Una volta avviati il backend e il frontend:

1.  **Accedi al Frontend:** Apri il tuo browser e vai a `http://localhost:3000`.
2.  **Autenticazione:** Clicca sul pulsante "Accedi con GitHub" (o GitLab/Bitbucket, se implementato sull'interfaccia principale) per autenticarti tramite OAuth. Verrai reindirizzato alla pagina di autorizzazione del provider Git, poi di nuovo alla dashboard di ReadyGen.
3.  **Dashboard:** Dopo l'autenticazione, sarai nella tua dashboard (`dashboard.html`). Qui vedrai un elenco dei tuoi repository GitHub (o del provider selezionato).
4.  **Genera documentazione:**
    *   Seleziona un repository dall'elenco.
    *   Scegli il tipo di documentazione che desideri generare (es. `README`, `API Docs`, `Changelog`).
    *   Potresti dover specificare un branch o un percorso file a seconda del tipo di documentazione.
    *   Clicca sul pulsante "Genera". La documentazione verrà processata dall'AI.
    *   Una volta pronta, la documentazione apparirà in un modal. Puoi copiarla, scaricarla o, per i piani Pro/Team, fare il push direttamente nel repository.
5.  **Storico:** Nella pagina `history.html` puoi visualizzare tutte le documentazioni generate in precedenza.
6.  **Gestione Piani:** Dalla dashboard, potrai visualizzare il tuo piano attuale e opzioni per l'upgrade (se configurato con Stripe).

### Esempio di utilizzo (Generazione README)

Supponiamo che tu abbia un repository chiamato `my-awesome-project` su GitHub.

1.  Accedi a ReadyGen.
2.  Nella dashboard, trova e clicca su `my-awesome-project`.
3.  Clicca sul pulsante "README".
4.  Attendi che l'AI elabori il codice del tuo repository.
5.  Una volta completato, si aprirà un modal con il testo del tuo nuovo `README.md`.
6.  Clicca su "Copia" per copiarlo negli appunti, o "Scarica" per salvarlo come file. Se sei un utente Pro, puoi anche cliccare su "Push nel repo" per aggiornare direttamente il file `README.md` sul tuo repository.

## Struttura delle cartelle

```
.
├── .gitignore                      # File ignorati da Git
├── backend                         # Codice del server (FastAPI)
│   ├── .env.example                # Esempio di variabili d'ambiente
│   ├── .gitignore                  # File ignorati da Git nel backend
│   ├── .idea/                      # File di configurazione di IDE (es. PyCharm)
│   ├── Procfile                    # Configurazione per deployment su piattaforme come Heroku
│   ├── db/                         # Moduli per l'interazione con il database Supabase
│   │   └── supabase.py
│   ├── main.py                     # Punto di ingresso dell'applicazione FastAPI
│   ├── models/                     # Definizioni Pydantic per i modelli di dati
│   │   └── schemas.py
│   ├── railway.json                # Configurazione per il deployment su Railway.app
│   ├── requirements.txt            # Dipendenze Python del backend
│   ├── routes/                     # Endpoint API dell'applicazione
│   │   ├── auth.py                 # Rotte per l'autenticazione (OAuth)
│   │   ├── docs.py                 # Rotte per la generazione e gestione delle documentazioni
│   │   └── payments.py             # Rotte per la gestione dei pagamenti (Stripe)
│   ├── runtime.txt                 # Specifica della versione di Python
│   ├── services/                   # Logica di business e integrazioni esterne
│   │   ├── ai.py                   # Integrazione con servizi AI (es. OpenAI/Gemini)
│   │   ├── email.py                # Servizio di invio email (Resend)
│   │   ├── git/                    # Implementazioni dei provider Git
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Interfaccia astratta per i provider Git
│   │   │   ├── bitbucket.py        # Implementazione per Bitbucket
│   │   │   ├── github.py           # Implementazione per GitHub
│   │   │   └── gitlab.py           # Implementazione per GitLab
│   │   └── github.py               # (Compatibilità) Shim per il vecchio modulo GitHub
│   │   └── provider_factory.py     # Factory per scegliere il provider Git corretto
├── context.md                      # Potenziale documentazione aggiuntiva sul contesto del progetto
├── frontend                        # Codice del client web (HTML, CSS, JS)
│   ├── css/                        # Fogli di stile CSS
│   │   └── style.css
│   ├── dashboard.html              # Pagina della dashboard utente
│   ├── history.html                # Pagina per lo storico delle documentazioni generate
│   ├── images/                     # Immagini e media per il frontend
│   │   ├── AbbonamentoSingoloSito.png
│   │   ├── AbbonamentoTeamSito.png
│   │   └── demo_web.mp4
│   ├── index.html                  # Pagina principale / di atterraggio
│   ├── js/                         # Script JavaScript del frontend
│   │   ├── auth.js                 # Funzionalità di autenticazione e gestione token
│   │   ├── dashboard.js            # Logica specifica della dashboard
│   │   ├── history.js              # Logica specifica dello storico
│   │   └── i18n.js                 # Gestione della localizzazione (traduzioni)
│   ├── netlify.toml                # Configurazione per il deployment su Netlify
│   └── serve.json                  # Configurazione per il server HTTP locale `npx serve`
├── start.sh                        # Script per avviare l'intero stack localmente (solo macOS)
├── supabase_migration_v2_multiprovider.sql # Script di migrazione Supabase per multi-provider
├── supabase_migration_v3_payments.sql      # Script di migrazione Supabase per pagamenti
└── supabase_schema.sql             # Schema iniziale del database Supabase
```

## Licenza

Sebbene non sia specificata esplicitamente una licenza nel file `README.md` o in un file `LICENSE` dedicato, il progetto sembra essere di natura proprietaria dato l'uso del nome `ReadyGen` come brand, piani di abbonamento e integrazione con servizi di pagamento. In assenza di una licenza esplicita, tutti i diritti sono riservati all'autore (`paulnatan`).