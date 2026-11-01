""" 
Servicio de integración con el LLM. 
Construye el prompt ensamblando el contexto estático (CAG) y
realiza la petición a la API de OpenAI. 
"""

from openai import AsyncOpenAI
from app.config import get_settings
from app.context.examples import ESTIMATION_EXAMPLES


def build_system_prompt() -> str:
    """Construye el prompt del sistema con los ejemplos históricos CAG."""
    examples = "\n\n".join(
        f"--- Ejemplo {index} ---\n"
        f"Resumen de reunión: {example['meeting_summary']}\n"
        f"Estimación:\n{example['estimation']}"
        for index, example in enumerate(ESTIMATION_EXAMPLES, start=1)
    )
    return (
        "Eres un experto en estimaciones de proyectos. "
        "Basándote en los siguientes ejemplos históricos, genera una estimación "
        "detallada para la solicitud actual:\n\n"
        f"{examples}"
    )


async def generate_estimation(meeting_summary: str) -> dict[str, str]:
    """
    Genera una estimación de tiempo y recursos para un proyecto basado en el resumen de la reunión.
    
    Args:
        meeting_summary (str): Resumen de la reunión con los requerimientos del proyecto.
    
    Returns:
        dict[str, str]: Estimación y metadatos del modelo utilizado.
    """

    # 1. Cargar la configuración centralizada (API key, modelo, etc.)
    settings = get_settings()

    # 2. Validación preventiva de la API key
    if not settings.OPENAI_API_KEY:
        raise ValueError("La clave de API de OpenAI no está configurada. Por favor, revisa el archivo .env.")
    
    system_prompt = build_system_prompt()

    async with AsyncOpenAI(api_key=settings.OPENAI_API_KEY) as client:
        # 5. Enviar la solicitud a la API del modelo
        response = await client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": meeting_summary},
            ],
            max_tokens=500,
            temperature=0.3,
        )

    # 6. Extraer el texto de la respuesta devuelta por el modelo   
    estimation_text = response.choices[0].message.content    

    # 7. Retornar un diccionario estructurado 
    return { 
        "estimation": estimation_text, 
        "model": settings.LLM_MODEL, 
        "provider": settings.LLM_PROVIDER 
    }
