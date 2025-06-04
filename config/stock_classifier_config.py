#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
종목 분류 에이전트 설정 파일

사용자가 종목 분류 에이전트의 동작 방식을 설정할 수 있어요.
"""


class StockClassifierConfig:
    """종목 분류 에이전트 설정 클래스예요"""

    # === 자동 실행 설정 ===
    # 키워드 없이도 종목이 감지되면 자동으로 분류를 실행할지 결정해요
    AUTO_CLASSIFY_ON_STOCK_DETECTION = True  # True로 설정하면 자동 실행

    # 키워드 기반 분류 실행 여부
    ENABLE_KEYWORD_CLASSIFICATION = True  # 키워드 감지 시 분류 실행

    # === 감지 키워드 설정 ===
    # 이 키워드들이 포함되면 종목 분류를 실행해요
    CLASSIFICATION_KEYWORDS = [
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

    # === 실행 모드 설정 ===
    EXECUTION_MODES = {
        "AUTO": "자동 실행 (종목 감지 시 자동으로 분류도 실행)",
        "KEYWORD_ONLY": "키워드 기반만 (특정 키워드가 있을 때만 실행)",
        "MANUAL": "수동 실행 (사용자가 명시적으로 요청할 때만)",
        "ALWAYS": "항상 실행 (모든 요청에 대해 분류 실행)",
    }

    # 현재 실행 모드 설정
    CURRENT_MODE = "AUTO"  # AUTO, KEYWORD_ONLY, MANUAL, ALWAYS 중 선택

    # === 로깅 설정 ===
    # 분류 실행 이유를 로그에 상세히 기록할지 결정해요
    DETAILED_LOGGING = True

    # 분류 결과를 사용자에게 보여줄 때의 형태
    SHOW_CLASSIFICATION_REASON = True  # 왜 분류가 실행되었는지 표시

    # === 성능 설정 ===
    # 분류와 일반 분석을 동시에 실행할지, 순차적으로 실행할지
    PARALLEL_EXECUTION = False  # True면 동시 실행, False면 분류 먼저

    @classmethod
    def get_execution_description(cls):
        """현재 설정된 실행 모드의 설명을 반환해요"""
        return cls.EXECUTION_MODES.get(cls.CURRENT_MODE, "알 수 없는 모드")

    @classmethod
    def should_run_classification(cls, has_keyword, has_stock):
        """
        현재 설정에 따라 분류를 실행해야 하는지 판단해요
        - has_keyword: 키워드가 감지되었는지
        - has_stock: 종목이 감지되었는지
        - 반환값: (실행 여부, 실행 이유)
        """
        if cls.CURRENT_MODE == "ALWAYS":
            return True, "항상 실행 모드"

        elif cls.CURRENT_MODE == "AUTO":
            if cls.ENABLE_KEYWORD_CLASSIFICATION and has_keyword:
                if cls.AUTO_CLASSIFY_ON_STOCK_DETECTION and has_stock:
                    return True, "키워드 + 종목 자동 감지"
                else:
                    return True, "키워드 감지"
            elif cls.AUTO_CLASSIFY_ON_STOCK_DETECTION and has_stock:
                return True, "종목 자동 감지"
            else:
                return False, "감지 조건 미충족"

        elif cls.CURRENT_MODE == "KEYWORD_ONLY":
            if cls.ENABLE_KEYWORD_CLASSIFICATION and has_keyword:
                return True, "키워드 감지"
            else:
                return False, "키워드 없음"

        elif cls.CURRENT_MODE == "MANUAL":
            return False, "수동 모드 (명시적 요청 필요)"

        else:
            return False, "알 수 없는 모드"

    @classmethod
    def set_mode(cls, mode):
        """실행 모드를 변경해요"""
        if mode in cls.EXECUTION_MODES:
            cls.CURRENT_MODE = mode
            return True
        return False

    @classmethod
    def get_status_summary(cls):
        """현재 설정 상태를 요약해서 반환해요"""
        return f"""
=== 종목 분류 에이전트 설정 상태 ===
🔧 실행 모드: {cls.CURRENT_MODE} ({cls.get_execution_description()})
🎯 자동 실행: {'켜짐' if cls.AUTO_CLASSIFY_ON_STOCK_DETECTION else '꺼짐'}
🏷️ 키워드 감지: {'켜짐' if cls.ENABLE_KEYWORD_CLASSIFICATION else '꺼짐'}
📝 상세 로깅: {'켜짐' if cls.DETAILED_LOGGING else '꺼짐'}
🔍 실행 이유 표시: {'켜짐' if cls.SHOW_CLASSIFICATION_REASON else '꺼짐'}
⚡ 병렬 실행: {'켜짐' if cls.PARALLEL_EXECUTION else '꺼짐'}
📋 감지 키워드 개수: {len(cls.CLASSIFICATION_KEYWORDS)}개
"""


# 설정 변경을 위한 편의 함수들
def enable_auto_classification():
    """자동 분류를 켜요 (종목 감지 시 자동 실행)"""
    StockClassifierConfig.AUTO_CLASSIFY_ON_STOCK_DETECTION = True
    StockClassifierConfig.CURRENT_MODE = "AUTO"
    print("✅ 자동 종목 분류가 활성화되었습니다!")
    print("이제 종목명이나 종목코드가 감지되면 자동으로 분류 분석을 실행해요.")


def disable_auto_classification():
    """자동 분류를 꺼요 (키워드 기반만)"""
    StockClassifierConfig.AUTO_CLASSIFY_ON_STOCK_DETECTION = False
    StockClassifierConfig.CURRENT_MODE = "KEYWORD_ONLY"
    print("⚠️ 자동 종목 분류가 비활성화되었습니다!")
    print("이제 '분류', '분석' 등의 키워드가 있을 때만 분류 분석을 실행해요.")


def set_manual_mode():
    """수동 모드로 설정해요"""
    StockClassifierConfig.CURRENT_MODE = "MANUAL"
    print("🔧 수동 모드로 설정되었습니다!")
    print("이제 명시적으로 분류를 요청할 때만 실행해요.")


def set_always_mode():
    """항상 실행 모드로 설정해요"""
    StockClassifierConfig.CURRENT_MODE = "ALWAYS"
    print("🚀 항상 실행 모드로 설정되었습니다!")
    print("이제 모든 요청에 대해 종목 분류 분석을 실행해요.")


def show_current_config():
    """현재 설정을 보여줘요"""
    print(StockClassifierConfig.get_status_summary())


# 사용 예시
if __name__ == "__main__":
    print("🛠️ 종목 분류 에이전트 설정 도구")
    print("\n현재 설정 상태:")
    show_current_config()

    print("\n설정 변경 예시:")
    print("1. enable_auto_classification()  - 자동 분류 켜기")
    print("2. disable_auto_classification() - 자동 분류 끄기")
    print("3. set_manual_mode()             - 수동 모드")
    print("4. set_always_mode()             - 항상 실행 모드")
    print("5. show_current_config()         - 현재 설정 보기")
