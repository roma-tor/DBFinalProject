import random
from datetime import date, timedelta
import requests

BASE_URL = "http://127.0.0.1:8000"

def post(path: str, payload: dict) -> dict:
    r = requests.post(f"{BASE_URL}{path}", json=payload, timeout=10)
    r.raise_for_status()
    return r.json()

def random_date():
    start = date.today() - timedelta(days=90)
    end = date.today() + timedelta(days=30)
    d = start + timedelta(days=random.randint(0, (end - start).days))
    return d.isoformat()

def main():
    NUM_PRODUCTS = 50
    NUM_CUSTOMERS = 30
    NUM_PURCHASES = 300

    units = ["pcs", "kg", "liter", "box"]
    manufacturers = ["DairyCo", "MegaFood", "FreshFarm", "TechParts"]

    product_ids = []
    customer_ids = []

    # products
    for i in range(NUM_PRODUCTS):
        res = post("/products", {
            "name": f"Product {i+1}",
            "manufacturer": random.choice(manufacturers),
            "unit": random.choice(units)
        })
        product_ids.append(res["id"])

    # customers
    for i in range(NUM_CUSTOMERS):
        res = post("/customers", {
            "name": f"Customer {i+1}",
            "address": f"Street {random.randint(1,200)}",
            "phone": f"+374{random.randint(10000000, 99999999)}",
            "contact_person": f"Person {random.randint(1,200)}"
        })
        customer_ids.append(res["id"])

    # purchases
    for i in range(NUM_PURCHASES):
        post("/purchases", {
            "product_id": random.choice(product_ids),
            "customer_id": random.choice(customer_ids),
            "quantity": random.randint(1, 100),
            "unit_price": round(random.uniform(1.0, 500.0), 2),
            "delivery_date": random_date()
        })
        if (i + 1) % 50 == 0:
            print(f"Purchases: {i+1}/{NUM_PURCHASES}")

    print("✅ Done! DB filled via REST API.")

if __name__ == "__main__":
    main()

