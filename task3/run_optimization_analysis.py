#!/usr/bin/env python3
"""
Task3 통합 실행 스크립트

속도 최적화 분석을 위한 전체 프로세스를 통합 실행합니다.

실행 단계:
1. 기준선 성능 측정
2. 최적화 구현 및 적용
3. 최적화 후 성능 측정
4. 비교 분석 및 보고서 생성
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from performance_measurement import PerformanceMeasurementSystem
    from speed_optimization import SpeedOptimizer
    from optimization_report_generator import OptimizationReportGenerator
    from optimization_metrics import SpeedOptimizationMetrics, create_test_data
except ImportError as e:
    print(f"모듈 import 오류: {e}")
    print("필요한 파일들이 모두 존재하는지 확인해주세요.")
    sys.exit(1)


class Task3OptimizationRunner:
    """Task3 최적화 분석 통합 실행 클래스"""
    
    def __init__(self):
        """초기화"""
        self.measurement_system = None
        self.optimizer = None
        self.report_generator = OptimizationReportGenerator()
        self.test_data = create_test_data()
        self.results = {
            'baseline': {},
            'optimized': {},
            'comparison': {},
            'metadata': {
                'start_time': datetime.now().isoformat(),
                'test_data_size': len(self.test_data['test_texts'])
            }
        }
    
    def print_banner(self):
        """시작 배너 출력"""
        print("=" * 70)
        print("🚀 Task3: 속도 최적화 분석 시스템")
        print("=" * 70)
        print("📅 실행 시간:", datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분"))
        print("🎯 목표: Task1(RAG)과 Task2(챗봇)의 성능 최적화 및 분석")
        print("📊 분석 범위: 임베딩, 벡터검색, 엔드투엔드 성능")
        print("-" * 70)
    
    async def run_baseline_measurement(self) -> bool:
        """1단계: 기준선 성능 측정"""
        print("\n📊 1단계: 기준선 성능 측정")
        print("-" * 40)
        
        try:
            # 성능 측정 시스템 초기화
            self.measurement_system = PerformanceMeasurementSystem()
            
            if not self.measurement_system.initialize_components():
                print("❌ 기준선 측정을 위한 컴포넌트 초기화 실패")
                return False
            
            # 기준선 성능 측정
            print("🔍 현재 시스템 성능 측정 중...")
            baseline_results = self.measurement_system.measure_current_performance()
            
            # 기준선 저장
            self.measurement_system.save_performance_baseline("optimization_baseline")
            self.results['baseline'] = baseline_results
            
            print("✅ 기준선 성능 측정 완료")
            self._print_baseline_summary(baseline_results)
            
            return True
            
        except Exception as e:
            print(f"❌ 기준선 성능 측정 실패: {e}")
            return False
    
    async def run_optimization_implementation(self) -> bool:
        """2단계: 최적화 구현 및 적용"""
        print("\n🚀 2단계: 최적화 구현 및 적용")
        print("-" * 40)
        
        try:
            # 최적화 시스템 초기화
            self.optimizer = SpeedOptimizer()
            
            # 최적화 설정 적용
            print("🔧 최적화 컴포넌트 설정 중...")
            setup_result = self.optimizer.setup_optimizations()
            
            if setup_result['status'] != 'success':
                print(f"❌ 최적화 설정 실패: {setup_result['message']}")
                return False
            
            print("✅ 최적화 컴포넌트 설정 완료")
            print("   📦 구현된 최적화:")
            print("   - 임베딩 캐싱 (LRU, 1000개)")
            print("   - 검색 결과 캐싱 (TTL, 5분)")
            print("   - 응답 캐싱 (TTL, 30분)")
            print("   - 비동기 처리 파이프라인")
            print("   - 배치 처리 최적화")
            
            return True
            
        except Exception as e:
            print(f"❌ 최적화 구현 실패: {e}")
            return False
    
    async def run_optimized_measurement(self) -> bool:
        """3단계: 최적화 후 성능 측정"""
        print("\n📈 3단계: 최적화 후 성능 측정")
        print("-" * 40)
        
        try:
            print("🔍 최적화된 시스템 성능 측정 중...")
            
            # 최적화된 시스템으로 성능 비교
            comparison_results = await self.optimizer.run_performance_comparison(self.test_data)
            
            self.results['optimized'] = comparison_results['optimized']
            self.results['comparison'] = comparison_results['improvement']
            
            print("✅ 최적화 후 성능 측정 완료")
            self._print_optimization_summary(comparison_results)
            
            return True
            
        except Exception as e:
            print(f"❌ 최적화 후 성능 측정 실패: {e}")
            return False
    
    async def generate_comprehensive_report(self) -> bool:
        """4단계: 종합 보고서 생성"""
        print("\n📝 4단계: 종합 보고서 생성")
        print("-" * 40)
        
        try:
            print("📋 상세 분석 보고서 생성 중...")
            
            # 종합 보고서 생성
            report_content = self.report_generator.generate_comprehensive_report(
                self.results['baseline'],
                self.results['optimized']
            )
            
            # 보고서 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = self.report_generator.save_report(
                report_content,
                f"task3_optimization_analysis_{timestamp}.md"
            )
            
            # JSON 결과 저장
            json_path = current_dir / "reports" / f"optimization_results_{timestamp}.json"
            json_path.parent.mkdir(exist_ok=True)
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"✅ 보고서 생성 완료")
            print(f"   📄 마크다운 보고서: {report_path}")
            print(f"   📊 JSON 데이터: {json_path}")
            
            # 차트 생성 시도
            try:
                chart_paths = self.report_generator.create_performance_charts(
                    self.results['baseline'],
                    self.results['optimized']
                )
                if chart_paths:
                    print(f"   📈 성능 차트: {chart_paths}")
            except Exception as e:
                print(f"   ⚠️ 차트 생성 건너뜀: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ 보고서 생성 실패: {e}")
            return False
    
    def _print_baseline_summary(self, baseline: dict):
        """기준선 성능 요약 출력"""
        print("\n📊 기준선 성능 요약:")
        
        if 'embedding' in baseline and 'individual_throughput' in baseline['embedding']:
            throughput = baseline['embedding']['individual_throughput']
            print(f"   🤖 임베딩 처리량: {throughput:.2f} texts/sec")
        
        if 'search' in baseline and 'queries_per_second' in baseline['search']:
            qps = baseline['search']['queries_per_second']
            print(f"   🔍 검색 처리량: {qps:.2f} queries/sec")
        
        if 'end_to_end' in baseline and 'avg_total_response_time' in baseline['end_to_end']:
            response_time = baseline['end_to_end']['avg_total_response_time']
            print(f"   🔄 평균 응답시간: {response_time:.2f}초")
    
    def _print_optimization_summary(self, comparison: dict):
        """최적화 결과 요약 출력"""
        print("\n📈 최적화 결과 요약:")
        
        if 'improvement' in comparison:
            improvements = comparison['improvement']
            
            for category, metrics in improvements.items():
                print(f"\n   📦 {category.upper()} 개선도:")
                for metric, data in metrics.items():
                    if isinstance(data, dict) and 'improvement_percent' in data:
                        improvement = data['improvement_percent']
                        status = "🟢" if improvement > 0 else "🔴"
                        print(f"      {status} {metric}: {improvement:+.1f}%")
    
    async def run_complete_analysis(self) -> bool:
        """전체 분석 프로세스 실행"""
        self.print_banner()
        
        try:
            # 1단계: 기준선 측정
            if not await self.run_baseline_measurement():
                return False
            
            # 2단계: 최적화 구현
            if not await self.run_optimization_implementation():
                return False
            
            # 3단계: 최적화 후 측정
            if not await self.run_optimized_measurement():
                return False
            
            # 4단계: 보고서 생성
            if not await self.generate_comprehensive_report():
                return False
            
            # 최종 요약
            self._print_final_summary()
            
            return True
            
        except Exception as e:
            print(f"\n❌ 분석 프로세스 중 오류 발생: {e}")
            return False
    
    def _print_final_summary(self):
        """최종 요약 출력"""
        print("\n" + "=" * 70)
        print("🎉 Task3 속도 최적화 분석 완료!")
        print("=" * 70)
        
        # 핵심 성과 계산
        key_improvements = []
        
        if 'comparison' in self.results:
            for category, metrics in self.results['comparison'].items():
                for metric, data in metrics.items():
                    if isinstance(data, dict) and 'improvement_percent' in data:
                        improvement = data['improvement_percent']
                        if improvement > 0:
                            key_improvements.append(f"{metric}: {improvement:.1f}% 개선")
        
        if key_improvements:
            print("🏆 주요 성과:")
            for improvement in key_improvements[:5]:  # 상위 5개만 표시
                print(f"   ✅ {improvement}")
        
        print(f"\n📁 결과 위치: {current_dir / 'reports'}")
        print("📖 상세한 분석 결과는 생성된 마크다운 보고서를 참고하세요.")
        
        # 권장사항
        print("\n💡 다음 단계 권장사항:")
        print("   1. 생성된 보고서 검토 및 팀 공유")
        print("   2. 우선순위 높은 최적화 방안 프로덕션 적용")
        print("   3. 정기적인 성능 모니터링 체계 구축")
        print("   4. 사용자 피드백 기반 추가 최적화 검토")


async def main():
    """메인 실행 함수"""
    runner = Task3OptimizationRunner()
    
    success = await runner.run_complete_analysis()
    
    if success:
        print("\n✅ 모든 분석이 성공적으로 완료되었습니다!")
        return 0
    else:
        print("\n❌ 분석 중 오류가 발생했습니다.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️ 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 예상치 못한 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)