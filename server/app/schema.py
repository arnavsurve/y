from typing import Optional

from pydantic import BaseModel


class QueryLLMRequest(BaseModel):
    user_id: Optional[int] = None
    query: str
