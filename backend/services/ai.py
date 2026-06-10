from openai import OpenAI
import os

# Gemini 2.0 Flash: contesto fino a ~1M token, limiti per-minuto molto più ampi
# rispetto a Groq free tier. Manteniamo comunque il chunking come rete di
# sicurezza per repository molto grandi, ma con soglie molto più alte.
CHUNK_TOKEN_LIMIT = 100000
# Stima conservativa: 1 token ≈ 4 caratteri
CHARS_PER_TOKEN = 4
CHUNK_SIZE_CHARS = CHUNK_TOKEN_LIMIT * CHARS_PER_TOKEN  # ~400.000 caratteri per chunk

PROMPTS = {
    "readme": """Sei un esperto di documentazione tecnica. Analizza il seguente codice/struttura di un repository GitHub e genera un README.md completo e professionale.

Il README deve includere:
- Nome e descrizione del progetto
- Funzionalità principali
- Requisiti e dipendenze
- Istruzioni di installazione
- Come usare il progetto (con esempi)
- Struttura delle cartelle
- Licenza (se deducibile)

Usa Markdown. Sii chiaro e conciso.

Repository: {repo_name}
Struttura file:
{file_tree}

Contenuto file principali:
{file_contents}
""",

    "readme_chunk": """Sei un esperto di documentazione tecnica. Stai analizzando una PARTE di un repository GitHub (chunk {chunk_num} di {total_chunks}).

Estrai e documenta solo quello che trovi in questo chunk:
- Funzionalità e moduli presenti
- Dipendenze rilevate
- Pattern architetturali rilevati

Repository: {repo_name}
Chunk {chunk_num}/{total_chunks}:
{file_contents}
""",

    "readme_merge": """Sei un esperto di documentazione tecnica. Hai analizzato un repository GitHub in {total_chunks} parti.
Di seguito hai le analisi parziali di ogni parte. Combinale in un unico README.md completo e professionale.

Il README deve includere:
- Nome e descrizione del progetto
- Funzionalità principali
- Requisiti e dipendenze
- Istruzioni di installazione
- Come usare il progetto (con esempi)
- Struttura delle cartelle

Repository: {repo_name}
Struttura file:
{file_tree}

Analisi parziali:
{partial_docs}
""",

    "api_docs": """Sei un esperto di documentazione API. Analizza il codice seguente e genera una documentazione API completa.

Per ogni endpoint trovato documenta:
- Metodo HTTP e path
- Descrizione
- Parametri (query, body, path)
- Risposta (schema + esempio)
- Codici di errore

Usa formato Markdown con esempi pratici.

Repository: {repo_name}
Codice:
{file_contents}
""",

    "api_docs_chunk": """Sei un esperto di documentazione API. Stai analizzando la PARTE {chunk_num} di {total_chunks} di un repository.

Estrai da questo chunk TUTTI gli endpoint API trovati:
- Metodo HTTP e path
- Descrizione
- Parametri (query, body, path)
- Risposta (schema + esempio)
- Codici di errore

Sii preciso e tecnico. Questo sarà usato per costruire una documentazione API completa.

Repository: {repo_name}
Chunk {chunk_num}/{total_chunks}:
{file_contents}
""",

    "api_docs_merge": """Sei un esperto di documentazione API. Hai analizzato il repository {repo_name} in {total_chunks} parti.

Combina tutte le analisi parziali in un'unica documentazione API completa in Markdown.

Per ogni endpoint trovato nelle analisi parziali documenta:
- Metodo HTTP e path
- Descrizione
- Parametri (query, body, path)
- Risposta (schema + esempio)
- Codici di errore

Repository: {repo_name}
Analisi parziali:
{partial_docs}
""",

    "changelog": """Sei un esperto di release management. Analizza i seguenti commit Git e genera un CHANGELOG.md professionale.

Raggruppa i cambiamenti per tipo:
- ✨ Nuove funzionalità
- 🐛 Bug fix
- 🔧 Miglioramenti
- 💥 Breaking changes
- 📦 Dipendenze

Usa formato Keep a Changelog (https://keepachangelog.com).

Repository: {repo_name}
Commit recenti:
{commits}
""",

    "overview": """Sei un senior software architect con 15 anni di esperienza. Analizza questo repository GitHub e produci un documento tecnico DETTAGLIATO e COMPLETO. Non essere generico — ogni sezione deve contenere dettagli specifici estratti dal codice reale.

REGOLE FONDAMENTALI:
- Cita nomi reali di classi, funzioni, file e variabili trovati nel codice
- Includi snippet di codice significativi dove utile
- Spiega il PERCHÉ delle scelte architetturali, non solo il COSA
- Ogni sezione deve essere sostanziosa (almeno 3-5 punti dettagliati)
- Scrivi come se stessi facendo onboarding a un senior developer

# 📋 Project Overview — {repo_name}

## 1. 🎯 Cos'è questo progetto
- Problema specifico che risolve
- Target utente
- Valore principale offerto
- Contesto d'uso

## 2. 🏛️ Architettura generale
- Pattern architetturale principale (con motivazione)
- Come sono separati i layer (UI, business logic, data)
- Principi di design seguiti
- Diagramma testuale del flusso generale

## 3. 📁 Struttura del progetto
Per ogni cartella/modulo principale:
- Scopo esatto
- File chiave al suo interno
- Responsabilità e confini

## 4. ⚙️ Componenti principali
Per ogni componente rilevante trovato nel codice:
- Nome esatto della classe/modulo
- Responsabilità specifica
- Metodi/funzioni più importanti (con firma)
- Dipendenze con altri componenti
- Esempio d'uso se rilevante

## 5. 🔄 Flussi principali
Descrivi passo per passo i flussi più importanti con riferimenti al codice:
- Flusso di avvio dell'applicazione
- Flusso principale dell'utente
- Gestione degli errori
- Flusso dei dati (input → elaborazione → output)

## 6. 🛠️ Stack tecnologico
Per ogni dipendenza trovata:
- Nome e versione (se disponibile)
- Perché è stata scelta
- Come viene usata nel progetto
- Alternative possibili

## 7. 🎨 Pattern e decisioni tecniche
- Design pattern specifici trovati nel codice (con esempi)
- Convenzioni di naming usate
- Gestione dello stato
- Gestione degli errori e dei casi limite
- Scelte di performance rilevate

## 8. ⚠️ Punti di attenzione
- Aree di debito tecnico specifiche (con riferimento ai file)
- Codice che potrebbe causare problemi
- Miglioramenti architetturali suggeriti
- Test coverage rilevata
- Sicurezza: punti critici identificati

## 9. 🚀 Come iniziare (per un nuovo developer)
- Prerequisiti specifici
- Passi per il setup locale
- File di configurazione da modificare
- Come testare che tutto funzioni

Repository: {repo_name}
Struttura completa file:
{file_tree}

Codice sorgente analizzato:
{file_contents}
""",

    "overview_chunk": """Sei un senior software architect. Stai analizzando la PARTE {chunk_num} di {total_chunks} di un repository GitHub.

Estrai da questo chunk tutte le informazioni tecniche rilevanti:
- Componenti/classi/funzioni principali trovati
- Pattern architetturali rilevati
- Dipendenze e librerie usate
- Logica di business rilevante
- Flussi di dati identificati

Sii tecnico e preciso. Questo sarà usato per costruire un documento finale completo.

Repository: {repo_name}
Chunk {chunk_num}/{total_chunks}:
{file_contents}
""",

    "overview_merge": """Sei un senior software architect. Hai analizzato il repository {repo_name} in {total_chunks} parti.

Combina le analisi parziali in un documento tecnico DEFINITIVO, DETTAGLIATO e COERENTE. Cita nomi reali di classi, funzioni e file trovati nel codice. Non essere generico.

Il documento deve includere tutte queste sezioni con contenuto ricco e specifico:

# 📋 Project Overview — {repo_name}

## 1. 🎯 Cos'è questo progetto
## 2. 🏛️ Architettura generale
## 3. 📁 Struttura del progetto
## 4. ⚙️ Componenti principali (con nomi reali dal codice)
## 5. 🔄 Flussi principali (passo per passo)
## 6. 🛠️ Stack tecnologico (con motivazioni)
## 7. 🎨 Pattern e decisioni tecniche
## 8. ⚠️ Punti di attenzione (specifici)
## 9. 🚀 Come iniziare

Struttura file del progetto:
{file_tree}

Analisi parziali da unire:
{partial_docs}

Crea un documento definitivo professionale. Ogni sezione deve avere almeno 4-6 punti dettagliati.
""",

    "openapi_chunk": """Sei un esperto di API design. Stai analizzando la PARTE {chunk_num} di {total_chunks} di un repository.

Estrai da questo chunk TUTTI gli endpoint API trovati:
- Metodo HTTP e path
- Parametri (query, path, body)
- Schema di risposta
- Eventuali modelli di dati (classi, interfacce, tipi)

Sii preciso e tecnico. Questo sarà usato per costruire una specifica OpenAPI completa.

Repository: {repo_name}
Chunk {chunk_num}/{total_chunks}:
{file_contents}
""",

    "openapi_merge": """Sei un esperto di API design. Hai analizzato il repository {repo_name} in {total_chunks} parti.

Combina tutte le analisi parziali in una specifica OpenAPI 3.0 COMPLETA e VALIDA in formato YAML.

La specifica deve includere:
- info (title, version, description)
- servers
- paths con TUTTI gli endpoint trovati nelle analisi parziali
- Per ogni endpoint: summary, description, parameters, requestBody, responses con schema
- components/schemas per tutti i modelli di dati trovati

Restituisci SOLO il YAML valido, senza spiegazioni o markdown code block.

Repository: {repo_name}
Analisi parziali:
{partial_docs}
""",

    "sdk_chunk": """Sei un esperto sviluppatore. Stai analizzando la PARTE {chunk_num} di {total_chunks} di un repository.

Estrai da questo chunk:
- Tutti gli endpoint API (metodo, path, parametri, risposta)
- Modelli di dati / interfacce rilevanti
- Logica di autenticazione se presente

Sii preciso. Questo sarà usato per generare un SDK client completo.

Repository: {repo_name}
Chunk {chunk_num}/{total_chunks}:
{file_contents}
""",

    "sdk_merge": """Sei un esperto sviluppatore. Hai analizzato il repository {repo_name} in {total_chunks} parti.

Genera un SDK client COMPLETO in JavaScript/TypeScript e Python basandoti su tutte le analisi parziali.

Per ogni linguaggio:
1. Classe client con TUTTI i metodi per ogni endpoint trovato
2. Tipi/interfacce TypeScript per tutti i modelli di dati
3. Gestione degli errori
4. Esempi d'uso per ogni metodo

## JavaScript/TypeScript SDK
```typescript
// codice completo
```

## Python SDK
```python
# codice completo
```

## Esempi d'uso
```typescript
// esempi JS
```
```python
# esempi Python
```

Repository: {repo_name}
Analisi parziali:
{partial_docs}
""",

    "openapi": """Sei un esperto di API design. Analizza il codice seguente e genera una specifica OpenAPI 3.0 completa in formato YAML.

La specifica deve includere:
- info (title, version, description)
- servers
- paths con tutti gli endpoint trovati nel codice
- Per ogni endpoint: summary, description, parameters, requestBody, responses con schema
- components/schemas per i modelli di dati trovati
- security schemes se presenti

Restituisci SOLO il YAML valido, senza spiegazioni o markdown code block.

Repository: {repo_name}
Codice:
{file_contents}
""",

    "sdk": """Sei un esperto sviluppatore. Analizza il codice seguente e genera un SDK client completo in JavaScript/TypeScript e Python per consumare le API trovate.

Per ogni linguaggio genera:
1. Una classe client con tutti i metodi corrispondenti agli endpoint API trovati
2. Tipi/interfacce TypeScript per i modelli di dati
3. Gestione degli errori
4. Esempi d'uso per ogni metodo

Formato output:
## JavaScript/TypeScript SDK
```typescript
// codice qui
```

## Python SDK
```python
# codice qui
```

## Esempi d'uso
```typescript
// esempi JS
```
```python
# esempi Python
```

Repository: {repo_name}
Codice API:
{file_contents}
""",

    "comments": """Sei un esperto sviluppatore software. Il tuo compito è aggiungere commenti inline chiari e utili al codice seguente.

Regole:
- Aggiungi commenti sopra ogni funzione/metodo spiegando cosa fa, i parametri e il valore di ritorno
- Aggiungi commenti inline per blocchi di logica complessa
- Aggiungi commenti sopra ogni classe spiegando il suo scopo
- NON modificare il codice, aggiungi SOLO commenti
- Usa la stessa lingua del codice (se ha commenti in italiano, scrivi in italiano, altrimenti in inglese)
- Mantieni i commenti concisi e informativi
- Restituisci SOLO il codice commentato, senza spiegazioni aggiuntive

Repository: {repo_name}
File: {file_path}

Codice da commentare:
{file_contents}
""",
}


