from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from ldap3 import ALL, Connection, Server, Tls
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .db import get_db_session
from .models import User
from .schemas import LoginRequest, TokenResponse, CurrentUserResponse

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class TokenData(BaseModel):
    sub: str
    exp: int


async def _ldap_bind_and_fetch(username: str, password: str) -> dict[str, Optional[str]]:
    user_dn_value = settings.ad_user_dn_format.format(username=username)

    server = Server(settings.ad_server_uri, get_info=ALL, use_ssl=settings.ad_use_ssl)

    def sync_bind_and_search() -> dict[str, Optional[str]]:
        with Connection(server, user=user_dn_value, password=password, auto_bind=True) as user_conn:
            # If a service account is provided, use it for the search to get attributes
            if settings.ad_service_account_dn and settings.ad_service_account_password:
                with Connection(
                    server,
                    user=settings.ad_service_account_dn,
                    password=settings.ad_service_account_password,
                    auto_bind=True,
                ) as svc_conn:
                    svc_conn.search(
                        search_base=settings.ad_base_dn,
                        search_filter=f"(sAMAccountName={username.split('\\\\')[-1].split('@')[0]})",
                        attributes=[
                            "displayName",
                            "mail",
                            "department",
                            "sAMAccountName",
                        ],
                        size_limit=1,
                    )
                    if not svc_conn.entries:
                        return {}
                    entry = svc_conn.entries[0]
                    return {
                        "sam": str(entry.sAMAccountName) if hasattr(entry, "sAMAccountName") else None,
                        "display_name": str(entry.displayName) if hasattr(entry, "displayName") else None,
                        "email": str(entry.mail) if hasattr(entry, "mail") else None,
                        "department": str(entry.department) if hasattr(entry, "department") else None,
                    }
            else:
                # Use the bound user for self lookup
                user_conn.search(
                    search_base=settings.ad_base_dn,
                    search_filter=f"(sAMAccountName={username.split('\\\\')[-1].split('@')[0]})",
                    attributes=["displayName", "mail", "department", "sAMAccountName"],
                    size_limit=1,
                )
                if not user_conn.entries:
                    return {}
                entry = user_conn.entries[0]
                return {
                    "sam": str(entry.sAMAccountName) if hasattr(entry, "sAMAccountName") else None,
                    "display_name": str(entry.displayName) if hasattr(entry, "displayName") else None,
                    "email": str(entry.mail) if hasattr(entry, "mail") else None,
                    "department": str(entry.department) if hasattr(entry, "department") else None,
                }

    return await asyncio.to_thread(sync_bind_and_search)


def _create_access_token(subject: str) -> str:
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, session: AsyncSession = Depends(get_db_session)) -> TokenResponse:
    profile = await _ldap_bind_and_fetch(data.username, data.password)
    if not profile or not profile.get("sam"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    sam_name = profile.get("sam") or data.username

    result = await session.execute(select(User).where(User.sam_account_name == sam_name))
    user: Optional[User] = result.scalar_one_or_none()

    if user is None:
        user = User(
            sam_account_name=sam_name,
            display_name=profile.get("display_name"),
            email=profile.get("email"),
            department=profile.get("department"),
            is_admin=False,
        )
        session.add(user)
    else:
        user.display_name = profile.get("display_name")
        user.email = profile.get("email")
        user.department = profile.get("department")

    await session.commit()

    token = _create_access_token(subject=user.sam_account_name)
    return TokenResponse(access_token=token)


async def get_current_user(
    token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_db_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        subject: str | None = payload.get("sub")
        if subject is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await session.execute(select(User).where(User.sam_account_name == subject))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


@router.get("/me", response_model=CurrentUserResponse)
async def me(current_user: User = Depends(get_current_user)) -> CurrentUserResponse:
    return CurrentUserResponse.model_validate(current_user)