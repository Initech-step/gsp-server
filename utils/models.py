from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Any, Optional
from datetime import datetime


class UserRegister(BaseModel):
    phone_or_email: str
    password: str

class UserLogin(BaseModel):
    phone_or_email: str
    password: str

class ProgressData(BaseModel):
    user_identifier: str  # phone or email
    progress: Dict[str, Any]  # The entire progress object
    current_level: str
    current_week: int
    current_audio: Optional[str] = None
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class NoteData(BaseModel):
    user_identifier: str
    audio_id: str
    note_text: str
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class NotesBackup(BaseModel):
    user_identifier: str
    notes: Dict[str, Any]  # All notes
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class UserProfile(BaseModel):
    user_identifier: str
    name: Optional[str] = None
    preferences: Dict[str, Any] = {}
    created_at: str
    last_login: Optional[str] = None

class PasswordChange(BaseModel):
    user_identifier: str
    old_password: str
    new_password: str

class PasswordReset(BaseModel):
    phone_or_email: str
    # In production, you'd need a reset token mechanism

class DeleteAccount(BaseModel):
    user_identifier: str
    password: str
