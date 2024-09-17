from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import or_
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from ..db.models.user import User
from ..schemas.user import UserCreate, UserUpdate
from typing import Optional

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="v1/auth/token")
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINS = 60 * 24 * 30


async def existing_user(db: Session, username: str, email: str) -> Optional[User]:
    db_user = db.query(User).filter(or_(User.username == username, User.email == email)).first()
    return db_user


async def create_access_token(username: str, id: int):
    encode = {"sub": username, "id": id}
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINS)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(db: Session, token: str = Depends(oauth2_bearer)) -> Optional[User]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        id: int = payload.get("id")
        expire: datetime = payload.get("exp")
        if datetime(expire) < datetime.utcnow():
            return None
        if username is None or id is None:
            return None
        return db.query(User).filter(User.id == id).first()
    except JWTError:
        return None


async def get_user_from_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


async def create_user(db: Session, user: UserCreate) -> Optional[User]:
    db_user = User(
        email=user.email.lower().strip(),
        userName=user.username,
        hashed_password=bcrypt_context.hash(user.password),
        dob=user.dob or None,
        gender=user.gender or None,
        profile_pic=user.profile_pic or None,
        name=user.name or None
    )
    db.add(db_user)
    db.commit()
    return db_user


async def authenticate(db: Session, username: str, password: str) -> Optional[User]:
    db_user = await existing_user(db=db, username=username, email="")
    if not db_user:
        return None
    if not bcrypt_context.verify(password, db_user.hashed_password):
        return None
    return db_user


async def update_user(db: Session, db_user: User, user_update: UserUpdate):
    db_user.name = user_update.name or db_user.name
    db_user.dob = user_update.dob or db_user.dob
    db_user.gender = user_update.gender or db_user.gender
    db_user.profile_pic = user_update.profile_pic or db_user.profile_pic
    db.commit()
