import json
import os

# cases.json 파일 경로
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'cases.json')

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    cases = json.load(f)

# 첫 번째 판례의 key 목록 출력
if cases:
    print('첫 번째 판례의 key 목록:')
    for key in cases[0].keys():
        print(key)
else:
    print('데이터가 비어 있습니다.')

# 전체 데이터에서 등장하는 모든 key 집합 출력
all_keys = set()
for case in cases:
    all_keys.update(case.keys())
print('\n전체 데이터에서 등장하는 모든 key:')
for key in sorted(all_keys):
    print(key)
