from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.security import hash_password, verify_password


class EmailAlreadyRegisteredError(Exception):
    """注册邮箱已经存在。"""


def get_user_by_email(
    database_session: Session,
    email: str,
) -> User | None:
    """根据规范化邮箱查询用户。"""

    statement = select(User).where(User.email == email)

    return database_session.scalar(statement)


def create_user(
    database_session: Session,
    user_data: UserCreate,
) -> User:
    """创建用户，但不提交当前数据库事务。"""

    normalized_email = str(user_data.email).lower()

    existing_user = get_user_by_email(
        database_session,
        normalized_email,
    )

    if existing_user is not None:
        raise EmailAlreadyRegisteredError

    user = User(
        email=normalized_email,
        password_hash=hash_password(user_data.password),
    )

    database_session.add(user)

    try:
        database_session.flush()
    except IntegrityError as error:
        database_session.rollback()
        raise EmailAlreadyRegisteredError from error

    database_session.refresh(user)

    return user


def authenticate_user(
    database_session: Session,
    email: str,
    password: str,
) -> User | None:
    """验证邮箱和密码，成功时返回用户。"""

    normalized_email = email.lower()
    user = get_user_by_email(
        database_session,
        normalized_email,
    )

    if user is None:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    if not user.is_active:
        return None

    return user
