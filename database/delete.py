import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('chat.db')
cursor = conn.cursor()

# Specify the table name
table_name = 'chatHistory'

# Execute the DELETE query to empty the table
cursor.execute('DELETE FROM {}'.format(table_name))

# Commit the changes
conn.commit()

# Close the connection
conn.close()
