#!/usr/bin/env python3
"""
Task 3: 시스템 평가 및 보고서 생성

이 모듈은 Task 1과 Task 2에서 구축한 시스템의 종합적인 평가를 수행하고
상세한 분석 보고서를 생성합니다.

주요 기능:
- 벡터 데이터베이스 성능 분석
- RAG 시스템 정확도 평가
- 챗봇 품질 분석
- 종합 보고서 생성

사용법:
    python task3/main.py

출력:
    - reports/system_analysis_report.md
    - reports/performance_metrics.json
    - reports/test_results.json
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent directories to path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from analysis.performance_analyzer import PerformanceAnalyzer
from analysis.quality_evaluator import QualityEvaluator
from reports.report_generator import ReportGenerator


def main():
    """Task 3 메인 실행 함수"""
    print("🚀 Task 3 시작: 시스템 평가 및 보고서 생성")
    print("=" * 60)
    
    # 분석 시작 시간 기록
    start_time = datetime.now()
    
    try:
        # 1. 성능 분석기 초기화
        print("\n📊 1단계: 성능 분석 수행")
        performance_analyzer = PerformanceAnalyzer()
        perf_results = performance_analyzer.run_comprehensive_analysis()
        
        # 2. 품질 평가기 초기화
        print("\n🎯 2단계: 품질 평가 수행")
        quality_evaluator = QualityEvaluator()
        quality_results = quality_evaluator.evaluate_system_quality()
        
        # 3. 보고서 생성
        print("\n📝 3단계: 종합 보고서 생성")
        report_generator = ReportGenerator(
            performance_results=perf_results,
            quality_results=quality_results,
            analysis_start_time=start_time
        )
        
        # 보고서 파일들 생성
        report_paths = report_generator.generate_all_reports()
        
        # 완료 메시지
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n✅ Task 3 완료! (소요시간: {duration:.1f}초)")
        print("\n📄 생성된 보고서:")
        for path in report_paths:
            print(f"   - {path}")
        
        print(f"\n📂 보고서 위치: {current_dir / 'reports'}")
        
    except Exception as e:
        print(f"\n❌ Task 3 실행 중 오류 발생: {e}")
        print("시스템 구성을 확인해주세요:")
        print("1. Task 1이 완료되어 벡터 데이터베이스가 구축되어 있는지 확인")
        print("2. Task 2 챗봇이 정상 동작하는지 확인")
        print("3. 필요한 환경변수가 모두 설정되어 있는지 확인")
        raise


if __name__ == "__main__":
    main()