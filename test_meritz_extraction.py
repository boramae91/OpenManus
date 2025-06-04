#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
메리츠증권 종목 정보 추출 테스트

AI 응답에서 "PDF"가 아닌 "메리츠증권"과 "008560"을 정확히 추출하는지 확인해요
"""

import os
import sys

sys.path.append(".")

from app.agent.dynamic_stock_extractor import DynamicStockExtractor

# 실제 메리츠증권 AI 응답 (문제가 되었던 응답)
meritz_response = """
Step 1: 종목 기본 정보 분석을 완료했습니다.

메리츠증권에 대한 기본 정보를 다음과 같이 정리할 수 있습니다.

1. 종목명 및 종목코드
   - 종목명: 메리츠증권
   - 종목코드: 008560

2. 업종 분류
   - 업종: 금융업, 증권업

3. 시가총액 규모
   - 메리츠증권은 한국 증권업계에서 중견 증권사로, 시가총액은 대략적으로 중간 규모에 해당합니다.

[PDF] 2023년 하반기 전망 시리즈 - 메리츠증권
URL: http://home.imeritz.com/include/resource/research/WorkFlow/20230529224232774K_02.pdf
Description: May 30, 2023 · 2023년 동사영업이익은7.9조원으로 2022년의 43.4조원에서 크게
"""


def test_meritz_extraction():
    """메리츠증권 추출 테스트"""
    print("🧪 메리츠증권 종목 정보 추출 테스트 시작...")

    # 동적 추출기 생성
    extractor = DynamicStockExtractor()

    # 추출 실행
    result = extractor.extract_and_compare(
        meritz_response, "메리츠증권에 대해서 분석해"
    )

    print(f"\n📊 추출 결과:")
    print(f"   종목명: {result['stock_name']}")
    print(f"   종목코드: {result['stock_code']}")
    print(f"   찾았는지: {result['found']}")
    print(f"   신뢰도: {result['confidence']}")
    print(f"   패턴: {result['pattern']}")
    print(f"   점수: {result['final_score']}")

    # 성공 여부 확인
    if (
        result["found"]
        and result["stock_name"] == "메리츠증권"
        and result["stock_code"] == "008560"
    ):
        print("\n✅ 테스트 성공! 메리츠증권 정보를 정확히 추출했습니다!")
        return True
    else:
        print(f"\n❌ 테스트 실패! 잘못된 정보가 추출되었습니다.")
        print(f"   예상: 메리츠증권 (008560)")
        print(f"   실제: {result['stock_name']} ({result['stock_code']})")
        return False


if __name__ == "__main__":
    test_meritz_extraction()
