import sqlite3

DB = "shop.db"

def column_exists(cur, table: str, column: str) -> bool:
    cur.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cur.fetchall()]  # row[1] = column name
    return column in cols

def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # product.barcode
    if not column_exists(cur, "product", "barcode"):
        cur.execute("ALTER TABLE product ADD COLUMN barcode TEXT")
        print("Added column product.barcode")
    else:
        print("Column product.barcode already exists")

    # customer.email
    if not column_exists(cur, "customer", "email"):
        cur.execute("ALTER TABLE customer ADD COLUMN email TEXT")
        print("Added column customer.email")
    else:
        print("Column customer.email already exists")

    conn.commit()
    conn.close()
    print("✅ Migration 001 complete")

if __name__ == "__main__":
    main()

