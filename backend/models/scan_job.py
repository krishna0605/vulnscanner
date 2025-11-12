from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from db.session import Base


class ScanJobStatus(str, Enum):
    queued = "queued"
    running = "running"
    done = "done"
    failed = "failed"


class ScanJob(Base):
    __tablename__ = "scan_jobs"

    id: Mapped[str] = mapped_column(
        sa.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    url: Mapped[str] = mapped_column(sa.String(2000), index=True, nullable=False)
    status: Mapped[str] = mapped_column(
        sa.Enum(ScanJobStatus, name="scan_job_status"),
        nullable=False,
        default=ScanJobStatus.queued.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
        nullable=False,
    )