"""
Module for authentication utilities.
"""
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth
from storytopia_backend.firebase_config import db

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Get the current user based on the provided credentials.

    Args:
        credentials (HTTPAuthorizationCredentials): The HTTP authorization credentials.

    Returns:
        dict: The user information.

    Raises:
        HTTPException: If the token is invalid or the user is not found.
    """
    try:
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token['uid']
        user_ref = db.collection('users').document(user_id)
        user = user_ref.get()
        if user.exists:
            return user.to_dict()
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token {exc}") from exc
