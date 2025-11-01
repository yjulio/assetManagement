import mysql.connector
from mysql.connector import Error

try:
    # connect to the MySQL database
    connection = mysql.connector.connect(
        host='127.0.0.1',        # or your server IP if remote
        user='asset',         # your MySQL username
        password='tannatanna@kava',  # your MySQL password
        database='assets'        # your database name
    )

    if connection.is_connected():
        print("✅ Connected to MySQL Server successfully!")

        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")
        db_name = cursor.fetchone()
        print("Using database:", db_name[0])

        # create and query a test table
        cursor.execute("CREATE TABLE IF NOT EXISTS sample (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100));")
        cursor.execute("INSERT INTO sample (name) VALUES ('Alfred'), ('George');")
        connection.commit()

        cursor.execute("SELECT * FROM sample;")
        rows = cursor.fetchall()
        print("Data in sample table:")
        for row in rows:
            print(row)

except Error as e:
    print("❌ Error while connecting to MySQL:", e)

finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("🔒 MySQL connection closed.")

