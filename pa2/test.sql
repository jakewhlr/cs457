USE cs457p2;
create table Product (pid int, name varchar(20), price float);
insert INTO Product VALUES(1,	'Gizmo',      	19.99);
insert INTO Product VALUES(2,	'PowerGizmo', 	29.99);
insert INTO Product VALUES(3,	'SingleTouch', 	149.99);
insert INTO Product VALUES(4,	'MultiTouch', 	199.99);
insert INTO Product VALUES(5,	'SuperGizmo', 	49.99);
delete from Product where price > 50.00;

select * from Product;
