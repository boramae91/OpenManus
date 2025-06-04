import asyncio
import os
import sys
from datetime import datetime

# 현재 스크립트의 디렉토리를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from app.agent.stock_classifier import StockClassifier, StockType
from app.logger import logger


def print_classification_types():
    """사용 가능한 분류 유형들을 출력하는 함수예요"""
    print("=== 지원하는 종목 분류 유형 ===")
    for i, stock_type in enumerate(StockType, 1):
        print(f"{i}. {stock_type.value} ({stock_type.name})")
    print("=" * 35)


async def main():
    """
    종목 분류 테스트를 위한 메인 함수예요
    """
    print("🏷️ 종목 분류 에이전트 테스트 시작!\n")

    # 분류 유형 출력
    print_classification_types()
    print()

    # 종목 분류 에이전트 생성
    try:
        classifier = StockClassifier()
        logger.info("종목 분류 에이전트가 성공적으로 생성되었습니다.")
    except Exception as e:
        logger.error(f"에이전트 생성 실패: {e}")
        return

    while True:
        try:
            # 사용자 입력 받기
            print("\n" + "=" * 50)
            print("종목을 입력해주세요 (종료하려면 'quit' 입력):")
            print("예시:")
            print("- '삼성전자 분류해줘'")
            print("- '005930 어떤 유형의 주식인가요?'")
            print("- 'AAPL classify this stock'")
            print("-" * 50)

            user_input = input("입력: ").strip()

            if not user_input:
                print("⚠️ 입력이 비어있습니다. 다시 입력해주세요.")
                continue

            if user_input.lower() in ["quit", "exit", "종료", "q"]:
                print("👋 종목 분류 에이전트를 종료합니다.")
                break

            print(f"\n🔍 분석 중: {user_input}")
            print("=" * 50)

            # 분류 시작 시간 기록
            start_time = datetime.now()

            # 종목 분류 실행
            result = await classifier.classify_stock(user_input)

            # 분류 완료 시간 계산
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()

            # 결과 출력
            print("\n🎯 분류 결과:")
            print("=" * 50)

            if result.get("classification"):
                classification = result["classification"]
                print(f"🏷️  분류: {classification.get('classification', '알 수 없음')}")
                print(f"📊  신뢰도: {classification.get('confidence', '보통')}")
                print(f"⏱️  처리 시간: {processing_time:.2f}초")

                # 근거 출력
                reasoning = classification.get("reasoning", [])
                if reasoning:
                    print(f"📋  주요 근거:")
                    for i, reason in enumerate(reasoning[:5], 1):  # 최대 5개까지만 표시
                        print(f"    {i}. {reason}")

                print(f"🔄  에이전트 상태: {result.get('agent_state', '알 수 없음')}")
            else:
                print("❌ 분류 결과를 생성할 수 없었습니다.")
                print(f"📄 전체 분석 결과:\n{result.get('full_analysis', '분석 실패')}")

            print("=" * 50)

            # 상세 분석 보기 옵션
            show_detail = (
                input("\n상세 분석 결과를 보시겠습니까? (y/n): ").strip().lower()
            )
            if show_detail in ["y", "yes", "네", "ㅇ"]:
                print("\n📄 상세 분석 결과:")
                print("-" * 50)
                print(result.get("full_analysis", "상세 분석 결과 없음"))
                print("-" * 50)

        except KeyboardInterrupt:
            print("\n\n⚠️ 사용자에 의해 중단되었습니다.")
            break
        except Exception as e:
            logger.error(f"분류 중 오류 발생: {e}")
            print(f"❌ 오류가 발생했습니다: {e}")
            print("다시 시도해주세요.")


def demo_examples():
    """
    데모용 예시 함수예요
    """
    examples = [
        "삼성전자 분류해줘",
        "005930 어떤 종류의 주식인가요?",
        "테슬라는 어떤 유형의 종목인가요?",
        "한화에어로스페이스 분류",
        "AAPL classify this stock",
        "현대자동차 주식 유형 분석해주세요",
    ]

    print("=== 예시 질문들 ===")
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example}")
    print("=" * 20)


async def quick_test():
    """
    빠른 테스트를 위한 함수예요
    """
    print("🚀 빠른 테스트 모드")
    print("삼성전자 분류 테스트를 실행합니다...\n")

    classifier = StockClassifier()

    test_input = "삼성전자 분류해줘"
    result = await classifier.classify_stock(test_input)

    print("테스트 결과:")
    if result.get("classification"):
        classification = result["classification"]
        print(f"분류: {classification.get('classification')}")
        print(f"신뢰도: {classification.get('confidence')}")
    else:
        print("분류 실패")

    print(f"\n전체 결과: {result}")


if __name__ == "__main__":
    try:
        print("종목 분류 에이전트 테스트 프로그램")
        print("1. 일반 테스트 (대화형)")
        print("2. 빠른 테스트 (삼성전자)")
        print("3. 예시 보기")

        choice = input("선택 (1-3): ").strip()

        if choice == "1":
            asyncio.run(main())
        elif choice == "2":
            asyncio.run(quick_test())
        elif choice == "3":
            demo_examples()
            print("\n예시를 참고하여 일반 테스트를 실행합니다...")
            asyncio.run(main())
        else:
            print("잘못된 선택입니다. 일반 테스트를 실행합니다.")
            asyncio.run(main())

    except Exception as e:
        logger.error(f"프로그램 실행 중 오류: {e}")
        print(f"오류가 발생했습니다: {e}")
