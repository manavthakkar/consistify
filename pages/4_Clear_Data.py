import streamlit as st
from firebase_admin import credentials, firestore
import firebase_admin
import calendar
import utils

st.set_page_config(page_title="Clear Data", page_icon="🗑️")

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def get_user_data(user_id):
    """
    Fetches the user's data from Firestore.
    
    Args:
        user_id (str): The user ID.
    
    Returns:
        dict: The user's data or None if not found.
    """
    doc = db.collection("users").document(user_id).get()
    return doc.to_dict() if doc.exists else None

def delete_data_for_year_month(user_id, year, month):
    """
    Deletes data for a specific year and month from a user's document in Firestore.
    
    Args:
        user_id (str): The ID of the user.
        year (str): The year to delete (e.g., "2020").
        month (str): The month to delete (e.g., "January").
    """
    try:
        # Reference the Firestore document for the user
        user_ref = db.collection("users").document(user_id)

        # Build the path to the specific year and month
        field_path = f"{year}.{month}"

        # Use Firestore's update method with DELETE_FIELD to remove the data
        from google.cloud.firestore_v1 import DELETE_FIELD
        user_ref.update({
            field_path: DELETE_FIELD
        })
        
        print(f"Data for {year}, {month} has been successfully deleted.")
    except Exception as e:
        print(f"An error occurred while deleting data: {e}")

def delete_data_for_year(user_id, year):
    """
    Deletes all data for a specific year from a user's document in Firestore.
    
    Args:
        user_id (str): The ID of the user.
        year (str): The year to delete (e.g., "2020").
    """
    try:
        # Reference the Firestore document for the user
        user_ref = db.collection("users").document(user_id)

        # Use Firestore's update method with DELETE_FIELD to remove the year data
        from google.cloud.firestore_v1 import DELETE_FIELD
        user_ref.update({
            year: DELETE_FIELD
        })
        
        print(f"Data for {year} has been successfully deleted for user {user_id}.")
    except Exception as e:
        print(f"An error occurred while deleting data: {e}")

def delete_all_user_data(user_id):
    """
    Deletes all data for a specific user from their Firestore document.
    
    Args:
        user_id (str): The ID of the user.
    """
    try:
        # Reference the Firestore document for the user
        user_ref = db.collection("users").document(user_id)

        # Delete the entire document
        user_ref.delete()
        
        print(f"All data for user {user_id} has been successfully deleted.")
    except Exception as e:
        print(f"An error occurred while deleting all data for user {user_id}: {e}")

def clear_data_main():

    utils.add_side_logo()

    # Check if the user is authenticated
    if not st.session_state.get('connected', False):
        st.warning("Please log in from the Home page to access this feature.")
        st.stop()

    st.title("Clear Data")

    # Display user details
    #st.image(st.session_state['user_info'].get('picture'), width=80)
    #st.write(f"**Hello, {st.session_state['user_info'].get('name')}!**")
    #st.write(f"Your email: **{st.session_state['user_info'].get('email')}**")
    st.write(f"**Logged in as : {st.session_state['user_info'].get('name')}** ({st.session_state['user_info'].get('email')})")
    user_id = st.session_state['oauth_id']

    # Fetch user data
    user_data = get_user_data(user_id)

    if user_data:
        #st.subheader("Clear Data Options")
        st.write("You can delete all your data or data for a specific year or month.")

        # Options to delete data
        clear_data_options = ["All Data", "Data for a Specific Year", "Data for a Specific Month"]
        clear_data_choice = st.radio("Select an option:", clear_data_options)

        if clear_data_choice == "All Data":
            st.warning("You are about to delete all your data. This action cannot be undone.")
            if st.button("Delete All Data"):
                try:
                    # Call function to delete all data for the user
                    delete_all_user_data(user_id)
                    st.success("All data has been successfully deleted.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

        elif clear_data_choice == "Data for a Specific Year":
            # Dropdown to select year
            available_years = sorted(user_data.keys())
            selected_year = st.selectbox("Select Year to Delete", available_years)

            if st.button(f"Delete Data for {selected_year}"):
                try:
                    # Call function to delete data for the specific year
                    delete_data_for_year(user_id, selected_year)
                    st.success(f"Data for {selected_year} has been successfully deleted.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

        elif clear_data_choice == "Data for a Specific Month":
            # Dropdowns to select year and month
            available_years = sorted(user_data.keys())
            selected_year = st.selectbox("Select Year", available_years)

            if selected_year:
                available_months = sorted(user_data[selected_year].keys(), key=lambda x: list(calendar.month_name).index(x))
                selected_month = st.selectbox("Select Month to Delete", available_months)

                if st.button(f"Delete Data for {selected_month} {selected_year}"):
                    try:
                        # Call function to delete data for the specific year and month
                        delete_data_for_year_month(user_id, selected_year, selected_month)
                        st.success(f"Data for {selected_month} {selected_year} has been successfully deleted.")
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
    else:
        st.error("No data found for your user ID.")

if __name__ == "__main__":
    clear_data_main()
