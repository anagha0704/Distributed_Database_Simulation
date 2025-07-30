CREATE TABLE central_products (
    id INT PRIMARY KEY,              -- This will match product_id from regional DBs
    product_name VARCHAR(255) NOT NULL);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    product_id INT,
    quantity INT,
    customer_name VARCHAR(255),
    region VARCHAR(50)
);


"""
Use this if you need to reset the tables
truncate table central_products;

select * from central_products;

insert into central_products(id, product_name) values 
(1,'Laptop'),
(2,'Mouse'),
(3,'Keyboard'),
(4,'Monitor'),
(5,'Webcam');

select * from central_products;

truncate table orders;

select * from orders;
"""