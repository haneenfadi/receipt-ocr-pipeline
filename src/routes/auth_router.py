from fastapi import APIRouter, Depends, HTTPException, status
from src.utils.schema import RegisterRequest, TokenResponse
from src.utils.security import ( get_conn, hash_password, verify_password,create_token, check_user_has_data)
from fastapi.security import OAuth2PasswordRequestForm
from src.utils.security import get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", status_code=201)
def register(body: RegisterRequest):
    conn = get_conn()
    existing = conn.execute(
        "SELECT id FROM users WHERE email = ?", (body.email,)
    ).fetchone()

    if existing:
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(body.password)
    conn.execute(
        "INSERT INTO users (email, password_hash) VALUES (?, ?)",
        (body.email, hashed),
    )
    conn.commit()
    conn.close()
    return {"message": "User registered successfully",
            }


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends()):
    """
    Login with email + password.
    Returns JWT token + whether the user already has receipt data.
    """
    conn = get_conn()
    user = conn.execute(
        "SELECT id, password_hash FROM users WHERE email = ?", (form.username,)
    ).fetchone()
    conn.close()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This account does not exist. Please create an account first.",
        )

    if not verify_password(form.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    user_id = user["id"]
    receipt_count = check_user_has_data(user_id)
    token = create_token(user_id, form.username)

    return TokenResponse(
        access_token=token,
        has_data=receipt_count > 0,
        receipt_count=receipt_count,
    )


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    """
    Returns current user info + live data status.
    Useful to re-check after uploading first receipt.
    """
    user_id = current_user["user_id"]
    receipt_count = check_user_has_data(user_id)
    return {
        "user_id": user_id,
        "email": current_user["email"],
        "has_data": receipt_count > 0,
        "receipt_count": receipt_count,
    }
