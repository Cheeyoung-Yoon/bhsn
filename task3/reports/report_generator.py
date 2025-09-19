#!/usr/bin/env python3
"""
보고서 생성기 모듈

분석 결과를 종합하여 상세한 보고서를 생성합니다.
"""

import os
import json
from datetime import datetime
from typing import Dict, List
from pathlib import Path


class ReportGenerator:
    """보고서 생성 클래스"""
    
    def __init__(self, performance_results: Dict, quality_results: Dict, analysis_start_time: datetime):
        """보고서 생성기 초기화"""
        self.performance_results = performance_results
        self.quality_results = quality_results
        self.analysis_start_time = analysis_start_time
        self.report_dir = Path(__file__).parent.parent / "reports"
        self.report_dir.mkdir(exist_ok=True)
    
    def generate_markdown_report(self) -> str:
        """Markdown 형식 종합 보고서 생성"""
        
        report_content = f"""# 법률 AI 시스템 종합 분석 보고서

## 📋 분석 개요

**분석 일시**: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}  
**분석 소요시간**: {(datetime.now() - self.analysis_start_time).total_seconds():.1f}초  
**보고서 버전**: 1.0  

---

## 🎯 Executive Summary

### 주요 성과
{self._generate_key_achievements()}

### 핵심 지표
{self._generate_key_metrics()}

### 권장사항
{self._generate_recommendations()}

---

## 🏗️ 시스템 아키텍처 분석

### Task 1: 벡터 데이터베이스 구축
- **데이터 처리**: 한국 법률 판례 데이터 파싱 및 청킹
- **임베딩 모델**: Google Gemini Embedding (3072차원)
- **벡터 저장소**: Pinecone 클라우드 기반 벡터 데이터베이스
- **청킹 전략**: 판결요지 중심 스마트 청킹 (300자 기준)

### Task 2: RAG 기반 챗봇
- **검색 시스템**: 의미적 유사도 기반 벡터 검색
- **생성 모델**: Google Gemini 2.0 Flash
- **사용자 인터페이스**: Gradio 웹 기반 인터페이스
- **대화 관리**: 컨텍스트 유지 및 히스토리 관리

---

## 📊 성능 분석 결과

### 임베딩 성능
{self._generate_embedding_performance()}

### 벡터 데이터베이스 성능
{self._generate_vector_db_performance()}

### 검색 정확도
{self._generate_retrieval_accuracy()}

---

## 🎯 품질 평가 결과

### 챗봇 응답 품질
{self._generate_chatbot_quality()}

### 카테고리별 성능
{self._generate_category_performance()}

### 응답 패턴 분석
{self._generate_response_patterns()}

---

## 🔍 상세 분석

### 시스템 강점
{self._generate_strengths()}

### 개선 영역
{self._generate_weaknesses()}

### 기술적 고려사항
{self._generate_technical_considerations()}

---

## 📈 성능 최적화 권장사항

### 단기 개선 방안
{self._generate_short_term_improvements()}

### 중장기 로드맵
{self._generate_long_term_roadmap()}

---

## 🔬 실험 결과 상세

### 테스트 케이스 분석
{self._generate_test_case_analysis()}

### 오류 분석
{self._generate_error_analysis()}

---

## 📝 결론

{self._generate_conclusion()}

---

## 📚 부록

### A. 기술 스택
- **Backend**: Python 3.x
- **임베딩**: Google GenAI Embedding
- **벡터 DB**: Pinecone
- **LLM**: Google Gemini 2.0 Flash
- **Frontend**: Gradio
- **데이터**: 한국 법률 판례 데이터

### B. 환경 설정
```bash
# 필요 패키지
pip install google-genai pinecone gradio python-dotenv numpy pandas

# 환경 변수
GOOGLE_API_KEY=your_google_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=law-bot-korean
```

### C. 참고 자료
- Task 1 구현: `bhsn/task1/`
- Task 2 구현: `bhsn/task2/`
- 분석 스크립트: `bhsn/task3/analysis/`

---

*본 보고서는 자동 생성되었습니다. 정확한 법률 자문은 전문 변호사와 상담하시기 바랍니다.*
"""
        
        return report_content
    
    def _generate_key_achievements(self) -> str:
        """주요 성과 섹션 생성"""
        achievements = [
            "✅ **법률 데이터 벡터화 완료**: 한국 법률 판례 데이터의 효과적인 임베딩 및 인덱싱",
            "✅ **RAG 기반 챗봇 구현**: 검색 증강 생성을 통한 법률 질의응답 시스템 구축",
            "✅ **웹 인터페이스 제공**: 사용자 친화적인 Gradio 기반 채팅 인터페이스"
        ]
        
        # 성능 결과가 있다면 추가
        if self.performance_results and 'total_errors' in self.performance_results:
            if self.performance_results['total_errors'] == 0:
                achievements.append("✅ **안정적 시스템 운영**: 분석 과정에서 오류 없이 동작")
        
        if self.quality_results and 'test_results' in self.quality_results:
            test_results = self.quality_results['test_results']
            if test_results.get('successful_responses', 0) > 0:
                success_rate = test_results['successful_responses'] / test_results['total_questions']
                achievements.append(f"✅ **높은 응답 성공률**: {success_rate:.1%}의 질문 응답 성공")
        
        return '\n'.join(achievements)
    
    def _generate_key_metrics(self) -> str:
        """핵심 지표 섹션 생성"""
        metrics = []
        
        # 성능 지표
        if self.performance_results:
            if 'embedding_performance' in self.performance_results:
                embed_perf = self.performance_results['embedding_performance']
                if 'average_time' in embed_perf and embed_perf['average_time'] > 0:
                    metrics.append(f"🕐 **임베딩 속도**: {embed_perf['average_time']:.3f}초/텍스트")
                if 'dimension' in embed_perf:
                    metrics.append(f"📏 **임베딩 차원**: {embed_perf['dimension']}차원")
            
            if 'vector_db_performance' in self.performance_results:
                db_perf = self.performance_results['vector_db_performance']
                if 'search_performance' in db_perf and 'average_time' in db_perf['search_performance']:
                    avg_time = db_perf['search_performance']['average_time']
                    metrics.append(f"🔍 **검색 속도**: {avg_time:.3f}초/쿼리")
        
        # 품질 지표
        if self.quality_results and 'test_results' in self.quality_results:
            test_results = self.quality_results['test_results']
            if 'average_scores' in test_results:
                avg_scores = test_results['average_scores']
                metrics.append(f"⭐ **평균 관련성**: {avg_scores.get('relevance', 0):.1f}/10")
                metrics.append(f"🎯 **평균 정확도**: {avg_scores.get('accuracy', 0):.1f}/10")
        
        if not metrics:
            metrics.append("📊 성능 지표 수집 중...")
        
        return '\n'.join(metrics)
    
    def _generate_recommendations(self) -> str:
        """권장사항 섹션 생성"""
        recommendations = []
        
        # 품질 평가 결과 기반 권장사항
        if (self.quality_results and 'overall_assessment' in self.quality_results and 
            'recommendations' in self.quality_results['overall_assessment']):
            for rec in self.quality_results['overall_assessment']['recommendations']:
                recommendations.append(f"💡 {rec}")
        
        # 성능 분석 기반 권장사항
        if self.performance_results:
            if self.performance_results.get('total_errors', 0) > 0:
                recommendations.append("⚠️ 시스템 안정성 개선을 위한 오류 처리 강화 필요")
        
        # 기본 권장사항
        if not recommendations:
            recommendations = [
                "💡 벡터 검색 최적화를 통한 응답 속도 개선",
                "💡 더 많은 법률 도메인 데이터 추가",
                "💡 사용자 피드백 수집 및 반영 체계 구축"
            ]
        
        return '\n'.join(recommendations)
    
    def _generate_embedding_performance(self) -> str:
        """임베딩 성능 섹션 생성"""
        if not self.performance_results or 'embedding_performance' not in self.performance_results:
            return "⚠️ 임베딩 성능 데이터를 수집하지 못했습니다."
        
        embed_perf = self.performance_results['embedding_performance']
        content = []
        
        if 'average_time' in embed_perf:
            content.append(f"- **평균 처리 시간**: {embed_perf['average_time']:.3f}초")
        
        if 'throughput' in embed_perf:
            content.append(f"- **처리량**: {embed_perf['throughput']:.1f} texts/second")
        
        if 'dimension' in embed_perf:
            content.append(f"- **벡터 차원**: {embed_perf['dimension']}차원")
        
        if 'batch_performance' in embed_perf:
            content.append("- **배치 성능**:")
            for batch_size, perf in embed_perf['batch_performance'].items():
                time_per_item = perf.get('time_per_item', 0)
                content.append(f"  - 배치 크기 {batch_size}: {time_per_item:.3f}초/item")
        
        if embed_perf.get('errors', 0) > 0:
            content.append(f"- ⚠️ **오류 발생**: {embed_perf['errors']}건")
        
        return '\n'.join(content) if content else "데이터 없음"
    
    def _generate_vector_db_performance(self) -> str:
        """벡터 DB 성능 섹션 생성"""
        if not self.performance_results or 'vector_db_performance' not in self.performance_results:
            return "⚠️ 벡터 데이터베이스 성능 데이터를 수집하지 못했습니다."
        
        db_perf = self.performance_results['vector_db_performance']
        content = []
        
        if 'search_performance' in db_perf:
            search_perf = db_perf['search_performance']
            if 'average_time' in search_perf:
                content.append(f"- **평균 검색 시간**: {search_perf['average_time']:.3f}초")
                content.append(f"- **검색 처리량**: {1.0/search_perf['average_time']:.1f} queries/second")
            
            if 'min_time' in search_perf and 'max_time' in search_perf:
                content.append(f"- **검색 시간 범위**: {search_perf['min_time']:.3f}초 ~ {search_perf['max_time']:.3f}초")
        
        if 'index_stats' in db_perf and db_perf['index_stats']:
            content.append("- **인덱스 정보**: 정상 연결")
        
        if db_perf.get('errors', 0) > 0:
            content.append(f"- ⚠️ **오류 발생**: {db_perf['errors']}건")
        
        return '\n'.join(content) if content else "데이터 없음"
    
    def _generate_retrieval_accuracy(self) -> str:
        """검색 정확도 섹션 생성"""
        if not self.performance_results or 'retrieval_accuracy' not in self.performance_results:
            return "⚠️ 검색 정확도 데이터를 수집하지 못했습니다."
        
        accuracy = self.performance_results['retrieval_accuracy']
        content = []
        
        if 'precision_at_k' in accuracy:
            content.append("**Precision@K 결과**:")
            for metric, data in accuracy['precision_at_k'].items():
                if 'mean' in data:
                    content.append(f"- {metric.upper()}: {data['mean']:.3f}")
        
        if accuracy.get('errors', 0) > 0:
            content.append(f"- ⚠️ **오류 발생**: {accuracy['errors']}건")
        
        return '\n'.join(content) if content else "데이터 없음"
    
    def _generate_chatbot_quality(self) -> str:
        """챗봇 품질 섹션 생성"""
        if not self.quality_results or 'test_results' not in self.quality_results:
            return "⚠️ 챗봇 품질 데이터를 수집하지 못했습니다."
        
        test_results = self.quality_results['test_results']
        content = []
        
        # 기본 통계
        total = test_results.get('total_questions', 0)
        success = test_results.get('successful_responses', 0)
        failed = test_results.get('failed_responses', 0)
        
        content.append(f"- **총 테스트 질문**: {total}개")
        success_rate = success/total if total > 0 else 0
        content.append(f"- **성공률**: {success}/{total} ({success_rate:.1%})")
        
        # 평균 점수
        if 'average_scores' in test_results:
            avg_scores = test_results['average_scores']
            content.append("- **평균 점수**:")
            content.append(f"  - 관련성: {avg_scores.get('relevance', 0):.1f}/10")
            content.append(f"  - 완성도: {avg_scores.get('completeness', 0):.1f}/10")
            content.append(f"  - 정확도: {avg_scores.get('accuracy', 0):.1f}/10")
            content.append(f"  - 명확성: {avg_scores.get('clarity', 0):.1f}/10")
            content.append(f"  - 개념 포함도: {avg_scores.get('concept_coverage', 0):.1%}")
        
        return '\n'.join(content)
    
    def _generate_category_performance(self) -> str:
        """카테고리별 성능 섹션 생성"""
        if not self.quality_results or 'test_results' not in self.quality_results:
            return "⚠️ 카테고리별 성능 데이터를 사용할 수 없습니다."
        
        test_results = self.quality_results['test_results']
        
        if 'category_analysis' not in test_results:
            return "카테고리별 분석 데이터 없음"
        
        content = []
        for category, stats in test_results['category_analysis'].items():
            content.append(f"**{category}**")
            content.append(f"- 질문 수: {stats.get('question_count', 0)}개")
            content.append(f"- 평균 관련성: {stats.get('avg_relevance', 0):.1f}/10")
            content.append(f"- 평균 정확도: {stats.get('avg_accuracy', 0):.1f}/10")
            content.append(f"- 개념 포함도: {stats.get('avg_concept_coverage', 0):.1%}")
            content.append("")
        
        return '\n'.join(content)
    
    def _generate_response_patterns(self) -> str:
        """응답 패턴 섹션 생성"""
        if not self.quality_results or 'pattern_analysis' not in self.quality_results:
            return "⚠️ 응답 패턴 데이터를 사용할 수 없습니다."
        
        pattern = self.quality_results['pattern_analysis']
        content = []
        
        # 법적 근거 포함률
        if 'legal_reference_rate' in pattern:
            rate = pattern['legal_reference_rate']
            content.append(f"- **법적 근거 포함률**: {rate:.1%}")
        
        # 응답 길이 통계
        if 'response_length_stats' in pattern:
            length_stats = pattern['response_length_stats']
            content.append("- **응답 길이 통계**:")
            content.append(f"  - 평균: {length_stats.get('average', 0):.0f}자")
            content.append(f"  - 범위: {length_stats.get('min', 0)}자 ~ {length_stats.get('max', 0)}자")
        
        # 공통 문제점
        if 'common_issues' in pattern and pattern['common_issues']:
            content.append("- **주요 문제점**:")
            for issue, count in sorted(pattern['common_issues'].items(), 
                                     key=lambda x: x[1], reverse=True):
                content.append(f"  - {issue}: {count}회")
        
        return '\n'.join(content)
    
    def _generate_strengths(self) -> str:
        """강점 섹션 생성"""
        strengths = []
        
        if (self.quality_results and 'overall_assessment' in self.quality_results and 
            'strengths' in self.quality_results['overall_assessment']):
            for strength in self.quality_results['overall_assessment']['strengths']:
                strengths.append(f"✅ {strength}")
        
        # 기본 강점들
        default_strengths = [
            "✅ 한국어 법률 도메인 특화 시스템",
            "✅ 최신 임베딩 및 생성 모델 활용",
            "✅ 확장 가능한 클라우드 기반 아키텍처"
        ]
        
        if not strengths:
            strengths = default_strengths
        
        return '\n'.join(strengths)
    
    def _generate_weaknesses(self) -> str:
        """약점 섹션 생성"""
        weaknesses = []
        
        if (self.quality_results and 'overall_assessment' in self.quality_results and 
            'weaknesses' in self.quality_results['overall_assessment']):
            for weakness in self.quality_results['overall_assessment']['weaknesses']:
                weaknesses.append(f"⚠️ {weakness}")
        
        # 시스템 오류 기반 약점
        if self.performance_results and self.performance_results.get('total_errors', 0) > 0:
            weaknesses.append("⚠️ 시스템 안정성 개선 필요")
        
        if not weaknesses:
            weaknesses.append("🔍 추가 분석이 필요한 영역 없음")
        
        return '\n'.join(weaknesses)
    
    def _generate_technical_considerations(self) -> str:
        """기술적 고려사항 섹션 생성"""
        considerations = [
            "🔧 **확장성**: 더 많은 법률 데이터 처리를 위한 시스템 확장 고려",
            "🔒 **보안**: 민감한 법률 정보 처리를 위한 보안 강화",
            "⚡ **성능**: 실시간 응답을 위한 검색 및 생성 속도 최적화",
            "🔄 **업데이트**: 법률 변경사항 반영을 위한 주기적 데이터 업데이트",
            "📊 **모니터링**: 시스템 성능 및 품질 지속적 모니터링 체계"
        ]
        
        return '\n'.join(considerations)
    
    def _generate_short_term_improvements(self) -> str:
        """단기 개선방안 섹션 생성"""
        improvements = [
            "🎯 **응답 품질 개선**: 프롬프트 엔지니어링 및 컨텍스트 최적화",
            "⚡ **속도 최적화**: 캐싱 및 배치 처리 개선",
            "🔍 **검색 정확도 향상**: 더 정교한 청킹 및 메타데이터 활용",
            "🐛 **오류 처리 강화**: 예외 상황 대응 및 fallback 메커니즘 구현"
        ]
        
        return '\n'.join(improvements)
    
    def _generate_long_term_roadmap(self) -> str:
        """중장기 로드맵 섹션 생성"""
        roadmap = [
            "📚 **데이터 확장**: 판례, 법령, 해석례 등 다양한 법률 데이터 추가",
            "🤖 **모델 개선**: 법률 도메인 특화 파인튜닝 모델 개발",
            "🔗 **시스템 통합**: 기존 법률 정보 시스템과의 연동",
            "👥 **사용자 경험**: 개인화된 법률 상담 기능 추가",
            "📱 **멀티플랫폼**: 모바일 앱 및 API 서비스 제공"
        ]
        
        return '\n'.join(roadmap)
    
    def _generate_test_case_analysis(self) -> str:
        """테스트 케이스 분석 섹션 생성"""
        if not self.quality_results or 'test_results' not in self.quality_results:
            return "⚠️ 테스트 케이스 분석 데이터를 사용할 수 없습니다."
        
        test_results = self.quality_results['test_results']
        content = []
        
        if 'individual_results' in test_results:
            content.append(f"**총 {len(test_results['individual_results'])}개 테스트 케이스 분석**")
            content.append("")
            
            # 상위 및 하위 성과 케이스 분석
            results = test_results['individual_results']
            if results:
                # 관련성 점수 기준 정렬
                sorted_results = sorted(results, 
                                      key=lambda x: x['quality_evaluation']['relevance_score'], 
                                      reverse=True)
                
                if len(sorted_results) > 0:
                    best = sorted_results[0]
                    content.append("**최고 성과 케이스**:")
                    content.append(f"- 질문: {best['question'][:100]}...")
                    content.append(f"- 카테고리: {best['category']}")
                    content.append(f"- 관련성 점수: {best['quality_evaluation']['relevance_score']}/10")
                    content.append("")
                
                if len(sorted_results) > 1:
                    worst = sorted_results[-1]
                    content.append("**개선 필요 케이스**:")
                    content.append(f"- 질문: {worst['question'][:100]}...")
                    content.append(f"- 카테고리: {worst['category']}")
                    content.append(f"- 관련성 점수: {worst['quality_evaluation']['relevance_score']}/10")
                    content.append(f"- 주요 이슈: {', '.join(worst['quality_evaluation']['issues'])}")
        
        return '\n'.join(content)
    
    def _generate_error_analysis(self) -> str:
        """오류 분석 섹션 생성"""
        total_errors = 0
        error_details = []
        
        # 성능 분석 오류
        if self.performance_results:
            perf_errors = self.performance_results.get('total_errors', 0)
            total_errors += perf_errors
            
            if perf_errors > 0:
                error_details.append(f"- 성능 분석 오류: {perf_errors}건")
        
        # 품질 평가 오류
        if self.quality_results and 'test_results' in self.quality_results:
            quality_errors = self.quality_results['test_results'].get('failed_responses', 0)
            total_errors += quality_errors
            
            if quality_errors > 0:
                error_details.append(f"- 챗봇 응답 실패: {quality_errors}건")
        
        if total_errors == 0:
            return "✅ 분석 과정에서 발생한 오류가 없습니다."
        else:
            content = [f"⚠️ **총 {total_errors}개 오류 발생**", ""]
            content.extend(error_details)
            content.extend([
                "",
                "**권장 조치사항**:",
                "- 시스템 환경 설정 점검",
                "- API 키 및 네트워크 연결 확인",
                "- 오류 로깅 및 모니터링 강화"
            ])
            return '\n'.join(content)
    
    def _generate_conclusion(self) -> str:
        """결론 섹션 생성"""
        conclusion = []
        
        # 전체 평가 등급
        if (self.quality_results and 'overall_assessment' in self.quality_results and 
            'overall_grade' in self.quality_results['overall_assessment']):
            grade = self.quality_results['overall_assessment']['overall_grade']
            conclusion.append(f"**전체 시스템 평가: {grade}**")
            conclusion.append("")
        
        conclusion.extend([
            "본 분석을 통해 구축된 법률 AI 시스템은 다음과 같은 특징을 보입니다:",
            "",
            "1. **기술적 완성도**: 최신 AI 기술을 활용한 견고한 RAG 파이프라인 구축",
            "2. **도메인 특화**: 한국 법률 데이터에 특화된 처리 및 응답 생성",
            "3. **사용자 접근성**: 직관적인 웹 인터페이스를 통한 쉬운 접근",
            "",
            "향후 지속적인 개선과 확장을 통해 더욱 정확하고 유용한 법률 AI 서비스로 발전할 수 있을 것으로 기대됩니다.",
            "",
            "**주의사항**: 본 시스템의 답변은 참고용이며, 실제 법률 문제에 대해서는 반드시 전문 변호사와 상담하시기 바랍니다."
        ])
        
        return '\n'.join(conclusion)
    
    def generate_json_summary(self) -> str:
        """JSON 형식 요약 보고서 생성"""
        summary = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "analysis_duration": (datetime.now() - self.analysis_start_time).total_seconds(),
                "report_version": "1.0"
            },
            "performance_summary": self.performance_results,
            "quality_summary": self.quality_results,
            "key_findings": {
                "overall_status": "completed",
                "critical_issues": [],
                "recommendations": []
            }
        }
        
        # 중요 발견사항 추가
        if self.performance_results and self.performance_results.get('total_errors', 0) > 0:
            summary["key_findings"]["critical_issues"].append("시스템 안정성 개선 필요")
        
        if (self.quality_results and 'overall_assessment' in self.quality_results and 
            'recommendations' in self.quality_results['overall_assessment']):
            summary["key_findings"]["recommendations"] = self.quality_results['overall_assessment']['recommendations']
        
        return json.dumps(summary, indent=2, ensure_ascii=False)
    
    def generate_all_reports(self) -> List[str]:
        """모든 보고서 생성 및 저장"""
        generated_files = []
        
        try:
            # Markdown 보고서 생성
            markdown_content = self.generate_markdown_report()
            markdown_path = self.report_dir / "system_analysis_report.md"
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            generated_files.append(str(markdown_path))
            print(f"   ✅ Markdown 보고서 생성: {markdown_path}")
            
            # JSON 요약 보고서 생성
            json_content = self.generate_json_summary()
            json_path = self.report_dir / "analysis_summary.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                f.write(json_content)
            generated_files.append(str(json_path))
            print(f"   ✅ JSON 요약 생성: {json_path}")
            
            # 성능 데이터 상세 저장
            if self.performance_results:
                perf_path = self.report_dir / "performance_metrics.json"
                with open(perf_path, 'w', encoding='utf-8') as f:
                    json.dump(self.performance_results, f, indent=2, ensure_ascii=False)
                generated_files.append(str(perf_path))
                print(f"   ✅ 성능 메트릭 저장: {perf_path}")
            
            # 품질 데이터 상세 저장
            if self.quality_results:
                quality_path = self.report_dir / "quality_assessment.json"
                with open(quality_path, 'w', encoding='utf-8') as f:
                    json.dump(self.quality_results, f, indent=2, ensure_ascii=False)
                generated_files.append(str(quality_path))
                print(f"   ✅ 품질 평가 저장: {quality_path}")
            
        except Exception as e:
            print(f"   ❌ 보고서 생성 중 오류: {e}")
            raise
        
        return generated_files


if __name__ == "__main__":
    # 테스트용 더미 데이터
    dummy_performance = {"test": "performance_data"}
    dummy_quality = {"test": "quality_data"}
    
    generator = ReportGenerator(dummy_performance, dummy_quality, datetime.now())
    files = generator.generate_all_reports()
    
    print("생성된 보고서:")
    for file_path in files:
        print(f"  - {file_path}")