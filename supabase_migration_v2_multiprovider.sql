-- DocPilot v2 — Migrazione Multi-Provider
-- Esegui questo script nella Supabase SQL Editor: https://supabase.com/dashboard/project/cmpoemzdiiuebwdxludz/sql

-- 1. Aggiungi colonna provider alla tabella users (default 'github' per utenti esistenti)
ALTER TABLE users
  ADD COLUMN IF NOT EXISTS provider VARCHAR(20) NOT NULL DEFAULT 'github';

-- 2. Aggiungi ID provider per GitLab e Bitbucket
ALTER TABLE users
  ADD COLUMN IF NOT EXISTS gitlab_id BIGINT UNIQUE;

ALTER TABLE users
  ADD COLUMN IF NOT EXISTS bitbucket_id VARCHAR(100) UNIQUE;

-- 3. Aggiungi colonna provider alla tabella docs (traccia da quale piattaforma viene)
ALTER TABLE docs
  ADD COLUMN IF NOT EXISTS provider VARCHAR(20) DEFAULT 'github';

-- 4. Indici per performance
CREATE INDEX IF NOT EXISTS idx_users_gitlab_id ON users(gitlab_id) WHERE gitlab_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_users_bitbucket_id ON users(bitbucket_id) WHERE bitbucket_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_users_provider ON users(provider);
CREATE INDEX IF NOT EXISTS idx_docs_provider ON docs(provider);

-- Verifica risultato
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;
