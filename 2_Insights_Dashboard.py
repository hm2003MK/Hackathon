# pages/2_Insights_Dashboard.py

import streamlit as st
import pandas as pd
from theme import apply_theme

apply_theme()

st.markdown(
    """
    <h2 style="font-size:32px; font-weight:700; margin-bottom:4px;">
        📊 Insights Dashboard
    </h2>
    <p style="font-size:14px; opacity:0.7; max-width:620px;">
        View analytics on your creative profile, interests, and top entertainment career matches.
    </p>
    """,
    unsafe_allow_html=True
)

# Load Spark results
if "spark_results" not in st.session_state or st.session_state.spark_results is None:
    st.warning("No results yet. Run the 🎤 Career Explorer first.")
    st.stop()

results = st.session_state.spark_results
traits = results["traits"]
matches = results["matches"]

# ========== INTERESTS ==========
st.markdown("### 🎨 Interest Breakdown")

interests = traits.get("interests", {})
if interests:
    df_interests = pd.DataFrame(
        {"Dimension": list(interests.keys()), "Score": list(interests.values())}
    ).sort_values("Score", ascending=False)
    st.bar_chart(df_interests.set_index("Dimension"))
else:
    st.info("No interest scores detected.")

# ========== SKILLS ==========
st.markdown("### 🧰 Transferable Skills")

skills = traits.get("transferable_skills", {})
if skills:
    df_skills = pd.DataFrame(
        {"Skill": list(skills.keys()), "Score": list(skills.values())}
    ).sort_values("Score", ascending=False)
    st.bar_chart(df_skills.set_index("Skill"))
else:
    st.info("No skills detected.")

# ========== PASSION SIGNALS ==========
st.markdown("### 🔥 Passion Signals")
ps = traits.get("passion_signals", [])
st.write(", ".join(ps) if ps else "None detected.")

# ========== MATCH SCORES ==========
st.markdown("### 🎯 Career Match Scores")

if matches:
    titles = [m[0] for m in matches[:5]]
    scores = [float(m[1]) for m in matches[:5]]

    df_matches = pd.DataFrame({"Career": titles, "Score": scores})
    st.dataframe(df_matches, use_container_width=True)
else:
    st.info("No matches returned.")


