from fastapi import FastAPI, BackgroundTasks
from queue import Queue
import requests
import json

app = FastAPI()
request_queue = Queue()
results_dict = {} # Shared data structure to store results

def callGPT(prompt):
    print("Start callGPT")
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

def process_queue():
    while not request_queue.empty():
        request_data = request_queue.get()
        input_data = request_data.get("prompt")
        
        try:
            gptResult, gptSource = callGPT(input_data)
            request_data['gptResult'] = gptResult
            request_data['gptSource'] = gptSource
            # Store the results in a dictionary with a unique identifier
            results_dict[id(request_data)] = {"gptResult": gptResult, "gptSource": gptSource}
        except Exception as e:
            print(f"Error processing request: {e}")
        finally:
            request_queue.task_done()

@app.post("/add_to_queue/")
async def add_to_queue(background_tasks: BackgroundTasks, request_data: dict):
    # Add the request to the queue
    request_queue.put(request_data)
    # Schedule the background task to process the request
    background_tasks.add_task(process_queue)
    
    # Return the response with a unique identifier for the request
    request_id = id(request_data)
    return {"message": "Request added to queue", "request_id": request_id}

@app.get("/get_result/{request_id}")
async def get_result(request_id: int):
    # Retrieve the processed results for the given request ID
    result = results_dict.get(request_id)
    if result:
        return result
    else:
        return {"message": "Results not available yet"}

if __name__ == "__main__":
    # Run the FastAPI server
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
