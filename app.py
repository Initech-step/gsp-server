import os
from fastapi import (
    FastAPI,
    HTTPException,
    status,
    Depends
)
from fastapi.middleware.cors import CORSMiddleware
# from bson.objectid import ObjectId
# from typing import List, Optional
from datetime import datetime
from utils.database import connect_to_db
from utils.models import (
    UserRegister,
    UserLogin,
    NotesBackup,
    ProgressData,
    PasswordChange,
    DeleteAccount
)
from utils.util import (
    get_password_hash,
    create_access_token,
    verify_password,
    get_current_user
)

# initialize app
app = FastAPI()

"""SET UP CORS"""
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_headers=["*"],
    allow_methods=["*"],
)

database = connect_to_db()

# root
@app.get("/")
def root():
    return {
        "message": "Hello Godslighthouse Starter Kit Server",
        "version": "1.0.0",
        "date": "28-1-26"
    }


"""
User Auth APIS
"""


@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserRegister):
    """Register a new user with phone/email and password"""
    users_collection = database["users_collection"]
    
    # Check if user already exists
    existing_user = users_collection.find_one({"phone_or_email": user.phone_or_email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this phone/email already exists"
        )
    
    # Hash password and save user
    hashed_password = get_password_hash(user.password)
    user_data = {
        "phone_or_email": user.phone_or_email,
        "hashed_password": hashed_password,
        "created_at": datetime.now().isoformat(),
    }
    
    try:
        result = users_collection.insert_one(user_data)
        # Create access token
        access_token = create_access_token(data={"sub": user.phone_or_email})
        
        return {
            "status": True,
            "message": "User registered successfully",
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )

@app.post("/api/auth/login")
def login_user(user: UserLogin):
    """Login user and return access token"""
    users_collection = database["users_collection"]
    
    # Find user
    db_user = users_collection.find_one({"phone_or_email": user.phone_or_email})
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone/email or password"
        )
    
    # Verify password
    if not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone/email or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.phone_or_email})
    
    return {
        "status": True,
        "access_token": access_token,
        "token_type": "bearer",
        "user_identifier": user.phone_or_email
    }

"""
User Progress APIS
"""

@app.post("/api/progress/upload", status_code=status.HTTP_200_OK)
def upload_progress(progress_data: ProgressData):
    """Upload user's local progress to cloud"""
    progress_collection = database["progress_collection"]
    
    try:
        # Upsert (update if exists, insert if not)
        progress_collection.update_one(
            {"user_identifier": progress_data.user_identifier},
            {
                "$set": {
                    "progress": progress_data.progress,
                    "current_level": progress_data.current_level,
                    "current_week": progress_data.current_week,
                    "current_audio": progress_data.current_audio,
                    "updated_at": progress_data.updated_at
                }
            },
            upsert=True
        )
        
        return {
            "status": True,
            "message": "Progress uploaded successfully"
        }
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload progress"
        )

@app.get("/api/progress/download/{user_identifier}")
def download_progress(user_identifier: str):
    """Download user's progress from cloud"""
    progress_collection = database["progress_collection"]
    
    try:
        progress_data = progress_collection.find_one(
            {"user_identifier": user_identifier},
            {"_id": 0}  # Exclude MongoDB ID
        )
        
        if not progress_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No progress found for this user"
            )
        
        return {
            "status": True,
            "data": progress_data
        }
    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download progress"
        )


"""
Notes Backup APIS
"""

@app.post("/api/notes/backup", status_code=status.HTTP_200_OK)
def backup_notes(notes_data: NotesBackup):
    """Backup all user notes to cloud"""
    notes_collection = database["notes_collection"]
    
    try:
        # Upsert notes
        notes_collection.update_one(
            {"user_identifier": notes_data.user_identifier},
            {
                "$set": {
                    "notes": notes_data.notes,
                    "updated_at": notes_data.updated_at
                }
            },
            upsert=True
        )
        
        return {
            "status": True,
            "message": "Notes backed up successfully"
        }
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to backup notes"
        )

