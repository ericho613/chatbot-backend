def test_create_token_success(client, monkeypatch):
    from app.config import get_settings
    settings = get_settings()

    monkeypatch.setattr(settings, "DEMO_AUTH_USERNAME", "admin", raising=False)
    monkeypatch.setattr(settings, "DEMO_AUTH_PASSWORD", "password", raising=False)

    response = client.post(
        "/auth/token",
        json={"username": "admin", "password": "password"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_create_token_failure(client, monkeypatch):
    from app.config import get_settings
    settings = get_settings()

    monkeypatch.setattr(settings, "DEMO_AUTH_USERNAME", "admin", raising=False)
    monkeypatch.setattr(settings, "DEMO_AUTH_PASSWORD", "password", raising=False)

    response = client.post(
        "/auth/token",
        json={"username": "wrong", "password": "wrong"},
    )

    assert response.status_code == 401