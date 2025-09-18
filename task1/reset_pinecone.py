#!/usr/bin/env python3
"""
Pinecone 인덱스 초기화 스크립트
"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone

def reset_pinecone_index():
    """Pinecone 인덱스 초기화"""
    
    # 환경변수 로드
    env_path = os.path.join(os.path.dirname(__file__), '..', 'env', '.env')
    load_dotenv(env_path)
    
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        print("❌ PINECONE_API_KEY 환경변수가 설정되지 않았습니다.")
        return False
    
    index_name = os.getenv("PINECONE_INDEX_NAME", "law-bot-korean")
    
    try:
        print("🔧 Pinecone 클라이언트 초기화...")
        pc = Pinecone(api_key=api_key)
        
        # 기존 인덱스 확인 및 삭제
        indexes = pc.list_indexes()
        existing_names = {ix["name"] for ix in indexes.get("indexes", [])}
        
        if index_name in existing_names:
            print(f"🗑️  기존 인덱스 '{index_name}' 삭제 중...")
            pc.delete_index(index_name)
            print("✅ 인덱스 삭제 완료")
            
            # 삭제 완료 대기
            import time
            print("⏳ 삭제 완료 대기 중 (10초)...")
            time.sleep(10)
        else:
            print(f"ℹ️  인덱스 '{index_name}'가 존재하지 않습니다.")
        
        print("🎯 인덱스 초기화 완료!")
        print("📋 다음 단계: python main.py 실행하여 새 데이터 업로드")
        
        return True
        
    except Exception as e:
        print(f"❌ 인덱스 초기화 실패: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Pinecone 인덱스 초기화 시작\n")
    
    print("⚠️  기존 데이터가 모두 삭제됩니다!")
    response = input("계속하시겠습니까? (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        success = reset_pinecone_index()
        
        if success:
            print("\n🎉 초기화 완료!")
        else:
            print("\n💥 초기화 실패")
    else:
        print("❌ 작업이 취소되었습니다.")