"""
Methodology and analytical policies route handler.
"""

from fastapi import APIRouter, HTTPException
from ...schemas.methodology import MethodologyResponse
from ...services.data_service import data_service

router = APIRouter(prefix="/api/v1/methodology", tags=["Methodology & Guardrails"])


@router.get("", response_model=MethodologyResponse, summary="Get analytical methodology and evidence contracts")
def get_methodology():
    """
    Returns the project charter, anti-hoarding policies, data contracts,
    and evidence level definitions governing Punjab GrainWatch.
    """
    try:
        return data_service.get_methodology()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load methodology: {str(e)}")
