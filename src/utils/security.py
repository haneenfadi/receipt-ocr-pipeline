from datetime import datetime, timedelta
import sqlite3
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.config.settings import settings


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# for FastAPI to know where to get the token from when using Depends(get_current_user) in protected routes. This should match the login route prefix.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_conn():
    conn = sqlite3.connect(settings.DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_token(user_id: int, email: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "email": email, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def check_user_has_data(user_id: int) -> int:
    """Returns number of receipts the user has."""
    conn = get_conn()
    row = conn.execute(
        "SELECT COUNT(*) AS cnt FROM receipts WHERE user_id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return row["cnt"] if row else 0


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Decode JWT and return {"user_id": int, "email": str}.
    Raise 401 if invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = int(payload.get("sub"))
        email: str = payload.get("email")
        if user_id is None:
            raise credentials_exception
        return {"user_id": user_id, "email": email}
    except JWTError:
        raise credentials_exception
