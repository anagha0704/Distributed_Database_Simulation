-- schema.sql
CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(255),
    quantity INT
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    product_id INT,
    quantity INT,
    customer_name VARCHAR(255),
    region VARCHAR(50)
);


"""
Use this if you need to reset the tables

truncate table inventory;

select * from inventory;

insert into inventory(id, product_name, quantity) values 
(1,'Laptop', 100),
(2,'Mouse', 200),
(3,'Keyboard', 150),
(4,'Monitor', 75),
(5,'Webcam', 120);

select * from inventory;

truncate table orders;

select * from orders;

"""