import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def delete_data_for_year_month(user_id, year, month):
    """Deletes data for a specific year and month from a user's document in Firestore.
    
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
            field_path: DELETE_FIELD,
        })

        print(f"Data for {year}, {month} has been successfully deleted for user {user_id}.")
    except Exception as e:
        print(f"An error occurred while deleting data: {e}")

def delete_data_for_year(user_id, year):
    """Deletes all data for a specific year from a user's document in Firestore.
    
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
            year: DELETE_FIELD,
        })

        print(f"Data for {year} has been successfully deleted for user {user_id}.")
    except Exception as e:
        print(f"An error occurred while deleting data: {e}")

def delete_all_user_data(user_id):
    """Deletes all data for a specific user from their Firestore document.
    
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

# Example usage
# delete_data_for_year_month("123456789", "2020", "January")

# delete_data_for_year("123456789", "2023")

delete_all_user_data("123456")
