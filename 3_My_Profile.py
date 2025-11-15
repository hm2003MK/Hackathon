import streamlit as st
from theme import apply_theme, render_sidebar

apply_theme()

st.markdown(
    """
    <h2 style="font-size:32px; font-weight:700; margin-bottom:4px;">
        🙋 My Profile
    </h2>
    <p style="font-size:14px; opacity:0.7; max-width:620px;">
        Review your SparkPath responses and any careers you've saved during exploration.
    </p>
    """,
    unsafe_allow_html=True
)

# ======================================================
# ORIGINAL ANSWERS
# ======================================================
st.markdown("### ✏️ Your Answers to SparkPath")

if "answers" in st.session_state and st.session_state.answers:
    for qid, text in st.session_state.answers.items():
        st.markdown(f"**{qid.replace('_', ' ').title()}**")
        st.write(text if text.strip() else "_(Skipped)_")
        st.markdown("---")
else:
    st.info("No answers found yet. Try the **🎤 Career Explorer** page first.")

# ======================================================
# SAVED CAREERS
# ======================================================
st.markdown("### ⭐ Saved Careers")

saved = st.session_state.get("saved_careers", [])
if not saved:
    st.info("You haven’t saved any careers yet. On the **Career Explorer** page, click ⭐ Save on a match.")
else:
    for c in saved:
        st.markdown(
            f"""
            <div class="sp-card">
                <div class="sp-chip">Saved Career</div>
                <div class="sp-match-title">{c['title']}</div>
                <p style="font-size:13px; opacity:0.7;">Match score when saved: {c['score']:.3f}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    if st.button("🗑 Clear Saved Careers"):
        st.session_state.saved_careers = []
        st.success("Cleared all saved careers from your profile.")
