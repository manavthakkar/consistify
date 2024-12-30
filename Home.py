
import streamlit as st
from PIL import Image
from st_social_media_links import SocialMediaIcons

import auth_functions
import utils

st.set_page_config(page_title="Home", page_icon="🏠", layout="centered")

st.image("assets/consistify-logo-full.png", width=300)

def home_page():
    st.title("Welcome to Consistify!")

    # Display the Consistify logo
    utils.add_side_logo()

    # If the user is authenticated, display navigation and user details
    if "user_info" not in st.session_state:
        st.markdown("""
        Transform your habits, transform your life – one day at a time with Consistify! ✨  
        Log in to unlock 🔓 personalized insights and take control of your progress. 📊🚀
        """)

        st.write("")

        col1, col2, col3 = st.columns([1, 2, 1])
        do_you_have_an_account = col2.selectbox(label="Do you have an account?", options=("Yes", "No", "I forgot my password"))
        auth_form = col2.form(key="Authentication form", clear_on_submit=False)
        email = auth_form.text_input(label="Email")
        password = auth_form.text_input(label="Password", type="password") if do_you_have_an_account in {"Yes", "No"} else auth_form.empty()
        auth_notification = col2.empty()

        if do_you_have_an_account == "Yes" and auth_form.form_submit_button(label="Sign In", use_container_width=True, type="primary"):
            with auth_notification, st.spinner("Signing in"):
                auth_functions.sign_in(email, password)

        elif do_you_have_an_account == "No" and auth_form.form_submit_button(label="Create Account", use_container_width=True, type="primary"):
            with auth_notification, st.spinner("Creating account"):
                auth_functions.create_account(email, password)

        elif do_you_have_an_account == "I forgot my password" and auth_form.form_submit_button(label="Send Password Reset Email", use_container_width=True, type="primary"):
            with auth_notification, st.spinner("Sending password reset link"):
                auth_functions.reset_password(email)

        if "auth_success" in st.session_state:
            auth_notification.success(st.session_state.auth_success)
            del st.session_state.auth_success
        elif "auth_warning" in st.session_state:
            auth_notification.warning(st.session_state.auth_warning)
            del st.session_state.auth_warning

        st.divider()

    else:
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

        template_link = "https://drive.google.com/file/d/1cpl8YLXIe4vJfZ4hAozNPmR3PP9_IRaU/view?usp=sharing"
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
        At **Consistify**, your privacy is our priority. We adhere to the following principles:

        - **Data Collection**: We only collect essential data, such as your email for authentication and habit data for generating personalized insights.
        - **Data Usage**: Your data is never shared and is used solely for providing habit-tracking analysis.
        - **Sensitive Information**: Passwords are securely handled by Firebase Authentication and are never stored by us.
        - **User Control**: You have full control over your data and can delete specific months, years, or all your data at any time.
        - **Data Security**: All data exchanges are encrypted, and your habit data is securely stored in Firebase Firestore.

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
        "https://github.com/manavthakkar",
        ]

        social_media_icons = SocialMediaIcons(social_media_links)

        social_media_icons.render(sidebar=False, justify_content="space-evenly")

        # Logout button in the sidebar
        if st.sidebar.button("Log out"):
            auth_functions.sign_out()
            st.rerun()

if __name__ == "__main__":
    home_page()
