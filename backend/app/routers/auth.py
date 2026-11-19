from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    verify_password,
    hash_session_token,
    generate_session_token,
    get_current_admin,
    needs_rehash,
    hash_password,
)
from app.core.config import settings
from app.models.auth import AdminUser, AdminSession
from app.schemas.auth import LoginRequest, AdminUserOut
from app.utils.activity import log_activity

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
async def login(
    data: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    ip = request.client.host if request.client else None

    # Find user by username or email
    result = await db.execute(
        select(AdminUser).where(
            (AdminUser.username == data.username) | (AdminUser.email == data.username)
        )
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        await log_activity(db, "login_failed", ip_address=ip, description=f"Failed login for: {data.username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")

    # Rehash if needed
    if needs_rehash(user.hashed_password):
        await db.execute(
            update(AdminUser).where(AdminUser.id == user.id).values(hashed_password=hash_password(data.password))
        )

    # Update last login
    await db.execute(
        update(AdminUser).where(AdminUser.id == user.id).values(last_login=datetime.now(timezone.utc))
    )

    # Create session
    token = generate_session_token()
    token_hash = hash_session_token(token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.SESSION_EXPIRE_DAYS)

    session = AdminSession(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
        ip_address=ip,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(session)
    await db.commit()

    await log_activity(db, "login_success", entity_type="admin_user", entity_id=str(user.id), ip_address=ip)

    # Set HttpOnly cookie
    is_prod = settings.is_production
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=is_prod,
        samesite="lax",
        max_age=settings.SESSION_EXPIRE_DAYS * 86400,
        path="/",
    )

    # Token is set as HttpOnly cookie above — do NOT return it in the body.
    # login.astro reads it via a custom X-Session-Token response header (SSR only).
    response.headers["X-Session-Token"] = token
    return {"message": "Login successful", "user": AdminUserOut.model_validate(user)}


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    session_token = request.cookies.get("session_token")
    if session_token:
        token_hash = hash_session_token(session_token)
        await db.execute(
            update(AdminSession).where(AdminSession.token_hash == token_hash).values(is_valid=False)
        )
        await db.commit()

    await log_activity(db, "logout", entity_type="admin_user", entity_id=str(current_admin.id))

    response.delete_cookie("session_token", path="/")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=AdminUserOut)
async def get_me(current_admin=Depends(get_current_admin)):
    return current_admin
