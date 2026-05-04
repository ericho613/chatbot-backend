def test_pdf_summary_non_streaming(client, auth_headers, sample_pdf_bytes, mock_pdf_text):
    response = client.post(
        "/pdf/summary",
        headers=auth_headers,
        files={"file": ("sample.pdf", sample_pdf_bytes, "application/pdf")},
        data={
            "stream": "false",
            "generation_config": '{"max_tokens":1000,"temperature":0.5,"top_p":1.0}',
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["summary"] == "This is a fake summary."
    assert data["filename"] == "sample.pdf"


def test_pdf_summary_streaming(client, auth_headers, sample_pdf_bytes, mock_pdf_text):
    with client.stream(
        "POST",
        "/pdf/summary",
        headers=auth_headers,
        files={"file": ("sample.pdf", sample_pdf_bytes, "application/pdf")},
        data={
            "stream": "true",
            "generation_config": '{"max_tokens":1000,"temperature":0.5,"top_p":1.0}',
        },
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/x-ndjson")
        body = "".join([chunk.decode() if isinstance(chunk, bytes) else chunk for chunk in response.iter_text()])
        assert '"type": "chunk"' in body
        assert '"type": "done"' in body


def test_pdf_citation_apa(client, auth_headers, sample_pdf_bytes, mock_pdf_text):
    response = client.post(
        "/pdf/citation",
        headers=auth_headers,
        files={"file": ("paper.pdf", sample_pdf_bytes, "application/pdf")},
        data={
            "citation_style": "APA",
            "stream": "false",
            "generation_config": '{"max_tokens":400,"temperature":0.2,"top_p":1.0}',
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["citation_style"] == "APA"
    assert "Doe, J." in data["citation"]


def test_pdf_citation_mla(client, auth_headers, sample_pdf_bytes, mock_pdf_text):
    response = client.post(
        "/pdf/citation",
        headers=auth_headers,
        files={"file": ("paper.pdf", sample_pdf_bytes, "application/pdf")},
        data={
            "citation_style": "MLA",
            "stream": "false",
            "generation_config": '{"max_tokens":400,"temperature":0.2,"top_p":1.0}',
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["citation_style"] == "MLA"


def test_pdf_citation_invalid_style(client, auth_headers, sample_pdf_bytes, mock_pdf_text):
    response = client.post(
        "/pdf/citation",
        headers=auth_headers,
        files={"file": ("paper.pdf", sample_pdf_bytes, "application/pdf")},
        data={
            "citation_style": "IEEE",
            "stream": "false",
            "generation_config": '{"max_tokens":400,"temperature":0.2,"top_p":1.0}',
        },
    )

    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False


def test_pdf_upload_to_vector_db(client, auth_headers, sample_pdf_bytes, mock_pdf_text):
    response = client.post(
        "/pdf/upload",
        headers=auth_headers,
        files={"file": ("paper.pdf", sample_pdf_bytes, "application/pdf")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["filename"] == "paper.pdf"
    assert data["chunks_indexed"] > 0
    assert data["citation"] == "APA citation"
    assert data["vector_backend"] == "fake-vector-store"


def test_pdf_upload_invalid_extension(client, auth_headers):
    response = client.post(
        "/pdf/upload",
        headers=auth_headers,
        files={"file": ("not_pdf.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False