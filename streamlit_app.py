import time

import streamlit as st
from openai import OpenAI, OpenAIError

from app.config import get_settings
from app.context.examples import ESTIMATION_EXAMPLES
from app.services.llm_service import build_system_prompt


# Cargar configuración global (API keys y proveedor).
settings = get_settings()

st.set_page_config(
    page_title="Estimador de Software CAG",
    page_icon="🤖",
    layout="wide",
)
st.title("🤖 Estimador de Proyectos de Software")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "metrics" not in st.session_state:
    st.session_state.metrics = None

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input(
    "Pega aquí la transcripción de la reunión o haz una consulta..."
):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not settings.OPENAI_API_KEY:
        st.error("La clave de API de OpenAI no está configurada.")
    else:
        with st.chat_message("assistant"):
            try:
                system_prompt = build_system_prompt()
                api_messages = [
                    {"role": "system", "content": system_prompt},
                    *st.session_state.messages,
                ]
                start_time = time.perf_counter()

                with OpenAI(api_key=settings.OPENAI_API_KEY) as client:
                    stream_response = client.chat.completions.create(
                        model=settings.LLM_MODEL,
                        messages=api_messages,
                        temperature=0.2,
                        stream=True,
                        stream_options={"include_usage": True},
                    )

                    usage_data = {"value": None}

                    def response_chunks():
                        for chunk in stream_response:
                            if chunk.usage is not None:
                                usage_data["value"] = chunk.usage
                            if chunk.choices:
                                content = chunk.choices[0].delta.content
                                if content:
                                    yield content

                    full_response = st.write_stream(response_chunks())
                    duration = time.perf_counter() - start_time

                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )
                usage = usage_data["value"]
                st.session_state.metrics = {
                    "duration": duration,
                    "prompt_tokens": (
                        usage.prompt_tokens
                        if usage
                        else len(
                            " ".join(message["content"] for message in api_messages).split()
                        )
                    ),
                    "completion_tokens": (
                        usage.completion_tokens
                        if usage
                        else len(full_response.split())
                    ),
                }
            except OpenAIError as error:
                st.error(f"No se pudo generar la respuesta: {error}")

with st.sidebar:
    st.header("⚙️ Configuración y Contexto CAG")
    st.text(f"Proveedor: {settings.LLM_PROVIDER.upper()}")
    st.text(f"Modelo: {settings.LLM_MODEL}")
    st.divider()

    with st.expander("📋 Ver System Prompt Activo"):
        st.code(build_system_prompt(), language="markdown")

    with st.expander("📚 Ver Ejemplos Estáticos (CAG Context)"):
        for index, example in enumerate(ESTIMATION_EXAMPLES, start=1):
            st.markdown(f"**Ejemplo {index}:**")
            st.caption(example.get("meeting_summary", "Sin descripción"))

    st.divider()
    if st.session_state.metrics is not None:
        metrics = st.session_state.metrics
        st.subheader("📊 Métricas de la última llamada")
        st.metric("Tiempo de respuesta", f"{metrics['duration']:.2f} s")
        st.metric("Tokens Entrada (aprox.)", metrics["prompt_tokens"])
        st.metric("Tokens Salida (aprox.)", metrics["completion_tokens"])