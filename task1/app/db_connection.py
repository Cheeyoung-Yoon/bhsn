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
            print(f"🏗️  인덱스 '{self.index_name}' 생성 중 (차원: {self.dim})")
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dim,
                metric=self.metric,
                spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION),
                )
            print(f"✅ 인덱스 생성 완료")
        else:
            # 기존 인덱스의 차원 확인
            index = self.pc.Index(self.index_name)
            stats = index.describe_index_stats()
            existing_dim = stats.get('dimension')
            
            if existing_dim != self.dim:
                print(f"⚠️  차원 불일치 감지!")
                print(f"   기존: {existing_dim}차원, 요구: {self.dim}차원")
                print(f"🗑️  기존 인덱스 삭제 중...")
                self.pc.delete_index(self.index_name)
                
                # 삭제 대기
                import time
                print("⏳ 삭제 완료 대기 중...")
                time.sleep(10)
                
                print(f"🏗️  새 인덱스 생성 중 (차원: {self.dim})")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dim,
                    metric=self.metric,
                    spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION),
                )
                print(f"✅ 인덱스 재생성 완료")
            else:
                print(f"✅ 기존 인덱스 사용 (차원: {existing_dim})")


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