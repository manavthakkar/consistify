import streamlit as st
from streamlit_google_auth import Authenticate

# Page configuration
st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")

st.sidebar.title("Navigation")
st.title("Consistify")

st.write("Some description of the app")

# Centralized Google Authentication
authenticator = Authenticate(
    secret_credentials_path='google_credentials.json',
    cookie_name='auth_cookie',
    cookie_key='this_is_secret',
    redirect_uri='http://localhost:8501',
)

# Check authentication status
authenticator.check_authentification()

if st.session_state.get('connected', False):
    # If the user is logged in
    st.sidebar.success("Logged in successfully!")
    st.image(st.session_state['user_info'].get('picture'), width=80)
    st.write(f"**Hello, {st.session_state['user_info'].get('name')}!**")
    st.write(f"Your email is **{st.session_state['user_info'].get('email')}**.")
    
    # Logout button
    if st.button("Log out"):
        authenticator.logout()
        st.session_state.clear()
        st.experimental_rerun()  # Refresh the app to reflect the login state

else:
    # If the user is not logged in
    st.warning("Please log in to access the app features.")
    authenticator.login()
