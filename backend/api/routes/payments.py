from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db, csrf_protect


router = APIRouter(prefix="/api/payments", tags=["payments"])


@router.post("/checkout")
async def checkout(plan_id: str, db: AsyncSession = Depends(get_db), _=Depends(csrf_protect)):
  # Placeholder: validate plan, create Stripe session, return session URL
  if plan_id not in {"starter", "pro", "enterprise"}:
    raise HTTPException(status_code=400, detail="Invalid plan")
  return {"checkout_url": f"https://example.com/checkout/{plan_id}"}