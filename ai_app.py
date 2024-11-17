import streamlit as st
import pandas as pd
from openai import OpenAI

# Start the app locally by executing the command: streamlit run ai_app.py

# Load the Pokémon dataset
@st.cache_data
def load_pokemon_data():
    return pd.read_csv('data/pokemon.csv')
pokemon_data = load_pokemon_data()

# Write data to the screen (temporarily for debugging)
st.write(pokemon_data)

# Define the sidebar text
with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password") # Ask for an OpenAPI key
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/Gitfoe/ai-guessing-game/)"

# Set the Streamlit page title
st.title("💬 Who's that Pokémon?")

# Initialize the session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Please guess the Pokémon!"}]
    st.session_state["selected_pokemon"] = None
    st.session_state["hints_given"] = 0
    st.session_state["game_over"] = False

# Function to pick a random Pokémon
def pick_random_pokemon():
    return pokemon_data.sample().iloc[0]

# Pick a Pokémon if not already picked
if st.session_state["selected_pokemon"] is None:
    st.session_state["selected_pokemon"] = pick_random_pokemon()
selected_pokemon = st.session_state["selected_pokemon"]

# Write selected Pokémon to screen (temporarily for debugging)
st.write(selected_pokemon)

# Function to generate hints based on the Pokémon attributes
def generate_hint(hint_number, pokemon):
    hints = [
        f"This Pokémon belongs to Generation {pokemon['generation']}.",
        f"Its primary type is {pokemon['type1']}." + (f" and secondary type is {pokemon['type2']}." if not pd.isna(pokemon['type2']) else ""),
        f"It has an ability like {pokemon['abilities'].split(',')[0]}.",
        f"Its classification is '{pokemon['classification']}'.",
        f"The Pokémon is {'Legendary' if pokemon['is_legendary'] else 'not Legendary'}.",
        f"It has a base HP of {pokemon['hp']}, Attack of {pokemon['attack']}, and Speed of {pokemon['speed']}.",
    ]
    return hints[hint_number] if hint_number < len(hints) else "No more hints available!"

# Write new messages to the chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Define prompts
system_prompt = """
You are an intelligent and engaging assistant in a "Who's that Pokémon?" guessing game.
Your role is to help the player guess the name of a randomly selected Pokémon by providing clues and responding to their questions.
Your responses should be friendly, encouraging, and informative, but avoid directly revealing the Pokémon's name. Here are your guidelines:
"""

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
        # Provide hints or ask OpenAI for a response
        hint_message = ""
        if st.session_state["hints_given"] < 5:
            hint_message = generate_hint(st.session_state["hints_given"], selected_pokemon)
            st.session_state["hints_given"] += 1
        else:
            hint_message = "Try again or type 'I give up' to reveal the answer."
        
        # Use OpenAI to create a response based on the hint
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                *st.session_state.messages,
                {"role": "assistant", "content": hint_message}
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
            st.experimental_rerun()