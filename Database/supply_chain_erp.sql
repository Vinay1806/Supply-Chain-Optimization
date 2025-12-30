create database if not exists supply_chain_erp; 

USE supply_chain_erp;

CREATE TABLE inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    price DECIMAL(10,2),
    supplier_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

create table suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(100),
    email VARCHAR(100),
    address TEXT
);

CREATE TABLE purchase_orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    item_id INT not null,
    quantity INT NOT NULL,
    status ENUM('pending', 'completed', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES purchase_orders(order_id),
    FOREIGN KEY (item_id) REFERENCES inventory(id)
);

create table productts(
	product_id int auto_increment primary key,
    product_name varchar(100)
);

INSERT INTO productts (product_name) VALUES ('Mobile Phone');
INSERT INTO productts (product_name) VALUES ('Tablet');
INSERT INTO productts (product_name) VALUES ('Smart Watch');
INSERT INTO productts (product_name) VALUES ('Smart Glasses');

CREATE TABLE product_components (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id int,
    item_id int,
    quantity_required DOUBLE,
    FOREIGN KEY (product_id) REFERENCES productts(product_id),
    FOREIGN KEY (item_id) REFERENCES inventory(id)
);

CREATE TABLE production_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    product_name VARCHAR(100),
    quantity INT DEFAULT 1,
    manufactured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

select * from inventory;
select * from suppliers;
select * from purchase_orders;
select * from order_items;
select * from productts;
select * from product_components;
select * from production_log;

