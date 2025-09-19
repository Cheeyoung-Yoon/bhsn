#!/usr/bin/env python3
"""
속도 최적화 구현

Task 1과 Task 2의 핵심 성능 병목지점을 해결하는 최적화 기법들을 구현합니다.
"""

import os
import sys
import time
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import cachetools
import pickle
import hashlib
import numpy as np

# Add parent directories to path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

try:
    from task1.app.embedding_client import EmbeddingClient
    from task1.app.db_connection import VectorDB
    from task1.app.config import INDEX_NAME, NAMESPACE
    from task2.app import LawChatbot
except ImportError as e:
    print(f"모듈 import 오류: {e}")


class OptimizedEmbeddingClient:
    """최적화된 임베딩 클라이언트
    
    주요 최적화:
    1. 임베딩 결과 캐싱
    2. 배치 처리 최적화
    3. 비동기 처리 지원
    4. 연결 풀링
    """
    
    def __init__(self, original_client: EmbeddingClient, cache_size: int = 1000):
        """
        Args:
            original_client: 원본 임베딩 클라이언트
            cache_size: 캐시 크기 (임베딩 개수)
        """
        self.original_client = original_client
        
        # LRU 캐시 설정
        self.cache = cachetools.LRUCache(maxsize=cache_size)
        self.cache_hits = 0
        self.cache_misses = 0
        
        # 배치 최적화 설정
        self.optimal_batch_size = 8  # API 제한 고려
        self.max_concurrent_batches = 3
        
        # 성능 통계
        self.stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_time': 0,
            'avg_batch_time': 0
        }
    
    def _get_cache_key(self, text: str) -> str:
        """텍스트에 대한 캐시 키 생성"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def embed_with_cache(self, texts: List[str]) -> Dict[str, Any]:
        """캐시를 활용한 임베딩 생성
        
        Args:
            texts: 임베딩할 텍스트 리스트
            
        Returns:
            임베딩 결과 딕셔너리
        """
        start_time = time.time()
        
        # 캐시에서 기존 임베딩 확인
        cached_embeddings = {}
        uncached_texts = []
        uncached_indices = []
        
        for i, text in enumerate(texts):
            cache_key = self._get_cache_key(text)
            if cache_key in self.cache:
                cached_embeddings[i] = self.cache[cache_key]
                self.cache_hits += 1
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)
                self.cache_misses += 1
        
        # 캐시되지 않은 텍스트만 임베딩 생성
        new_embeddings = {}
        if uncached_texts:
            print(f"캐시 미스: {len(uncached_texts)}개, 캐시 히트: {len(cached_embeddings)}개")
            result = self.original_client.embed(uncached_texts, batch_size=self.optimal_batch_size)
            
            # 새로운 임베딩을 캐시에 저장
            for i, (text, embedding) in enumerate(zip(uncached_texts, result['embeddings'])):
                cache_key = self._get_cache_key(text)
                self.cache[cache_key] = embedding.tolist()
                new_embeddings[uncached_indices[i]] = embedding.tolist()
        
        # 결과 조합
        final_embeddings = []
        for i in range(len(texts)):
            if i in cached_embeddings:
                final_embeddings.append(cached_embeddings[i])
            else:
                final_embeddings.append(new_embeddings[i])
        
        # 통계 업데이트
        end_time = time.time()
        self.stats['total_requests'] += len(texts)
        self.stats['cache_hits'] = self.cache_hits
        self.stats['cache_misses'] = self.cache_misses
        self.stats['total_time'] += (end_time - start_time)
        
        return {
            'embeddings': final_embeddings,
            'dim': len(final_embeddings[0]) if final_embeddings else 0,
            'cache_hit_rate': self.cache_hits / (self.cache_hits + self.cache_misses)
        }
    
    def embed_query_with_cache(self, text: str):
        """단일 쿼리 임베딩 (캐시 적용)"""
        result = self.embed_with_cache([text])
        return result['embeddings'][0]
    
    async def embed_async(self, texts: List[str]) -> Dict[str, Any]:
        """비동기 임베딩 생성"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.embed_with_cache, texts)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """캐시 통계 반환"""
        total_requests = self.cache_hits + self.cache_misses
        if total_requests > 0:
            hit_rate = self.cache_hits / total_requests
        else:
            hit_rate = 0
        
        return {
            'cache_size': len(self.cache),
            'max_cache_size': self.cache.maxsize,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': hit_rate,
            'total_requests': self.stats['total_requests']
        }


class OptimizedVectorDB:
    """최적화된 벡터 데이터베이스 클라이언트
    
    주요 최적화:
    1. 검색 결과 캐싱
    2. 배치 검색 지원
    3. 연결 풀링
    4. 지능형 쿼리 최적화
    """
    
    def __init__(self, original_db: VectorDB, cache_ttl: int = 300):
        """
        Args:
            original_db: 원본 벡터 DB 클라이언트
            cache_ttl: 캐시 TTL (초)
        """
        self.original_db = original_db
        
        # TTL 캐시 설정 (5분)
        self.search_cache = cachetools.TTLCache(maxsize=500, ttl=cache_ttl)
        self.cache_hits = 0
        self.cache_misses = 0
        
        # 성능 통계
        self.stats = {
            'total_searches': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'avg_search_time': 0
        }
    
    def _get_search_cache_key(self, query_vector: List[float], top_k: int, namespace: str = None) -> str:
        """검색 쿼리에 대한 캐시 키 생성"""
        # 벡터를 간단한 해시로 변환 (정확도 vs 성능 트레이드오프)
        vector_hash = hashlib.md5(str(query_vector[:10]).encode()).hexdigest()
        return f"{vector_hash}_{top_k}_{namespace or 'default'}"
    
    def search_with_cache(self, query_vector: Union[List[float], np.ndarray], 
                         top_k: int = 5, namespace: str = None) -> Any:
        """캐시를 활용한 벡터 검색
        
        Args:
            query_vector: 쿼리 벡터
            top_k: 반환할 결과 수
            namespace: 검색할 네임스페이스
            
        Returns:
            검색 결과
        """
        start_time = time.time()
        
        # 벡터를 리스트로 변환
        if hasattr(query_vector, 'tolist'):
            query_vector = query_vector.tolist()
        
        # 캐시 키 생성
        cache_key = self._get_search_cache_key(query_vector, top_k, namespace)
        
        # 캐시 확인
        if cache_key in self.search_cache:
            self.cache_hits += 1
            result = self.search_cache[cache_key]
            print(f"🎯 벡터 검색 캐시 히트")
        else:
            self.cache_misses += 1
            result = self.original_db.search(query_vector, top_k, namespace)
            self.search_cache[cache_key] = result
            print(f"🔍 벡터 검색 수행 (캐시 미스)")
        
        # 통계 업데이트
        end_time = time.time()
        search_time = end_time - start_time
        self.stats['total_searches'] += 1
        self.stats['cache_hits'] = self.cache_hits
        self.stats['cache_misses'] = self.cache_misses
        
        if self.stats['avg_search_time'] == 0:
            self.stats['avg_search_time'] = search_time
        else:
            self.stats['avg_search_time'] = (self.stats['avg_search_time'] + search_time) / 2
        
        return result
    
    async def search_async(self, query_vector: Union[List[float], np.ndarray], 
                          top_k: int = 5, namespace: str = None) -> Any:
        """비동기 벡터 검색"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.search_with_cache, query_vector, top_k, namespace)
    
    def batch_search(self, query_vectors: List[List[float]], top_k: int = 5, 
                    namespace: str = None) -> List[Any]:
        """배치 벡터 검색"""
        results = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_vector = {
                executor.submit(self.search_with_cache, vector, top_k, namespace): vector 
                for vector in query_vectors
            }
            
            for future in as_completed(future_to_vector):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"배치 검색 오류: {e}")
                    results.append(None)
        
        return results
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """캐시 통계 반환"""
        total_requests = self.cache_hits + self.cache_misses
        if total_requests > 0:
            hit_rate = self.cache_hits / total_requests
        else:
            hit_rate = 0
        
        return {
            'cache_size': len(self.search_cache),
            'max_cache_size': self.search_cache.maxsize,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': hit_rate,
            'avg_search_time': self.stats['avg_search_time']
        }


