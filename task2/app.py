import gradio as gr
import os
import sys
import time
from typing import List, Tuple, Optional

# Add parent directory to path to import from task1
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from task1.app.embedding_client import EmbeddingClient
from task1.app.db_connection import VectorDB
from task1.app.config import INDEX_NAME, NAMESPACE
from google.genai import Client
from dotenv import load_dotenv


class LawChatbot:
    def __init__(self):
        """법률 챗봇 초기화"""
        # Load environment variables
        env_path = os.path.join(os.path.dirname(__file__), '..', 'env', '.env')
        load_dotenv(env_path)
        
        # Initialize components
        self.embedder = EmbeddingClient()
        self.vector_db = VectorDB(
            dim=3072  # Google Gemini embedding model dimension
        )
        
        # Initialize Google GenAI client for chat
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY 환경변수가 설정되지 않았습니다")
        self.genai_client = Client(api_key=api_key)
        
        # Chat history
        self.chat_history = []
    
    def retrieve_relevant_docs(self, query: str, top_k: int = 3) -> List[str]:
        """질의와 관련된 문서 검색"""
        try:
            # Generate query embedding
            query_embedding = self.embedder.embed_query(query)
            
            # Search in vector database
            results = self.vector_db.search(
                query_vector=query_embedding.tolist(),
                top_k=top_k
            )
            
            # Extract text content from results
            docs = []
            for match in results.get('matches', []):
                metadata = match.get('metadata', {})
                content = metadata.get('content', '')
                if content:
                    docs.append(content)
            
            return docs
        except Exception as e:
            print(f"문서 검색 중 오류 발생: {e}")
            return []
    
    def generate_response(self, query: str, context_docs: List[str]) -> str:
        """검색된 문서를 바탕으로 답변 생성"""
        try:
            # Prepare context
            context = "\n\n".join(context_docs) if context_docs else "관련 문서를 찾을 수 없습니다."
            
            # Create prompt
            prompt = f"""당신은 한국 법률 전문가입니다. 주어진 법률 문서를 바탕으로 사용자의 질문에 정확하고 도움이 되는 답변을 제공해주세요.

관련 법률 문서:
{context}

사용자 질문: {query}

답변 시 다음 사항을 고려해주세요:
1. 제공된 법률 문서의 내용을 기반으로 답변하세요
2. 정확한 법조문이나 판례를 인용하세요
3. 이해하기 쉽게 설명해주세요
4. 추가 상담이 필요한 경우 전문가 상담을 권하세요

답변:"""

            # Generate response using Google GenAI
            response = self.genai_client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents=prompt
            )
            
            return response.text
            
        except Exception as e:
            print(f"답변 생성 중 오류 발생: {e}")
            return "죄송합니다. 답변을 생성하는 중에 오류가 발생했습니다. 다시 시도해주세요."
    
    def chat(self, message: str, history: List[dict]) -> Tuple[str, List[dict]]:
        """챗봇과의 대화 처리"""
        if not message.strip():
            return "", history
        
        try:
            # Retrieve relevant documents
            print(f"사용자 질문: {message}")
            relevant_docs = self.retrieve_relevant_docs(message, top_k=3)
            print(f"검색된 문서 수: {len(relevant_docs)}")
            
            # Generate response
            response = self.generate_response(message, relevant_docs)
            
            # Update history with new message format
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": response})
            
            return "", history
            
        except Exception as e:
            error_msg = f"오류가 발생했습니다: {str(e)}"
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": error_msg})
            return "", history
    
    def clear_history(self):
        """대화 기록 초기화"""
        return []


def create_chatbot_interface():
    """Gradio 챗봇 인터페이스 생성"""
    
    # Initialize chatbot
    chatbot = LawChatbot()
    
    # Create Gradio interface
    with gr.Blocks(
        title="한국 법률 AI 챗봇",
        theme=gr.themes.Soft(),
        css="""
        .chatbot { height: 500px; }
        .chat-input { min-height: 50px; }
        """
    ) as demo:
        
        gr.Markdown(
            """
            # 🏛️ 한국 법률 AI 챗봇
            
            안녕하세요! 저는 한국 법률 전문 AI 챗봇입니다.
            법률 관련 질문을 하시면 관련 법조문과 판례를 바탕으로 답변해드리겠습니다.
            
            **주의사항:**
            - 이 챗봇의 답변은 참고용이며, 정확한 법률 상담은 전문가와 상담하시기 바랍니다.
            - 개인정보나 민감한 정보는 입력하지 마세요.
            """
        )
        
        # Chat interface
        chatbot_interface = gr.Chatbot(
            label="법률 상담",
            type="messages",
            elem_classes=["chatbot"],
            height=500,
            show_copy_button=True
        )
        
        with gr.Row():
            msg_input = gr.Textbox(
                placeholder="법률 관련 질문을 입력하세요...",
                label="질문",
                elem_classes=["chat-input"],
                scale=4
            )
            send_btn = gr.Button("전송", variant="primary", scale=1)
        
        with gr.Row():
            clear_btn = gr.Button("대화 기록 초기화", variant="secondary")
        
        # Examples
        gr.Examples(
            examples=[
                "계약서 작성 시 주의사항은 무엇인가요?",
                "임금 체불 시 어떻게 대응해야 하나요?",
                "교통사고 발생 시 처리 절차를 알려주세요",
                "부동산 매매계약 해지는 어떤 경우에 가능한가요?",
                "근로기준법상 연차휴가 규정을 설명해주세요"
            ],
            inputs=msg_input,
            label="예시 질문"
        )
        
        # Event handlers
        def send_message(message, history):
            return chatbot.chat(message, history)
        
        # Bind events
        send_btn.click(
            send_message,
            inputs=[msg_input, chatbot_interface],
            outputs=[msg_input, chatbot_interface]
        )
        
        msg_input.submit(
            send_message,
            inputs=[msg_input, chatbot_interface],
            outputs=[msg_input, chatbot_interface]
        )
        
        clear_btn.click(
            chatbot.clear_history,
            outputs=chatbot_interface
        )
        
        # Footer
        gr.Markdown(
            """
            ---
            **⚠️ 법률 면책 조항:**
            이 AI 챗봇의 답변은 일반적인 법률 정보 제공을 목적으로 하며, 구체적인 법률 조언을 대체할 수 없습니다.
            실제 법률 문제에 대해서는 반드시 전문 변호사와 상담하시기 바랍니다.
            """
        )
    
    return demo


if __name__ == "__main__":
    try:
        # Create and launch the chatbot interface
        demo = create_chatbot_interface()
        
        print("🚀 법률 AI 챗봇을 시작합니다...")
        print("📱 브라우저에서 http://localhost:7860 으로 접속하세요")
        
        # Launch with configuration
        demo.launch(
            server_name="0.0.0.0",  # Allow external access
            server_port=7860,
            share=False,  # Set to True if you want to create a public link
            show_error=True,
            inbrowser=True  # Automatically open in browser
        )
        
    except Exception as e:
        print(f"❌ 챗봇 시작 중 오류 발생: {e}")
        print("환경 설정을 확인해주세요:")
        print("1. GOOGLE_API_KEY 환경변수가 설정되어 있는지 확인")
        print("2. Pinecone 설정이 올바른지 확인")
        print("3. task1이 먼저 실행되어 벡터 데이터베이스가 준비되어 있는지 확인")
