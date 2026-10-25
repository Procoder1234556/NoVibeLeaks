-- SecMCP Phase 3: scan history (scores only, no raw secrets)
create table if not exists public.scans (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  created_at timestamptz not null default now(),
  source_type text not null check (source_type in ('upload', 'github')),
  source_label text not null,
  overall_score numeric not null,
  grade text not null,
  breakdown jsonb not null default '{}'::jsonb,
  finding_count int not null default 0
);

create index if not exists scans_user_created_idx on public.scans (user_id, created_at desc);

alter table public.scans enable row level security;

create policy "Users read own scans"
  on public.scans for select
  using (auth.uid() = user_id);

create policy "Users insert own scans"
  on public.scans for insert
  with check (auth.uid() = user_id);
