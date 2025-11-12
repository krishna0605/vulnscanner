from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from schemas.scan_job import ScanJobCreate, ScanJobRead
from services.scan_job_service import create_scan_job

router = APIRouter(prefix="/api/v1/scan-jobs", tags=["scan-jobs"])


@router.post("", response_model=ScanJobRead)
async def create_scan_job_endpoint(
    payload: ScanJobCreate, session: AsyncSession = Depends(get_async_session)
):
    job = await create_scan_job(session, url=payload.url)
    return ScanJobRead.model_validate(job)