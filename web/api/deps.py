from fastapi import Cookie, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from .auth import decode_access_token
from .config import get_settings
from .db import get_db
from .models import User

settings = get_settings()


def get_token_from_request(
    cinema_token: str | None = Cookie(default=None, alias="cinema_token"),
    authorization: str | None = Header(default=None),
) -> str | None:
    if cinema_token:
        return cinema_token
    if authorization and authorization.startswith("Bearer "):
        return authorization.split(" ", 1)[1]
    return None


def _user_from_token(db: Session, token: str | None) -> User | None:
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    return db.get(User, int(user_id))


def get_current_user_optional(
    db: Session = Depends(get_db),
    token: str | None = Depends(get_token_from_request),
) -> User | None:
    return _user_from_token(db, token)


def get_current_user(
    db: Session = Depends(get_db),
    token: str | None = Depends(get_token_from_request),
) -> User:
    user = _user_from_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bạn cần đăng nhập.",
        )
    return user


def get_admin_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ admin mới được phép.",
        )
    return user

