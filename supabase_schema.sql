-- Tabella utenti
create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  github_id bigint unique not null,
  username text not null,
  email text,
  avatar_url text,
  access_token text not null,
  created_at timestamptz default now()
);

-- Tabella documentazioni generate
create table if not exists docs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  repo_name text not null,
  doc_type text not null,  -- 'readme' | 'api_docs' | 'changelog'
  content text not null,
  generated_at timestamptz default now()
);

-- Indici per performance
create index if not exists docs_user_id_idx on docs(user_id);
create index if not exists docs_generated_at_idx on docs(generated_at desc);
