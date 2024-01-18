from fastapi import FastAPI, Depends, HTTPException 
from schema.schema import UserSchema 
from sqlalchemy.orm import Session
from utils.password_hashing import get_password_hash, verify_password
from database.database import SessionLocal, engine
from model.model import Base, UserCreds

server = FastAPI()
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# register route
@server.post("/register/")
def register(user: UserSchema, db: Session = Depends(get_db)):
    fake_hashed_password = get_password_hash(user.password)
    db_user = UserCreds(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"Email": db_user.email, "message": "User created successfully."}

# login route
@server.post("/login/")
def login(user:UserSchema, db: Session = Depends(get_db)):
    db_user = db.query(UserCreds).filter(UserCreds.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect username")
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    return {"Email": db_user.email, "message": "Login successful"}
