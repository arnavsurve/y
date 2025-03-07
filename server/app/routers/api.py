from typing import List, Optional

from fastapi import (APIRouter, Depends, File, Form, HTTPException, Request,
                     UploadFile)
from google import genai
from groq import AsyncGroq

from app.db.chroma import VectorStore, get_vector_store
from app.schema import QueryLLMRequest
from app.services.llm import (extract_text_from_image, format_prompt,
                              format_vibe_check_prompt, get_gemini_client,
                              get_groq_client)

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

    res = ""

    try:
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
    except Exception as e:
        print("Error querying groq api: ", e)
        raise HTTPException(status_code=500, detail="Unexpected error in querying LLM")

    return {"message": "Completion successful", "result": res}


@router.post("/query/vibe")
async def vibe_check_query(
    query: Optional[str] = Form(None),
    images: Optional[List[UploadFile]] = File(None),
    # vector_store: VectorStore = Depends(get_vector_store),
    groq_client: AsyncGroq = Depends(get_groq_client),
    gemini_client: genai.Client = Depends(get_gemini_client),
) -> dict:
    """
    Query LLM for a vibe check with optional OCR-extracted text from images.
    """

    # Extract text from images if provided
    ocr_text = await extract_text_from_image(gemini_client, images) if images else None

    # # Retrieve RAG-based knowledge
    # global_context = await vector_store.retrieve_global_knowledge(request.query)
    # user_context = (
    #     await vector_store.retrieve_user_docs(request.user_id, request.query)
    #     if request.user_id
    #     else []
    # )

    # Format prompt for the vibe check
    content = format_vibe_check_prompt(user_prompt=query, ocr_text=ocr_text)
    try:
        # completion = await groq_client.chat.completions.create(
        #     messages=[{"role": "user", "content": content}],
        #     model="llama3-8b-8192",
        # )
        # response_text = completion.choices[0].message.content
        response = gemini_client.models.generate_content(
            model="gemini-2.0-pro-exp-02-05",
            contents=content,
        )
    except Exception as e:
        print("Error querying Groq API:", e)
        raise HTTPException(status_code=500, detail="Unexpected error in querying LLM")

    return {"message": "Vibe check complete", "result": response}


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
