import requests
import time

def get_results(request_id):
    url = f"http://localhost:8000/get_result/{request_id}"
    response = requests.get(url)
    return response.json()

url = "http://localhost:8000/add_to_queue/"
headers = {
    "Content-Type": "application/json"
}
data = {
    "prompt": "Kelelawar itu apa?"
}

response = requests.post(url, headers=headers, json=data)

response_data = response.json()
message = response_data["message"]
request_id = response_data["request_id"]

print("Message:", message)
print("Request ID:", request_id)

# Wait for the results to be available
time.sleep(10)  # Adjust this time as needed

# Retrieve the results
results = get_results(request_id)
print("GPT Result:", results.get("gptResult"))
print("GPT Source:", results.get("gptSource"))
