"""
Task 2 Configuration

Task 2 관련 설정 파일
"""

import os
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '..', 'env', '.env')
load_dotenv(env_path)

# Chat Configuration
CHAT_MODEL = "gemini-2.0-flash-001"
MAX_HISTORY_LENGTH = 50  # 최대 대화 기록 수
SEARCH_TOP_K = 3  # 검색할 문서 수

# UI Configuration
GRADIO_SERVER_NAME = "0.0.0.0"
GRADIO_SERVER_PORT = 7860
GRADIO_SHARE = False  # Public link 생성 여부

# Vector DB Configuration (Task 1에서 사용한 설정 재사용)
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "law-bot-korean")
CHAT_NAMESPACE = "task2_chat"  # Task 2 전용 네임스페이스

# Response Configuration
SYSTEM_PROMPT_TEMPLATE = """당신은 한국 법률 전문가입니다. 주어진 법률 문서를 바탕으로 사용자의 질문에 정확하고 도움이 되는 답변을 제공해주세요.

관련 법률 문서:
{context}

사용자 질문: {query}

답변 시 다음 사항을 고려해주세요:
1. 제공된 법률 문서의 내용을 기반으로 답변하세요
2. 정확한 법조문이나 판례를 인용하세요
3. 이해하기 쉽게 설명해주세요
4. 추가 상담이 필요한 경우 전문가 상담을 권하세요

답변:"""
