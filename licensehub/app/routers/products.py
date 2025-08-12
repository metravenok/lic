from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..db import get_db_session
from ..models import Vendor, SoftwareProduct
from ..schemas import VendorCreate, VendorRead, ProductCreate, ProductRead
from ..auth import get_current_user

router = APIRouter(prefix="", tags=["catalog"])


# Vendors
@router.post("/vendors", response_model=VendorRead)
async def create_vendor(
    data: VendorCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    vendor = Vendor(name=data.name, homepage=data.homepage, notes=data.notes)
    session.add(vendor)
    await session.commit()
    await session.refresh(vendor)
    return vendor


@router.get("/vendors", response_model=list[VendorRead])
async def list_vendors(session: AsyncSession = Depends(get_db_session)):
    result = await session.execute(select(Vendor).order_by(Vendor.name))
    return list(result.scalars().all())


# Products
@router.post("/products", response_model=ProductRead)
async def create_product(
    data: ProductCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    product = SoftwareProduct(name=data.name, category=data.category, vendor_id=data.vendor_id, notes=data.notes)
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


@router.get("/products", response_model=list[ProductRead])
async def list_products(session: AsyncSession = Depends(get_db_session)):
    result = await session.execute(select(SoftwareProduct).order_by(SoftwareProduct.name))
    return list(result.scalars().all())