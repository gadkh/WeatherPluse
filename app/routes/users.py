from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from ..schemas.user import UserUpdate, User as UserSchema
from ..db.session_handler import get_session
from ..services.auth_service import get_current_user
from ..services.user_service import update_user as update_user_svc

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/profile", status_code=status.HTTP_200_OK, response_model=UserSchema)
async def get_user(token: str, db: Session = Depends(get_session)):
    db_user = await get_current_user(db=db, token=token)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return db_user


@router.put("/{username}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(username: str, token: str, user_update: UserUpdate, db: Session = Depends(get_session)):
    db_user = await get_current_user(db=db, token=token)
    if db_user.username != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this user"
        )
    await update_user_svc(db=db, db_user=db_user, user_update=user_update)
