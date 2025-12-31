import sqlite3

DB = "shop.db"

def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # В SQLite удобно так: CREATE INDEX IF NOT EXISTS
    cur.execute("CREATE INDEX IF NOT EXISTS idx_purchase_product_id ON purchase(product_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_purchase_customer_id ON purchase(customer_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_purchase_delivery_date ON purchase(delivery_date)")

    conn.commit()
    conn.close()
    print("✅ Migration 002 complete (indexes created)")

if __name__ == "__main__":
    main()

