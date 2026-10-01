from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.user_repo import user_repo
from app.schemas.user import UserRegister, UserLogin, TokenResponse, UserResponse
from app.core import hash_password, verify_password, create_access_token


class AuthService:
    """
    All authentication business logic lives here.
    Router just calls these methods.
    """

    def register(self, db: Session, user_data: UserRegister) -> object:
        # Check username taken
        if user_repo.get_by_username(db, user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

        # Check email taken
        if user_repo.get_by_email(db, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Hash password and create user
        hashed = hash_password(user_data.password)
        return user_repo.create(db, user_data.username, user_data.email, hashed)

    def login(self, db: Session, user_data: UserLogin) -> TokenResponse:
        # Find user
        user = user_repo.get_by_username(db, user_data.username)

        # Vague error — security best practice
        if not user or not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account deactivated"
            )

        # Create token
        token = create_access_token(data={
            "sub": str(user.id),
            "username": user.username,
            "is_admin": user.is_admin
        })

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )


auth_service = AuthService()