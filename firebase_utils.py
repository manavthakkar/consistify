import firebase_admin
import streamlit as st
from firebase_admin import credentials, firestore


def initialize_firestore():
    if not firebase_admin._apps:
        cred = credentials.Certificate(dict(st.secrets["firebase"]))
        firebase_admin.initialize_app(cred)
    return firestore.client()

def delete_data_for_year_month(db, user_email, year, month):
    """Deletes data for a specific year and month from a user's document in Firestore.
    
    Args:
        user_email (str): The email of the user.
        year (str): The year to delete (e.g., "2020").
        month (str): The month to delete (e.g., "January").

    """
    try:
        # Reference the Firestore document for the user
        user_ref = db.collection("users").document(user_email)

        # Build the path to the specific year and month
        field_path = f"{year}.{month}"

        # Use Firestore's update method with DELETE_FIELD to remove the data
        from google.cloud.firestore_v1 import DELETE_FIELD
        user_ref.update({
            field_path: DELETE_FIELD,
        })

        print(f"Data for {year}, {month} has been successfully deleted.")
    except Exception as e:
        print(f"An error occurred while deleting data: {e}")


def get_user_data(db, user_email, year, month_name):
    """Retrieve user data for a specific year and month from Firestore.
    """
    doc = db.collection("users").document(user_email).get()
    if doc.exists:
        user_data = doc.to_dict()
        if str(year) in user_data and month_name in user_data[str(year)]:
            return user_data[str(year)][month_name]
    return None


def store_user_data(db, user_email, user_data):
    """Store user data in Firestore.
    """
    db.collection("users").document(user_email).set(user_data, merge=True)


def get_all_user_data(db, user_email: str)->dict:
    """Fetches the user's data from Firestore.
    
    Args:
        user_email (str): The user email.
    
    Returns:
        dict: The user's data or None if not found.

    """
    doc = db.collection("users").document(user_email).get()
    return doc.to_dict() if doc.exists else None

def delete_data_for_year(db, user_email: str, year: str)->None:
    """Deletes all data for a specific year from a user's document in Firestore.
    
    Args:
        user_email (str): The ID of the user.
        year (str): The year to delete (e.g., "2020").

    """
    try:
        # Reference the Firestore document for the user
        user_ref = db.collection("users").document(user_email)

        # Use Firestore's update method with DELETE_FIELD to remove the year data
        from google.cloud.firestore_v1 import DELETE_FIELD
        user_ref.update({
            year: DELETE_FIELD,
        })

        print(f"Data for {year} has been successfully deleted for user {user_email}.")
    except Exception as e:
        print(f"An error occurred while deleting data: {e}")


def delete_all_user_data(db, user_email: str)->None:
    """Deletes all data for a specific user from their Firestore document.
    
    Args:
        user_email (str): The email of the user.

    """
    try:
        # Reference the Firestore document for the user
        user_ref = db.collection("users").document(user_email)

        # Delete the entire document
        user_ref.delete()

        print(f"All data for user {user_email} has been successfully deleted.")
    except Exception as e:
        print(f"An error occurred while deleting all data for user {user_email}: {e}")