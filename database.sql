CREATE TABLE product (
    id INTEGER PRIMARY KEY,
    name TEXT,
    manufacturer TEXT,
    unit TEXT
);

CREATE TABLE customer (
    id INTEGER PRIMARY KEY,
    name TEXT,
    address TEXT,
    phone TEXT,
    contact_person TEXT
);

CREATE TABLE purchase (
    id INTEGER PRIMARY KEY,
    product_id INTEGER,
    customer_id INTEGER,
    quantity INTEGER,
    unit_price REAL,
    delivery_date DATE,

    FOREIGN KEY (product_id) REFERENCES product(id),
    FOREIGN KEY (customer_id) REFERENCES customer(id)
);
