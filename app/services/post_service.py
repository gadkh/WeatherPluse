from typing import List, Optional
from sqlalchemy import desc
from sqlalchemy.orm import Session
from datetime import datetime

from ..schemas.post import PostCreate, Post as PostSchema
from ..db.models.post import Post
from ..db.models.user import User


async def create_post_svc(db: Session, post: PostCreate, user_id: int) -> Post:
    db_post = Post(
        content=post.content,
        image=post.image,
        location=post.location,
        author_id=user_id
    )
    db.add(db_post)
    db.commit()
    return db_post


async def get_user_posts_svc(db: Session, user_id: int) -> List[PostSchema]:
    posts = (db.query(Post)
             .filter(Post.author_id == user_id)
             .order_by(desc(Post.created_dt))
             .all())
    return posts


async def get_random_post_svc(db: Session, page: int = 1, limit: int = 0):
    total_post = db.query(Post).count()
    result = []
    offset = (page - 1) * limit
    if offset >= total_post:
        return result
    posts = db.query(Post, User.username).join(User).order_by(desc(Post.created_dt))
    posts = posts.offset(offset).limit(limit).all()
    for post, username in posts:
        post_dict = post.__dict__
        post_dict["username"] = username
        result.append(post_dict)

    return result


async def get_post_from_post_id_svc(db: Session, post_id: int) -> Optional[PostSchema]:
    print("hello")
    return db.query(Post).filter(Post.id == post_id).first()


async def delete_post_svc(db: Session, post_id: int):
    post = await get_post_from_post_id_svc(db, post_id)
    db.delete(post)
    db.commit()
