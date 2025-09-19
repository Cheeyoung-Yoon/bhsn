#!/usr/bin/env python3
"""
속도 최적화 지표 정의 및 측정 시스템

Task 1과 Task 2의 성능 최적화를 위한 핵심 지표들을 정의하고 측정합니다.
"""

import time
import asyncio
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime
import statistics
import json


@dataclass
class PerformanceMetric:
    """성능 측정 지표 클래스"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    category: str
    description: str


class SpeedOptimizationMetrics:
    """속도 최적화 지표 측정 시스템"""
    
    def __init__(self):
        self.metrics = []
        self.baselines = {}
        
    # =================
    # 1. 임베딩 성능 지표
    # =================
    
    def measure_embedding_throughput(self, embedder, test_texts: List[str]) -> Dict[str, float]:
        """임베딩 처리량 측정
        
        지표:
        - texts_per_second: 초당 처리 가능한 텍스트 수
        - avg_time_per_text: 텍스트 당 평균 처리 시간
        - batch_efficiency: 배치 처리 효율성
        """
        metrics = {}
        
        # 1. 개별 처리 성능
        start_time = time.time()
        for text in test_texts[:3]:  # 샘플 3개
            embedder.embed([text])
        end_time = time.time()
        
        total_time = end_time - start_time
        metrics['individual_avg_time'] = total_time / 3
        metrics['individual_throughput'] = 3 / total_time
        
        # 2. 배치 처리 성능
        batch_sizes = [1, 3, 5]
        batch_metrics = {}
        
        for batch_size in batch_sizes:
            if len(test_texts) >= batch_size:
                batch_texts = test_texts[:batch_size]
                start_time = time.time()
                embedder.embed(batch_texts)
                end_time = time.time()
                
                batch_time = end_time - start_time
                batch_metrics[batch_size] = {
                    'total_time': batch_time,
                    'time_per_text': batch_time / batch_size,
                    'throughput': batch_size / batch_time
                }
        
        metrics['batch_performance'] = batch_metrics
        
        # 배치 효율성 계산 (배치 처리가 개별 처리보다 얼마나 효율적인가)
        if 5 in batch_metrics and metrics['individual_avg_time'] > 0:
            batch_5_time_per_text = batch_metrics[5]['time_per_text']
            metrics['batch_efficiency'] = metrics['individual_avg_time'] / batch_5_time_per_text
        
        return metrics
    
    def measure_embedding_latency(self, embedder, test_text: str, iterations: int = 5) -> Dict[str, float]:
        """임베딩 지연시간 측정
        
        지표:
        - min_latency: 최소 지연시간
        - max_latency: 최대 지연시간  
        - avg_latency: 평균 지연시간
        - p95_latency: 95 퍼센타일 지연시간
        """
        latencies = []
        
        for _ in range(iterations):
            start_time = time.time()
            embedder.embed([test_text])
            end_time = time.time()
            latencies.append(end_time - start_time)
        
        return {
            'min_latency': min(latencies),
            'max_latency': max(latencies),
            'avg_latency': statistics.mean(latencies),
            'p95_latency': sorted(latencies)[int(0.95 * len(latencies))],
            'latency_std': statistics.stdev(latencies) if len(latencies) > 1 else 0
        }
    
    # =================
    # 2. 벡터 검색 성능 지표
    # =================
    
    def measure_search_performance(self, vector_db, embedder, test_queries: List[str]) -> Dict[str, float]:
        """벡터 검색 성능 측정
        
        지표:
        - queries_per_second: 초당 처리 가능한 쿼리 수
        - avg_search_time: 평균 검색 시간
        - search_accuracy: 검색 정확도 (관련성)
        """
        search_times = []
        total_results = 0
        
        for query in test_queries:
            # 쿼리 임베딩 생성
            query_embedding = embedder.embed_query(query)
            
            # 검색 시간 측정
            start_time = time.time()
            results = vector_db.search(query_embedding, top_k=5)
            end_time = time.time()
            
            search_time = end_time - start_time
            search_times.append(search_time)
            total_results += len(results.matches) if hasattr(results, 'matches') else 0
        
        return {
            'avg_search_time': statistics.mean(search_times),
            'min_search_time': min(search_times),
            'max_search_time': max(search_times),
            'queries_per_second': len(test_queries) / sum(search_times),
            'avg_results_count': total_results / len(test_queries),
            'search_time_std': statistics.stdev(search_times) if len(search_times) > 1 else 0
        }
    
    # =================
    # 3. 엔드투엔드 성능 지표
    # =================
    
    def measure_rag_pipeline_performance(self, chatbot, test_questions: List[str]) -> Dict[str, float]:
        """RAG 파이프라인 전체 성능 측정
        
        지표:
        - total_response_time: 전체 응답 시간
        - retrieval_time: 문서 검색 시간
        - generation_time: 응답 생성 시간
        - questions_per_minute: 분당 처리 가능한 질문 수
        """
        pipeline_metrics = []
        
        for question in test_questions:
            metrics = {}
            
            # 전체 파이프라인 시간 측정
            total_start = time.time()
            
            # 1. 문서 검색 시간
            retrieval_start = time.time()
            relevant_docs = chatbot.retrieve_relevant_docs(question, top_k=3)
            retrieval_end = time.time()
            metrics['retrieval_time'] = retrieval_end - retrieval_start
            
            # 2. 응답 생성 시간
            generation_start = time.time()
            response = chatbot.generate_response(question, relevant_docs)
            generation_end = time.time()
            metrics['generation_time'] = generation_end - generation_start
            
            total_end = time.time()
            metrics['total_response_time'] = total_end - total_start
            metrics['response_length'] = len(response) if response else 0
            
            pipeline_metrics.append(metrics)
        
        # 통계 계산
        total_times = [m['total_response_time'] for m in pipeline_metrics]
        retrieval_times = [m['retrieval_time'] for m in pipeline_metrics]
        generation_times = [m['generation_time'] for m in pipeline_metrics]
        
        return {
            'avg_total_response_time': statistics.mean(total_times),
            'avg_retrieval_time': statistics.mean(retrieval_times),
            'avg_generation_time': statistics.mean(generation_times),
            'questions_per_minute': 60 / statistics.mean(total_times),
            'total_time_std': statistics.stdev(total_times) if len(total_times) > 1 else 0,
            'retrieval_time_ratio': statistics.mean(retrieval_times) / statistics.mean(total_times),
            'generation_time_ratio': statistics.mean(generation_times) / statistics.mean(total_times)
        }
    
    # =================
    # 4. 리소스 사용률 지표
    # =================
    
    def measure_memory_usage(self, operation_func: Callable, *args) -> Dict[str, float]:
        """메모리 사용량 측정"""
        import tracemalloc
        
        tracemalloc.start()
        
        # 작업 실행
        result = operation_func(*args)
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        return {
            'current_memory_mb': current / 1024 / 1024,
            'peak_memory_mb': peak / 1024 / 1024,
            'memory_efficiency': len(str(result)) / (peak / 1024) if peak > 0 else 0  # bytes per KB
        }
    
    # =================
    # 5. 최적화 목표 지표
    # =================
    
    def set_performance_targets(self) -> Dict[str, Dict[str, float]]:
        """성능 최적화 목표 설정
        
        Returns:
            카테고리별 목표 성능 지표
        """
        return {
            'embedding': {
                'target_throughput': 10.0,  # texts/second
                'target_latency': 0.5,      # seconds
                'target_batch_efficiency': 3.0  # 배치가 개별보다 3배 효율적
            },
            'search': {
                'target_search_time': 0.1,   # seconds
                'target_qps': 20.0,          # queries/second
                'target_accuracy': 0.8       # precision@5
            },
            'end_to_end': {
                'target_response_time': 3.0,  # seconds
                'target_qpm': 20.0,           # questions/minute
                'target_retrieval_ratio': 0.3 # 검색이 전체의 30% 이하
            },
            'resource': {
                'target_memory_mb': 500,      # MB
                'target_memory_efficiency': 1000  # bytes per KB
            }
        }
    
    def calculate_optimization_score(self, current_metrics: Dict, targets: Dict) -> Dict[str, float]:
        """최적화 점수 계산
        
        Args:
            current_metrics: 현재 측정된 성능 지표
            targets: 목표 성능 지표
            
        Returns:
            카테고리별 최적화 점수 (0-100)
        """
        scores = {}
        
        for category, target_metrics in targets.items():
            if category not in current_metrics:
                scores[category] = 0
                continue
            
            category_scores = []
            current_category = current_metrics[category]
            
            for metric, target_value in target_metrics.items():
                if metric in current_category:
                    current_value = current_category[metric]
                    
                    # 높을수록 좋은 지표 (throughput, qps, efficiency 등)
                    if 'throughput' in metric or 'qps' in metric or 'efficiency' in metric:
                        score = min(100, (current_value / target_value) * 100)
                    # 낮을수록 좋은 지표 (latency, time 등)
                    else:
                        score = min(100, (target_value / current_value) * 100)
                    
                    category_scores.append(score)
            
            scores[category] = statistics.mean(category_scores) if category_scores else 0
        
        # 전체 평균 점수
        scores['overall'] = statistics.mean(list(scores.values())) if scores else 0
        
        return scores
    
    # =================
    # 6. 비교 및 보고
    # =================
    
    def save_baseline(self, metrics: Dict[str, Any], name: str = "baseline"):
        """기준선 성능 저장"""
        self.baselines[name] = {
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        }
    
    def compare_with_baseline(self, current_metrics: Dict, baseline_name: str = "baseline") -> Dict[str, Dict]:
        """기준선과 현재 성능 비교"""
        if baseline_name not in self.baselines:
            return {"error": f"Baseline '{baseline_name}' not found"}
        
        baseline_metrics = self.baselines[baseline_name]['metrics']
        comparison = {}
        
        def compare_nested(current, baseline, path=""):
            result = {}
            for key, current_value in current.items():
                if isinstance(current_value, dict):
                    if key in baseline and isinstance(baseline[key], dict):
                        result[key] = compare_nested(current_value, baseline[key], f"{path}.{key}")
                elif key in baseline and isinstance(baseline[key], (int, float)):
                    baseline_value = baseline[key]
                    if baseline_value != 0:
                        improvement = ((current_value - baseline_value) / baseline_value) * 100
                        result[key] = {
                            'current': current_value,
                            'baseline': baseline_value,
                            'improvement_percent': improvement,
                            'better': improvement > 0 if 'throughput' in key or 'qps' in key or 'efficiency' in key
                                     else improvement < 0  # 시간 지표는 감소가 개선
                        }
            return result
        
        return compare_nested(current_metrics, baseline_metrics)
    
    def generate_optimization_report(self, metrics: Dict, scores: Dict, comparison: Optional[Dict] = None) -> str:
        """최적화 보고서 생성"""
        report = [
            "# 🚀 속도 최적화 분석 보고서",
            f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 📊 현재 성능 지표",
        ]
        
        for category, category_metrics in metrics.items():
            report.append(f"\n### {category.title()} 성능")
            for metric, value in category_metrics.items():
                if isinstance(value, (int, float)):
                    report.append(f"- **{metric}**: {value:.3f}")
                elif isinstance(value, dict):
                    report.append(f"- **{metric}**:")
                    for sub_metric, sub_value in value.items():
                        if isinstance(sub_value, (int, float)):
                            report.append(f"  - {sub_metric}: {sub_value:.3f}")
        
        report.append("\n## 🎯 최적화 점수")
        for category, score in scores.items():
            status = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
            report.append(f"- **{category.title()}**: {score:.1f}점 {status}")
        
        if comparison:
            report.append("\n## 📈 기준선 대비 개선도")
            # 비교 결과 추가 (간략화)
            improved_count = 0
            total_count = 0
            
            def count_improvements(comp_dict):
                nonlocal improved_count, total_count
                for key, value in comp_dict.items():
                    if isinstance(value, dict):
                        if 'better' in value:
                            total_count += 1
                            if value['better']:
                                improved_count += 1
                        else:
                            count_improvements(value)
            
            count_improvements(comparison)
            if total_count > 0:
                improvement_rate = (improved_count / total_count) * 100
                report.append(f"- 전체 지표 중 {improvement_rate:.1f}% 개선")
        
        return "\n".join(report)


# 사용 예시 함수들
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


if __name__ == "__main__":
    # 테스트 실행
    metrics_system = SpeedOptimizationMetrics()
    
    # 목표 지표 출력
    targets = metrics_system.set_performance_targets()
    print("🎯 최적화 목표 지표:")
    print(json.dumps(targets, indent=2, ensure_ascii=False))