
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate
from app.repositories import user_repository
from sqlalchemy.exc import IntegrityError


from app.core.security import hash_password

async def signup(db: AsyncSession, payload: UserCreate) -> User:
    user = User(
        name = payload.name,
        username = payload.username,
        email = payload.email,
        password_hash = hash_password(payload.password)
    )

    try:
        await user_repository.create(db, user)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = "User with this email or username already exists."
        )
    return user