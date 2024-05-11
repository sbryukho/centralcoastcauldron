create table
  public.global_inventory (
    num_green_ml integer not null default 0,
    gold integer generated by default 0,
    num_red_ml integer not null default 0,
    num_blue_ml integer not null default 0,
    num_dark_ml integer not null default 0,
    constraint global_inventory_pkey primary key (gold)
  ) tablespace pg_default;

create table
  public.potion_table (
    id integer generated by default as identity,
    sku text not null,
    price integer not null default 0,
    quantity integer not null default 0,
    potion_name text null,
    red integer not null default 0,
    green integer not null default 0,
    dark integer not null default 0,
    blue integer not null default 0,
    constraint potion_table_pkey primary key (id)
  ) tablespace pg_default;

  insert into potion_table (sku, potion_name, quantity, price, red, green, blue, dark) values 
('RED_POTION_0',10,0, 'red potion', 100, 0, 0, 0), 
('GREEN_POTION_0',10,0, 'green basic', 0, 100, 0, 0), 
('BLUE_POTION_0',10, 0, 'blue potion', 0, 0, 100, 0), 
('AQUA_0', 10, 0, 'aqua', 0, 50, 50, 0), 
('PURPLE_0',10, 0, 'purple', 50, 0, 50, 0)

create table
  public.carts (
    id integer generated by default as identity,
    class text null,
    name text null,
    level integer null default 0,
    constraint carts_pkey primary key (id)
  ) tablespace pg_default;

create table
  public.carts_items (
    id integer generated by default as identity,
    customer_id integer null,
    quantity integer null,
    item_id integer null,
    constraint carts_items_pkey primary key (id),
    constraint public_carts_items_customer_id_fkey foreign key (customer_id) references carts (id),
    constraint public_carts_items_item_id_fkey foreign key (item_id) references potion_table (id)
  ) tablespace pg_default;

   create table
  public.gold_ledger (
    id integer generated by default as identity,
    created_at timestamp with time zone not null default now(),
    change integer null default 0,
    "desc" integer null,
    constraint gold_ledger_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.ml_ledger (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    type text null,
    change integer not null default 0,
    constraint ml_ledger_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.potion_ledger (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    potion_id integer null,
    change integer not null default 0,
    "desc" integer null,
    constraint ledger_entries_pkey primary key (id)
  ) tablespace pg_default;