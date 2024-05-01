from fastapi import FastAPI, Form
from pydantic import BaseModel
import sqlite3

app = FastAPI()
conn = sqlite3.connect("chat.db")
c = conn.cursor()

@app.get("/last_id")
async def get_last_id():
    # Execute a query to fetch the ID of the latest entry
    c.execute("SELECT MAX(ID) FROM chatHistory")
    last_id = c.fetchone()[0]  # Fetch the first column of the result

    return {"id": last_id}


class ChatData(BaseModel):
    prompt: str
    chatID: int

@app.post("/insert_chat")
async def insert_chat(data: ChatData):

    c.execute("""
        INSERT INTO chatHistory (prompt, chatID)
        VALUES (?, ?)
    """, (data.prompt, data.chatID))
    conn.commit()
    last_id = c.lastrowid
    return {"message": "Chat data inserted successfully!", "id": last_id}

class IdQuery(BaseModel):
    id: int

@app.get("/get_prompt")
async def get_prompt(prompt_query: IdQuery):
    # Query the database for the "prompt" column of the entry with the given ID
    c.execute("SELECT prompt FROM chatHistory WHERE id = ?", (prompt_query.id,))
    prompt_result = c.fetchone()

    if prompt_result:
        # If a result is found, return the content of the "prompt" column
        return {"prompt": prompt_result[0]}
    else:
        # If no result is found, return a message indicating that
        return {"error": "No entry found with the provided ID."}
    
@app.get("/get_flagA")
async def get_flagA(prompt_query: IdQuery):
    # Query the database for the "prompt" column of the entry with the given ID
    c.execute("SELECT flagA FROM chatHistory WHERE id = ?", (prompt_query.id,))
    prompt_result = c.fetchone()

    if prompt_result:
        # If a result is found, return the content of the "prompt" column
        return {"flagA": prompt_result[0]}
    else:
        # If no result is found, return a message indicating that
        return {"error": "No entry found with the provided ID."}
    
@app.get("/get_result")
async def get_result(prompt_query: IdQuery):
    # Query the database for the "prompt" column of the entry with the given ID
    c.execute("SELECT * FROM chatHistory WHERE id = ?", (prompt_query.id,))
    prompt_result = c.fetchone()

    if prompt_result:
        # If a result is found, return the content of the "prompt" column
        return {"response": prompt_result[2], "source1": prompt_result[3], "source2": prompt_result[4]}
    else:
        # If no result is found, return a message indicating that
        return {"error": "No entry found with the provided ID."}

class UpdateData(BaseModel):
    id: int
    response: str
    source1: str
    source2: str
    flagA: int

@app.post("/update_entry")
async def update_entry(data: UpdateData):

    # Update the entry in the database
    c.execute("UPDATE chatHistory SET response = ?, source1 = ?, source2 = ?, flagA = ? WHERE id = ?", 
              (data.response, data.source1, data.source2, data.flagA, data.id))
    conn.commit()

    return {"message": "Chat data updated successfully!"}

class flagBData(BaseModel):
    id: int
    flagB: int
    duration: str

@app.post("/update_flagb")
async def update_entry(data: flagBData):

    # Update the entry in the database
    c.execute("UPDATE chatHistory SET flagB = ?, duration = ? WHERE id = ?", 
              (data.flagB, data.duration, data.id))
    conn.commit()

    return {"message": "Chat data updated successfully!"}

if __name__ == "__main__":
    # Run the FastAPI server
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
