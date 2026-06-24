import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.email import send_email
from app.core.security import hash_password
from app.modules.auth import repository
from app.modules.auth.models import EmailVerificationToken, User
from app.modules.auth.schemas import UserCreate

# How long a verification link stays valid.
VERIFICATION_TOKEN_TTL_HOURS = 24


async def signup(db: AsyncSession, payload: UserCreate) -> User:
    user = User(
        name=payload.name,
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )

    try:
        await repository.create(db, user)  # flush -> user.id is now available

        # Build a one-time verification token tied to this user.
        token_str = secrets.token_urlsafe(32)
        token = EmailVerificationToken(
            user_id=user.id,
            token=token_str,
            expires_at=datetime.now(timezone.utc)
            + timedelta(hours=VERIFICATION_TOKEN_TTL_HOURS),
        )
        await repository.add_email_token(db, token)

        # User + token are persisted together (atomic).
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email or username already exists.",
        )

    # Side effect AFTER commit. In production this would move to a background
    # job (outbox pattern, Day 5) so a slow/failing SMTP can't block signup.
    await _send_verification_email(user.email, token_str)
    return user


async def _send_verification_email(email: str, token_str: str) -> None:
    link = f"{settings.app_base_url}/api/v1/auth/verify-email?token={token_str}"
    await send_email(
        to=email,
        subject="Verify your FlowTask email",
        body=(
            "Welcome to FlowTask!\n\n"
            "Please verify your email by opening this link:\n"
            f"{link}\n\n"
            f"This link expires in {VERIFICATION_TOKEN_TTL_HOURS} hours."
        ),
    )


async def verify_email(db: AsyncSession, token_str: str) -> User:
    token = await repository.get_email_token(db, token_str)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or unknown verification token.",
        )

    now = datetime.now(timezone.utc)
    if token.expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired.",
        )

    user = await repository.get_user_by_id(db, token.user_id)
    user.email_verified_at = now
    await repository.delete_email_token(db, token)  # one-time use
    await db.commit()
    return user
