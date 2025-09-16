import jwt
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

def decode_jwt_from_header(authorization: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Decodes a JWT from an Authorization header to extract user name and email.

    Args:
        authorization: The content of the Authorization header (e.g., "Bearer <token>").

    Returns:
        A tuple containing (name, email). Returns (None, None) if the token
        cannot be decoded or the claims are not present.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None, None

    token = authorization.split(" ")[1]
    try:
        # Decode the JWT without verification, as Kong is trusted to have already verified it.
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        
        user_email = decoded_token.get("email")
        user_name = decoded_token.get("name")
        
        logger.info("JWT decoded successfully.")
        return user_name, user_email

    except jwt.PyJWTError as e:
        logger.error(f"Error decoding JWT: {e}")
        return None, None
