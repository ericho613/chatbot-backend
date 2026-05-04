def test_rag_non_streaming(client, auth_headers):
    response = client.post(
        "/rag",
        headers=auth_headers,
        json={
            "query": "What are the main findings?",
            "stream": False,
            "top_k": 2,
            "generation_config": {
                "max_tokens": 500,
                "temperature": 0.4,
                "top_p": 1.0,
            },
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["model"] == "fake-model"
    assert data["response"] == "This is a fake RAG response based on retrieved chunks."
    assert len(data["retrieved_chunks"]) == 2


def test_rag_streaming(client, auth_headers):
    with client.stream(
        "POST",
        "/rag",
        headers=auth_headers,
        json={
            "query": "Stream the RAG answer",
            "stream": True,
            "top_k": 2,
            "generation_config": {
                "max_tokens": 500,
                "temperature": 0.4,
                "top_p": 1.0,
            },
        },
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/x-ndjson")
        body = "".join([chunk.decode() if isinstance(chunk, bytes) else chunk for chunk in response.iter_text()])
        assert '"type": "chunk"' in body
        assert '"type": "done"' in body


def test_rag_validation_error(client, auth_headers):
    response = client.post(
        "/rag",
        headers=auth_headers,
        json={
            "query": "Invalid top_k",
            "stream": False,
            "top_k": 0,
            "generation_config": {
                "max_tokens": 500,
                "temperature": 0.4,
                "top_p": 1.0,
            },
        },
    )

    assert response.status_code == 422