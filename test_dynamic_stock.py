#!/usr/bin/env python3
"""
록히드마틴 동적 종목 감지 테스트
"""

import logging
import os
import sys

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agent.stock_name_extractor import StockNameExtractor


def main():
    """메인 테스트 함수"""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

    print("🚀 동적 종목 감지 테스트 시작")
    print("=" * 50)

    # StockNameExtractor 초기화
    extractor = StockNameExtractor()

    # 테스트 케이스들
    test_cases = [
        "록히드마틴에 대해서 분석해줘",
        "록히드 주식 분석",
        "Lockheed Martin 투자 전망",
        "보잉과 록히드마틴 비교분석",
        "방산주 록히드마틴 전망",
    ]

    print("\n🧪 테스트 케이스별 결과:")
    print("-" * 50)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. 테스트: '{test_case}'")
        try:
            result = extractor.extract_from_prompt(test_case)
            print(f"   📊 결과: {result}")

            if result[0]:  # 종목명이 발견되면
                print(f"   ✅ 성공! 종목명: {result[0]}, 티커: {result[1]}")
            else:
                print(f"   ❌ 종목 감지 실패")

        except Exception as e:
            print(f"   💥 오류 발생: {e}")

    print("\n" + "=" * 50)
    print("🏁 테스트 완료")


if __name__ == "__main__":
    main()
