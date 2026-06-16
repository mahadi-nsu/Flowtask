from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Shared declarative base. All models inherit from this so they share
    a single MetaData — which is what Alembic autogenerate inspects."""


class TimestampMixin:
    """Adds created_at / updated_at, both filled by the database server."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),  # bumped on every UPDATE
        nullable=False,
    )


class SoftDeleteMixin:
    """Adds deleted_at. NULL = active row; a timestamp = soft-deleted.
    We never hard-delete; queries filter on deleted_at IS NULL."""

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
