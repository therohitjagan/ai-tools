import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Generator
from contextlib import contextmanager

from .config import settings

DDL_STATEMENTS = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    segment TEXT NOT NULL CHECK(segment IN ('Enterprise', 'SMB', 'Consumer')),
    country TEXT NOT NULL,
    signup_date TEXT NOT NULL,
    churn_status TEXT NOT NULL CHECK(churn_status IN ('Active', 'Churned'))
);

CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_name TEXT NOT NULL,
    country TEXT NOT NULL,
    rating REAL NOT NULL,
    reliability_score REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT NOT NULL,
    unit_price REAL NOT NULL,
    unit_cost REAL NOT NULL,
    stock_quantity INTEGER NOT NULL,
    supplier_id INTEGER NOT NULL REFERENCES suppliers(supplier_id)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Delivered', 'Shipped', 'Pending', 'Cancelled', 'Refunded')),
    payment_method TEXT NOT NULL CHECK(payment_method IN ('Credit Card', 'Wire Transfer', 'PayPal', 'ACH')),
    shipping_cost REAL NOT NULL,
    fulfillment_days INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders(order_id),
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    discount_percent REAL NOT NULL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS support_tickets (
    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    category TEXT NOT NULL CHECK(category IN ('Billing', 'Technical', 'Product Inquiry', 'Return')),
    priority TEXT NOT NULL CHECK(priority IN ('Low', 'Medium', 'High', 'Urgent')),
    status TEXT NOT NULL CHECK(status IN ('Resolved', 'Open', 'In Progress', 'Escalated')),
    open_date TEXT NOT NULL,
    resolution_hours REAL,
    satisfaction_score INTEGER CHECK(satisfaction_score BETWEEN 1 AND 5)
);

CREATE TABLE IF NOT EXISTS product_reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
    review_date TEXT NOT NULL,
    helpful_votes INTEGER NOT NULL DEFAULT 0
);
"""

class DatabaseManager:
    """Manages SQLite connections, read-only sandboxed execution, and schema creation."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = Path(db_path or settings.DATABASE_PATH).resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def initialize_schema(self) -> None:
        """Creates tables and indexes."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(DDL_STATEMENTS)
            conn.commit()

    @contextmanager
    def get_read_only_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Yields an OS/C-level read-only SQLite connection.
        Enforces PRAGMA query_only = ON and busy timeout.
        """
        # Convert path to URI format for SQLite
        path_str = str(self.db_path).replace("\\", "/")
        uri = f"file:{path_str}?mode=ro"
        
        conn = sqlite3.connect(uri, uri=True, timeout=settings.MAX_EXECUTION_TIMEOUT_SECONDS)
        try:
            conn.execute("PRAGMA query_only = ON;")
            conn.row_factory = sqlite3.Row
            yield conn
        finally:
            conn.close()

    @contextmanager
    def get_write_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Used strictly for seeding and administrative maintenance."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.row_factory = sqlite3.Row
            yield conn
        finally:
            conn.close()


