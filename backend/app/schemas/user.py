import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """创建用户时允许客户端提交的数据。"""

    email: EmailStr
    password: str = Field(
        min_length=12,
        max_length=128,
    )


class UserResponse(BaseModel):
    """返回给客户端的公开用户数据。"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime
