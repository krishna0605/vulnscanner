from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from models.scan_job import ScanJob, ScanJobStatus


async def create_scan_job(session: AsyncSession, url: str) -> ScanJob:
    job = ScanJob(url=url, status=ScanJobStatus.queued.value)
    session.add(job)
    await session.flush()
    await session.commit()
    await session.refresh(job)
    return job