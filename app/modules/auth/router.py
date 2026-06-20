from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.schemas import UserCreate, UserRead
from app.modules.auth import service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserRead)
async def signup(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    return await service.signup(db, payload)
