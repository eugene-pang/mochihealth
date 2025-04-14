import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="Mood Tracker", layout="centered")

st.title("Mood Tracker")

# Initialize mood log
if "mood_log" not in st.session_state:
    st.session_state.mood_log = pd.DataFrame(columns=["timestamp", "mood", "note"])

# --- Mood Logging UI ---
st.header("1. Log your mood")

mood = st.radio(
    "How are you feeling?",
    ["Happy 😊", "Angry 😠", "Confused 😕", "Celebratory 🎉"],
    horizontal=True
)
note = st.text_input("Optional note:", placeholder="e.g., feeling very bad because a client was rude to me")

if st.button("Submit Mood"):
    new_entry = {
        "timestamp": datetime.now(),
        "mood": mood,
        "note": note
    }

    st.session_state.mood_log = pd.concat(
        [st.session_state.mood_log, pd.DataFrame([new_entry])],
        ignore_index=True
    )

    st.session_state.mood_log.to_csv("mood_log.csv", index=False)
    st.success("Mood logged and saved to CSV!")

# --- Mood Visualization ---
st.header("2. Today's vibes over time")

df = st.session_state.mood_log.copy()
df["timestamp"] = pd.to_datetime(df["timestamp"])
today = pd.Timestamp.now().date()
df_today = df[df["timestamp"].dt.date == today]

if df_today.empty:
    st.info("No moods logged yet today.")
else:
    # Normalize mood values
    df_today["mood"] = df_today["mood"].str.strip()

    # Hourly summary
    df_today["hour"] = df_today["timestamp"].dt.hour
    pivot = df_today.pivot_table(index="hour", columns="mood", aggfunc="size", fill_value=0)

    # Ensure all expected moods are present
    all_moods = ["Happy 😊", "Angry 😠", "Confused 😕", "Celebratory 🎉"]
    for mood in all_moods:
        if mood not in pivot.columns:
            pivot[mood] = 0
    pivot = pivot[all_moods]  # Keep columns in correct order

    # Define mood colors
    mood_colors = {
        "Happy 😊": "#ffd700",
        "Angry 😠": "#ff6961",
        "Confused 😕": "#a9a9a9",
        "Celebratory 🎉": "#87cefa"
    }

    fig, ax = plt.subplots(figsize=(10, 6))
    bottom = pd.Series([0] * len(pivot), index=pivot.index)

    for mood in all_moods:
        values = pivot[mood]
        bars = ax.bar(pivot.index, values, bottom=bottom, label=mood, color=mood_colors[mood])

        # Add percent labels inside bars
        total_per_hour = pivot.sum(axis=1)
        for i, (bar, val) in enumerate(zip(bars, values)):
            total = total_per_hour.iloc[i]
            if val > 0 and total > 0:
                percent = val / total * 100
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_y() + bar.get_height() / 2,
                    f"{percent:.0f}%",
                    ha='center',
                    va='center',
                    fontsize=9,
                    color="black"
                )

        bottom += values

    ax.set_title("Mood Breakdown by Hour (Today)", fontsize=16)
    ax.set_ylabel("Mood Count")
    ax.set_xlabel("Hour of the Day")
    ax.set_xticks(pivot.index)
    ax.set_xticklabels([f"{hour}:00" for hour in pivot.index])
    ax.legend(title="Mood", bbox_to_anchor=(1.05, 1), loc="upper left")
    ax.yaxis.get_major_locator().set_params(integer=True)  # Whole number y-axis

    st.pyplot(fig)


# Optional: Show full log
with st.expander("See full mood log"):
    st.dataframe(st.session_state.mood_log)
