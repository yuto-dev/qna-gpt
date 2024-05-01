import sqlite3
import requests
import json
import base64

dbURL = "http://localhost:8003"

user = 'REPLACE'
password = 'WPAPPLICATIONPASSWORD'

def get_chat_entries_above_id(db_file, min_id):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Select entries from chatHistory table where ID is higher than min_id
    cursor.execute("SELECT * FROM chatHistory WHERE ID > ? AND flagA = 1", (min_id,))
    
    # Fetch all the rows and store them in a list
    entries = cursor.fetchall()

    # Close the database connection
    conn.close()

    return entries

def get_last_insert_id():
    url = "https://kayumeranti.my.id/wp-json/chat/v1/last-insert-id"

    try:
        
        wp_connection = user + ':' + password
        token = base64.b64encode(wp_connection.encode())

        headers = {
        "Content-Type": "application/json",
        "Authorization": 'Basic ' + token.decode('utf-8')
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for 4XX and 5XX status codes
        data = response.json()
        return data.get('last_insert_id', None)
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None

def getLocalLastRowId():
    url = dbURL + "/last_id"
    response = requests.get(url)
    item = response.json()
    return item

# Specify the minimum ID
min_id = int(get_last_insert_id()) # Change this to your desired minimum ID
#min_id = 0

lastLocalId = getLocalLastRowId()
lastLocalId = int(lastLocalId.get("id"))
print(lastLocalId)
print(min_id)

if lastLocalId > min_id:
    print("True")
    # Specify the SQLite database file path
    db_file = "chat.db"  # Change this to your database file path

    # Call the function to retrieve entries above the specified ID
    entries = get_chat_entries_above_id(db_file, min_id)

    # Print the retrieved entries (for demonstration)
    print("Retrieved entries:")
    for entry in entries:
        data = {
        "id": entry[0],
        "prompt": entry[1],
        "response": entry[2],
        "sourceA": entry[3],
        "sourceB": entry[4],
        "flagA": entry[5],
        "flagB": entry[6],
        "chatID": entry[7],
        "startTime": entry[8],
        "duration": entry[9]  # Add endTime to the data dictionary with the current time
        }
        
        print(data)
        print("\n")
        print("-----------------------------------------------------------")


        wp_connection = user + ':' + password
        token = base64.b64encode(wp_connection.encode())

        headers = {
    "Content-Type": "application/json",
    "Authorization": 'Basic ' + token.decode('utf-8')
}
        url = "https://kayumeranti.my.id/wp-json/chat/v1/insert"
        response = requests.post(url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            print("Data inserted successfully.")
        else:
            print(f"Error: {response.status_code} - {response.text}")
