# ReadyGen — Contesto del progetto

Micro SaaS per la **generazione automatica di documentazione tecnica** da repository Git.
Sviluppatore: Paolo Natan — `p.natan23@gmail.com`
Cartella progetto: `/Users/paulblack/Desktop/Development/DocPilot`
Avviato: 04/06/2026
Ultimo aggiornamento: 10/06/2026 — alla vigilia del lancio pubblico

> ✅ Nome definitivo: **ReadyGen** — dominio `readygen.eu` scelto dall'utente.
> Da acquistare prima del lancio pubblico (~€10/anno su Namecheap o Cloudflare).

---

## 1. Idea

Problema reale vissuto internamente: nei team di sviluppo la documentazione tecnica è sempre disorganizzata o assente.
Il tool si connette al repository (GitHub, GitLab, Bitbucket), legge il codice ad ogni commit e genera automaticamente tutta la documentazione tecnica con AI.

> "I developer odiano scrivere documentazione. ReadyGen la scrive al posto loro."

---

## 2. Target

- **Primario**: piccole e medie aziende con team di sviluppo
- **Secondario**: freelance e startup piccole
- Mercato trasversale — chiunque abbia un repository con documentazione da mantenere

---

## 3. Stato attuale — LIVE ✅ (pronto per il lancio)

### URL produzione
| Componente | URL |
|---|---|
| Frontend | https://readygen-app.netlify.app |
| Backend | https://docpilot-production-ff6b.up.railway.app |
| Repository | https://github.com/paulnatan/docpilot |
| Database | Supabase — https://cmpoemzdiiuebwdxludz.supabase.co |

### Stack tecnico
```
Backend     → Python + FastAPI (Railway)
Frontend    → HTML + CSS + JS vanilla (Netlify)
AI          → Gemini 2.5 Flash (gemini-2.5-flash) via endpoint OpenAI-compatible
              → Sostituisce Groq (esaurito limite 100k token/giorno durante test)
              → Migrazione futura a Claude API quando i volumi giustificano il costo
Database    → Supabase (PostgreSQL)
Webhook     → n8n (self-hosted Docker locale — da migrare in cloud)
Auth        → OAuth: GitHub / GitLab / Bitbucket
Pagamenti   → Stripe — LIVE (Pro €19/mese, Team €49/mese; card, PayPal, SEPA)
```

---

## 4. Funzionalità implementate ✅

| Funzionalità | Stato |
|---|---|
| GitHub OAuth | ✅ |
| GitLab OAuth | ✅ (configurare credenziali reali) |
| Bitbucket OAuth | ✅ (configurare credenziali reali) |
| Generazione README | ✅ |
| Generazione API Docs | ✅ |
| Generazione Changelog | ✅ |
| Commenti inline AI | ✅ |
| Project Overview (architettura) | ✅ |
| Push documentazione nel repo | ✅ |
| Webhook automatico su push | ✅ |
| Storico documentazioni | ✅ |
| Chunking per repo grandi | ✅ (rete di sicurezza, soglie alte con Gemini) |
| Multi-lingua UI | ✅ IT, EN, ES, FR, DE — copertura completa home + dashboard |
| Multi-lingua documentazione AI | ✅ IT, EN, ES, FR, DE |
| Landing page professionale | ✅ |
| Provider abstraction layer | ✅ |
| Rebranding → ReadyGen | ✅ |
| Pagamenti Stripe (Pro/Team) | ✅ card, PayPal, SEPA — checkout funzionante |
| Immagini abbonamenti Pro/Team in pricing | ✅ |
| Sezione demo video in home | ✅ (`images/demo_web.mp4`, 720p, 2.3MB) |
| Selezione file intelligente per repo grandi | ✅ MAX_FILES=60, prioritizzazione, esclusione build/dipendenze |
| Supporto linguaggi esteso | ✅ 33 estensioni (backend, frontend, config/infra) |
| Notice trasparenza beta (limite 60 file) | ✅ in home, sotto Pricing + in Features |
| Elenco linguaggi supportati in home | ✅ in sezione Features |
| Materiali marketing pronti | ✅ Product Hunt, Reddit, LinkedIn, X/Twitter, banner, video demo |

