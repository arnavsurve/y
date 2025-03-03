from typing import Optional

from fastapi import APIRouter, Depends

from db.chroma import VectorStore, get_vector_store

router = APIRouter()


@router.get("/ping")
async def pong():
    return {"message": "pong"}


@router.post("/query")
async def query(
    query: str,
    user_id: Optional[str] = None,
    vector_store: VectorStore = Depends(get_vector_store),
) -> dict:
    """
    Query
    """
    # Retrieve global knowledge
    global_context = await vector_store.retrieve_global_knowledge(query)

    # Retrieve user documents (if user_id is provided)
    user_context = (
        await vector_store.retrieve_user_docs(user_id, query) if user_id else []
    )

    # Merge retrieved knowledge
    context = "\n\n".join(global_context + user_context)

    return {
        "query": query,
        "retrieved_global_knowledge": global_context,
        "retrieved_user_documents": user_context,
        "full_context": context,
    }