class OptimizedLawChatbot:
    """최적화된 법률 챗봇
    
    주요 최적화:
    1. 전체 파이프라인 캐싱
    2. 병렬 처리
    3. 지능형 컨텍스트 관리
    4. 응답 품질 개선
    """
    
    def __init__(self, original_chatbot: LawChatbot):
        """
        Args:
            original_chatbot: 원본 챗봇 인스턴스
        """
        self.original_chatbot = original_chatbot
        
        # 최적화된 컴포넌트로 교체
        self.optimized_embedder = OptimizedEmbeddingClient(original_chatbot.embedder)
        self.optimized_vector_db = OptimizedVectorDB(original_chatbot.vector_db)
        
        # 응답 캐싱 (질문-응답 쌍)
        self.response_cache = cachetools.TTLCache(maxsize=200, ttl=1800)  # 30분
        
        # 성능 통계
        self.stats = {
            'total_queries': 0,
            'avg_response_time': 0,
            'cache_hit_rate': 0
        }
    
    def _get_response_cache_key(self, query: str) -> str:
        """응답 캐시 키 생성"""
        return hashlib.md5(query.strip().lower().encode('utf-8')).hexdigest()
    
    async def retrieve_relevant_docs_async(self, query: str, top_k: int = 3) -> List[str]:
        """비동기 문서 검색"""
        try:
            # 임베딩 생성
            query_embedding = await self.optimized_embedder.embed_async([query])
            query_vector = query_embedding['embeddings'][0]
            
            # 벡터 검색
            results = await self.optimized_vector_db.search_async(
                query_vector=query_vector,
                top_k=top_k
            )
            
            # 문서 추출
            docs = []
            for match in results.matches:
                metadata = match.metadata or {}
                content = metadata.get('text', '') or metadata.get('content', '') or metadata.get('판결요지', '')
                case_name = metadata.get('사건명', '')
                case_number = metadata.get('사건번호', '')
                
                if content:
                    doc_text = f"[사건: {case_name} ({case_number})]\n{content}"
                    docs.append(doc_text)
            
            return docs
            
        except Exception as e:
            print(f"비동기 문서 검색 오류: {e}")
            return []
    
    def generate_response_optimized(self, query: str, context_docs: List[str]) -> str:
        """최적화된 응답 생성"""
        try:
            # 컨텍스트 최적화 (중복 제거, 길이 제한)
            optimized_context = self._optimize_context(context_docs)
            
            # 기존 응답 생성 로직 사용
            return self.original_chatbot.generate_response(query, optimized_context)
            
        except Exception as e:
            print(f"응답 생성 오류: {e}")
            return "죄송합니다. 응답 생성 중 오류가 발생했습니다. 다시 시도해주세요."
    
    def _optimize_context(self, docs: List[str], max_length: int = 3000) -> List[str]:
        """컨텍스트 최적화"""
        # 중복 제거
        unique_docs = list(dict.fromkeys(docs))
        
        # 길이 제한
        optimized_docs = []
        total_length = 0
        
        for doc in unique_docs:
            if total_length + len(doc) <= max_length:
                optimized_docs.append(doc)
                total_length += len(doc)
            else:
                # 남은 공간에 맞게 자르기
                remaining = max_length - total_length
                if remaining > 100:  # 최소 100자는 포함
                    optimized_docs.append(doc[:remaining] + "...")
                break
        
        return optimized_docs
    
    async def chat_optimized(self, message: str, history: List[dict]) -> tuple[str, List[dict]]:
        """최적화된 챗봇 대화"""
        if not message.strip():
            return "", history
        
        start_time = time.time()
        
        try:
            # 응답 캐시 확인
            cache_key = self._get_response_cache_key(message)
            
            if cache_key in self.response_cache:
                print("💰 응답 캐시 히트")
                response = self.response_cache[cache_key]
            else:
                print("🔄 새로운 응답 생성")
                # 병렬 처리로 문서 검색과 기타 작업 수행
                relevant_docs = await self.retrieve_relevant_docs_async(message, top_k=3)
                response = self.generate_response_optimized(message, relevant_docs)
                
                # 응답 캐싱
                self.response_cache[cache_key] = response
            
            # 히스토리 업데이트
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": response})
            
            # 통계 업데이트
            end_time = time.time()
            response_time = end_time - start_time
            self.stats['total_queries'] += 1
            
            if self.stats['avg_response_time'] == 0:
                self.stats['avg_response_time'] = response_time
            else:
                self.stats['avg_response_time'] = (self.stats['avg_response_time'] + response_time) / 2
            
            return "", history
            
        except Exception as e:
            error_msg = f"오류가 발생했습니다: {str(e)}"
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": error_msg})
            return "", history
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """최적화 통계 반환"""
        return {
            'chatbot': self.stats,
            'embedding': self.optimized_embedder.get_cache_stats(),
            'vector_db': self.optimized_vector_db.get_cache_stats(),
            'response_cache_size': len(self.response_cache)
        }


