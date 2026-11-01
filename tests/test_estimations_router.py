from types import SimpleNamespace

import pytest

from app.routers import estimations
from app.services import llm_service


def test_estimate_router_returns_generated_estimation(client, monkeypatch):
    settings = SimpleNamespace(
        OPENAI_API_KEY="sk-test-key",
        LLM_MODEL="gpt-4o-mini",
        LLM_PROVIDER="openai",
    )

    class FakeCompletions:
        async def create(self, **kwargs):
            messages = kwargs["messages"]
            assert any(
                message["role"] == "user"
                and "Reunión con cliente" in message["content"]
                for message in messages
            )
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            content="Se requieren 3 semanas con 2 desarrolladores"
                        )
                    )
                ]
            )

    class FakeOpenAIClient:
        def __init__(self, api_key):
            self.chat = SimpleNamespace(
                completions=FakeCompletions()
            )

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return None

    monkeypatch.setattr(llm_service, "get_settings", lambda: settings)
    monkeypatch.setattr(llm_service, "AsyncOpenAI", FakeOpenAIClient)
    response = client.post(
        "/api/v1/estimate",
        json={
            "transcription": "Reunión con cliente para crear una plataforma de ventas con dashboards y autenticación."
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "estimation": "Se requieren 3 semanas con 2 desarrolladores",
        "model": "gpt-4o-mini",
        "provider": "openai",
    }


def test_estimate_router_rejects_short_transcription(client):
    """RED: la API debe rechazar transcripciones demasiado cortas."""
    response = client.post("/api/v1/estimate", json={"transcription": "corto"})

    assert response.status_code == 422


def test_estimate_router_returns_400_for_validation_error(client, monkeypatch):
    """RED: errores de validación del servicio deben convertirse en 400."""

    async def fake_generate_estimation(_transcription: str):
        raise ValueError("La clave de API de OpenAI no está configurada")

    monkeypatch.setattr(estimations, "generate_estimation", fake_generate_estimation)

    response = client.post(
        "/api/v1/estimate",
        json={
            "transcription": "Reunión con cliente para crear una plataforma de ventas con dashboards y autenticación."
        },
    )

    assert response.status_code == 400
    assert "configurada" in response.json()["detail"]


def test_estimate_router_returns_500_for_unexpected_errors(client, monkeypatch):
    """Refactor: errores inesperados del backend deben responder 500."""

    async def fake_generate_estimation(_transcription: str):
        raise RuntimeError("Fallo interno inesperado")

    monkeypatch.setattr(estimations, "generate_estimation", fake_generate_estimation)

    response = client.post(
        "/api/v1/estimate",
        json={
            "transcription": "Reunión con cliente para crear una plataforma de ventas con dashboards y autenticación."
        },
    )

    assert response.status_code == 500
    assert "Error en el procesamiento de la estimación" in response.json()["detail"]
