import streamlit as st
import requests

st.title("🗓️ Calendar Booking Assistant")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def send_message(message):
    try:
        response = requests.post(
            "http://localhost:8000/chat",
            json={"message": message, "session_id": "user1"}
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "[No response from backend]")
    except requests.exceptions.RequestException as e:
        return f"[Error communicating with backend: {e}]"
    except Exception as e:
        return f"[Unexpected error: {e}]"

user_input = st.text_input("You:", key="input")
if st.button("Send") and user_input:
    st.session_state.chat_history.append(("user", user_input))
    agent_reply = send_message(user_input)
    st.session_state.chat_history.append(("agent", agent_reply))
    st.rerun()  # ✅ Use this instead of st.experimental_rerun()

for role, msg in st.session_state.chat_history:
    st.markdown(f"**{role.capitalize()}:** {msg}")