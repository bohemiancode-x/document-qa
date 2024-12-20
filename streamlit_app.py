import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from streamlit_auth0 import login_button

# Load environment variables from .env file
load_dotenv()

# Auth0 Configuration
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL")

# Initialize session state for authentication
if "auth_state" not in st.session_state:
    st.session_state["auth_state"] = "loading"

# CSS styles
def set_styles():
    st.markdown(
        """
        <style>
        .center-container {
            display: flex;
            justify-content: flex-end;
            margin-top: 20px;
        }
        .logout-button {
            border: none;
            padding: 10px 20px;
            text-decoration: underline;
            font-size: 14px;
            cursor: pointer;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Check authentication
def check_auth():
    user_info = login_button(client_id=AUTH0_CLIENT_ID, domain=AUTH0_DOMAIN)
    if user_info:
        st.session_state["auth_state"] = "authenticated"
        st.session_state["user_info"] = user_info
    else:
        st.session_state["auth_state"] = "unauthenticated"

# Logout button
def logout_button():
    logout_url = f"https://{AUTH0_DOMAIN}/v2/logout?client_id={AUTH0_CLIENT_ID}&returnTo={AUTH0_CALLBACK_URL}"
    st.markdown(
        f"""
        <div class="center-container">
            <a href="{logout_url}" target="_self" class="logout-button">Logout</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Protected page template
def protected_page(content_function):
    check_auth()
    set_styles()

    if st.session_state["auth_state"] == "loading":
        with st.spinner("Loading... Please wait."):
            pass

    elif st.session_state["auth_state"] == "authenticated":
        st.success(f"Logged in as: {st.session_state['user_info']['email']}")
        content_function()
        logout_button()

    else:
        st.info("Please log in to access the application.")

# Example content function
def document_qa_page():
    st.title("📄 Document Question Answering")
    st.write(
        "Upload a document below and ask a question about it – GPT will answer! "
        "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys)."
    )

    openai_api_key = st.text_input("OpenAI API Key", type="password")
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.", icon="🗝️")
        return

    client = OpenAI(api_key=openai_api_key)
    uploaded_file = st.file_uploader("Upload a document (.txt or .md)", type=("txt", "md"))

    question = st.text_area(
        "Now ask a question about the document!",
        placeholder="Can you give me a short summary?",
        disabled=not uploaded_file,
    )

    if uploaded_file and question:
        document = uploaded_file.read().decode()
        messages = [
            {"role": "user", "content": f"Here's a document: {document} \n\n---\n\n {question}"}
        ]

        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream=True,
        )
        st.write_stream(stream)

# Main app execution
if __name__ == "__main__":
    protected_page(document_qa_page)
