import datetime
from fastapi import APIRouter, Depends, Form, HTTPException
from typing import Optional
from api.dto import UserResponse
from sqlalchemy.orm import Session
from database import User, get_db
from middleware import get_current_user

router = APIRouter()

# Get all user
@router.get("/users")
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    users = db.query(User).offset(skip).limit(limit).all()

    if current_user != 'admin':
        raise HTTPException(status_code=403 , detail="Access denied")
    
    response = []
    for user in users:
        response.append(UserResponse(
            id = user.id,
            name = user.name,
            email = user.email,
            line_id = user.line_id,
            created_at = str(user.created_at),
            pinecone_index = user.pinecone_index,
            access_token = user.access_token,
            refresh_token = user.refresh_token
        ))
    return response

# Get user by id
@router.get("/users/{user_id}")
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()

    if user.name != current_user:
        raise HTTPException(status_code=403 , detail="Access denied")
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id = user.id,
        name = user.name,
        email = user.email,
        line_id = user.line_id,
        created_at = str(user.created_at),
        pinecone_index = user.pinecone_index,
        access_token = user.access_token,
        refresh_token = user.refresh_token
    )

# Create user
@router.post("/users/create")
async def create_user(
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    line_id: Optional[int] = Form(None),
    pinecone_index: Optional[str] = Form(None),
    access_token: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    user_db = db.query(User).filter(User.name == name or User.email == email).first()
    if user_db:
        raise HTTPException(status_code=409, detail="Email already exists")
    new_user = User(
        name = name,
        email = email,
        line_id = line_id,
        created_at = datetime.datetime.now(),
        pinecone_index = pinecone_index,
        access_token = access_token,
        refresh_token = refresh_token
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(
        id = new_user.id,
        name = new_user.name,
        email = new_user.email,
        line_id = new_user.line_id,
        created_at = str(new_user.created_at),
        pinecone_index = new_user.pinecone_index,
        access_token = new_user.access_token,
        refresh_token = new_user.refresh_token
    )

# Update user
@router.put("/users/update/{user_id}")
async def update_user(
    user_id: int,
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    line_id: Optional[int] = Form(None),
    pinecone_index: Optional[str] = Form(None),
    access_token: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()

    if user.name != current_user:
        raise HTTPException(status_code=403 , detail="Access denied")
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if name and name != user.name:
        user.name = name
    if email and email != user.email:
        user.email = email
    if line_id and line_id != user.line_id:
        user.line_id = line_id
    if pinecone_index and pinecone_index != user.pinecone_index:
        user.pinecone_index = pinecone_index
    if access_token and access_token != user.access_token:
        user.access_token = access_token
    if refresh_token and refresh_token != user.refresh_token:
        user.refresh_token = refresh_token
    
    db.merge(user)
    db.commit()
    db.refresh(user)

    return UserResponse(
        id = user.id,
        name = user.name,
        email = user.email,
        line_id = user.line_id,
        created_at = str(user.created_at),
        pinecone_index = user.pinecone_index,
        access_token = user.access_token,
        refresh_token = user.refresh_token
    )
    
# Delete user
@router.delete("/users/delete/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()

    if user.name != current_user:
        raise HTTPException(status_code=403 , detail="Access denied")
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()

    return {"result": "delete success"}