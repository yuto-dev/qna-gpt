import sqlite3

def fetch_chat_data():
    # Connect to the SQLite database
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    # Query the chat data
    c.execute("SELECT * FROM chatHistory")
    rows = c.fetchall()

    # Print the fetched data
    for row in rows:
        print(f"ID: {row[0]}, Prompt: {row[1]}, Response: {row[2]}, Source A: {row[3]}, Source B: {row[4]}, Chat ID: {row[5]}")

    # Close the database connection
    conn.close()

if __name__ == "__main__":
    fetch_chat_data()

