"""
Task 2: Gradio 챗봇 인터페이스

이 모듈은 Task 1에서 구축한 벡터 데이터베이스를 활용하여
법률 관련 질문에 답변하는 RAG 기반 챗봇을 제공합니다.

주요 기능:
- 벡터 검색을 통한 관련 문서 검색
- Google GenAI를 활용한 답변 생성
- Gradio 웹 인터페이스
- 대화 기록 관리

사용법:
    python task2/app.py

필요 조건:
- Task 1이 완료되어 벡터 데이터베이스가 구축되어 있어야 함
- GOOGLE_API_KEY 환경변수 설정
- Pinecone API 키 설정
"""

import os
import sys

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app import create_chatbot_interface

if __name__ == "__main__":
    demo = create_chatbot_interface()
    demo.launch()