---

## 5. Funzionalità da implementare 🔜

### Priorità alta
| Funzionalità | Difficoltà | Tempo stimato | Note |
|---|---|---|---|
| **Acquisto dominio readygen.eu** | ⭐ Triviale | 15min | ~€10/anno su Namecheap o Cloudflare Registrar |
| **Email notifiche (Resend)** | ⭐⭐ Facile | 30min | Aggiungere `RESEND_API_KEY` e `FROM_EMAIL` su Railway — codice già pronto |
| **Lancio pubblico** | — | — | Materiali pronti in `marketing/` — Product Hunt, Reddit, LinkedIn, X |

### Priorità media
| Funzionalità | Difficoltà | Tempo stimato | Note |
|---|---|---|---|
| **SDK Generation** | ⭐⭐ Facile | 2-3h | AI genera codice client JS/Python/Swift per chiamare le API (già nei prompt, da rifinire) |
| **Swagger/OpenAPI export** | ⭐⭐ Facile | 2-3h | Genera file openapi.json/swagger.yaml dal codice (già nei prompt, da rifinire) |
| **Mock Server** | ⭐⭐⭐ Medio | 4-6h | Server simulato per testare API senza backend |
| **n8n cloud** | ⭐⭐ Facile | 2h | Migrare n8n da locale a cloud per webhook stabili |
| **GitLab credenziali** | ⭐ Triviale | 30min | Creare OAuth app su gitlab.com |
| **Bitbucket credenziali** | ⭐ Triviale | 30min | Creare OAuth app su bitbucket.org |
| **Migrazione Claude API** | ⭐⭐ Facile | 1h | Da valutare dopo il lancio in base ai volumi reali — alzare CHUNK_TOKEN_LIMIT, cambiare client in `ai.py` |

### Priorità bassa (Fase 2)
| Funzionalità | Note |
|---|---|
| QA Assistant | Genera test cases, traccia bug |
| Azure DevOps | Quarto provider Git |
| Team multi-utente | Dashboard condivisa per team |
| Aumento limite file oltre 60 | Da valutare in base a costi/qualità Gemini su repo molto grandi |

---

## 6. Modello di business

| Piano | Prezzo | Cosa include |
|---|---|---|
| Free | €0 | 1 repo, documentazione base, storico 7 giorni |
| Pro | €19/mese | Repo illimitati, tutti i tipi di doc, push automatico, storico illimitato |
| Team | €49/mese | Multi utente, priorità, SLA garantito |

Pagamenti live su Stripe — checkout supporta carta, PayPal e SEPA (Satispay rimosso: non compatibile con subscription mode).

Break-even con soli **5 clienti Pro** (5 × €19 = €95 - €20 costi = €75 profitto).

---

## 7. Costi operativi

| Voce | Costo mensile |
|---|---|
| Railway (backend) | €0 → €5-10 con crescita |
| Netlify (frontend) | €0 |
| Supabase (database) | €0 → €25 con crescita |
| Gemini API (AI) | Pay-as-you-go, gemini-2.5-flash — stimati pochi €/mese a basso volume (~€2-10/mese fino a ~5.000 generazioni/mese) |
| Dominio readygen.eu | ~€1/mese |
| Stripe | 2.9% + €0.30 per transazione |
| **Totale MVP** | **€0-10/mese** in fase beta |

### Roadmap costi AI (per riferimento futuro)
| Provider/modello | Costo blended ~ per milione token | Note |
|---|---|---|
| Groq llama-3.1-8b-instant | ~$0.06 | Scartato — qualità bassa |
| Gemini 2.5 Flash (ATTUALE) | ~$0.30-2.50 (con thinking) | Buon rapporto qualità/prezzo, contesto enorme |
| OpenAI gpt-4o-mini | ~$0.29 | Alternativa simile a Gemini |
| Claude Haiku 4.5 | ~$1.76 | Step intermedio se serve più qualità |
| Claude Sonnet 4.5 | ~$6.60 | Top di gamma — da considerare a progetto avviato |

