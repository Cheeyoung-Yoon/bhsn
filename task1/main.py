import itertools

from numpy import iterable
from app.config import DATA_JSON, CHUNK_MIN, CHUNK_MAX, CHUNK_OVERLAP
from app.parser import parse_cases
from app.chunker import build_chunk_entries
from app.embedding_client import EmbeddingClient
from app.db_connection import VectorDB


def batched(iterable, n):
    it = iter(iterable)
    while True:
        batch = list(itertools.islice(it, n))
        if not batch:
            break
        yield batch


def run_task1():
    """섹션별 처리로 메모리 효율성과 안정성 향상"""
    print("🚀 Task1 시작: 케이스별 섹션 처리")
    
    records = parse_cases(DATA_JSON)
    print(f"📚 총 {len(records)}개 케이스 파싱 완료")
    
    # 임베딩 클라이언트 초기화
    embedder = EmbeddingClient()
    
    # VectorDB 초기화 (첫 번째 케이스에서 차원 설정)
    vdb = None
    total_processed = 0
    
    for case_idx, rec in enumerate(records):
        print(f"\n📋 케이스 {case_idx + 1}/{len(records)} 처리 중: {rec.get('title', 'Unknown')}")
        
        # 현재 케이스의 청크 생성
        case_entries = build_chunk_entries(rec, CHUNK_MIN, CHUNK_MAX, CHUNK_OVERLAP)
        print(f"   📝 청크 수: {len(case_entries)}")
        
        if not case_entries:
            print("   ⚠️  빈 케이스, 건너뜀")
            continue
        
        # 케이스별 텍스트 임베딩 생성
        texts = [e["text"] for e in case_entries]
        print(f"   🔄 임베딩 생성 중...")
        
        try:
            emb_out = embedder.embed(texts, batch_size=8)  # 작은 배치 크기로 안정성 향상
            vectors, dim = emb_out["embeddings"], emb_out["dim"]
            print(f"   ✅ 임베딩 완료: {vectors.shape}")
            
            # VectorDB 초기화 (첫 번째 성공한 케이스에서)
            if vdb is None:
                print(f"   🔧 VectorDB 초기화 (차원: {dim})")
                vdb = VectorDB(dim=dim)
            
            # 판례정보일련번호를 ID로 사용 (ASCII 호환)
            ids = []
            for e in case_entries:
                # 판례정보일련번호 + 청크인덱스로 고유 ID 생성 (판결요지만 처리하므로 간단)
                case_id = e.get('source_id', 'unknown')  # 판례정보일련번호
                chunk_idx = e.get('chunk_idx', 0)
                unique_id = f"{case_id}_summary_{chunk_idx}"  # summary로 고정
                ids.append(unique_id)
            
            metas = [e["meta"] for e in case_entries]
            
            # 배치별로 Pinecone에 업로드
            batch_size = 64  # Pinecone 배치 크기
            for i in range(0, len(ids), batch_size):
                batch_ids = ids[i:i+batch_size]
                batch_vecs = [vectors[j].tolist() for j in range(i, min(i+batch_size, len(vectors)))]
                batch_metas = metas[i:i+batch_size]
                
                print(f"   📤 배치 업로드: {len(batch_ids)}개 벡터")
                vdb.upsert(batch_ids, batch_vecs, batch_metas)
                print(f"   ✅ 업로드 완료: {batch_ids[0]} ... {batch_ids[-1]}")
            
            total_processed += len(case_entries)
            print(f"   🎯 케이스 완료. 누적 처리: {total_processed}개 청크")
            
        except Exception as e:
            print(f"   ❌ 케이스 처리 실패: {e}")
            print(f"   ⏭️  다음 케이스로 계속...")
            continue
    
    print(f"\n🎉 Task1 완료!")
    print(f"📊 최종 통계:")
    print(f"   - 처리된 케이스: {len(records)}개")
    print(f"   - 총 청크 수: {total_processed}개")
    print(f"   - VectorDB 상태: {'초기화 완료' if vdb else '초기화 실패'}")


if __name__ == "__main__":
    run_task1()