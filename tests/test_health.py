def test_health_endpoint_returns_service_status(client):
    """RED: el servicio debe indicar que está saludable."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "estimador-cag",
        "version": "0.1.0",
    }


def test_health_endpoint_returns_json_content_type(client):
    """Refactor: la respuesta debe ser JSON con content-type correcto."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
