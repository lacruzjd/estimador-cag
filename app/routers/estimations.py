"""
Capa de transporte HTTP y schemas de datos.

Gestiona el endpoint POST /api/v1/estimate y valida las peticiones y
respuestas mediante Pydantic.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.estimation import EstimationRequest, EstimationResponse
from app.services.llm_service import generate_estimation

router = APIRouter(prefix="/api/v1", tags=["estimations"])

@router.post(
    "/estimate",
    response_model=EstimationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generar estimación de software desde transcripción"         
)
async def estimate(request: EstimationRequest):
    """Genera una estimación a partir de la transcripción recibida."""
    try: 
        result = await generate_estimation(request.transcription)
        return result 
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        ) from ve
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el procesamiento de la estimación: {str(e)}"
        ) from e