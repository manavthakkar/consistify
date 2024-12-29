import firebase_admin
from firebase_admin import credentials, firestore

# Check if the app is already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase.json")
    firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

# Retrieve user data from Firestore
def get_user_data(user_id):
    doc = db.collection("users").document(user_id).get()
    if doc.exists:
        return doc.to_dict()
    return None

user_id = "123456789" # will be obtained from Google Authentication

# retrieve all data from the user_id
user_data = get_user_data(user_id)

print(user_data)









