from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from uuid import UUID
from typing import List, Optional


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @field_validator("password")
    def password_strength(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        return v


class UserUpdate(UserBase):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    blocked_at: Optional[datetime] = None


class UserResponse(UserBase):
    id: UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    blocked_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProfileBase(UserBase):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    phone: Optional[str] = None


class ProfileCreate(ProfileBase, UserCreate):
    pass


class ProfileUpdate(ProfileBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    phone: Optional[str] = None


class ProfileResponse(ProfileBase):
    id: UUID
    user_id: UUID

    class Config:
        from_attributes = True


class BannedRefreshTokenResponse(BaseModel):
    id: UUID
    jti: str

    class Config:
        from_attributes = True


class Token(BaseModel):  # for service
    access_token: str
    refresh_token: str
    token_type: str
    access_token_expires: datetime
    refresh_token_expires: datetime
    scopes: List[str] = Field(default_factory=list)


class TokenResponse(BaseModel):  # new
    access_token: str | None = None
    token_type: str
    refresh_token: str | None = None
    scopes: List[str]
    access_token_expires: datetime
    refresh_token_expires: datetime
