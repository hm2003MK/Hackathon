import streamlit as st
from theme import apply_theme, render_sidebar
from db import create_user, get_user

if "user_id" not in st.session_state:
    st.session_state.user_id = create_user()


# ======================================================
# PAGE CONFIG — ONLY HERE
# ======================================================
st.set_page_config(
    page_title="SparkPath – Entertainment Career Explorer",
    page_icon="🎤",
    layout="wide"
)

# Apply global theme + sidebar
apply_theme()

# ======================================================
# HOME / LANDING CONTENT
# ======================================================
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown(
        """
        <h1 style="font-size:52px; font-weight:800; margin-bottom:8px;">
            🎤 SparkPath – Entertainment Career Explorer
        </h1>
        <p style="font-size:18px; opacity:0.85; max-width:640px;">
            SparkPath helps teens and young adults translate their <b>real interests</b> 
            into <b>real entertainment careers</b> across Film, Music, Performance, and Digital Media.
        </p>
        <p style="font-size:14px; opacity:0.7; max-width:640px;">
            Powered by Amazon Bedrock, an entertainment career graph, and a personality-aware matching engine.
        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### How it works")
    st.markdown(
        """
        1. **Answer 5 quick questions** about your interests, strengths, and creative environment.  
        2. **Spark builds a creative profile** (vibe, interests, transferable skills).  
        3. **You get matched** to top entertainment careers with next-step pathways.  
        4. Explore insights, save careers, and share your Spark identity.
        """
    )

    st.markdown("---")
    st.markdown("#### Ready to try it?")

    # Streamlit will automatically show the pages in the sidebar “Pages” menu.
    st.write("Go to **🎤 Career Explorer** in the left sidebar to get started.")

with col2:
    st.markdown(
        """
        <div class="sp-card">
            <div class="sp-chip">Demo Snapshot</div>
            <h3>What SparkPath returns</h3>
            <ul style="font-size:14px; opacity:0.85;">
                <li><b>Creative Persona</b> (e.g., “The Visual Storyteller”)</li>
                <li><b>Top 3 Career Matches</b> with match scores</li>
                <li><b>Suggested learning path</b> and starter steps</li>
                <li><b>Skill + interest breakdown</b></li>
            </ul>
            <p style="font-size:13px; opacity:0.65;">
                Use the <b>Insights Dashboard</b> to view analytics, and 
                <b>My Profile</b> to review your answers and saved careers.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )



