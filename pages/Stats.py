import streamlit as st
import pandas as pd

# Set the Streamlit page title
st.title("📊 Game Statistics")

# Check if there is any game data
if "guesses_per_completed_game" not in st.session_state or len(st.session_state["guesses_per_completed_game"]) == 0:
    st.write("No games played yet.")
else:
    # Get guesses and hints data
    guesses = st.session_state["guesses_per_completed_game"]
    hints = st.session_state["hints_per_completed_game"]

    # Display basic stats in columns
    total_games = len(guesses)
    total_guesses = sum(guesses)
    total_hints = sum(hints)
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Games", value=total_games)
    col2.metric(label="Total Guesses", value=total_guesses)
    col3.metric(label="Total Hints", value=total_hints)
    
    # Display Bar Chart for guesses
    st.write("#### Guesses per Game")
    guesses_df = pd.DataFrame({"Game Number": range(1, total_games + 1), "Guesses": guesses})
    st.bar_chart(guesses_df.set_index("Game Number")["Guesses"])

    # Display Bar Chart for hints
    st.write("#### Hints per Game")
    hints_df = pd.DataFrame({"Game Number": range(1, total_games + 1), "Hints": hints})
    st.bar_chart(hints_df.set_index("Game Number")["Hints"])