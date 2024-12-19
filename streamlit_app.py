import streamlit as st
from openai import OpenAI
from auth0.authentication import GetToken
from auth0.management import Auth0
from streamlit_auth0 import login_button

# Auth0 configuration
AUTH0_DOMAIN = "curiflow-dev.us.auth0.com"
AUTH0_CLIENT_ID = "NnioCmlbjs3JtPrRxcEIgDeJPEzQNnV0"
AUTH0_CLIENT_SECRET = "wqdZ2bMXg-qhMrqRGGkm4YeOkfWE2crkT63G38xV-oHVyQlzespHuVJqvOZ54Hq7"
AUTH0_CALLBACK_URL = "https://obscure-broccoli-94v5977r4rwcpq4p-8501.app.github.dev/"  # Replace with your deployment URL

# Initialize session state for authentication
if "auth_state" not in st.session_state:
    st.session_state["auth_state"] = "loading"  # Initial state

# Function to check authentication and update session state
def check_auth():
    user_info = login_button(
        client_id=AUTH0_CLIENT_ID,
        domain=AUTH0_DOMAIN
    )
    print(user_info)
    if user_info:
        st.session_state["auth_state"] = "authenticated"
        st.session_state["user_info"] = user_info
    else:
        st.session_state["auth_state"] = "unauthenticated"

# Call the authentication check
check_auth()
# Initialize login button
# Show loading spinner while fetching user info

# with st.spinner("Fetching user information..."):
#    user_info = login_button(
#        client_id=AUTH0_CLIENT_ID,
#        domain=AUTH0_DOMAIN
#   )

if st.session_state["auth_state"] == "loading":
    with st.spinner("Loading... Please wait."):
        pass


elif st.session_state["auth_state"] == "authenticated":
    user_info = st.session_state["user_info"]
    st.success(f"Logged in as: {user_info['email']}")  # Adjust based on what `user_info` contains
    st.write("Welcome to the app! You are authenticated.")
    # Show authenticated content
# Show title and description.
    st.title("📄 Document question answering")
    st.write(
        "Upload a document below and ask a question about it – GPT will answer! "
        "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
    )

    # Ask user for their OpenAI API key via `st.text_input`.
    # Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
    # via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.", icon="🗝️")
    else:

        # Create an OpenAI client.
        client = OpenAI(api_key=openai_api_key)

        # Let the user upload a file via `st.file_uploader`.
        uploaded_file = st.file_uploader(
            "Upload a document (.txt or .md)", type=("txt", "md")
        )

        # Ask the user for a question via `st.text_area`.
        question = st.text_area(
            "Now ask a question about the document!",
            placeholder="Can you give me a short summary?",
            disabled=not uploaded_file,
        )

        if uploaded_file and question:

            # Process the uploaded file and question.
            document = uploaded_file.read().decode()
            messages = [
                {
                    "role": "user",
                    "content": f"Here's a document: {document} \n\n---\n\n {question}",
                }
            ]

            # Generate an answer using the OpenAI API.
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                stream=True,
            )

            # Stream the response to the app using `st.write_stream`.
            st.write_stream(stream)
        # Create a logout button
        logout_url = f"https://{AUTH0_DOMAIN}/v2/logout?client_id={AUTH0_CLIENT_ID}&returnTo={AUTH0_CALLBACK_URL}"
        if st.button("Logout"):
            st.write(f'<a href="{logout_url}" target="_self">Click here to logout</a>', unsafe_allow_html=True)

else:
    st.info("Please log in to access the application..")