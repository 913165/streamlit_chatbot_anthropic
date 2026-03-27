import streamlit as st
import anthropic
import os
from datetime import date

# ── Load API key from environment variable ──
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="SkyBook – Flight Booking",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS (dark navy theme) ──────────────────────────────
st.markdown("""
<style>
/* ── Global ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #1a2035 !important;
    color: #d0d8ef;
    font-family: 'Segoe UI', sans-serif;
}
[data-testid="stHeader"] { background: #141d30 !important; }
[data-testid="stToolbar"] { display: none; }
footer { visibility: hidden; }

/* ── Top nav bar ── */
.navbar {
    background: #141d30;
    border-bottom: 1px solid #2d3a55;
    padding: 12px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0;
}
.navbar .logo { font-size: 20px; font-weight: 800; color: #fff; }
.navbar .logo span { color: #3a7bd5; }
.navbar .nav-right { font-size: 13px; color: #8a96b4; }

/* ── Stat cards ── */
.stat-row { display: flex; gap: 10px; margin-bottom: 14px; }
.stat-card {
    background: #1e2a42;
    border: 1px solid #2d3a55;
    border-radius: 8px;
    padding: 12px 18px;
    flex: 1;
    min-width: 0;
}
.stat-card .num { font-size: 22px; font-weight: 800; line-height: 1; }
.stat-card .lbl { font-size: 11px; color: #8a96b4; margin-top: 4px; }

/* ── Section title ── */
.section-title {
    font-size: 22px; font-weight: 800; color: #fff;
    margin-bottom: 14px;
}

/* ── Table styles ── */
.booking-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}
.booking-table thead th {
    text-align: left;
    padding: 10px 12px;
    color: #8a96b4;
    font-weight: 500;
    font-size: 12px;
    border-bottom: 1px solid #2d3a55;
    background: #1a2035;
}
.booking-table tbody tr {
    border-bottom: 1px solid #1f2b43;
    transition: background 0.15s;
}
.booking-table tbody tr:hover { background: #1e2a42; }
.booking-table tbody td {
    padding: 11px 12px;
    color: #c8d0e7;
    vertical-align: middle;
}
.pname  { font-weight: 600; color: #fff; font-size: 13px; }
.pemail { font-size: 11px; color: #8a96b4; }
.fcode  { font-weight: 500; color: #fff; font-size: 13px; }
.fairline { font-size: 11px; color: #8a96b4; }
.ref-cell { font-family: monospace; font-size: 11px; color: #8a96b4; }
.price-cell { font-weight: 600; color: #fff; }

.badge {
    display: inline-block;
    padding: 3px 9px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
}
.badge-confirmed { background: rgba(43,219,153,0.12); color: #2bdb99; }
.badge-pending   { background: rgba(255,159,28,0.12);  color: #ff9f1c; }
.badge-cancelled { background: rgba(255,107,107,0.12); color: #ff6b6b; }

/* ── Chat panel ── */
.chat-header {
    background: #141d30;
    border-bottom: 1px solid #2d3a55;
    padding: 14px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    border-radius: 8px 8px 0 0;
}
.chat-avatar {
    width: 38px; height: 38px;
    border-radius: 50%;
    background: linear-gradient(135deg, #3a7bd5, #2bdb99);
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
}
.chat-bot-name { font-size: 14px; font-weight: 700; color: #fff; }
.chat-online { font-size: 11px; color: #8a96b4; }
.dot-green { color: #2bdb99; }

.chat-msg-bot {
    display: flex;
    gap: 8px;
    align-items: flex-end;
    margin-bottom: 12px;
}
.chat-msg-user {
    display: flex;
    gap: 8px;
    align-items: flex-end;
    justify-content: flex-end;
    margin-bottom: 12px;
}
.bubble-bot {
    background: #1e2a42;
    border: 1px solid #2d3a55;
    border-radius: 12px 12px 12px 4px;
    padding: 10px 14px;
    font-size: 13px;
    color: #d0d8ef;
    line-height: 1.55;
    max-width: 82%;
    min-width: 60px;
    word-break: break-word;
    white-space: normal;
}
.bubble-user {
    background: #3a7bd5;
    border-radius: 12px 12px 4px 12px;
    padding: 10px 14px;
    font-size: 13px;
    color: #fff;
    line-height: 1.55;
    max-width: 82%;
    min-width: 60px;
    word-break: break-word;
    white-space: normal;
}
.msg-time { font-size: 10px; color: #8a96b4; margin-top: 3px; }
.av-bot {
    width: 28px; height: 28px;
    border-radius: 50%;
    background: linear-gradient(135deg, #3a7bd5, #2bdb99);
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 12px; flex-shrink: 0;
}
.av-user {
    width: 28px; height: 28px;
    border-radius: 50%;
    background: #2d3a55;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 12px; flex-shrink: 0; color: #8a96b4;
}

/* ── Streamlit overrides ── */
[data-testid="stTextInput"] > div > div {
    background: #1e2a42 !important;
    border: 1px solid #2d3a55 !important;
    border-radius: 6px !important;
    color: #d0d8ef !important;
}
[data-testid="stTextInput"] input {
    background: transparent !important;
    color: #d0d8ef !important;
}
[data-testid="stSelectbox"] > div > div {
    background: #1e2a42 !important;
    border: 1px solid #2d3a55 !important;
    color: #d0d8ef !important;
}
[data-testid="stNumberInput"] > div > div {
    background: #1e2a42 !important;
    border: 1px solid #2d3a55 !important;
    color: #d0d8ef !important;
}
[data-testid="stDateInput"] > div > div {
    background: #1e2a42 !important;
    border: 1px solid #2d3a55 !important;
    color: #d0d8ef !important;
}
div[data-testid="stForm"] {
    background: #1e2a42 !important;
    border: 1px solid #2d3a55 !important;
    border-radius: 10px !important;
    padding: 20px !important;
}
label { color: #8a96b4 !important; font-size: 12px !important; }
.stButton > button {
    background: #3a7bd5 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    padding: 8px 16px !important;
}
.stButton > button:hover { background: #2f66b8 !important; }

/* Chat input */
[data-testid="stChatInput"] {
    background: #1e2a42 !important;
    border-top: 1px solid #2d3a55 !important;
}
[data-testid="stChatInput"] textarea {
    background: #1e2a42 !important;
    color: #d0d8ef !important;
    border: 1px solid #2d3a55 !important;
    border-radius: 8px !important;
}
[data-testid="stChatMessage"] {
    background: transparent !important;
}

/* Divider */
hr { border-color: #2d3a55 !important; }

/* ── Action button colors & compact size ── */
div[data-testid="stColumn"] .stButton > button {
    padding: 0px 4px !important;
    font-size: 16px !important;
    min-height: 32px !important;
    height: 32px !important;
    line-height: 32px !important;
    border-radius: 6px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Sample Data ───────────────────────────────────────────────
if "bookings" not in st.session_state:
    st.session_state.bookings = [
        {"id":1,"ref":"SB-10021","name":"Maria Santos",   "email":"maria@email.com",  "phone":"09171234567","flight":"PR-181","airline":"Philippine Airline","from":"Metro Manila","to":"Bacolod",      "date":"Apr 10, 2026","cls":"Economy",   "price":4800,"status":"confirmed"},
        {"id":2,"ref":"SB-10022","name":"Jose Reyes",     "email":"jose@email.com",   "phone":"09281234567","flight":"5J-471","airline":"Cebu Pacific",      "from":"Metro Manila","to":"Bacolod",      "date":"Apr 12, 2026","cls":"Business",  "price":7200,"status":"confirmed"},
        {"id":3,"ref":"SB-10023","name":"Ana Gonzales",   "email":"ana@email.com",    "phone":"09331234567","flight":"Z2-204","airline":"AirAsia",           "from":"Bacolod",     "to":"Pampanga",     "date":"Apr 15, 2026","cls":"Economy",   "price":3800,"status":"pending"},
        {"id":4,"ref":"SB-10024","name":"Carlos Mendoza", "email":"carlos@email.com", "phone":"09451234567","flight":"PR-183","airline":"Philippine Airline","from":"Bacolod",     "to":"Metro Manila", "date":"Apr 18, 2026","cls":"First Class","price":9500,"status":"cancelled"},
        {"id":5,"ref":"SB-10025","name":"Luz Villanueva", "email":"luz@email.com",    "phone":"09561234567","flight":"Z2-205","airline":"AirAsia",           "from":"Pampanga",    "to":"Bacolod",      "date":"Apr 20, 2026","cls":"Economy",   "price":2500,"status":"pending"},
    ]
if "next_id" not in st.session_state:
    st.session_state.next_id = 6
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hi! I'm SkyBot ✈\nI can help you with the flight bookings on the left — ask me about passengers, routes, statuses, or totals!"}
    ]
if "show_add_form" not in st.session_state:
    st.session_state.show_add_form = False
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None
if "pending_response" not in st.session_state:
    st.session_state.pending_response = False

# ── Navbar ────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
  <div class="logo">Sky<span>Book</span></div>
  <div class="nav-right">✈ Flight Booking System</div>
</div>
""", unsafe_allow_html=True)

