from fastapi import FastAPI, HTTPException
from routers import users
from database.database import engine
from models import models

models.Base.metadata.create_all(bind=engine)

server = FastAPI()

server.include_router(users.router)