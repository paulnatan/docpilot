-- ReadyGen — Migration v3: Payments & Plans
-- Esegui questo script nel Supabase SQL Editor

-- Aggiunge colonne per piano e Stripe all'utente
ALTER TABLE users ADD COLUMN IF NOT EXISTS plan VARCHAR(20) NOT NULL DEFAULT 'free';
ALTER TABLE users ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(100) UNIQUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS stripe_subscription_id VARCHAR(100) UNIQUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(255);

-- Aggiunge colonne per i limiti piano
-- free: max 1 repo, pro: illimitato, team: illimitato multi-user
COMMENT ON COLUMN users.plan IS 'free | pro | team';
