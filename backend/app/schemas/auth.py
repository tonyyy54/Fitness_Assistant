from typing import Literal

from pydantic import BaseModel


class TokenResponse(BaseModel):
    """登录成功后返回的访问令牌。"""

    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int
