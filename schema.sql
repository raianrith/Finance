drop table if exists users;
create table users(
  id integer primary key autoincrement,
  first_name text,
  last_name text,
  email text,
  phonenumber text not null unique
);

drop table if exists weights;
create table weights(
    weight_id integer primary key autoincrement,
    id integer not null,
    weight integer not null,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

drop table if exists notes;
create table notes(
    note_id integer primary key autoincrement,
    id integer not null,
    note text not null,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);