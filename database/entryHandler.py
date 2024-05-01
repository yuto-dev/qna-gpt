import sqlite3
import time
import requests
import json
from datetime import datetime

dbURL = "http://localhost:8003"
gptURL = "http://192.168.1.53:8001"
# Connect to the SQLite database
conn = sqlite3.connect('chat.db')
cursor = conn.cursor()

# Initialize an empty list to store the IDs
ids_list = []

def callGPT(prompt):
    print("Start callGPT")
    # Define the URL
    url = gptURL + "/v1/completions"
    # Define the headers
    headers = {
        "Content-Type": "application/json"
    }

    # Define the data
    data = {
        "prompt": prompt,
        "stream": False,
        "use_context": True,
        "system_prompt": "Kamu adalah LibraryAI. Kamu adalah AI LLM yang memiliki akses ke database literatur fisik. Gunakan literatur ini untuk menjawab pertanyaan yang diajukan padamu. Jika kamu tidak dapat menemukan jawabannya dalam informasi tersebut, katakan saja bahwa kamu tidak yakin dan berikan perkiraan tentang apa yang kamu pikirkan sebagai jawabannya, pastikan untuk memberi tahu pengguna bahwa ini adalah tebakan terbaikmu dan tidak 100 persen benar."
    }

    print("Calling")
        
    # Make the POST request
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    print(response.status_code)
    
    # Check if the request was successful
    if response.status_code ==  200:
        # Parse the JSON response
        response_data = response.json()
        jsonContent = response_data.keys()
        # Extract choices key
        choices = response_data.get('choices')
        #--------------------------------------------
        #Extract content
        message = choices[0].get('message')
        content = message.get('content')
        print(content)
        #--------------------------------------------
        sources = choices[0].get('sources')
    
        i = 0
        sourcesList = []
        for entry in sources:
            document = sources[i].get('document')
            doc_metadata = document.get('doc_metadata')
            page_label = doc_metadata.get('page_label')
            file_name = doc_metadata.get('file_name')
        
            number = str(i + 1)
            formattedSource = number + ". " + file_name + " (page " + page_label + ")"
            sourcesList.append(formattedSource)
            i = i + 1
        
        i = 0
        for source in sources:
            print(sourcesList[i])
            i = i + 1  
    
    else:
        print("Request failed with status code:", response.status_code)

    return content, sourcesList

while True:
    # Query the database for entries where flagA is 0
    cursor.execute("SELECT id FROM chatHistory WHERE flagA = 0")
    entries = cursor.fetchall()
    
    # Clear the current list of IDs
    #ids_list.clear()
    if entries:
        # Add the IDs from the query entries to the list
        for row in entries:
            # Make an API call to the queue system
            id = row[0]
            url = dbURL + "/get_prompt"
            headers = {"Content-Type": "application/json"}
            data = {"id": id}
            print(id)
            print(type(id))
            response = requests.get(url, headers=headers, json=data)
            response_data = response.json()
            promptInput = response_data.get("prompt")
            print(promptInput)
            print(type(promptInput))
            gptResult, gptSource = callGPT(promptInput)
            print(gptResult)
            print(gptSource)
            
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            updateData = {
                    "id": id,
                    "response": gptResult,
                    "source1": gptSource[0],
                    "source2": gptSource[1],
                    "flagA": 1,
            }
            
            response = requests.post(dbURL + "/update_entry", json=updateData)
            response_data = response.json()
            print(response_data)
    
    # Print the list of IDs for demonstration purposes
    if entries:
        print("Current IDs with flagA = False:", entries)
    else:
        print("No ID with flagA = 0")
    
    # Sleep for a while before the next query to avoid overloading the database
    time.sleep(5) # Adjust the sleep duration as needed
