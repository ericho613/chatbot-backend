import json
from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import StreamingResponse

from app.config import get_settings
from app.dependencies import optional_jwt_auth
from app.exceptions import ValidationException
from app.models import ChatMessage, CitationResponse, GenerationConfig, SummaryResponse, UploadResponse
from app.services.factory import get_ai_service, get_embedding_service, get_vector_store
from app.utils.pdf_utils import extract_text_from_pdf_bytes, chunk_text
from app.utils.streaming import json_line_stream
from app.utils.text_utils import truncate_text

router = APIRouter(prefix="/pdf", tags=["pdf"])


async def _read_pdf(file: UploadFile) -> bytes:
    settings = get_settings()

    if not file.filename.lower().endswith(".pdf"):
        raise ValidationException("Uploaded file must be a .pdf file")

    data = await file.read()
    if len(data) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise ValidationException(f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB} MB")

    return data


@router.post("/summary", response_model=SummaryResponse)
async def summarize_pdf(
    file: UploadFile = File(...),
    summary_language: str = Form("English"),
    stream: bool = Form(False),
    generation_config: str = Form('{"max_tokens":1000,"temperature":0.7,"top_p":1.0}'),
    _user=Depends(optional_jwt_auth),
):
    """
    Upload a PDF and generate a summary in the requested language.
    Supported summary_language values: English, French
    """
    settings = get_settings()
    ai_service = get_ai_service()

    normalized_language = summary_language.strip().capitalize()
    if normalized_language not in {"English", "French"}:
        raise ValidationException("summary_language must be English or French")

    pdf_bytes = await _read_pdf(file)
    pdf_text = extract_text_from_pdf_bytes(pdf_bytes)
    pdf_text = truncate_text(pdf_text, settings.MAX_INPUT_TEXT_CHARS)
    gen_cfg = GenerationConfig.model_validate(json.loads(generation_config))

    messages = [
        ChatMessage(
            role="system",
            content=(
                f"You are a helpful assistant that summarizes PDF documents clearly, accurately, and concisely. "
                f"You must write the summary in {normalized_language}."
            ),
        ),
        ChatMessage(
            role="user",
            content=(
                f"Please summarize the following PDF content in {normalized_language}.\n\n"
                f"PDF content:\n{pdf_text}"
            ),
        ),
    ]

    if stream:
        generator = ai_service.stream_text(messages, gen_cfg)
        return StreamingResponse(
            json_line_stream(generator),
            media_type="application/x-ndjson",
        )

    summary = await ai_service.generate_text(messages, gen_cfg)
    return SummaryResponse(
        success=True,
        model=ai_service.model_name(),
        summary=summary,
        filename=file.filename,
    )


@router.post("/citation", response_model=CitationResponse)
async def generate_citation(
    file: UploadFile = File(...),
    citation_style: str = Form(...),
    stream: bool = Form(False),
    generation_config: str = Form('{"max_tokens":500,"temperature":0.2,"top_p":1.0}'),
    _user=Depends(optional_jwt_auth),
):
    settings = get_settings()
    ai_service = get_ai_service()

    style = citation_style.strip().upper()
    if style not in {"APA", "MLA"}:
        raise ValidationException("citation_style must be APA or MLA")

    pdf_bytes = await _read_pdf(file)
    pdf_text = extract_text_from_pdf_bytes(pdf_bytes)
    pdf_text = truncate_text(pdf_text, settings.MAX_INPUT_TEXT_CHARS)
    gen_cfg = GenerationConfig.model_validate(json.loads(generation_config))

    messages = [
        ChatMessage(
            role="system",
            content=(
                "You generate scientific citations. "
                "Output only the citation text in the requested style. "
                "If some metadata is missing, infer conservatively from the document."
            ),
        ),
        ChatMessage(
            role="user",
            content=f"Generate a {style} citation for this PDF content:\n\n{pdf_text}",
        ),
    ]

    if stream:
        generator = ai_service.stream_text(messages, gen_cfg)
        return StreamingResponse(
            json_line_stream(generator),
            media_type="application/x-ndjson",
        )

    citation = await ai_service.generate_text(messages, gen_cfg)

    return CitationResponse(
        success=True,
        model=ai_service.model_name(),
        citation_style=style,
        citation=citation,
        filename=file.filename,
    )


@router.post("/upload", response_model=UploadResponse)
async def upload_pdf_to_vector_db(
    file: UploadFile = File(...),
    generation_config: str = Form('{"max_tokens":500,"temperature":0.2,"top_p":1.0}'),
    _user=Depends(optional_jwt_auth),
):
    settings = get_settings()
    embedding_service = get_embedding_service()
    vector_store = get_vector_store()

    pdf_bytes = await _read_pdf(file)
    pdf_text = extract_text_from_pdf_bytes(pdf_bytes)
    pdf_text = truncate_text(pdf_text, settings.MAX_INPUT_TEXT_CHARS)
    gen_cfg = GenerationConfig.model_validate(json.loads(generation_config))

    messages = [
        ChatMessage(
            role="system",
            content=(
                "You generate scientific citations. "
                "Output only the citation text in the requested style. "
                "If some metadata is missing, infer conservatively from the document."
            ),
        ),
        ChatMessage(
            role="user",
            content=f"Generate an APA citation for this PDF content:\n\n{pdf_text}",
        ),
    ]

    ai_service = get_ai_service()
    citation = await ai_service.generate_text(messages, gen_cfg)

    chunks = chunk_text(
        pdf_text,
        chunk_size=settings.DEFAULT_CHUNK_SIZE,
        chunk_overlap=settings.DEFAULT_CHUNK_OVERLAP,
    )

    if not chunks:
        raise ValidationException("No chunks could be created from the PDF")

    embeddings = embedding_service.embed_texts(chunks)
    count = vector_store.add_document_chunks(
        filename=file.filename,
        chunks=chunks,
        embeddings=embeddings,
        citation=citation
    )

    return UploadResponse(
        success=True,
        message="PDF uploaded and indexed successfully",
        filename=file.filename,
        chunks_indexed=count,
        citation=citation,
        vector_backend=vector_store.backend_name(),
    )