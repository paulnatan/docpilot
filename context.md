# DocPilot — Contesto del progetto

Micro SaaS per la **generazione automatica di documentazione tecnica** collegato a GitHub (poi GitLab e Bitbucket).
Sviluppatore: Paolo — full stack, linguaggi principali Python e n8n.

---

## 1. Idea

Problema reale vissuto internamente: nei team di sviluppo la documentazione tecnica è sempre disorganizzata o assente.
DocPilot si connette al repository GitHub, legge il codice ad ogni commit/PR e genera automaticamente tutta la documentazione tecnica con AI.

> "I developer odiano scrivere documentazione. DocPilot la scrive al posto loro."

---

## 2. Target

- **Primario**: piccole e medie aziende con team di sviluppo
- **Secondario**: freelance e startup piccole
- Mercato trasversale — chiunque abbia un repository GitHub con documentazione da mantenere

---

## 3. Funzionalità core (Fase 1)

| Cosa genera | Dettaglio |
|---|---|
| README | Struttura progetto, setup, dipendenze |
| Docs API | Endpoint, parametri, esempi automatici |
| Commenti codice | Inline, generati con AI |
| Changelog | Da ogni commit/PR automaticamente |

---

## 4. Roadmap

```
Fase 1 (ora)         → GitHub + documentazione automatica (DocPilot core)
Fase 2 (6-12 mesi)  → Modulo QA Assistant (genera test cases, traccia bug)
Risultato finale     → Tool completo per la qualità del software nei team dev di PMI
```

### Timeline di sviluppo

```
Settimana 1  → Setup progetto + integrazione GitHub OAuth
Settimana 2  → Connessione Claude/OpenAI API + generazione README
Settimana 3  → UI base + primo test su repo reale
Settimana 4  → Aggiustamenti + beta privata (uso interno + colleghi)

Mese 2       → Aggiungi API docs e changelog automatico
Mese 3       → Stripe attivo + lancio pubblico
```

---

## 5. Stack tecnico

```
Backend     →  Python (Flask o FastAPI)
Webhook     →  n8n (gestisce webhook GitHub)
AI          →  Claude API (Anthropic) o OpenAI API
GitHub API  →  OAuth + Webhook via n8n
Database    →  Supabase (free tier generoso)
Frontend    →  HTML + CSS + JS vanilla
Pagamenti   →  Stripe
Deploy      →  Railway o Render (free tier per iniziare)
```

### Flusso principale

```
GitHub push commit
      ↓
n8n riceve il webhook
      ↓
n8n manda il codice al backend Python
      ↓
Python chiama Claude/OpenAI API → genera documentazione
      ↓
Salva su Supabase + mostra all'utente nella UI
```

---

## 6. Modello di business

| Piano | Prezzo | Cosa include |
|---|---|---|
| Free | €0 | 1 repo, documentazione base |
| Pro | €19/mese | Repo illimitati + tutto |
| Team | €49/mese | Multi utente + priorità |

---

## 7. Costi operativi stimati

| Voce | Costo mensile |
|---|---|
| Hosting (Railway/Render) | €0 → €5-10 con crescita |
| Supabase | €0 → €25 con crescita |
| Claude/OpenAI API | €10-30 con pochi utenti |
| Dominio | ~€1/mese (€10-15/anno) |
| n8n (self-hosted) | €0 |
| Stripe | 2.9% + €0.30 per transazione |
| **Totale MVP** | **€10-20/mese** |

Break-even con soli **5 clienti Pro** (5 × €19 = €95 - €20 costi = €75 profitto).

---

## 8. Integrazioni previste

- **Fase 1**: GitHub
- **Fase 2**: GitLab
- **Fase 3**: Bitbucket

---

## 9. Cose da fare — prossimi passi

- [ ] Creare account GitHub OAuth App per autenticazione
- [ ] Setup progetto Python (Flask o FastAPI)
- [ ] Configurare n8n per ricevere webhook GitHub
- [ ] Prima chiamata API Claude/OpenAI → generare README da un repo di test
- [ ] UI base per visualizzare la documentazione generata
- [ ] Setup Supabase per salvare i dati
- [ ] Deploy su Railway/Render
- [ ] Beta privata con uso interno

---

## 10. Account / accesso

- Sviluppatore: `p.natan23@gmail.com`
- Cartella progetto: `/Users/paulblack/Desktop/Development/DocPilot`

---

## 11. Note

- Paolo è il primo utilizzatore — il problema è reale e vissuto in prima persona nel suo team
- Il progetto è stato ideato il 04/06/2026 in una sessione di brainstorming Micro SaaS
- La Fase 2 (QA Assistant) è già pianificata come modulo aggiuntivo dello stesso prodotto
