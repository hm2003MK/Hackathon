# pages/3_My_Profile.py

import streamlit as st
from theme import apply_theme

apply_theme()

st.markdown(
    """
    <h2 style="font-size:32px; font-weight:700; margin-bottom:6px;">
        🧠 Your Creative Profile
    </h2>
    <p style="font-size:14px; opacity:0.7; max-width:620px;">
        Review your SparkPath creative persona, your traits, and any careers you've saved.
    </p>
    """,
    unsafe_allow_html=True
)

# =================================================================
# CHECK RESULTS
# =================================================================
if "spark_results" not in st.session_state or st.session_state.spark_results is None:
    st.warning("No profile available yet — try the 🎤 Career Explorer first.")
    st.stop()

results = st.session_state.spark_results

# =================================================================
# SAFE PERSONA HANDLING
# =================================================================
persona = results.get("persona", {})

# 🔥 normalize persona (fix for TypeError)
if isinstance(persona, str):
    persona = {
        "name": persona,
        "blurb": ""
    }

persona_name = persona.get("name", "Creative Explorer")
persona_blurb = persona.get("blurb", "")

# =================================================================
# DISPLAY PERSONA
# =================================================================
st.markdown("## 🌟 Your Creative Persona")

st.markdown(
    f"""
    <div class="sp-card" style="margin-bottom:14px;">
        <div class="sp-chip">Persona</div>
        <h3 style="margin-top:6px;">{persona_name}</h3>
        <p style="opacity:0.8;">{persona_blurb}</p>
    </div>
    """,
    unsafe_allow_html=True
)


# =================================================================
# TRAITS SECTION
# =================================================================
traits = results.get("traits", {})

st.markdown("## 🎨 Your Creative Traits")

if traits:
    st.json(traits)
else:
    st.info("No traits were extracted.")


# =================================================================
# SAVED CAREERS
# =================================================================
st.markdown("## ⭐ Saved Careers")

if "saved_careers" not in st.session_state:
    st.session_state.saved_careers = []

saved = st.session_state.saved_careers

if not saved:
    st.info("You haven’t saved any careers yet. Go to the **Career Explorer** page to save matches.")
else:
    for c in saved:
        st.markdown(
            f"""
            <div class="sp-card" style="margin-bottom:14px;">
                <div class="sp-chip">Saved Career</div>
                <h4 style="margin-top:4px;">{c['title']}</h4>
                <p style="opacity:0.7;">Match score when saved: {c['score']:.3f}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    if st.button("🗑 Clear Saved Careers"):
        st.session_state.saved_careers = []
        st.success("Cleared all saved careers.")


# =================================================================
# SHOW RAW REPORT
# =================================================================
st.markdown("## 📄 Full SparkPath Report")

full_report = results.get("report", "(no report generated)")
st.code(full_report)


