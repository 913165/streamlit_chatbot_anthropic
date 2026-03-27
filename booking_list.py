import streamlit as st
from database import get_all_bookings, get_airlines, add_booking, update_booking, delete_booking


def init_state():
    if "show_add_form" not in st.session_state: st.session_state.show_add_form = False
    if "edit_id"       not in st.session_state: st.session_state.edit_id       = None
    if "search_query"  not in st.session_state: st.session_state.search_query  = ""


def badge_html(status):
    cls = {"confirmed":"badge-confirmed","pending":"badge-pending","cancelled":"badge-cancelled"}.get(status,"")
    return f'<span class="badge {cls}">{status.capitalize()}</span>'


def render_stats(bookings):
    total = len(bookings)
    conf  = sum(1 for b in bookings if b["status"] == "confirmed")
    pend  = sum(1 for b in bookings if b["status"] == "pending")
    canc  = sum(1 for b in bookings if b["status"] == "cancelled")
    rev   = sum(b["price"] for b in bookings if b["status"] != "cancelled")
    st.markdown(f"""
    <div class="stat-row">
      <div class="stat-card"><div class="num">{total}</div><div class="lbl">Total</div></div>
      <div class="stat-card"><div class="num" style="color:#2bdb99">{conf}</div><div class="lbl">Confirmed</div></div>
      <div class="stat-card"><div class="num" style="color:#ff9f1c">{pend}</div><div class="lbl">Pending</div></div>
      <div class="stat-card"><div class="num" style="color:#ff6b6b">{canc}</div><div class="lbl">Cancelled</div></div>
      <div class="stat-card"><div class="num" style="color:#3a7bd5;font-size:17px">₱{rev:,.2f}</div><div class="lbl">Revenue</div></div>
    </div>
    """, unsafe_allow_html=True)


def render_form(bookings):
    editing = st.session_state.edit_id
    eb = next((b for b in bookings if b["id"] == editing), {}) if editing else {}
    title = f"Edit Booking — {eb.get('name','')}" if editing else "Add New Booking"

    airlines = [a["name"] for a in get_airlines()]
    airline_val = eb.get("airline", airlines[0]) if eb.get("airline") in airlines else airlines[0]

    with st.form("booking_form", clear_on_submit=True):
        st.markdown(f"**{title}**")
        fc1, fc2 = st.columns(2)
        with fc1:
            f_name    = st.text_input("Passenger Name *", value=eb.get("name",""))
            f_email   = st.text_input("Email",            value=eb.get("email",""))
            f_flight  = st.text_input("Flight No. *",     value=eb.get("flight",""))
            f_from    = st.text_input("From *",           value=eb.get("from",""))
            f_cls     = st.selectbox("Class", ["Economy","Business","First Class"],
                                     index=["Economy","Business","First Class"].index(eb.get("cls","Economy")))
        with fc2:
            f_phone   = st.text_input("Mobile",  value=eb.get("phone",""))
            f_airline = st.selectbox("Airline", airlines,
                                     index=airlines.index(airline_val))
            f_to      = st.text_input("To *",    value=eb.get("to",""))
            f_price   = st.number_input("Price (₱) *", min_value=0, value=int(eb.get("price",0)))
            f_date    = st.text_input("Travel Date (YYYY-MM-DD) *", value=eb.get("date",""))
            f_status  = st.selectbox("Status", ["confirmed","pending","cancelled"],
                                     index=["confirmed","pending","cancelled"].index(eb.get("status","confirmed")))

        fb1, fb2 = st.columns(2)
        with fb1: submitted      = st.form_submit_button("💾 Save Booking", use_container_width=True)
        with fb2: cancelled_form = st.form_submit_button("Cancel",          use_container_width=True)

        if submitted:
            if not f_name or not f_flight or not f_from or not f_to or not f_date:
                st.error("Please fill all required fields.")
            else:
                if editing:
                    update_booking(editing, f_name, f_email, f_phone, f_flight,
                                   f_airline, f_from, f_to, f_date, f_cls, f_price, f_status)
                else:
                    add_booking(f_name, f_email, f_phone, f_flight, f_airline,
                                f_from, f_to, f_date, f_cls, f_price, f_status)
                st.session_state.show_add_form = False
                st.session_state.edit_id = None
                st.rerun()

        if cancelled_form:
            st.session_state.show_add_form = False
            st.session_state.edit_id = None
            st.rerun()


