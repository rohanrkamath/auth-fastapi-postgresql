from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from util import crud, password
from schema import schema 
from database import database
router = APIRouter()

# * register
@router.post("/register/")
async def register(user: schema.UserSchema, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        return HTTPException(status_code=400, detail="User already exists. Please login.")
    
    db_user = crud.create_user(db=db, email=user.email, password=user.password)
    return {"email": db_user.email, "message": "User register!"}

# * login
@router.post("/login/")
async def login(user: schema.UserSchema, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if not db_user or not password.verify_password(user.password, db_user.password):
        return HTTPException(status_code=400, detail="Incorrect email/password")

    return {"message": "Welcome" + db_user.email}
                   
# delete

# update

