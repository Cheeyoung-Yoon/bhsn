#!/usr/bin/env python3
"""
성능 측정 시스템

현재 시스템의 성능을 종합적으로 측정하고 최적화 방안을 제시합니다.
"""

import os
import sys
import time
import json
import asyncio
from datetime import datetime
from pathlib import Path
import tracemalloc
from typing import Dict, List, Any, Optional

# Add parent directories to path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

try:
    from task1.app.embedding_client import EmbeddingClient
    from task1.app.db_connection import VectorDB
    from task1.app.parser import parse_cases
    from task1.app.config import DATA_JSON
    from task2.app import LawChatbot
    from optimization_metrics import SpeedOptimizationMetrics, create_test_data
except ImportError as e:
    print(f"모듈 import 오류: {e}")


class PerformanceMeasurementSystem:
    """성능 측정 시스템 클래스"""
    
    def __init__(self):
        """시스템 초기화"""
        self.metrics_system = SpeedOptimizationMetrics()
        self.embedder = None
        self.vector_db = None
        self.chatbot = None
        self.test_data = create_test_data()
        self.results = {}
        
    def initialize_components(self) -> bool:
        """시스템 컴포넌트 초기화"""
        try:
            print("🔧 시스템 컴포넌트 초기화 중...")
            
            # 임베딩 클라이언트 초기화
            print("   - 임베딩 클라이언트 초기화...")
            self.embedder = EmbeddingClient()
            
            # 벡터 데이터베이스 초기화
            print("   - 벡터 데이터베이스 연결...")
            self.vector_db = VectorDB(dim=3072)
            
            # 챗봇 초기화
            print("   - 챗봇 시스템 초기화...")
            self.chatbot = LawChatbot()
            
            print("✅ 모든 컴포넌트 초기화 완료")
            return True
            
        except Exception as e:
            print(f"❌ 컴포넌트 초기화 실패: {e}")
            return False
    
    def measure_current_performance(self) -> Dict[str, Any]:
        """현재 시스템 성능 측정"""
        print("\n📊 현재 시스템 성능 측정 시작...")
        
        performance_results = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'embedding_model': 'gemini-embedding-001',
                'vector_db': 'pinecone',
                'chat_model': 'gemini-2.0-flash-001'
            }
        }
        
        # 1. 임베딩 성능 측정
        print("\n🤖 1. 임베딩 성능 측정...")
        try:
            embedding_metrics = {}
            
            # 처리량 측정
            print("   - 임베딩 처리량 측정 중...")
            throughput_metrics = self.metrics_system.measure_embedding_throughput(
                self.embedder, self.test_data['test_texts']
            )
            embedding_metrics.update(throughput_metrics)
            
            # 지연시간 측정
            print("   - 임베딩 지연시간 측정 중...")
            latency_metrics = self.metrics_system.measure_embedding_latency(
                self.embedder, self.test_data['test_texts'][0]
            )
            embedding_metrics.update(latency_metrics)
            
            performance_results['embedding'] = embedding_metrics
            print(f"   ✅ 임베딩 성능 측정 완료")
            
        except Exception as e:
            print(f"   ❌ 임베딩 성능 측정 실패: {e}")
            performance_results['embedding'] = {'error': str(e)}
        
        # 2. 벡터 검색 성능 측정
        print("\n🔍 2. 벡터 검색 성능 측정...")
        try:
            search_metrics = self.metrics_system.measure_search_performance(
                self.vector_db, self.embedder, self.test_data['test_queries']
            )
            performance_results['search'] = search_metrics
            print(f"   ✅ 검색 성능 측정 완료")
            
        except Exception as e:
            print(f"   ❌ 검색 성능 측정 실패: {e}")
            performance_results['search'] = {'error': str(e)}
        
        # 3. 엔드투엔드 성능 측정
        print("\n🔄 3. RAG 파이프라인 성능 측정...")
        try:
            rag_metrics = self.metrics_system.measure_rag_pipeline_performance(
                self.chatbot, self.test_data['test_texts'][:3]  # 시간 절약을 위해 3개만
            )
            performance_results['end_to_end'] = rag_metrics
            print(f"   ✅ RAG 파이프라인 성능 측정 완료")
            
        except Exception as e:
            print(f"   ❌ RAG 파이프라인 성능 측정 실패: {e}")
            performance_results['end_to_end'] = {'error': str(e)}
        
        # 4. 리소스 사용률 측정
        print("\n💾 4. 리소스 사용률 측정...")
        try:
            # 간단한 메모리 사용량 측정
            def test_operation():
                return self.embedder.embed([self.test_data['test_texts'][0]])
            
            memory_metrics = self.metrics_system.measure_memory_usage(test_operation)
            performance_results['resource'] = memory_metrics
            print(f"   ✅ 리소스 사용률 측정 완료")
            
        except Exception as e:
            print(f"   ❌ 리소스 사용률 측정 실패: {e}")
            performance_results['resource'] = {'error': str(e)}
        
        self.results = performance_results
        return performance_results
    
    def calculate_optimization_scores(self) -> Dict[str, float]:
        """최적화 점수 계산"""
        if not self.results:
            return {'error': '성능 측정 결과가 없습니다.'}
            
        targets = self.metrics_system.set_performance_targets()
        scores = self.metrics_system.calculate_optimization_score(self.results, targets)
        return scores
    
    def save_performance_baseline(self, name: str = "baseline"):
        """성능 기준선 저장"""
        if self.results:
            self.metrics_system.save_baseline(self.results, name)
            print(f"✅ 성능 기준선 '{name}' 저장 완료")
        else:
            print("❌ 저장할 성능 데이터가 없습니다.")
    
    def generate_performance_report(self) -> str:
        """성능 분석 보고서 생성"""
        if not self.results:
            return "성능 측정 결과가 없습니다."
        
        scores = self.calculate_optimization_scores()
        
        report = self.metrics_system.generate_optimization_report(
            self.results, scores
        )
        
        # 추가 분석 내용
        additional_analysis = self._generate_detailed_analysis()
        report += "\n\n" + additional_analysis
        
        return report
    
    def _generate_detailed_analysis(self) -> str:
        """상세 분석 내용 생성"""
        analysis = [
            "## 🔍 상세 성능 분석",
            "",
            "### 주요 발견사항",
        ]
        
        # 임베딩 성능 분석
        if 'embedding' in self.results and 'error' not in self.results['embedding']:
            embedding = self.results['embedding']
            
            # 배치 효율성 분석
            if 'batch_efficiency' in embedding:
                efficiency = embedding['batch_efficiency']
                if efficiency > 2.0:
                    analysis.append("✅ 배치 처리가 효율적으로 작동하고 있습니다.")
                else:
                    analysis.append("⚠️ 배치 처리 효율성을 개선할 필요가 있습니다.")
            
            # 지연시간 변동성 분석
            if 'latency_std' in embedding:
                std = embedding['latency_std']
                avg = embedding.get('avg_latency', 0)
                if avg > 0 and std / avg > 0.3:
                    analysis.append("⚠️ 임베딩 지연시간의 변동성이 큽니다.")
        
        # 검색 성능 분석
        if 'search' in self.results and 'error' not in self.results['search']:
            search = self.results['search']
            
            if 'avg_search_time' in search:
                search_time = search['avg_search_time']
                if search_time > 1.0:
                    analysis.append("⚠️ 벡터 검색 시간이 1초를 초과합니다.")
                elif search_time < 0.1:
                    analysis.append("✅ 벡터 검색이 매우 빠르게 작동합니다.")
        
        # RAG 파이프라인 분석
        if 'end_to_end' in self.results and 'error' not in self.results['end_to_end']:
            rag = self.results['end_to_end']
            
            if 'retrieval_time_ratio' in rag and 'generation_time_ratio' in rag:
                retrieval_ratio = rag['retrieval_time_ratio']
                generation_ratio = rag['generation_time_ratio']
                
                if retrieval_ratio > 0.5:
                    analysis.append("⚠️ 문서 검색이 전체 시간의 50% 이상을 차지합니다.")
                if generation_ratio > 0.7:
                    analysis.append("⚠️ 응답 생성이 전체 시간의 70% 이상을 차지합니다.")
        
        analysis.extend([
            "",
            "### 🚀 최적화 권장사항",
            "",
            "#### 단기 개선 방안 (1-2주)",
            "1. **임베딩 최적화**",
            "   - 배치 크기를 최적화하여 API 호출 횟수 감소",
            "   - 임베딩 캐싱으로 중복 계산 방지",
            "",
            "2. **검색 최적화**", 
            "   - 검색 결과 캐싱 구현",
            "   - 벡터 인덱스 설정 최적화",
            "",
            "#### 중장기 개선 방안 (1-2개월)",
            "1. **아키텍처 최적화**",
            "   - 비동기 처리 도입으로 병렬화",
            "   - 마이크로서비스 아키텍처 적용",
            "",
            "2. **고급 최적화**",
            "   - 지능형 캐싱 전략 구현",
            "   - 로드 밸런싱 및 스케일링",
            "",
            "### 📈 예상 개선 효과",
            "",
            "| 항목 | 현재 | 목표 | 개선율 |",
            "|------|------|------|--------|"
        ])
        
        # 구체적인 수치 추가
        if 'embedding' in self.results and 'individual_throughput' in self.results['embedding']:
            current_throughput = self.results['embedding']['individual_throughput']
            analysis.append(f"| 임베딩 처리량 | {current_throughput:.1f} texts/sec | 10.0 texts/sec | {(10.0/current_throughput - 1)*100:.0f}% |")
        
        if 'search' in self.results and 'queries_per_second' in self.results['search']:
            current_qps = self.results['search']['queries_per_second']
            analysis.append(f"| 검색 처리량 | {current_qps:.1f} queries/sec | 20.0 queries/sec | {(20.0/current_qps - 1)*100:.0f}% |")
        
        if 'end_to_end' in self.results and 'avg_total_response_time' in self.results['end_to_end']:
            current_response = self.results['end_to_end']['avg_total_response_time']
            analysis.append(f"| 응답 시간 | {current_response:.1f}초 | 3.0초 | {(1 - 3.0/current_response)*100:.0f}% |")
        
        return "\n".join(analysis)
    
    def save_results(self, filepath: Optional[str] = None):
        """결과를 파일로 저장"""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = current_dir / "reports" / f"performance_measurement_{timestamp}.json"
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"📁 측정 결과 저장: {filepath}")
        return filepath


