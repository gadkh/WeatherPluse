from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm.session import Session
from ..db.db_handler import get_db
from ..schemas.user import UserCreate
from ..services.auth_service import create_access_token, authenticate
from ..services.user_service import existing_user, create_user as create_user_svc

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = await existing_user(db=db, username=user.username, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Username or Email already exist")
    db_user = await create_user_svc(db, user)
    access_token = await create_access_token(username=user.username, id=db_user.id)
    return {"access_token": access_token, "type": "bearer", "username": user.username}


@router.post("/token", status_code=status.HTTP_201_CREATED)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = await authenticate(db=db, username=form_data.username, password=form_data.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token = await create_access_token(username=db_user.username, id=db_user.id)
    return {"access_token": access_token, "type": "bearer"}
