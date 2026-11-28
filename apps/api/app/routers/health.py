from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: Literal["ok"]


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Point de santé : ne touche à aucune donnée, sert à vérifier que le service répond."""
    return HealthResponse(status="ok")
