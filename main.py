import streamlit as st
from styles import load_css
from booking_list import init_state, render_booking_list
from chatbot import init_chat_state, render_chatbot

# ── Config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="SkyBook – Flight Booking",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── API Key ───────────────────────────────────────────────────
ANTHROPIC_API_KEY = st.secrets["ANTHROPIC_API_KEY"]

# ── CSS ───────────────────────────────────────────────────────
load_css()

# ── Session state ─────────────────────────────────────────────
init_state()
init_chat_state()

# ── Navbar ────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
  <div class="logo">Sky<span>Book</span></div>
  <div class="nav-right">✈ Flight Booking System</div>
</div>
""", unsafe_allow_html=True)

# ── Layout ────────────────────────────────────────────────────
left_col, right_col = st.columns([2.8, 1], gap="small")

with left_col:
    render_booking_list()

with right_col:
    render_chatbot(ANTHROPIC_API_KEY)