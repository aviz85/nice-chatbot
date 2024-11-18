import streamlit as st
from openai import OpenAI

# Initialize session state for API key
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

st.title("ChatGPT Assistant")

# API key input in sidebar
with st.sidebar:
    api_key = st.text_input("Enter your OpenAI API key:", type="password", value=st.session_state.api_key)
    if api_key:
        st.session_state.api_key = api_key

# Display chat messages
for message in st.session_state.messages[1:]:  # Skip the system message
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input
if prompt := st.chat_input("What's on your mind?"):
    if not st.session_state.api_key:
        st.error("Please enter your OpenAI API key in the sidebar first!")
    else:
        # Initialize OpenAI client with current API key
        client = OpenAI(api_key=st.session_state.api_key)
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)

        # Get assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=st.session_state.messages,
                    stream=True
                )
                
                full_response = ""
                # Stream the response
                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.write(full_response + "▌")
                
                message_placeholder.write(full_response)
                
                # Add assistant response to chat history
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Add a clear button
if st.button("Clear Chat"):
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    st.rerun() 