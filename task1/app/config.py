import os
from dotenv import load_dotenv


load_dotenv()


# Index / Namespace
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "law-bot-korean")
NAMESPACE = "task1"


# Pinecone serverless spec (인덱스 자동 생성용)
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")


# Chunking
CHUNK_MIN = 400
CHUNK_MAX = 900
CHUNK_OVERLAP = 80


# Paths
DATA_JSON = os.getenv("DATA_JSON", "./data/cases.json")