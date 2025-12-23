import pyodbc

server = "localhost"
port = "1433"
database = "CryptoNews"
username = "sa"
password = ""  # đổi nếu khác
driver = "ODBC Driver 17 for SQL Server"

conn_str = (
    "DRIVER={%s};"
    "SERVER=%s,%s;"
    "DATABASE=%s;"
    "UID=%s;"
    "PWD=%s;"
) % (driver, server, port, database, username, password)

print("Connection string:", conn_str)

conn = pyodbc.connect(conn_str)
print("Connected OK")
cursor = conn.cursor()
cursor.execute("SELECT 1")
print("SELECT 1 result:", cursor.fetchone())
conn.close()