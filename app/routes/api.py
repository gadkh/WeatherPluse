from fastapi import APIRouter
from .users import router as user_router
from .auth import router as auth_router

router = APIRouter(prefix="/v1")

router.include_router(user_router)
router.include_router(auth_router)