def seed_database(db_manager: DatabaseManager | None = None, seed: int = 42) -> None:
    """Populates the database with realistic enterprise data."""
    manager = db_manager or DatabaseManager()
    manager.initialize_schema()
    
    rnd = random.Random(seed)

    # Pre-defined realistic datasets
    first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Sam", "Chris", "Pat", "Robin",
                   "Emma", "Liam", "Sophia", "Noah", "Olivia", "Ethan", "Ava", "Lucas", "Mia", "Mason"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez",
                  "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore"]
    segments = ["Enterprise", "SMB", "Consumer"]
    countries = ["United States", "Germany", "United Kingdom", "Canada", "France", "Japan", "Australia", "Singapore"]

    suppliers_data = [
        ("TechSupply Global", "United States", 4.8, 0.96),
        ("Bavaria Microchips", "Germany", 4.9, 0.98),
        ("Pacific Displays", "Japan", 4.6, 0.91),
        ("Nordic Logistics & Hardware", "Germany", 4.5, 0.89),
        ("Maple Software & Cloud", "Canada", 4.7, 0.94),
        ("Albion Precision Electronics", "United Kingdom", 4.4, 0.88),
        ("Apex Office Furnishings", "United States", 4.6, 0.92),
        ("SingaTech Components", "Singapore", 4.8, 0.95),
        ("Oz Innovations", "Australia", 4.3, 0.86),
        ("Hexagon Data Systems", "France", 4.7, 0.93)
    ]

    products_data = [
        # Electronics
        ("UltraBook Pro 15", "Electronics", "Laptops", 1499.99, 950.00, 120, 1),
        ("AeroTab 11 Tablet", "Electronics", "Tablets", 699.99, 420.00, 240, 3),
        ("NoiseZero Pro Headphones", "Electronics", "Audio", 299.99, 130.00, 350, 1),
        ("VisionCurve 34-inch Monitor", "Electronics", "Monitors", 799.99, 480.00, 85, 3),
        ("Mechanical RGB Keyboard", "Electronics", "Accessories", 129.99, 55.00, 500, 6),
        ("ErgoGrip Wireless Mouse", "Electronics", "Accessories", 79.99, 32.00, 600, 6),
        ("ThunderBolt 4 Docking Station", "Electronics", "Accessories", 249.99, 110.00, 180, 2),
        ("4K UltraStream Webcam", "Electronics", "Audio & Video", 159.99, 70.00, 210, 8),
        
        # Software
        ("Enterprise Cloud Analytics Suite", "Software", "Analytics", 4999.00, 500.00, 9999, 5),
        ("CyberShield Endpoint Defense", "Software", "Security", 1200.00, 150.00, 9999, 5),
        ("DevOps Continuous Pipeline Tool", "Software", "Developer Tools", 850.00, 90.00, 9999, 10),
        ("CRM Synergy Pro License", "Software", "Productivity", 1500.00, 200.00, 9999, 5),

        # Furniture
        ("AeroSpine Ergonomic Office Chair", "Furniture", "Chairs", 549.00, 260.00, 75, 7),
        ("Motorized Standing Desk 60x30", "Furniture", "Desks", 689.00, 340.00, 45, 7),
        ("Acoustic ModuScreen Divider", "Furniture", "Partitions", 189.00, 80.00, 90, 7),
        ("Steel Modular Filing Cabinet", "Furniture", "Storage", 229.00, 95.00, 60, 7),

        # Office Supplies
        ("Recycled Multi-Purpose Paper (Case)", "Office Supplies", "Paper", 49.99, 22.00, 400, 7),
        ("Archival Gel Pens Box of 24", "Office Supplies", "Writing", 24.99, 8.50, 800, 7),
        ("Heavy Duty Thermal Label Printer", "Office Supplies", "Printers", 199.99, 90.00, 110, 9),
        ("Biodegradable Packing Pellets (Bag)", "Office Supplies", "Shipping Supplies", 34.99, 11.00, 300, 9)
    ]

    base_date = datetime(2025, 1, 1)

    with manager.get_write_connection() as conn:
        cursor = conn.cursor()
        
        # Check if already seeded
        cursor.execute("SELECT COUNT(*) FROM customers")
        if cursor.fetchone()[0] > 0:
            return  # Already seeded

        # 1. Insert Suppliers
        cursor.executemany(
            "INSERT INTO suppliers (supplier_name, country, rating, reliability_score) VALUES (?, ?, ?, ?)",
            suppliers_data
        )

        # 2. Insert Products
        cursor.executemany(
            "INSERT INTO products (product_name, category, subcategory, unit_price, unit_cost, stock_quantity, supplier_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
            products_data
        )

        # 3. Insert Customers (100 customers)
        customers = []
        for i in range(1, 101):
            fname = rnd.choice(first_names)
            lname = rnd.choice(last_names)
            email = f"{fname.lower()}.{lname.lower()}{i}@example.com"
            segment = rnd.choice(segments)
            country = rnd.choice(countries)
            signup_delta = rnd.randint(0, 500)
            signup_date = (base_date + timedelta(days=signup_delta)).strftime("%Y-%m-%d")
            churn_status = "Churned" if rnd.random() < 0.15 else "Active"
            customers.append((fname, lname, email, segment, country, signup_date, churn_status))

        cursor.executemany(
            "INSERT INTO customers (first_name, last_name, email, segment, country, signup_date, churn_status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            customers
        )

        # 4. Insert Orders & Order Items
        statuses = ["Delivered", "Delivered", "Delivered", "Shipped", "Pending", "Cancelled", "Refunded"]
        payment_methods = ["Credit Card", "Wire Transfer", "PayPal", "ACH"]
        
        orders = []
        order_items = []
        order_id_counter = 1

        for cust_id in range(1, 101):
            num_orders = rnd.randint(1, 8)
            for _ in range(num_orders):
                order_delta = rnd.randint(100, 600)
                order_date = (base_date + timedelta(days=order_delta)).strftime("%Y-%m-%d")
                status = rnd.choice(statuses)
                pay_method = rnd.choice(payment_methods)
                ship_cost = round(rnd.uniform(5.0, 35.0), 2)
                fulfillment = rnd.randint(1, 10) if status in ("Delivered", "Shipped") else 0
                
                orders.append((cust_id, order_date, status, pay_method, ship_cost, fulfillment))
                
                # Order items (1 to 4 items)
                num_items = rnd.randint(1, 4)
                chosen_products = rnd.sample(range(1, len(products_data) + 1), num_items)
                for prod_id in chosen_products:
                    prod = products_data[prod_id - 1]
                    qty = rnd.randint(1, 5) if prod[1] != "Software" else rnd.randint(1, 2)
                    price = prod[4]
                    discount = rnd.choice([0.0, 0.05, 0.10, 0.15, 0.20]) if rnd.random() < 0.3 else 0.0
                    order_items.append((order_id_counter, prod_id, qty, price, discount))

                order_id_counter += 1

        cursor.executemany(
            "INSERT INTO orders (customer_id, order_date, status, payment_method, shipping_cost, fulfillment_days) VALUES (?, ?, ?, ?, ?, ?)",
            orders
        )
        cursor.executemany(
            "INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_percent) VALUES (?, ?, ?, ?, ?)",
            order_items
        )

        # 5. Insert Support Tickets
        ticket_categories = ["Billing", "Technical", "Product Inquiry", "Return"]
        ticket_priorities = ["Low", "Medium", "High", "Urgent"]
        ticket_statuses = ["Resolved", "Resolved", "Open", "In Progress", "Escalated"]
        tickets = []
        for _ in range(150):
            c_id = rnd.randint(1, 100)
            cat = rnd.choice(ticket_categories)
            pri = rnd.choice(ticket_priorities)
            st = rnd.choice(ticket_statuses)
            open_d = (base_date + timedelta(days=rnd.randint(200, 600))).strftime("%Y-%m-%d")
            res_hrs = round(rnd.uniform(0.5, 48.0), 2) if st == "Resolved" else None
            sat_score = rnd.randint(1, 5) if st == "Resolved" else None
            tickets.append((c_id, cat, pri, st, open_d, res_hrs, sat_score))

        cursor.executemany(
            "INSERT INTO support_tickets (customer_id, category, priority, status, open_date, resolution_hours, satisfaction_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
            tickets
        )

        # 6. Insert Product Reviews
        reviews = []
        for _ in range(200):
            p_id = rnd.randint(1, len(products_data))
            c_id = rnd.randint(1, 100)
            rating = rnd.choices([5, 4, 3, 2, 1], weights=[45, 30, 12, 8, 5])[0]
            rev_d = (base_date + timedelta(days=rnd.randint(200, 600))).strftime("%Y-%m-%d")
            votes = rnd.randint(0, 45)
            reviews.append((p_id, c_id, rating, rev_d, votes))

        cursor.executemany(
            "INSERT INTO product_reviews (product_id, customer_id, rating, review_date, helpful_votes) VALUES (?, ?, ?, ?, ?)",
            reviews
        )

        conn.commit()
