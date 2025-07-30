# Distributed Database Simulation

## Overview

This project simulates a distributed e-commerce and inventory management system designed for scalability and resilience across multiple geographical regions. It demonstrates a common architectural pattern where regional databases handle local transactions, while data is asynchronously synchronized to a central database for global analytics and reporting. The system also leverages **polyglot persistence**, combining the strengths of **PostgreSQL** for structured transactional data and **MongoDB** for flexible, document-based logging and complex relationships.

---

## Key Features

1. **Regional Inventory & Order Management**  
   Each region (e.g., Seattle, Boston) maintains its own PostgreSQL database for local inventory and order processing, ensuring high availability and low latency within the region.

2. **Centralized Analytics & Reporting**  
   A dedicated central PostgreSQL database consolidates order and product data from all regions, providing a unified view for administrative and analytical purposes.

3. **Asynchronous Data Synchronization**  
   Mimics the use of message queues (like Kafka or RabbitMQ) to asynchronously push order and product updates from regional databases to the central reporting database. This ensures regional operations are non-blocking and enables eventual consistency for the central view.

4. **Polyglot Persistence**
   - **PostgreSQL**: Used for structured, ACID-compliant data like inventory counts, product details, and core order records (both regional and central).
   - **MongoDB**: Utilized for flexible logging of order details and managing complex product component relationships.

5. **Idempotent Data Synchronization**  
   Central database writes are designed to be idempotent using `ON CONFLICT` clauses, allowing safe re-processing of messages without data duplication or corruption.

6. **Transaction Management**
    Proper use of database transactions ensures atomicity and consistency for critical operations like placing an order.

---

## Technologies Used

- Python 3.x: The core programming language  
- PostgreSQL: Relational database for transactional and analytical data  
- MongoDB: Document database for flexible logging and relationships  
- `psycopg2`: PostgreSQL adapter for Python  
- `pymongo`: MongoDB driver for Python  

---

## Setup Instructions

### 1. Prerequisites

Ensure the following are installed on your system:

- Python 3.x  
- PostgreSQL server  
- MongoDB server  
- Git  

---

### 2. Clone the Repository

```bash
git clone https://github.com/anagha0704/Distributed_Database_Simulation.git
cd Distributed_Database_Simulation
```

---

### 3. Set up a Python Virtual Environment (Recommended)
```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: `venv\Scripts\activate`
```

---

### 4. Install Dependencies
```bash
    pip install -r requirements.txt
```

---

### 5. Database Setup
You need to create the necessary databases and tables in your PostgreSQL instance.

- PostgreSQL Databases
    Create four PostgreSQL databases. You can do this via psql or pgAdmin:
    boston, seattle, denver, central

- PostgreSQL Tables
    Connect to each of your newly created databases and execute data/chema.sql for boston, seattle, denver databases and for central use data/schema_central_db.sql,  it will create necessary tables inside the databases.

### 6. Initialize MongoDB collections
Create a new database called distributed_db. Inside it, create 2 collections:
product_component, order_product

### 7. Run Main Application Loop
If you have a main.py with an interactive menu, run it:
    
```bash
    python main.py
```
Or
After creation and setups of databases, project can be run by executing the run.bat file.

## Key Learnings & Concepts Demonstrated
This project effectively illustrates:
1. **Distributed Database Design**
    Strategies for partitioning data across multiple database instances.

2. **Polyglot Persistence**
    Choosing different database technologies based on data characteristics and access patterns.

3. **Asynchronous Communication**
    The importance of message queues for decoupling services and handling eventual consistency in distributed environments.

4. **Eventual Consistency**
    How data eventually converges across distributed systems, which is acceptable for reporting/analytical needs.

5. **Idempotent Operations**
    Designing operations that can be re-executed safely without side effects, crucial for fault tolerance in message-driven architectures.

6. **Transactional Integrity (ACID Properties)**
    Demonstrating how Atomicity, Consistency, Isolation, and Durability are maintained within single database transactions to ensure data reliability.
