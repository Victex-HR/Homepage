-- NARA 어드민용 Supabase 스키마
-- Supabase 대시보드 > SQL Editor 에 통째로 붙여넣고 Run 하면 됩니다. 여러 번 실행해도 안전합니다.
-- 가장 먼저 가입한 사람이 자동으로 관리자(승인됨)가 되고, 이후 가입자는 관리자가 승인해야 들어올 수 있습니다.

-- 가입자 ------------------------------------------------------------------
create table if not exists public.profiles (
  id uuid primary key references auth.users on delete cascade,
  email text,
  name text default '',
  role text not null default 'member' check (role in ('admin', 'member')),
  approved boolean not null default false,
  created_at timestamptz not null default now()
);

create or replace function public.is_admin() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from profiles where id = auth.uid() and role = 'admin' and approved)
$$;

create or replace function public.is_member() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from profiles where id = auth.uid() and approved)
$$;

create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
declare first_user boolean;
begin
  select not exists (select 1 from profiles) into first_user;
  insert into profiles (id, email, name, role, approved)
  values (new.id, new.email, coalesce(new.raw_user_meta_data->>'name', ''),
          case when first_user then 'admin' else 'member' end, first_user);
  return new;
end $$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.handle_new_user();

-- 메일 수신자 ---------------------------------------------------------------
create table if not exists public.recipients (
  id bigint generated always as identity primary key,
  email text not null unique,
  name text default '',
  active boolean not null default true,
  created_at timestamptz not null default now()
);

-- 발송 일정 (한국시간) --------------------------------------------------------
create table if not exists public.schedules (
  id bigint generated always as identity primary key,
  name text not null default '매일 발송',
  send_time time not null default '00:00',
  weekdays int[] not null default '{1,2,3,4,5,6,7}',   -- 1=월 … 7=일
  active boolean not null default true,
  last_sent_on date,
  created_at timestamptz not null default now()
);

-- 발송 기록 ---------------------------------------------------------------
create table if not exists public.send_log (
  id bigint generated always as identity primary key,
  schedule_id bigint references public.schedules on delete set null,
  report_date date,
  recipients text[],
  status text not null,
  detail text,
  sent_at timestamptz not null default now()
);

-- 권한: 승인된 가입자는 보기, 관리자는 수정 ------------------------------------------
alter table public.profiles enable row level security;
alter table public.recipients enable row level security;
alter table public.schedules enable row level security;
alter table public.send_log enable row level security;

drop policy if exists "profiles read" on public.profiles;
create policy "profiles read" on public.profiles for select using (id = auth.uid() or public.is_admin());
drop policy if exists "profiles admin update" on public.profiles;
create policy "profiles admin update" on public.profiles for update using (public.is_admin()) with check (public.is_admin());
drop policy if exists "profiles admin delete" on public.profiles;
create policy "profiles admin delete" on public.profiles for delete using (public.is_admin() and id <> auth.uid());

do $$
declare t text;
begin
  foreach t in array array['recipients', 'schedules', 'send_log'] loop
    execute format('drop policy if exists "%1$s read" on public.%1$s', t);
    execute format('create policy "%1$s read" on public.%1$s for select using (public.is_member())', t);
    execute format('drop policy if exists "%1$s admin write" on public.%1$s', t);
    execute format('create policy "%1$s admin write" on public.%1$s for all using (public.is_admin()) with check (public.is_admin())', t);
  end loop;
end $$;

-- 처음 값 ------------------------------------------------------------------
insert into public.recipients (email, name) values ('jhw82@victex.co.kr', '')
  on conflict (email) do nothing;
insert into public.schedules (name, send_time, weekdays)
  select '매일 자정 (전날 공고)', '00:00', '{1,2,3,4,5,6,7}'
  where not exists (select 1 from public.schedules);
