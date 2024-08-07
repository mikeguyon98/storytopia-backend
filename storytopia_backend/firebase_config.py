import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

cred_json = os.getenv("FIREBASE_CREDENTIALS")
if cred_json:
    cred = credentials.Certificate("./storytopia_backend/repurpose-ai-firebase-adminsdk-kf6c0-cd0dd6cdfd.json")
    firebase_admin.initialize_app(cred)
else:
    raise ValueError("FIREBASE_CREDENTIALS environment variable not set")

db = firestore.client()
