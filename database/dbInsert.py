from fastapi import FastAPI, Form
from pydantic import BaseModel
import sqlite3

app = FastAPI()

class ChatData(BaseModel):
    prompt: str
    response: str
    sourceA: str
    sourceB: str
    chatID: int

@app.post("/insert_chat")
async def insert_chat(data: ChatData):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO chatHistory (prompt, response, sourceA, sourceB, chatID)
        VALUES (?, ?, ?, ?, ?)
    """, (data.prompt, data.response, data.sourceA, data.sourceB, data.chatID))
    conn.commit()
    conn.close()
    return {"message": "Chat data inserted successfully!"}

if __name__ == "__main__":
    # Run the FastAPI server
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
