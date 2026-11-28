from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.security import CurrentUser, require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


class AdminStatus(BaseModel):
    status: Literal["ok"]


@router.get("/status", response_model=AdminStatus)
def admin_status(_: CurrentUser = Depends(require_admin)) -> AdminStatus:
    """Page admin vide (partie 1) : sert à prouver que le contrôle de rôle est côté serveur."""
    return AdminStatus(status="ok")
