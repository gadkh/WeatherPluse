from sqlalchemy.orm import Session
from sqlalchemy import or_
from passlib.context import CryptContext
from ..db.models.user import User
from ..schemas.user import UserCreate, UserUpdate
from typing import Optional

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def existing_user(db: Session, username: str, email: str) -> Optional[User]:
    db_user = db.query(User).filter(or_(User.username == username, User.email == email)).first()
    return db_user


async def get_user_from_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


async def create_user(db: Session, user: UserCreate) -> Optional[User]:
    db_user = User(
        email=user.email.lower().strip(),
        username=user.username,
        hashed_password=bcrypt_context.hash(user.password),
        dob=user.dob or None,
        gender=user.gender or None,
        profile_pic=user.profile_pic or None,
        name=user.name or None
    )
    db.add(db_user)
    db.commit()
    return db_user


async def update_user(db: Session, db_user: User, user_update: UserUpdate):
    db_user.name = user_update.name or db_user.name
    db_user.dob = user_update.dob or db_user.dob
    db_user.gender = user_update.gender or db_user.gender
    db_user.profile_pic = user_update.profile_pic or db_user.profile_pic
    db.commit()
