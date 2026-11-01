from types import SimpleNamespace

import pytest

from app.services.llm_service import generate_estimation


class FakeCompletions:
    def __init__(self, response_text):
        self.response_text = response_text
        self.kwargs = None

    async def create(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=self.response_text),
                )
            ]
        )


class FakeOpenAIClient:
    def __init__(self, response_text):
        self.completions = FakeCompletions(response_text)
        self.chat = SimpleNamespace(completions=self.completions)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return None


@pytest.mark.asyncio
async def test_generate_estimation_returns_model_output(monkeypatch):
    settings = SimpleNamespace(
        OPENAI_API_KEY="sk-test-key",
        LLM_MODEL="gpt-4o-mini",
        LLM_PROVIDER="openai",
    )
    fake_client = FakeOpenAIClient(
        "Se requieren 3 semanas con 2 desarrolladores"
    )

    monkeypatch.setattr("app.services.llm_service.get_settings", lambda: settings)
    monkeypatch.setattr(
        "app.services.llm_service.AsyncOpenAI",
        lambda api_key: fake_client,
    )

    result = await generate_estimation(
        "Resumen de reunión con dashboard y autenticación"
    )

    assert result == {
        "estimation": "Se requieren 3 semanas con 2 desarrolladores",
        "model": "gpt-4o-mini",
        "provider": "openai",
    }


@pytest.mark.asyncio
async def test_generate_estimation_raises_when_api_key_missing(monkeypatch):
    settings = SimpleNamespace(
        OPENAI_API_KEY="",
        LLM_MODEL="gpt-4o-mini",
        LLM_PROVIDER="openai",
    )

    monkeypatch.setattr("app.services.llm_service.get_settings", lambda: settings)

    with pytest.raises(ValueError, match="no está configurada"):
        await generate_estimation("Resumen válido")


@pytest.mark.asyncio
async def test_generate_estimation_uses_prompt_context_from_examples(monkeypatch):
    settings = SimpleNamespace(
        OPENAI_API_KEY="sk-test-key",
        LLM_MODEL="gpt-4o-mini",
        LLM_PROVIDER="openai",
    )
    fake_client = FakeOpenAIClient("Estimación generada")

    monkeypatch.setattr("app.services.llm_service.get_settings", lambda: settings)
    monkeypatch.setattr(
        "app.services.llm_service.AsyncOpenAI",
        lambda api_key: fake_client,
    )

    await generate_estimation("Necesito una app con login y dashboard")

    messages = fake_client.completions.kwargs["messages"]
    assert messages[0]["role"] == "system"
    assert "Ejemplo 1" in messages[0]["content"]
    assert messages[1] == {
        "role": "user",
        "content": "Necesito una app con login y dashboard",
    }
