import psycopg2
from pymongo import MongoClient

def connect_pg(db_name):
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user='postgres',         # Replace with your PostgreSQL user
            password='password', # Replace with your PostgreSQL password
            host='localhost',
            port='5432'
        )
        print(f"[PostgreSQL] Connected to {db_name}")
        return conn
    except Exception as e:
        print(f"[PostgreSQL] Connection failed to {db_name}: {e}")
        return None

def connect_mongo():
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client['distributed_db']
        print("[MongoDB] Connected to distributed_db")
        return db
    except Exception as e:
        print(f"[MongoDB] Connection failed: {e}")
        return None
