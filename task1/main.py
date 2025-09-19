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
    """Process cases by sections for memory efficiency and stability"""
    print("Task1 starting: Processing cases by sections")
    
    records = parse_cases(DATA_JSON)
    print(f"Total {len(records)} cases parsed successfully")
    
    # Initialize embedding client
    embedder = EmbeddingClient()
    
    # Initialize VectorDB (dimension will be set from first case)
    vdb = None
    total_processed = 0
    
    for case_idx, rec in enumerate(records):
        print(f"\nProcessing case {case_idx + 1}/{len(records)}: {rec.get('title', 'Unknown')}")
        
        # Generate chunks for current case
        case_entries = build_chunk_entries(rec, CHUNK_MIN, CHUNK_MAX, CHUNK_OVERLAP)
        print(f"   Number of chunks: {len(case_entries)}")
        
        if not case_entries:
            print("   Warning: Empty case, skipping")
            continue
        
        # Generate embeddings for case texts
        texts = [e["text"] for e in case_entries]
        print(f"   Generating embeddings...")
        
        try:
            emb_out = embedder.embed(texts, batch_size=8)  # Small batch size for stability
            vectors, dim = emb_out["embeddings"], emb_out["dim"]
            print(f"   Embeddings complete: {vectors.shape}")
            
            # Initialize VectorDB (on first successful case)
            if vdb is None:
                print(f"   Initializing VectorDB (dimension: {dim})")
                vdb = VectorDB(dim=dim)
            
            # Use case serial number as ID (ASCII compatible)
            ids = []
            for e in case_entries:
                # Create unique ID using case serial number + chunk index
                case_id = e.get('source_id', 'unknown')  # Case serial number
                chunk_idx = e.get('chunk_idx', 0)
                unique_id = f"{case_id}_summary_{chunk_idx}"  # Fixed as summary
                ids.append(unique_id)
            
            metas = [e["meta"] for e in case_entries]
            
            # Upload to Pinecone in batches
            batch_size = 64  # Pinecone batch size
            for i in range(0, len(ids), batch_size):
                batch_ids = ids[i:i+batch_size]
                batch_vecs = [vectors[j].tolist() for j in range(i, min(i+batch_size, len(vectors)))]
                batch_metas = metas[i:i+batch_size]
                
                print(f"   Uploading batch: {len(batch_ids)} vectors")
                vdb.upsert(batch_ids, batch_vecs, batch_metas)
                print(f"   Upload complete: {batch_ids[0]} ... {batch_ids[-1]}")
            
            total_processed += len(case_entries)
            print(f"   Case complete. Total processed: {total_processed} chunks")
            
        except Exception as e:
            print(f"   Error processing case: {e}")
            print(f"   Continuing to next case...")
            continue
    
    print(f"\nTask1 complete!")
    print(f"Final statistics:")
    print(f"   - Processed cases: {len(records)}")
    print(f"   - Total chunks: {total_processed}")
    print(f"   - VectorDB status: {'Initialized successfully' if vdb else 'Initialization failed'}")


if __name__ == "__main__":
    run_task1()