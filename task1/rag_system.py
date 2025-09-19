#!/usr/bin/env python3
"""
Complete RAG Query System for Legal Case Retrieval
법률 판례 검색을 위한 완전한 RAG 시스템
"""

import os
import sys
import json
import traceback
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import INDEX_NAME, NAMESPACE
from app.embedding_client import EmbeddingClient
from app.db_connection import VectorDB


class LegalRAGSystem:
    """법률 판례 검색을 위한 RAG 시스템"""
    
    def __init__(self):
        """Initialize the RAG system components"""
        print("🚀 Legal RAG System 초기화 중...")
        
        # Load environment variables
        env_path = os.path.join(os.path.dirname(__file__), '..', 'env', '.env')
        load_dotenv(env_path)
        
        # Initialize components
        self.embedder = None
        self.vdb = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize embedding client and vector database"""
        try:
            # Initialize embedding client
            print("🤖 임베딩 클라이언트 초기화 중...")
            self.embedder = EmbeddingClient()
            print("✅ 임베딩 클라이언트 초기화 완료")
            
            # Initialize vector database with appropriate dimension
            print("🗄️ 벡터 데이터베이스 연결 중...")
            self.vdb = VectorDB(dim=768)  # Gemini embedding dimension
            
            # Check database status
            stats = self.vdb.index.describe_index_stats()
            total_vectors = stats.get('total_vector_count', 0)
            namespace_vectors = 0
            
            if NAMESPACE in stats.get('namespaces', {}):
                namespace_vectors = stats['namespaces'][NAMESPACE].get('vector_count', 0)
            
            print(f"✅ 벡터 DB 연결 완료")
            print(f"📊 데이터베이스 상태:")
            print(f"   - 총 벡터 수: {total_vectors}")
            print(f"   - 네임스페이스 '{NAMESPACE}' 벡터 수: {namespace_vectors}")
            
            if namespace_vectors == 0:
                print("⚠️  경고: 데이터베이스에 벡터가 없습니다!")
                print("   먼저 task1/main.py를 실행하여 데이터를 색인화하세요.")
            
        except Exception as e:
            print(f"❌ 초기화 실패: {e}")
            print(f"🔍 오류 상세: {traceback.format_exc()}")
            raise
    
    def query(self, question: str, top_k: int = 5, min_score: float = 0.3) -> List[Dict[str, Any]]:
        """
        Execute a RAG query to find relevant legal cases
        
        Args:
            question: 질문 텍스트
            top_k: 반환할 결과 수
            min_score: 최소 유사도 점수
        
        Returns:
            List of relevant case information
        """
        print(f"\n🔍 질문 처리 중: '{question}'")
        
        if not self.embedder or not self.vdb:
            raise RuntimeError("RAG 시스템이 초기화되지 않았습니다.")
        
        try:
            # Step 1: Generate query embedding
            print("🤖 질문 임베딩 생성 중...")
            query_vector = self.embedder.embed_query(question)
            print(f"✅ 임베딩 완료: {len(query_vector)}차원")
            
            # Step 2: Search vector database
            print(f"🔍 유사한 판례 검색 중 (상위 {top_k}개)...")
            search_results = self.vdb.search(query_vector, top_k=top_k)
            
            print(f"📊 검색 결과: {len(search_results.matches)}개 발견")
            
            # Step 3: Process and format results
            formatted_results = []
            relevant_count = 0
            
            for i, match in enumerate(search_results.matches):
                score = match.score
                metadata = match.metadata or {}
                
                # Filter by minimum score
                if score < min_score:
                    print(f"   ⏭️  결과 {i+1}: 점수 {score:.4f} (임계값 {min_score} 미만)")
                    continue
                
                relevant_count += 1
                
                # Extract metadata safely
                case_info = {
                    "rank": relevant_count,
                    "similarity_score": score,
                    "match_id": match.id,
                    "case_id": metadata.get('판례정보일련번호', 'Unknown'),
                    "case_name": metadata.get('사건명', 'Unknown'),
                    "case_number": metadata.get('사건번호', 'Unknown'),
                    "court": metadata.get('법원명', 'Unknown'),
                    "date": metadata.get('선고일자', 'Unknown'),
                    "case_type": metadata.get('사건종류명', 'Unknown'),
                    "judgment_type": metadata.get('판결유형', 'Unknown'),
                    "key_issues": metadata.get('판시사항', ''),
                    "judgment_summary": metadata.get('판결요지', ''),
                    "referenced_laws": metadata.get('참조조문', ''),
                    "chunk_type": metadata.get('chunk_type', 'Unknown')
                }
                
                formatted_results.append(case_info)
                
                print(f"   ✅ 결과 {relevant_count}: 점수 {score:.4f}")
                print(f"      사건: {case_info['case_name']} ({case_info['case_number']})")
                print(f"      법원: {case_info['court']} ({case_info['date']})")
            
            if not formatted_results:
                print(f"⚠️  관련성 높은 결과가 없습니다 (최소 점수: {min_score})")
            else:
                print(f"🎯 관련성 높은 결과: {len(formatted_results)}개")
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ 검색 실패: {e}")
            print(f"🔍 오류 상세: {traceback.format_exc()}")
            return []
    
    def detailed_result(self, case_info: Dict[str, Any]) -> str:
        """Format a detailed result for display"""
        result = f"""
