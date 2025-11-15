import streamlit as st
import pandas as pd

from theme import apply_theme, render_sidebar

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

if "results" not in st.session_state or st.session_state.results is None:
    st.warning("No results yet. Run the **🎤 Career Explorer** first.")
    st.stop()

results = st.session_state.results
traits = results["traits"]
matches = results["matches"]

# ======================================================
# INTERESTS CHART
# ======================================================
st.markdown("### 🎨 Interest Breakdown")

interests = traits.get("interests", {})
if interests:
    df_interests = pd.DataFrame(
        {"Dimension": list(interests.keys()), "Score": list(interests.values())}
    ).sort_values("Score", ascending=False)
    st.bar_chart(df_interests.set_index("Dimension"))
else:
    st.info("No structured interest scores were returned by the engine.")

# ======================================================
# TRANSFERABLE SKILLS
# ======================================================
st.markdown("### 🧰 Transferable Skills")

skills = traits.get("transferable_skills", {})
if skills:
    df_skills = pd.DataFrame(
        {"Skill": list(skills.keys()), "Score": list(skills.values())}
    ).sort_values("Score", ascending=False)
    st.bar_chart(df_skills.set_index("Skill"))
else:
    st.info("No structured transferable skills were returned by the engine.")

# ======================================================
# PASSION SIGNALS
# ======================================================
st.markdown("### 🔥 Passion Signals (Keywords)")

passion_signals = traits.get("passion_signals", [])
if passion_signals:
    st.write(", ".join(passion_signals))
else:
    st.info("No passion signals were extracted for this run.")

# ======================================================
# CAREER MATCH SUMMARY
# ======================================================
st.markdown("### 🎯 Career Match Scores")

if matches:
    titles = [m[0] for m in matches[:5]]
    scores = [float(m[1]) for m in matches[:5]]

    df_matches = pd.DataFrame({"Career": titles, "Match Score": scores})
    st.dataframe(df_matches, use_container_width=True)
else:
    st.info("No matches were returned by the engine.")

st.markdown("---")
st.caption("These analytics can be extended to cohort-level views for schools, non-profits, or partners.")
