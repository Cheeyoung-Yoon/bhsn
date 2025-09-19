#!/usr/bin/env python3
"""
Simple launcher for the Gradio Legal Chatbot
"""

import os
import sys
import subprocess

def main():
    """Launch the Gradio chatbot"""
    print("=== Legal RAG Chatbot Launcher ===")
    
    # Set working directory
    task2_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(task2_dir)
    
    print(f"Working directory: {task2_dir}")
    print("Starting Gradio interface...")
    
    try:
        # Import and launch the app
        import gradio as gr
        from app import create_chatbot_interface
        
        # Create the interface
        demo = create_chatbot_interface()
        
        print("Legal AI Chatbot starting...")
        print("Open your browser to: http://localhost:7860")
        
        # Launch with configuration
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True,
            inbrowser=True
        )
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please install required packages:")
        print("pip install gradio")
        
    except Exception as e:
        print(f"Error launching chatbot: {e}")
        print("Please check:")
        print("1. GOOGLE_API_KEY environment variable is set")
        print("2. Pinecone configuration is correct")
        print("3. task1 has been run to prepare the vector database")


if __name__ == "__main__":
    main()