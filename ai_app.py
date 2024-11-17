import streamlit as st
from openai import OpenAI
# streamlit run ai_app.py

# Define the sidebar text
with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password") # Ask for an OpenAPI key
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/Gitfoe/ai-guessing-game/)"

# Set the Streamlit page title
st.title("💬 Who's that Pokémon?")

# Write the first chat message
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Please guess the Pokémon!"}]

# Write new messages to the chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Obtain a prompt from the user
if prompt := st.chat_input():
    # Ask the user for an OpenAI key if not entered yet
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    # Create the OpenAI client
    client = OpenAI(api_key=openai_api_key)

    # Add the prompt to the chat history and write to the chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Send prompt and chat history to OpenAI API and write message
    response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.messages)
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)