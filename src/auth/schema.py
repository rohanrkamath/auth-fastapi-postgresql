from pydantic import BaseModel

class UserRegistration(BaseModel):
    username: str
    password: str

class TOTPValidation(BaseModel):
    username: str
    totp_code: str
