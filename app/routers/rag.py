from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.dependencies import optional_jwt_auth
from app.models import ChatMessage, RagRequest, RagResponse
from app.services.factory import get_ai_service, get_embedding_service, get_vector_store
from app.utils.streaming import json_line_stream
import json

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("", response_model=RagResponse)
async def rag_chat(
    request: RagRequest,
    _user=Depends(optional_jwt_auth),
):
    ai_service = get_ai_service()
    embedding_service = get_embedding_service()
    vector_store = get_vector_store()

    query_embedding = embedding_service.embed_query(request.query)
    retrieved_data = vector_store.search(query_embedding, request.top_k)

    # context = "\n\n---\n\n".join(retrieved_chunks) if retrieved_chunks else ""
    context = json.dumps(retrieved_data, indent=4) if retrieved_data else ""

    messages = [
        ChatMessage(
            role="system",
            content=(
f'''You are a scientific expert that can communicate simply, clearly, and concisely.

Provide a detailed answer for the following question:
{request.query}

To answer the question, ONLY use the following context if relevant.  If no context is provided, say "The information is not available":
{context}

If any resource in the context is used, then at the end of the response, specify the full citation for the resource in the format:

References:

*Citations*

where *Citations* should be substituted with the citations as an alphabetically ordered list.

If no resource in the context is used, then do not include the "References" section.
'''
            ),
        ),
        # ChatMessage(
        #     role="user",
        #     content=f"Question:\n{request.query}",
        # ),
    ]
    
    if request.stream:
        generator = ai_service.stream_text(messages, request.generation_config)
        return StreamingResponse(
            json_line_stream(generator),
            media_type="application/x-ndjson",
        )

    response_text = await ai_service.generate_text(messages, request.generation_config)
    return RagResponse(
        success=True,
        model=ai_service.model_name(),
        response=response_text,
        retrieved_chunks=[data.document for data in retrieved_data if data.document],
    )