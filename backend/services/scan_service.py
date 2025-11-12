"""
Scan Service for managing scan operations and database interactions.
"""
import logging
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timezone

from ..models.unified_models import ScanSession, DiscoveredUrl, ExtractedForm, TechnologyFingerprint

logger = logging.getLogger(__name__)


class ScanService:
    """Service for managing scan operations."""
    
    def __init__(self):
        """Initialize the scan service."""
    
    async def update_scan_status(self, session: AsyncSession, scan_id: str, status: str) -> None:
        """Update the status of a scan session. Raises on failure."""
        stmt = update(ScanSession).where(ScanSession.id == scan_id).values(
            status=status,
            updated_at=datetime.now(timezone.utc)
        )
        try:
            await session.execute(stmt)
            await session.commit()
            logger.info(f"Updated scan {scan_id} status to {status}")
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to update scan {scan_id} status to {status}: {e}")
            raise
    
    async def get_scan_session(self, session: AsyncSession, scan_id: str) -> Optional[ScanSession]:
        """Get a scan session by ID. Returns None when not found; raises on query error."""
        stmt = select(ScanSession).where(ScanSession.id == scan_id)
        try:
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed querying scan session {scan_id}: {e}")
            raise
    
    async def save_discovered_url(self, session: AsyncSession, url_data: Dict[str, Any]) -> None:
        """Save a discovered URL to the database. Raises on failure."""
        try:
            discovered_url = DiscoveredUrl(**url_data)
            session.add(discovered_url)
            await session.commit()
        except Exception as e:
            logger.error(f"Failed to save discovered URL: {e}")
            await session.rollback()
            raise
    
    async def save_extracted_form(self, session: AsyncSession, form_data: Dict[str, Any]) -> None:
        """Save an extracted form to the database. Raises on failure."""
        try:
            extracted_form = ExtractedForm(**form_data)
            session.add(extracted_form)
            await session.commit()
        except Exception as e:
            logger.error(f"Failed to save extracted form: {e}")
            await session.rollback()
            raise
    
    async def save_technology_fingerprint(self, session: AsyncSession, tech_data: Dict[str, Any]) -> None:
        """Save technology fingerprint data to the database. Raises on failure."""
        try:
            tech_fingerprint = TechnologyFingerprint(**tech_data)
            session.add(tech_fingerprint)
            await session.commit()
        except Exception as e:
            logger.error(f"Failed to save technology fingerprint: {e}")
            await session.rollback()
            raise
    
    async def get_scan_statistics(self, session: AsyncSession, scan_id: str) -> Dict[str, Any]:
        """Get statistics for a scan session."""
        try:
            # Count discovered URLs
            url_count_stmt = select(DiscoveredUrl).where(DiscoveredUrl.session_id == scan_id)
            url_result = await session.execute(url_count_stmt)
            url_count = len(url_result.scalars().all())
            
            # Count extracted forms
            form_count_stmt = select(ExtractedForm).join(DiscoveredUrl).where(DiscoveredUrl.session_id == scan_id)
            form_result = await session.execute(form_count_stmt)
            form_count = len(form_result.scalars().all())
            
            # Count technology fingerprints
            tech_count_stmt = select(TechnologyFingerprint).join(DiscoveredUrl).where(DiscoveredUrl.session_id == scan_id)
            tech_result = await session.execute(tech_count_stmt)
            tech_count = len(tech_result.scalars().all())
            
            return {
                "urls_discovered": url_count,
                "forms_extracted": form_count,
                "technologies_detected": tech_count
            }
        except Exception as e:
            logger.error(f"Failed to get scan statistics: {e}")
            return {
                "urls_discovered": 0,
                "forms_extracted": 0,
                "technologies_detected": 0
            }