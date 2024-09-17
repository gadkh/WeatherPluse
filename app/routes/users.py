from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime
from ..schemas.user import UserCreate, UserUpdate, User as UserSchema
from ..db.db_handler import get_db
from ..services.user_service import (existing_user, create_access_token, get_user_from_id, get_current_user,
                                     create_user as create_user_svc, authenticate, update_user as update_user_svc)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = await existing_user(db=db, username=user.username, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Username or Email already exist")
    db_user = create_user_svc(db, user)
    access_token = await create_access_token(username=user.username, id=db_user.id)
    return {"access_token": access_token, "type": "bearer", "username": user.username}


@router.post("/toke", status_code=status.HTTP_201_CREATED)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = await authenticate(db=db, username=form_data.username, password=form_data.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token = await create_access_token(username=db_user.username, id=db_user.id)
    return {"access_token": access_token, "type": "bearer"}


@router.get("/profile", status_code=status.HTTP_200_OK, response_model=UserSchema)
async def get_user(token: str, db: Session = Depends(get_db)):
    db_user = await get_current_user(db=db, token=token)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return db_user


@router.put("/{username}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(username: str, token: str, user_update: UserUpdate, db: Session = Depends(get_db)):
    db_user = await get_current_user(db=db, token=token)
    if db_user.username != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this user"
        )
    await update_user_svc(db=db, db_user=db_user, user_update=user_update)
