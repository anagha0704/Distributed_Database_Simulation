from db_connector import connect_pg, connect_mongo
import uuid
from datetime import datetime, timezone # Import timezone for robust timestamps
import json # For serializing log data for the conceptual queue

# --- Conceptual Central Log Worker (defined first so send_to_central_log_queue can call it) ---
# This simulates a separate worker consuming from the queue and writing to the Central DB.
def process_central_log_queue_item(log_data):
    """
    Simulates a dedicated worker consuming a log item and inserting it into the Central PostgreSQL DB.
    This function demonstrates what would happen in the background.
    """
    print(f"Central Log Worker: Attempting to log order_id={log_data.get('order_id')} to Central DB...")
    central_pg_conn = None
    central_pg_cursor = None
    try:
        # NOTE: Keeping 'central' as your specified DB name for consistency with your provided code.
        # Ensure this matches the actual name of your central database.
        central_pg_conn = connect_pg('central')
        if central_pg_conn is None:
            print("Central Log Worker: Failed to connect to Central DB. This item might be retried or moved to a dead-letter queue.")
            return False

        central_pg_cursor = central_pg_conn.cursor()

        # Insert into the central 'orders' table
        central_pg_cursor.execute("""
            INSERT INTO orders (order_id, product_id, quantity, customer_name, region)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (order_id) DO NOTHING; -- Use ON CONFLICT for idempotency if order_id is unique
        """, (
            log_data['order_id'],
            log_data['product_id'],
            log_data['quantity'],
            log_data['customer_name'],
            log_data['region']
        ))
        central_pg_conn.commit()
        print(f"Central Log Worker: Successfully logged order_id={log_data.get('order_id')} to Central DB.")
        return True
    except Exception as e:
        print(f"Central Log Worker: Error inserting into Central DB for order_id={log_data.get('order_id')}: {e}")
        if central_pg_conn:
            try:
                central_pg_conn.rollback()
            except Exception as rb_e:
                print(f"Error during Central DB rollback: {rb_e}")
        # In a real system, robust retry logic (e.g., exponential backoff) and dead-letter queueing would go here.
        return False
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

# --- Conceptual Asynchronous Queue Publisher (MODIFIED for simulation) ---
# This function simulates sending data to a message queue.
def send_to_central_log_queue(log_data):
    """
    Simulates publishing order data to a queue. For this simulation,
    it directly calls the processing function to immediately log to Central DB.
    """
    print(f"\n--- Async Central Log Event (Simulated Queueing) ---")
    print(f"Attempting to queue data: {json.dumps(log_data, indent=2)}")

    # **THE KEY ADJUSTMENT FOR THE SIMULATION:**
    # Instead of just printing, we directly call the processing function.
    # In a real system, this would be replaced with actual queueing logic.
    processed_successfully = process_central_log_queue_item(log_data)

    if processed_successfully:
        print("Simulated queue processing completed successfully.")
    else:
        print("Simulated queue processing failed.")
    print(f"--- End Async Central Log Event (Simulated Queueing) ---\n")


# --- Your place_order function remains UNCHANGED ---
def place_order(region, customer, product, quantity):
    pg_conn = None
    cursor = None
    mongo_db_instance = None # Database object
    actual_mongo_client = None # This will hold the MongoClient for closing

    try:
        pg_conn = connect_pg(region)
        if not pg_conn:
            print(f"Could not connect to {region} PostgreSQL database. Aborting order.")
            return False

        cursor = pg_conn.cursor()

        cursor.execute("SELECT id, quantity FROM inventory WHERE product_name = %s FOR UPDATE", (product,))
        item = cursor.fetchone()

        if not item:
            print(f"{product} not found in {region} inventory. Rolling back PostgreSQL.")
            pg_conn.rollback()
            return False

        product_id, stock = item
        if stock < quantity:
            print(f"Not enough stock. Available: {stock}, Requested: {quantity}. Rolling back PostgreSQL.")
            pg_conn.rollback()
            return False

        current_order_timestamp = datetime.now(timezone.utc)

        cursor.execute("""
            INSERT INTO orders (product_id, quantity, customer_name, region)
            VALUES (%s, %s, %s, %s) RETURNING order_id
        """, (product_id, quantity, customer, region))
        order_id = cursor.fetchone()[0]

        cursor.execute("""
            UPDATE inventory SET quantity = quantity - %s WHERE id = %s
        """, (quantity, product_id))

        print(f"PostgreSQL operations prepared for order {order_id}. Now attempting MongoDB log...")

        mongo_db_instance = connect_mongo()
        if mongo_db_instance is None:
            raise Exception("Failed to connect to MongoDB.")

        actual_mongo_client = mongo_db_instance.client
        orders_col = mongo_db_instance["order_product"]

        log_data = {
            "order_id_pg": order_id,
            "customer": customer,
            "product": product,
            "quantity": quantity,
            "region": region,
            "log_id": str(uuid.uuid4()),
            "timestamp": current_order_timestamp
        }

        orders_col.insert_one(log_data)
        print("MongoDB log successfully inserted. Committing regional PostgreSQL transaction.")

        pg_conn.commit()
        print(f"Order {order_id} placed for {customer}: {quantity} {product}(s) in {region} region. Regional DB and MongoDB updated.")

        central_log_data = {
            "order_id": order_id,
            "product_id": product_id,
            "quantity": quantity,
            "customer_name": customer,
            "region": region,
        }
        send_to_central_log_queue(central_log_data) # This now triggers the worker directly
        print("Order data initiated for asynchronous central logging.")

        return True

    except Exception as e:
        print(f"Error occurred during order placement: {e}")
        if pg_conn:
            try:
                pg_conn.rollback()
                print("PostgreSQL transaction rolled back to maintain consistency.")
            except Exception as rb_e:
                print(f"Error during PostgreSQL rollback: {rb_e}")
        return False

    finally:
        if cursor:
            try:
                cursor.close()
            except Exception as close_e:
                print(f"Error closing cursor: {close_e}")
        if pg_conn:
            try:
                pg_conn.close()
            except Exception as close_e:
                print(f"Error closing PG connection: {close_e}")
        if actual_mongo_client:
            try:
                actual_mongo_client.close()
            except Exception as close_e:
                print(f"Error closing Mongo connection: {close_e}")