from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class ScanJobCreate(BaseModel):
    url: str = Field(min_length=4)


class ScanJobRead(BaseModel):
    id: str
    url: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }