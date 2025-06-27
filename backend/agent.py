import re
from datetime import datetime, timedelta
from calendar_utils import get_free_slots, book_event

# Simple in-memory session state
sessions = {}

# Helper functions for intent and slot extraction

def extract_datetime(text):
    # Very basic extraction for demo purposes
    # Handles 'tomorrow', 'today', 'next week', 'Friday', and times like '3pm', '15:00', 'afternoon'
    now = datetime.utcnow()
    text = text.lower()
    if 'tomorrow' in text:
        date = now + timedelta(days=1)
    elif 'today' in text:
        date = now
    elif 'next week' in text:
        date = now + timedelta(days=7)
    elif 'friday' in text:
        days_ahead = (4 - now.weekday() + 7) % 7
        date = now + timedelta(days=days_ahead)
    else:
        date = now
    # Time extraction
    hour = 15 if 'afternoon' in text else 9
    match = re.search(r'(\d{1,2})(:(\d{2}))? ?(am|pm)?', text)
    if match:
        hour = int(match.group(1))
        if match.group(4) == 'pm' and hour < 12:
            hour += 12
    return date.replace(hour=hour, minute=0, second=0, microsecond=0)

def extract_duration(text):
    # Looks for '30 minutes', '1 hour', etc.
    match = re.search(r'(\d+) ?(minute|hour)', text)
    if match:
        value = int(match.group(1))
        if 'hour' in match.group(2):
            return value * 60
        return value
    return 30  # default 30 minutes

def extract_purpose(text):
    # Use everything after 'for' or 'about' as purpose
    match = re.search(r'(for|about) (.+)', text)
    if match:
        return match.group(2)
    return 'Meeting'

async def booking_agent(user_message, session_id):
    # Get or create session state
    state = sessions.get(session_id, {"step": 0})
    response = ""
    if state["step"] == 0:
        # Extract slots
        date = extract_datetime(user_message)
        duration = extract_duration(user_message)
        purpose = extract_purpose(user_message)
        state.update({"date": date, "duration": duration, "purpose": purpose, "step": 1})
        # Find free slots for that day
        start = date.replace(hour=8, minute=0)
        end = date.replace(hour=18, minute=0)
        slots = get_free_slots(start, end, duration)
        state["slots"] = slots
        if not slots:
            response = f"Sorry, no free slots found on {date.strftime('%A, %B %d')}. Try another day?"
            state["step"] = 0
        else:
            slot_strs = [f"{s[0].strftime('%H:%M')}–{s[1].strftime('%H:%M')}" for s in slots[:3]]
            response = f"I found these free slots on {date.strftime('%A, %B %d')}: {', '.join(slot_strs)}. Which one would you like to book?"
            state["step"] = 2
    elif state["step"] == 2:
        # User picks a slot
        slots = state.get("slots", [])
        chosen = None
        for i, s in enumerate(slots[:3]):
            if str(i+1) in user_message or s[0].strftime('%H') in user_message:
                chosen = s
                break
        if not chosen:
            # Try to match time in message
            for s in slots[:3]:
                if s[0].strftime('%H:%M') in user_message:
                    chosen = s
                    break
        if not chosen:
            response = "Please specify which slot you'd like to book (e.g., 'first', '10:00', etc.)."
        else:
            state["chosen_slot"] = chosen
            response = f"Great! Should I book {chosen[0].strftime('%H:%M')}–{chosen[1].strftime('%H:%M')} for '{state['purpose']}'? (yes/no)"
            state["step"] = 3
    elif state["step"] == 3:
        if 'yes' in user_message.lower():
            slot = state["chosen_slot"]
            event = book_event(slot[0], slot[1], state["purpose"], f"Booked via assistant for {state['purpose']}")
            response = f"Booked! Your event is confirmed for {slot[0].strftime('%A, %B %d %H:%M')}."
            state["step"] = 0
        else:
            response = "Okay, booking cancelled. Let me know if you want to try another time."
            state["step"] = 0
    sessions[session_id] = state
    return response