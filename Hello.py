import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome to Who's That Pokémon? An AI-powered interactive guessing game! 👋")

st.sidebar.success("Select a page above.")

st.markdown(
    """
    I developed this game as part of a course in my Master's program in Cognitive Science.
    This course focuses on the application of AI technologies within web applications.
    [Source code](https://github.com/Gitfoe/ai-guessing-game)

    ## Features
    - **Interactive Chat Interface**: Engage with an AI-powered assistant that provides hints about a randomly selected Pokémon from generations 1 to 7.
    - **Scoring System**: Your guessing performance is evaluated by a judge model, which rates your accuracy on a scale of 1 to 10.
    - **Game Statistics**: Track your gameplay stats, including total games played, number of guesses, hints used, and judge ratings.
    - **Session Persistence**: Your progress is automatically saved to disk, allowing you to resume your game anytime.
    - **Game Statistics Dashboard**: The app also features a detailed statistics page that shows data such as the total guesses and the judge's rating.

    ## Instructions
    ### Playing the Game
    In the navigation pane on the left of your screen, go to the `Play` page to open the chat with the AI and start playing the guessing game!

    ### OpenAI API key
    In order to play the game, you need an [OpenAI API key](https://platform.openai.com/account/api-keys).
    You can enter your API key directly in the sidebar on the `Play` page. Press the `Enter` key after inputting the API key.
    This API key is only saved in memory.

    ### Viewing the Statistics Dashboard
    On the `Stats` page, you can find the Statistics Dashboard. This dashboard is appended with new statistics after the end of every game.
"""
)