# Catena di fallback: se il primo modello/provider è sovraccarico (503) o ha
# esaurito la quota (429), si passa al successivo. Gemini Flash → Gemini Flash
# Lite (più leggero, meno soggetto a sovraccarico) → Groq come ultima spiaggia.
FALLBACK_CHAIN = [
    {"provider": "gemini", "model": "gemini-2.5-flash"},
    {"provider": "gemini", "model": "gemini-2.5-flash-lite"},
    {"provider": "groq", "model": "llama-3.3-70b-versatile"},
]

PROVIDER_CONFIG = {
    "gemini": {
        "api_key_env": "GEMINI_API_KEY",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
    },
    "groq": {
        "api_key_env": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
    },
}

_clients: dict[str, OpenAI] = {}


def _get_client_for(provider: str) -> OpenAI | None:
    if provider not in _clients:
        config = PROVIDER_CONFIG[provider]
        api_key = os.getenv(config["api_key_env"])
        if not api_key:
            return None
        _clients[provider] = OpenAI(api_key=api_key, base_url=config["base_url"])
    return _clients[provider]


def _call_model(prompt: str, max_tokens: int = 8000) -> str:
    import time
    from openai import APIStatusError

    last_error: Exception | None = None

    for entry in FALLBACK_CHAIN:
        client = _get_client_for(entry["provider"])
        if client is None:
            continue

        # Un solo retry rapido per modello prima di passare al successivo della catena
        for attempt in range(2):
            try:
                response = client.chat.completions.create(
                    model=entry["model"],
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.choices[0].message.content
            except APIStatusError as e:
                last_error = e
                if e.status_code in (429, 503) and attempt == 0:
                    print(f"[AI] {entry['provider']}/{entry['model']} -> {e.status_code}, retry tra 2s")
                    time.sleep(2)
                    continue
                print(f"[AI] {entry['provider']}/{entry['model']} -> {e.status_code}, passo al provider successivo")
                break
            except Exception as e:
                last_error = e
                print(f"[AI] {entry['provider']}/{entry['model']} -> errore inatteso: {e}, passo al provider successivo")
                break

    if last_error:
        raise last_error
    raise RuntimeError("Nessun provider AI configurato (GEMINI_API_KEY / GROQ_API_KEY mancanti)")


def _split_into_chunks(text: str) -> list[str]:
    """Divide il testo in chunks da CHUNK_SIZE_CHARS caratteri."""
    chunks = []
    while len(text) > CHUNK_SIZE_CHARS:
        # Taglia al prossimo separatore di file (###) per non spezzare file a metà
        cut = text.rfind("###", 0, CHUNK_SIZE_CHARS)
        if cut == -1:
            cut = CHUNK_SIZE_CHARS
        chunks.append(text[:cut])
        text = text[cut:]
    if text:
        chunks.append(text)
    return chunks


LANG_INSTRUCTIONS = {
    "it": "ISTRUZIONE OBBLIGATORIA: Scrivi TUTTO il documento in italiano. Non usare altre lingue.",
    "en": "MANDATORY INSTRUCTION: Write the ENTIRE document in English. Do not use any other language.",
    "fr": "INSTRUCTION OBLIGATOIRE: Écrivez TOUT le document en français. N'utilisez pas d'autres langues.",
    "de": "PFLICHTANWEISUNG: Schreibe das GESAMTE Dokument auf Deutsch. Verwende keine andere Sprache.",
    "es": "INSTRUCCIÓN OBLIGATORIA: Escribe TODO el documento en español. No uses ningún otro idioma.",
}

def generate_doc(doc_type: str, repo_name: str, file_tree: str = "", file_contents: str = "", commits: str = "", file_path: str = "", lang: str = "it") -> str:

    lang_instruction = LANG_INSTRUCTIONS.get(lang, LANG_INSTRUCTIONS["it"])

    # Per doc type che supportano chunking → chunking automatico se il contenuto è grande
    if doc_type in ("readme", "overview", "openapi", "sdk", "api_docs") and len(file_contents) > CHUNK_SIZE_CHARS:
        return _generate_with_chunks(repo_name, file_tree, file_contents, doc_type, lang_instruction)

    prompt_template = PROMPTS.get(doc_type)
    if not prompt_template:
        raise ValueError(f"doc_type non supportato: {doc_type}")

    prompt = (
        lang_instruction + "\n\n" +
        prompt_template.format(
            repo_name=repo_name,
            file_tree=file_tree,
            file_contents=file_contents,
            commits=commits,
            file_path=file_path,
        ) +
        "\n\n" + lang_instruction
    )

    return _call_model(prompt)


def _generate_with_chunks(repo_name: str, file_tree: str, file_contents: str, doc_type: str = "readme", lang_instruction: str = "") -> str:
    """Genera documentazione dividendo il contenuto in chunks e poi unendo i risultati."""
    chunks = _split_into_chunks(file_contents)
    total = len(chunks)

    chunk_prompt_key = f"{doc_type}_chunk"
    merge_prompt_key = f"{doc_type}_merge"

    print(f"[CHUNKING] {repo_name} ({doc_type}): {total} chunks da ~{CHUNK_SIZE_CHARS} chars")

    # Analizza ogni chunk
    partial_docs = []
    for i, chunk in enumerate(chunks, 1):
        chunk_body = PROMPTS[chunk_prompt_key].format(
            repo_name=repo_name,
            chunk_num=i,
            total_chunks=total,
            file_contents=chunk,
        )
        chunk_prompt = lang_instruction + "\n\n" + chunk_body + "\n\n" + lang_instruction
        partial = _call_model(chunk_prompt, max_tokens=4000)
        partial_docs.append(f"--- Chunk {i}/{total} ---\n{partial}")
        print(f"[CHUNKING] Chunk {i}/{total} completato")

    # Unisci tutto nel documento finale
    merge_body = PROMPTS[merge_prompt_key].format(
        repo_name=repo_name,
        total_chunks=total,
        file_tree=file_tree,
        partial_docs="\n\n".join(partial_docs),
    )
    merge_prompt = lang_instruction + "\n\n" + merge_body + "\n\n" + lang_instruction

    return _call_model(merge_prompt, max_tokens=8000)
