#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
종목명 추출 테스트 스크립트
- 삼성바이오로직스가 올바르게 인식되는지 테스트
- KRW가 더 이상 종목명으로 잘못 인식되지 않는지 테스트
"""

import os
import sys

# main.py의 함수들을 임포트하기 위한 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import (
    convert_to_english_ticker,
    cross_verify_stock_name,
    extract_stock_name_from_ai_response,
    find_most_frequent_stock_name,
)


def test_samsung_biologics():
    """삼성바이오로직스 테스트"""
    print("=" * 60)
    print("🧪 삼성바이오로직스 종목명 추출 테스트")
    print("=" * 60)

    # 삼성바이오로직스가 포함된 가상의 AI 응답
    ai_response = """
    삼성바이오로직스는 바이오의약품 위탁개발생산(CDMO) 분야의 글로벌 선도 기업입니다.

    주요 재무 지표:
    - 시가총액: 73.38T KRW
    - 기업가치: 73.51T KRW
    - 주가수익비율: 57.36
    - 순이익률: 5.84%
    - 매출액: 4.9T KRW

    삼성바이오로직스의 현재 주가는 1,031,000 KRW이며,
    목표주가 평균은 1,318,840 KRW입니다.

    삼성바이오로직스는 고성장주로 분류됩니다.
    """

    # 프롬프트 시뮬레이션
    prompt = "삼성바이오로직스를 분석해달라고"

    print("\n1️⃣ find_most_frequent_stock_name 테스트:")
    most_frequent, frequency = find_most_frequent_stock_name(ai_response)
    print(f"   가장 빈번한 종목명: {most_frequent}")
    print(f"   출현 빈도: {frequency}")

    print("\n2️⃣ convert_to_english_ticker 테스트:")
    if most_frequent:
        english_ticker = convert_to_english_ticker(most_frequent)
        print(f"   {most_frequent} -> {english_ticker}")

    print("\n3️⃣ cross_verify_stock_name 테스트:")
    stock_name, stock_code = cross_verify_stock_name(prompt, ai_response)
    print(f"   최종 종목명: {stock_name}")
    print(f"   종목코드: {stock_code}")

    print("\n4️⃣ extract_stock_name_from_ai_response 테스트:")
    final_name, final_code = extract_stock_name_from_ai_response(ai_response, prompt)
    print(f"   최종 추출된 종목명: {final_name}")
    print(f"   최종 추출된 종목코드: {final_code}")

    # 결과 검증
    success = True
    if most_frequent != "삼성바이오로직스":
        print(
            f"❌ 오류: 가장 빈번한 종목명이 '삼성바이오로직스'가 아닙니다: {most_frequent}"
        )
        success = False

    if final_name != "SAMSUNG_BIO":
        print(f"❌ 오류: 최종 종목명이 'SAMSUNG_BIO'가 아닙니다: {final_name}")
        success = False

    if success:
        print("\n✅ 모든 테스트 통과! 삼성바이오로직스가 올바르게 인식됩니다.")
    else:
        print("\n❌ 테스트 실패! 추가 수정이 필요합니다.")

    return success


def test_krw_exclusion():
    """KRW 제외 테스트"""
    print("\n" + "=" * 60)
    print("🧪 KRW 통화 코드 제외 테스트")
    print("=" * 60)

    # KRW가 많이 포함된 응답 (하지만 실제 종목명은 없음)
    ai_response = """
    주요 재무 정보:
    - 시가총액: 100T KRW
    - 매출액: 50T KRW
    - 순이익: 5T KRW
    - 현재 주가: 50,000 KRW
    - 목표 주가: 60,000 KRW

    KRW 기준으로 모든 금액이 표시됩니다.
    """

    print("\n1️⃣ KRW가 종목명으로 인식되는지 테스트:")
    most_frequent, frequency = find_most_frequent_stock_name(ai_response)
    print(f"   가장 빈번한 종목명: {most_frequent}")
    print(f"   출현 빈도: {frequency}")

    if most_frequent == "KRW":
        print("❌ 오류: KRW가 여전히 종목명으로 인식됩니다!")
        return False
    else:
        print("✅ 성공: KRW가 종목명으로 인식되지 않습니다.")
        return True


def test_various_stocks():
    """다양한 종목 테스트"""
    print("\n" + "=" * 60)
    print("🧪 다양한 종목명 변환 테스트")
    print("=" * 60)

    test_cases = [
        "삼성바이오로직스",
        "삼성전자",
        "SK하이닉스",
        "네이버",
        "카카오",
        "LG화학",
        "현대자동차",
        "셀트리온",
    ]

    print("\n종목명 -> 영문 티커 변환:")
    all_success = True

    for stock_name in test_cases:
        english_ticker = convert_to_english_ticker(stock_name)
        print(f"   {stock_name} -> {english_ticker}")

        # 삼성바이오로직스가 올바르게 변환되는지 특별히 확인
        if stock_name == "삼성바이오로직스" and english_ticker != "SAMSUNG_BIO":
            print(f"   ❌ 오류: 삼성바이오로직스가 SAMSUNG_BIO로 변환되지 않았습니다!")
            all_success = False

    if all_success:
        print("\n✅ 모든 종목명이 올바르게 변환되었습니다.")
    else:
        print("\n❌ 일부 종목명 변환에 문제가 있습니다.")

    return all_success


def main():
    """메인 테스트 함수"""
    print("🚀 종목명 추출 시스템 테스트 시작")
    print("이 테스트는 삼성바이오로직스가 KRW 대신 올바르게 인식되는지 확인합니다.\n")

    # 테스트 실행
    test1_result = test_samsung_biologics()
    test2_result = test_krw_exclusion()
    test3_result = test_various_stocks()

    # 최종 결과
    print("\n" + "=" * 60)
    print("📊 최종 테스트 결과")
    print("=" * 60)

    if test1_result and test2_result and test3_result:
        print("🎉 모든 테스트 통과! 시스템이 올바르게 작동합니다.")
        print("이제 삼성바이오로직스가 JSON 파일명에서 올바르게 표시될 것입니다.")
    else:
        print("⚠️ 일부 테스트가 실패했습니다. 추가 수정이 필요합니다.")

        if not test1_result:
            print("   - 삼성바이오로직스 인식 문제")
        if not test2_result:
            print("   - KRW 제외 문제")
        if not test3_result:
            print("   - 종목명 변환 문제")


if __name__ == "__main__":
    main()
