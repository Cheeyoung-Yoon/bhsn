#!/usr/bin/env python3
"""
성능 분석기 모듈

벡터 데이터베이스와 RAG 시스템의 정량적 성능을 분석합니다.
"""

import os
import sys
import time
import json
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import traceback

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from task1.app.embedding_client import EmbeddingClient
    from task1.app.db_connection import VectorDB
    from task1.app.parser import parse_cases
    from task1.app.config import DATA_JSON
except ImportError as e:
    print(f"Task 1 모듈 import 오류: {e}")


class PerformanceAnalyzer:
    """시스템 성능 분석 클래스"""
    
    def __init__(self):
        """성능 분석기 초기화"""
        self.embedder = None
        self.vector_db = None
        self.test_cases = []
        self.results = {}
        
    def initialize_components(self):
        """시스템 컴포넌트 초기화"""
        try:
            print("🔧 시스템 컴포넌트 초기화 중...")
            
            # 임베딩 클라이언트 초기화
            self.embedder = EmbeddingClient()
            print("   ✅ 임베딩 클라이언트 초기화 완료")
            
            # 벡터 데이터베이스 초기화
            self.vector_db = VectorDB(dim=3072)  # Google Gemini embedding dimension
            print("   ✅ 벡터 데이터베이스 연결 완료")
            
            return True
            
        except Exception as e:
            print(f"   ❌ 컴포넌트 초기화 실패: {e}")
            return False
    
    def load_test_data(self):
        """테스트 데이터 로드"""
        try:
            print("📚 테스트 데이터 로드 중...")
            
            # 케이스 데이터 파싱
            records = parse_cases(DATA_JSON)
            self.test_cases = records[:10]  # 처음 10개 케이스만 사용
            
            print(f"   ✅ {len(self.test_cases)}개 테스트 케이스 로드 완료")
            return True
            
        except Exception as e:
            print(f"   ❌ 테스트 데이터 로드 실패: {e}")
            return False
    
    def analyze_embedding_performance(self) -> Dict:
        """임베딩 성능 분석"""
        print("\n🔍 임베딩 성능 분석 중...")
        
        embedding_results = {
            "average_time": 0,
            "throughput": 0,
            "dimension": 0,
            "batch_performance": {},
            "errors": 0
        }
        
        if not self.embedder:
            print("   ⚠️ 임베딩 클라이언트가 초기화되지 않음")
            return embedding_results
        
        try:
            # 테스트 텍스트 준비
            test_texts = []
            for case in self.test_cases:
                summary = case.get("판결요지", "")
                if summary and len(summary) > 50:
                    test_texts.append(summary[:500])  # 최대 500자
            
            if not test_texts:
                print("   ⚠️ 테스트할 텍스트가 없음")
                return embedding_results
            
            # 개별 임베딩 성능 측정
            times = []
            for i, text in enumerate(test_texts[:5]):  # 처음 5개만 테스트
                start_time = time.time()
                try:
                    result = self.embedder.embed([text])
                    embedding_results["dimension"] = result["dim"]
                    end_time = time.time()
                    times.append(end_time - start_time)
                except Exception as e:
                    print(f"   ⚠️ 임베딩 실패 {i+1}: {e}")
                    embedding_results["errors"] += 1
            
            if times:
                embedding_results["average_time"] = np.mean(times)
                embedding_results["throughput"] = 1.0 / np.mean(times)
            
            # 배치 성능 측정
            batch_sizes = [1, 3, 5]
            for batch_size in batch_sizes:
                if len(test_texts) >= batch_size:
                    batch_texts = test_texts[:batch_size]
                    start_time = time.time()
                    try:
                        self.embedder.embed(batch_texts)
                        end_time = time.time()
                        batch_time = end_time - start_time
                        embedding_results["batch_performance"][batch_size] = {
                            "total_time": batch_time,
                            "time_per_item": batch_time / batch_size
                        }
                    except Exception as e:
                        print(f"   ⚠️ 배치 크기 {batch_size} 실패: {e}")
                        embedding_results["errors"] += 1
            
            print(f"   ✅ 임베딩 성능 분석 완료")
            print(f"      - 평균 시간: {embedding_results['average_time']:.3f}초")
            print(f"      - 처리량: {embedding_results['throughput']:.1f} texts/sec")
            print(f"      - 차원: {embedding_results['dimension']}")
            
        except Exception as e:
            print(f"   ❌ 임베딩 성능 분석 실패: {e}")
            embedding_results["errors"] += 1
        
        return embedding_results
    
    def analyze_vector_db_performance(self) -> Dict:
        """벡터 데이터베이스 성능 분석"""
        print("\n🗄️ 벡터 데이터베이스 성능 분석 중...")
        
        db_results = {
            "search_performance": {},
            "index_stats": {},
            "errors": 0
        }
        
        if not self.vector_db or not self.embedder:
            print("   ⚠️ 벡터 데이터베이스 또는 임베딩 클라이언트가 초기화되지 않음")
            return db_results
        
        try:
            # 검색 성능 측정
            test_queries = [
                "근로계약 해지",
                "부동산 소유권",
                "교통사고 손해배상",
                "임금체불",
                "계약서 작성"
            ]
            
            search_times = []
            for query in test_queries:
                try:
                    # 쿼리 임베딩 생성
                    query_embedding = self.embedder.embed_query(query)
                    
                    # 검색 시간 측정
                    start_time = time.time()
                    results = self.vector_db.search(
                        query_vector=query_embedding.tolist(),
                        top_k=5
                    )
                    end_time = time.time()
                    
                    search_time = end_time - start_time
                    search_times.append(search_time)
                    
                    # 결과 품질 확인
                    matches = results.get('matches', [])
                    print(f"   📝 쿼리 '{query}': {len(matches)}개 결과, {search_time:.3f}초")
                    
                except Exception as e:
                    print(f"   ⚠️ 쿼리 '{query}' 검색 실패: {e}")
                    db_results["errors"] += 1
            
            if search_times:
                db_results["search_performance"] = {
                    "average_time": np.mean(search_times),
                    "min_time": np.min(search_times),
                    "max_time": np.max(search_times),
                    "std_time": np.std(search_times)
                }
            
            # 인덱스 통계 (Pinecone의 경우)
            try:
                index_stats = self.vector_db.get_index_stats()
                db_results["index_stats"] = index_stats
            except Exception as e:
                print(f"   ⚠️ 인덱스 통계 조회 실패: {e}")
                db_results["errors"] += 1
            
            print(f"   ✅ 벡터 데이터베이스 성능 분석 완료")
            if search_times:
                avg_time = np.mean(search_times)
                print(f"      - 평균 검색 시간: {avg_time:.3f}초")
                print(f"      - 검색 처리량: {1.0/avg_time:.1f} queries/sec")
            
        except Exception as e:
            print(f"   ❌ 벡터 데이터베이스 성능 분석 실패: {e}")
            db_results["errors"] += 1
        
        return db_results
    
    def analyze_retrieval_accuracy(self) -> Dict:
        """검색 정확도 분석"""
        print("\n🎯 검색 정확도 분석 중...")
        
        accuracy_results = {
            "precision_at_k": {},
            "recall_estimates": {},
            "relevance_scores": [],
            "errors": 0
        }
        
        if not self.vector_db or not self.embedder:
            print("   ⚠️ 필요한 컴포넌트가 초기화되지 않음")
            return accuracy_results
        
        try:
            # 테스트 쿼리-답변 쌍
            test_pairs = [
                {
                    "query": "근로계약 해지 절차",
                    "expected_keywords": ["근로계약", "해지", "통고", "의사표시"]
                },
                {
                    "query": "부동산 소유권 등기",
                    "expected_keywords": ["부동산", "소유권", "등기", "추정"]
                },
                {
                    "query": "교통사고 손해배상",
                    "expected_keywords": ["교통사고", "손해배상", "과실", "배상"]
                }
            ]
            
            k_values = [1, 3, 5]
            precision_scores = {k: [] for k in k_values}
            
            for test_pair in test_pairs:
                query = test_pair["query"]
                expected_keywords = test_pair["expected_keywords"]
                
                try:
                    # 쿼리 임베딩 및 검색
                    query_embedding = self.embedder.embed_query(query)
                    results = self.vector_db.search(
                        query_vector=query_embedding.tolist(),
                        top_k=max(k_values)
                    )
                    
                    matches = results.get('matches', [])
                    
                    # 각 k값에 대한 정확도 계산
                    for k in k_values:
                        relevant_count = 0
                        top_k_matches = matches[:k]
                        
                        for match in top_k_matches:
                            metadata = match.get('metadata', {})
                            content = metadata.get('content', '').lower()
                            
                            # 키워드 매칭으로 관련성 판단
                            keyword_matches = sum(1 for kw in expected_keywords 
                                                if kw.lower() in content)
                            if keyword_matches >= len(expected_keywords) // 2:
                                relevant_count += 1
                        
                        precision = relevant_count / k if k > 0 else 0
                        precision_scores[k].append(precision)
                    
                    print(f"   📝 쿼리 '{query}': {len(matches)}개 결과")
                    
                except Exception as e:
                    print(f"   ⚠️ 쿼리 '{query}' 정확도 분석 실패: {e}")
                    accuracy_results["errors"] += 1
            
            # 평균 정확도 계산
            for k in k_values:
                if precision_scores[k]:
                    accuracy_results["precision_at_k"][f"p@{k}"] = {
                        "mean": np.mean(precision_scores[k]),
                        "std": np.std(precision_scores[k]),
                        "scores": precision_scores[k]
                    }
            
            print(f"   ✅ 검색 정확도 분석 완료")
            for k in k_values:
                if f"p@{k}" in accuracy_results["precision_at_k"]:
                    mean_precision = accuracy_results["precision_at_k"][f"p@{k}"]["mean"]
                    print(f"      - Precision@{k}: {mean_precision:.3f}")
            
        except Exception as e:
            print(f"   ❌ 검색 정확도 분석 실패: {e}")
            accuracy_results["errors"] += 1
        
        return accuracy_results
    
    def run_comprehensive_analysis(self) -> Dict:
        """종합 성능 분석 실행"""
        print("🚀 종합 성능 분석 시작")
        
        # 컴포넌트 초기화
        if not self.initialize_components():
            return {"error": "컴포넌트 초기화 실패"}
        
        # 테스트 데이터 로드
        if not self.load_test_data():
            return {"error": "테스트 데이터 로드 실패"}
        
        # 각종 분석 수행
        analysis_results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "test_cases_count": len(self.test_cases),
            "embedding_performance": self.analyze_embedding_performance(),
            "vector_db_performance": self.analyze_vector_db_performance(),
            "retrieval_accuracy": self.analyze_retrieval_accuracy()
        }
        
        # 전체 오류 수 계산
        total_errors = (
            analysis_results["embedding_performance"].get("errors", 0) +
            analysis_results["vector_db_performance"].get("errors", 0) +
            analysis_results["retrieval_accuracy"].get("errors", 0)
        )
        
        analysis_results["total_errors"] = total_errors
        analysis_results["analysis_status"] = "완료" if total_errors == 0 else "경고"
        
        print(f"\n✅ 종합 성능 분석 완료 (오류: {total_errors}개)")
        
        return analysis_results


if __name__ == "__main__":
    analyzer = PerformanceAnalyzer()
    results = analyzer.run_comprehensive_analysis()
    
    print("\n📊 분석 결과:")
    print(json.dumps(results, indent=2, ensure_ascii=False))