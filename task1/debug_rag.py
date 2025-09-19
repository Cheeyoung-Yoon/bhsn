#!/usr/bin/env python3
"""
Debug script to check RAG system status and test queries
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import INDEX_NAME, NAMESPACE
from app.embedding_client import EmbeddingClient
from app.db_connection import VectorDB
import json


def check_db_status():
    """Check the current status of the vector database"""
    print("🔍 Checking vector database status...")
    
    try:
        # Initialize with a dummy dimension first to check if index exists
        vdb = VectorDB(dim=768)  # Common embedding dimension
        
        # Get index stats
        stats = vdb.index.describe_index_stats()
        print(f"📊 Index stats:")
        print(f"   - Total vectors: {stats.get('total_vector_count', 0)}")
        print(f"   - Dimension: {stats.get('dimension', 'Unknown')}")
        print(f"   - Namespaces: {list(stats.get('namespaces', {}).keys())}")
        
        if NAMESPACE in stats.get('namespaces', {}):
            namespace_stats = stats['namespaces'][NAMESPACE]
            print(f"   - Vectors in '{NAMESPACE}': {namespace_stats.get('vector_count', 0)}")
        else:
            print(f"   - Namespace '{NAMESPACE}' not found!")
            
        return vdb
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return None


def test_search_functionality(vdb, embedder):
    """Test the search functionality with sample queries"""
    print("\n🧪 Testing search functionality...")
    
    # Test queries from the QnA sample
    test_queries = [
        "인사팀장도 사용자에 해당하나요?",
        "상무이사가 근로기준법상 근로자에 해당되는지",
        "사용자의 범위",
        "근로자 지휘 감독",
        "권한과 책임"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        try:
            # Generate query embedding
            query_vector = embedder.embed_query(query)
            print(f"   ✅ Query embedding generated: {len(query_vector)} dimensions")
            
            # Search for similar vectors
            results = vdb.search(query_vector, top_k=3)
            print(f"   📊 Found {len(results.matches)} matches")
            
            if results.matches:
                for i, match in enumerate(results.matches):
                    score = match.score
                    metadata = match.metadata or {}
                    case_id = metadata.get('판례정보일련번호', 'Unknown')
                    case_name = metadata.get('사건명', 'Unknown')
                    print(f"   📄 Match {i+1}: Score={score:.4f}, Case={case_id}, Name='{case_name[:50]}...'")
            else:
                print("   ⚠️  No matches found!")
                
        except Exception as e:
            print(f"   ❌ Error during search: {e}")


def sample_stored_data(vdb):
    """Sample some stored data to see what's in the database"""
    print("\n📋 Sampling stored data...")
    
    try:
        # Try to fetch some vectors to see what's stored
        # This is a bit tricky with Pinecone as it doesn't have a direct "list all" function
        # We'll try searching with a random vector
        import numpy as np
        
        stats = vdb.index.describe_index_stats()
        dim = stats.get('dimension', 768)
        
        # Create a random query vector
        random_vector = np.random.random(dim).tolist()
        results = vdb.search(random_vector, top_k=5)
        
        print(f"   📊 Random sample ({len(results.matches)} items):")
        for i, match in enumerate(results.matches):
            metadata = match.metadata or {}
            case_id = metadata.get('판례정보일련번호', 'Unknown')
            case_name = metadata.get('사건명', 'Unknown')
            chunk_type = metadata.get('chunk_type', 'Unknown')
            print(f"   📄 Item {i+1}: ID={match.id}, Case={case_id}, Type={chunk_type}")
            print(f"        Name: {case_name[:80]}...")
            
    except Exception as e:
        print(f"   ❌ Error sampling data: {e}")


def create_rag_query_function():
    """Create a complete RAG query function"""
    print("\n🔧 Creating RAG query function...")
    
    rag_code = '''
def rag_query(query_text: str, top_k: int = 5):
    """
    Complete RAG query function that finds relevant legal cases
    """
    from app.embedding_client import EmbeddingClient
    from app.db_connection import VectorDB
    
    print(f"🔍 Processing query: '{query_text}'")
    
    # Initialize components
    embedder = EmbeddingClient()
    vdb = VectorDB(dim=768)  # Adjust dimension as needed
    
    try:
        # Generate query embedding
        query_vector = embedder.embed_query(query_text)
        
        # Search for similar vectors
        results = vdb.search(query_vector, top_k=top_k)
        
        print(f"📊 Found {len(results.matches)} relevant cases")
        
        # Format results
        formatted_results = []
        for i, match in enumerate(results.matches):
            metadata = match.metadata or {}
            
            result = {
                "rank": i + 1,
                "similarity_score": match.score,
                "case_id": metadata.get('판례정보일련번호', 'Unknown'),
                "case_name": metadata.get('사건명', 'Unknown'),
                "case_number": metadata.get('사건번호', 'Unknown'),
                "court": metadata.get('법원명', 'Unknown'),
                "date": metadata.get('선고일자', 'Unknown'),
                "chunk_type": metadata.get('chunk_type', 'Unknown'),
                "content": metadata.get('text', 'No content available')
            }
            formatted_results.append(result)
            
            print(f"📄 Result {i+1}: Score={match.score:.4f}")
            print(f"    Case: {result['case_name']} ({result['case_number']})")
            print(f"    Content: {result['content'][:200]}...")
            print()
        
        return formatted_results
        
    except Exception as e:
        print(f"❌ Error during RAG query: {e}")
        return []
'''
    
    # Save the RAG function to a file
    with open("rag_query_function.py", "w", encoding="utf-8") as f:
        f.write(rag_code)
    
    print("✅ RAG query function saved to 'rag_query_function.py'")


def main():
    """Main debug function"""
    print("🚀 Starting RAG system debug...")
    
    # Check database status
    vdb = check_db_status()
    if not vdb:
        print("❌ Cannot continue without database connection")
        return
    
    # Initialize embedding client
    try:
        embedder = EmbeddingClient()
        print("✅ Embedding client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize embedding client: {e}")
        return
    
    # Sample stored data
    sample_stored_data(vdb)
    
    # Test search functionality
    test_search_functionality(vdb, embedder)
    
    # Create RAG query function
    create_rag_query_function()
    
    print("\n🎉 Debug complete!")


if __name__ == "__main__":
    main()