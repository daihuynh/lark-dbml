CREATE SCHEMA IF NOT EXISTS "myschema";

CREATE TYPE status AS ENUM ('active','inactive','archived');
CREATE TYPE myschema.priority AS ENUM ('high','medium','low');
CREATE TYPE simple_enum AS ENUM ('a','b','c');
