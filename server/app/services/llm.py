from typing import List

from groq import AsyncGroq

from app.config import settings


async def get_groq_client() -> AsyncGroq:
    return AsyncGroq(api_key=settings.groq_api_key)


def format_prompt(
    user_rag_context: List[str], global_rag_context: List[str], query: str
) -> str:
    return f"""
### System Instruction ###
You are an AI assistant that provides helpful, context-aware, and personalized responses.
You will be given:
1. **User-Specific RAG Context**: Information retrieved from the user's own documents.
2. **Global RAG Context**: Knowledge retrieved from external sources.
3. **User Query**: The user's actual request.

Your goal is to generate a response that:
- Prioritizes **User-Specific RAG Context** to ensure personalization and relevance.
- Supplements with **Global RAG Context** if additional information is needed.
- Directly addresses the **User Query** in a **clear, concise, and informative manner**.
- If conflicts exist between **User-Specific** and **Global RAG Context**, prioritize the **User-Specific Context** unless explicitly instructed otherwise.

### User-Specific RAG Context ###
{user_rag_context}

### Global RAG Context ###
{global_rag_context}

### User Query ###
{query}

### Response ###
(Your answer here)
""".strip()
