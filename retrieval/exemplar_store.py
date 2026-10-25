from dataclasses import dataclass
from typing import List

@dataclass
class GoldenExemplar:
    id: str
    question: str
    sql: str
    complexity: str  # "simple" | "join" | "aggregation" | "subquery" | "window"
    tables: List[str]
    description: str

EXEMPLARS_DATABASE: List[GoldenExemplar] = [
    # 1. Simple Filtering & Projections
    GoldenExemplar(
        id="EX-001",
        question="List all active customers located in Germany who signed up after January 2025.",
        sql="SELECT customer_id, first_name, last_name, email FROM customers WHERE country = 'Germany' AND churn_status = 'Active' AND signup_date >= '2025-01-01' ORDER BY signup_date DESC;",
        complexity="simple",
        tables=["customers"],
        description="Filter by country, churn status, and signup date with order by."
    ),
    GoldenExemplar(
        id="EX-002",
        question="Show all products in the Electronics category with unit price greater than 500 dollars.",
        sql="SELECT product_id, product_name, subcategory, unit_price FROM products WHERE category = 'Electronics' AND unit_price > 500.00 ORDER BY unit_price DESC;",
        complexity="simple",
        tables=["products"],
        description="Filter products by category and minimum unit price."
    ),
    GoldenExemplar(
        id="EX-003",
        question="Find all support tickets with Urgent priority that are currently unresolved.",
        sql="SELECT ticket_id, customer_id, category, open_date FROM support_tickets WHERE priority = 'Urgent' AND status IN ('Open', 'In Progress', 'Escalated') ORDER BY open_date ASC;",
        complexity="simple",
        tables=["support_tickets"],
        description="Filter tickets by priority and unresolved status."
    ),
    GoldenExemplar(
        id="EX-004",
        question="List suppliers with a reliability score above 0.90 located in Germany or Japan.",
        sql="SELECT supplier_id, supplier_name, country, reliability_score FROM suppliers WHERE reliability_score > 0.90 AND country IN ('Germany', 'Japan') ORDER BY reliability_score DESC;",
        complexity="simple",
        tables=["suppliers"],
        description="Filter suppliers by country list and reliability threshold."
    ),
    GoldenExemplar(
        id="EX-005",
        question="Find all orders that were cancelled or refunded with shipping cost greater than 20 dollars.",
        sql="SELECT order_id, customer_id, order_date, status, shipping_cost FROM orders WHERE status IN ('Cancelled', 'Refunded') AND shipping_cost > 20.00 ORDER BY shipping_cost DESC;",
        complexity="simple",
        tables=["orders"],
        description="Filter orders by status enumeration and shipping cost."
    ),

    # 2. Multi-Table Joins (2, 3, 4 tables)
    GoldenExemplar(
        id="EX-006",
        question="Get the full name, email, order date, and status of orders placed by Enterprise customers.",
        sql="""SELECT c.customer_id, c.first_name, c.last_name, c.email, o.order_id, o.order_date, o.status
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE c.segment = 'Enterprise'
ORDER BY o.order_date DESC;""",
        complexity="join",
        tables=["customers", "orders"],
        description="Two-table join between customers and orders filtered by customer segment."
    ),
    GoldenExemplar(
        id="EX-007",
        question="List each product name, category, and its supplier's name and country.",
        sql="""SELECT p.product_id, p.product_name, p.category, s.supplier_name, s.country AS supplier_country
FROM products p
JOIN suppliers s ON p.supplier_id = s.supplier_id
ORDER BY p.category, p.product_name;""",
        complexity="join",
        tables=["products", "suppliers"],
        description="Two-table join between products and suppliers."
    ),
    GoldenExemplar(
        id="EX-008",
        question="Display the order ID, customer name, product name, and quantity ordered for all delivered orders.",
        sql="""SELECT o.order_id, c.first_name || ' ' || c.last_name AS customer_name, p.product_name, oi.quantity
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.status = 'Delivered'
ORDER BY o.order_id, oi.quantity DESC;""",
        complexity="join",
        tables=["orders", "customers", "order_items", "products"],
        description="Four-table join connecting customers, orders, order items, and products."
    ),
    GoldenExemplar(
        id="EX-009",
        question="Show customer names along with the ratings and reviews they left on products.",
        sql="""SELECT c.customer_id, c.first_name, c.last_name, p.product_name, pr.rating, pr.review_date
FROM product_reviews pr
JOIN customers c ON pr.customer_id = c.customer_id
JOIN products p ON pr.product_id = p.product_id
WHERE pr.rating >= 4
ORDER BY pr.rating DESC, pr.review_date DESC;""",
        complexity="join",
        tables=["product_reviews", "customers", "products"],
        description="Three-table join between product reviews, customers, and products."
    ),
    GoldenExemplar(
        id="EX-010",
        question="Find customer names who have open support tickets along with the ticket priority and open date.",
        sql="""SELECT c.customer_id, c.first_name, c.last_name, st.ticket_id, st.category, st.priority, st.open_date
FROM support_tickets st
JOIN customers c ON st.customer_id = c.customer_id
WHERE st.status = 'Open'
ORDER BY st.open_date ASC;""",
        complexity="join",
        tables=["support_tickets", "customers"],
        description="Two-table join between support tickets and customers for open issues."
    ),

    # 3. Aggregations, GROUP BY, and HAVING
    GoldenExemplar(
        id="EX-011",
        question="Calculate the total revenue and total units sold for each product category.",
        sql="""SELECT p.category,
       ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent)), 2) AS total_revenue,
       SUM(oi.quantity) AS total_units_sold
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'Delivered'
GROUP BY p.category
ORDER BY total_revenue DESC;""",
        complexity="aggregation",
        tables=["order_items", "products", "orders"],
        description="Multi-table aggregation computing revenue with discounts grouped by product category."
    ),
    GoldenExemplar(
        id="EX-012",
        question="Find customer segments that have generated more than 10,000 dollars in total delivered order revenue.",
        sql="""SELECT c.segment,
       ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent)), 2) AS total_segment_revenue,
       COUNT(DISTINCT o.order_id) AS total_orders
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Delivered'
GROUP BY c.segment
HAVING total_segment_revenue > 10000.00
ORDER BY total_segment_revenue DESC;""",
        complexity="aggregation",
        tables=["customers", "orders", "order_items"],
        description="Group by customer segment with HAVING clause on aggregated total revenue."
    ),
    GoldenExemplar(
        id="EX-013",
        question="What is the average resolution time in hours for each support ticket category?",
        sql="""SELECT category,
       ROUND(AVG(resolution_hours), 2) AS avg_resolution_hours,
       COUNT(*) AS total_resolved_tickets
FROM support_tickets
WHERE status = 'Resolved' AND resolution_hours IS NOT NULL
GROUP BY category
ORDER BY avg_resolution_hours ASC;""",
        complexity="aggregation",
        tables=["support_tickets"],
        description="Group by ticket category computing average resolution time for resolved tickets."
    ),
    GoldenExemplar(
        id="EX-014",
        question="Find suppliers who have supplied products with an average review rating of at least 4.0 stars.",
        sql="""SELECT s.supplier_id, s.supplier_name, ROUND(AVG(pr.rating), 2) AS avg_supplier_rating, COUNT(pr.review_id) AS review_count
FROM suppliers s
JOIN products p ON s.supplier_id = p.supplier_id
JOIN product_reviews pr ON p.product_id = pr.product_id
GROUP BY s.supplier_id, s.supplier_name
HAVING avg_supplier_rating >= 4.0
ORDER BY avg_supplier_rating DESC, review_count DESC;""",
        complexity="aggregation",
        tables=["suppliers", "products", "product_reviews"],
        description="Aggregation across suppliers, products, and reviews with HAVING filter on average rating."
    ),
    GoldenExemplar(
        id="EX-015",
        question="Show monthly order counts and total shipping costs for each month.",
        sql="""SELECT strftime('%Y-%m', order_date) AS order_month,
       COUNT(order_id) AS total_orders,
       ROUND(SUM(shipping_cost), 2) AS total_shipping_cost
FROM orders
GROUP BY order_month
ORDER BY order_month ASC;""",
        complexity="aggregation",
        tables=["orders"],
        description="Date formatting with strftime grouped by month."
    ),

    # 4. Nested Subqueries & Correlated Subqueries
    GoldenExemplar(
        id="EX-016",
        question="Find all customers who have never placed an order.",
        sql="""SELECT customer_id, first_name, last_name, email, segment
FROM customers
WHERE customer_id NOT IN (
    SELECT DISTINCT customer_id FROM orders
)
ORDER BY customer_id ASC;""",
        complexity="subquery",
        tables=["customers", "orders"],
        description="NOT IN subquery to find customers with zero recorded orders."
    ),
    GoldenExemplar(
        id="EX-017",
        question="List products whose unit price is higher than the average unit price within their category.",
        sql="""SELECT p1.product_id, p1.product_name, p1.category, p1.unit_price
FROM products p1
WHERE p1.unit_price > (
    SELECT AVG(p2.unit_price)
    FROM products p2
    WHERE p2.category = p1.category
)
ORDER BY p1.category, p1.unit_price DESC;""",
        complexity="subquery",
        tables=["products"],
        description="Correlated subquery comparing each product's price against its category average."
    ),
    GoldenExemplar(
        id="EX-018",
        question="Find customers who have spent more than the average customer lifetime spending on delivered orders.",
        sql="""WITH customer_spending AS (
    SELECT o.customer_id, SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent)) AS total_spent
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status = 'Delivered'
    GROUP BY o.customer_id
)
SELECT c.customer_id, c.first_name, c.last_name, c.email, ROUND(cs.total_spent, 2) AS total_spent
FROM customer_spending cs
JOIN customers c ON cs.customer_id = c.customer_id
WHERE cs.total_spent > (
    SELECT AVG(total_spent) FROM customer_spending
)
ORDER BY total_spent DESC;""",
        complexity="subquery",
        tables=["orders", "order_items", "customers"],
        description="CTE with subquery to filter customers above the overall average customer spend."
    ),
    GoldenExemplar(
        id="EX-019",
        question="Find products that have received at least one 1-star review but have never had a support ticket opened.",
        sql="""SELECT DISTINCT p.product_id, p.product_name, p.category
FROM products p
JOIN product_reviews pr ON p.product_id = pr.product_id
WHERE pr.rating = 1
  AND p.product_id NOT IN (
      SELECT DISTINCT oi.product_id
      FROM order_items oi
      JOIN orders o ON oi.order_id = o.order_id
      JOIN support_tickets st ON o.customer_id = st.customer_id
  )
ORDER BY p.product_name;""",
        complexity="subquery",
        tables=["products", "product_reviews", "order_items", "orders", "support_tickets"],
        description="Complex subquery with multiple join conditions and set exclusion."
    ),

    # 5. Window Functions & Analytical CTEs
    GoldenExemplar(
        id="EX-020",
        question="Rank the top 3 highest-spending customers within each customer segment.",
        sql="""WITH ranked_customers AS (
    SELECT c.customer_id,
           c.first_name || ' ' || c.last_name AS customer_name,
           c.segment,
           ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent)), 2) AS total_spent,
           DENSE_RANK() OVER (
               PARTITION BY c.segment
               ORDER BY SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent)) DESC
           ) AS spending_rank
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status = 'Delivered'
    GROUP BY c.customer_id, customer_name, c.segment
)
SELECT customer_id, customer_name, segment, total_spent, spending_rank
FROM ranked_customers
WHERE spending_rank <= 3
ORDER BY segment, spending_rank;""",
        complexity="window",
        tables=["customers", "orders", "order_items"],
        description="Analytical CTE with DENSE_RANK() OVER (PARTITION BY segment ORDER BY spend DESC)."
    ),
    GoldenExemplar(
        id="EX-021",
        question="Calculate the running cumulative revenue of delivered orders over time ordered by order date.",
        sql="""SELECT o.order_id,
       o.order_date,
       ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent)), 2) AS order_total,
       ROUND(SUM(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent))) OVER (
           ORDER BY o.order_date, o.order_id
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ), 2) AS cumulative_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Delivered'
GROUP BY o.order_id, o.order_date
ORDER BY o.order_date ASC, o.order_id ASC;""",
        complexity="window",
        tables=["orders", "order_items"],
        description="Window aggregation computing cumulative sum over order timeline."
    ),
    GoldenExemplar(
        id="EX-022",
        question="Find the row number of each customer's orders ordered chronologically to identify first and repeat purchases.",
        sql="""SELECT order_id,
       customer_id,
       order_date,
       status,
       ROW_NUMBER() OVER (
           PARTITION BY customer_id
           ORDER BY order_date ASC, order_id ASC
       ) AS purchase_sequence_number
FROM orders
ORDER BY customer_id, purchase_sequence_number;""",
        complexity="window",
        tables=["orders"],
        description="ROW_NUMBER() window function partitioned by customer to track purchase sequence."
    ),
    GoldenExemplar(
        id="EX-023",
        question="Rank products by their total units sold within each category.",
        sql="""WITH product_sales AS (
    SELECT p.product_id,
           p.product_name,
           p.category,
           SUM(oi.quantity) AS total_units_sold,
           RANK() OVER (
               PARTITION BY p.category
               ORDER BY SUM(oi.quantity) DESC
           ) AS sales_rank
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    GROUP BY p.product_id, p.product_name, p.category
)
SELECT product_id, product_name, category, total_units_sold, sales_rank
FROM product_sales
ORDER BY category, sales_rank;""",
        complexity="window",
        tables=["products", "order_items"],
        description="RANK() window function partitioned by product category."
    ),
    GoldenExemplar(
        id="EX-024",
        question="Compute the percentage contribution of each product category to total delivered revenue.",
        sql="""WITH category_rev AS (
    SELECT p.category,
           ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent)), 2) AS cat_revenue
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.status = 'Delivered'
    GROUP BY p.category
)
SELECT category,
       cat_revenue,
       ROUND(cat_revenue * 100.0 / SUM(cat_revenue) OVER (), 2) AS percentage_of_total
FROM category_rev
ORDER BY cat_revenue DESC;""",
        complexity="window",
        tables=["products", "order_items", "orders"],
        description="Window function calculating ratio of category revenue to total overall revenue."
    )
]

def get_all_exemplars() -> List[GoldenExemplar]:
    return EXEMPLARS_DATABASE
