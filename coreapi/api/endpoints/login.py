from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Form, HTTPException, Security, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
import jwt
from sqlalchemy.orm import Session
from middleware import create_access_token, decode_access_token, get_current_user, get_current_line_token
from dotenv import load_dotenv
from database import User, get_db
import os
import requests

from middleware.authentication import create_refresh_token, get_current_line_id

load_dotenv()

security = HTTPBearer()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
CLIENT_ID = os.getenv('LINE_CHANNEL_ACCESS_TOKEN_LOGIN')
CLIENT_SECRET = os.getenv('LINE_CHANNEL_SECRET_LOGIN')
REDIRECT_URI = os.getenv('LOGIN_REDIRECT_URI')

router = APIRouter()

@router.get('/api/line/authorize')
def line_login():
    # Go to line login home page
    authorization_url = f"https://access.line.me/oauth2/v2.1/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&state=state&scope=openid%20profile"
    return JSONResponse(content={"url": authorization_url})

@router.post('/v1/login')
def line_callback(
    code: str,
    db: Session = Depends(get_db)
):
    # Login with line
    access_token_url = "https://api.line.me/oauth2/v2.1/token"
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI
    }
    response = requests.post(access_token_url, data=payload)
    line_access_token = response.json().get('access_token')

    # Get user_line info
    profile_url = "https://api.line.me/v2/profile"
    headers = {'Authorization': f'Bearer {line_access_token}'}
    response = requests.get(profile_url, headers=headers)
    profile_data = response.json()
    
    # Processing user_line info
    line_id = profile_data.get('userId')
    user_name = profile_data.get('displayName')
    
    # Update access token in data base
    user = db.query(User).filter(User.line_id == line_id).first()

    id = None
    if not user:
        # Create access token
        access_token = create_access_token({"user_name": user_name, "line_id": line_id})
        refresh_token = create_refresh_token({"user_name": user_name, "line_id": line_id})

        newUser = User(
            name = user_name,
            line_id = line_id,
            created_at = datetime.now(),
            pinecone_index = "pinecone_index",
            access_token = access_token,
            refresh_token = refresh_token,
        )
        db.add(newUser)
        db.commit()
        db.refresh(newUser)
        id = newUser.id
    else:
        # Create access token
        access_token = create_access_token({"user_name": user.name, "line_id": line_id})
        refresh_token = create_refresh_token({"user_name": user.name, "line_id": line_id})

        user.access_token = access_token
        user.refresh_token = refresh_token
        db.merge(user)
        db.commit()
        db.refresh(user)
        user_name = user.name
        id = user.id

    result = {
        "line_id": line_id,
        "name": user_name,
        "id": id,
        "expires_in": 30,
        "access_token": access_token,
        "refresh_token": refresh_token
    }

    return JSONResponse(result)

@router.post('/v1/logout')
def log_out(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_line_id),
):
    user = db.query(User).filter(User.line_id == current_user).first()
    
    user.access_token = None
    user.refresh_token = None
    db.merge(user)
    db.commit()
    db.refresh(user)

    return {"detail": f"Log out account {user.name} success"}

@router.get('/v1/refreshToken/{refresh_token}')
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    payload = decode_access_token(refresh_token)
    line_id = payload.get("line_id")
    user = db.query(User).filter(User.line_id == line_id).first()
    if not user:
        return HTTPException(status_code=404, detail="User not found")  

    access_token = create_access_token({"user_name": user.name, "line_id": user.line_id})
    if access_token:
        user.access_token = access_token

    exp = payload.get("exp")
    exp_time = datetime.utcfromtimestamp(exp)
    now = datetime.utcnow()

    # refresh_token expired
    if now >= exp_time:
        refresh_token = create_refresh_token({"user_name": user.name, "line_id": user.line_id})
        if refresh_token:
            user.refresh_token = refresh_token
    
    db.merge(user)
    db.commit()
    db.refresh(user)
    return user