def main():
    """메인 실행 함수"""
    print("🚀 성능 측정 시스템 시작")
    print("=" * 50)
    
    # 시스템 초기화
    measurement_system = PerformanceMeasurementSystem()
    
    if not measurement_system.initialize_components():
        print("❌ 시스템 초기화 실패")
        return
    
    try:
        # 성능 측정 실행
        print("\n📊 성능 측정 실행 중...")
        results = measurement_system.measure_current_performance()
        
        # 점수 계산
        scores = measurement_system.calculate_optimization_scores()
        
        # 기준선 저장
        measurement_system.save_performance_baseline("current_baseline")
        
        # 보고서 생성
        report = measurement_system.generate_performance_report()
        
        # 결과 출력
        print("\n" + "="*50)
        print("📋 성능 측정 결과:")
        print("="*50)
        print(report)
        
        # 파일 저장
        json_file = measurement_system.save_results()
        
        # 마크다운 보고서 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = current_dir / "reports" / f"performance_report_{timestamp}.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 보고서 저장: {report_file}")
        print(f"📊 JSON 데이터: {json_file}")
        
        # 최적화 점수 요약
        print(f"\n🎯 전체 최적화 점수: {scores.get('overall', 0):.1f}/100")
        
        if scores.get('overall', 0) < 70:
            print("⚠️ 성능 개선이 필요합니다. 보고서의 권장사항을 참고하세요.")
        else:
            print("✅ 양호한 성능 상태입니다.")
        
    except Exception as e:
        print(f"❌ 성능 측정 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()