@app.get("/api/notes/retrieve/{user_identifier}")
def retrieve_notes(user_identifier: str):
    """Retrieve user's notes from cloud"""
    notes_collection = database["notes_collection"]
    
    try:
        notes_data = notes_collection.find_one(
            {"user_identifier": user_identifier},
            {"_id": 0}  # Exclude MongoDB ID
        )
        
        if not notes_data:
            return {
                "status": True,
                "data": {
                    "notes": {},
                    "message": "No notes found"
                }
            }
        
        return {
            "status": True,
            "data": notes_data
        }
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve notes"
        )


@app.get("/api/auth/verify")
def verify_token(current_user: str = Depends(get_current_user)):
    """Verify if a token is valid"""
    return {
        "status": True,
        "valid": True,
        "user_identifier": current_user
    }


@app.post("/api/auth/refresh")
def refresh_token(current_user: str = Depends(get_current_user)):
    """Refresh access token"""
    new_token = create_access_token(data={"sub": current_user})
    return {
        "status": True,
        "access_token": new_token,
        "token_type": "bearer"
    }


@app.post("/api/auth/change-password")
def change_password(password_data: PasswordChange):
    """Change user password"""
    users_collection = database["users_collection"]
    
    # Find user
    user = users_collection.find_one({"phone_or_email": password_data.user_identifier})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify old password
    if not verify_password(password_data.old_password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect old password"
        )
    
    # Update password
    new_hashed_password = get_password_hash(password_data.new_password)
    users_collection.update_one(
        {"phone_or_email": password_data.user_identifier},
        {"$set": {"hashed_password": new_hashed_password}}
    )
    
    return {
        "status": True,
        "message": "Password changed successfully"
    }


@app.delete("/api/auth/delete-account")
def delete_account(delete_data: DeleteAccount):
    """Delete user account and all associated data"""
    users_collection = database["users_collection"]
    progress_collection = database["progress_collection"]
    notes_collection = database["notes_collection"]
    
    # Find and verify user
    user = users_collection.find_one({"phone_or_email": delete_data.user_identifier})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify password
    if not verify_password(delete_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    
    # Delete all user data
    users_collection.delete_one({"phone_or_email": delete_data.user_identifier})
    progress_collection.delete_one({"user_identifier": delete_data.user_identifier})
    notes_collection.delete_one({"user_identifier": delete_data.user_identifier})
    
    return {
        "status": True,
        "message": "Account and all data deleted successfully"
    }


@app.get("/api/user/profile/{user_identifier}")
def get_user_profile(user_identifier: str):
    """Get user profile information"""
    users_collection = database["users_collection"]
    
    user = users_collection.find_one(
        {"phone_or_email": user_identifier},
        {"_id": 0, "hashed_password": 0}  # Exclude sensitive data
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "status": True,
        "data": user
    }


@app.delete("/api/notes/delete/{user_identifier}/{audio_id}")
def delete_specific_note(user_identifier: str, audio_id: str):
    """Delete a specific note"""
    notes_collection = database["notes_collection"]
    
    result = notes_collection.update_one(
        {"user_identifier": user_identifier},
        {"$unset": {f"notes.{audio_id}": ""}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User notes not found"
        )
    
    return {
        "status": True,
        "message": "Note deleted successfully"
    }


@app.delete("/api/progress/reset/{user_identifier}")
def reset_progress(user_identifier: str):
    """Reset user progress"""
    progress_collection = database["progress_collection"]
    
    result = progress_collection.delete_one({"user_identifier": user_identifier})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No progress found to reset"
        )
    
    return {
        "status": True,
        "message": "Progress reset successfully"
    }


@app.get("/api/stats/{user_identifier}")
def get_user_stats(user_identifier: str):
    """Get user statistics (progress and notes count)"""
    progress_collection = database["progress_collection"]
    notes_collection = database["notes_collection"]
    
    progress_data = progress_collection.find_one({"user_identifier": user_identifier})
    notes_data = notes_collection.find_one({"user_identifier": user_identifier})
    
    stats = {
        "user_identifier": user_identifier,
        "has_progress": progress_data is not None,
        "current_level": progress_data.get("current_level") if progress_data else None,
        "current_week": progress_data.get("current_week") if progress_data else None,
        "notes_count": len(notes_data.get("notes", {})) if notes_data else 0,
        "last_updated": progress_data.get("updated_at") if progress_data else None
    }
    
    return {
        "status": True,
        "data": stats
    }
