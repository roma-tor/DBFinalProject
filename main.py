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

@app.get("/q/where")
def q_where(customer_id: int, min_qty: int, max_price: float):
    # SELECT ... WHERE с несколькими условиями (AND AND AND)
    sql = """
    SELECT * FROM purchase
    WHERE customer_id = ?
      AND quantity >= ?
      AND unit_price <= ?
    """
    return fetch_all(sql, (customer_id, min_qty, max_price))

@app.get("/q/join")
def q_join():
    # JOIN: покупка + название товара + имя покупателя
    sql = """
    SELECT
      p.id,
      pr.name AS product_name,
      c.name  AS customer_name,
      p.quantity,
      p.unit_price,
      p.delivery_date
    FROM purchase p
    JOIN product pr ON pr.id = p.product_id
    JOIN customer c ON c.id = p.customer_id
    """
    return fetch_all(sql)

@app.put("/q/update")
def q_update(customer_id: int, min_qty: int, percent: float):
    # UPDATE с условием не по id, а по логике
    factor = (100 - percent) / 100

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        UPDATE purchase
        SET unit_price = unit_price * ?
        WHERE customer_id = ?
          AND quantity >= ?
    """, (factor, customer_id, min_qty))
    conn.commit()
    changed = cur.rowcount
    conn.close()
    return {"updated_rows": changed}


@app.get("/q/groupby")
def q_groupby():
    sql = """
    SELECT
      c.id,
      c.name,
      COUNT(p.id) AS purchases_count,
      SUM(p.quantity * p.unit_price) AS total_sum
    FROM customer c
    JOIN purchase p ON p.customer_id = c.id
    GROUP BY c.id, c.name
    """
    return fetch_all(sql)


@app.get("/q/sort")
def q_sort(by: str = "unit_price", order: str = "asc"):
    # Супер-просто: разрешим только 2 поля, чтобы не было SQL-injection
    if by not in ("unit_price", "delivery_date"):
        raise HTTPException(400, "by must be unit_price or delivery_date")
    if order.lower() not in ("asc", "desc"):
        raise HTTPException(400, "order must be asc or desc")

    sql = f"SELECT * FROM purchase ORDER BY {by} {order.upper()}"
    return fetch_all(sql)


import os
import psycopg2
from fastapi import Query

PG_DSN = os.getenv(
    "PG_DSN",
    "dbname=shop_db user=shop_user password=password123 host=127.0.0.1 port=5432"
)

def pg_fetch_all(sql: str, params=()):
    conn = psycopg2.connect(PG_DSN)
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.get("/search/products")
def search_products_regex(
    pattern: str = Query(..., description="PostgreSQL regex, e.g. milk|cheese"),
    limit: int = Query(50, ge=1, le=500),
):
    # regex поиск по JSON (psql-style): meta::text ~ pattern
    sql = """
    SELECT id, name, manufacturer, unit, meta
    FROM product
    WHERE (meta::text ~ %s)
    LIMIT %s
    """
    return pg_fetch_all(sql, (pattern, limit))
