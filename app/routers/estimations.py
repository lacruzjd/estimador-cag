"""
Capa de transporte HTTP y schemas de datos.

Gestiona el endpoint POST /api/v1/estimate y valida las peticiones y
respuestas mediante Pydantic.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.llm_service import generate_estimation


class EstimationRequest(BaseModel):
    """Estructura y validación de la solicitud enviada por el cliente."""

    transcription: str = Field(
        ...,
        min_length=20,
        description="Texto de la transcripción de la reunión con el cliente",
        examples=[
            "En la reunión el cliente solicitó un e-commerce con catálogo y "
            "pasarela de pago Stripe."
        ],
    )


class EstimationResponse(BaseModel):
    """Estructura de la respuesta devuelta por la API."""

    estimation: str = Field(
        ...,
        description="Estimación en formato Markdown generada por el LLM",
    )
    model: str = Field(..., description="Nombre del modelo de IA utilizado")
    provider: str = Field(
        ...,
        description="Proveedor del servicio (ej. openai, anthropic)",
    )


router = APIRouter(prefix="/api/v1", tags=["estimations"])


@router.post("/estimate", response_model=EstimationResponse)
async def estimate(request: EstimationRequest):
    """Genera una estimación a partir de la transcripción de una reunión."""
    try:
        return generate_estimation(request.transcription)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar la estimación: {error}",
        )
