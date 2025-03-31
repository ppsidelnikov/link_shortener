from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.user import Token, UserCreate, UserInDB
from crud import crud_user
from core.security import create_access_token, verify_password, get_password_hash

router = APIRouter(tags=["auth"])

@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Регистрация нового пользователя.
    Проверяет уникальность email и хеширует пароль.
    """

    existing_user = crud_user.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    new_user = crud_user.create_user(
        db=db,
        user_data=user_data
    )
    
    return new_user

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Залогин пользователя, выдает ему токен по имейлу и паролю
    """
    user = crud_user.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
