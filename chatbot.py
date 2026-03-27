import streamlit as st
import anthropic
import json


def init_chat_state():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Hi! I'm SkyBot ✈\nI can help you manage flight bookings — ask me to delete, update status, or get info about any booking!"}
        ]
    if "pending_response" not in st.session_state:
        st.session_state.pending_response = False


def build_system_prompt():
    bk     = st.session_state.bookings
    conf_n = sum(1 for b in bk if b["status"] == "confirmed")
    pend_n = sum(1 for b in bk if b["status"] == "pending")
    canc_n = sum(1 for b in bk if b["status"] == "cancelled")
    rev_n  = sum(b["price"] for b in bk if b["status"] != "cancelled")
    blist  = "\n".join([
        f"- [{b['ref']}] {b['name']} | {b['flight']} ({b['airline']}) | {b['from']}→{b['to']} | {b['date']} | {b['cls']} | ₱{b['price']:,} | {b['status']}"
        for b in bk
    ])
    return f"""You are SkyBot, a flight booking assistant for SkyBook. You CAN perform actions on bookings.

Current booking data:
Total: {len(bk)} | Confirmed: {conf_n} | Pending: {pend_n} | Cancelled: {canc_n} | Revenue: ₱{rev_n:,}

Bookings:
{blist}

You have the ability to:
1. DELETE a booking when the user asks to delete/remove/cancel a booking
2. UPDATE STATUS of a booking (confirmed, pending, cancelled)
3. ANSWER questions about bookings

When the user asks to perform an action, you MUST respond with a JSON block in this exact format (nothing else before or after):

For delete:
{{"action": "delete", "ref": "SB-XXXXX", "message": "Booking SB-XXXXX for [name] has been deleted."}}

For status update:
{{"action": "update_status", "ref": "SB-XXXXX", "status": "confirmed", "message": "Booking SB-XXXXX for [name] has been updated to confirmed."}}

For questions (no action needed), respond normally in plain text without any JSON.

Important: Match passenger names case-insensitively. If you cannot find a booking, say so in plain text."""


def apply_action(action_data: dict) -> str:
    action = action_data.get("action")
    ref    = action_data.get("ref", "").upper()

    if action == "delete":
        before = len(st.session_state.bookings)
        st.session_state.bookings = [b for b in st.session_state.bookings if b["ref"].upper() != ref]
        if len(st.session_state.bookings) < before:
            return action_data.get("message", f"Booking {ref} deleted.")
        return f"Could not find booking {ref}."

    elif action == "update_status":
        new_status = action_data.get("status", "").lower()
        for i, b in enumerate(st.session_state.bookings):
            if b["ref"].upper() == ref:
                st.session_state.bookings[i] = {**b, "status": new_status}
                return action_data.get("message", f"Booking {ref} updated to {new_status}.")
        return f"Could not find booking {ref}."

    return action_data.get("message", "Action completed.")


def fetch_bot_reply(api_key: str) -> str:
    try:
        client = anthropic.Anthropic(api_key=api_key)
        messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.chat_history
            if m["role"] in ("user", "assistant")
        ]
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=600,
            system=build_system_prompt(),
            messages=messages,
        )
        reply = response.content[0].text.strip()

        # Check if the reply contains a JSON action
        if reply.startswith("{") and "action" in reply:
            try:
                action_data = json.loads(reply)
                result = apply_action(action_data)
                st.rerun()  # refresh the table immediately
                return result
            except json.JSONDecodeError:
                pass

        return reply

    except Exception as e:
        return f"Sorry, I couldn't connect. ({str(e)[:60]})"


def render_messages(container):
    with container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "assistant":
                st.markdown(f"""
                <div class="chat-msg-bot">
                  <div class="av-bot">✈</div>
                  <div><div class="bubble-bot">{msg['content'].replace(chr(10), '<br>')}</div></div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-msg-user">
                  <div><div class="bubble-user">{msg['content']}</div></div>
                  <div class="av-user">👤</div>
                </div>""", unsafe_allow_html=True)


def render_chatbot(api_key: str):
    st.markdown("""
    <div class="chat-header">
      <div class="chat-avatar">✈</div>
      <div>
        <div class="chat-bot-name">SkyBot Assistant</div>
        <div class="chat-online"><span class="dot-green">●</span> Online · AI Powered</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    chat_container = st.container(height=520)
    render_messages(chat_container)

    user_input = st.chat_input("Ask or say: delete Jose Reyes booking…")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.pending_response = True
        st.rerun()

    if st.session_state.pending_response:
        st.session_state.pending_response = False

        with chat_container:
            st.markdown("""
            <div class="chat-msg-bot">
              <div class="av-bot">✈</div>
              <div><div class="bubble-bot">⏳ Thinking…</div></div>
            </div>""", unsafe_allow_html=True)

        reply = fetch_bot_reply(api_key)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()