import os, time
import numpy as np
from typing import Any, Dict, List, Sequence
from dotenv import load_dotenv
from google.genai import Client
from tqdm import tqdm



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
        print(f"Processing embeddings: {len(texts)} texts")
        
        for i, t in enumerate(tqdm(texts, desc="Generating embeddings", unit="text")):
            max_retries = 3
            retry_delay = 2.0
            
            for attempt in range(max_retries):
                try:
                    print(f"Processing: {i+1}/{len(texts)} - attempt {attempt+1}")
                    resp = self.client.models.embed_content(model=self.model, contents=t)
                    vecs.append(resp.embeddings[0].values)
                    print(f"Success: {i+1}/{len(texts)}")
                    # Add delay to avoid rate limiting
                    time.sleep(1.5)  # Increased delay to 1.5 seconds
                    break
                except Exception as e:
                    print(f"Error occurred (attempt {attempt+1}/{max_retries}): {e}")
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        print(f"Rate limit exceeded. Waiting {retry_delay}s before retry...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    elif attempt == max_retries - 1:
                        print(f"Max retries exceeded. Using zero vector")
                        # Return zero vector on error
                        vecs.append([0.0] * 768)  # Assuming 768-dimensional embeddings
                    else:
                        time.sleep(retry_delay)
        
        print(f"Embedding complete: {len(vecs)} vectors generated")
        return vecs


    def embed(self, texts: Sequence[str], batch_size=16) -> Dict[str, Any]:
        print(f"Starting embeddings: {len(texts)} texts, batch size: {batch_size}")
        all_vecs = []
        
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        for i in tqdm(range(0, len(texts), batch_size), desc="Processing batches", total=total_batches):
            batch_num = i // batch_size + 1
            chunk = texts[i:i+batch_size]
            print(f"\nProcessing batch {batch_num}/{total_batches} ({len(chunk)} texts)")
            
            batch_vecs = self._embed_once(chunk)
            all_vecs.extend(batch_vecs)
            
            print(f"Batch {batch_num} complete. Total: {len(all_vecs)} vectors")
            
            # Add delay between batches to avoid rate limiting
            if i + batch_size < len(texts):
                print("Waiting 3s before next batch...")
                time.sleep(3.0)
        
        arr = np.array(all_vecs, dtype=np.float32)
        if self.normalize:
            print("Normalizing vectors...")
            arr = self._l2_normalize(arr)
            print("Normalization complete")
        
        print(f"Final result: {arr.shape[0]} vectors, dimension: {arr.shape[1]}")
        return {"embeddings": arr, "dim": arr.shape[1]}


    def embed_query(self, text: str):
        print("Query embedding generation...")
        result = self.embed([text])["embeddings"][0]
        print("Query embedding complete")
        return result


    @staticmethod
    def _l2_normalize(x: np.ndarray, eps=1e-12):
        norm = np.linalg.norm(x, axis=1, keepdims=True)
        return x / np.maximum(norm, eps)