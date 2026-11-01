from pydantic import BaseModel, Field


class EstimationRequest(BaseModel):
    transcription: str = Field(
        ...,
        min_length=10,
        description="Texto plano con la transcripción de la reunión de requerimientos",
        examples=[
            "El cliente necesita una plataforma web de gestión de inventario...",
            "Creación de una landing page promocional con formulario de contacto e integración a CRM vía API.",
        ],
    )


class EstimationResponse(BaseModel):
    estimation: str = Field(..., description="Reporte de estimación generado en formato Markdown")
    model: str = Field(..., description="Modelo de lenguaje utilizado para la generación")
    provider: str = Field(..., description="Proveedor del servicio de IA")


EstimadorRequest = EstimationRequest
EstimadorResponse = EstimationResponse
