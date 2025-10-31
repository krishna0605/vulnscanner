from typing import Optional
from datetime import datetime
import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from db.session import Base


class User(Base):
  __tablename__ = "users"

  id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
  email: Mapped[str] = mapped_column(sa.String(255), unique=True, index=True)
  hashed_password: Mapped[str] = mapped_column(sa.String(255))
  full_name: Mapped[Optional[str]] = mapped_column(sa.String(255), nullable=True)
  created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())