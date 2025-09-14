import re
from typing import Dict, List


def _split_paragraphs(text: str) -> List[str]:
    paras = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    if not paras:
        return [text]
    return paras


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


def _base_meta(rec: Dict) -> Dict:
    return {
    "사건명": rec.get("사건명"),
    "사건번호": rec.get("사건번호"),
    "선고일자": rec.get("선고일자"),
    "법원명": rec.get("법원명"),
    "사건종류명": rec.get("사건종류명"),
    "판결유형": rec.get("판결유형"),
    "참조조문": rec.get("참조조문"),
    }


def build_chunk_entries(rec: Dict, min_len=400, max_len=900, overlap=80) -> List[Dict]:
    entries = []
    for i, ch in enumerate(make_chunks(rec.get("판결요지", ""), min_len, max_len, overlap)):
        entries.append({"source_id": rec.get("판례정보일련번호"), "chunk_type": "요지", "chunk_idx": i, "text": ch, "meta": _base_meta(rec)})
    for i, ch in enumerate(make_chunks(rec.get("판시사항", ""), min_len, max_len, overlap)):
        entries.append({"source_id": rec.get("판례정보일련번호"), "chunk_type": "판시", "chunk_idx": i, "text": ch, "meta": _base_meta(rec)})
    if rec.get("참조조문"):
        entries.append({"source_id": rec.get("판례정보일련번호"), "chunk_type": "조문", "chunk_idx": 0, "text": rec.get("참조조문"), "meta": _base_meta(rec)})
    return entries