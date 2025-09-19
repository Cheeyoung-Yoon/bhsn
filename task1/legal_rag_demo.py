#!/usr/bin/env python3
"""
Legal RAG System Demo
Complete demonstration of the legal case retrieval system
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

from app.embedding_client import EmbeddingClient
from app.db_connection import VectorDB
from app.config import NAMESPACE


class LegalRAGDemo:
    """Complete demonstration of the Legal RAG system"""
    
    def __init__(self):
        """Initialize the RAG system"""
        print("=== Legal RAG System Demo ===")
        print("Initializing system components...")
        
        self.embedder = EmbeddingClient()
        self.vdb = VectorDB(dim=3072)  # Gemini embedding dimension
        
        # Check system status
        self._check_system_status()
    
    def _check_system_status(self):
        """Check if the system is ready"""
        stats = self.vdb.index.describe_index_stats()
        total_vectors = stats.get('total_vector_count', 0)
        
        if NAMESPACE in stats.get('namespaces', {}):
            namespace_vectors = stats['namespaces'][NAMESPACE].get('vector_count', 0)
            print(f"System ready: {namespace_vectors} legal cases indexed")
        else:
            print("Warning: No data found. Please run main.py first.")
            return False
        
        return True
    
    def query(self, question: str, top_k: int = 3, detailed: bool = True):
        """Execute a RAG query"""
        print(f"\nQuery: '{question}'")
        print("-" * 80)
        
        try:
            # Generate query embedding
            query_vector = self.embedder.embed_query(question)
            
            # Search for similar cases
            results = self.vdb.search(query_vector, top_k=top_k)
            
            if not results.matches:
                print("No relevant cases found.")
                return []
            
            # Process results
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
                    "case_type": metadata.get('사건종류명', 'Unknown'),
                    "key_issues": metadata.get('판시사항', ''),
                    "judgment_summary": metadata.get('판결요지', ''),
                    "content": metadata.get('text', 'Content not available')
                }
                formatted_results.append(result)
                
                if detailed:
                    self._display_result(result)
            
            return formatted_results
            
        except Exception as e:
            print(f"Error during search: {e}")
            return []
    
    def _display_result(self, result):
        """Display a single search result"""
        print(f"\nResult #{result['rank']} (Similarity: {result['similarity_score']:.4f})")
        print(f"Case: {result['case_name']} ({result['case_number']})")
        print(f"Court: {result['court']} | Date: {result['date']}")
        print(f"Type: {result['case_type']}")
        
        if result['key_issues']:
            print(f"\nKey Issues:")
            print(f"{result['key_issues'][:200]}{'...' if len(result['key_issues']) > 200 else ''}")
        
        if result['content'] and result['content'] != 'Content not available':
            print(f"\nContent:")
            print(f"{result['content'][:300]}{'...' if len(result['content']) > 300 else ''}")
        
        print("-" * 60)
    
    def demo_with_sample_questions(self):
        """Run demo with sample questions from QnA dataset"""
        print("\n" + "="*80)
        print("DEMO: Testing with Sample Legal Questions")
        print("="*80)
        
        # Load sample questions
        sample_questions = [
            "인사팀장도 사용자에 해당하나요?",
            "Is the HR manager considered an employer?",
            "상무이사가 근로기준법상 근로자에 해당되는지",
            "공장도 상가임대차법의 보호를 받나요?",
            "임대인을 상대로 권리금을 청구할 수 있나요?",
            "근로자의 지휘 감독",
            "사용자의 권한과 책임"
        ]
        
        for i, question in enumerate(sample_questions):
            print(f"\n{'='*20} Question {i+1}/{len(sample_questions)} {'='*20}")
            self.query(question, top_k=2)
    
    def interactive_mode(self):
        """Interactive query mode"""
        print("\n" + "="*80)
        print("INTERACTIVE MODE")
        print("Type your legal questions below. Type 'quit' to exit.")
        print("="*80)
        
        while True:
            try:
                question = input("\nYour question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("Exiting interactive mode.")
                    break
                
                if not question:
                    print("Please enter a question.")
                    continue
                
                self.query(question, top_k=3)
                
            except KeyboardInterrupt:
                print("\nExiting interactive mode.")
                break
    
    def benchmark_similarity_scores(self):
        """Benchmark similarity scores for known questions"""
        print("\n" + "="*80)
        print("BENCHMARK: Similarity Score Analysis")
        print("="*80)
        
        known_pairs = [
            ("인사팀장도 사용자에 해당하나요?", "Expected high similarity for HR manager case"),
            ("상무이사가 근로기준법상 근로자인가?", "Expected high similarity for executive worker case"),
            ("임대차 권리금 회수", "Expected high similarity for lease rights case"),
            ("부동산 매매", "Expected low similarity (not in dataset)"),
            ("형사처벌", "Expected low similarity (civil law dataset)")
        ]
        
        for question, expectation in known_pairs:
            print(f"\nTesting: '{question}'")
            print(f"Expectation: {expectation}")
            
            results = self.query(question, top_k=1, detailed=False)
            
            if results:
                score = results[0]['similarity_score']
                case = results[0]['case_name']
                print(f"Best match: {case} (Score: {score:.4f})")
                
                if score > 0.7:
                    print("✅ Excellent match")
                elif score > 0.5:
                    print("✅ Good match")
                elif score > 0.3:
                    print("⚠️  Fair match")
                else:
                    print("❌ Poor match")
            else:
                print("❌ No matches found")


def main():
    """Main demo function"""
    print("Legal RAG System - Complete Demo")
    
    try:
        # Initialize demo
        demo = LegalRAGDemo()
        
        # Run different demo modes
        if len(sys.argv) > 1:
            mode = sys.argv[1].lower()
            
            if mode == "sample":
                demo.demo_with_sample_questions()
            elif mode == "interactive":
                demo.interactive_mode()
            elif mode == "benchmark":
                demo.benchmark_similarity_scores()
            else:
                print(f"Unknown mode: {mode}")
                print("Available modes: sample, interactive, benchmark")
        else:
            # Default: run sample questions demo
            demo.demo_with_sample_questions()
            
            # Ask if user wants to continue with interactive mode
            response = input("\nWould you like to try interactive mode? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                demo.interactive_mode()
    
    except Exception as e:
        print(f"Demo failed: {e}")
        import traceback
        print(traceback.format_exc())


if __name__ == "__main__":
    main()