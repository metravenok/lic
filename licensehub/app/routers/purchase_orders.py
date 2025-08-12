from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..db import get_db_session
from ..models import PurchaseOrder
from ..schemas import PurchaseOrderCreate, PurchaseOrderRead
from ..auth import get_current_user

router = APIRouter(prefix="", tags=["purchase_orders"])


@router.post("/purchase-orders", response_model=PurchaseOrderRead)
async def create_po(
    data: PurchaseOrderCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    po = PurchaseOrder(**data.model_dump())
    session.add(po)
    await session.commit()
    await session.refresh(po)
    return po


@router.get("/purchase-orders", response_model=list[PurchaseOrderRead])
async def list_pos(session: AsyncSession = Depends(get_db_session)):
    result = await session.execute(select(PurchaseOrder).order_by(PurchaseOrder.id.desc()))
    return list(result.scalars().all())