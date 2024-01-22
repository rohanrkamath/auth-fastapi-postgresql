from jose import jwt
from datetime import datetime, timedelta

# todo: put default timedelta, jwt secret, algorithm in a separate config file.

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        "secret_key",
        algorithm="HS256"
    )

    return encoded_jwt