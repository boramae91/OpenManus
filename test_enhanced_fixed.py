#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
수정된 Enhanced DART API 테스트
"""

import asyncio
import os
import sys

# 프로젝트 루트 디렉토리를 PYTHONPATH에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.data_collector.enhanced_financial_data_collector import (
    EnhancedDartDataCollector,
)


async def test_samsung_enhanced():
    """삼성전자 Enhanced DART API 테스트"""
    print("🚀 수정된 Enhanced DART API 테스트")
    print("=" * 60)

    # Enhanced 수집기 초기화 (환경변수에서 API 키 읽기)
    dart_api_key = os.getenv("DART_API_KEY")
    collector = EnhancedDartDataCollector(dart_api_key=dart_api_key)

    # 삼성전자 정보
    samsung_corp_code = "00126380"
    samsung_stock_code = "005930"

    print(f"📊 삼성전자 테스트")
    print(f"기업코드: {samsung_corp_code}")
    print(f"종목코드: {samsung_stock_code}")

    # 2024년 사업보고서 테스트
    print(f"\n🔍 2024년 사업보고서 검색 테스트:")
    business_exists = await collector._check_report_exists(
        corp_code=samsung_corp_code, bsns_year="2024", report_code="11011"  # 사업보고서
    )
    print(f'결과: {"✅ 찾음" if business_exists else "❌ 못찾음"}')

    # 2024년 3분기 보고서 테스트
    print(f"\n🔍 2024년 3분기보고서 검색 테스트:")
    quarterly_exists = await collector._check_report_exists(
        corp_code=samsung_corp_code,
        bsns_year="2024",
        report_code="11014",  # 3분기보고서
    )
    print(f'결과: {"✅ 찾음" if quarterly_exists else "❌ 못찾음"}')

    # 2023년 사업보고서 테스트
    print(f"\n🔍 2023년 사업보고서 검색 테스트:")
    business_2023_exists = await collector._check_report_exists(
        corp_code=samsung_corp_code, bsns_year="2023", report_code="11011"  # 사업보고서
    )
    print(f'결과: {"✅ 찾음" if business_2023_exists else "❌ 못찾음"}')

    print(f"\n🎯 테스트 요약:")
    print(f'2024년 사업보고서: {"✅" if business_exists else "❌"}')
    print(f'2024년 3분기보고서: {"✅" if quarterly_exists else "❌"}')
    print(f'2023년 사업보고서: {"✅" if business_2023_exists else "❌"}')


if __name__ == "__main__":
    # 이벤트 루프 실행
    asyncio.run(test_samsung_enhanced())