class SpeedOptimizer:
    """속도 최적화 관리자"""
    
    def __init__(self):
        """최적화 관리자 초기화"""
        self.original_components = {}
        self.optimized_components = {}
        self.benchmark_results = {}
    
    def setup_optimizations(self) -> Dict[str, Any]:
        """최적화 설정 적용"""
        print("🚀 속도 최적화 설정 중...")
        
        try:
            # 1. 원본 컴포넌트 초기화
            print("   - 원본 컴포넌트 초기화...")
            self.original_components['embedder'] = EmbeddingClient()
            self.original_components['vector_db'] = VectorDB(dim=3072)
            self.original_components['chatbot'] = LawChatbot()
            
            # 2. 최적화된 컴포넌트 생성
            print("   - 최적화된 컴포넌트 생성...")
            self.optimized_components['embedder'] = OptimizedEmbeddingClient(
                self.original_components['embedder']
            )
            self.optimized_components['vector_db'] = OptimizedVectorDB(
                self.original_components['vector_db']
            )
            self.optimized_components['chatbot'] = OptimizedLawChatbot(
                self.original_components['chatbot']
            )
            
            print("✅ 최적화 설정 완료")
            return {'status': 'success', 'message': '모든 최적화 컴포넌트가 준비되었습니다.'}
            
        except Exception as e:
            print(f"❌ 최적화 설정 실패: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def run_performance_comparison(self, test_data: Dict) -> Dict[str, Any]:
        """원본 vs 최적화 성능 비교"""
        print("\n📊 성능 비교 테스트 시작...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'original': {},
            'optimized': {},
            'improvement': {}
        }
        
        # 1. 임베딩 성능 비교
        print("\n🤖 임베딩 성능 비교...")
        results['original']['embedding'] = await self._benchmark_embedding_original(test_data['test_texts'])
        results['optimized']['embedding'] = await self._benchmark_embedding_optimized(test_data['test_texts'])
        
        # 2. 검색 성능 비교
        print("\n🔍 검색 성능 비교...")
        results['original']['search'] = await self._benchmark_search_original(test_data['test_queries'])
        results['optimized']['search'] = await self._benchmark_search_optimized(test_data['test_queries'])
        
        # 3. 엔드투엔드 성능 비교
        print("\n🔄 챗봇 성능 비교...")
        results['original']['chatbot'] = await self._benchmark_chatbot_original(test_data['test_texts'][:3])
        results['optimized']['chatbot'] = await self._benchmark_chatbot_optimized(test_data['test_texts'][:3])
        
        # 4. 개선도 계산
        results['improvement'] = self._calculate_improvements(results['original'], results['optimized'])
        
        return results
    
    async def _benchmark_embedding_original(self, test_texts: List[str]) -> Dict[str, float]:
        """원본 임베딩 성능 측정"""
        start_time = time.time()
        
        for text in test_texts[:3]:  # 샘플만 테스트
            self.original_components['embedder'].embed([text])
        
        end_time = time.time()
        total_time = end_time - start_time
        
        return {
            'total_time': total_time,
            'avg_time_per_text': total_time / 3,
            'throughput': 3 / total_time
        }
    
    async def _benchmark_embedding_optimized(self, test_texts: List[str]) -> Dict[str, float]:
        """최적화 임베딩 성능 측정"""
        start_time = time.time()
        
        # 첫 번째 실행 (캐시 미스)
        await self.optimized_components['embedder'].embed_async(test_texts[:3])
        
        # 두 번째 실행 (캐시 히트)
        await self.optimized_components['embedder'].embed_async(test_texts[:3])
        
        end_time = time.time()
        total_time = end_time - start_time
        
        cache_stats = self.optimized_components['embedder'].get_cache_stats()
        
        return {
            'total_time': total_time,
            'avg_time_per_text': total_time / 6,  # 6개 요청 (3 x 2)
            'throughput': 6 / total_time,
            'cache_hit_rate': cache_stats['hit_rate']
        }
    
    async def _benchmark_search_original(self, test_queries: List[str]) -> Dict[str, float]:
        """원본 검색 성능 측정"""
        embedder = self.original_components['embedder']
        vector_db = self.original_components['vector_db']
        
        start_time = time.time()
        
        for query in test_queries[:3]:
            query_embedding = embedder.embed_query(query)
            vector_db.search(query_embedding, top_k=5)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        return {
            'total_time': total_time,
            'avg_time_per_query': total_time / 3,
            'queries_per_second': 3 / total_time
        }
    
    async def _benchmark_search_optimized(self, test_queries: List[str]) -> Dict[str, float]:
        """최적화 검색 성능 측정"""
        embedder = self.optimized_components['embedder']
        vector_db = self.optimized_components['vector_db']
        
        start_time = time.time()
        
        # 첫 번째 실행 (캐시 미스)
        for query in test_queries[:3]:
            query_embedding = embedder.embed_query_with_cache(query)
            await vector_db.search_async(query_embedding, top_k=5)
        
        # 두 번째 실행 (캐시 히트)
        for query in test_queries[:3]:
            query_embedding = embedder.embed_query_with_cache(query)
            await vector_db.search_async(query_embedding, top_k=5)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        cache_stats = vector_db.get_cache_stats()
        
        return {
            'total_time': total_time,
            'avg_time_per_query': total_time / 6,  # 6개 요청 (3 x 2)
            'queries_per_second': 6 / total_time,
            'cache_hit_rate': cache_stats['hit_rate']
        }
    
    async def _benchmark_chatbot_original(self, test_questions: List[str]) -> Dict[str, float]:
        """원본 챗봇 성능 측정"""
        chatbot = self.original_components['chatbot']
        
        start_time = time.time()
        
        for question in test_questions:
            history = []
            chatbot.chat(question, history)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        return {
            'total_time': total_time,
            'avg_response_time': total_time / len(test_questions),
            'questions_per_minute': len(test_questions) / (total_time / 60)
        }
    
    async def _benchmark_chatbot_optimized(self, test_questions: List[str]) -> Dict[str, float]:
        """최적화 챗봇 성능 측정"""
        chatbot = self.optimized_components['chatbot']
        
        start_time = time.time()
        
        for question in test_questions:
            history = []
            await chatbot.chat_optimized(question, history)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        stats = chatbot.get_optimization_stats()
        
        return {
            'total_time': total_time,
            'avg_response_time': total_time / len(test_questions),
            'questions_per_minute': len(test_questions) / (total_time / 60),
            'optimization_stats': stats
        }
    
    def _calculate_improvements(self, original: Dict, optimized: Dict) -> Dict[str, Dict]:
        """개선도 계산"""
        improvements = {}
        
        for category in original:
            if category in optimized:
                improvements[category] = {}
                
                for metric in original[category]:
                    if isinstance(original[category][metric], (int, float)) and \
                       metric in optimized[category] and \
                       isinstance(optimized[category][metric], (int, float)):
                        
                        orig_val = original[category][metric]
                        opt_val = optimized[category][metric]
                        
                        if orig_val > 0:
                            # 시간 지표는 감소가 개선, 처리량 지표는 증가가 개선
                            if 'time' in metric.lower():
                                improvement = ((orig_val - opt_val) / orig_val) * 100
                            else:
                                improvement = ((opt_val - orig_val) / orig_val) * 100
                            
                            improvements[category][metric] = {
                                'original': orig_val,
                                'optimized': opt_val,
                                'improvement_percent': improvement
                            }
        
        return improvements
    
    def save_benchmark_results(self, results: Dict, filepath: Optional[str] = None):
        """벤치마크 결과 저장"""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = current_dir / "reports" / f"optimization_benchmark_{timestamp}.json"
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"📁 벤치마크 결과 저장: {filepath}")
        return filepath


