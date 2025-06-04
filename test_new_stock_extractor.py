#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
새로운 종목명 추출 에이전트 테스트
- StockNameExtractor 클래스 테스트
- 프롬프트에서 직접 종목명 추출하는 방식 검증
"""

import os
import sys

# app 모듈을 임포트하기 위한 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agent.stock_name_extractor import StockNameExtractor


def test_samsung_biologics():
    """삼성바이오로직스 테스트"""
    print("=" * 60)
    print("🧪 삼성바이오로직스 추출 테스트")
    print("=" * 60)

    extractor = StockNameExtractor()

    test_prompts = [
        "삼성바이오로직스를 분석해달라고",
        "삼성바이오로직스 종목에 대해서 분석해줘",
        "삼성바이오로직스 주식 정보 알려줘",
        "삼성바이오로직스의 재무상태는?",
        "삼성바이오로직스 투자 전망은?",
    ]

    for prompt in test_prompts:
        print(f"\n프롬프트: '{prompt}'")

        stock_info = extractor.get_extracted_info(prompt)
        print(f"  추출된 종목명: {stock_info['stock_name']}")
        print(f"  종목코드: {stock_info['stock_code']}")
        print(f"  감지 여부: {stock_info['found']}")

        # 삼성바이오로직스가 정확히 인식되는지 확인
        if stock_info["stock_name"] == "SAMSUNG_BIO":
            print("  ✅ 성공!")
        else:
            print(f"  ❌ 실패! 예상: SAMSUNG_BIO, 실제: {stock_info['stock_name']}")


def test_various_stocks():
    """다양한 종목 테스트"""
    print("\n" + "=" * 60)
    print("🧪 다양한 종목 추출 테스트")
    print("=" * 60)

    extractor = StockNameExtractor()

    test_cases = [
        ("삼성전자를 분석해줘", "SAMSUNG_ELEC", "005930"),
        ("SK하이닉스 주가는?", "SKHYNIX", "000660"),
        ("네이버 종목 정보", "NAVER", "035420"),
        ("카카오 투자 전망", "KAKAO", "035720"),
        ("현대자동차 재무제표", "HYUNDAI_MOTOR", "005380"),
        ("LG화학 분석 결과", "LG_CHEM", "051910"),
        ("셀트리온 주식", "CELLTRION", "068270"),
        ("휴니드 005870", "HUNEED", "005870"),  # 종목코드와 함께
        ("애플 주식 분석", "APPLE", "AAPL"),  # 해외 주식
        ("테슬라 전망", "TESLA", "TSLA"),
    ]

    success_count = 0

    for prompt, expected_name, expected_ticker in test_cases:
        print(f"\n프롬프트: '{prompt}'")

        stock_info = extractor.get_extracted_info(prompt)
        actual_name = stock_info["stock_name"]
        actual_ticker = stock_info["ticker"]

        print(f"  예상 종목명: {expected_name}")
        print(f"  실제 종목명: {actual_name}")
        print(f"  예상 티커: {expected_ticker}")
        print(f"  실제 티커: {actual_ticker}")
        print(f"  종목 타입: {stock_info['stock_type']}")
        print(f"  시장: {stock_info['market']}")

        if actual_name == expected_name and actual_ticker == expected_ticker:
            print("  ✅ 성공!")
            success_count += 1
        else:
            print("  ❌ 실패!")

    print(
        f"\n📊 결과: {success_count}/{len(test_cases)} 성공 ({success_count/len(test_cases)*100:.1f}%)"
    )


def test_no_stock_prompts():
    """종목이 없는 프롬프트 테스트"""
    print("\n" + "=" * 60)
    print("🧪 종목이 없는 프롬프트 테스트")
    print("=" * 60)

    extractor = StockNameExtractor()

    no_stock_prompts = [
        "오늘 날씨 어때?",
        "주식 시장 전반적인 상황은?",
        "투자 전략을 알려줘",
        "경제 뉴스 요약해줘",
        "코스피 지수는?",
        "달러 환율은?",
    ]

    success_count = 0

    for prompt in no_stock_prompts:
        print(f"\n프롬프트: '{prompt}'")

        stock_info = extractor.get_extracted_info(prompt)
        found = stock_info["found"]

        print(f"  종목 감지: {found}")

        if not found:
            print("  ✅ 정확! 종목이 없음을 올바르게 인식")
            success_count += 1
        else:
            print(f"  ❌ 오류! 종목이 없는데 {stock_info['stock_name']}를 감지함")

    print(
        f"\n📊 결과: {success_count}/{len(no_stock_prompts)} 성공 ({success_count/len(no_stock_prompts)*100:.1f}%)"
    )


def test_edge_cases():
    """경계 사례 테스트"""
    print("\n" + "=" * 60)
    print("🧪 경계 사례 테스트")
    print("=" * 60)

    extractor = StockNameExtractor()

    edge_cases = [
        ("삼성", "SAMSUNG"),  # 짧은 이름
        ("AAPL 주식", "AAPL"),  # 티커 직접 입력
        ("005930 분석", "CODE005930"),  # 종목코드만
        ("삼성전자 005930", "SAMSUNG_ELEC"),  # 이름 + 코드
        ("", None),  # 빈 문자열
        ("   ", None),  # 공백만
    ]

    for prompt, expected in edge_cases:
        print(f"\n프롬프트: '{prompt}' (길이: {len(prompt)})")

        if prompt.strip():
            stock_info = extractor.get_extracted_info(prompt)
            actual = stock_info["stock_name"]
            print(f"  예상: {expected}")
            print(f"  실제: {actual}")

            if actual == expected:
                print("  ✅ 성공!")
            else:
                print("  ❌ 실패!")
        else:
            stock_info = extractor.get_extracted_info(prompt)
            if not stock_info["found"]:
                print("  ✅ 빈 입력 올바르게 처리")
            else:
                print("  ❌ 빈 입력인데 종목을 감지함")


def main():
    """메인 테스트 함수"""
    print("🚀 새로운 종목명 추출 에이전트 테스트")
    print("이 테스트는 프롬프트에서 직접 종목명을 추출하는 새로운 방식을 검증합니다.\n")

    # 모든 테스트 실행
    test_samsung_biologics()
    test_various_stocks()
    test_no_stock_prompts()
    test_edge_cases()

    print("\n" + "=" * 60)
    print("🎯 새로운 방식의 장점:")
    print("   ✅ 프롬프트에서 바로 추출 - 빠르고 정확")
    print("   ✅ AI 응답 분석 불필요 - KRW 같은 오류 없음")
    print("   ✅ 단순하고 명확한 로직")
    print("   ✅ JSON 파일명에 정확한 종목명 사용 가능")
    print("=" * 60)


if __name__ == "__main__":
    main()
