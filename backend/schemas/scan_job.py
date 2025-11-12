from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field
from pydantic import ConfigDict


class ScanJobCreate(BaseModel):
    url: str = Field(..., min_length=1)


class ScanJobRead(BaseModel):
    id: str
    url: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)