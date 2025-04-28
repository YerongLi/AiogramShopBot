import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('data/database.db')

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Query to list all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

# Fetch and print all table names
tables = cursor.fetchall()
print("Tables in the database:")
for table in tables:
    print(table[0])

# Close the connection
conn.close()
