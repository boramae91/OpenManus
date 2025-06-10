# 테스트용 공통 헬퍼 함수들
# 여러 테스트 파일에서 중복되던 기능들을 모아둔 도구상자예요!

import re

from .test_constants import CLASSIFICATION_KEYWORDS, COMPANY_CODES, KOREAN_COMPANIES


def extract_stock_name_simple(prompt):
    """
    간단한 종목명 추출 함수 (모든 테스트 파일에서 공통 사용)
    실제 main.py의 함수보다 단순화된 버전이에요

    Args:
        prompt: 사용자가 입력한 질문

    Returns:
        tuple: (종목명, 종목코드)
    """
    if not prompt or not prompt.strip():
        return "GENERAL", None

    # 한국 종목코드 패턴 (6자리 숫자)
    korean_code_pattern = r"\b(\d{6})\b"
    korean_codes = re.findall(korean_code_pattern, prompt)

    # 해외 종목 티커 패턴 (2-5자리 대문자)
    ticker_pattern = r"\b([A-Z]{2,5})\b"
    tickers = re.findall(ticker_pattern, prompt.upper())

    # 종목명 검색
    found_company = None
    for company in KOREAN_COMPANIES:
        if company.lower() in prompt.lower():
            found_company = company
            break

    # 결과 반환
    if korean_codes:
        return f"CODE{korean_codes[0]}", korean_codes[0]
    elif found_company:
        # 해당 회사의 코드가 있다면 함께 반환
        code = COMPANY_CODES.get(found_company, None)
        return found_company, code
    elif tickers:
        return tickers[0], tickers[0]

    return "GENERAL", None


def check_keyword_detection(prompt):
    """
    프롬프트에서 분류 키워드를 감지하는 공통 함수

    Args:
        prompt: 검사할 프롬프트

    Returns:
        tuple: (키워드 감지 여부, 발견된 키워드 리스트)
    """
    if not prompt:
        return False, []

    # 키워드 감지 로직
    is_keyword_detected = any(
        keyword in prompt.lower() for keyword in CLASSIFICATION_KEYWORDS
    )

    # 발견된 키워드들 찾기
    found_keywords = [
        keyword for keyword in CLASSIFICATION_KEYWORDS if keyword in prompt.lower()
    ]

    return is_keyword_detected, found_keywords


def check_stock_detection(prompt):
    """
    프롬프트에서 종목 감지를 확인하는 공통 함수

    Args:
        prompt: 검사할 프롬프트

    Returns:
        tuple: (종목 감지 여부, 감지된 종목 정보, 종목 코드)
    """
    detected_stock_info, detected_stock_code = extract_stock_name_simple(prompt)
    has_stock_detected = (
        detected_stock_info != "GENERAL" and detected_stock_code is not None
    )

    return has_stock_detected, detected_stock_info, detected_stock_code


def print_test_header(title, description=""):
    """
    테스트 헤더를 예쁘게 출력하는 함수

    Args:
        title: 테스트 제목
        description: 테스트 설명 (선택사항)
    """
    print("=" * 60)
    print(f"🧪 {title}")
    if description:
        print(f"📝 {description}")
    print("=" * 60)


def print_test_result(test_name, success, message=""):
    """
    테스트 결과를 예쁘게 출력하는 함수

    Args:
        test_name: 테스트명
        success: 성공 여부
        message: 추가 메시지
    """
    status = "✅ 성공" if success else "❌ 실패"
    print(f"   {test_name}: {status}")
    if message:
        print(f"      └ {message}")


def count_success_rate(results):
    """
    테스트 성공률을 계산하는 함수

    Args:
        results: 불린 값들의 리스트

    Returns:
        tuple: (성공 개수, 전체 개수, 성공률 퍼센트)
    """
    success_count = sum(results)
    total_count = len(results)
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0

    return success_count, total_count, success_rate


def print_success_summary(results, test_type="테스트"):
    """
    테스트 성공률 요약을 출력하는 함수

    Args:
        results: 불린 값들의 리스트
        test_type: 테스트 종류 설명
    """
    success_count, total_count, success_rate = count_success_rate(results)

    print(
        f"\n📊 {test_type} 결과: {success_count}/{total_count} 성공 ({success_rate:.1f}%)"
    )

    if success_rate == 100:
        print("🎉 모든 테스트가 성공했습니다!")
    elif success_rate >= 80:
        print("👍 대부분의 테스트가 성공했습니다.")
    elif success_rate >= 50:
        print("⚠️ 일부 개선이 필요합니다.")
    else:
        print("❗ 많은 부분에서 개선이 필요합니다.")


def get_user_choice(prompt, valid_choices):
    """
    사용자 선택을 받는 공통 함수

    Args:
        prompt: 사용자에게 보여줄 메시지
        valid_choices: 유효한 선택지 리스트

    Returns:
        str: 사용자가 선택한 값
    """
    while True:
        choice = input(prompt).strip()
        if choice in valid_choices:
            return choice
        print(
            f"❌ 잘못된 선택입니다. 다음 중에서 선택하세요: {', '.join(valid_choices)}"
        )


def interactive_test_loop(test_function, exit_commands=None):
    """
    대화형 테스트 루프를 실행하는 공통 함수

    Args:
        test_function: 각 입력에 대해 실행할 테스트 함수
        exit_commands: 종료 명령어 리스트 (기본값: ['quit', 'exit', '종료', 'q'])
    """
    if exit_commands is None:
        exit_commands = ["quit", "exit", "종료", "q"]

    print("프롬프트를 입력하면 테스트를 실행합니다!")
    print(f"종료하려면 다음 중 하나를 입력하세요: {', '.join(exit_commands)}")
    print()

    while True:
        user_input = input("테스트할 프롬프트: ").strip()

        if user_input.lower() in [cmd.lower() for cmd in exit_commands]:
            print("👋 테스트를 종료합니다.")
            break

        if not user_input:
            print("⚠️ 입력이 비어있습니다.\n")
            continue

        # 테스트 함수 실행
        try:
            test_function(user_input)
        except Exception as e:
            print(f"❌ 테스트 중 오류 발생: {e}")

        print("-" * 40)
