# import necessary modules
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import User

async def create(db: AsyncSession, user: User) -> User:
    db.add(user)
    await db.flush() 
    await db.refresh(user)  
    return user
