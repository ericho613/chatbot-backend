def test_chat_non_streaming_no_auth_when_disabled(client, monkeypatch):
    from app.config import get_settings
    settings = get_settings()
    monkeypatch.setattr(settings, "ENABLE_JWT_AUTH", False, raising=False)

    response = client.post(
        "/chat",
        json={
            "messages": [
                {"role": "user", "content": "Hello chatbot"}
            ],
            "stream": False,
            "generation_config": {
                "max_tokens": 100,
                "temperature": 0.7,
                "top_p": 1.0,
            },
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["model"] == "fake-model"
    assert data["response"] == "This is a fake chat response."


def test_chat_non_streaming_auth_required(client, monkeypatch):
    from app.config import get_settings
    settings = get_settings()
    monkeypatch.setattr(settings, "ENABLE_JWT_AUTH", True, raising=False)

    response = client.post(
        "/chat",
        json={
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": False,
            "generation_config": {"max_tokens": 100, "temperature": 0.7, "top_p": 1.0},
        },
    )

    assert response.status_code == 401


def test_chat_non_streaming_with_auth(client, auth_headers):
    response = client.post(
        "/chat",
        headers=auth_headers,
        json={
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": False,
            "generation_config": {"max_tokens": 100, "temperature": 0.7, "top_p": 1.0},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["response"] == "This is a fake chat response."


def test_chat_streaming_with_auth(client, auth_headers):
    with client.stream(
        "POST",
        "/chat",
        headers=auth_headers,
        json={
            "messages": [{"role": "user", "content": "Stream please"}],
            "stream": True,
            "generation_config": {"max_tokens": 100, "temperature": 0.7, "top_p": 1.0},
        },
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/x-ndjson")
        body = "".join([chunk.decode() if isinstance(chunk, bytes) else chunk for chunk in response.iter_text()])
        assert '"type": "chunk"' in body
        assert '"type": "done"' in body


def test_chat_validation_error(client, monkeypatch):
    from app.config import get_settings
    settings = get_settings()
    monkeypatch.setattr(settings, "ENABLE_JWT_AUTH", False, raising=False)

    response = client.post(
        "/chat",
        json={
            "messages": [
                {"role": "invalid-role", "content": "Hello"}
            ],
            "stream": False,
        },
    )

    assert response.status_code == 422