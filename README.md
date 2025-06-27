# Calendar Booking Assistant

A conversational AI agent to help you book appointments on your Google Calendar via chat.

## Project Structure

- `backend/` — FastAPI app, LangGraph agent, Google Calendar integration
- `frontend/` — Streamlit chat interface

## Setup Instructions

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### 2. Frontend

```bash
cd ../frontend
pip install -r requirements.txt
streamlit run app.py
```

### 3. Google Calendar Credentials
- You will need to set up Google Calendar API credentials.
- Place your credentials file in the backend directory and update `calendar_utils.py` accordingly.
- See: https://developers.google.com/calendar/api/quickstart/python

## Usage
- Open the Streamlit app in your browser.
- Chat with the assistant to book appointments.

---

**Note:** The current implementation uses placeholders for the agent and calendar logic. You need to implement intent extraction, slot filling, and Google Calendar integration for full functionality. 