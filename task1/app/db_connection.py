import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from .config import INDEX_NAME, NAMESPACE, PINECONE_CLOUD, PINECONE_REGION


load_dotenv()


class VectorDB:
    def __init__(self, dim: int, metric="cosine"):
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise RuntimeError("PINECONE_API_KEY 필요")
        self.pc = Pinecone(api_key=api_key)
        self.index_name = INDEX_NAME
        self.dim = dim
        self.metric = metric
        self._ensure_index()
        self.index = self.pc.Index(self.index_name)

    def _ensure_index(self):
        existing = {ix["name"] for ix in self.pc.list_indexes().get("indexes", [])}
        if self.index_name not in existing:
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dim,
                metric=self.metric,
                spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION),
                )


    def upsert(self, ids, vectors, metadatas):
        payload = [{"id": i, "values": v, "metadata": m} for i, v, m in zip(ids, vectors, metadatas)]
        self.index.upsert(vectors=payload, namespace=NAMESPACE)
    
    def search(self, query_vector, top_k=5, namespace=None):
        """Search for similar vectors in the index"""
        search_namespace = namespace or NAMESPACE
        response = self.index.query(
            vector=query_vector,
            top_k=top_k,
            namespace=search_namespace,
            include_metadata=True
        )
        return response