drop table if exists users;
create table users (
    userID varchar(36) primary key,
    username varchar(36),
    email varchar(320) unique,
    passhash varchar(255)
);

