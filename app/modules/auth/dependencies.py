import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.modules.auth import repository
from app.modules.auth.models import User

# Reads the "Authorization: Bearer <token>" header. Gives Swagger an
# "Authorize" button where you paste the access token.
bearer_scheme = HTTPBearer()

# One shared 401 — we never reveal *why* auth failed (token bad? user gone?).
_credentials_error = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials.",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Resolve the User behind the bearer token. Use as a dependency on any
    protected route: `current_user: User = Depends(get_current_user)`.
    """
    token = credentials.credentials  # the raw JWT string

    # 1. Verify signature + expiry, get the payload.
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise _credentials_error

    # 2. Pull the user id out of the "sub" claim.
    user_id = payload.get("sub")
    if user_id is None:
        raise _credentials_error

    # 3. Load the user fresh from the DB (token only carries the id).
    try:
        user = await repository.get_user_by_id(db, uuid.UUID(user_id))
    except ValueError:  # sub wasn't a valid UUID string
        raise _credentials_error

    # 4. Token was valid but the user no longer exists.
    if user is None:
        raise _credentials_error

    return user