---

## 8. Concorrenti analizzati

| Prodotto | URL | Differenza |
|---|---|---|
| docpilot.dev | https://www.docpilot.dev | Solo API docs interattive + Swagger. Solo GitHub. Niente README/Changelog/Comments/Overview. |
| Mintlify | mintlify.com | Doc hosting, non generazione AI da codice |
| Swimm | swimm.io | Doc interna team, non generazione automatica |

**Vantaggio competitivo**: unico tool che combina README + API Docs + Changelog + Comments + Overview + SDK su 3 piattaforme Git in 5 lingue.

---

## 9. Marketing — piano lancio

```
Step 1: Acquistare readygen.eu
Step 2: Aggiornare URL Netlify (rinominare sito) e puntare dominio custom
Step 3: Product Hunt launch (martedì/mercoledì 00:01 PST)
Step 4: Reddit — r/webdev, r/programming, r/SideProject
Step 5: Hacker News — Show HN
Step 6: Twitter/X + LinkedIn thread #buildinpublic
Step 7: Articolo tecnico su Dev.to / Hashnode
Step 8: GitHub Marketplace + GitLab Marketplace
```

**Materiali pronti** (in `marketing/`):
- `launch_texts.md` — copy completo per Product Hunt, Reddit (r/webdev, r/SideProject, r/programming), LinkedIn, thread X/Twitter, calendario di lancio (date reali a partire dal 10/06), lista screenshot, script video demo — copy aggiornato a Gemini 2.5 Flash (rimossi riferimenti a Groq/LLaMA)
- `product_hunt_banner.html` + `product_hunt_banner.png` — banner 1270x760px brandizzato ReadyGen, con sezione "30+ languages supported"
- `video/demo_web.mp4` (2.3MB, 720p) e `video/demo_hd.mp4` (9.3MB, 1080p) — generati da `Video.mov` originale (352MB) via ffmpeg
- `screenshots/` — 8 screenshot raw del prodotto live (hero, come funziona, funzionalità, dashboard, output README, pricing free/pro-team, login modal)
- `gallery/` — le stesse 8 immagini ridimensionate a larghezza uniforme 1270px, pronte per la gallery Product Hunt (01_hero → 08_login)

**Calendario di lancio aggiornato** (Product Hunt prima di tutto, LinkedIn per ultimo):
| Data | Azione | Stato |
|---|---|---|
| Mer 10/06 | Screenshot + video demo — materiale pronto | ✅ Fatto |
| Gio 11/06 | Finalizzare/sottomettere bozza listing Product Hunt | ✅ Fatto — lancio programmato (scheduled) per Mar 16/06 00:01 PT / 09:01 CEST |
| Mar 16/06 00:01 PT (09:01 CEST) | 🚀 Lancio Product Hunt + thread X/Twitter + r/webdev | ⏳ Programmato, in attesa |
| Mer 17/06 | Post r/programming | ⏳ Da fare |
| Gio 18/06 | Post r/SideProject | ⏳ Da fare |
| Ven 19/06 | Post LinkedIn (ultimo — recap risultati PH) | ⏳ Da fare |

**Nota**: alla domanda "Vercel Day" durante la submission, scelto "No, but I still want to launch on June 16" (ReadyGen non usa stack Vercel).

**Strategia post-lancio**: validare adozione utenti sul tier AI attuale (Gemini), poi valutare migrazione a Claude API quando i volumi lo giustificano. Dopo ReadyGen, l'obiettivo è "collezionare" più Micro SaaS.

---

## 10. Note tecniche importanti

