from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..db import get_db_session
from ..models import Memo
from ..schemas import MemoCreate, MemoRead
from ..auth import get_current_user

router = APIRouter(prefix="", tags=["memos"])


@router.post("/memos", response_model=MemoRead)
async def create_memo(
    data: MemoCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    memo = Memo(**data.model_dump(), author_user_id=current_user.id)
    session.add(memo)
    await session.commit()
    await session.refresh(memo)
    return memo


@router.get("/memos", response_model=list[MemoRead])
async def list_memos(session: AsyncSession = Depends(get_db_session)):
    result = await session.execute(select(Memo).order_by(Memo.id.desc()))
    return list(result.scalars().all())