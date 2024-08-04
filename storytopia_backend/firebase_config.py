"""
This module initializes the Firebase application and sets up the Firestore client.

It imports the necessary Firebase Admin SDK modules, loads the credentials from a JSON file,
initializes the Firebase app, and creates a Firestore client instance.

Modules:
	firebase_admin: The Firebase Admin SDK.
	credentials: Used to authenticate the Firebase app.
	firestore: Firestore client for database operations.
"""
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("./repurpose-ai-firebase-adminsdk-kf6c0-cd0dd6cdfd.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
