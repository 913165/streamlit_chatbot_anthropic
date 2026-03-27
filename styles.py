import streamlit as st

def load_css():
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
.section-title { font-size: 22px; font-weight: 800; color: #fff; margin-bottom: 14px; }

/* ── Badge ── */
.badge { display: inline-block; padding: 3px 9px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.badge-confirmed { background: rgba(43,219,153,0.12); color: #2bdb99; }
.badge-pending   { background: rgba(255,159,28,0.12);  color: #ff9f1c; }
.badge-cancelled { background: rgba(255,107,107,0.12); color: #ff6b6b; }

/* ── Row cells ── */
.pname    { font-weight: 600; color: #fff; font-size: 13px; }
.pemail   { font-size: 11px; color: #8a96b4; }
.fcode    { font-weight: 500; color: #fff; font-size: 13px; }
.fairline { font-size: 11px; color: #8a96b4; }
.ref-cell { font-family: monospace; font-size: 11px; color: #8a96b4; }
.price-cell { font-weight: 600; color: #fff; }

/* ── Chat bubbles ── */
.chat-header {
    background: #141d30;
    border-bottom: 1px solid #2d3a55;
    padding: 14px 16px;
    display: flex; align-items: center; gap: 12px;
    border-radius: 8px 8px 0 0;
}
.chat-avatar {
    width: 38px; height: 38px; border-radius: 50%;
    background: linear-gradient(135deg, #3a7bd5, #2bdb99);
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
}
.chat-bot-name { font-size: 14px; font-weight: 700; color: #fff; }
.chat-online   { font-size: 11px; color: #8a96b4; }
.dot-green     { color: #2bdb99; }

.chat-msg-bot  { display: flex; gap: 8px; align-items: flex-end; margin-bottom: 12px; }
.chat-msg-user { display: flex; gap: 8px; align-items: flex-end; justify-content: flex-end; margin-bottom: 12px; }

.bubble-bot {
    background: #1e2a42; border: 1px solid #2d3a55;
    border-radius: 12px 12px 12px 4px;
    padding: 10px 14px; font-size: 13px; color: #d0d8ef;
    line-height: 1.55; max-width: 82%; min-width: 60px;
    word-break: break-word; white-space: normal;
}
.bubble-user {
    background: #3a7bd5; border-radius: 12px 12px 4px 12px;
    padding: 10px 14px; font-size: 13px; color: #fff;
    line-height: 1.55; max-width: 82%; min-width: 60px;
    word-break: break-word; white-space: normal;
}
.av-bot {
    width: 28px; height: 28px; border-radius: 50%;
    background: linear-gradient(135deg, #3a7bd5, #2bdb99);
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 12px; flex-shrink: 0;
}
.av-user {
    width: 28px; height: 28px; border-radius: 50%;
    background: #2d3a55; display: inline-flex; align-items: center;
    justify-content: center; font-size: 12px; flex-shrink: 0; color: #8a96b4;
}

/* ── Streamlit overrides ── */
[data-testid="stTextInput"] > div > div {
    background: #1e2a42 !important; border: 1px solid #2d3a55 !important;
    border-radius: 6px !important; color: #d0d8ef !important;
}
[data-testid="stTextInput"] input { background: transparent !important; color: #d0d8ef !important; }
[data-testid="stSelectbox"] > div > div {
    background: #1e2a42 !important; border: 1px solid #2d3a55 !important; color: #d0d8ef !important;
}
[data-testid="stNumberInput"] > div > div {
    background: #1e2a42 !important; border: 1px solid #2d3a55 !important; color: #d0d8ef !important;
}
div[data-testid="stForm"] {
    background: #1e2a42 !important; border: 1px solid #2d3a55 !important;
    border-radius: 10px !important; padding: 20px !important;
}
label { color: #8a96b4 !important; font-size: 12px !important; }
.stButton > button {
    background: #3a7bd5 !important; color: #fff !important; border: none !important;
    border-radius: 6px !important; font-weight: 600 !important; padding: 8px 16px !important;
}
.stButton > button:hover { background: #2f66b8 !important; }
[data-testid="stChatInput"] { background: #1e2a42 !important; border-top: 1px solid #2d3a55 !important; }
[data-testid="stChatInput"] textarea {
    background: #1e2a42 !important; color: #d0d8ef !important;
    border: 1px solid #2d3a55 !important; border-radius: 8px !important;
}
hr { border-color: #2d3a55 !important; }

/* ── Action buttons ── */
div[data-testid="stColumn"] .stButton > button {
    padding: 0 !important; font-size: 15px !important;
    min-height: 30px !important; height: 30px !important;
    line-height: 30px !important; border-radius: 6px !important;
}
div[data-testid="stHorizontalBlock"] { align-items: center !important; }
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
    padding-left: 3px !important; padding-right: 3px !important;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(8) button { background: #2563eb !important; }
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(9) button { background: #dc2626 !important; }
</style>
""", unsafe_allow_html=True)