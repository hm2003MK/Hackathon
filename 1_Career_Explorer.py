# pages/1_Career_Explorer.py

import streamlit as st
import json

from theme import apply_theme
from spark_conversation import run_spark_turn
from db import update_user, add_saved_career

from match_student_to_careers import (
    extract_traits,
    get_embedding,
    match_careers,
    build_report,
    career_embeddings
)

# ======================================================
# APPLY THEME
# ======================================================
apply_theme()

st.markdown(
    """
    <h2 style="font-size:32px; font-weight:700; margin-bottom:4px;">
        🎤 SparkPath – Conversational Career Explorer
    </h2>
    <p style="font-size:14px; opacity:0.7; max-width:640px;">
        Chat with Spark about your interests, strengths, and creative energy.
        Spark will listen, ask follow-ups, and then show you a creative persona
        and some possible entertainment career paths.
    </p>
    """,
    unsafe_allow_html=True
)

# ======================================================
# SESSION STATE SETUP
# ======================================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "summary_ready" not in st.session_state:
    st.session_state.summary_ready = False

if "results" not in st.session_state:
    st.session_state.results = None

user_id = st.session_state.get("user_id")

# ======================================================
# INITIAL MESSAGE
# ======================================================
if not st.session_state.chat_history:
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": (
            "Hey, I’m Spark ✨ Tell me about something creative you naturally "
            "gravitate toward—TikToks, dance, music, fashion, film, design… "
            "whatever feels most you."
        )
    })

# ======================================================
# SHOW CHAT
# ======================================================
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ======================================================
# USER INPUT
# ======================================================
if not st.session_state.summary_ready:
    user_input = st.chat_input("Tell Spark about your creative world...")
else:
    user_input = None

if user_input:
    # Add user msg
    st.session_state.chat_history.append(
        {"role": "user", "content": user_input}
    )

    # Run Groq chat turn
    spark_reply, _, _, _ = run_spark_turn(
        st.session_state.chat_history,
        profile={},       # unused with Groq
        phase="chat"      # unused with Groq
    )

    st.session_state.chat_history.append(
        {"role": "assistant", "content": spark_reply}
    )

    # Check if Spark asked something like "OK, ready for summary?"
    if any(word in spark_reply.lower() for word in ["summarize", "summary", "pull this together", "ready?"]):
        st.session_state.summary_ready = True

    st.rerun()

# ======================================================
# WHEN USER FINISHES → RUN MATCHING ENGINE
# ======================================================
if st.session_state.summary_ready and st.session_state.results is None:

    with st.spinner("Got it. Let me pull your vibe together… ✨"):

        user_text = " ".join(
            m["content"] for m in st.session_state.chat_history
            if m["role"] == "user"
        )

        # Build trait extraction chat
        chat_for_traits = [
            {"role": "assistant", "content": "You are Spark, an entertainment career coach."},
            {"role": "user", "content": user_text}
        ]

        traits = extract_traits(chat_for_traits)

        # Build embedding input
        text_block = (
            json.dumps(traits.get("interests", {})) + " " +
            json.dumps(traits.get("transferable_skills", {})) + " " +
            " ".join(traits.get("passion_signals", [])) + " " +
            user_text
        )

        emb = get_embedding(text_block)
        matches = match_careers(emb, career_embeddings)

        # Persona logic
        def infer_persona(traits_obj, combined_text):
            blob = (traits_obj.get("vibe_summary", "") + " " + combined_text).lower()

            if any(k in blob for k in ["dance", "movement", "choreo"]):
                return {"name": "The Movement Storyteller", "blurb": "You express emotion through movement and rhythm."}

            if any(k in blob for k in ["camera", "film", "edit", "video"]):
                return {"name": "The Visual Storyteller", "blurb": "You see stories in images and scenes."}

            if any(k in blob for k in ["music", "sound", "producer"]):
                return {"name": "The Music Architect", "blurb": "You shape energy through sound."}

            if any(k in blob for k in ["write", "script", "story"]):
                return {"name": "The Story Weaver", "blurb": "You craft stories and emotion through words."}

            return {"name": "The Creative Explorer", "blurb": "You have wide creative interests."}

        persona = infer_persona(traits, user_text)
        report = build_report(traits, matches)

        # Save
        st.session_state.results = {
            "traits": traits,
            "matches": matches,
            "persona": persona,
            "report": report
        }

        if user_id is not None:
            update_user(user_id, {
                "answers": {"chat_history": st.session_state.chat_history},
                "traits": traits,
                "persona": persona,
                "matches": matches,
            })

# ======================================================
# DISPLAY RESULTS
# ======================================================
if st.session_state.results:
    results = st.session_state.results
    persona = results["persona"]
    matches = results["matches"]

    st.markdown("## 🌟 Your Creative Identity")
    st.markdown(f"### **{persona['name']}**")
    st.markdown(persona["blurb"])

    st.markdown("## 🎯 Top Career Matches")
    for title, score in matches[:3]:
        st.markdown(f"**{title}** — match score: `{score:.3f}`")

    st.markdown("## 📄 Full SparkPath Report")
    st.code(results["report"])


