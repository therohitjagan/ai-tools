from dataclasses import dataclass
from typing import List

@dataclass
class BenchmarkQuery:
    id: str
    question: str
    gold_sql: str
    complexity: str  # "simple" | "join" | "aggregation" | "subquery" | "window"
    tables: List[str]

BENCHMARK_QUERIES: List[BenchmarkQuery] = [
    # ==========================================
    # LEVEL 1: Simple Filtering & Projections (15)
    # ==========================================
    BenchmarkQuery(
        id="BM-001",
        question="List all active customers from the United States.",
        gold_sql="SELECT customer_id, first_name, last_name, email FROM customers WHERE country = 'United States' AND churn_status = 'Active';",
        complexity="simple",
        tables=["customers"]
    ),
    BenchmarkQuery(
        id="BM-002",
        question="Find products in the Software category with stock quantity greater than 5000.",
        gold_sql="SELECT product_id, product_name, unit_price, stock_quantity FROM products WHERE category = 'Software' AND stock_quantity > 5000;",
        complexity="simple",
        tables=["products"]
    ),
    BenchmarkQuery(
        id="BM-003",
        question="Show all orders that are currently in Pending status.",
        gold_sql="SELECT order_id, customer_id, order_date, status, payment_method FROM orders WHERE status = 'Pending';",
        complexity="simple",
        tables=["orders"]
    ),
    BenchmarkQuery(
        id="BM-004",
        question="List all suppliers located in Germany with rating above 4.5.",
        gold_sql="SELECT supplier_id, supplier_name, country, rating FROM suppliers WHERE country = 'Germany' AND rating > 4.5;",
        complexity="simple",
        tables=["suppliers"]
    ),
    BenchmarkQuery(
        id="BM-005",
        question="Find support tickets marked with Urgent priority.",
        gold_sql="SELECT ticket_id, customer_id, category, priority, status FROM support_tickets WHERE priority = 'Urgent';",
        complexity="simple",
        tables=["support_tickets"]
    ),
    BenchmarkQuery(
        id="BM-006",
        question="Retrieve all 5-star product reviews.",
        gold_sql="SELECT review_id, product_id, customer_id, rating, helpful_votes FROM product_reviews WHERE rating = 5;",
        complexity="simple",
        tables=["product_reviews"]
    ),
    BenchmarkQuery(
        id="BM-007",
        question="List Enterprise customers who have churned.",
        gold_sql="SELECT customer_id, first_name, last_name, email FROM customers WHERE segment = 'Enterprise' AND churn_status = 'Churned';",
        complexity="simple",
        tables=["customers"]
    ),
    BenchmarkQuery(
        id="BM-008",
        question="Find order items with quantity greater than or equal to 3 and discount greater than 0.",
        gold_sql="SELECT order_item_id, order_id, product_id, quantity, discount_percent FROM order_items WHERE quantity >= 3 AND discount_percent > 0.0;",
        complexity="simple",
        tables=["order_items"]
    ),
    BenchmarkQuery(
        id="BM-009",
        question="List products in the Furniture category with unit cost under 150 dollars.",
        gold_sql="SELECT product_id, product_name, category, unit_cost FROM products WHERE category = 'Furniture' AND unit_cost < 150.00;",
        complexity="simple",
        tables=["products"]
    ),
    BenchmarkQuery(
        id="BM-010",
        question="Show all orders paid with Wire Transfer having shipping cost less than 15 dollars.",
        gold_sql="SELECT order_id, customer_id, payment_method, shipping_cost FROM orders WHERE payment_method = 'Wire Transfer' AND shipping_cost < 15.00;",
        complexity="simple",
        tables=["orders"]
    ),
    BenchmarkQuery(
        id="BM-011",
        question="Find resolved support tickets with resolution time under 5 hours.",
        gold_sql="SELECT ticket_id, customer_id, category, resolution_hours FROM support_tickets WHERE status = 'Resolved' AND resolution_hours < 5.0;",
        complexity="simple",
        tables=["support_tickets"]
    ),
    BenchmarkQuery(
        id="BM-012",
        question="List suppliers with reliability score of at least 0.95.",
        gold_sql="SELECT supplier_id, supplier_name, reliability_score FROM suppliers WHERE reliability_score >= 0.95;",
        complexity="simple",
        tables=["suppliers"]
    ),
    BenchmarkQuery(
        id="BM-013",
        question="Find customer reviews with at least 20 helpful votes.",
        gold_sql="SELECT review_id, product_id, rating, helpful_votes FROM product_reviews WHERE helpful_votes >= 20;",
        complexity="simple",
        tables=["product_reviews"]
    ),
    BenchmarkQuery(
        id="BM-014",
        question="List all SMB customers located in Canada.",
        gold_sql="SELECT customer_id, first_name, last_name, email FROM customers WHERE segment = 'SMB' AND country = 'Canada';",
        complexity="simple",
        tables=["customers"]
    ),
    BenchmarkQuery(
        id="BM-015",
        question="Show all orders that took more than 7 days to fulfill.",
        gold_sql="SELECT order_id, customer_id, status, fulfillment_days FROM orders WHERE fulfillment_days > 7;",
        complexity="simple",
        tables=["orders"]
    ),

    # ==========================================
    # LEVEL 2: Multi-Table Joins (25)
    # ==========================================
    BenchmarkQuery(
        id="BM-016",
        question="Show customer names and their order IDs for delivered orders.",
        gold_sql="""SELECT c.first_name, c.last_name, o.order_id, o.order_date
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.status = 'Delivered';""",
        complexity="join",
        tables=["customers", "orders"]
    ),
    BenchmarkQuery(
        id="BM-017",
        question="List each product along with the name and country of its supplier.",
        gold_sql="""SELECT p.product_name, p.category, s.supplier_name, s.country
FROM products p
JOIN suppliers s ON p.supplier_id = s.supplier_id;""",
        complexity="join",
        tables=["products", "suppliers"]
    ),
    BenchmarkQuery(
        id="BM-018",
        question="Get order details including customer email, product name, and quantity ordered.",
        gold_sql="""SELECT c.email, p.product_name, oi.quantity, oi.unit_price
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id;""",
        complexity="join",
        tables=["customers", "orders", "order_items", "products"]
    ),
    BenchmarkQuery(
        id="BM-019",
        question="Show all customer support tickets along with the customer segment and country.",
        gold_sql="""SELECT st.ticket_id, c.segment, c.country, st.category, st.priority, st.status
FROM support_tickets st
JOIN customers c ON st.customer_id = c.customer_id;""",
        complexity="join",
        tables=["support_tickets", "customers"]
    ),
    BenchmarkQuery(
        id="BM-020",
        question="Find customer reviews on Electronics products including review rating and product name.",
        gold_sql="""SELECT pr.review_id, p.product_name, pr.rating, pr.review_date
FROM product_reviews pr
JOIN products p ON pr.product_id = p.product_id
WHERE p.category = 'Electronics';""",
        complexity="join",
        tables=["product_reviews", "products"]
    ),
    BenchmarkQuery(
        id="BM-021",
        question="List orders placed by customers in Germany along with the customer name and order status.",
        gold_sql="""SELECT o.order_id, c.first_name, c.last_name, c.country, o.status
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE c.country = 'Germany';""",
        complexity="join",
        tables=["orders", "customers"]
    ),
    BenchmarkQuery(
        id="BM-022",
        question="Display products supplied by suppliers with a rating greater than 4.6.",
        gold_sql="""SELECT p.product_id, p.product_name, s.supplier_name, s.rating
FROM products p
JOIN suppliers s ON p.supplier_id = s.supplier_id
WHERE s.rating > 4.6;""",
        complexity="join",
        tables=["products", "suppliers"]
    ),
    BenchmarkQuery(
        id="BM-023",
        question="Show customer full names who gave 1-star reviews along with the product reviewed.",
        gold_sql="""SELECT c.first_name || ' ' || c.last_name AS customer_name, p.product_name, pr.rating
FROM product_reviews pr
JOIN customers c ON pr.customer_id = c.customer_id
JOIN products p ON pr.product_id = p.product_id
WHERE pr.rating = 1;""",
        complexity="join",
        tables=["product_reviews", "customers", "products"]
    ),
    BenchmarkQuery(
        id="BM-024",
        question="Find delivered orders for Laptops including customer ID, order date, and quantity.",
        gold_sql="""SELECT o.order_id, o.customer_id, o.order_date, oi.quantity
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.status = 'Delivered' AND p.subcategory = 'Laptops';""",
        complexity="join",
        tables=["orders", "order_items", "products"]
    ),
    BenchmarkQuery(
        id="BM-025",
        question="List customer names with unresolved support tickets and their order counts.",
        gold_sql="""SELECT DISTINCT c.customer_id, c.first_name, c.last_name, st.category, st.priority
FROM customers c
JOIN support_tickets st ON c.customer_id = st.customer_id
WHERE st.status != 'Resolved';""",
        complexity="join",
        tables=["customers", "support_tickets"]
    ),
    BenchmarkQuery(
        id="BM-026",
        question="Show products and their supplier names for items with unit price over 1000.",
        gold_sql="""SELECT p.product_name, p.unit_price, s.supplier_name
FROM products p
JOIN suppliers s ON p.supplier_id = s.supplier_id
WHERE p.unit_price > 1000;""",
        complexity="join",
        tables=["products", "suppliers"]
    ),
    BenchmarkQuery(
        id="BM-027",
        question="Retrieve all cancelled orders along with customer name and payment method.",
        gold_sql="""SELECT o.order_id, c.first_name, c.last_name, o.payment_method, o.order_date
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.status = 'Cancelled';""",
        complexity="join",
        tables=["orders", "customers"]
    ),
    BenchmarkQuery(
        id="BM-028",
        question="Find all order items for products in the Office Supplies category.",
        gold_sql="""SELECT oi.order_item_id, oi.order_id, p.product_name, oi.quantity, oi.unit_price
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
WHERE p.category = 'Office Supplies';""",
        complexity="join",
        tables=["order_items", "products"]
    ),
    BenchmarkQuery(
        id="BM-029",
        question="List customers and tickets where the ticket satisfaction score was 1 or 2.",
        gold_sql="""SELECT c.customer_id, c.first_name, c.last_name, st.ticket_id, st.satisfaction_score
FROM customers c
JOIN support_tickets st ON c.customer_id = st.customer_id
WHERE st.satisfaction_score <= 2;""",
        complexity="join",
        tables=["customers", "support_tickets"]
    ),
    BenchmarkQuery(
        id="BM-030",
        question="Display products reviewed by customers located in France.",
        gold_sql="""SELECT DISTINCT p.product_id, p.product_name, c.country
FROM product_reviews pr
JOIN products p ON pr.product_id = p.product_id
JOIN customers c ON pr.customer_id = c.customer_id
WHERE c.country = 'France';""",
        complexity="join",
        tables=["product_reviews", "products", "customers"]
    ),
    BenchmarkQuery(
        id="BM-031",
        question="Show delivered order items that received discounts over 10 percent.",
        gold_sql="""SELECT o.order_id, oi.product_id, oi.unit_price, oi.discount_percent
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Delivered' AND oi.discount_percent > 0.10;""",
        complexity="join",
        tables=["orders", "order_items"]
    ),
    BenchmarkQuery(
        id="BM-032",
        question="List all suppliers providing products in the Audio subcategory.",
        gold_sql="""SELECT DISTINCT s.supplier_id, s.supplier_name, s.country
FROM suppliers s
JOIN products p ON s.supplier_id = p.supplier_id
WHERE p.subcategory = 'Audio';""",
        complexity="join",
        tables=["suppliers", "products"]
    ),
    BenchmarkQuery(
        id="BM-033",
        question="Find customers who opened support tickets in the Billing category.",
        gold_sql="""SELECT DISTINCT c.customer_id, c.first_name, c.last_name, c.email
FROM customers c
JOIN support_tickets st ON c.customer_id = st.customer_id
WHERE st.category = 'Billing';""",
        complexity="join",
        tables=["customers", "support_tickets"]
    ),
    BenchmarkQuery(
        id="BM-034",
        question="Display orders that include products manufactured in Japan.",
        gold_sql="""SELECT DISTINCT o.order_id, o.order_date, s.supplier_name, s.country
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
JOIN suppliers s ON p.supplier_id = s.supplier_id
WHERE s.country = 'Japan';""",
        complexity="join",
        tables=["orders", "order_items", "products", "suppliers"]
    ),
    BenchmarkQuery(
        id="BM-035",
        question="Show customer reviews on products supplied by TechSupply Global.",
        gold_sql="""SELECT pr.review_id, p.product_name, pr.rating, s.supplier_name
FROM product_reviews pr
JOIN products p ON pr.product_id = p.product_id
JOIN suppliers s ON p.supplier_id = s.supplier_id
WHERE s.supplier_name = 'TechSupply Global';""",
        complexity="join",
        tables=["product_reviews", "products", "suppliers"]
    ),
    BenchmarkQuery(
        id="BM-036",
        question="List refunded orders along with the customer segment and shipping cost.",
        gold_sql="""SELECT o.order_id, c.customer_id, c.segment, o.shipping_cost, o.status
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.status = 'Refunded';""",
        complexity="join",
        tables=["orders", "customers"]
    ),
    BenchmarkQuery(
        id="BM-037",
        question="Find customer names who purchased ErgoGrip Wireless Mouse.",
        gold_sql="""SELECT DISTINCT c.first_name, c.last_name, c.email
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE p.product_name = 'ErgoGrip Wireless Mouse';""",
        complexity="join",
        tables=["customers", "orders", "order_items", "products"]
    ),
    BenchmarkQuery(
        id="BM-038",
        question="List support tickets opened by churned customers.",
        gold_sql="""SELECT st.ticket_id, c.customer_id, c.churn_status, st.category, st.status
FROM support_tickets st
JOIN customers c ON st.customer_id = c.customer_id
WHERE c.churn_status = 'Churned';""",
        complexity="join",
        tables=["support_tickets", "customers"]
    ),
    BenchmarkQuery(
        id="BM-039",
        question="Show suppliers who supply products that have received at least one review.",
        gold_sql="""SELECT DISTINCT s.supplier_id, s.supplier_name
FROM suppliers s
JOIN products p ON s.supplier_id = p.supplier_id
JOIN product_reviews pr ON p.product_id = pr.product_id;""",
        complexity="join",
        tables=["suppliers", "products", "product_reviews"]
    ),
    BenchmarkQuery(
        id="BM-040",
        question="Find products ordered via Credit Card with quantity greater than 2.",
        gold_sql="""SELECT DISTINCT p.product_id, p.product_name, o.payment_method
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.payment_method = 'Credit Card' AND oi.quantity > 2;""",
        complexity="join",
        tables=["products", "order_items", "orders"]
    ),

    # ==========================================
    # LEVEL 3: Aggregations & GROUP BY / HAVING (20)
    # ==========================================
    BenchmarkQuery(
        id="BM-041",
        question="Count the number of customers in each country.",
        gold_sql="""SELECT country, COUNT(customer_id) AS customer_count
FROM customers
GROUP BY country
ORDER BY customer_count DESC;""",
        complexity="aggregation",
        tables=["customers"]
    ),
    BenchmarkQuery(
        id="BM-042",
        question="Calculate total revenue generated by each product category.",
        gold_sql="""SELECT p.category, ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent)), 2) AS total_revenue
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'Delivered'
GROUP BY p.category
ORDER BY total_revenue DESC;""",
        complexity="aggregation",
        tables=["products", "order_items", "orders"]
    ),
    BenchmarkQuery(
        id="BM-043",
        question="Find the average rating and review count for each product.",
        gold_sql="""SELECT p.product_id, p.product_name, ROUND(AVG(pr.rating), 2) AS avg_rating, COUNT(pr.review_id) AS total_reviews
FROM products p
JOIN product_reviews pr ON p.product_id = pr.product_id
GROUP BY p.product_id, p.product_name
ORDER BY avg_rating DESC, total_reviews DESC;""",
        complexity="aggregation",
        tables=["products", "product_reviews"]
    ),
    BenchmarkQuery(
        id="BM-044",
        question="Calculate the total amount spent by each customer on delivered orders.",
        gold_sql="""SELECT c.customer_id, c.first_name, c.last_name, ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent)), 2) AS total_spent
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Delivered'
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY total_spent DESC;""",
        complexity="aggregation",
        tables=["customers", "orders", "order_items"]
    ),
    BenchmarkQuery(
        id="BM-045",
        question="Find countries having more than 10 customers.",
        gold_sql="""SELECT country, COUNT(customer_id) AS customer_count
FROM customers
GROUP BY country
HAVING COUNT(customer_id) > 10
ORDER BY customer_count DESC;""",
        complexity="aggregation",
        tables=["customers"]
    ),
    BenchmarkQuery(
        id="BM-046",
        question="Compute average resolution time for support tickets grouped by priority.",
        gold_sql="""SELECT priority, ROUND(AVG(resolution_hours), 2) AS avg_resolution_time, COUNT(ticket_id) AS ticket_count
FROM support_tickets
WHERE status = 'Resolved' AND resolution_hours IS NOT NULL
GROUP BY priority
ORDER BY avg_resolution_time ASC;""",
        complexity="aggregation",
        tables=["support_tickets"]
    ),
    BenchmarkQuery(
        id="BM-047",
        question="Calculate total units sold and total orders for each product.",
        gold_sql="""SELECT p.product_id, p.product_name, SUM(oi.quantity) AS total_units_sold, COUNT(DISTINCT oi.order_id) AS order_count
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.product_name
ORDER BY total_units_sold DESC;""",
        complexity="aggregation",
        tables=["products", "order_items"]
    ),
    BenchmarkQuery(
        id="BM-048",
        question="Find customer segments with total order count exceeding 50.",
        gold_sql="""SELECT c.segment, COUNT(o.order_id) AS total_orders
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.segment
HAVING COUNT(o.order_id) > 50
ORDER BY total_orders DESC;""",
        complexity="aggregation",
        tables=["customers", "orders"]
    ),
    BenchmarkQuery(
        id="BM-049",
        question="Calculate average fulfillment days by order status.",
        gold_sql="""SELECT status, ROUND(AVG(fulfillment_days), 2) AS avg_fulfillment_days
FROM orders
GROUP BY status
ORDER BY avg_fulfillment_days DESC;""",
        complexity="aggregation",
        tables=["orders"]
    ),
    BenchmarkQuery(
        id="BM-050",
        question="Find products with average review rating less than 3.5.",
        gold_sql="""SELECT p.product_id, p.product_name, ROUND(AVG(pr.rating), 2) AS avg_rating
FROM products p
JOIN product_reviews pr ON p.product_id = pr.product_id
GROUP BY p.product_id, p.product_name
HAVING AVG(pr.rating) < 3.5
ORDER BY avg_rating ASC;""",
        complexity="aggregation",
        tables=["products", "product_reviews"]
    ),
    BenchmarkQuery(
        id="BM-051",
        question="Count total orders by payment method.",
        gold_sql="""SELECT payment_method, COUNT(order_id) AS order_count
FROM orders
GROUP BY payment_method
ORDER BY order_count DESC;""",
        complexity="aggregation",
        tables=["orders"]
    ),
    BenchmarkQuery(
        id="BM-052",
        question="Calculate total shipping revenue collected per customer segment.",
        gold_sql="""SELECT c.segment, ROUND(SUM(o.shipping_cost), 2) AS total_shipping
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.segment
ORDER BY total_shipping DESC;""",
        complexity="aggregation",
        tables=["customers", "orders"]
    ),
    BenchmarkQuery(
        id="BM-053",
        question="Find suppliers who supply more than 2 products.",
        gold_sql="""SELECT s.supplier_id, s.supplier_name, COUNT(p.product_id) AS product_count
FROM suppliers s
JOIN products p ON s.supplier_id = p.supplier_id
GROUP BY s.supplier_id, s.supplier_name
HAVING COUNT(p.product_id) > 2
ORDER BY product_count DESC;""",
        complexity="aggregation",
        tables=["suppliers", "products"]
    ),
    BenchmarkQuery(
        id="BM-054",
        question="Count support tickets by category and satisfaction score.",
        gold_sql="""SELECT category, satisfaction_score, COUNT(ticket_id) AS count
FROM support_tickets
WHERE satisfaction_score IS NOT NULL
GROUP BY category, satisfaction_score
ORDER BY category, satisfaction_score;""",
        complexity="aggregation",
        tables=["support_tickets"]
    ),
    BenchmarkQuery(
        id="BM-055",
        question="Find subcategories with total stock quantity greater than 300.",
        gold_sql="""SELECT subcategory, SUM(stock_quantity) AS total_stock
FROM products
GROUP BY subcategory
HAVING SUM(stock_quantity) > 300
ORDER BY total_stock DESC;""",
        complexity="aggregation",
        tables=["products"]
    ),
    BenchmarkQuery(
        id="BM-056",
        question="Calculate the total discount amount given on delivered orders.",
        gold_sql="""SELECT ROUND(SUM(oi.quantity * oi.unit_price * oi.discount_percent), 2) AS total_discount_given
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'Delivered';""",
        complexity="aggregation",
        tables=["order_items", "orders"]
    ),
    BenchmarkQuery(
        id="BM-057",
        question="Find customer segments where churned customers represent more than 5 accounts.",
        gold_sql="""SELECT segment, COUNT(customer_id) AS churned_count
FROM customers
WHERE churn_status = 'Churned'
GROUP BY segment
HAVING COUNT(customer_id) > 5
ORDER BY churned_count DESC;""",
        complexity="aggregation",
        tables=["customers"]
    ),
    BenchmarkQuery(
        id="BM-058",
        question="Calculate the average unit cost and average unit price per product category.",
        gold_sql="""SELECT category, ROUND(AVG(unit_cost), 2) AS avg_cost, ROUND(AVG(unit_price), 2) AS avg_price
FROM products
GROUP BY category
ORDER BY category;""",
        complexity="aggregation",
        tables=["products"]
    ),
    BenchmarkQuery(
        id="BM-059",
        question="Find products that have received more than 10 reviews.",
        gold_sql="""SELECT p.product_id, p.product_name, COUNT(pr.review_id) AS review_count
FROM products p
JOIN product_reviews pr ON p.product_id = pr.product_id
GROUP BY p.product_id, p.product_name
HAVING COUNT(pr.review_id) > 10
ORDER BY review_count DESC;""",
        complexity="aggregation",
        tables=["products", "product_reviews"]
    ),
    BenchmarkQuery(
        id="BM-060",
        question="Count orders grouped by order year and month.",
        gold_sql="""SELECT strftime('%Y-%m', order_date) AS order_month, COUNT(order_id) AS order_count
FROM orders
GROUP BY order_month
ORDER BY order_month ASC;""",
        complexity="aggregation",
        tables=["orders"]
    ),

    # ==========================================
    # LEVEL 4: Nested Subqueries & Correlated Subqueries (25)
    # ==========================================
    BenchmarkQuery(
        id="BM-061",
        question="Find customers who have never placed an order.",
        gold_sql="""SELECT customer_id, first_name, last_name, email
FROM customers
WHERE customer_id NOT IN (SELECT DISTINCT customer_id FROM orders);""",
        complexity="subquery",
        tables=["customers", "orders"]
    ),
    BenchmarkQuery(
        id="BM-062",
        question="List products whose unit price is strictly above the average product unit price.",
        gold_sql="""SELECT product_id, product_name, unit_price
FROM products
WHERE unit_price > (SELECT AVG(unit_price) FROM products)
ORDER BY unit_price DESC;""",
        complexity="subquery",
        tables=["products"]
    ),
    BenchmarkQuery(
        id="BM-063",
        question="Find customers who have spent more than the average customer spending on delivered orders.",
        gold_sql="""WITH cust_spend AS (
    SELECT o.customer_id, SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent)) AS total_spent
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status = 'Delivered'
    GROUP BY o.customer_id
)
SELECT c.customer_id, c.first_name, c.last_name, ROUND(cs.total_spent, 2) AS total_spent
FROM cust_spend cs
JOIN customers c ON cs.customer_id = c.customer_id
WHERE cs.total_spent > (SELECT AVG(total_spent) FROM cust_spend)
ORDER BY cs.total_spent DESC;""",
        complexity="subquery",
        tables=["orders", "order_items", "customers"]
    ),
    BenchmarkQuery(
        id="BM-064",
        question="List products whose price is greater than the average price in their respective category.",
        gold_sql="""SELECT p1.product_id, p1.product_name, p1.category, p1.unit_price
FROM products p1
WHERE p1.unit_price > (
    SELECT AVG(p2.unit_price)
    FROM products p2
    WHERE p2.category = p1.category
)
ORDER BY p1.category, p1.unit_price DESC;""",
        complexity="subquery",
        tables=["products"]
    ),
    BenchmarkQuery(
        id="BM-065",
        question="Find suppliers that do not supply any product in the Software category.",
        gold_sql="""SELECT supplier_id, supplier_name, country
FROM suppliers
WHERE supplier_id NOT IN (
    SELECT DISTINCT supplier_id FROM products WHERE category = 'Software'
);""",
        complexity="subquery",
        tables=["suppliers", "products"]
    ),
    BenchmarkQuery(
        id="BM-066",
        question="Find customers who have opened support tickets but never left a product review.",
        gold_sql="""SELECT DISTINCT c.customer_id, c.first_name, c.last_name
FROM customers c
WHERE c.customer_id IN (SELECT customer_id FROM support_tickets)
  AND c.customer_id NOT IN (SELECT customer_id FROM product_reviews);""",
        complexity="subquery",
        tables=["customers", "support_tickets", "product_reviews"]
    ),
    BenchmarkQuery(
        id="BM-067",
        question="List orders whose shipping cost is higher than the average shipping cost of all orders.",
        gold_sql="""SELECT order_id, customer_id, shipping_cost
FROM orders
WHERE shipping_cost > (SELECT AVG(shipping_cost) FROM orders)
ORDER BY shipping_cost DESC;""",
        complexity="subquery",
        tables=["orders"]
    ),
    BenchmarkQuery(
        id="BM-068",
        question="Find products that have never been ordered.",
        gold_sql="""SELECT product_id, product_name, category
FROM products
WHERE product_id NOT IN (SELECT DISTINCT product_id FROM order_items);""",
        complexity="subquery",
        tables=["products", "order_items"]
    ),
    BenchmarkQuery(
        id="BM-069",
        question="List customers whose total number of orders is greater than the average orders per customer.",
        gold_sql="""WITH order_counts AS (
    SELECT customer_id, COUNT(order_id) AS num_orders
    FROM orders
    GROUP BY customer_id
)
SELECT c.customer_id, c.first_name, c.last_name, oc.num_orders
FROM order_counts oc
JOIN customers c ON oc.customer_id = c.customer_id
WHERE oc.num_orders > (SELECT AVG(num_orders) FROM order_counts)
ORDER BY oc.num_orders DESC;""",
        complexity="subquery",
        tables=["orders", "customers"]
    ),
    BenchmarkQuery(
        id="BM-070",
        question="Find products that have received a review rating lower than the overall average review rating.",
        gold_sql="""SELECT DISTINCT p.product_id, p.product_name, pr.rating
FROM products p
JOIN product_reviews pr ON p.product_id = pr.product_id
WHERE pr.rating < (SELECT AVG(rating) FROM product_reviews)
ORDER BY pr.rating ASC;""",
        complexity="subquery",
        tables=["products", "product_reviews"]
    ),
    BenchmarkQuery(
        id="BM-071",
        question="Find customers who have placed at least one order with total items greater than 5.",
        gold_sql="""SELECT customer_id, first_name, last_name
FROM customers
WHERE customer_id IN (
    SELECT o.customer_id
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.order_id, o.customer_id
    HAVING SUM(oi.quantity) > 5
);""",
        complexity="subquery",
        tables=["customers", "orders", "order_items"]
    ),
    BenchmarkQuery(
        id="BM-072",
        question="List suppliers whose average product cost is greater than 100 dollars.",
        gold_sql="""SELECT s.supplier_id, s.supplier_name
FROM suppliers s
WHERE (
    SELECT AVG(p.unit_cost)
    FROM products p
    WHERE p.supplier_id = s.supplier_id
) > 100.00;""",
        complexity="subquery",
        tables=["suppliers", "products"]
    ),
    BenchmarkQuery(
        id="BM-073",
        question="Find customers with support tickets whose resolution time exceeded the 75th percentile average of 24 hours.",
        gold_sql="""SELECT DISTINCT c.customer_id, c.first_name, c.last_name
FROM customers c
JOIN support_tickets st ON c.customer_id = st.customer_id
WHERE st.resolution_hours > 24.0;""",
        complexity="subquery",
        tables=["customers", "support_tickets"]
    ),
    BenchmarkQuery(
        id="BM-074",
        question="List products whose profit margin (unit price minus unit cost) is greater than the average profit margin.",
        gold_sql="""SELECT product_id, product_name, ROUND(unit_price - unit_cost, 2) AS profit_margin
FROM products
WHERE (unit_price - unit_cost) > (SELECT AVG(unit_price - unit_cost) FROM products)
ORDER BY profit_margin DESC;""",
        complexity="subquery",
        tables=["products"]
    ),
    BenchmarkQuery(
        id="BM-075",
        question="Find customers who have placed delivered orders in both 2025 and 2026.",
        gold_sql="""SELECT customer_id, first_name, last_name
FROM customers
WHERE customer_id IN (
    SELECT customer_id FROM orders WHERE strftime('%Y', order_date) = '2025' AND status = 'Delivered'
)
AND customer_id IN (
    SELECT customer_id FROM orders WHERE strftime('%Y', order_date) = '2026' AND status = 'Delivered'
);""",
        complexity="subquery",
        tables=["customers", "orders"]
    ),
    BenchmarkQuery(
        id="BM-076",
        question="List orders that contain the single most expensive product in inventory.",
        gold_sql="""SELECT DISTINCT order_id
FROM order_items
WHERE product_id = (
    SELECT product_id FROM products ORDER BY unit_price DESC LIMIT 1
);""",
        complexity="subquery",
        tables=["order_items", "products"]
    ),
    BenchmarkQuery(
        id="BM-077",
        question="Find suppliers that provide products belonging to more than one category.",
        gold_sql="""SELECT supplier_id, supplier_name
FROM suppliers
WHERE supplier_id IN (
    SELECT supplier_id
    FROM products
    GROUP BY supplier_id
    HAVING COUNT(DISTINCT category) > 1
);""",
        complexity="subquery",
        tables=["suppliers", "products"]
    ),
    BenchmarkQuery(
        id="BM-078",
        question="Find customers whose first order was cancelled.",
        gold_sql="""WITH first_orders AS (
    SELECT o.customer_id, o.status,
           ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date ASC, o.order_id ASC) AS rn
    FROM orders o
)
SELECT c.customer_id, c.first_name, c.last_name
FROM first_orders fo
JOIN customers c ON fo.customer_id = c.customer_id
WHERE fo.rn = 1 AND fo.status = 'Cancelled';""",
        complexity="subquery",
        tables=["orders", "customers"]
    ),
    BenchmarkQuery(
        id="BM-079",
        question="Find products that have received more reviews than the average review count across products.",
        gold_sql="""WITH prod_review_counts AS (
    SELECT product_id, COUNT(review_id) AS rev_count
    FROM product_reviews
    GROUP BY product_id
)
SELECT p.product_id, p.product_name, prc.rev_count
FROM prod_review_counts prc
JOIN products p ON prc.product_id = p.product_id
WHERE prc.rev_count > (SELECT AVG(rev_count) FROM prod_review_counts)
ORDER BY prc.rev_count DESC;""",
        complexity="subquery",
        tables=["product_reviews", "products"]
    ),
    BenchmarkQuery(
        id="BM-080",
        question="Find active customers who have spent more than 5000 dollars in total.",
        gold_sql="""SELECT c.customer_id, c.first_name, c.last_name
FROM customers c
WHERE c.churn_status = 'Active'
  AND c.customer_id IN (
      SELECT o.customer_id
      FROM orders o
      JOIN order_items oi ON o.order_id = oi.order_id
      WHERE o.status = 'Delivered'
      GROUP BY o.customer_id
      HAVING SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent)) > 5000.00
  );""",
        complexity="subquery",
        tables=["customers", "orders", "order_items"]
    ),
    BenchmarkQuery(
        id="BM-081",
        question="List products that have never received any review with rating 1 or 2.",
        gold_sql="""SELECT product_id, product_name
FROM products
WHERE product_id NOT IN (
    SELECT DISTINCT product_id FROM product_reviews WHERE rating IN (1, 2)
)
AND product_id IN (SELECT DISTINCT product_id FROM product_reviews);""",
        complexity="subquery",
        tables=["products", "product_reviews"]
    ),
    BenchmarkQuery(
        id="BM-082",
        question="Find customers whose average order value on delivered orders exceeds 1000 dollars.",
        gold_sql="""WITH order_totals AS (
    SELECT o.customer_id, o.order_id, SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent)) AS order_val
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status = 'Delivered'
    GROUP BY o.customer_id, o.order_id
)
SELECT c.customer_id, c.first_name, c.last_name, ROUND(AVG(ot.order_val), 2) AS avg_order_val
FROM order_totals ot
JOIN customers c ON ot.customer_id = c.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
HAVING AVG(ot.order_val) > 1000.00
ORDER BY avg_order_val DESC;""",
        complexity="subquery",
        tables=["orders", "order_items", "customers"]
    ),
    BenchmarkQuery(
        id="BM-083",
        question="Find suppliers that have a reliability score higher than the average supplier reliability score.",
        gold_sql="""SELECT supplier_id, supplier_name, reliability_score
FROM suppliers
WHERE reliability_score > (SELECT AVG(reliability_score) FROM suppliers)
ORDER BY reliability_score DESC;""",
        complexity="subquery",
        tables=["suppliers"]
    ),
    BenchmarkQuery(
        id="BM-084",
        question="List customers with support tickets where satisfaction was below their segment average satisfaction.",
        gold_sql="""WITH segment_avg AS (
    SELECT c.segment, AVG(st.satisfaction_score) AS seg_avg_sat
    FROM support_tickets st
    JOIN customers c ON st.customer_id = c.customer_id
    WHERE st.satisfaction_score IS NOT NULL
    GROUP BY c.segment
)
SELECT DISTINCT c.customer_id, c.first_name, c.last_name, c.segment, st.satisfaction_score
FROM support_tickets st
JOIN customers c ON st.customer_id = c.customer_id
JOIN segment_avg sa ON c.segment = sa.segment
WHERE st.satisfaction_score < sa.seg_avg_sat;""",
        complexity="subquery",
        tables=["support_tickets", "customers"]
    ),
    BenchmarkQuery(
        id="BM-085",
        question="Find the customer who has the highest total number of orders.",
        gold_sql="""SELECT c.customer_id, c.first_name, c.last_name, COUNT(o.order_id) AS order_count
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY order_count DESC
LIMIT 1;""",
        complexity="subquery",
        tables=["customers", "orders"]
    ),

    # ==========================================
    # LEVEL 5: Window Functions & Analytical CTEs (20)
    # ==========================================
    BenchmarkQuery(
        id="BM-086",
        question="Rank customers by total spending on delivered orders using DENSE_RANK.",
        gold_sql="""SELECT c.customer_id,
       c.first_name || ' ' || c.last_name AS customer_name,
       ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent)), 2) AS total_spend,
       DENSE_RANK() OVER (ORDER BY SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent)) DESC) AS spend_rank
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Delivered'
GROUP BY c.customer_id, customer_name
ORDER BY spend_rank ASC;""",
        complexity="window",
        tables=["customers", "orders", "order_items"]
    ),
    BenchmarkQuery(
        id="BM-087",
        question="Rank products by unit price within each category using ROW_NUMBER.",
        gold_sql="""SELECT product_id,
       product_name,
       category,
       unit_price,
       ROW_NUMBER() OVER (PARTITION BY category ORDER BY unit_price DESC) AS price_rank
FROM products
ORDER BY category, price_rank;""",
        complexity="window",
        tables=["products"]
    ),
    BenchmarkQuery(
        id="BM-088",
        question="Calculate cumulative running revenue across delivered orders ordered by date.",
        gold_sql="""SELECT o.order_id,
       o.order_date,
       ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent)), 2) AS order_revenue,
       ROUND(SUM(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent))) OVER (
           ORDER BY o.order_date, o.order_id
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ), 2) AS cumulative_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Delivered'
GROUP BY o.order_id, o.order_date
ORDER BY o.order_date, o.order_id;""",
        complexity="window",
        tables=["orders", "order_items"]
    ),
    BenchmarkQuery(
        id="BM-089",
        question="Find the chronological order sequence number for each customer using ROW_NUMBER.",
        gold_sql="""SELECT order_id,
       customer_id,
       order_date,
       status,
       ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date ASC, order_id ASC) AS order_sequence
FROM orders
ORDER BY customer_id, order_sequence;""",
        complexity="window",
        tables=["orders"]
    ),
    BenchmarkQuery(
        id="BM-090",
        question="Rank suppliers by their rating within each country using RANK.",
        gold_sql="""SELECT supplier_id,
       supplier_name,
       country,
       rating,
       RANK() OVER (PARTITION BY country ORDER BY rating DESC) AS country_rank
FROM suppliers
ORDER BY country, country_rank;""",
        complexity="window",
        tables=["suppliers"]
    ),
    BenchmarkQuery(
        id="BM-091",
        question="Calculate each product category's percentage of total delivered revenue.",
        gold_sql="""WITH cat_rev AS (
    SELECT p.category,
           ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent)), 2) AS revenue
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.status = 'Delivered'
    GROUP BY p.category
)
SELECT category,
       revenue,
       ROUND(revenue * 100.0 / SUM(revenue) OVER (), 2) AS pct_of_total
FROM cat_rev
ORDER BY revenue DESC;""",
        complexity="window",
        tables=["products", "order_items", "orders"]
    ),
    BenchmarkQuery(
        id="BM-092",
        question="Find the top 2 highest unit price products per category using a CTE and DENSE_RANK.",
        gold_sql="""WITH ranked_prods AS (
    SELECT product_id, product_name, category, unit_price,
           DENSE_RANK() OVER (PARTITION BY category ORDER BY unit_price DESC) AS rnk
    FROM products
)
SELECT product_id, product_name, category, unit_price, rnk
FROM ranked_prods
WHERE rnk <= 2
ORDER BY category, rnk;""",
        complexity="window",
        tables=["products"]
    ),
    BenchmarkQuery(
        id="BM-093",
        question="Compute running total of products in stock ordered by product ID.",
        gold_sql="""SELECT product_id,
       product_name,
       stock_quantity,
       SUM(stock_quantity) OVER (ORDER BY product_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_stock
FROM products
ORDER BY product_id;""",
        complexity="window",
        tables=["products"]
    ),
    BenchmarkQuery(
        id="BM-094",
        question="Rank support tickets chronologically for each customer.",
        gold_sql="""SELECT ticket_id,
       customer_id,
       category,
       open_date,
       ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY open_date ASC, ticket_id ASC) AS ticket_seq
FROM support_tickets
ORDER BY customer_id, ticket_seq;""",
        complexity="window",
        tables=["support_tickets"]
    ),
    BenchmarkQuery(
        id="BM-095",
        question="Rank customers by total spend within each segment, selecting the top 3 per segment.",
        gold_sql="""WITH seg_ranks AS (
    SELECT c.customer_id,
           c.first_name || ' ' || c.last_name AS customer_name,
           c.segment,
           ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent)), 2) AS spend,
           DENSE_RANK() OVER (
               PARTITION BY c.segment
               ORDER BY SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent)) DESC
           ) AS seg_rank
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status = 'Delivered'
    GROUP BY c.customer_id, customer_name, c.segment
)
SELECT customer_id, customer_name, segment, spend, seg_rank
FROM seg_ranks
WHERE seg_rank <= 3
ORDER BY segment, seg_rank;""",
        complexity="window",
        tables=["customers", "orders", "order_items"]
    ),
    BenchmarkQuery(
        id="BM-096",
        question="Calculate previous order date for each customer using LAG.",
        gold_sql="""SELECT order_id,
       customer_id,
       order_date,
       LAG(order_date, 1) OVER (PARTITION BY customer_id ORDER BY order_date ASC, order_id ASC) AS prev_order_date
FROM orders
ORDER BY customer_id, order_date;""",
        complexity="window",
        tables=["orders"]
    ),
    BenchmarkQuery(
        id="BM-097",
        question="Rank product reviews by helpful votes within each star rating tier.",
        gold_sql="""SELECT review_id,
       product_id,
       rating,
       helpful_votes,
       DENSE_RANK() OVER (PARTITION BY rating ORDER BY helpful_votes DESC) AS vote_rank
FROM product_reviews
ORDER BY rating DESC, vote_rank ASC;""",
        complexity="window",
        tables=["product_reviews"]
    ),
    BenchmarkQuery(
        id="BM-098",
        question="Compute running total of shipping costs collected over orders ordered by order date.",
        gold_sql="""SELECT order_id,
       order_date,
       shipping_cost,
       ROUND(SUM(shipping_cost) OVER (ORDER BY order_date, order_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS running_shipping_cost
FROM orders
ORDER BY order_date, order_id;""",
        complexity="window",
        tables=["orders"]
    ),
    BenchmarkQuery(
        id="BM-099",
        question="Find customer signups partitioned by country and ordered chronologically with ROW_NUMBER.",
        gold_sql="""SELECT customer_id,
       country,
       signup_date,
       ROW_NUMBER() OVER (PARTITION BY country ORDER BY signup_date ASC, customer_id ASC) AS signup_seq
FROM customers
ORDER BY country, signup_seq;""",
        complexity="window",
        tables=["customers"]
    ),
    BenchmarkQuery(
        id="BM-100",
        question="Calculate the lead order date for each customer's orders using LEAD.",
        gold_sql="""SELECT order_id,
       customer_id,
       order_date,
       LEAD(order_date, 1) OVER (PARTITION BY customer_id ORDER BY order_date ASC, order_id ASC) AS next_order_date
FROM orders
ORDER BY customer_id, order_date;""",
        complexity="window",
        tables=["orders"]
    ),
    BenchmarkQuery(
        id="BM-101",
        question="Rank product categories by total units sold using RANK.",
        gold_sql="""WITH cat_units AS (
    SELECT p.category, SUM(oi.quantity) AS total_units
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    GROUP BY p.category
)
SELECT category, total_units, RANK() OVER (ORDER BY total_units DESC) AS units_rank
FROM cat_units
ORDER BY units_rank;""",
        complexity="window",
        tables=["products", "order_items"]
    ),
    BenchmarkQuery(
        id="BM-102",
        question="Calculate difference in revenue between current order and previous order using LAG.",
        gold_sql="""WITH order_revs AS (
    SELECT o.order_id, o.order_date, ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent)), 2) AS rev
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status = 'Delivered'
    GROUP BY o.order_id, o.order_date
)
SELECT order_id, order_date, rev,
       LAG(rev, 1) OVER (ORDER BY order_date, order_id) AS prev_rev,
       ROUND(rev - LAG(rev, 1) OVER (ORDER BY order_date, order_id), 2) AS rev_diff
FROM order_revs
ORDER BY order_date, order_id;""",
        complexity="window",
        tables=["orders", "order_items"]
    ),
    BenchmarkQuery(
        id="BM-103",
        question="Rank customers by ticket resolution satisfaction within each segment.",
        gold_sql="""SELECT c.customer_id,
       c.segment,
       ROUND(AVG(st.satisfaction_score), 2) AS avg_sat,
       DENSE_RANK() OVER (PARTITION BY c.segment ORDER BY AVG(st.satisfaction_score) DESC) AS sat_rank
FROM customers c
JOIN support_tickets st ON c.customer_id = st.customer_id
WHERE st.satisfaction_score IS NOT NULL
GROUP BY c.customer_id, c.segment
ORDER BY c.segment, sat_rank;""",
        complexity="window",
        tables=["customers", "support_tickets"]
    ),
    BenchmarkQuery(
        id="BM-104",
        question="Calculate cumulative count of reviews over time ordered by review date.",
        gold_sql="""SELECT review_id,
       product_id,
       review_date,
       COUNT(review_id) OVER (ORDER BY review_date, review_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_review_count
FROM product_reviews
ORDER BY review_date, review_id;""",
        complexity="window",
        tables=["product_reviews"]
    ),
    BenchmarkQuery(
        id="BM-105",
        question="Compute running average product price within each category ordered by unit price.",
        gold_sql="""SELECT product_id,
       product_name,
       category,
       unit_price,
       ROUND(AVG(unit_price) OVER (PARTITION BY category ORDER BY unit_price ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS running_avg_price
FROM products
ORDER BY category, unit_price;""",
        complexity="window",
        tables=["products"]
    )
]

def get_benchmark_dataset() -> List[BenchmarkQuery]:
    return BENCHMARK_QUERIES
