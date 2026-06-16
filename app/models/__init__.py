from app.models.base import Base
from app.models.user import User

# Importing every model here ensures it's registered on Base.metadata before
# Alembic autogenerate runs. As you add models, import them in this file too.
__all__ = ["Base", "User"]
