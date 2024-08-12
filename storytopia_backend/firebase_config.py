import firebase_admin
from firebase_admin import credentials, firestore
import json

# Load credentials from JSON file
with open("/Users/gregoryguyon/Documents/GitHub/storytopia-backend/storytopia_backend/repurpose-ai-firebase-adminsdk-kf6c0-cd0dd6cdfd.json", 'r') as file:
    cred_dict = json.load(file)

# Initialize credentials
cred = credentials.Certificate(cred_dict)

# Initialize Firebase Admin using the credentials
firebase_admin.initialize_app(cred)

# Get the Firestore client
db = firestore.client()
