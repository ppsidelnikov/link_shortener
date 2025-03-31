from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from core.security import decode_token
from crud import crud_user
from sqlalchemy.orm import Session
from db.session import get_db
from typing import Optional
from schemas.user import UserInDB

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

async def get_current_user(
        token: str = Depends(oauth2_scheme), 
        db: Session = Depends(get_db)
        ):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
        
    )
    if not token:
        return None
    
    payload = decode_token(token)
    if not payload:
        return None
        
    email = payload.get("sub")
    if not email:
        return None
    
    user = crud_user.get_user_by_email(db, email)
    if not user:
        return None
        
    return user
