from fastapi import  APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import SessionLocal
import database_models
from models import UserCreate
from security import get_password_hash, verify_password, create_access_token

from database import get_db

router = APIRouter(tags=["Authentication"])

@router.post("/register")
def user_register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(database_models.User).filter(database_models.User.username == user.username).first()
    
    if existing_user:
        raise HTTPException(400, "User already exists")

    hashed_pw = get_password_hash(user.password)
    new_user = database_models.User(
        username=user.username,
        password_hash=hashed_pw
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "username": new_user.username,
        "created_at": new_user.created_at
    }

@router.post("/token")
def auth_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    found_user = db.query(database_models.User).filter(database_models.User.username == form_data.username).first()
    if not found_user or not verify_password(form_data.password, found_user.password_hash):
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"}
            )
    access_token = create_access_token(data={"sub": found_user.username, "user_id": found_user.id})
    return {"access_token": access_token, "token_type": "bearer"}