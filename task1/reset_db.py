#!/usr/bin/env python3
"""
Pinecone DB 초기화 스크립트
"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

def reset_pinecone_db():
    """Pinecone 인덱스를 삭제하고 재생성"""
    
    # 환경변수 로드
    env_path = os.path.join(os.path.dirname(__file__), '..', 'env', '.env')
    load_dotenv(env_path)
    
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        print("❌ PINECONE_API_KEY 환경변수가 설정되지 않았습니다.")
        return False
    
    # 설정값
    index_name = os.getenv("PINECONE_INDEX_NAME", "law-bot-korean")
    cloud = os.getenv("PINECONE_CLOUD", "aws")
    region = os.getenv("PINECONE_REGION", "us-east-1")
    
    try:
        print("🔧 Pinecone 클라이언트 초기화...")
        pc = Pinecone(api_key=api_key)
        
        # 기존 인덱스 확인 및 삭제
        indexes = pc.list_indexes()
        existing_names = {ix["name"] for ix in indexes.get("indexes", [])}
        
        if index_name in existing_names:
            print(f"🗑️  기존 인덱스 '{index_name}' 삭제 중...")
            pc.delete_index(index_name)
            print("✅ 삭제 완료")
            
            # 삭제 완료 대기
            import time
            print("⏳ 삭제 완료 대기 중...")
            time.sleep(15)
        else:
            print(f"ℹ️  인덱스 '{index_name}'가 존재하지 않습니다.")
        
        # 새 인덱스 생성 (3072차원 - Gemini embedding)
        print(f"🏗️  새 인덱스 생성 중...")
        print(f"   이름: {index_name}")
        print(f"   차원: 3072 (Gemini Embedding)")
        print(f"   메트릭: cosine")
        print(f"   클라우드: {cloud}")
        print(f"   지역: {region}")
        
        pc.create_index(
            name=index_name,
            dimension=3072,  # Gemini embedding 차원
            metric="cosine",
            spec=ServerlessSpec(
                cloud=cloud,
                region=region
            )
        )
        
        print("✅ 인덱스 생성 완료!")
        
        # 생성 확인
        import time
        print("⏳ 인덱스 준비 대기 중...")
        time.sleep(10)
        
        indexes = pc.list_indexes()
        for idx in indexes.get('indexes', []):
            if idx.get('name') == index_name:
                print(f"📊 인덱스 상태: {idx.get('status', 'Unknown')}")
                break
        
        print(f"\n🎉 DB 초기화 완료!")
        print(f"📋 다음 단계: python main.py 실행하여 데이터 업로드")
        
        return True
        
    except Exception as e:
        print(f"❌ DB 초기화 실패: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Pinecone DB 초기화 시작\n")
    
    print("⚠️  주의: 기존 데이터가 모두 삭제됩니다!")
    response = input("계속하시겠습니까? (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        reset_pinecone_db()
    else:
        print("❌ 작업이 취소되었습니다.")