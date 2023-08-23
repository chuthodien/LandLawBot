import os
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
from database import User, get_db, SessionLocal
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 120
CALL_TOKEN_EXPIRE_MINUTES = 10080

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_call_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=CALL_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})
        return payload
    except:
        return HTTPException(status_code=401, detail="Invalid token")

def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_access_token(token.credentials)
    user_name = payload.get("user_name")
    if user_name is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_name

def get_current_line_id(token: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_access_token(token.credentials)
    user_name = payload.get("line_id")
    if user_name is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_name

def get_current_line_token(token: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_access_token(token.credentials)
    line_access_token = payload.get("line_access_token")
    if line_access_token is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return line_access_token

async def authentication_middleware(
    request: Request,
    call_next
):
    if (
        request.url.path == "/v1/login" or
        request.url.path == "/api/line/authorize" or
        "/webhook" in request.url.path or
        "/webhook/verifyTokenToCall" in request.url.path or
        "/assets" in request.url.path
    ):
        response = await call_next(request)
        return response
    
    try:
        authorization = request.headers.get("Authorization")
        token = authorization.split("Bearer ")[1]

        db = SessionLocal()
        user = db.query(User).filter(User.access_token == token).first()
        db.close()

        payload = decode_access_token(token)
        exp = payload.get("exp")
        exp_time = datetime.utcfromtimestamp(exp)
        now = datetime.utcnow()

        if now >= exp_time:
            if "/v1/refreshToken" in request.url.path:
                response = await call_next(request)
                return response
            else:
                return JSONResponse(status_code=401, content={"detail": "Token expired"})
        if not user:
            return JSONResponse(status_code=403, content={"detail": "Invalid token"})
    except:
        return JSONResponse(status_code=404, content={"detail": "Authorication error"})
    response = await call_next(request)
    return response