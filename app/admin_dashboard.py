from db_connector import connect_pg

def view_all_sales():
    central_pg_conn = None
    central_pg_cursor = None
    try:
        central_pg_conn = connect_pg('central') 
        if not central_pg_conn:
            print("Could not connect to Central PostgreSQL database. Cannot view all sales.")
            return

        central_pg_cursor = central_pg_conn.cursor()
        print("\n--- All Sales Data from Central Log DB (with Product Names) ---")

        central_pg_cursor.execute("""
            SELECT
                o.order_id,
                o.customer_name,
                cp.product_name, -- Get product_name from central_products
                o.quantity,
                o.region
            FROM
                orders o
            JOIN
                central_products cp ON o.product_id = cp.id
            ORDER BY
                o.order_id DESC;
        """)

        results = central_pg_cursor.fetchall()
        if not results:
            print("No sales data available in the Central Log DB.")
        else:
            for row in results:
                print(f"Order ID: {row[0]}, Customer: {row[1]}, Product: {row[2]}, Quantity: {row[3]}, Region: {row[4]}")

    except Exception as e:
        print(f"Error fetching data from Central Log DB: {e}")
    finally:
        if central_pg_cursor:
            try:
                central_pg_cursor.close()
            except Exception as close_e:
                print(f"Error closing Central DB cursor: {close_e}")
        if central_pg_conn:
            try:
                central_pg_conn.close()
            except Exception as close_e:
                print(f"Error closing Central DB connection: {close_e}")