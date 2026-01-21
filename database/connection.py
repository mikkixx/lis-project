from peewee import MySQLDatabase

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'mikki@localhost',
    'password': '07bcf91@K',
    'database': 'elfimova',
    'charset': 'utf8mb4'
}

database = MySQLDatabase(
    DB_CONFIG['database'],
    host=DB_CONFIG['host'],
    port=DB_CONFIG['port'],
    user=DB_CONFIG['user'],
    password=DB_CONFIG['password'],
    charset=DB_CONFIG['charset']
)

def connect_db():
    if database.is_closed():
        database.connect()
    return True

def close_db():
    if not database.is_closed():
        database.close()
