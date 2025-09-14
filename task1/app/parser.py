import json
from typing import Dict, List


def load_cases(json_path: str) -> List[Dict]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "cases" in data:
        data = data["cases"]
    return data


def normalize_record(r: Dict) -> Dict:
    return {
    "판례정보일련번호": r.get("판례정보일련번호"),
    "사건명": r.get("사건명"),
    "사건번호": r.get("사건번호"),
    "선고일자": r.get("선고일자"),
    "법원명": r.get("법원명"),
    "사건종류명": r.get("사건종류명"),
    "판결유형": r.get("판결유형"),
    "판시사항": (r.get("판시사항") or "").strip(),
    "판결요지": (r.get("판결요지") or "").strip(),
    "참조조문": (r.get("참조조문") or "").strip(),
    # "전문": (r.get("전문") or "").strip(),
    }


def parse_cases(json_path: str) -> List[Dict]:
    raw = load_cases(json_path)
    return [normalize_record(r) for r in raw]