from app.db.db_handler import Base, engine
from fastapi import FastAPI

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Weather app",
    debug=True,
    description="Engine Behind Weather Social app",
    version="0.1"
)

# if __name__ == '__main__':
#     print("Hello world")