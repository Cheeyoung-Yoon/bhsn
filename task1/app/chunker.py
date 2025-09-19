import re
from typing import Dict, List


def _split_paragraphs(text: str) -> List[str]:
    paras = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    if not paras:
        return [text]
    return paras


def _split_sentences(text: str) -> List[str]:
    """문장 단위로 텍스트를 분할 (한국어 문장 구분자 기준)"""
    sentences = re.split(r'[.!?。]\s*', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences


def make_chunks(text: str, min_len=400, max_len=900, overlap=80) -> List[str]:
    if not text:
        return []
    paras = _split_paragraphs(text)
    chunks, buf = [], ""
    for p in paras:
        if not buf:
            buf = p
        elif len(buf) + len(p) <= max_len:
            buf += "\n" + p
        else:
            chunks.append(buf)
            buf = p
    if buf:
        chunks.append(buf)
    return chunks


def smart_chunk_summary(text: str, threshold=300) -> List[str]:
    """Smart chunking for judgment summary: split by sentences only if over 300 characters"""
    if not text or len(text) <= threshold:
        return [text] if text else []
    
    # Split by sentences only if over 300 characters
    sentences = _split_sentences(text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        potential_chunk = current_chunk + (" " if current_chunk else "") + sentence
        
        if len(potential_chunk) <= threshold:
            current_chunk = potential_chunk
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks


def _base_meta(rec: Dict) -> Dict:
    """null 값을 빈 문자열로 처리하여 Pinecone 호환성 확보"""
    meta = {}
    fields = [
        "사건명", "사건번호", "선고일자", "법원명", "사건종류명", 
        "판결유형", "판시사항", "참조조문", "참조판례", "전문", "판례정보일련번호"
    ]
    
    for field in fields:
        value = rec.get(field)
        if value is None:
            meta[field] = ""  # null을 빈 문자열로 변환
        elif isinstance(value, (str, int, float, bool)):
            meta[field] = value
        else:
            meta[field] = str(value)  # 기타 타입은 문자열로 변환
    
    return meta


def build_chunk_entries(rec: Dict, min_len=400, max_len=900, overlap=80) -> List[Dict]:
    """Smart chunking for judgment summary only, store rest as metadata"""
    entries = []
    
    # Smart chunking for judgment summary (split only if over 300 characters)
    judgment_summary = rec.get("판결요지", "")
    if judgment_summary:
        # Apply smart chunking: split by sentences only if over 300 characters
        chunks = smart_chunk_summary(judgment_summary, threshold=300)
        print(f"Judgment summary length: {len(judgment_summary)} chars -> {len(chunks)} chunks")
        
        for i, chunk_text in enumerate(chunks):
            # Create base metadata
            meta = _base_meta(rec)
            # Add the chunk text to metadata so it's retrievable
            meta["text"] = chunk_text
            meta["chunk_type"] = "판결요지"
            meta["chunk_idx"] = i
            
            entries.append({
                "source_id": rec.get("판례정보일련번호"), 
                "chunk_type": "판결요지", 
                "chunk_idx": i, 
                "text": chunk_text, 
                "meta": meta
            })
    else:
        print("Warning: No judgment summary found.")
    
    return entries