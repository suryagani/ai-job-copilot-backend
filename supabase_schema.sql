create table if not exists public.users (
  id uuid primary key,
  email text unique not null,
  full_name text default '',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table if not exists public.career_assets (
  id uuid primary key,
  user_id uuid not null,
  asset_type text not null,
  title text not null,
  target_role text default '',
  target_country text default '',
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  content_json jsonb default '{}'::jsonb,
  pdf_url text default '',
  docx_url text default ''
);

create table if not exists public.resume_versions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  career_asset_id uuid,
  created_at timestamptz default now(),
  content_json jsonb default '{}'::jsonb
);

create table if not exists public.cover_letter_versions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  career_asset_id uuid,
  created_at timestamptz default now(),
  content_json jsonb default '{}'::jsonb
);

create table if not exists public.linkedin_versions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  career_asset_id uuid,
  created_at timestamptz default now(),
  content_json jsonb default '{}'::jsonb
);

create table if not exists public.interview_reports (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  career_asset_id uuid,
  created_at timestamptz default now(),
  content_json jsonb default '{}'::jsonb
);

create table if not exists public.portfolio_versions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  career_asset_id uuid,
  created_at timestamptz default now(),
  content_json jsonb default '{}'::jsonb
);

create table if not exists public.job_applications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  career_asset_id uuid,
  created_at timestamptz default now(),
  content_json jsonb default '{}'::jsonb
);
