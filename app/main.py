from fastapi import FastAPI
from app.routers import estimations


app = FastAPI(
    title="Estimador CAG API",
    description=(
        "Sistema de estimación automatizada de software utilizando arquitectura "
        "Cache-Augmented Generation (CAG)."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(estimations.router)


@app.get("/health", tags=["system"])
async def health():
    """Verifica que la aplicación y el servidor web estén respondiendo."""
    return {
        "status": "healthy",
        "service": "estimador-cag",
        "version": "0.1.0",
    }