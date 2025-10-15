"""
Test file for Context7 integration - FastAPI async patterns
This file demonstrates patterns that Context7 should detect and provide guidance on
"""

from fastapi import FastAPI, Depends, HTTPException
from typing import List, Optional
import asyncio

app = FastAPI()

# ISSUE 1: Synchronous function in async framework
# Context7 should suggest using async def
@app.get("/users/{user_id}")
def get_user(user_id: int):
    """Fetch user by ID - synchronous (not optimal)"""
    return {"user_id": user_id, "name": "Test User"}


# ISSUE 2: Blocking I/O in endpoint
# Context7 should flag this and recommend async patterns
@app.get("/data")
def get_data():
    """Fetch data with blocking operation"""
    import time
    time.sleep(2)  # Blocking sleep
    return {"data": "result"}


# ISSUE 3: Missing async database operations
# Context7 should recommend async database drivers
@app.get("/items")
def get_items():
    """Fetch items from database"""
    # Simulated synchronous database call
    import sqlite3
    conn = sqlite3.connect("database.db")  # Sync connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    conn.close()
    return {"items": items}


# GOOD PATTERN: Proper async endpoint
# Context7 should recognize this as correct
@app.get("/async-users/{user_id}")
async def get_user_async(user_id: int):
    """Fetch user by ID - async (optimal)"""
    await asyncio.sleep(0.1)  # Simulated async I/O
    return {"user_id": user_id, "name": "Async User"}


# ISSUE 4: Missing dependency injection
# Context7 should suggest using FastAPI's Depends
@app.get("/admin/users")
def get_admin_users():
    """Admin endpoint without auth dependency"""
    # Missing authentication check
    return {"users": []}


# GOOD PATTERN: Dependency injection
# Context7 should recognize this as FastAPI best practice
async def get_current_user(token: str = Depends(lambda: "dummy")):
    """Dependency for user authentication"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"user": "authenticated"}


@app.get("/admin/users-secure")
async def get_admin_users_secure(current_user: dict = Depends(get_current_user)):
    """Admin endpoint with auth dependency"""
    return {"users": [], "admin": current_user}


# ISSUE 5: Missing response model
# Context7 should suggest using Pydantic models
@app.post("/users")
async def create_user(name: str, email: str):
    """Create user without response model"""
    return {"id": 1, "name": name, "email": email}


# GOOD PATTERN: Response model with Pydantic
# Context7 should recognize this as best practice
from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr


@app.post("/users-typed", response_model=UserResponse)
async def create_user_typed(name: str, email: EmailStr):
    """Create user with response model"""
    return UserResponse(id=1, name=name, email=email)
