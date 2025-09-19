#!/usr/bin/env python3
"""
Simple test script to verify the RAG system works
간단한 RAG 시스템 테스트 스크립트
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Load environment
env_path = os.path.join(current_dir, '..', 'env', '.env')
load_dotenv(env_path)

print("🔧 환경 설정 확인...")
print(f"GOOGLE_API_KEY: {'✅' if os.getenv('GOOGLE_API_KEY') else '❌'}")
print(f"PINECONE_API_KEY: {'✅' if os.getenv('PINECONE_API_KEY') else '❌'}")

try:
    from app.embedding_client import EmbeddingClient
    from app.db_connection import VectorDB
    from app.config import NAMESPACE
    
    print("\n🤖 임베딩 클라이언트 테스트...")
    embedder = EmbeddingClient()
    
    # Test embedding
    test_text = "인사팀장도 사용자에 해당하나요?"
    print(f"테스트 텍스트: '{test_text}'")
    
    query_vector = embedder.embed_query(test_text)
    print(f"✅ 임베딩 성공: {len(query_vector)}차원")
    
    print("\n🗄️ 벡터 DB 연결 테스트...")
    vdb = VectorDB(dim=len(query_vector))
    
    # Check database status
    stats = vdb.index.describe_index_stats()
    total_vectors = stats.get('total_vector_count', 0)
    print(f"📊 총 벡터 수: {total_vectors}")
    
    if NAMESPACE in stats.get('namespaces', {}):
        namespace_vectors = stats['namespaces'][NAMESPACE].get('vector_count', 0)
        print(f"📊 네임스페이스 '{NAMESPACE}' 벡터 수: {namespace_vectors}")
        
        if namespace_vectors > 0:
            print("\n🔍 검색 테스트...")
            results = vdb.search(query_vector, top_k=3)
            print(f"검색 결과: {len(results.matches)}개")
            
            for i, match in enumerate(results.matches):
                print(f"  {i+1}. 점수: {match.score:.4f}, ID: {match.id}")
                if match.metadata:
                    case_name = match.metadata.get('사건명', 'Unknown')
                    case_number = match.metadata.get('사건번호', 'Unknown')
                    print(f"     사건: {case_name} ({case_number})")
        else:
            print("⚠️  데이터가 없습니다. 먼저 main.py를 실행하세요.")
    else:
        print(f"⚠️  네임스페이스 '{NAMESPACE}'가 없습니다.")
    
    print("\n🎉 모든 테스트 통과!")
    
except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    print(traceback.format_exc())