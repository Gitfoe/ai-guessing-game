import streamlit as st
import pandas as pd
from openai import OpenAI

# Define the sidebar text
with st.sidebar:
    st.session_state["openai_api_key"] = st.text_input("OpenAI API Key", type="password", value=st.session_state.get("openai_api_key", ""))
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/Gitfoe/ai-guessing-game/)"
    st.write(st.session_state)

# Set the Streamlit page title
st.title("💬 Who's that Pokémon?")

# Load the Pokémon dataset
@st.cache_data
def load_pokemon_data():
    return pd.read_csv('data/pokemon.csv')
pokemon_data = load_pokemon_data()

#region Functions
def pick_random_pokemon():
    """Returns a random Pokémon from the dataset."""
    return pokemon_data.sample().iloc[0]

def reset_session_state():
    """Resets the current to guess Pokémon and accompanying variables"""
    st.session_state["messages"] = [{"role": "assistant", "content": "Please guess the Pokémon!"}]
    st.session_state["selected_pokemon"] = pick_random_pokemon()
    st.session_state["game_over"] = False
    st.session_state["current_game_guesses"] = 0
    st.session_state["current_game_hints"] = 0

    # Write selected Pokémon to screen (temporarily for debugging)
    st.dataframe(st.session_state["selected_pokemon"])

def get_system_prompt():
    """Returns the most recent system prompt for OpenAI based on the current session state."""
    mon = st.session_state["selected_pokemon"]
    return f"""
    You are an intelligent and engaging assistant in a "Who's that Pokémon?" guessing game.
    The player is trying to guess the name of a Pokémon based on your hints. 
    You know everything about the Pokémon and its attributes, but you should not directly reveal its name.
    The user may ask you questions or hints, but only reveal one attribute at a time.
    When giving the user information about the Pokémon, start your response with "Hint:"
    If the user names the correct Pokémon, start your response with "Correct!".
    If the user names an incorrect Pokémon, start your response with "Incorrect!".
    Here are the attributes of the Pokémon:
    - Name: {mon['name']}
    - Type(s): {mon['type1']}, {mon['type2']}
    - Classification: {mon['classification']}
    - Height: {mon['height_m']} m
    - Weight: {mon['weight_kg']} kg
    - Abilities: {mon['abilities']}
    - Base Stats: {mon['hp']} HP, {mon['attack']} Attack, {mon['defense']} Defense, {mon['sp_attack']} Special Attack, {mon['sp_defense']} Special Defense, {mon['speed']} Speed
    - Generation: {mon['generation']}
    - Legendary: {'Yes' if mon['is_legendary'] else 'No'}
    """
#endregion

# Initialize the session state
if "messages" not in st.session_state:
    reset_session_state()
    st.session_state["guesses_per_completed_game"] = []
    st.session_state["hints_per_completed_game"] = []

# Initialise empty variables
openai_client = None

# Write messages to the chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Sets session variables for when the user guessed correctly
def correct_guess():
    st.session_state["current_game_guesses"] += 1
    st.session_state["game_over"] = True    

# Obtain a prompt from the user
if prompt := st.chat_input():
    # Check if OpenAI API Key is provided, prompt the user if not
    if not st.session_state["openai_api_key"]:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    # Create the OpenAI client if it doesn't exist yet
    elif openai_client is None:
        openai_client = OpenAI(api_key=st.session_state["openai_api_key"])
    
    # Add the user's guess to the chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Check if the user guessed the correct Pokémon exactly
    mon = st.session_state["selected_pokemon"]
    if prompt.lower() == mon["name"].lower():
        msg = f"Correct! It's {mon['name']}!"
        correct_guess()
    # If not, send the more complex prompt to OpenAI
    else:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": get_system_prompt()},
                *st.session_state.messages,
            ]
        )
        msg = response.choices[0].message.content

        # Check if OpenAI's response indicates an (in)correct guess or a hint and log it
        if msg.strip().lower().startswith("correct"):
            correct_guess()
        elif msg.strip().lower().startswith("incorrect"):
            st.session_state["current_game_guesses"] += 1
        elif "hint:" in msg.strip().lower():
            st.session_state["current_game_hints"] += 1
    
    # Add assistant's message to the chat history and write it
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
    
    # End the game if guessed correctly
    if st.session_state["game_over"]:
        st.success("Congratulations! You've finished this round. You can continue playing if you want.")
        st.session_state["guesses_per_completed_game"].append(st.session_state["current_game_guesses"])
        st.session_state["hints_per_completed_game"].append(st.session_state["current_game_hints"])

        # Debug
        st.write(st.session_state)

        # Display button and prepare for new game once clicked
        st.button("Play Again", on_click=reset_session_state)