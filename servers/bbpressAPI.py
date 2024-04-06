import requests
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
from datetime import datetime
import json

user = "REPLACE"
pswd = "REPLACE"
mail = "REPLACE"

# URL to make the GET request
url = "https://kayumeranti.my.id/wp-json/bbp-api/v1/topics/189"

# Function to read old reply IDs from a file
def read_old_replies(filename):
    try:
        with open(filename, 'r') as file:
            old_replies = file.read().split(',')
            # Convert the list of strings to integers
            old_replies = [int(reply_id) for reply_id in old_replies if reply_id]
            return old_replies
    except FileNotFoundError:
        print(f"File {filename} not found. Starting with an empty list of old replies.")
        return []

# Function to write new reply IDs to a file
def write_new_reply_id(filename, reply_id):
    with open(filename, 'a') as file:
        file.write(f"{reply_id},")

# Function to make the GET request and parse the JSON response
def get_replies(url):
    response = requests.get(url)
    if response.status_code ==   200:
        return response.json()
    else:
        print(f"Failed to get data from {url}. Status code: {response.status_code}")
        return None

# Function to get the content of a specific reply
def get_reply_content(reply_id):
    reply_url = f"https://kayumeranti.my.id/wp-json/bbp-api/v1/replies/{reply_id}"
    response = requests.get(reply_url)
    if response.status_code ==   200:
        reply_data = response.json()
        content = reply_data.get('content', '')
        # Strip HTML tags from the content
        soup = BeautifulSoup(content, 'html.parser')
        stripped_content = soup.get_text()
        return stripped_content
    else:
        print(f"Failed to get content for reply ID {reply_id}. Status code: {response.status_code}")
        return None

# Function to process the replies and return the content of new replies
def process_replies(replies, old_replies, filename):
    new_reply_contents = []
    for reply in replies:
        reply_id = reply['id']
        author_name = reply['author_name']
        # Check if the reply is from a user other than "bot" and if it's a new reply
        if author_name != "bot" and reply_id not in old_replies:
            print(f"New reply ID: {reply_id}")
            write_new_reply_id(filename, reply_id)
            old_replies.append(reply_id)
            # Get the content of the new reply
            content = get_reply_content(reply_id)
            if content:
                new_reply_contents.append(content)
    return new_reply_contents

def notifyComment(target):
    
    # The post ID where the comment will be added

    url = 'http://kayumeranti.my.id/wp-json/bbp-api/v1/topics/189'
    username = user
    password = pswd
    email = mail

    headers = {
        'Content-Type': 'application/json',
    }

    # The comment data
    
    # Get current date and time
    now = datetime.now()
    
    formattedComment = "Processing prompt: \n" + "<blockquote>" + target + "</blockquote>" + "\n" + "Time start: " + now.strftime("%Y-%m-%d %H:%M:%S") + " (GMT +7)"
    
    data = {
    'content': formattedComment,
    'status': 'publish',
    'email': email
    }

    response = requests.post(url, json=data, headers=headers, auth=HTTPBasicAuth(username, password))
    
    # Check the response
    if response.status_code ==  201 or response.status_code ==  200:
        print("Reply posted successfully.")
        return response.json()
    else:
        print(f"Failed to post reply. Status code: {response.status_code}")
        print(response.text)
        return None

def callGPT(prompt):
    # Define the URL
    url = "http://localhost:8001/v1/completions"
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

    # Make the POST request
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
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


def replyComment(target, payload, source):
    
    # The post ID where the comment will be added

    url = 'http://kayumeranti.my.id/wp-json/bbp-api/v1/topics/189'
    username = user
    password = pswd
    email = mail

    headers = {
        'Content-Type': 'application/json',
    }

    # The comment data
    
    # Get current date and time
    now = datetime.now()
    formattedComment = "Replying to:\n" + "<blockquote>" + target + "</blockquote>" + "\n" + "Response:\n" + payload + "\n"
    formattedSource = "Source:\n" + source[0] + "\n" + source[1] + "\n"
    endTime = "Time stop: " + now.strftime("%Y-%m-%d %H:%M:%S") + " (GMT +7)"
    data = {
    'content': formattedComment + "\n" + formattedSource + "\n" + endTime,
    'status': 'publish',
    'email': email
    }
    
    response = requests.post(url, json=data, headers=headers, auth=HTTPBasicAuth(username, password))
    
    # Check the response
    if response.status_code ==  201 or response.status_code ==  200:
        print("Reply posted successfully.")
        return response.json()
    else:
        print(f"Failed to post reply. Status code: {response.status_code}")
        print(response.text)
        return None

# Main function to execute the script
def main():
    old_replies = read_old_replies('id.txt')
    print("Listening...")
    while True:
        data = get_replies(url)
        if data:
            replies = data.get('replies', [])
            new_reply_contents = process_replies(replies, old_replies, 'id.txt')
            # Here you can pass new_reply_contents to another function for further processing
            # For example:
            for content in new_reply_contents:
                if content:
                    print("Found new reply: ", content)
                    notifyComment(content)
                    gptResult, gptSource = callGPT(content)
                    replyComment(content, gptResult, gptSource)
        # Wait for a specified interval before checking again
        #time.sleep(60)  # Adjust the interval as needed

if __name__ == "__main__":
    main()
