from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.core import verify_token

# OAuth2PasswordBearer tells FastAPI:
# "Look for a Bearer token in the Authorization header"
# tokenUrl="/auth/login" tells Swagger where to get a token
# This makes the "Authorize" button appear in Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency that:
    1. Reads Bearer token from Authorization header
    2. Verifies the token
    3. Finds the user in DB
    4. Returns the user object

    Use this in any route that requires login.
    """
    # Verify token and get payload
    payload = verify_token(token)

    # Get user_id from payload
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    # Find user in DB
    user = db.query(User).filter(
        User.id == int(user_id)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account deactivated"
        )

    return user


def get_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency that requires admin role.
    Builds on get_current_user — dependency chain!

    If user is not admin → 403 Forbidden
    If user is admin → returns user
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user