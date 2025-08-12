from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from ..db import get_db_session
from ..models import Assignment, AssignmentStatus
from ..schemas import AssignmentCreate, AssignmentRead
from ..auth import get_current_user

router = APIRouter(prefix="", tags=["assignments"])


@router.post("/assignments", response_model=AssignmentRead)
async def create_assignment(
    data: AssignmentCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    assignment = Assignment(
        license_id=data.license_id,
        assigned_to_user_id=data.assigned_to_user_id,
        assigned_machine=data.assigned_machine,
        due_back_at=data.due_back_at,
        status=AssignmentStatus.ASSIGNED,
    )
    session.add(assignment)
    await session.commit()
    await session.refresh(assignment)
    return assignment


@router.get("/assignments", response_model=list[AssignmentRead])
async def list_assignments(session: AsyncSession = Depends(get_db_session)):
    result = await session.execute(select(Assignment))
    return list(result.scalars().all())


@router.post("/assignments/{assignment_id}/return", response_model=AssignmentRead)
async def return_assignment(
    assignment_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    result = await session.execute(select(Assignment).where(Assignment.id == assignment_id))
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    assignment.status = AssignmentStatus.RETURNED
    await session.commit()
    await session.refresh(assignment)
    return assignment