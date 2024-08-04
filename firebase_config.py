import firebase_admin
from firebase_admin import credentials, auth, firestore

cred = credentials.Certificate("./repurpose-ai-firebase-adminsdk-kf6c0-cd0dd6cdfd.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
