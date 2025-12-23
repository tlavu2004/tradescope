import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

DB_SERVER = os.getenv("DB_SERVER", "localhost")
DB_PORT = os.getenv("DB_PORT", "1433")
DB_NAME = os.getenv("DB_NAME", "CryptoNews")
DB_USER = os.getenv("DB_USER", "sa")
DB_PASS = os.getenv("DB_PASS", "")
ODBC_DRIVER_NAME = os.getenv("ODBC_DRIVER", "ODBC Driver 17 for SQL Server")

odbc_str = (
    "DRIVER={%s};"
    "SERVER=%s,%s;"
    "DATABASE=%s;"
    "UID=%s;"
    "PWD=%s;"
) % (ODBC_DRIVER_NAME, DB_SERVER, DB_PORT, DB_NAME, DB_USER, DB_PASS)

DATABASE_URL = "mssql+pyodbc:///?odbc_connect=" + quote_plus(odbc_str)