from contextlib import asynccontextmanager

from sentence_transformers import SentenceTransformer

import chromadb
from app.config import settings


class VectorStore:
    """
    Handles vector embedding and storage in ChromaDB.
    """

    def __init__(self, chroma_client, embedding_model, global_store, user_store):
        self.chroma_client = chroma_client
        self.embedding_model = embedding_model
        self.global_store = global_store
        self.user_store = user_store

    @classmethod
    async def create(cls, chroma_client):
        """
        Async factory method to initialize VectorStore.
        """
        embedding_model = SentenceTransformer("BAAI/bge-m3")

        global_store = await chroma_client.get_or_create_collection(name="global_store")
        user_store = await chroma_client.get_or_create_collection(name="user_store")

        return cls(chroma_client, embedding_model, global_store, user_store)

    async def embed_text(self, text: str):
        """
        Generate embeddings for a given text.
        """
        return self.embedding_model.encode(text)

    async def index_global_knowledge(self, doc_text: str):
        """
        Store external knowledge in the global vector DB.
        """
        vector = await self.embed_text(doc_text)
        await self.global_store.add(documents=[{"text": doc_text}], embeddings=[vector])

    async def index_user_doc(self, user_id: str, doc_text: str):
        """
        Store user-uploaded documents in the user vector DB.
        """
        vector = await self.embed_text(doc_text)
        await self.user_store.add(
            documents=[{"user_id": user_id, "text": doc_text}], embeddings=[vector]
        )

    async def retrieve_global_knowledge(self, query: str, top_k: int = 3):
        """
        Retrieve relevant external knowledge based on query.
        """
        query_vector = await self.embed_text(query)
        results = await self.global_store.query(
            query_embeddings=[query_vector], n_results=top_k
        )

        if not results or "documents" not in results or not results["documents"]:
            return []

        return [doc["text"] for doc in results["documents"][0]]

    async def retrieve_user_docs(self, user_id: str, query: str, top_k: int = 3):
        """
        Retrieve relevant user-specific documents.
        """
        query_vector = await self.embed_text(query)
        results = await self.user_store.query(
            query_embeddings=[query_vector], n_results=top_k
        )

        if not results or "documents" not in results or not results["documents"]:
            return []

        return [
            doc["text"]
            for doc in results["documents"][0]
            if "user_id" in doc and doc["user_id"] == user_id
        ]


@asynccontextmanager
async def get_chroma_client():
    client = await chromadb.AsyncHttpClient(host="chromadb", port=settings.chroma_port)
    try:
        yield client
    finally:
        pass


async def get_vector_store():
    """
    Dependency injection for ChromaDB vector store.
    """
    async with get_chroma_client() as chroma_client:
        vector_store = await VectorStore.create(chroma_client)
        yield vector_store
