#!/usr/bin/env python3
"""
AI 응답 파싱 로직 테스트
"""

import logging
import sys

sys.path.append(".")

from enhanced_main import EnhancedStockAnalysisSystem


def test_parsing():
    """파싱 로직 테스트"""
    logging.basicConfig(level=logging.INFO)

    system = EnhancedStockAnalysisSystem()

    # 테스트 케이스들 (실제 AI 응답 형태)
    test_cases = [
        # 케이스 1: 구조화된 형태
        """
        종목명: Lockheed Martin Corporation
        종목코드: LMT
        """,
        # 케이스 2: 괄호 형태
        "Lockheed Martin Corporation (LMT) Stock Price, News, Quote",
        # 케이스 3: 실제 로그에서 본 형태
        """
        I've found the information you need:

        종목명: Lockheed Martin Corporation
        종목코드: LMT

        If you have any more questions or need further assistance, feel free to ask!
        """,
        # 케이스 4: 한국 종목
        """
        종목명: 삼성전자
        종목코드: 005930
        """,
    ]

    print("🧪 AI 응답 파싱 테스트")
    print("=" * 50)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. 테스트 케이스:")
        print(f"   입력: {test_case.strip()[:50]}...")

        result = system._parse_ai_stock_response(test_case, "test")

        print(f"   결과: {result}")

        if result["detected"]:
            print(f"   ✅ 성공: {result['stock_name']} ({result['stock_code']})")
        else:
            print(f"   ❌ 실패")

    print("\n" + "=" * 50)
    print("🏁 테스트 완료")


if __name__ == "__main__":
    test_parsing()
