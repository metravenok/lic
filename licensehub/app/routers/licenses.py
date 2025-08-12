from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..db import get_db_session
from ..models import License, LicenseType
from ..schemas import LicenseCreate, LicenseRead
from ..auth import get_current_user

router = APIRouter(prefix="", tags=["licenses"])


@router.post("/licenses", response_model=LicenseRead)
async def create_license(
    data: LicenseCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    try:
        license_type = LicenseType(data.license_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid license_type")

    lic = License(
        product_id=data.product_id,
        license_key=data.license_key,
        license_type=license_type,
        seat_count=data.seat_count,
        start_date=data.start_date,
        end_date=data.end_date,
        maintenance_end_date=data.maintenance_end_date,
        purchase_order_id=data.purchase_order_id,
        owner_user_id=data.owner_user_id,
        cost_total=data.cost_total,
        currency=data.currency,
        notes=data.notes,
    )
    session.add(lic)
    await session.commit()
    await session.refresh(lic)
    return lic


@router.get("/licenses", response_model=list[LicenseRead])
async def list_licenses(session: AsyncSession = Depends(get_db_session)):
    result = await session.execute(select(License))
    return list(result.scalars().all())


@router.get("/jobs/check-expirations")
async def check_expirations(session: AsyncSession = Depends(get_db_session)):
    now = datetime.now(timezone.utc).date()
    result = await session.execute(select(License).where(License.end_date.is_not(None)))
    to_check = list(result.scalars().all())
    expired = []
    for lic in to_check:
        if lic.end_date and lic.end_date < now:
            expired.append(lic.id)
    return {"expired_count": len(expired), "expired_ids": expired}