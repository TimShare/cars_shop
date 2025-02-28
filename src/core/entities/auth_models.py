from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class User:
    email: str
    id: UUID | None = field(default_factory=uuid4)
    hashed_password: Optional[str] = None
    last_login: datetime | None = None
    is_active: bool = False
    is_superuser: bool = False
    created_at: datetime | None = field(default_factory=datetime.now)
    updated_at: datetime | None = field(default_factory=datetime.now)
    blocked_at: datetime | None = None


@dataclass
class Profile:
    user_id: UUID
    first_name: str
    last_name: str
    middle_name: str | None = None
    phone: str | None = None
    created_at: datetime | None = field(default_factory=datetime.now)
    updated_at: datetime | None = field(default_factory=datetime.now)
    id: UUID | None = field(default_factory=uuid4)


@dataclass
class BannedRefreshToken:
    jti: str
    id: UUID | None = field(default_factory=uuid4)
    created_at: datetime | None = field(default_factory=datetime.now)


@dataclass
class Token:
    access_token: str
    refresh_token: str
    token_type: str
    access_token_expires: datetime 
    refresh_token_expires: datetime
    scopes: List[str] = field(default_factory=list)
