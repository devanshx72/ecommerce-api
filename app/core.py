from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status

# ── Password Hashing ──
# CryptContext handles password hashing
# bcrypt is the algorithm — industry standard
# deprecated="auto" means old hashes auto-upgrade
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── JWT Settings ──
# SECRET_KEY signs the token — keep this secret in production
# In production: use environment variable, never hardcode
# ALGORITHM: HS256 = HMAC with SHA-256
# ACCESS_TOKEN_EXPIRE_MINUTES: token valid for 30 minutes
SECRET_KEY = "your-super-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def hash_password(password: str) -> str:
    """
    Convert plain password to hashed version.
    Example:
    "mypassword123" → "$2b$12$EixZaYVK1fsbw1Zfbx..."
    One-way hash — cannot be reversed
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check if plain password matches the hash.
    Returns True if match, False if not.
    Never compare plain passwords directly!
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """
    Create a JWT token.

    JWT has 3 parts separated by dots:
    header.payload.signature

    header:    algorithm used
    payload:   your data (user_id, username, expiry)
    signature: proves token wasn't tampered with

    Example token:
    eyJhbGc...  .eyJzdWI...  .SflKxwR...
    (header)     (payload)    (signature)
    """
    to_encode = data.copy()

    # Add expiry time to payload
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    # jwt.encode creates the token string
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT token.
    Raises HTTPException if:
    - Token is invalid
    - Token has expired
    - Token was tampered with
    """
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )