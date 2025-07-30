from db_connector import connect_pg, connect_mongo
import json # Import json for printing data
from datetime import datetime, timezone # Import timezone for robust timestamps

# --- Conceptual Central Product Sync Worker ---
# This simulates a separate worker consuming product updates for the Central DB.
def process_central_product_sync_item(product_data):
    """
    Simulates a worker consuming product data and inserting/updating it
    into the Central PostgreSQL DB's central_products table.
    """
    print(f"Central Product Sync Worker: Attempting to sync product_id={product_data.get('id')} to Central DB...")
    central_pg_conn = None
    central_pg_cursor = None
    try:
        # NOTE: Using 'central' as per your worker/dashboard code consistency.
        # Ensure this matches your actual central DB name.
        central_pg_conn = connect_pg('central') # Or 'central_log_db' if that's its true name
        if central_pg_conn is None:
            print("Central Product Sync Worker: Failed to connect to Central DB. Product sync failed.")
            return False

        central_pg_cursor = central_pg_conn.cursor()

        # Use an UPSERT (ON CONFLICT) to handle both new products and updates to existing ones
        central_pg_cursor.execute("""
            INSERT INTO central_products (id, product_name)
            VALUES (%s, %s)
            ON CONFLICT (id) DO UPDATE SET
                product_name = EXCLUDED.product_name;
        """, (
            product_data['id'],
            product_data['product_name']
        ))
        central_pg_conn.commit()
        print(f"Central Product Sync Worker: Successfully synced product_id={product_data.get('id')} to Central DB.")
        return True
    except Exception as e:
        print(f"Central Product Sync Worker: Error syncing product_id={product_data.get('id')}: {e}")
        if central_pg_conn:
            try:
                central_pg_conn.rollback()
            except Exception as rb_e:
                print(f"Error during Central DB rollback for product sync: {rb_e}")
        return False
    finally:
        if central_pg_cursor:
            try:
                central_pg_cursor.close()
            except Exception as close_e:
                print(f"Error closing Central DB cursor for product sync: {close_e}")
        if central_pg_conn:
            try:
                central_pg_conn.close()
            except Exception as close_e:
                print(f"Error closing Central DB connection for product sync: {close_e}")

# --- Conceptual Product Sync Queue Publisher (MODIFIED for simulation) ---
def send_product_to_central_sync_queue(product_data):
    """
    Simulates publishing product data to a queue for asynchronous central synchronization.
    For this simulation, it directly calls the processing function.
    """
    print(f"\n--- Async Central Product Sync Event (Simulated Queueing) ---")
    print(f"Attempting to queue product data: {json.dumps(product_data, indent=2)}")

    # **THE KEY ADJUSTMENT FOR THE SIMULATION:**
    # Directly call the product processing function
    processed_successfully = process_central_product_sync_item(product_data)

    if processed_successfully:
        print("Simulated product sync processing completed successfully.")
    else:
        print("Simulated product sync processing failed.")
    print(f"--- End Async Central Product Sync Event (Simulated Queueing) ---\n")


# --- MODIFIED add_product_with_components function ---
def add_product_with_components(region, product_name, components, quantity):
    # Step 1: Connect to MongoDB
    mongo_db_instance = connect_mongo()
    if mongo_db_instance is None:
        print("[MongoDB] Connection failed.")
        return False # Return False to indicate failure

    actual_mongo_client = mongo_db_instance.client # Get the MongoClient for closing

    # Step 2: Connect to PostgreSQL
    conn = connect_pg(region)
    if conn is None:
        print(f"[PostgreSQL] Connection to {region} failed.")
        if actual_mongo_client: actual_mongo_client.close()
        return False

    cursor = conn.cursor()

    try:
        # Step 3: Check if all components exist in inventory table
        for comp in components:
            cursor.execute("SELECT * FROM inventory WHERE product_name = %s", (comp,))
            if cursor.fetchone() is None:
                raise Exception(f"Component '{comp}' not found in inventory. Aborting.")

        # Step 4: Insert product into inventory (PostgreSQL)
        # Assuming your central_products table might also store quantity,
        # so we'll pass it in the sync data.
        cursor.execute("INSERT INTO inventory (product_name, quantity) VALUES (%s, %s) RETURNING id", (product_name, quantity))
        product_id = cursor.fetchone()[0]

        # Step 5: Log mapping in MongoDB (product -> components)
        # Using the actual database object from connect_mongo
        mongo_db_instance.product_component.insert_one({
            "product": product_name,
            "components": components,
            "region": region,
            "quantity": quantity,
            "product_id_pg": product_id # Log PG ID for traceability in MongoDB if needed
        })

        conn.commit()
        print(f"Product '{product_name}' (ID: {product_id}) added successfully in {region} with components {components}.")

        # --- NEW STEP: Asynchronously sync product data to Central DB ---
        central_product_data = {
            "id": product_id,
            "product_name": product_name
        }
        send_product_to_central_sync_queue(central_product_data)
        print("Product data sent to central sync queue for asynchronous processing.")

        return True # Indicate success

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Transaction failed for product '{product_name}': {e}")
        return False # Indicate failure

    finally:
        if cursor:
            try:
                cursor.close()
            except Exception as close_e:
                print(f"Error closing PG cursor: {close_e}")
        if conn:
            try:
                conn.close()
            except Exception as close_e:
                print(f"Error closing PG connection: {close_e}")
        if actual_mongo_client:
            try:
                actual_mongo_client.close()
            except Exception as close_e:
                print(f"Error closing Mongo client: {close_e}")