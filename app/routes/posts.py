from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from ..db.session_handler import get_session
from ..schemas.post import PostCreate, Post
from ..services.post_service import create_post_svc, get_post_from_post_id_svc, get_user_posts_svc, get_random_post_svc, delete_post_svc
from ..services.auth_service import get_current_user as get_current_user_svc, existing_user


router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/", response_model=Post, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, token: str, db: Session = Depends(get_session)):
    user = await get_current_user_svc(db=db, token=token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized")
    db_post = await create_post_svc(db=db, post=post, user_id=user.id)
    return db_post


@router.get("/user", response_model=list[Post])
async def get_current_user(token: str, db: Session = Depends(get_session)):
    user = await get_current_user_svc(db=db, token=token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized")
    return await get_user_posts_svc(db=db,user_id=user.id)


@router.get("/user/{username}", response_model=list[Post])
async def get_user_posts(username: str, db: Session = Depends(get_session)):
    user = await existing_user(db=db, username=username, email="")
    return await get_user_posts_svc(db=db, user_id=user.id)


@router.get("/feed")
async def get_random_posts(page: int = 1, limit: int = 5, db: Session = Depends(get_session)):
    return await get_random_post_svc(db=db,page=page, limit=limit)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(token: str, post_id: int, db: Session = Depends(get_session)):
    user = await get_current_user_svc(db=db, token=token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to delete")
    post = await get_post_from_post_id_svc(db=db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to delete this "
                                                                             "post.")
    await delete_post_svc(db=db, post_id=post_id)
