# DocPilot — Contesto del progetto

Micro SaaS per la **generazione automatica di documentazione tecnica** da repository Git.
Sviluppatore: Paolo Natan — `p.natan23@gmail.com`
Cartella progetto: `/Users/paulblack/Desktop/Development/DocPilot`
Avviato: 04/06/2026

> ⚠️ Il nome "DocPilot" è temporaneo — esiste già `docpilot.dev` (prodotto diverso ma stesso nome). Da scegliere un nuovo nome.

---

## 1. Idea

Problema reale vissuto internamente: nei team di sviluppo la documentazione tecnica è sempre disorganizzata o assente.
Il tool si connette al repository (GitHub, GitLab, Bitbucket), legge il codice ad ogni commit e genera automaticamente tutta la documentazione tecnica con AI.

> "I developer odiano scrivere documentazione. DocPilot la scrive al posto loro."

---

## 2. Target

- **Primario**: piccole e medie aziende con team di sviluppo
- **Secondario**: freelance e startup piccole
- Mercato trasversale — chiunque abbia un repository con documentazione da mantenere

---

## 3. Stato attuale — LIVE ✅

### URL produzione
| Componente | URL |
|---|---|
| Frontend | https://docpilot-app.netlify.app |
| Backend | https://docpilot-production-ff6b.up.railway.app |
| Repository | https://github.com/paulnatan/docpilot |
| Database | Supabase — https://cmpoemzdiiuebwdxludz.supabase.co |

### Stack tecnico
```
Backend     → Python + FastAPI (Railway)
Frontend    → HTML + CSS + JS vanilla (Netlify)
AI          → Groq API (llama-3.3-70b-versatile) — free tier
              → Migrazione a Claude API pianificata
Database    → Supabase (PostgreSQL)
Webhook     → n8n (self-hosted Docker locale — da migrare in cloud)
Auth        → OAuth: GitHub / GitLab / Bitbucket
Pagamenti   → Stripe (da implementare)
```

---

## 4. Funzionalità implementate ✅

| Funzionalità | Stato |
|---|---|
| GitHub OAuth | ✅ |
| GitLab OAuth | ✅ (configurare credenziali) |
| Bitbucket OAuth | ✅ (configurare credenziali) |
| Generazione README | ✅ |
| Generazione API Docs | ✅ |
| Generazione Changelog | ✅ |
| Commenti inline AI | ✅ |
| Project Overview (architettura) | ✅ |
| Push documentazione nel repo | ✅ |
| Webhook automatico su push | ✅ |
| Storico documentazioni | ✅ |
| Chunking per repo grandi | ✅ |
| Multi-lingua UI | ✅ IT, EN, ES, FR, DE |
| Multi-lingua documentazione AI | ✅ IT, EN, ES, FR, DE |
| Landing page professionale | ✅ |
| Provider abstraction layer | ✅ |

---

## 5. Funzionalità da implementare 🔜

### Priorità alta
| Funzionalità | Difficoltà | Tempo stimato | Note |
|---|---|---|---|
| **SDK Generation** | ⭐⭐ Facile | 2-3h | AI genera codice client JS/Python/Swift per chiamare le API |
| **Swagger/OpenAPI export** | ⭐⭐ Facile | 2-3h | Genera file openapi.json/swagger.yaml dal codice |
| **Stripe pagamenti** | ⭐⭐⭐ Medio | 4-6h | Piano Pro €19/mese, Team €49/mese |
| **Email notifiche** | ⭐⭐ Facile | 2h | Avvisa utente quando doc è pronta |

### Priorità media
| Funzionalità | Difficoltà | Tempo stimato | Note |
|---|---|---|---|
| **Mock Server** | ⭐⭐⭐ Medio | 4-6h | Server simulato per testare API senza backend |
| **Dominio custom** | ⭐ Triviale | 30min | docpilot.io o nome da scegliere (~€12/anno) |
| **Migrazione Claude API** | ⭐⭐ Facile | 1h | Aumentare CHUNK_TOKEN_LIMIT da 8.000 a 50.000+ |
| **n8n cloud** | ⭐⭐ Facile | 2h | Migrare n8n da locale a cloud per webhook stabili |
| **GitLab credenziali** | ⭐ Triviale | 30min | Creare OAuth app su gitlab.com |
| **Bitbucket credenziali** | ⭐ Triviale | 30min | Creare OAuth app su bitbucket.org |

### Priorità bassa (Fase 2)
| Funzionalità | Note |
|---|---|
| QA Assistant | Genera test cases, traccia bug |
| Azure DevOps | Quarto provider Git |
| Team multi-utente | Dashboard condivisa per team |

---

## 6. Modello di business

| Piano | Prezzo | Cosa include |
|---|---|---|
| Free | €0 | 1 repo, documentazione base, storico 7 giorni |
| Pro | €19/mese | Repo illimitati, tutti i tipi di doc, push automatico, storico illimitato |
| Team | €49/mese | Multi utente, priorità, SLA garantito |

Break-even con soli **5 clienti Pro** (5 × €19 = €95 - €20 costi = €75 profitto).

---

## 7. Costi operativi

| Voce | Costo mensile |
|---|---|
| Railway (backend) | €0 → €5-10 con crescita |
| Netlify (frontend) | €0 |
| Supabase (database) | €0 → €25 con crescita |
| Groq API (AI) | €0 free tier → migrazione Claude |
| Dominio | ~€1/mese |
| Stripe | 2.9% + €0.30 per transazione |
| **Totale MVP** | **€0-5/mese** |

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
Step 1: Scegliere nuovo nome e dominio
Step 2: Product Hunt launch (martedì/mercoledì 00:01 PST)
Step 3: Reddit — r/webdev, r/programming, r/SideProject
Step 4: Hacker News — Show HN
Step 5: Twitter/X + LinkedIn thread #buildinpublic
Step 6: Articolo tecnico su Dev.to / Hashnode
Step 7: GitHub Marketplace + GitLab Marketplace
```

---

## 10. Note tecniche importanti

- **Chunking AI**: `CHUNK_TOKEN_LIMIT = 8000` (limite Groq free). Da alzare a 50.000+ con Claude API
- **n8n webhook**: gira in Docker locale — ogni riavvio cambia URL Cloudflare tunnel. Da migrare in cloud
- **GITHUB_REDIRECT_URI**: `https://docpilot-production-ff6b.up.railway.app/auth/callback/github`
- **Railway PORT**: il server gira su porta 8080 (assegnata da Railway via $PORT)
- **Supabase migration v2**: eseguita — aggiunge colonne `provider`, `gitlab_id`, `bitbucket_id`

---

## 11. ⚠️ Da fare subito — NOME

Il nome "DocPilot" è già usato da `docpilot.dev` (prodotto diverso).
Bisogna scegliere un nome nuovo prima del lancio pubblico e del dominio.

Candidati da valutare:
- da definire in sessione brainstorming

