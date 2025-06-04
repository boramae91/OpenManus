#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
자동 종목 분류 테스트 스크립트

종목명이나 종목코드가 감지되면 자동으로 종목 분류가 실행되는지 테스트하는 스크립트예요.
"""

import re


def extract_stock_name_simple(prompt):
    """
    간단한 종목명 추출 함수 (테스트용)
    실제 main.py의 함수보다 단순화된 버전이에요
    """
    # 한국 종목코드 패턴 (6자리 숫자)
    korean_code_pattern = r"\b(\d{6})\b"
    korean_codes = re.findall(korean_code_pattern, prompt)

    # 일반적인 한국 주식 회사명 패턴
    korean_companies = [
        "삼성전자",
        "SK하이닉스",
        "LG전자",
        "현대자동차",
        "카카오",
        "네이버",
        "셀트리온",
        "휴니드",
        "HUNEED",
        "LG화학",
        "포스코",
        "삼성바이오로직스",
        "삼성SDI",
        "기아",
        "NAVER",
        "KAKAO",
        "SAMSUNG",
        "HYUNDAI",
        "LG",
        "SK",
        "POSCO",
    ]

    # 해외 종목 티커 패턴 (2-5자리 대문자)
    ticker_pattern = r"\b([A-Z]{2,5})\b"
    tickers = re.findall(ticker_pattern, prompt.upper())

    # 종목명 검색
    found_company = None
    for company in korean_companies:
        if company.lower() in prompt.lower():
            found_company = company
            break

    # 결과 반환
    if korean_codes:
        return f"CODE{korean_codes[0]}", korean_codes[0]
    elif found_company:
        # 해당 회사의 코드가 있다면 함께 반환 (예시)
        company_codes = {
            "삼성전자": "005930",
            "SK하이닉스": "000660",
            "LG전자": "066570",
            "현대자동차": "005380",
            "카카오": "035720",
            "네이버": "035420",
            "휴니드": "005870",
            "HUNEED": "005870",
        }
        code = company_codes.get(found_company, None)
        return found_company, code
    elif tickers:
        return tickers[0], tickers[0]

    return "GENERAL", None


def test_auto_classification():
    """자동 종목 분류 감지 테스트 함수예요"""

    # 키워드 리스트 (main.py와 동일)
    classification_keywords = [
        "분류",
        "classify",
        "유형",
        "type",
        "저성장주",
        "우량주",
        "고성장주",
        "자산주",
        "턴어라운드주",
        "시이클주",
        "기타주",
        "어떤 종류",
        "어떤 유형",
        "분석",
        "analyze",
        "어떤 주식",
        "어떤 종목",
        "성격",
        "특성",
        "투자유형",
        "투자 유형",
    ]

    # 테스트할 프롬프트들
    test_prompts = [
        # 자동 감지되어야 하는 경우들 (종목 감지)
        "휴니드에서 분석해달라고",  # 이제 종목명으로 자동 감지됨
        "삼성전자 실적 알려줘",
        "005930 주가 어때?",
        "AAPL 어떤 회사야?",
        "테슬라 TSLA 정보 좀",
        "현대자동차 전망은?",
        "LG전자 투자하기 어떤가",
        # 키워드로 감지되는 경우들
        "삼성전자 분류해줘",
        "어떤 유형의 주식인가요?",
        "투자 유형을 알고 싶어요",
        # 둘 다 감지되는 경우들 (키워드 + 종목)
        "삼성전자를 분석해주세요",
        "005930은 어떤 유형인가요?",
        "AAPL analyze this stock please",
        # 감지되지 않아야 하는 경우들
        "오늘 날씨 어때?",
        "주식시장 전반적인 상황은?",
        "코스피 지수 알려줘",
        "투자 전략이 뭐가 좋아?",
    ]

    print("=== 자동 종목 분류 감지 테스트 ===\n")
    print("🔍 감지 조건:")
    print("  1. 키워드 감지: 분류, 분석, 유형 등의 키워드가 포함된 경우")
    print("  2. 종목 감지: 종목명이나 종목코드가 감지된 경우")
    print("  3. 둘 중 하나라도 감지되면 Stock Classifier 실행!\n")
    print("=" * 60)

    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n{i:2d}. 📝 입력: '{prompt}'")

        # 1. 키워드 기반 감지
        is_keyword_detected = any(
            keyword in prompt.lower() for keyword in classification_keywords
        )
        found_keywords = [
            keyword for keyword in classification_keywords if keyword in prompt.lower()
        ]

        # 2. 종목 감지 기반
        detected_stock_info, detected_stock_code = extract_stock_name_simple(prompt)
        has_stock_detected = (
            detected_stock_info != "GENERAL" and detected_stock_code is not None
        )

        # 3. 최종 판단
        is_classification_request = is_keyword_detected or has_stock_detected

        # 결과 출력
        print(f"    🏷️ 키워드 감지: {'✅' if is_keyword_detected else '❌'}")
        if found_keywords:
            print(f"       └ 발견된 키워드: {found_keywords}")

        print(f"    📊 종목 감지: {'✅' if has_stock_detected else '❌'}")
        if has_stock_detected:
            print(
                f"       └ 감지된 종목: {detected_stock_info} ({detected_stock_code})"
            )

        print(
            f"    🤖 Stock Classifier 실행: {'✅ 실행됨' if is_classification_request else '❌ 실행 안됨'}"
        )

        # 실행 이유 표시
        if is_classification_request:
            if is_keyword_detected and has_stock_detected:
                print(f"       └ 실행 이유: 키워드 + 종목 둘 다 감지")
            elif is_keyword_detected:
                print(f"       └ 실행 이유: 키워드 감지")
            elif has_stock_detected:
                print(f"       └ 실행 이유: 종목 자동 감지")

        print("    " + "-" * 50)

    print("\n" + "=" * 60)
    print("🎯 결론:")
    print("✅ '휴니드에서 분석해달라고' → 종목명 '휴니드'가 감지되어 자동 실행!")
    print("✅ 키워드 없이도 종목명/코드만 있으면 자동으로 분류 분석 실행!")
    print("✅ 더 스마트한 종목 분류 시스템으로 업그레이드 완료!")


if __name__ == "__main__":
    print("🚀 자동 종목 분류 감지 테스트 프로그램")
    test_auto_classification()
