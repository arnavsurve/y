from typing import List, Optional

from fastapi import APIRouter, Depends, File, UploadFile
from groq import AsyncGroq

from app.db.chroma import VectorStore, get_vector_store
from app.schema import QueryLLMRequest
from app.services.llm import format_prompt, get_groq_client

router = APIRouter()


@router.get("/ping")
async def pong():
    return {"message": "pong"}


@router.post("/query")
async def query(
    request: QueryLLMRequest,
    vector_store: VectorStore = Depends(get_vector_store),
    groq_client: AsyncGroq = Depends(get_groq_client),
) -> dict:
    """
    Query LLM with RAG retrieval.
    """
    # Retrieve global knowledge
    global_context = await vector_store.retrieve_global_knowledge(request.query)

    # Retrieve user documents if user_id is provided
    user_context = (
        await vector_store.retrieve_user_docs(request.user_id, request.query)
        if request.user_id
        else []
    )

    content = format_prompt(user_context, global_context, request.query)

    completion = await groq_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": content,
            }
        ],
        model="llama3-8b-8192",
    )

    res = completion.choices[0].message.content

    return {"message": "Inference successful", "result": res}


@router.post("/upload/user")
async def user_upload(
    user_id: Optional[int] = None,
    files: List[UploadFile] = File(...),
    vector_store: VectorStore = Depends(get_vector_store),
) -> dict:
    """
    Store uploaded documents in user-only vector store.
    """
    return {}


@router.post("/upload/global")
async def global_upload(
    user_id: Optional[int] = None,
    files: List[UploadFile] = File(...),
    vector_store: VectorStore = Depends(get_vector_store),
) -> dict:
    """
    Store uploaded documents in global vector store.
    """
    return {}
