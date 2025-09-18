#!/usr/bin/env python3
"""
전문 길이 및 청크 수 분석 스크립트
"""

import json
from app.chunker import build_chunk_entries

def analyze_fulltext():
    """전문 데이터 분석"""
    
    with open('../data/cases.json', 'r', encoding='utf-8') as f:
        records = json.load(f)
    
    print(f"🔍 총 {len(records)}개 케이스 분석 중...")
    
    total_chunks = 0
    fulltext_chunks = 0
    case_stats = []
    
    for i, rec in enumerate(records[:10]):  # 처음 10개만 테스트
        case_id = rec.get("판례정보일련번호", "Unknown")
        fulltext = rec.get("전문", "")
        
        print(f"\n📋 케이스 {i+1}: {case_id}")
        print(f"   전문 길이: {len(fulltext):,} 문자")
        
        # 청크 생성
        entries = build_chunk_entries(rec)
        
        # 청크 유형별 카운트
        chunk_types = {}
        for entry in entries:
            chunk_type = entry['chunk_type']
            chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
        
        print(f"   총 청크: {len(entries)}개")
        for ctype, count in chunk_types.items():
            print(f"     - {ctype}: {count}개")
        
        total_chunks += len(entries)
        fulltext_chunks += chunk_types.get('전문', 0)
        
        case_stats.append({
            'case_id': case_id,
            'fulltext_length': len(fulltext),
            'total_chunks': len(entries),
            'fulltext_chunks': chunk_types.get('전문', 0)
        })
    
    print(f"\n📊 전체 통계 (10개 케이스):")
    print(f"   총 청크 수: {total_chunks}개")
    print(f"   전문 청크 수: {fulltext_chunks}개")
    print(f"   전문 청크 비율: {fulltext_chunks/total_chunks*100:.1f}%")
    
    # 가장 긴 전문 찾기
    max_case = max(case_stats, key=lambda x: x['fulltext_length'])
    print(f"\n📏 최대 전문 길이:")
    print(f"   케이스 ID: {max_case['case_id']}")
    print(f"   전문 길이: {max_case['fulltext_length']:,} 문자")
    print(f"   전문 청크: {max_case['fulltext_chunks']}개")

if __name__ == "__main__":
    analyze_fulltext()