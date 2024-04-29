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
        return {"response": prompt_result[2], "sourceA": prompt_result[3], "sourceB": prompt_result[4]}
    else:
        # If no result is found, return a message indicating that
        return {"error": "No entry found with the provided ID."}

class UpdateData(BaseModel):
    id: int
    response: str
    sourceA: str
    sourceB: str
    flagA: int
    endTime: str  # Assuming endTime is received as a string

@app.post("/update_entry")
async def update_entry(data: UpdateData):

    # Update the entry in the database
    c.execute("UPDATE chatHistory SET response = ?, sourceA = ?, sourceB = ?, flagA = ?, endTime = ? WHERE id = ?", 
              (data.response, data.sourceA, data.sourceB, data.flagA, data.endTime, data.id))
    conn.commit()

    return {"message": "Chat data updated successfully!"}

class flagBData(BaseModel):
    id: int
    flagB: int

@app.post("/update_flagb")
async def update_entry(data: flagBData):

    # Update the entry in the database
    c.execute("UPDATE chatHistory SET flagB = ? WHERE id = ?", 
              (data.flagB, data.id))
    conn.commit()

    return {"message": "Chat data updated successfully!"}

if __name__ == "__main__":
    # Run the FastAPI server
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
