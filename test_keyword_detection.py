#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
종목 분류 키워드 감지 테스트 스크립트

사용자 입력에서 종목 분류 키워드가 제대로 감지되는지 테스트하는 스크립트예요.
"""


def test_keyword_detection():
    """키워드 감지 로직을 테스트하는 함수예요"""

    # main.py와 동일한 키워드 리스트
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
        "휴니드에서 분석해달라고",
        "삼성전자 분류해줘",
        "005930 어떤 유형의 주식인가요?",
        "테슬라는 어떤 종류의 종목인가요?",
        "현대자동차 분석해주세요",
        "LG전자의 투자 유형을 알고 싶어요",
        "카카오 주식의 성격이 궁금해요",
        "AAPL analyze this stock",
        "단순한 주가 조회",  # 감지되지 않아야 함
        "종목 정보만 알려줘",  # 감지되지 않아야 함
    ]

    print("=== 종목 분류 키워드 감지 테스트 ===\n")
    print(f"감지 키워드 목록: {classification_keywords}\n")

    for i, prompt in enumerate(test_prompts, 1):
        # 키워드 감지 로직 (main.py와 동일)
        is_classification_request = any(
            keyword in prompt.lower() for keyword in classification_keywords
        )

        # 발견된 키워드들 찾기
        found_keywords = [
            keyword for keyword in classification_keywords if keyword in prompt.lower()
        ]

        # 결과 출력
        status = "✅ 감지됨" if is_classification_request else "❌ 감지 안됨"
        print(f"{i:2d}. {prompt}")
        print(f"    결과: {status}")
        if found_keywords:
            print(f"    발견된 키워드: {found_keywords}")
        print()

    print("=" * 50)
    print("🔍 결론:")
    print("- '휴니드에서 분석해달라고'는 이제 '분석' 키워드로 감지됩니다!")
    print("- 다른 분석 관련 키워드들도 추가되어 더 정확하게 감지할 수 있어요.")


def interactive_test():
    """대화형 테스트 함수예요"""

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

    print("\n=== 대화형 키워드 감지 테스트 ===")
    print("프롬프트를 입력하면 종목 분류 키워드가 감지되는지 확인해드려요!")
    print("종료하려면 'quit'를 입력하세요.\n")

    while True:
        user_input = input("테스트할 프롬프트: ").strip()

        if user_input.lower() in ["quit", "exit", "종료", "q"]:
            print("👋 테스트를 종료합니다.")
            break

        if not user_input:
            print("⚠️ 입력이 비어있습니다.\n")
            continue

        # 키워드 감지
        is_classification_request = any(
            keyword in user_input.lower() for keyword in classification_keywords
        )

        found_keywords = [
            keyword
            for keyword in classification_keywords
            if keyword in user_input.lower()
        ]

        # 결과 출력
        if is_classification_request:
            print(f"✅ Stock Classifier 실행됨!")
            print(f"📋 감지된 키워드: {found_keywords}")
            print("🏷️ 종목 분류 분석을 실행합니다...")
        else:
            print(f"❌ Stock Classifier 실행 안됨")
            print("📊 일반 분석만 실행됩니다...")

        print("-" * 40)


if __name__ == "__main__":
    print("종목 분류 키워드 감지 테스트 프로그램\n")
    print("1. 자동 테스트 (미리 정의된 예시들)")
    print("2. 대화형 테스트 (직접 입력)")

    choice = input("\n선택 (1 또는 2): ").strip()

    if choice == "1":
        test_keyword_detection()
    elif choice == "2":
        interactive_test()
    else:
        print("잘못된 선택입니다. 자동 테스트를 실행합니다.")
        test_keyword_detection()
