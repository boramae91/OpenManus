"""
회사명 정제 및 DART 매칭 디버깅 테스트
"""

import os
import sys

from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# sys.path에 프로젝트 루트 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.data_collector.financial_data_collector import FinancialDataCollector


def test_company_name_cleaning():
    """회사명 정제 테스트"""
    print("🧹 회사명 정제 테스트")
    print("=" * 50)

    collector = FinancialDataCollector()

    test_cases = [
        "1. 삼성생명",
        "2. 삼성전자",
        "LG전자(주)",
        "주식회사 SK하이닉스",
        "㈜카카오",
        "NAVER Corporation",
    ]

    for original in test_cases:
        cleaned = collector._clean_company_name(original)
        print(f"'{original}' → '{cleaned}'")
    print()


def test_alternative_names():
    """대체 표기법 생성 테스트"""
    print("🔄 대체 표기법 생성 테스트")
    print("=" * 50)

    collector = FinancialDataCollector()

    test_names = ["삼성생명", "LG전자", "SK하이닉스"]

    for name in test_names:
        alternatives = collector._try_alternative_company_names(name)
        print(f"'{name}' 대체 표기법:")
        for i, alt in enumerate(alternatives, 1):
            print(f"  {i}. {alt}")
        print()


def test_dart_search():
    """실제 DART API 검색 테스트"""
    print("🔍 DART API 회사명 검색 테스트")
    print("=" * 50)

    dart_api_key = os.getenv("DART_API_KEY")
    if not dart_api_key:
        print("❌ DART_API_KEY 환경변수가 설정되지 않았습니다")
        return

    collector = FinancialDataCollector(dart_api_key=dart_api_key)

    test_cases = [
        ("032830", "1. 삼성생명"),  # 문제가 있었던 케이스
        ("005930", "삼성전자"),  # 정상 케이스
        ("066570", "LG전자"),  # 다른 대기업
    ]

    for stock_code, company_name in test_cases:
        print(f"\n📊 테스트: {company_name} ({stock_code})")
        print("-" * 30)

        # 회사명 정제
        cleaned_name = collector._clean_company_name(company_name)
        print(f"정제된 회사명: '{cleaned_name}'")

        # DART 검색
        corp_code = collector._search_corp_code_by_company_name(company_name)
        if corp_code:
            print(f"✅ 검색 성공: {corp_code}")

            # 실제 재무데이터 확인
            financial_data = collector._get_dart_financial_statements(
                stock_code, company_name
            )
            if financial_data.get("revenue", 0) > 0:
                print(f"✅ 재무데이터: 매출 {financial_data['revenue']:,}원")
            else:
                print(f"⚠️ 재무데이터: {financial_data.get('note', '데이터 없음')}")
        else:
            print("❌ 검색 실패")


if __name__ == "__main__":
    print("🚀 DART API 디버깅 테스트 시작\n")

    # 1. 회사명 정제 테스트
    test_company_name_cleaning()

    # 2. 대체 표기법 테스트
    test_alternative_names()

    # 3. 실제 DART 검색 테스트
    test_dart_search()

    print("\n🎉 모든 테스트 완료!")
