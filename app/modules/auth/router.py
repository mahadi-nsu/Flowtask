from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth import service
from app.modules.auth.schemas import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserRead,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserRead)
async def signup(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    return await service.signup(db, payload)


@router.get("/verify-email")
async def verify_email(
    token: str = Query(..., description="Verification token from the email link"),
    db: AsyncSession = Depends(get_db),
):
    await service.verify_email(db, token)
    return {"message": "Email verified successfully."}


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    access_token = await service.login(db, payload)
    return TokenResponse(access_token=access_token)
