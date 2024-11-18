import streamlit as st
from openai import OpenAI

# Page config
st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stTextInput {
        width: 100%;
    }
    .stButton button {
        width: 100%;
        border-radius: 20px;
    }
    .settings-button button {
        background-color: #2a5298 !important;
        color: white;
        margin-bottom: 1rem;
    }
    .clear-button button {
        background-color: #ff4c4c !important;
    }
    .stButton button:hover {
        opacity: 0.8;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    h1 {
        background: linear-gradient(45deg, #1e3c72, #2a5298);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem 0;
    }
    .api-key-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session states
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "show_api_settings" not in st.session_state:
    st.session_state.show_api_settings = False

# Container for the header
with st.container():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🤖 AI Chat Assistant")

# Create two columns for chat and controls
chat_col, control_col = st.columns([4, 1])

with chat_col:
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        for message in st.session_state.messages[1:]:  # Skip the system message
            with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
                st.write(message["content"])

    # User input
    if prompt := st.chat_input("Send a message...", key="user_input"):
        if not st.session_state.api_key:
            st.error("Please configure your OpenAI API key in settings first!")
        else:
            # Initialize OpenAI client with current API key
            client = OpenAI(api_key=st.session_state.api_key)
            
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user", avatar="🧑‍💻"):
                st.write(prompt)

            # Get assistant response
            with st.chat_message("assistant", avatar="🤖"):
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

with control_col:
    st.markdown("### Controls")
    
    # Settings button
    if st.button("⚙️ API Settings", key="settings", help="Configure OpenAI API Key", type="primary", use_container_width=True):
        st.session_state.show_api_settings = not st.session_state.show_api_settings
    
    # API Settings Dialog
    if st.session_state.show_api_settings:
        with st.expander("API Configuration", expanded=True):
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                value=st.session_state.api_key,
                help="Enter your OpenAI API key to start chatting",
                placeholder="sk-..."
            )
            if api_key:
                st.session_state.api_key = api_key
                st.success("API Key saved!")
    
    # Add a clear button
    if st.button("🗑️ Clear Chat", help="Clear the chat history", type="secondary", use_container_width=True):
        st.session_state.messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        st.rerun()
    
    # Add info about the chat
    st.markdown("---")
    st.markdown("### Chat Info")
    message_count = len(st.session_state.messages) - 1  # Subtract system message
    st.markdown(f"Messages: **{message_count}**")
    
    # Show API status
    st.markdown("### API Status")
    if st.session_state.api_key:
        st.success("API Key Configured ✓")
    else:
        st.error("API Key Not Configured ✗")