import streamlit as st
import pandas as pd

# Set the Streamlit page title
st.title("📊 Game Statistics")

# Check if there is any game data
if ("guesses_per_completed_game" not in st.session_state or len(st.session_state["guesses_per_completed_game"]) == 0):
    st.write("No games played yet.")
else:
    # Get guesses, hints, and judge ratings data
    guesses = st.session_state["guesses_per_completed_game"]
    hints = st.session_state["hints_per_completed_game"]
    ratings = st.session_state.get("judge_ratings_per_game", [])
    explanations = st.session_state.get("judge_explanations_per_game", [])

    # Display basic stats in columns
    total_games = len(guesses)
    total_guesses = sum(guesses)
    total_hints = sum(hints)
    avg_rating = sum(ratings) / len(ratings) if ratings else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Total Games", value=total_games)
    col2.metric(label="Total Guesses", value=total_guesses)
    col3.metric(label="Total Hints", value=total_hints)
    col4.metric(label="Average Rating", value=f"{avg_rating:.1f} / 10")

    # Merge guesses, hints, and ratings into a single DataFrame for plotting
    stats_df = pd.DataFrame({
        "Game Number": range(1, total_games + 1),
        "Guesses": guesses,
        "Hints": hints,
        "Rating": ratings
    })

    # Display a line chart with two lines for guesses and hints, and a third for ratings
    st.subheader("Guesses, Hints, and Ratings per Game")
    st.line_chart(stats_df.set_index("Game Number"))

    # Display the full table for detailed insights
    st.subheader("Detailed Game Statistics")
    st.dataframe(stats_df, hide_index=True)

    # Display expandable explanations for each game
    st.subheader("Judge's Explanations")
    for game_num, (rating, explanation) in enumerate(zip(ratings, explanations), start=1):
        with st.expander(f"Game {game_num}: Rating {rating}/10"):
            st.write(explanation)