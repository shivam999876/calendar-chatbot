from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from agent import booking_agent

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message")
    session_id = data.get("session_id")
    response = await booking_agent(user_message, session_id)
    return {"response": response}

@app.get("/health")
def health():
    return {"status": "ok"}