def render_table(filtered):
    h0,h1,h2,h3,h4,h5,h6,h7,h8 = st.columns([1.2,1.8,1.4,1.8,1.2,1.0,1.2,0.7,0.7])
    for col, label in zip([h0,h1,h2,h3,h4,h5,h6,h7,h8],
                           ["Ref","Passenger","Flight","Route","Date","Price","Status","✏","🗑"]):
        col.markdown(f"<span style='font-size:12px;color:#8a96b4;font-weight:500'>{label}</span>",
                     unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#2d3a55;margin:4px 0 6px 0'>", unsafe_allow_html=True)

    if not filtered:
        st.markdown("<p style='text-align:center;color:#8a96b4;padding:32px'>No bookings found.</p>",
                    unsafe_allow_html=True)
        return

    for b in filtered:
        c0,c1,c2,c3,c4,c5,c6,c7,c8 = st.columns([1.2,1.8,1.4,1.8,1.2,1.0,1.2,0.7,0.7])
        c0.markdown(f"<span class='ref-cell'>{b['ref']}</span>", unsafe_allow_html=True)
        c1.markdown(f"<div class='pname'>{b['name']}</div><div class='pemail'>{b['email']}</div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='fcode'>{b['flight']}</div><div class='fairline'>{b['airline']}</div>", unsafe_allow_html=True)
        c3.markdown(f"<span style='font-size:12px;color:#c8d0e7'>{b['from']} → {b['to']}</span>", unsafe_allow_html=True)
        c4.markdown(f"<span style='font-size:12px;color:#c8d0e7;white-space:nowrap'>{b['date']}</span>", unsafe_allow_html=True)
        c5.markdown(f"<span class='price-cell'>₱{b['price']:,.2f}</span>", unsafe_allow_html=True)
        c6.markdown(badge_html(b['status']), unsafe_allow_html=True)
        with c7:
            if st.button("✏", key=f"edit_{b['id']}", use_container_width=True, help="Edit"):
                st.session_state.edit_id       = b["id"]
                st.session_state.show_add_form = False
                st.rerun()
        with c8:
            if st.button("🗑", key=f"del_{b['id']}", use_container_width=True, help="Delete"):
                delete_booking(booking_id=b["id"])
                st.rerun()
        st.markdown("<hr style='border-color:#1f2b43;margin:2px 0'>", unsafe_allow_html=True)


def render_booking_list():
    st.markdown('<div class="section-title">FLIGHT BOOKING LIST</div>', unsafe_allow_html=True)

    bookings = get_all_bookings()
    render_stats(bookings)

    s1, s2 = st.columns([5, 1])
    with s1:
        search = st.text_input("Search", placeholder="Search name, flight, route…",
                               key="search_query", label_visibility="collapsed")
    with s2:
        if st.button("+ Add", use_container_width=True):
            st.session_state.show_add_form = not st.session_state.show_add_form
            st.session_state.edit_id = None

    if st.session_state.show_add_form or st.session_state.edit_id is not None:
        render_form(bookings)

    q = search.lower()
    filtered = [b for b in bookings if not q or any(
        q in str(b.get(k,"")).lower() for k in ["name","flight","from","to","ref","airline"]
    )]

    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] { align-items: center !important; }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] { padding-left: 3px !important; padding-right: 3px !important; }
    div[data-testid="stColumn"] .stButton > button {
        padding: 0 !important; font-size: 15px !important;
        min-height: 30px !important; height: 30px !important; line-height: 30px !important; border-radius: 6px !important;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(8) button { background: #2563eb !important; }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(9) button { background: #dc2626 !important; }
    </style>
    """, unsafe_allow_html=True)

    render_table(filtered)