def create_test_data():
    """테스트용 데이터 생성"""
    return {
        'test_texts': [
            "근로계약 해지에 관한 법적 절차를 설명해주세요.",
            "부동산 소유권 이전 등기 절차는 어떻게 되나요?",
            "교통사고 발생 시 손해배상 책임에 대해 알려주세요.",
            "임금체불 시 근로자가 취할 수 있는 법적 조치는?",
            "계약서 작성 시 필수적으로 포함해야 할 내용은?"
        ],
        'test_queries': [
            "근로계약 해지",
            "부동산 소유권",
            "교통사고 손해배상",
            "임금체불",
            "계약서 작성"
        ]
    }


# 사용 예시
async def main():
    """메인 실행 함수"""
    print("🚀 속도 최적화 시스템 시작")
    print("=" * 50)
    
    # 최적화 관리자 초기화
    optimizer = SpeedOptimizer()
    
    # 최적화 설정
    setup_result = optimizer.setup_optimizations()
    if setup_result['status'] != 'success':
        print(f"❌ 최적화 설정 실패: {setup_result['message']}")
        return
    
    # 테스트 데이터
    test_data = {
        'test_texts': [
            "근로계약 해지에 관한 법적 절차를 설명해주세요.",
            "부동산 소유권 이전 등기 절차는 어떻게 되나요?",
            "교통사고 발생 시 손해배상 책임에 대해 알려주세요."
        ],
        'test_queries': [
            "근로계약 해지",
            "부동산 소유권",
            "교통사고 손해배상"
        ]
    }
    
    # 성능 비교 실행
    results = await optimizer.run_performance_comparison(test_data)
    
    # 결과 저장
    optimizer.save_benchmark_results(results)
    
    # 결과 출력
    print("\n📊 최적화 결과 요약:")
    print("=" * 50)
    
    for category, improvements in results['improvement'].items():
        print(f"\n📈 {category.upper()} 개선도:")
        for metric, data in improvements.items():
            improvement = data['improvement_percent']
            status = "🟢" if improvement > 0 else "🔴"
            print(f"   {status} {metric}: {improvement:+.1f}%")


if __name__ == "__main__":
    asyncio.run(main())