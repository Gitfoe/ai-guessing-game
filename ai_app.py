import streamlit as st
import pandas as pd
from openai import OpenAI
import random

# Start the app locally by executing the command: streamlit run ai_app.py

# Load the Pokémon dataset
@st.cache_data
def load_pokemon_data():
    return pd.read_csv('data/pokemon.csv')
pokemon_data = load_pokemon_data()

# Define the sidebar text
with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/Gitfoe/ai-guessing-game/)"

# Set the Streamlit page title
st.title("💬 Who's that Pokémon?")

# Initialize the session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Please guess the Pokémon!"}]
    st.session_state["selected_pokemon"] = None
    st.session_state["game_over"] = False

# Function to pick a random Pokémon
def pick_random_pokemon():
    return pokemon_data.sample().iloc[0]

# Pick a Pokémon if not already picked
if st.session_state["selected_pokemon"] is None:
    st.session_state["selected_pokemon"] = pick_random_pokemon()
selected_pokemon = st.session_state["selected_pokemon"]

# Write selected Pokémon to screen (temporarily for debugging)
st.dataframe(selected_pokemon)

# System prompt for OpenAI
system_prompt = f"""
You are an intelligent and engaging assistant in a "Who's that Pokémon?" guessing game.
The player is trying to guess the name of a Pokémon based on your hints. 
You know everything about the Pokémon, but you should not directly reveal its name.
You can answer questions about its attributes.
If the player guesses incorrectly, guide them towards the correct answer.
Here are the details of the Pokémon you have to provide hints for:
- Name: {selected_pokemon['name']}
- Japanese Name: {selected_pokemon['japanese_name']}
- Pokedex Number: {selected_pokemon['pokedex_number']}
- Type(s): {selected_pokemon['type1']}, {selected_pokemon['type2']}
- Classification: {selected_pokemon['classification']}
- Height: {selected_pokemon['height_m']} m
- Weight: {selected_pokemon['weight_kg']} kg
- Abilities: {selected_pokemon['abilities']}
- Base Stats: HP {selected_pokemon['hp']}, Attack {selected_pokemon['attack']}, Defense {selected_pokemon['defense']}, Special Attack {selected_pokemon['sp_attack']}, Special Defense {selected_pokemon['sp_defense']}, Speed {selected_pokemon['speed']}
- Generation: {selected_pokemon['generation']}
- Legendary: {'Yes' if selected_pokemon['is_legendary'] else 'No'}
"""

# Write new messages to the chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Obtain a prompt from the user
if prompt := st.chat_input():
    # Check if OpenAI API Key is provided
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    # Create the OpenAI client
    client = OpenAI(api_key=openai_api_key)
    
    # Add the user's guess to the chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Check if the user's guess is correct
    if prompt.lower() == selected_pokemon["name"].lower():
        st.session_state["game_over"] = True
        msg = f"Right! It's {selected_pokemon['name']}! You're a master."
    else:
        # Send the conversation history and Pokémon data to OpenAI for generating a response
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                *st.session_state.messages,
            ]
        )
        msg = response.choices[0].message.content

    # Add assistant's message to the chat history and write it
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
    
    # End the game if guessed correctly
    if st.session_state["game_over"]:
        st.success("Congratulations! Restart the game to play again.")
        if st.button("Play Again"):
            st.session_state.clear()
            st.rerun()