# Task A · Multi-Table Relational System

import csv
import mysql.connector

def export_revenue_report(rows):
    report_path = "revenue_report.csv"
    with open(report_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["customer_name", "total_spent"])
        writer.writerows(rows)
    print(f"\nRevenue report exported: {report_path} \n")


conn = None
cursor = None

try:
    conn = mysql.connector.connect(host="localhost", user="root", password="root")
    cursor = conn.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS store_db")
    cursor.execute("USE store_db")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            address VARCHAR(255)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            product_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            price DECIMAL(10, 2)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT,
            product_id INT,
            quantity INT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
        """
    )

    # Reset data so repeated runs produce stable output
    cursor.execute("SET FOREIGN_KEY_CHECKS=0")
    cursor.execute("DELETE FROM orders")
    cursor.execute("DELETE FROM customers")
    cursor.execute("DELETE FROM products")
    cursor.execute("ALTER TABLE customers AUTO_INCREMENT = 1")
    cursor.execute("ALTER TABLE products AUTO_INCREMENT = 1")
    cursor.execute("ALTER TABLE orders AUTO_INCREMENT = 1")
    cursor.execute("SET FOREIGN_KEY_CHECKS=1")

    customers = [
        ("Alice", "New York"),
        ("Bob", "Los Angeles"),
        ("Charlie", "Chicago"),
        ("David", "Houston"),
        ("Eve", "Phoenix"),
        ("Frank", "Philadelphia"),
        ("Grace", "San Antonio"),
        ("Heidi", "San Diego"),
        ("Ivan", "Dallas"),
        ("Judy", "San Jose"),
    ]

    products = [
        ("Laptop", 999.99),
        ("Smartphone", 499.99),
        ("Headphones", 199.99),
        ("Monitor", 299.99),
        ("Keyboard", 89.99),
        ("Mouse", 49.99),
        ("Printer", 149.99),
        ("Webcam", 79.99),
    ]

    orders = [
        (1, 1, 2),
        (1, 5, 1),
        (2, 2, 1),
        (2, 6, 2),
        (3, 3, 3),
        (3, 4, 1),
        (4, 4, 2),
        (4, 7, 1),
        (5, 5, 4),
        (5, 8, 2),
        (6, 6, 5),
        (6, 2, 1),
        (7, 7, 1),
        (7, 3, 2),
        (8, 8, 5),
        (8, 1, 1),
        (9, 4, 3),
        (9, 5, 2),
        (10, 1, 1),
        (10, 2, 2),
    ]

    cursor.executemany("INSERT INTO customers (name, address) VALUES (%s, %s)", customers)
    cursor.executemany("INSERT INTO products (name, price) VALUES (%s, %s)", products)
    cursor.executemany(
        "INSERT INTO orders (customer_id, product_id, quantity) VALUES (%s, %s, %s)",
        orders,
    )
    conn.commit()

    # 1) total money spent per customer (JOIN + price * quantity), highest first
    cursor.execute(
        """
        SELECT c.name, ROUND(SUM(p.price * o.quantity), 2) AS total_spent
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN products p ON o.product_id = p.product_id
        GROUP BY c.customer_id, c.name
        ORDER BY total_spent DESC
        """
    )
    revenue_rows = cursor.fetchall()
    print("1) Total Money Spent Per Customer:")
    for name, total_spent in revenue_rows:
        print(f"{name}: ${total_spent}")
    export_revenue_report(revenue_rows)

    # 2) most ordered product by total quantity
    cursor.execute(
        """
        SELECT p.name, SUM(o.quantity) AS total_quantity
        FROM products p
        JOIN orders o ON p.product_id = o.product_id
        GROUP BY p.product_id, p.name
        ORDER BY total_quantity DESC
        LIMIT 1
        """
    )
    most_ordered_product = cursor.fetchone()
    print("2) Most Ordered Product (By Total Quantity):", most_ordered_product[0] if most_ordered_product else "None")

    # 3) customers who placed more than 2 orders (HAVING COUNT)
    cursor.execute(
        """
        SELECT c.name, COUNT(o.order_id) AS order_count
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id, c.name
        HAVING COUNT(o.order_id) > 2
        ORDER BY order_count DESC, c.name
        """
    )
    results = cursor.fetchall()
    print("3) Customers Who Placed More Than 2 Orders:")
    if results:
        for name, order_count in results:
            print(f"{name}: {order_count} orders")
    else:
        print("Not Found \n")

    # 4) average order value per city (using customers.address as city)
    cursor.execute(
        """
        SELECT c.address AS city, ROUND(AVG(p.price * o.quantity), 2) AS avg_order_value
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN products p ON o.product_id = p.product_id
        GROUP BY c.address
        ORDER BY avg_order_value DESC
        """
    )
    print("4) Average Order Value Per City: ")
    results = cursor.fetchall()
    if results:
        for city, avg_order_value in results:
            print(f"{city}: ${avg_order_value}")
    else:
        print("None")

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()