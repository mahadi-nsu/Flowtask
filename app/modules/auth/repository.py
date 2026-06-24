import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import EmailVerificationToken, User


async def create(db: AsyncSession, user: User) -> User:
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    return await db.get(User, user_id)


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    return result.scalar_one_or_none()


# --- email verification tokens ---

async def add_email_token(
    db: AsyncSession, token: EmailVerificationToken
) -> EmailVerificationToken:
    db.add(token)
    await db.flush()
    await db.refresh(token)
    return token


async def get_email_token(
    db: AsyncSession, token: str
) -> EmailVerificationToken | None:
    result = await db.execute(
        select(EmailVerificationToken).where(EmailVerificationToken.token == token)
    )
    return result.scalar_one_or_none()


async def delete_email_token(
    db: AsyncSession, token: EmailVerificationToken
) -> None:
    await db.delete(token)