📄 판례 정보 (랭킹 #{case_info['rank']}, 유사도: {case_info['similarity_score']:.4f})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏛️ 사건명: {case_info['case_name']}
📋 사건번호: {case_info['case_number']}
⚖️ 법원: {case_info['court']}
📅 선고일자: {case_info['date']}
📂 사건종류: {case_info['case_type']}

📝 판시사항:
{case_info['key_issues'][:500]}{'...' if len(case_info['key_issues']) > 500 else ''}

⚖️ 판결요지:
{case_info['judgment_summary'][:1000]}{'...' if len(case_info['judgment_summary']) > 1000 else ''}

📚 참조조문:
{case_info['referenced_laws'][:200]}{'...' if len(case_info['referenced_laws']) > 200 else ''}
"""
        return result
    
    def answer_question(self, question: str, max_results: int = 3) -> str:
        """
        Provide a comprehensive answer based on relevant legal cases
        """
        print(f"\n❓ 질문 답변 생성 중...")
        
        # Get relevant cases
        results = self.query(question, top_k=max_results, min_score=0.3)
        
        if not results:
            return f"""
❌ 질문: "{question}"

죄송합니다. 관련된 판례를 찾을 수 없습니다.

💡 제안사항:
- 다른 키워드를 사용해 보세요
- 더 구체적이거나 더 일반적인 질문을 시도해 보세요
- 법률 용어를 포함한 질문을 사용해 보세요
"""
        
        # Build comprehensive answer
        answer = f"""
❓ 질문: "{question}"

📊 검색 결과: {len(results)}개의 관련 판례를 찾았습니다.

"""
        
        for i, case in enumerate(results):
            answer += f"""
{'='*80}
{case['case_name']} ({case['case_number']})
유사도: {case['similarity_score']:.4f} | {case['court']} | {case['date']}
{'='*80}

📝 판시사항:
{case['key_issues'][:300]}{'...' if len(case['key_issues']) > 300 else ''}

⚖️ 판결요지:
{case['judgment_summary'][:600]}{'...' if len(case['judgment_summary']) > 600 else ''}

"""
        
        return answer


def test_rag_system():
    """Test the RAG system with sample queries"""
    print("🧪 RAG 시스템 테스트 시작")
    
    try:
        # Initialize RAG system
        rag = LegalRAGSystem()
        
        # Test queries from the QnA sample
        test_queries = [
            "인사팀장도 사용자에 해당하나요?",
            "상무이사가 근로기준법상 근로자에 해당되는지",
            "공장도 상가임대차법의 보호를 받나요?",
            "기존 시설을 인수한 경우 원상회복 의무",
            "임대인을 상대로 권리금을 청구할 수 있나요?"
        ]
        
        for i, query in enumerate(test_queries):
            print(f"\n{'='*100}")
            print(f"테스트 {i+1}/{len(test_queries)}")
            print(f"{'='*100}")
            
            # Get answer
            answer = rag.answer_question(query, max_results=2)
            print(answer)
            
            print(f"{'='*100}")
            print(f"테스트 {i+1} 완료")
            print(f"{'='*100}")
        
        print("\n🎉 모든 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        print(f"🔍 오류 상세: {traceback.format_exc()}")


def interactive_query():
    """Interactive query mode"""
    print("🎯 대화형 질문 모드 시작")
    print("(종료하려면 'quit' 또는 'exit' 입력)")
    
    try:
        rag = LegalRAGSystem()
        
        while True:
            print("\n" + "="*80)
            question = input("💬 질문을 입력하세요: ").strip()
            
            if question.lower() in ['quit', 'exit', '종료', '나가기']:
                print("👋 대화형 모드를 종료합니다.")
                break
            
            if not question:
                print("⚠️  질문을 입력해주세요.")
                continue
            
            # Get and display answer
            answer = rag.answer_question(question)
            print(answer)
    
    except KeyboardInterrupt:
        print("\n👋 사용자에 의해 종료되었습니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")


if __name__ == "__main__":
    print("🏛️ Legal RAG System v1.0")
    print("=" * 50)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "test":
            test_rag_system()
        elif mode == "interactive":
            interactive_query()
        else:
            print(f"❌ 알 수 없는 모드: {mode}")
            print("사용법: python rag_system.py [test|interactive]")
    else:
        # Default: run test mode
        test_rag_system()