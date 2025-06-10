#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
종목 분류 키워드 감지 테스트 스크립트 (리팩토링 버전)

기존에 중복되던 코드들을 공통 유틸리티로 분리한 깔끔한 버전이에요!
"""

import os
import sys

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 공통 유틸리티 import
from app.utils.test_constants import (
    CLASSIFICATION_KEYWORDS,
    TEST_PROMPTS_KEYWORD_DETECTION,
)
from app.utils.test_helpers import (
    check_keyword_detection,
    get_user_choice,
    interactive_test_loop,
    print_success_summary,
    print_test_header,
)


def test_keyword_detection():
    """키워드 감지 로직을 테스트하는 함수예요 (리팩토링 버전)"""

    print_test_header(
        "종목 분류 키워드 감지 테스트",
        "사용자 입력에서 종목 분류 키워드가 제대로 감지되는지 테스트",
    )

    print(f"감지 키워드 목록: {CLASSIFICATION_KEYWORDS}\n")

    test_results = []

    for i, prompt in enumerate(TEST_PROMPTS_KEYWORD_DETECTION, 1):
        # 키워드 감지 (공통 함수 사용)
        is_classification_request, found_keywords = check_keyword_detection(prompt)

        # 결과 출력
        status = "✅ 감지됨" if is_classification_request else "❌ 감지 안됨"
        print(f"{i:2d}. {prompt}")
        print(f"    결과: {status}")
        if found_keywords:
            print(f"    발견된 키워드: {found_keywords}")
        print()

        # 테스트 결과 기록 (여기서는 감지됨을 성공으로 간주)
        test_results.append(is_classification_request)

    print("=" * 50)
    print("🔍 결론:")
    print("- '휴니드에서 분석해달라고'는 이제 '분석' 키워드로 감지됩니다!")
    print("- 다른 분석 관련 키워드들도 추가되어 더 정확하게 감지할 수 있어요.")

    # 테스트 결과 요약
    print_success_summary(test_results, "키워드 감지")


def interactive_test():
    """대화형 테스트 함수예요 (리팩토링 버전)"""

    def test_single_keyword(user_input):
        """단일 입력에 대한 키워드 테스트"""
        # 키워드 감지 (공통 함수 사용)
        is_classification_request, found_keywords = check_keyword_detection(user_input)

        # 결과 출력
        if is_classification_request:
            print(f"✅ Stock Classifier 실행됨!")
            print(f"📋 감지된 키워드: {found_keywords}")
            print("🏷️ 종목 분류 분석을 실행합니다...")
        else:
            print(f"❌ Stock Classifier 실행 안됨")
            print("📊 일반 분석만 실행됩니다...")

    print_test_header(
        "대화형 키워드 감지 테스트",
        "프롬프트를 입력하면 종목 분류 키워드가 감지되는지 확인해드려요!",
    )

    # 공통 대화형 테스트 루프 사용
    interactive_test_loop(test_single_keyword)


def main():
    """메인 함수 (리팩토링 버전)"""
    print("🚀 종목 분류 키워드 감지 테스트 프로그램 (리팩토링 버전)")
    print("중복 코드를 제거하고 공통 유틸리티를 사용한 깔끔한 버전입니다!\n")

    print("테스트 옵션:")
    print("1. 자동 테스트 (미리 정의된 예시들)")
    print("2. 대화형 테스트 (직접 입력)")

    choice = get_user_choice("\n선택 (1 또는 2): ", ["1", "2"])

    if choice == "1":
        test_keyword_detection()
    elif choice == "2":
        interactive_test()


if __name__ == "__main__":
    main()
