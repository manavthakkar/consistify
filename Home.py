import streamlit as st
from streamlit_google_auth import Authenticate
import utils
from PIL import Image
import json
from st_social_media_links import SocialMediaIcons

st.set_page_config(page_title="Home", page_icon="🏠", layout="centered")

st.image("assets/consistify-logo-full.png", width=300)

# Dynamically construct the JSON credentials using st.secrets
google_credentials = {
    "web": {
        "client_id": st.secrets["google_auth"]["client_id"],
        "project_id": st.secrets["google_auth"]["project_id"],
        "auth_uri": st.secrets["google_auth"]["auth_uri"],
        "token_uri": st.secrets["google_auth"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["google_auth"]["auth_provider_x509_cert_url"],
        "client_secret": st.secrets["google_auth"]["client_secret"],
        "redirect_uris": st.secrets["google_auth"]["redirect_uris"]
    }
}

# Write the credentials to a JSON file dynamically
with open("google_credentials.json", "w") as f:
    json.dump(google_credentials, f)

# Initialize Google Authentication
authenticator = Authenticate(
    secret_credentials_path='google_credentials.json', # Path to Google credentials
    cookie_name='auth_cookie',                         # Cookie name for the session
    cookie_key=st.secrets["auth"]["cookie_key"],                       # Secret key for the cookie
    redirect_uri=st.secrets["google_auth"]["redirect_uris"][0],              # Redirect URI for the Streamlit app
)

def home_page():
    st.title("Welcome to Consistify!")

    # Check authentication status
    authenticator.check_authentification()

    # Login or Logout button
    authenticator.login()

    # Display the Consistify logo
    utils.add_side_logo()

    # If the user is authenticated, display navigation and user details
    if st.session_state.get('connected', False):
        st.subheader(f"Hello, {st.session_state['user_info'].get('name').split()[0]}! 👋")
        #st.image(st.session_state['user_info'].get('picture'), width=80)
        #st.write(f"**Hello, {st.session_state['user_info'].get('name')}!**")
        #st.write(f"Logged in as: **{st.session_state['user_info'].get('email')}**")

        st.markdown("""
            **Consistify** is your go-to solution for effortless habit tracking, helping you stay consistent and focused. Consistify makes the process simple and effective! 🏆

            Here’s how it works: track your progress daily on a printable template, then upload a photo of your completed template at the end of the month. From there, the system analyzes your data to create **detailed monthly and yearly insights**. 📊

            With these insights, you can easily monitor your progress, uncover trends, and stay inspired to achieve your goals. Whether you’re building new habits or strengthening existing ones, **Consistify** provides the feedback you need to succeed. 🚀
                                """)
        
        st.subheader("How to Use Consistify 🛠️")
        st.markdown("""
        1. **Print and Fill the Template** 📝: Download the habit tracking template and keep it handy. Mark a ❌ each day you complete a habit.
        2. **Snap and Upload** 📸: At the end of the month, take a picture of your completed template and upload it to Consistify. 
        3. **Let the Magic Happen** ✨: Our app analyzes the image, extracts all habit data, and stores it securely.
        4. **Get Insights** 📊: View your **monthly** and **yearly habit insights** to track your progress over time.
        5. **Manage Your Data** 🗑️: Delete your **monthly**, **yearly**, or **lifetime data** anytime for full control.""")
        
        template_link = "https://template-link.com/template.pdf"  
        st.markdown(f"[📥 Download the consistify template]({template_link})")

        st.write("**Filled template example:**")
        st.markdown("""
        **Cover the portion of the template when clicking a picture as shown in the image below**. 
        This is required by the system to detect the markers accurately. 

        - You can cover it with your **finger** ☝️ or use any **small object** 🧩.
        - Make sure the rest of the template is clearly visible in the picture. 📷
                
        You can try uploading this image as well 😉
        """)
        
        # Display Template Image
        template_image_path = "assets/example.png"  
        template_image = Image.open(template_image_path)
        st.image(template_image, caption="Filled template example 🖼️", use_container_width=True)

        # Display Template Image
        # processed_image_path = "assets/processed-example.png"  
        # processed_image = Image.open(processed_image_path)
        # st.image(processed_image, caption="Processed template example 🖼️", use_container_width=True)

        st.markdown("""
        ### Visualize Your Progress Like Never Before! 📊

        Consistify takes your habit tracking to the next level by transforming your data into beautiful, easy-to-understand visualizations. See how your habits evolve over time with:

        - **Monthly Insights**: Track your performance for each habit and identify patterns within the month.
        - **Yearly Trends**: Get a bird’s-eye view of your progress across the entire year to stay motivated and focused.

        Below is an example of how your **monthly** and **yearly visualizations** will look:
        """)
        st.image("assets/filled-month.png", caption="Monthly Visualization Example 📅", use_container_width=True)
        st.image("assets/filled-year.png", caption="Yearly Overview Example 📈", use_container_width=True)

        # Privacy Policy
        st.header("Privacy Policy 🛡️")
        st.markdown("""
        At Consistify, your privacy is our priority. Here’s how we keep your data safe:
        - **Cloud Storage** ☁️: Your habit data is securely stored in the cloud for easy access anytime.
        - **Anonymous Identification** 🆔: Users are identified by a unique user ID, ensuring complete anonymity.
        - **Your Choice** 🗑️: You can delete any or all of your data (monthly, yearly, or lifetime) whenever you want.
        """)

        # Contact Information
        st.header("Get in Touch 📬")
        st.markdown("""
        Have questions or feedback? Feel free to [reach out](mailto:manavt2000@gmail.com) to me!

        I'd love to hear from you and help you make the most of Consistify! 🌟
        """)

        st.divider()

        social_media_links = [
        "https://www.linkedin.com/in/manavt2000",
        "https://github.com/manavthakkar"
        ]

        social_media_icons = SocialMediaIcons(social_media_links) 

        social_media_icons.render(sidebar=False, justify_content="space-evenly")

        # Logout button in the sidebar
        if st.sidebar.button("Log out"):
            authenticator.logout()

    # If not authenticated, show a login prompt
    else:
        st.info("Please log in using the button above to get started.")

if __name__ == "__main__":
    home_page()
