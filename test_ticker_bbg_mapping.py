#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏢 ticker_bbg 매핑 기능 테스트 스크립트

종목명을 바탕으로 dataset CSV 파일에서 ticker_bbg를 찾아서
JSON 파일명에 사용하는 기능을 테스트합니다.
"""

import asyncio
import os
import sys

# 프로젝트 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_main import EnhancedStockAnalysisSystem


async def test_ticker_bbg_mapping():
    """ticker_bbg 매핑 기능 테스트"""
    print("🏢 ticker_bbg 매핑 기능 테스트 시작")
    print("=" * 50)

    # 시스템 초기화
    system = EnhancedStockAnalysisSystem()

    # 테스트 케이스들
    test_cases = [
        # 한국 주식 (KOSPI)
        {
            "stock_name": "삼성전자",
            "stock_code": "005930",
            "expected_contains": "005930 KS",
        },
        {
            "stock_name": "현대자동차",
            "stock_code": "005380",
            "expected_contains": "005380 KS",
        },
        {
            "stock_name": "네이버",
            "stock_code": "035420",
            "expected_contains": "035420 KS",
        },
        # 한국 주식 (KOSDAQ)
        {
            "stock_name": "셀트리온",
            "stock_code": "068270",
            "expected_contains": "068270 KS",
        },
        {
            "stock_name": "카카오",
            "stock_code": "035720",
            "expected_contains": "035720 KS",
        },
        # 해외 주식 (미국)
        {"stock_name": "APPLE", "stock_code": "AAPL", "expected_contains": "AAPL"},
        {"stock_name": "MICROSOFT", "stock_code": "MSFT", "expected_contains": "MSFT"},
        {"stock_name": "TESLA", "stock_code": "TSLA", "expected_contains": "TSLA"},
        # 종목명만으로 테스트
        {"stock_name": "삼성SDI", "stock_code": None, "expected_contains": "006400 KS"},
        {"stock_name": "LG전자", "stock_code": None, "expected_contains": "066570 KS"},
    ]

    print("📊 매핑 테이블 로드 상태:")
    if system.stock_mapping_table:
        for market, df in system.stock_mapping_table.items():
            if market != "ALL":
                print(f"  - {market}: {len(df)} 종목")
        print(f"  - 전체 통합: {len(system.stock_mapping_table.get('ALL', []))} 종목")
    else:
        print("  ❌ 매핑 테이블 로드 실패")
        return

    print("\n🔍 ticker_bbg 매핑 테스트:")
    print("-" * 50)

    success_count = 0
    total_count = len(test_cases)

    for i, test_case in enumerate(test_cases, 1):
        stock_name = test_case["stock_name"]
        stock_code = test_case["stock_code"]
        expected = test_case["expected_contains"]

        print(f"\n테스트 {i}: {stock_name} ({stock_code or '코드없음'})")

        # ticker_bbg 매핑 실행
        ticker_bbg = system.get_ticker_bbg_from_name(
            stock_name=stock_name, stock_code=stock_code
        )

        print(f"  🎯 결과: {ticker_bbg}")

        # 결과 검증
        if expected in ticker_bbg:
            print(f"  ✅ 성공: 예상값 '{expected}' 포함됨")
            success_count += 1
        else:
            print(f"  ❌ 실패: 예상값 '{expected}' 미포함")
            print(f"     예상: {expected} 포함")
            print(f"     실제: {ticker_bbg}")

    print("\n" + "=" * 50)
    print(
        f"📊 테스트 결과: {success_count}/{total_count} 성공 ({success_count/total_count*100:.1f}%)"
    )

    if success_count == total_count:
        print("🎉 모든 테스트 통과!")
    else:
        print(f"⚠️ {total_count - success_count}개 테스트 실패")


async def test_full_analysis_with_ticker_bbg():
    """전체 분석 플로우에서 ticker_bbg가 제대로 적용되는지 테스트"""
    print("\n🚀 전체 분석 플로우 테스트")
    print("=" * 50)

    system = EnhancedStockAnalysisSystem()

    test_prompts = [
        "삼성전자 주식 분석해줘",
        "005930 종목 어떤가요?",
        "애플 주식 투자 전망은?",
        "TSLA 분석 부탁드립니다",
    ]

    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n테스트 {i}: {prompt}")
        print("-" * 30)

        try:
            # 전체 분석 실행
            results = await system.run_enhanced_analysis(prompt)

            # 결과 확인
            if results.get("success"):
                stock_info = results.get("steps", {}).get("step1_stock_detection", {})

                print(f"  📊 감지된 종목: {stock_info.get('stock_name')}")
                print(f"  🏷️ 원본 코드: {stock_info.get('original_stock_code')}")
                print(f"  🎯 ticker_bbg: {stock_info.get('ticker_bbg')}")

                saved_file = results.get("saved_file")
                if saved_file:
                    print(f"  💾 저장 파일: {os.path.basename(saved_file)}")

                    # 파일명에서 ticker_bbg 확인
                    filename = os.path.basename(saved_file)
                    if stock_info.get("ticker_bbg") in filename:
                        print("  ✅ 파일명에 ticker_bbg 적용됨")
                    else:
                        print("  ❌ 파일명에 ticker_bbg 미적용")
                else:
                    print("  ❌ 파일 저장 실패")
            else:
                print(f"  ❌ 분석 실패: {results.get('error')}")

        except Exception as e:
            print(f"  ❌ 오류 발생: {e}")


if __name__ == "__main__":
    print("🏢 Enhanced Stock Analysis System - ticker_bbg 매핑 테스트")
    print("=" * 60)

    # 매핑 기능 테스트
    asyncio.run(test_ticker_bbg_mapping())

    # 전체 플로우 테스트 (선택사항 - 실제 API 호출 필요)
    print("\n" + "=" * 60)
    print("전체 분석 플로우 테스트를 실행하시겠습니까? (API 키 필요)")
    user_input = input("y/N: ").lower().strip()

    if user_input == "y":
        asyncio.run(test_full_analysis_with_ticker_bbg())
    else:
        print("전체 플로우 테스트를 건너뜁니다.")

    print("\n🎉 모든 테스트 완료!")
