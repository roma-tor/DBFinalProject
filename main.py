import sqlite3
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Simple Shop CRUD API")
DB = "shop.db"


def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS product (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        manufacturer TEXT,
        unit TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS customer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT,
        phone TEXT,
        contact_person TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS purchase (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        customer_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        delivery_date TEXT,
        FOREIGN KEY(product_id) REFERENCES product(id),
        FOREIGN KEY(customer_id) REFERENCES customer(id)
    )
    """)

    conn.commit()
    conn.close()


def fetch_one(query, params=()):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(query, params)
    row = cur.fetchone()
    conn.close()
    return row


def fetch_all(query, params=()):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows


def execute(query, params=()):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id


init_db()

# ---------------- PRODUCTS ----------------
@app.post("/products")
def create_product(item: dict):
    new_id = execute(
        "INSERT INTO product(name, manufacturer, unit) VALUES(?,?,?)",
        (item.get("name"), item.get("manufacturer"), item.get("unit"))
    )
    return {"id": new_id, **item}


@app.get("/products")
def list_products():
    return fetch_all("SELECT * FROM product")


@app.get("/products/{id}")
def get_product(id: int):
    row = fetch_one("SELECT * FROM product WHERE id=?", (id,))
    if not row:
        raise HTTPException(404, "Product not found")
    return row


@app.put("/products/{id}")
def update_product(id: int, item: dict):
    execute(
        "UPDATE product SET name=?, manufacturer=?, unit=? WHERE id=?",
        (item.get("name"), item.get("manufacturer"), item.get("unit"), id)
    )
    return {"id": id, **item}


@app.delete("/products/{id}")
def delete_product(id: int):
    execute("DELETE FROM product WHERE id=?", (id,))
    return {"deleted": id}


# ---------------- CUSTOMERS ----------------
@app.post("/customers")
def create_customer(item: dict):
    new_id = execute(
        "INSERT INTO customer(name, address, phone, contact_person) VALUES(?,?,?,?)",
        (item.get("name"), item.get("address"), item.get("phone"), item.get("contact_person"))
    )
    return {"id": new_id, **item}


@app.get("/customers")
def list_customers():
    return fetch_all("SELECT * FROM customer")


@app.get("/customers/{id}")
def get_customer(id: int):
    row = fetch_one("SELECT * FROM customer WHERE id=?", (id,))
    if not row:
        raise HTTPException(404, "Customer not found")
    return row


@app.put("/customers/{id}")
def update_customer(id: int, item: dict):
    execute(
        "UPDATE customer SET name=?, address=?, phone=?, contact_person=? WHERE id=?",
        (item.get("name"), item.get("address"), item.get("phone"), item.get("contact_person"), id)
    )
    return {"id": id, **item}


@app.delete("/customers/{id}")
def delete_customer(id: int):
    execute("DELETE FROM customer WHERE id=?", (id,))
    return {"deleted": id}


# ---------------- PURCHASES ----------------
@app.post("/purchases")
def create_purchase(item: dict):
    # простая проверка что product и customer существуют
    if not fetch_one("SELECT id FROM product WHERE id=?", (item.get("product_id"),)):
        raise HTTPException(400, "Invalid product_id")
    if not fetch_one("SELECT id FROM customer WHERE id=?", (item.get("customer_id"),)):
        raise HTTPException(400, "Invalid customer_id")

    new_id = execute(
        """INSERT INTO purchase(product_id, customer_id, quantity, unit_price, delivery_date)
           VALUES(?,?,?,?,?)""",
        (item.get("product_id"), item.get("customer_id"), item.get("quantity"),
         item.get("unit_price"), item.get("delivery_date"))
    )
    return {"id": new_id, **item}


@app.get("/purchases")
def list_purchases():
    return fetch_all("SELECT * FROM purchase")


@app.get("/purchases/{id}")
def get_purchase(id: int):
    row = fetch_one("SELECT * FROM purchase WHERE id=?", (id,))
    if not row:
        raise HTTPException(404, "Purchase not found")
    return row


@app.put("/purchases/{id}")
def update_purchase(id: int, item: dict):
    execute(
        """UPDATE purchase
           SET product_id=?, customer_id=?, quantity=?, unit_price=?, delivery_date=?
           WHERE id=?""",
        (item.get("product_id"), item.get("customer_id"), item.get("quantity"),
         item.get("unit_price"), item.get("delivery_date"), id)
    )
    return {"id": id, **item}


@app.delete("/purchases/{id}")
def delete_purchase(id: int):
    execute("DELETE FROM purchase WHERE id=?", (id,))
    return {"deleted": id}
