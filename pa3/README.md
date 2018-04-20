# CS457 Database Management Systems
## Programming Assignment 3: Table Joins
#### Sui Cheung, Eric Olson, Jake Wheeler

## Assignment Overview
"In this assignment you will write a program that allows a database user to make queries over multiple tables. That is, you will implement table joins using techniques we discussed in the class. This assignment assumes the metadata and data manipulations on singular tables are already available, which should have been provided (implemented) in the  rst two programming assignments."

## Implementation
This database metadata management application is implemented using Python 3, and allows for the creation, deletion, and altering of databases and tables. Databases are created as subdirectories within the `databases` directory in the root of the repository. Within those directories, tables are created with the format:
```
attribute_name1 attribute_type1 | attribute_name2 attribute_type2
value1 | value2
```
Attributes that are selected from tables are loaded into two dimensional lists and parsed to output any associated values, or alter attributes.

## Usage
**REQUIRES PYTHON 3.6**

The program can be run with: `python3.6 app.py`
The following commands can be used:
```
CREATE DATABASE <database name>;
CREATE TABLE <table name>(<attributes>);
USE <database name>;
INSERT into <table name> values(<values>);
UPDATE <table name> SET <attribute> = <value> WHERE <attribute> = <value>;
SELECT <attribute, *> FROM <table name>;
DELETE from <table name> WHERE <attribute> = <value>;
DROP DATABASE <database name>;
DROP TABLE <table name>;
ALTER <table name> ADD <attribute_name> <attribute_type>;
.EXIT
--<Comment>
```

### Sample Input
```
CREATE DATABASE CS457_PA2;
USE CS457_PA2;
CREATE TABLE Product (pid int, name varchar(20), price float);

--Insert new data (20 points)
insert into Product values(1,	'Gizmo',      	19.99);
insert into Product values(2,	'PowerGizmo', 	29.99);
insert into Product values(3,	'SingleTouch', 	149.99);
insert into Product values(4,	'MultiTouch', 	199.99);
insert into Product values(5,	'SuperGizmo', 	49.99);

select * from Product;

--Modify data (20 points)
update Product
set name = 'Gizmo'
where name = 'SuperGizmo';

update Product
set price = 14.99
where name = 'Gizmo';

select * from Product;

--Delete data (20 points)
delete from product
where name = 'Gizmo';

delete from product
where price > 150;

select * from Product;

--Query subsets (10 points)
select name, price
from product
where pid != 2;

.exit
```

### Expected output
```
-- Expected output
--
-- Database CS457_PA2 created.
-- Using database CS457_PA2.
-- Table Product created.
-- 1 new record inserted.
-- 1 new record inserted.
-- 1 new record inserted.
-- 1 new record inserted.
-- 1 new record inserted.
-- pid int|name varchar(20)|price float
-- 1|Gizmo|19.99
-- 2|PowerGizmo|29.99
-- 3|SingleTouch|149.99
-- 4|MultiTouch|199.99
-- 5|SuperGizmo|49.99
-- 1 record modified.
-- 2 records modified.
-- pid int|name varchar(20)|price float
-- 1|Gizmo|14.99
-- 2|PowerGizmo|29.99
-- 3|SingleTouch|149.99
-- 4|MultiTouch|199.99
-- 5|Gizmo|14.99
-- 2 records deleted.
-- 1 record deleted.
-- pid int|name varchar(20)|price float
-- 2|PowerGizmo|29.99
-- 3|SingleTouch|149.99
-- name varchar(20)|price float
-- SingleTouch|149.99
-- All done.
```
