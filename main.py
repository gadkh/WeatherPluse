from app.db.session_handler import Base, engine
from fastapi import FastAPI
from app.routes.api import router

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Weather app",
    debug=True,
    description="Engine Behind Weather Social app",
    version="0.1"
)

app.include_router(router)