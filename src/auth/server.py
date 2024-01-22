from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials, OAuth2PasswordBearer
from fastapi.responses import StreamingResponse
import asyncpg
from jose import jwt
import datetime
import pyotp
import qrcode
import io
import os

server = FastAPI()
security = HTTPBasic()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="")

DATABASE_URL = f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@{os.environ.get('POSTGRES_HOST')}:{os.environ.get('POSTGRES_PORT')}/{os.environ.get('POSTGRES_DB')}"

# DATABASE_URL = "postgresql://postgres:postgres@localhost/auth"
# TEMP_DATABASE_URL = os.environ.get("TEMP_DATABAE_URL") #temp_auth
JWT_SECRET = os.environ.get("JWT_SECRET")
# JWT_SECRET = "JWT_SECRET"
ALGORITHM = "HS256" 

async def get_db():
    conn = await asyncpg.create_pool(dsn=DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()

# async def get_temp_db():
#     temp_conn = await asyncpg.create_pool(dsn=TEMP_DATABASE_URL)
#     try:
#         yield temp_conn
#     finally:
#         await temp_conn.close()

def create_jwt(username: str, secret: str, admin: bool):
    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
        "iat": datetime.datetime.utcnow(),
        "admin": admin
    }
    return jwt.encode(payload, secret, algorithm=ALGORITHM)

##### Registration routes

@server.post("/register")
async def register(credentials: HTTPBasicCredentials, db=Depends(get_db)):
    username = credentials.username
    password = credentials.password 

    async with db.acquire() as connection:
        existing_user = await connection.fetchrow(
            "SELECT email FROM temp_users WHERE email = $1", username
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        totp_secret = pyotp.random_base32()

        # Store temporary data in temp_users table
        await connection.execute(
            "INSERT INTO temp_users (email, password, totp_secret) VALUES ($1, $2, $3)",
            username, password, totp_secret
        )

        # Generate QR code
        totp_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(username, issuer_name="YourAppName")
        qr_image = qrcode.make(totp_uri)
        qr_buffer = io.BytesIO()
        qr_image.save(qr_buffer)
        qr_buffer.seek(0)

    return StreamingResponse(qr_buffer, media_type="image/png")

@server.post("/validate-totp")
async def validate_totp(username: str, totp_code: str, db=Depends(get_db)):
    async with db.acquire() as connection:
        # Retrieve the temporarily stored TOTP secret
        temp_user = await connection.fetchrow(
            "SELECT * FROM temp_users WHERE email = $1", username
        )
        if not temp_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        totp_secret = temp_user['totp_secret']
        totp = pyotp.TOTP(totp_secret)
        if totp.verify(totp_code):
            await connection.execute(
                "INSERT INTO users (email, password) VALUES ($1, $2)",
                temp_user['email'], temp_user['password']
            )
            await connection.execute(
                "DELETE FROM temp_users WHERE email = $1", username
            )
            return {"message": "Registration successful"}
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid TOTP code")
        
##### Login routes

@server.post("/login")
async def login(credentials: HTTPBasicCredentials, db=Depends(get_db)):
    username = credentials.username
    password = credentials.password

    async with db.acquire() as connection:
        row = await connection.fetchrow(
            "SELECT email, password FROM users WHERE email = $1", username
        )
        if row and row['password'] == password:
            return create_jwt(username, JWT_SECRET, True)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        

@server.post("/validate")        
async def validate(token: str = Depends(oauth2_scheme)):
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except jwt.JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    return decoded["username"] + " has sucessfully logged in!"
        