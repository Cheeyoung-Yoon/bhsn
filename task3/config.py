#!/usr/bin/env python3
"""
Task 3 설정 파일

시스템 평가 및 보고서 생성을 위한 설정값들
"""

import os
from pathlib import Path

# 분석 설정
ANALYSIS_CONFIG = {
    "performance": {
        "test_embedding_count": 5,      # 임베딩 성능 테스트용 텍스트 수
        "test_query_count": 5,          # 검색 성능 테스트용 쿼리 수
        "batch_sizes": [1, 3, 5],       # 배치 성능 테스트 크기들
        "top_k_values": [1, 3, 5]       # Precision@K 평가용 K값들
    },
    "quality": {
        "response_timeout": 30,         # 챗봇 응답 타임아웃 (초)
        "min_response_length": 50,      # 최소 응답 길이
        "max_response_length": 1000,    # 최대 응답 길이 경고 기준
        "concept_match_threshold": 0.5  # 개념 매칭 임계값
    }
}

# 테스트 질문 카테고리
TEST_CATEGORIES = [
    "근로법",
    "부동산법", 
    "민사법",
    "교통사고",
    "노동법",
    "특허법"
]

# 난이도 레벨
DIFFICULTY_LEVELS = ["쉬움", "보통", "어려움"]

# 평가 기준
EVALUATION_CRITERIA = {
    "relevance": {
        "description": "질문과 답변의 관련성",
        "weight": 0.3,
        "max_score": 10
    },
    "accuracy": {
        "description": "법적 정확성 및 근거 제시",
        "weight": 0.3,
        "max_score": 10
    },
    "completeness": {
        "description": "답변의 완성도",
        "weight": 0.2,
        "max_score": 10
    },
    "clarity": {
        "description": "답변의 명확성 및 이해도",
        "weight": 0.2,
        "max_score": 10
    }
}

# 보고서 설정
REPORT_CONFIG = {
    "output_formats": ["markdown", "json"],
    "include_detailed_results": True,
    "include_charts": False,  # 향후 확장용
    "compress_output": False
}

# 파일 경로
TASK3_DIR = Path(__file__).parent
REPORTS_DIR = TASK3_DIR / "reports"
ANALYSIS_DIR = TASK3_DIR / "analysis"
TESTS_DIR = TASK3_DIR / "tests"

# 보고서 파일명
REPORT_FILES = {
    "main_report": "system_analysis_report.md",
    "summary": "analysis_summary.json",
    "performance": "performance_metrics.json",
    "quality": "quality_assessment.json"
}

# 법적 근거 키워드 (응답 품질 평가용)
LEGAL_INDICATORS = [
    "판례", "법원", "대법원", "고등법원", "지방법원",
    "조", "항", "호", "법률", "판결", "결정",
    "민법", "상법", "근로기준법", "헌법",
    "소송", "재판", "변호사", "법무부"
]

# 성능 임계값 (경고 기준)
PERFORMANCE_THRESHOLDS = {
    "embedding_time_warning": 2.0,     # 초
    "search_time_warning": 1.0,        # 초
    "error_rate_warning": 0.1,         # 10%
    "success_rate_minimum": 0.8        # 80%
}