#!/usr/bin/env python3
"""
Task 3 시스템 테스트 스크립트

Task 3 구성 요소들이 올바르게 설정되었는지 확인합니다.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

def test_imports():
    """필요한 모듈들의 import 테스트"""
    print("🔍 모듈 import 테스트 중...")
    
    try:
        # Task 3 내부 모듈
        from analysis.performance_analyzer import PerformanceAnalyzer
        from analysis.quality_evaluator import QualityEvaluator
        from reports.report_generator import ReportGenerator
        print("   ✅ Task 3 내부 모듈 import 성공")
        
        # Task 1 모듈
        try:
            from task1.app.embedding_client import EmbeddingClient
            from task1.app.db_connection import VectorDB
            print("   ✅ Task 1 모듈 import 성공")
        except ImportError as e:
            print(f"   ⚠️ Task 1 모듈 import 실패: {e}")
        
        # Task 2 모듈
        try:
            from task2.app import LawChatbot
            print("   ✅ Task 2 모듈 import 성공")
        except ImportError as e:
            print(f"   ⚠️ Task 2 모듈 import 실패: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 모듈 import 실패: {e}")
        return False

def test_directory_structure():
    """디렉토리 구조 테스트"""
    print("\n📁 디렉토리 구조 테스트 중...")
    
    required_dirs = [
        current_dir / "analysis",
        current_dir / "reports", 
        current_dir / "tests"
    ]
    
    required_files = [
        current_dir / "main.py",
        current_dir / "config.py",
        current_dir / "README.md",
        current_dir / "analysis" / "performance_analyzer.py",
        current_dir / "analysis" / "quality_evaluator.py",
        current_dir / "reports" / "report_generator.py"
    ]
    
    all_good = True
    
    for directory in required_dirs:
        if directory.exists():
            print(f"   ✅ {directory.name}/ 디렉토리 존재")
        else:
            print(f"   ❌ {directory.name}/ 디렉토리 누락")
            all_good = False
    
    for file_path in required_files:
        if file_path.exists():
            print(f"   ✅ {file_path.name} 파일 존재")
        else:
            print(f"   ❌ {file_path.name} 파일 누락")
            all_good = False
    
    return all_good

def test_configuration():
    """설정 파일 테스트"""
    print("\n⚙️ 설정 테스트 중...")
    
    try:
        import config
        
        # 필수 설정 확인
        required_configs = [
            "ANALYSIS_CONFIG",
            "TEST_CATEGORIES", 
            "EVALUATION_CRITERIA",
            "REPORT_CONFIG"
        ]
        
        for config_name in required_configs:
            if hasattr(config, config_name):
                print(f"   ✅ {config_name} 설정 존재")
            else:
                print(f"   ❌ {config_name} 설정 누락")
                return False
        
        print(f"   📊 테스트 카테고리 수: {len(config.TEST_CATEGORIES)}")
        print(f"   📝 평가 기준 수: {len(config.EVALUATION_CRITERIA)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 설정 로드 실패: {e}")
        return False

def test_environment():
    """환경 변수 테스트"""
    print("\n🌍 환경 변수 테스트 중...")
    
    required_env_vars = [
        "GOOGLE_API_KEY",
        "PINECONE_API_KEY"
    ]
    
    optional_env_vars = [
        "PINECONE_INDEX_NAME"
    ]
    
    all_good = True
    
    for var in required_env_vars:
        if os.getenv(var):
            print(f"   ✅ {var} 설정됨")
        else:
            print(f"   ❌ {var} 누락 (필수)")
            all_good = False
    
    for var in optional_env_vars:
        if os.getenv(var):
            print(f"   ✅ {var} 설정됨")
        else:
            print(f"   ⚠️ {var} 누락 (선택)")
    
    return all_good

def test_dependencies():
    """의존성 패키지 테스트"""
    print("\n📦 의존성 패키지 테스트 중...")
    
    required_packages = [
        "google.genai",
        "pinecone", 
        "gradio",
        "numpy",
        "pandas"
    ]
    
    all_good = True
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package} 설치됨")
        except ImportError:
            print(f"   ❌ {package} 누락")
            all_good = False
    
    return all_good

def main():
    """메인 테스트 실행"""
    print("🧪 Task 3 시스템 테스트 시작")
    print("=" * 50)
    
    tests = [
        ("디렉토리 구조", test_directory_structure),
        ("모듈 Import", test_imports),
        ("설정 파일", test_configuration),
        ("환경 변수", test_environment),
        ("의존성 패키지", test_dependencies)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} 테스트 중 오류 발생: {e}")
            results.append((test_name, False))
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("🏁 테스트 결과 요약")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{test_name:15} : {status}")
        if result:
            passed += 1
    
    print(f"\n📊 전체 결과: {passed}/{total} 테스트 통과")
    
    if passed == total:
        print("🎉 모든 테스트 통과! Task 3를 실행할 준비가 되었습니다.")
        print("   python task3/main.py 명령으로 분석을 시작하세요.")
    else:
        print("⚠️ 일부 테스트가 실패했습니다. 위의 오류를 해결한 후 다시 시도하세요.")
        print("📋 체크리스트:")
        print("   1. Task 1이 완료되어 벡터 데이터베이스가 구축되어 있는지 확인")
        print("   2. Task 2 챗봇이 정상 동작하는지 확인")
        print("   3. 환경 변수가 올바르게 설정되어 있는지 확인")
        print("   4. 필요한 패키지가 모두 설치되어 있는지 확인")

if __name__ == "__main__":
    main()