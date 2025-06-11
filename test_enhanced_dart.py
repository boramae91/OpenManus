"""
Enhanced DART 동적 검색 기능 테스트
"""

import os
import sys

from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# sys.path에 프로젝트 루트 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.data_collector.enhanced_financial_data_collector import (
    EnhancedDartDataCollector,
)


def test_enhanced_dart_search():
    """Enhanced DART 동적 검색 테스트"""
    print("🚀 Enhanced DART 동적 검색 테스트")
    print("=" * 60)

    dart_api_key = os.getenv("DART_API_KEY")
    if not dart_api_key:
        print("❌ DART_API_KEY 환경변수가 설정되지 않았습니다")
        return

    collector = EnhancedDartDataCollector(dart_api_key=dart_api_key)

    test_cases = [
        ("012450", "한화에어로스페이스"),  # 문제가 있었던 케이스
        ("032830", "삼성생명"),  # 이미 성공한 케이스
        ("005930", "삼성전자"),  # 기본 매핑 케이스
    ]

    for stock_code, company_name in test_cases:
        print(f"\n📊 Enhanced DART 테스트: {company_name} ({stock_code})")
        print("-" * 40)

        # 1. 법인고유번호 검색
        corp_code = collector.get_corp_code_from_stock_code(stock_code, company_name)
        if corp_code:
            print(f"✅ 법인고유번호 검색 성공: {corp_code}")

            # 2. 종합 기업 분석
            analysis_result = collector.get_comprehensive_company_analysis(
                stock_code=stock_code, company_name=company_name
            )

            if analysis_result["success"]:
                print(f"✅ Enhanced DART 종합 분석 성공!")
                print(
                    f"  - 재무분석: {'있음' if 'financial_analysis' in analysis_result else '없음'}"
                )
                print(
                    f"  - 지배구조: {'있음' if 'governance_analysis' in analysis_result else '없음'}"
                )
                print(
                    f"  - 투자정보: {'있음' if 'investment_analysis' in analysis_result else '없음'}"
                )
                print(
                    f"  - 공시모니터링: {'있음' if 'disclosure_monitoring' in analysis_result else '없음'}"
                )
            else:
                print(
                    f"❌ Enhanced DART 종합 분석 실패: {analysis_result.get('error')}"
                )
        else:
            print("❌ 법인고유번호 검색 실패")


if __name__ == "__main__":
    test_enhanced_dart_search()
