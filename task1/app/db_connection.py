import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from .config import INDEX_NAME, NAMESPACE, PINECONE_CLOUD, PINECONE_REGION


load_dotenv()


class VectorDB:
    def __init__(self, dim: int, metric="cosine"):
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise RuntimeError("PINECONE_API_KEY required")
        self.pc = Pinecone(api_key=api_key)
        self.index_name = INDEX_NAME
        self.dim = dim
        self.metric = metric
        self._ensure_index()
        self.index = self.pc.Index(self.index_name)

    def _ensure_index(self):
        existing = {ix["name"] for ix in self.pc.list_indexes().get("indexes", [])}
        if self.index_name not in existing:
            print(f"Creating index '{self.index_name}' (dimension: {self.dim})")
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dim,
                metric=self.metric,
                spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION),
                )
            print(f"Index creation complete")
        else:
            # Check existing index dimension
            index = self.pc.Index(self.index_name)
            stats = index.describe_index_stats()
            existing_dim = stats.get('dimension')
            
            if existing_dim != self.dim:
                print(f"Dimension mismatch detected!")
                print(f"   Existing: {existing_dim}D, Required: {self.dim}D")
                print(f"Deleting existing index...")
                self.pc.delete_index(self.index_name)
                
                # Wait for deletion
                import time
                print("Waiting for deletion to complete...")
                time.sleep(10)
                
                print(f"Creating new index (dimension: {self.dim})")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dim,
                    metric=self.metric,
                    spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION),
                )
                print(f"Index recreation complete")
            else:
                print(f"Using existing index (dimension: {existing_dim})")


    def upsert(self, ids, vectors, metadatas):
        payload = [{"id": i, "values": v, "metadata": m} for i, v, m in zip(ids, vectors, metadatas)]
        self.index.upsert(vectors=payload, namespace=NAMESPACE)
    
    def search(self, query_vector, top_k=5, namespace=None):
        """Search for similar vectors in the index"""
        search_namespace = namespace or NAMESPACE
        
        # Convert numpy array to list if necessary
        if hasattr(query_vector, 'tolist'):
            query_vector = query_vector.tolist()
        
        response = self.index.query(
            vector=query_vector,
            top_k=top_k,
            namespace=search_namespace,
            include_metadata=True
        )
        return response