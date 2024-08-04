import os
import json
import firebase_admin
from firebase_admin import credentials

cred_json = os.getenv("FIREBASE_CREDENTIALS")
if cred_json:
    cred_dict = json.loads(cred_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
else:
    raise ValueError("FIREBASE_CREDENTIALS environment variable not set")

# Now you can use Firebase services
from firebase_admin import firestore

db = firestore.client()
