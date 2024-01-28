from fastapi import FastAPI, Depends, HTTPException, status, Request, File, UploadFile
import pika, gridfs, json, os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

from schema import UserRegistration, TOTPValidation

from tokenAuth import validate
from auth_svc import access
from storage import util
from reg import regAuth

server = FastAPI()
MONGO_URI = "mongodb://host.minikube.internal:27017/videos"
async_client = AsyncIOMotorClient(MONGO_URI)
async_db = async_client.get_default_database()

sync_client = MongoClient(MONGO_URI)
sync_db = sync_client.get_default_database()
fs = gridfs.GridFS(sync_db)

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()

@server.post("/register/")
async def register(user_registration: UserRegistration):
    username, qr_code_data, err = await regAuth.dbCheck(user_registration)
    if err:
        raise HTTPException(status_code=400, detail=err)

@server.post("/validate-totp/")
async def validate_totp(totp_validation: TOTPValidation):
    result = await regAuth.totpCheck(totp_validation)
    if 'detail' in result:
        raise HTTPException(status_code=400, detail=result['detail'])

@server.post("/login/")
async def login(request: Request):
    token, err = await access.login(request)
    if not err:
        return token
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="An error has occured")
    
@server.post("/upload")
async def upload(request: Request, file: UploadFile = File(...)):
    access, err = await validate.token(request)
    access = json.loads(access)

    if access["admin"]:
        if not file:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please submit a file")
        
        err = await util.upload(file, fs, channel, access)

        if err:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))
        
        return {"message": "success"}

    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
        
@server.get("/download")
async def download():
    pass

