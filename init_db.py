import sqlite3

# This is the name of our private database file
DATABASE_FILE = 'billing.db'

# Connect to the database (it will be created if it doesn't exist)
connection = sqlite3.connect(DATABASE_FILE)

# Read the blueprint from our schema.sql file
with open('schema.sql') as f:
    connection.executescript(f.read())

# Close the connection
connection.close()

print(f"Database '{DATABASE_FILE}' has been created successfully.")