# ── Layout: Left (list) | Right (chat) ───────────────────────
left_col, right_col = st.columns([2.8, 1], gap="small")

# ════════════════════════════════════════
# LEFT PANEL — BOOKING LIST
# ════════════════════════════════════════
with left_col:
    st.markdown('<div class="section-title">FLIGHT BOOKING LIST</div>', unsafe_allow_html=True)

    bookings = st.session_state.bookings
    total  = len(bookings)
    conf   = sum(1 for b in bookings if b["status"] == "confirmed")
    pend   = sum(1 for b in bookings if b["status"] == "pending")
    canc   = sum(1 for b in bookings if b["status"] == "cancelled")
    rev    = sum(b["price"] for b in bookings if b["status"] != "cancelled")

    # Stats
    st.markdown(f"""
    <div class="stat-row">
      <div class="stat-card"><div class="num">{total}</div><div class="lbl">Total</div></div>
      <div class="stat-card"><div class="num" style="color:#2bdb99">{conf}</div><div class="lbl">Confirmed</div></div>
      <div class="stat-card"><div class="num" style="color:#ff9f1c">{pend}</div><div class="lbl">Pending</div></div>
      <div class="stat-card"><div class="num" style="color:#ff6b6b">{canc}</div><div class="lbl">Cancelled</div></div>
      <div class="stat-card"><div class="num" style="color:#3a7bd5;font-size:17px">₱{rev:,}</div><div class="lbl">Revenue</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Search + Add
    s1, s2 = st.columns([5, 1])
    with s1:
        search = st.text_input("Search", placeholder="Search name, flight, route…",
                               key="search_query", label_visibility="collapsed")
    with s2:
        if st.button("+ Add", use_container_width=True):
            st.session_state.show_add_form = not st.session_state.show_add_form
            st.session_state.edit_id = None

    # Add / Edit Form
    if st.session_state.show_add_form or st.session_state.edit_id is not None:
        editing = st.session_state.edit_id
        eb = next((b for b in bookings if b["id"] == editing), {}) if editing else {}
        form_title = f"Edit Booking — {eb.get('name','')}" if editing else "Add New Booking"

        with st.form("booking_form", clear_on_submit=True):
            st.markdown(f"**{form_title}**")
            fc1, fc2 = st.columns(2)
            with fc1:
                f_name    = st.text_input("Passenger Name *", value=eb.get("name",""))
                f_email   = st.text_input("Email", value=eb.get("email",""))
                f_flight  = st.text_input("Flight No. *", value=eb.get("flight",""))
                f_from    = st.text_input("From *", value=eb.get("from",""))
                f_cls     = st.selectbox("Class", ["Economy","Business","First Class"],
                                         index=["Economy","Business","First Class"].index(eb.get("cls","Economy")))
            with fc2:
                f_phone   = st.text_input("Mobile", value=eb.get("phone",""))
                f_airline = st.selectbox("Airline", ["Philippine Airline","Cebu Pacific","AirAsia"],
                                         index=["Philippine Airline","Cebu Pacific","AirAsia"].index(eb.get("airline","Philippine Airline")))
                f_to      = st.text_input("To *", value=eb.get("to",""))
                f_price   = st.number_input("Price (₱) *", min_value=0, value=int(eb.get("price",0)))
                f_status  = st.selectbox("Status", ["confirmed","pending","cancelled"],
                                         index=["confirmed","pending","cancelled"].index(eb.get("status","confirmed")))

            fb1, fb2 = st.columns([1,1])
            with fb1:
                submitted = st.form_submit_button("💾 Save Booking", use_container_width=True)
            with fb2:
                cancelled_form = st.form_submit_button("Cancel", use_container_width=True)

            if submitted:
                if not f_name or not f_flight or not f_from or not f_to:
                    st.error("Please fill all required fields.")
                else:
                    if editing:
                        for i, b in enumerate(st.session_state.bookings):
                            if b["id"] == editing:
                                st.session_state.bookings[i] = {
                                    **b, "name":f_name,"email":f_email,"phone":f_phone,
                                    "flight":f_flight,"airline":f_airline,"from":f_from,
                                    "to":f_to,"cls":f_cls,"price":f_price,"status":f_status
                                }
                    else:
                        nid = st.session_state.next_id
                        st.session_state.bookings.append({
                            "id":nid,"ref":f"SB-1{10020+nid}","name":f_name,"email":f_email,
                            "phone":f_phone,"flight":f_flight,"airline":f_airline,"from":f_from,
                            "to":f_to,"date":str(date.today().strftime("%b %d, %Y")),"cls":f_cls,
                            "price":f_price,"status":f_status
                        })
                        st.session_state.next_id += 1
                    st.session_state.show_add_form = False
                    st.session_state.edit_id = None
                    st.rerun()
            if cancelled_form:
                st.session_state.show_add_form = False
                st.session_state.edit_id = None
                st.rerun()

    # Filter
    q = search.lower()
    filtered = [b for b in bookings if not q or any(
        q in str(b.get(k,"")).lower() for k in ["name","flight","from","to","ref","airline"]
    )]

    # ── Column header row ──
    def badge_html(status):
        cls = {"confirmed":"badge-confirmed","pending":"badge-pending","cancelled":"badge-cancelled"}.get(status,"")
        return f'<span class="badge {cls}">{status.capitalize()}</span>'

    st.markdown("""
    <style>
    .row-divider { border-bottom: 1px solid #1f2b43; margin: 0; }
    div[data-testid="stHorizontalBlock"] { align-items: center !important; }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] { padding-left: 3px !important; padding-right: 3px !important; }
    /* Compact icon buttons */
    div[data-testid="stColumn"] .stButton > button {
        padding: 0 !important;
        font-size: 15px !important;
        min-height: 30px !important;
        height: 30px !important;
        line-height: 30px !important;
        border-radius: 6px !important;
    }
    /* Edit col (8th) = blue, Del col (9th) = red */
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(8) button { background: #2563eb !important; }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(9) button { background: #dc2626 !important; }
    </style>
    """, unsafe_allow_html=True)

    # Header
    h0,h1,h2,h3,h4,h5,h6,h7,h8 = st.columns([1.2, 1.8, 1.4, 1.8, 1.2, 1.0, 1.2, 0.7, 0.7])
    with h0: st.markdown("<span style='font-size:12px;color:#8a96b4;font-weight:500'>Ref</span>", unsafe_allow_html=True)
    with h1: st.markdown("<span style='font-size:12px;color:#8a96b4;font-weight:500'>Passenger</span>", unsafe_allow_html=True)
    with h2: st.markdown("<span style='font-size:12px;color:#8a96b4;font-weight:500'>Flight</span>", unsafe_allow_html=True)
    with h3: st.markdown("<span style='font-size:12px;color:#8a96b4;font-weight:500'>Route</span>", unsafe_allow_html=True)
    with h4: st.markdown("<span style='font-size:12px;color:#8a96b4;font-weight:500'>Date</span>", unsafe_allow_html=True)
    with h5: st.markdown("<span style='font-size:12px;color:#8a96b4;font-weight:500'>Price</span>", unsafe_allow_html=True)
    with h6: st.markdown("<span style='font-size:12px;color:#8a96b4;font-weight:500'>Status</span>", unsafe_allow_html=True)
    with h7: st.markdown("<span style='font-size:12px;color:#8a96b4;font-weight:500'>✏</span>", unsafe_allow_html=True)
    with h8: st.markdown("<span style='font-size:12px;color:#8a96b4;font-weight:500'>🗑</span>", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#2d3a55;margin:4px 0 6px 0'>", unsafe_allow_html=True)

    # Data rows — each row is one st.columns() so buttons are perfectly aligned
    if not filtered:
        st.markdown("<p style='text-align:center;color:#8a96b4;padding:32px'>No bookings found.</p>", unsafe_allow_html=True)
    else:
        for b in filtered:
            c0,c1,c2,c3,c4,c5,c6,c7,c8 = st.columns([1.2, 1.8, 1.4, 1.8, 1.2, 1.0, 1.2, 0.7, 0.7])
            with c0:
                st.markdown(f"<span class='ref-cell'>{b['ref']}</span>", unsafe_allow_html=True)
            with c1:
                st.markdown(f"<div class='pname'>{b['name']}</div><div class='pemail'>{b['email']}</div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='fcode'>{b['flight']}</div><div class='fairline'>{b['airline']}</div>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"<span style='font-size:12px;color:#c8d0e7'>{b['from']} → {b['to']}</span>", unsafe_allow_html=True)
            with c4:
                st.markdown(f"<span style='font-size:12px;color:#c8d0e7;white-space:nowrap'>{b['date']}</span>", unsafe_allow_html=True)
            with c5:
                st.markdown(f"<span class='price-cell'>₱{b['price']:,}</span>", unsafe_allow_html=True)
            with c6:
                st.markdown(badge_html(b['status']), unsafe_allow_html=True)
            with c7:
                if st.button("✏", key=f"edit_{b['id']}", use_container_width=True, help="Edit booking"):
                    st.session_state.edit_id = b["id"]
                    st.session_state.show_add_form = False
                    st.rerun()
            with c8:
                if st.button("🗑", key=f"del_{b['id']}", use_container_width=True, help="Delete booking"):
                    st.session_state.bookings = [x for x in st.session_state.bookings if x["id"] != b["id"]]
                    st.rerun()

            st.markdown("<hr style='border-color:#1f2b43;margin:2px 0'>", unsafe_allow_html=True)

# ════════════════════════════════════════
# RIGHT PANEL — CHATBOT
# ════════════════════════════════════════
with right_col:
    # Chat header
    st.markdown("""
    <div class="chat-header">
      <div class="chat-avatar">✈</div>
      <div>
        <div class="chat-bot-name">SkyBot Assistant</div>
        <div class="chat-online"><span class="dot-green">●</span> Online · AI Powered</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Chat history display
    chat_container = st.container(height=520)
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "assistant":
                st.markdown(f"""
                <div class="chat-msg-bot">
                  <div class="av-bot">✈</div>
                  <div><div class="bubble-bot">{msg['content'].replace(chr(10),'<br>')}</div></div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-msg-user">
                  <div><div class="bubble-user">{msg['content']}</div></div>
                  <div class="av-user">👤</div>
                </div>""", unsafe_allow_html=True)

    # Chat input
    user_input = st.chat_input("Ask about bookings, passengers, flights…")

    if user_input:
        # Step 1: append user message and rerun immediately to show it
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.pending_response = True
        st.rerun()

    # Step 2: on next run, pending_response is True — fetch bot reply
    if st.session_state.pending_response:
        st.session_state.pending_response = False

        bk = st.session_state.bookings
        conf_n = sum(1 for b in bk if b["status"]=="confirmed")
        pend_n = sum(1 for b in bk if b["status"]=="pending")
        canc_n = sum(1 for b in bk if b["status"]=="cancelled")
        rev_n  = sum(b["price"] for b in bk if b["status"]!="cancelled")
        blist  = "\n".join([
            f"- [{b['ref']}] {b['name']} | {b['flight']} ({b['airline']}) | {b['from']}→{b['to']} | {b['date']} | {b['cls']} | ₱{b['price']:,} | {b['status']}"
            for b in bk
        ])
        system_prompt = f"""You are SkyBot, a helpful flight booking assistant for SkyBook.
Current booking data:
Total: {len(bk)} | Confirmed: {conf_n} | Pending: {pend_n} | Cancelled: {canc_n} | Revenue: ₱{rev_n:,}

Bookings:
{blist}

Answer questions about these bookings concisely. Keep replies short and clear. Use plain text, no markdown symbols."""

        with chat_container:
            st.markdown("""
            <div class="chat-msg-bot">
              <div class="av-bot">✈</div>
              <div><div class="bubble-bot">⏳ Thinking…</div></div>
            </div>""", unsafe_allow_html=True)

        try:
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.chat_history
                if m["role"] in ("user", "assistant")
            ]
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=600,
                system=system_prompt,
                messages=messages,
            )
            reply = response.content[0].text
        except Exception as e:
            reply = f"Sorry, I couldn't connect. ({str(e)[:60]})"

        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()