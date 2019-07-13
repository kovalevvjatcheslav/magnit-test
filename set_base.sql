pragma foreign_keys = 1;

create table if not exists Region(id integer primary key autoincrement, name text not null unique);

create table if not exists City(
    id integer primary key autoincrement,
    name text not null unique,
    region_id integer not null,
    foreign key(region_id) references Region(id)
);

create table if not exists Comments(
    id integer primary key autoincrement,
    name text not null,
    surname text not null,
    patronymic text,
    city_id integer,
    phone integer,
    email text,
    comment text not null,
    foreign key(city_id) references City(id)
);