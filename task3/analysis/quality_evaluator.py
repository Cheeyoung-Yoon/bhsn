#!/usr/bin/env python3
"""
품질 평가기 모듈

챗봇과 RAG 시스템의 정성적 품질을 평가합니다.
"""

import os
import sys
import json
import time
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from task2.app import LawChatbot
    from task1.app.parser import parse_cases
    from task1.app.config import DATA_JSON
except ImportError as e:
    print(f"Task 1/2 모듈 import 오류: {e}")


class QualityEvaluator:
    """시스템 품질 평가 클래스"""
    
    def __init__(self):
        """품질 평가기 초기화"""
        self.chatbot = None
        self.test_questions = []
        self.evaluation_results = {}
        
    def initialize_chatbot(self):
        """챗봇 초기화"""
        try:
            print("🤖 챗봇 초기화 중...")
            self.chatbot = LawChatbot()
            print("   ✅ 챗봇 초기화 완료")
            return True
        except Exception as e:
            print(f"   ❌ 챗봇 초기화 실패: {e}")
            return False
    
    def prepare_test_questions(self):
        """테스트 질문 준비"""
        self.test_questions = [
            {
                "category": "근로법",
                "question": "사직원을 제출한 후 철회할 수 있나요?",
                "expected_concepts": ["사직", "철회", "근로계약", "해지"],
                "difficulty": "보통"
            },
            {
                "category": "부동산법",
                "question": "소유권보존등기의 추정력이 깨지는 경우는 언제인가요?",
                "expected_concepts": ["소유권보존등기", "추정력", "사정", "양도"],
                "difficulty": "어려움"
            },
            {
                "category": "민사법",
                "question": "계약서 작성 시 주의사항을 알려주세요",
                "expected_concepts": ["계약서", "작성", "주의사항"],
                "difficulty": "쉬움"
            },
            {
                "category": "교통사고",
                "question": "교통사고로 사망한 사업자의 일실이익은 어떻게 산정하나요?",
                "expected_concepts": ["교통사고", "일실이익", "사업자", "산정"],
                "difficulty": "보통"
            },
            {
                "category": "노동법",
                "question": "대기운전사도 정규직과 같은 대우를 받을 수 있나요?",
                "expected_concepts": ["대기운전사", "근무", "배차", "노동"],
                "difficulty": "보통"
            },
            {
                "category": "특허법",
                "question": "실용신안 등록 요건에 대해 설명해주세요",
                "expected_concepts": ["실용신안", "등록", "요건"],
                "difficulty": "어려움"
            }
        ]
        
        print(f"📝 {len(self.test_questions)}개 테스트 질문 준비 완료")
    
    def evaluate_response_quality(self, question: str, response: str, expected_concepts: List[str]) -> Dict:
        """응답 품질 평가"""
        evaluation = {
            "relevance_score": 0,      # 관련성 점수 (0-10)
            "completeness_score": 0,   # 완성도 점수 (0-10)
            "accuracy_score": 0,       # 정확도 점수 (0-10)
            "clarity_score": 0,        # 명확성 점수 (0-10)
            "concept_coverage": 0,     # 개념 포함도 (0-1)
            "has_legal_reference": False,  # 법적 근거 포함 여부
            "response_length": len(response),
            "issues": []
        }
        
        if not response or len(response) < 50:
            evaluation["issues"].append("응답이 너무 짧음")
            return evaluation
        
        response_lower = response.lower()
        
        # 1. 개념 포함도 평가
        covered_concepts = 0
        for concept in expected_concepts:
            if concept.lower() in response_lower:
                covered_concepts += 1
        
        evaluation["concept_coverage"] = covered_concepts / len(expected_concepts)
        
        # 2. 법적 근거 포함 여부
        legal_indicators = ["판례", "법원", "대법원", "조", "항", "호", "법률", "판결"]
        evaluation["has_legal_reference"] = any(indicator in response for indicator in legal_indicators)
        
        # 3. 응답 품질 점수 (간단한 휴리스틱)
        
        # 관련성: 기대 개념 포함도 기반
        evaluation["relevance_score"] = min(10, evaluation["concept_coverage"] * 10 + 2)
        
        # 완성도: 응답 길이와 구조 기반
        if len(response) > 200:
            evaluation["completeness_score"] = 8
        elif len(response) > 100:
            evaluation["completeness_score"] = 6
        else:
            evaluation["completeness_score"] = 4
        
        # 정확도: 법적 근거 포함 여부 기반
        if evaluation["has_legal_reference"]:
            evaluation["accuracy_score"] = 8
        elif evaluation["concept_coverage"] > 0.5:
            evaluation["accuracy_score"] = 6
        else:
            evaluation["accuracy_score"] = 4
        
        # 명확성: 구조화된 응답인지 확인
        structure_indicators = ["답변:", "참조", "1.", "2.", "-", "•"]
        has_structure = any(indicator in response for indicator in structure_indicators)
        evaluation["clarity_score"] = 8 if has_structure else 5
        
        # 문제점 체크
        if evaluation["concept_coverage"] < 0.3:
            evaluation["issues"].append("관련 개념 부족")
        
        if not evaluation["has_legal_reference"]:
            evaluation["issues"].append("법적 근거 부족")
        
        if len(response) > 1000:
            evaluation["issues"].append("응답이 너무 길음")
        
        return evaluation
    
    def test_chatbot_responses(self) -> Dict:
        """챗봇 응답 테스트"""
        print("\n🧪 챗봇 응답 품질 테스트 중...")
        
        test_results = {
            "total_questions": len(self.test_questions),
            "successful_responses": 0,
            "failed_responses": 0,
            "individual_results": [],
            "average_scores": {},
            "category_analysis": {}
        }
        
        if not self.chatbot:
            print("   ⚠️ 챗봇이 초기화되지 않음")
            return test_results
        
        all_scores = {
            "relevance": [],
            "completeness": [],
            "accuracy": [],
            "clarity": [],
            "concept_coverage": []
        }
        
        category_stats = {}
        
        for i, test_q in enumerate(self.test_questions, 1):
            question = test_q["question"]
            category = test_q["category"]
            expected_concepts = test_q["expected_concepts"]
            difficulty = test_q["difficulty"]
            
            print(f"   📝 질문 {i}/{len(self.test_questions)}: {question[:50]}...")
            
            try:
                # 챗봇에게 질문
                start_time = time.time()
                history = []
                _, updated_history = self.chatbot.chat(question, history)
                end_time = time.time()
                
                response_time = end_time - start_time
                
                if updated_history and len(updated_history) >= 2:
                    response = updated_history[-1]["content"]
                    
                    # 응답 품질 평가
                    quality_eval = self.evaluate_response_quality(
                        question, response, expected_concepts
                    )
                    
                    # 결과 저장
                    result = {
                        "question_id": i,
                        "question": question,
                        "category": category,
                        "difficulty": difficulty,
                        "response": response,
                        "response_time": response_time,
                        "quality_evaluation": quality_eval
                    }
                    
                    test_results["individual_results"].append(result)
                    test_results["successful_responses"] += 1
                    
                    # 점수 누적
                    all_scores["relevance"].append(quality_eval["relevance_score"])
                    all_scores["completeness"].append(quality_eval["completeness_score"])
                    all_scores["accuracy"].append(quality_eval["accuracy_score"])
                    all_scores["clarity"].append(quality_eval["clarity_score"])
                    all_scores["concept_coverage"].append(quality_eval["concept_coverage"])
                    
                    # 카테고리별 통계
                    if category not in category_stats:
                        category_stats[category] = {
                            "count": 0,
                            "avg_relevance": 0,
                            "avg_accuracy": 0,
                            "concept_coverage": 0
                        }
                    
                    category_stats[category]["count"] += 1
                    category_stats[category]["avg_relevance"] += quality_eval["relevance_score"]
                    category_stats[category]["avg_accuracy"] += quality_eval["accuracy_score"]
                    category_stats[category]["concept_coverage"] += quality_eval["concept_coverage"]
                    
                    print(f"      ✅ 응답 생성 완료 ({response_time:.2f}초)")
                    print(f"         관련성: {quality_eval['relevance_score']}/10, "
                          f"정확도: {quality_eval['accuracy_score']}/10")
                    
                else:
                    print(f"      ❌ 응답 생성 실패: 빈 응답")
                    test_results["failed_responses"] += 1
                    
            except Exception as e:
                print(f"      ❌ 질문 처리 실패: {e}")
                test_results["failed_responses"] += 1
        
        # 평균 점수 계산
        if all_scores["relevance"]:
            test_results["average_scores"] = {
                "relevance": sum(all_scores["relevance"]) / len(all_scores["relevance"]),
                "completeness": sum(all_scores["completeness"]) / len(all_scores["completeness"]),
                "accuracy": sum(all_scores["accuracy"]) / len(all_scores["accuracy"]),
                "clarity": sum(all_scores["clarity"]) / len(all_scores["clarity"]),
                "concept_coverage": sum(all_scores["concept_coverage"]) / len(all_scores["concept_coverage"])
            }
        
        # 카테고리별 분석 완료
        for category, stats in category_stats.items():
            if stats["count"] > 0:
                test_results["category_analysis"][category] = {
                    "question_count": stats["count"],
                    "avg_relevance": stats["avg_relevance"] / stats["count"],
                    "avg_accuracy": stats["avg_accuracy"] / stats["count"],
                    "avg_concept_coverage": stats["concept_coverage"] / stats["count"]
                }
        
        print(f"   ✅ 챗봇 응답 테스트 완료")
        print(f"      성공: {test_results['successful_responses']}개, "
              f"실패: {test_results['failed_responses']}개")
        
        if test_results["average_scores"]:
            avg_scores = test_results["average_scores"]
            print(f"      평균 점수 - 관련성: {avg_scores['relevance']:.1f}/10, "
                  f"정확도: {avg_scores['accuracy']:.1f}/10")
        
        return test_results
    
    def analyze_response_patterns(self, test_results: Dict) -> Dict:
        """응답 패턴 분석"""
        print("\n📊 응답 패턴 분석 중...")
        
        pattern_analysis = {
            "common_issues": {},
            "response_length_stats": {},
            "legal_reference_rate": 0,
            "difficulty_performance": {}
        }
        
        if not test_results["individual_results"]:
            return pattern_analysis
        
        # 공통 문제점 분석
        all_issues = []
        response_lengths = []
        legal_ref_count = 0
        difficulty_scores = {}
        
        for result in test_results["individual_results"]:
            quality_eval = result["quality_evaluation"]
            
            # 문제점 수집
            all_issues.extend(quality_eval["issues"])
            
            # 응답 길이 수집
            response_lengths.append(quality_eval["response_length"])
            
            # 법적 근거 포함 여부
            if quality_eval["has_legal_reference"]:
                legal_ref_count += 1
            
            # 난이도별 성능
            difficulty = result["difficulty"]
            if difficulty not in difficulty_scores:
                difficulty_scores[difficulty] = []
            difficulty_scores[difficulty].append(quality_eval["relevance_score"])
        
        # 공통 문제점 빈도 계산
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        pattern_analysis["common_issues"] = issue_counts
        
        # 응답 길이 통계
        if response_lengths:
            pattern_analysis["response_length_stats"] = {
                "average": sum(response_lengths) / len(response_lengths),
                "min": min(response_lengths),
                "max": max(response_lengths),
                "median": sorted(response_lengths)[len(response_lengths) // 2]
            }
        
        # 법적 근거 포함률
        total_responses = len(test_results["individual_results"])
        pattern_analysis["legal_reference_rate"] = legal_ref_count / total_responses if total_responses > 0 else 0
        
        # 난이도별 성능
        for difficulty, scores in difficulty_scores.items():
            if scores:
                pattern_analysis["difficulty_performance"][difficulty] = {
                    "average_score": sum(scores) / len(scores),
                    "question_count": len(scores)
                }
        
        print(f"   ✅ 응답 패턴 분석 완료")
        print(f"      법적 근거 포함률: {pattern_analysis['legal_reference_rate']:.1%}")
        
        if pattern_analysis["common_issues"]:
            print("      주요 문제점:")
            for issue, count in sorted(pattern_analysis["common_issues"].items(), 
                                     key=lambda x: x[1], reverse=True):
                print(f"         - {issue}: {count}회")
        
        return pattern_analysis
    
    def evaluate_system_quality(self) -> Dict:
        """시스템 전체 품질 평가"""
        print("🎯 시스템 품질 평가 시작")
        
        # 챗봇 초기화
        if not self.initialize_chatbot():
            return {"error": "챗봇 초기화 실패"}
        
        # 테스트 질문 준비
        self.prepare_test_questions()
        
        # 챗봇 응답 테스트
        test_results = self.test_chatbot_responses()
        
        # 응답 패턴 분석
        pattern_analysis = self.analyze_response_patterns(test_results)
        
        # 종합 평가 결과
        quality_evaluation = {
            "evaluation_timestamp": datetime.now().isoformat(),
            "test_results": test_results,
            "pattern_analysis": pattern_analysis,
            "overall_assessment": self.generate_overall_assessment(test_results, pattern_analysis)
        }
        
        print(f"\n✅ 시스템 품질 평가 완료")
        
        return quality_evaluation
    
    def generate_overall_assessment(self, test_results: Dict, pattern_analysis: Dict) -> Dict:
        """전체적인 평가 생성"""
        assessment = {
            "overall_grade": "미평가",
            "strengths": [],
            "weaknesses": [],
            "recommendations": []
        }
        
        if not test_results["average_scores"]:
            return assessment
        
        avg_scores = test_results["average_scores"]
        success_rate = test_results["successful_responses"] / test_results["total_questions"]
        
        # 전체 등급 계산
        overall_score = (
            avg_scores["relevance"] * 0.3 +
            avg_scores["accuracy"] * 0.3 +
            avg_scores["completeness"] * 0.2 +
            avg_scores["clarity"] * 0.2
        )
        
        if overall_score >= 8.0:
            assessment["overall_grade"] = "우수"
        elif overall_score >= 6.0:
            assessment["overall_grade"] = "양호"
        elif overall_score >= 4.0:
            assessment["overall_grade"] = "보통"
        else:
            assessment["overall_grade"] = "개선필요"
        
        # 강점 분석
        if success_rate >= 0.9:
            assessment["strengths"].append("높은 응답 성공률")
        
        if avg_scores["relevance"] >= 7.0:
            assessment["strengths"].append("질문과 관련성 높은 응답")
        
        if pattern_analysis["legal_reference_rate"] >= 0.5:
            assessment["strengths"].append("법적 근거 포함률 양호")
        
        # 약점 분석
        if success_rate < 0.8:
            assessment["weaknesses"].append("응답 생성 실패율 높음")
        
        if avg_scores["accuracy"] < 6.0:
            assessment["weaknesses"].append("법적 정확도 부족")
        
        if pattern_analysis["legal_reference_rate"] < 0.3:
            assessment["weaknesses"].append("법적 근거 부족")
        
        # 개선 권장사항
        if avg_scores["concept_coverage"] < 0.5:
            assessment["recommendations"].append("관련 개념 포함도 향상 필요")
        
        if pattern_analysis["legal_reference_rate"] < 0.5:
            assessment["recommendations"].append("법적 근거 인용 강화 필요")
        
        if "응답이 너무 길음" in pattern_analysis["common_issues"]:
            assessment["recommendations"].append("응답 길이 최적화 필요")
        
        return assessment


if __name__ == "__main__":
    evaluator = QualityEvaluator()
    results = evaluator.evaluate_system_quality()
    
    print("\n📊 품질 평가 결과:")
    print(json.dumps(results, indent=2, ensure_ascii=False))