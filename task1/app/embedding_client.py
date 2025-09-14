import os, time
import numpy as np
from typing import Any, Dict, List, Sequence
from dotenv import load_dotenv
from google.genai import Client



class EmbeddingClient:
    def __init__(self, model="gemini-embedding-001", api_key_env="GOOGLE_API_KEY", normalize=True):
        # Load environment variables from the correct path
        env_path = os.path.join(os.path.dirname(__file__), '..', '..', 'env', '.env')
        load_dotenv(env_path)
        api_key = os.getenv(api_key_env)
        if not api_key:
            raise RuntimeError(f"환경변수 {api_key_env}가 비어 있습니다")
        self.client = Client(api_key=api_key)
        self.model = model
        self.normalize = normalize


    def _embed_once(self, texts: Sequence[str]) -> List[List[float]]:
        vecs = []
        for t in texts:
            try:
                resp = self.client.models.embed_content(model=self.model, contents=t)
                vecs.append(resp.embeddings[0].values)
                # Add delay to avoid rate limiting
                time.sleep(0.1)  # 100ms delay between requests
            except Exception as e:
                print(f"Error embedding text: {e}")
                # Return zero vector on error
                vecs.append([0.0] * 768)  # Assuming 768-dimensional embeddings
        return vecs


    def embed(self, texts: Sequence[str], batch_size=16) -> Dict[str, Any]:
        all_vecs = []
        for i in range(0, len(texts), batch_size):
            chunk = texts[i:i+batch_size]
            all_vecs.extend(self._embed_once(chunk))
        arr = np.array(all_vecs, dtype=np.float32)
        if self.normalize:
            arr = self._l2_normalize(arr)
        return {"embeddings": arr, "dim": arr.shape[1]}


    def embed_query(self, text: str):
        return self.embed([text])["embeddings"][0]


    @staticmethod
    def _l2_normalize(x: np.ndarray, eps=1e-12):
        norm = np.linalg.norm(x, axis=1, keepdims=True)
        return x / np.maximum(norm, eps)