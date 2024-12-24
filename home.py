import streamlit as st
from streamlit_google_auth import Authenticate

# Initialize Google Authentication
authenticator = Authenticate(
    secret_credentials_path='google_credentials.json',  # Path to your Google credentials
    cookie_name='auth_cookie',                         # Cookie name for the session
    cookie_key='this_is_secret',                       # Secret key for the cookie
    redirect_uri='http://localhost:8501',              # Redirect URI for the Streamlit app
)

def home_page():
    st.title("Welcome to the Habit Tracker App")

    # Check authentication status
    authenticator.check_authentification()

    # Login or Logout button
    authenticator.login()

    # If the user is authenticated, display navigation and user details
    if st.session_state.get('connected', False):
        st.image(st.session_state['user_info'].get('picture'), width=80)
        st.write(f"**Hello, {st.session_state['user_info'].get('name')}!**")
        st.write(f"Your email: **{st.session_state['user_info'].get('email')}**")

        # Navigation menu using session state
        # st.sidebar.title("Navigation")
        pages = {
            "Home": "home",
            "Image Processing": "script1",
            "Monthly Visualization": "script2",
            "Yearly Overview": "script3",
        }

        # # Select the page
        # selected_page = st.sidebar.selectbox("Choose a page", list(pages.keys()))
        # st.session_state["selected_page"] = pages[selected_page]

        # Logout button in the sidebar
        if st.sidebar.button("Log out"):
            authenticator.logout()

        # Inform the user about navigation
        # st.info(f"Go to the **{selected_page}** page from the sidebar.")

    # If not authenticated, show a login prompt
    else:
        st.warning("Please log in using the button above to access the app.")

if __name__ == "__main__":
    home_page()
