# CS457 Database Management Systems
## Programming Assignment 1: Metadata Management
#### Sui Cheung, Eric Olson, Jake Wheeler

## Assignment Overview
"In this assignment you will write a program that allows a database user to manage the metadata of their relational data. By metadata, we mean the database’s own information (e.g., database’s name, creation time, owner) as well  as the properties of the tables (e.g., table’s names, attributes, constraints program."

## Implementation
This database metadata management application is implemented using Python 3, and allows for the creation, deletion, and altering of databases and tables. Databases are created as subdirectories within the `databases` directory in the root of the repository. Within those directories, tables are created with the format:
```
attribute_name1 attribute_type1 | attribute_name2 attribute_type2
value1 | value2
```
Attributes that are selected from tables are loaded into two dimensional lists and parsed to output any associated values, or alter attributes.

## Usage
The following commands can be used:
```
CREATE DATABASE <database name>;
CREATE TABLE <table name>(<attributes>);
USE <database name>;
SELECT <attribute, *> FROM <table name>;
DROP DATABASE <database name>;
DROP TABLE <table name>;
ALTER <table name> ADD <attribute_name> <attribute_type>;
.EXIT
--<Comment>
```

### Sample Input
```
--Database metadata (20 points)
CREATE DATABASE db_1;
CREATE DATABASE db_1;
CREATE DATABASE db_2;
DROP DATABASE db_2;
DROP DATABASE db_2;
CREATE DATABASE db_2;

--Table metadata (50 points)
USE db_1;
CREATE TABLE tbl_1 (a1 int, a2 varchar(20));
CREATE TABLE tbl_1 (a3 float, a4 char(20));
DROP TABLE tbl_1;
DROP TABLE tbl_1;
CREATE TABLE tbl_1 (a1 int, a2 varchar(20));
SELECT * FROM tbl_1;
ALTER TABLE tbl_1 ADD a3 float;
SELECT * FROM tbl_1;
CREATE TABLE tbl_2 (a3 float, a4 char(20));
SELECT * FROM tbl_2;
USE db_2;
SELECT * FROM tbl_1;
CREATE TABLE tbl_1 (a3 float, a4 char(20));
SELECT * FROM tbl_1;

.EXIT
```

### Expected output
```
-- Database db_1 created.
-- !Failed to create database db_1 because it already exists.
-- Database db_2 created.
-- Database db_2 deleted.
-- !Failed to delete db_2 because it does not exist.
-- Database db_2 created.
-- Using database db_1.
-- Table tbl_1 created.
-- !Failed to create table tbl_1 because it already exists.
-- Table tbl_1 deleted.
-- !Failed to delete tbl_1 because it does not exist.
-- Table tbl_1 created.
-- a1 int | a2 varchar(20)
-- Table tbl_1 modified.
-- a1 int | a2 varchar(20) | a3 float
-- Table tbl_2 created.
-- a3 float | a4 char(20)
-- Using Database db_2.
-- !Failed to query table tbl_1 because it does not exist.
-- Table tbl_1 created.
-- a3 float | a4 char(20)
-- All done.
```
