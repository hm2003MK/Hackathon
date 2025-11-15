# theme.py
import streamlit as st

def apply_theme():
    """Inject global CSS / theme styling for all pages."""
    st.markdown("""
    <style>
    :root {
        --primary: #5B8CFF;
        --primary-hover: #3E6FE0;

        --bg-page: #0D0F12;
        --bg-sidebar: #0E1014;
        --bg-card: #15181E;

        --border: rgba(255,255,255,0.08);
        --border-heavy: rgba(255,255,255,0.12);

        --font: -apple-system, BlinkMacSystemFont, "Inter", "SF Pro Display", "Segoe UI", Roboto, sans-serif;

        --accent: #ff6a6a;
        --accent-soft: rgba(255,106,106,0.15);
        --border-subtle: rgba(255,255,255,0.08);
        --bg-panel: rgba(9,10,18,0.85);
    }

    html, body, [class*="css"] {
        font-family: var(--font);
        background-color: var(--bg-page);
        color: white;
    }

    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border-heavy);
        padding-top: 30px;
    }

    .sidebar-title {
        font-size: 18px;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin-bottom: 12px;
    }

    .sidebar-item {
        padding: 10px 14px;
        border-radius: 8px;
        margin-bottom: 6px;
        cursor: pointer;
        transition: 0.15s ease;
    }
    .sidebar-item:hover {
        background: rgba(255,255,255,0.06);
    }
    .sidebar-item-active {
        background: rgba(255,255,255,0.10);
    }

    /* CARDS */
    .ai-card, .sp-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        padding: 22px;
        border-radius: 14px;
        margin-bottom: 20px;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.25);
    }

    .sp-chip {
        padding: 3px 10px;
        border-radius: 100px;
        background: var(--accent-soft);
        border: 1px solid rgba(255,255,255,0.12);
        font-size: 11px;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .sp-progress-outer {
        width: 100%;
        height: 8px;
        background: rgba(255,255,255,0.08);
        border-radius: 999px;
        overflow: hidden;
        margin-bottom: 6px;
    }

    .sp-progress-inner {
        height: 100%;
        background: linear-gradient(90deg, #ff6a6a, #ffb85a);
        border-radius: 999px;
        transition: width 0.3s ease;
    }

    .sp-match-title {
        font-weight: 600;
        font-size: 16px;
        margin-bottom: 4px;
    }

    .block-container {
        padding-top: 1.5rem;
    }

    /* Textarea + buttons */
    textarea {
        background: #0F1116 !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        padding: 14px !important;
        font-size: 15px !important;
    }
    textarea:focus {
        border-color: var(--primary) !important;
    }

    div.stButton > button {
        background: var(--primary);
        color: white;
        border-radius: 10px;
        padding: 10px 18px;
        font-weight: 600;
        font-size: 15px;
        border: none;
        transition: 0.2s ease;
        width: 100%;
    }
    div.stButton > button:hover {
        background: var(--primary-hover);
    }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar(active: str):
    """Render the left sidebar with an 'active' section."""
    with st.sidebar:
        st.markdown("<div class='sidebar-title'>SparkPath</div>", unsafe_allow_html=True)

        def item(label, page_name):
            cls = "sidebar-item"
            if active == page_name:
                cls += " sidebar-item-active"
            st.markdown(f"<div class='{cls}'>{label}</div>", unsafe_allow_html=True)

        item("🏠 Home", "Home")
        item("🎤 Career Explorer", "Career Explorer")
        item("📊 Insights Dashboard", "Insights")
        item("🙋 My Profile", "My Profile")
