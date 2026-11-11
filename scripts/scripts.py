'''
this script will create the database operational.db where we gonna store the data in two tables 
customers and orders 
'''
from sqlalchemy import create_engine , MetaData , Table , Column , Integer , String , DateTime , ForeignKey , Float 
from sqlalchemy.dialects.sqlite import insert
import logging
from datetime import datetime

metadata = MetaData()
logging.basicConfig( 
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


# create table customers
try : 
    customers_table = Table(
        'customers' ,
        metadata ,
        Column('customer_id' , Integer , nullable=False , primary_key=True , unique=True) ,
        Column('name' , String , nullable=False) ,
        Column('email' , String , nullable=False , unique=True) ,
        Column('country' , String) ,
        Column('created_at' , DateTime) ,
        Column('updated_at' , DateTime)
    )

# create table orders
    orders_table = Table(
        'orders' , 
        metadata ,
        Column('order_id' , Integer , nullable=False , primary_key=True , unique=True) ,
        Column('customer_id' , Integer , ForeignKey('customers.customer_id')) ,
        Column('order_date' , DateTime , nullable=False) ,
        Column('total_amount' , Float) ,
        Column('status' , String) ,
        Column('updated_at' , DateTime)
    )
    logging.info('tables customers , orders created successuffly')
except Exception:
    logging.error('tables not created successfully in the database')


try : 
    def dt(s):
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

    customers_raw = [
        (1,  "Youssef Benali",   "youssef.benali@example.com",   "Morocco", "2024-01-15 10:20:00", "2024-06-01 09:00:00"),
        (2,  "Fatima El Idrissi","fatima.elidrissi@example.com", "Morocco", "2024-02-03 14:05:00", "2024-02-03 14:05:00"),
        (3,  "Omar Alaoui",      "omar.alaoui@example.com",      "France",  "2024-02-20 09:45:00", "2024-08-12 16:30:00"),
        (4,  "Aya Tazi",         "aya.tazi@example.com",         "Spain",   "2024-03-11 11:10:00", "2024-03-11 11:10:00"),
        (5,  "Karim Haddad",     "karim.haddad@example.com",     "France",  "2024-03-29 17:25:00", "2024-09-05 10:00:00"),
        (6,  "Salma Fassi",      "salma.fassi@example.com",      "Morocco", "2024-04-14 08:30:00", "2024-04-14 08:30:00"),
        (7,  "John Smith",       "john.smith@example.com",       "USA",     "2024-05-02 19:40:00", "2024-10-18 12:15:00"),
        (8,  "Emma Dupont",      "emma.dupont@example.com",      "France",  "2024-05-21 13:00:00", "2024-05-21 13:00:00"),
        (9,  "Lucas Garcia",     "lucas.garcia@example.com",     "Spain",   "2024-06-09 15:50:00", "2024-11-02 09:20:00"),
        (10, "Sofia Rossi",      "sofia.rossi@example.com",      "Italy",   "2024-07-01 10:00:00", "2024-07-01 10:00:00"),
        (11, "Hamza Bennani",    "hamza.bennani@example.com",    "Morocco", "2024-07-23 12:35:00", "2025-01-10 14:45:00"),
        (12, "Imane Lopez",      "imane.lopez@example.com",      "Spain",   "2024-08-15 16:20:00", "2024-08-15 16:20:00"),
        (13, "Anas Martin",      "anas.martin@example.com",      "Canada",  "2024-09-04 09:10:00", "2025-02-20 11:30:00"),
        (14, "Nora Khan",        "nora.khan@example.com",        "UK",      "2024-09-26 18:05:00", "2024-09-26 18:05:00"),
        (15, "Pierre Silva",     "pierre.silva@example.com",     "France",  "2024-10-12 14:40:00", "2025-03-08 08:55:00"),
        (16, "Marta Garcia",     "marta.garcia@example.com",     "Spain",   "2024-11-05 11:25:00", "2024-11-05 11:25:00"),
        (17, "Ahmed Alaoui",     "ahmed.alaoui@example.com",     "Germany", "2024-11-30 20:15:00", "2025-04-17 13:10:00"),
        (18, "Sara Benali",      "sara.benali@example.com",      "Morocco", "2024-12-18 07:50:00", "2024-12-18 07:50:00"),
        (19, "Laila Haddad",     "laila.haddad@example.com",     "Canada",  "2025-01-22 15:30:00", "2025-06-30 10:40:00"),
        (20, "Mohamed Tazi",     "mohamed.tazi@example.com",     "Germany", "2025-02-14 12:00:00", "2025-02-14 12:00:00"),
    ]

    orders_raw = [
        (1,  1,  "2024-02-10 11:00:00", 129.99, "delivered", "2024-02-15 09:30:00"),
        (2,  2,  "2024-03-05 15:20:00",  54.50, "delivered", "2024-03-10 12:00:00"),
        (3,  3,  "2024-04-01 10:45:00", 899.00, "delivered", "2024-04-08 17:10:00"),
        (4,  1,  "2024-06-18 13:30:00", 215.75, "shipped",   "2024-06-20 08:00:00"),
        (5,  5,  "2024-05-12 09:15:00",  39.90, "cancelled", "2024-05-12 18:45:00"),
        (6,  7,  "2024-06-25 20:00:00", 450.00, "delivered", "2024-07-02 14:20:00"),
        (7,  4,  "2024-07-14 16:40:00",  75.25, "returned",  "2024-07-30 10:05:00"),
        (8,  9,  "2024-08-09 11:55:00", 1320.40,"delivered", "2024-08-16 09:50:00"),
        (9,  6,  "2024-09-01 08:25:00",  22.00, "delivered", "2024-09-05 13:35:00"),
        (10, 10, "2024-09-19 14:10:00", 310.60, "shipped",   "2024-09-21 11:00:00"),
        (11, 8,  "2024-10-03 17:35:00", 67.80,  "delivered", "2024-10-09 15:25:00"),
        (12, 11, "2024-11-11 12:20:00", 540.00, "pending",   "2024-11-11 12:20:00"),
        (13, 12, "2024-12-02 09:05:00", 98.30,  "delivered", "2024-12-07 10:15:00"),
        (14, 13, "2024-12-20 19:45:00", 189.99, "cancelled", "2024-12-21 08:30:00"),
        (15, 15, "2025-01-15 10:30:00", 725.50, "delivered", "2025-01-22 16:00:00"),
        (16, 14, "2025-02-08 13:15:00", 44.95,  "shipped",   "2025-02-10 09:40:00"),
        (17, 17, "2025-03-27 15:50:00", 260.00, "delivered", "2025-04-03 12:30:00"),
        (18, 18, "2025-04-30 11:10:00", 1049.99,"pending",   "2025-04-30 11:10:00"),
        (19, 19, "2025-07-12 18:25:00", 83.40,  "delivered", "2025-07-18 14:55:00"),
        (20, 20, "2025-09-05 09:55:00", 332.15, "returned",  "2025-09-20 11:45:00"),
    ]

    customers = [
        dict(customer_id=c[0], name=c[1], email=c[2], country=c[3],
            created_at=dt(c[4]), updated_at=dt(c[5]))
        for c in customers_raw
    ]
    orders = [
        dict(order_id=o[0], customer_id=o[1], order_date=dt(o[2]),
            total_amount=o[3], status=o[4], updated_at=dt(o[5]))
        for o in orders_raw
    ]

    engine = create_engine('sqlite:///data/database/operational.db')
    metadata.create_all(engine)

    with engine.begin() as conn :
        conn.execute(insert(customers_table).on_conflict_do_nothing() , customers)
        conn.execute(insert(orders_table).on_conflict_do_nothing() , orders)
    logging.info('tables customers and orders have been inserted with the data successfully')
except:
    logging.error('there is an error in inserting data into tables customers and orders')