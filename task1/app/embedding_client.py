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
        print(f"🔄 임베딩 처리 중: {len(texts)}개 텍스트")
        
        for i, t in enumerate(tqdm(texts, desc="임베딩 생성", unit="text")):
            max_retries = 3
            retry_delay = 2.0
            
            for attempt in range(max_retries):
                try:
                    print(f"📝 처리 중: {i+1}/{len(texts)} - 시도 {attempt+1}")
                    resp = self.client.models.embed_content(model=self.model, contents=t)
                    vecs.append(resp.embeddings[0].values)
                    print(f"✅ 성공: {i+1}/{len(texts)}")
                    # Add delay to avoid rate limiting
                    time.sleep(1.5)  # Increased delay to 1.5 seconds
                    break
                except Exception as e:
                    print(f"❌ 오류 발생 (시도 {attempt+1}/{max_retries}): {e}")
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        print(f"⏳ 할당량 초과. {retry_delay}초 대기 후 재시도...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    elif attempt == max_retries - 1:
                        print(f"💀 최대 재시도 횟수 초과. 영벡터로 대체")
                        # Return zero vector on error
                        vecs.append([0.0] * 768)  # Assuming 768-dimensional embeddings
                    else:
                        time.sleep(retry_delay)
        
        print(f"🎉 임베딩 완료: {len(vecs)}개 벡터 생성")
        return vecs


    def embed(self, texts: Sequence[str], batch_size=16) -> Dict[str, Any]:
        print(f"🚀 임베딩 시작: 총 {len(texts)}개 텍스트, 배치 크기: {batch_size}")
        all_vecs = []
        
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        for i in tqdm(range(0, len(texts), batch_size), desc="배치 처리", total=total_batches):
            batch_num = i // batch_size + 1
            chunk = texts[i:i+batch_size]
            print(f"\n📦 배치 {batch_num}/{total_batches} 처리 중 ({len(chunk)}개 텍스트)")
            
            batch_vecs = self._embed_once(chunk)
            all_vecs.extend(batch_vecs)
            
            print(f"✅ 배치 {batch_num} 완료. 누적: {len(all_vecs)}개 벡터")
            
            # Add delay between batches to avoid rate limiting
            if i + batch_size < len(texts):
                print("⏳ 다음 배치 전 3초 대기...")
                time.sleep(3.0)
        
        arr = np.array(all_vecs, dtype=np.float32)
        if self.normalize:
            print("🔧 벡터 정규화 중...")
            arr = self._l2_normalize(arr)
            print("✅ 정규화 완료")
        
        print(f"🎯 최종 결과: {arr.shape[0]}개 벡터, 차원: {arr.shape[1]}")
        return {"embeddings": arr, "dim": arr.shape[1]}


    def embed_query(self, text: str):
        print(f"🔍 쿼리 임베딩 생성 중...")
        result = self.embed([text])["embeddings"][0]
        print(f"✅ 쿼리 임베딩 완료")
        return result


    @staticmethod
    def _l2_normalize(x: np.ndarray, eps=1e-12):
        norm = np.linalg.norm(x, axis=1, keepdims=True)
        return x / np.maximum(norm, eps)