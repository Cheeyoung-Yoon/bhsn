import itertools

from numpy import iterable
from app.config import DATA_JSON, CHUNK_MIN, CHUNK_MAX, CHUNK_OVERLAP
from app.parser import parse_cases
from app.chunker import build_chunk_entries
from app.embedding_client import EmbeddingClient
# from app.db_connection import VectorDB


def batched(iterable, n):
    it = iter(iterable)
    while True:
        batch = list(itertools.islice(it, n))
        if not batch:
            break
        yield batch


def run_task1():
    records = parse_cases(DATA_JSON)
    entries = []
    for rec in records:
        entries.extend(build_chunk_entries(rec, CHUNK_MIN, CHUNK_MAX, CHUNK_OVERLAP))
        print(f"총 청크 수: {len(entries)}")


    texts = [e["text"] for e in entries]
    embedder = EmbeddingClient()
    emb_out = embedder.embed(texts)
    vectors, dim = emb_out["embeddings"], emb_out["dim"]
    print(f"임베딩 완료: {vectors.shape}")


    # vdb = VectorDB(dim=dim)
    ids = [f"{e['source_id']}::{e['chunk_type']}::{e['chunk_idx']}" for e in entries]
    metas = [e["meta"] for e in entries]


    for batch_idx in batched(range(len(ids)), 128):
        b_ids = [ids[j] for j in batch_idx]
        b_vecs = [vectors[j].tolist() for j in batch_idx]
        b_meta = [metas[j] for j in batch_idx]
        # vdb.upsert(b_ids, b_vecs, b_meta)
        print(b_ids[0], "...", b_ids[-1])
        print(f"업서트 완료: {len(b_ids)}개")
        print("-----")
        print(b_meta)
    print("✅ Task1 완료")


if __name__ == "__main__":
    run_task1()