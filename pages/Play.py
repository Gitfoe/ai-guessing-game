# Copyright 2024 Julian Calvin Rill

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
import pandas as pd
from openai import OpenAI

#region Streamlit Page Initialisation
# Define the sidebar text
with st.sidebar:
    st.session_state["openai_api_key"] = st.text_input("OpenAI API Key", type="password", value=st.session_state.get("openai_api_key", ""))
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"

# Set the Streamlit page title
st.title("💬 Who's that Pokémon?")
#endregion

#region Dataset 
# Load the Pokémon dataset
@st.cache_data
def load_pokemon_data():
    return pd.read_csv('data/pokemon.csv')
pokemon_data = load_pokemon_data()

def pick_random_pokemon():
    """Returns a random Pokémon from the dataset."""
    return pokemon_data.sample().iloc[0]
#endregion

#region Helper functions
def reset_session_state():
    """Resets the current to guess Pokémon and accompanying variables"""
    st.session_state["messages"] = [{"role": "assistant", "content": "Please start with guessing the Pokémon! You can ask me anything, but try to ask clever questions!"}]
    st.session_state["selected_pokemon"] = pick_random_pokemon()
    st.session_state["game_over"] = False
    st.session_state["current_game_guesses"] = 0
    st.session_state["current_game_hints"] = 0

    # Write selected Pokémon to screen (for debugging)
    #st.dataframe(st.session_state["selected_pokemon"])

def correct_guess():
    """Sets session variables for when the user guessed correctly"""
    st.session_state["current_game_guesses"] += 1
    st.session_state["game_over"] = True   

def game_over_check():
    """Shows the 'Play Again' button and disables the chat."""
    if st.session_state["game_over"]:
        st.button("Play Again", on_click=reset_session_state)
#endregion

#region Prompts
def get_system_prompt():
    """Returns the most recent system prompt for OpenAI based on the current session state."""
    mon = st.session_state["selected_pokemon"]
    return f"""
    You are an intelligent and engaging assistant in a "Who's that Pokémon?" guessing game.
    The player is trying to guess the name of a Pokémon based on your hints. 
    You know everything about the Pokémon and its attributes, but you should not directly reveal its name.
    The user may ask you questions or hints, but only reveal one attribute at a time.

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

    Start your responses with:
    - "Hint:" when giving the user information about the Pokémon.
    - "Correct!" if the user names the correct Pokémon.
    - "Incorrect!" if the user names an incorrect Pokémon.
    """

def get_judge_prompt():
    """Generates a prompt for the judging agent to evaluate the quality of guesses."""
    mon = st.session_state["selected_pokemon"]
    return f"""
    You are an expert judge evaluating the quality of guesses in a "Who's that Pokémon?" guessing game.
    The user has just finished the game by correctly guessing the Pokémon. Your task is to rate the quality of the guesses on a scale of 1 to 10.

    Consider the following factors:
    - How many guesses the user made before guessing correctly (4 guesses is the average)
    - How many hints were needed (7 hints is the average)
    - The similarity between the user's guesses and the correct Pokémon (e.g., type, generation, abilities).
    - A lower score indicates poor guess quality (many incorrect guesses, irrelevant guesses, lots of hints).
    - A higher score indicates excellent guess quality (few guesses, few hints, and guesses closely related to the correct Pokémon).

    The correct Pokémon's attributes are:
    - Name: {mon['name']}
    - Type(s): {mon['type1']}, {mon['type2']}
    - Classification: {mon['classification']}
    - Height: {mon['height_m']} m
    - Weight: {mon['weight_kg']} kg
    - Abilities: {mon['abilities']}
    - Base Stats: {mon['hp']} HP, {mon['attack']} Attack, {mon['defense']} Defense, {mon['sp_attack']} Special Attack, {mon['sp_defense']} Special Defense, {mon['speed']} Speed
    - Generation: {mon['generation']}
    - Legendary: {'Yes' if mon['is_legendary'] else 'No'}

    Here is the chat history:
    {st.session_state["messages"]}

    Here is the amount of guesses and hints:
    - Guesses: {st.session_state["current_game_guesses"]}
    - Hints: {st.session_state["current_game_hints"]}
    
    Respond in the following format, omitting the chevron icons: <rating from 1 to 10>: <brief explanation of your evaluation>
    """
#endregion

#region Persistent Storage
import json
import os

SAVE_FILE_PATH = "data/session_state.json"

def save_session_state():
    """Save the current session state to a JSON file."""
    data = {
        "guesses_per_completed_game": st.session_state.get("guesses_per_completed_game", []),
        "hints_per_completed_game": st.session_state.get("hints_per_completed_game", []),
        "judge_ratings_per_game": st.session_state.get("judge_ratings_per_game", []),
        "judge_explanations_per_game": st.session_state.get("judge_explanations_per_game", [])
    }
    with open(SAVE_FILE_PATH, "w") as file:
        json.dump(data, file)

def load_session_state():
    """Load the session state from a JSON file if available."""
    if os.path.exists(SAVE_FILE_PATH):
        with open(SAVE_FILE_PATH, "r") as file:
            data = json.load(file)
            st.session_state["guesses_per_completed_game"] = data.get("guesses_per_completed_game", [])
            st.session_state["hints_per_completed_game"] = data.get("hints_per_completed_game", [])
            st.session_state["judge_ratings_per_game"] = data.get("judge_ratings_per_game", [])
            st.session_state["judge_explanations_per_game"] = data.get("judge_explanations_per_game", [])
#endregion

# Initialize the session state
if "messages" not in st.session_state:
    reset_session_state()
    st.session_state["guesses_per_completed_game"] = []
    st.session_state["hints_per_completed_game"] = []
    st.session_state["judge_ratings_per_game"] = []
    st.session_state["judge_explanations_per_game"] = []
    load_session_state() # Load saved session state if available

# Write messages to the chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

game_over_check()

# Obtain a prompt from the user
if prompt := st.chat_input(disabled=st.session_state["game_over"]):
    # Initialise OpenAI client variable
    openai_client = None
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
        # Add the guesses and hints to the completed games
        st.session_state["guesses_per_completed_game"].append(st.session_state["current_game_guesses"])
        st.session_state["hints_per_completed_game"].append(st.session_state["current_game_hints"])

        # Call the judge LLM to evaluate the game
        judge_response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": get_judge_prompt()}
            ]
        )
        judge_result = judge_response.choices[0].message.content.strip()

        # Extract the rating and explanation
        try:
            rating, explanation = judge_result.split(": ", 1)
            rating = int(rating)  # Convert rating to an integer
        # Fallback in case of unexpected output
        except ValueError:
            rating, explanation = 5, "Invalid response from the judge."

        # Save the judge's rating
        st.session_state["judge_ratings_per_game"].append(rating)
        st.session_state["judge_explanations_per_game"].append(explanation)

        game_over_check() # Check if the game is over and show a button
        save_session_state() # Save session state to JSON
        st.rerun() # Rerun so that the chat_input() will be rendered disabled