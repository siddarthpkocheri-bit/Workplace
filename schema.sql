-- This table will store every sale transaction
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    customer_phone TEXT,
    product_details TEXT NOT NULL,
    gold_weight REAL NOT NULL,
    gold_rate REAL NOT NULL,
    making_charges REAL NOT NULL,
    total_amount REAL NOT NULL,
    sale_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