### AI / generazione documentazione
- **Provider AI attuale**: Gemini 2.5 Flash (`gemini-2.5-flash`), via `https://generativelanguage.googleapis.com/v1beta/openai/`, env var `GEMINI_API_KEY`
- **GEMINI_API_KEY**: impostata in `backend/.env` (locale, gitignored). **DA AGGIUNGERE su Railway** → Settings → Variables → `GEMINI_API_KEY`
- `GROQ_API_KEY` non più usata dal codice, può restare su Railway senza problemi
- **Chunking AI**: `CHUNK_TOKEN_LIMIT = 100000`, `CHARS_PER_TOKEN = 4` (~400.000 char/chunk) — soglie molto alte grazie al contesto ampio di Gemini, scatta solo per repo enormi
- `max_tokens`: 8000 per generazione normale e merge, 4000 per chunk
- **Selezione file** (`backend/routes/docs.py`): `_select_relevant_files()` sceglie fino a `MAX_FILES = 60` file per rilevanza (priorità a main/index/app/server/api/router/routes/config/settings/schema/models), esclude `node_modules/`, `dist/`, `build/`, lock file, ecc. `MAX_CHARS_PER_FILE = 3000`
- **SUPPORTED_EXTENSIONS**: 33 estensioni — Python, JS/TS, Go, Java, Ruby, PHP, C#, C/C++, Rust, Dart, Swift, Kotlin, Scala, Elixir, Lua, R, Perl, Objective-C, Vue, HTML/CSS/SCSS/SASS/LESS, SQL, Shell, YAML, JSON, TOML

### i18n
- `frontend/js/i18n.js`: `TRANSLATIONS` (dashboard, `t()`) e `LANDING` (home, `tl()`), entrambi completi per it/en/fr/de/es
- `applyLandingLang()` in `index.html` traduce TUTTE le sezioni della home (navbar, hero, come funziona, features + lista linguaggi + beta note, confronto, demo, pricing + beta note, footer)
- `applyTranslations()` + `setupPlanUI()` in `dashboard.js` traducono completamente la dashboard incluso banner piano e modal upgrade

### Pagamenti
- `backend/routes/payments.py`: `payment_method_types=["card", "paypal", "sepa_debit"]`
- Satispay rimosso (incompatibile con subscription mode di Stripe)

### Trasparenza beta (home page)
- Box sotto la sezione Pricing: avviso limite 60 file/repo in beta
- Sezione Features: stesso avviso + elenco linguaggi supportati
- Tutto tradotto nelle 5 lingue

### Altri dettagli infrastrutturali
- **n8n webhook**: gira in Docker locale — ogni riavvio cambia URL Cloudflare tunnel. Da migrare in cloud
- **GITHUB_REDIRECT_URI**: `https://docpilot-production-ff6b.up.railway.app/auth/callback/github`
- **Railway PORT**: il server gira su porta 8080 (assegnata da Railway via $PORT)
- **Supabase migration v2**: eseguita — aggiunge colonne `provider`, `gitlab_id`, `bitbucket_id`
- **localStorage keys**: `docpilot_token` e `docpilot_lang` (mantenute per retrocompatibilità — cambiarle comporterebbe logout forzato di tutti gli utenti)

---

## 11. Prossimi passi immediati

1. ⏳ Aggiungere `GEMINI_API_KEY` su Railway (variabile ambiente) — **bloccante per il lancio**
2. ⏳ Test end-to-end generazione doc con Gemini in produzione
3. ⏳ Acquistare dominio readygen.eu e collegarlo a Netlify/Railway
4. ⏳ Configurare Resend per email notifiche (`RESEND_API_KEY`, `FROM_EMAIL`)
5. 🚀 Eseguire il piano di lancio (Product Hunt, Reddit, LinkedIn, X) — materiali pronti
6. 📊 Monitorare adozione utenti e costi Gemini reali nei primi giorni
7. 💡 Dopo il lancio: iniziare a pensare al prossimo Micro SaaS della "collezione"
