import os

from dotenv import load_dotenv

load_dotenv()
import sys

sys.path.append(".")
from app.data_collector.financial_data_collector import FinancialDataCollector


def test_samsung_life_detail():
    """삼성생명 재무데이터 상세 분석"""
    collector = FinancialDataCollector(os.getenv("DART_API_KEY"))

    print("🔍 삼성생명 재무데이터 상세 분석")
    print("=" * 50)

    # 1. 법인고유번호 확인
    corp_code = collector._get_corp_code_from_stock_code("032830", "삼성생명")
    print(f"법인고유번호: {corp_code}")

    # 2. 재무제표 조회 결과 상세 분석
    result = collector._get_dart_financial_statements("032830", "삼성생명")
    print(f"\n재무데이터 결과:")
    for key, value in result.items():
        print(f"  {key}: {value}")

    # 3. 전체 수집 프로세스 테스트
    print(f"\n전체 수집 테스트:")
    full_result = collector.collect_stock_data("032830", "삼성생명")
    print(f"성공 여부: {full_result.get('success')}")
    print(f"데이터 소스: {full_result.get('data_sources')}")
    if "dart_info" in full_result:
        dart_financial = full_result["dart_info"]["financial_statements"]
        print(f"DART 매출: {dart_financial.get('revenue')}")
        print(f"DART 총자산: {dart_financial.get('total_assets')}")


if __name__ == "__main__":
    test_samsung_life_detail()
