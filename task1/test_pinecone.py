#!/usr/bin/env python3
"""
Pinecone 연결 테스트 스크립트
"""

import os
import sys
from dotenv import load_dotenv
from pinecone import Pinecone

def test_pinecone_connection():
    """Pinecone 연결 및 설정 테스트"""
    
    # 환경변수 로드
    env_path = os.path.join(os.path.dirname(__file__), '..', 'env', '.env')
    print(f"🔧 환경변수 파일: {env_path}")
    load_dotenv(env_path)
    
    # API 키 확인
    api_key = os.getenv("PINECONE_API_KEY")
    print(f"🔑 Pinecone API 키: {'✅ 설정됨' if api_key else '❌ 없음'}")
    if api_key:
        print(f"   키 길이: {len(api_key)} 문자")
        print(f"   키 시작: {api_key[:10]}...")
    
    if not api_key:
        print("❌ PINECONE_API_KEY 환경변수가 설정되지 않았습니다.")
        return False
    
    try:
        # Pinecone 클라이언트 초기화
        print("\n📡 Pinecone 연결 시도...")
        pc = Pinecone(api_key=api_key)
        
        # 인덱스 목록 확인
        print("📋 인덱스 목록 조회 중...")
        indexes = pc.list_indexes()
        print(f"✅ 연결 성공!")
        print(f"📊 사용 가능한 인덱스: {len(indexes.get('indexes', []))}개")
        
        for idx in indexes.get('indexes', []):
            print(f"   - {idx.get('name', 'Unknown')}: {idx.get('status', 'Unknown')} 상태")
        
        # 설정된 인덱스 확인
        index_name = os.getenv("PINECONE_INDEX_NAME", "law-bot-korean")
        print(f"\n🎯 설정된 인덱스명: {index_name}")
        
        existing_names = {ix["name"] for ix in indexes.get("indexes", [])}
        if index_name in existing_names:
            print(f"✅ 인덱스 '{index_name}' 존재함")
            
            # 인덱스 상세 정보
            index = pc.Index(index_name)
            stats = index.describe_index_stats()
            print(f"📈 인덱스 통계:")
            print(f"   - 총 벡터 수: {stats.get('total_vector_count', 0)}")
            print(f"   - 차원: {stats.get('dimension', 'Unknown')}")
            
        else:
            print(f"⚠️  인덱스 '{index_name}' 없음")
            print("🔧 새 인덱스가 생성될 예정입니다.")
        
        return True
        
    except Exception as e:
        print(f"❌ Pinecone 연결 실패: {e}")
        print(f"🔍 오류 타입: {type(e).__name__}")
        
        # 자주 발생하는 오류별 해결방법 제시
        error_str = str(e).lower()
        if "unauthorized" in error_str or "401" in error_str:
            print("💡 해결방법: API 키가 잘못되었을 수 있습니다.")
        elif "forbidden" in error_str or "403" in error_str:
            print("💡 해결방법: API 키 권한을 확인하세요.")
        elif "network" in error_str or "connection" in error_str:
            print("💡 해결방법: 네트워크 연결을 확인하세요.")
        
        return False

if __name__ == "__main__":
    print("🚀 Pinecone 연결 테스트 시작\n")
    success = test_pinecone_connection()
    
    if success:
        print("\n🎉 모든 테스트 통과!")
    else:
        print("\n💥 연결 테스트 실패")
        print("📋 확인사항:")
        print("1. PINECONE_API_KEY 환경변수 설정")
        print("2. API 키 유효성")
        print("3. 네트워크 연결")
        print("4. Pinecone 계정 상태")
        sys.exit(1)