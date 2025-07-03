# -*- coding: utf-8 -*-
"""
주석(footnote) 전문가 특화 도구 모음

이 파일은 사업보고서, 재무제표 등에서 주석(footnote) 정보를 초보자도 쉽게 분석할 수 있도록 도와주는 도구들이에요.
각 함수와 로직에는 아주 쉬운 한국어 주석이 달려 있어요!
"""

from typing import Any, Dict, List

from app.logger import logger


class FootnoteAnalysisTools:
    """
    주석(footnote) 전문가를 위한 특화 도구
    사업보고서, 재무제표의 주석을 쉽게 해석하고, 중요한 정보를 뽑아낼 수 있어요.
    """

    def __init__(self):
        # 도구가 처음 만들어질 때 한 번 실행돼요
        logger.info("📝 주석 분석 도구가 준비됐어요!")

    def extract_important_footnotes(
        self, footnotes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        # 여러 주석 중에서 중요한 것만 뽑아줘요
        # (예: 회계정책 변경, 소송, 특이사항 등)
        important = []
        for note in footnotes:
            # 주석의 제목이나 내용에 따라 중요도를 판단해요
            title = note.get("title", "")
            content = note.get("content", "")
            if any(
                keyword in title + content
                for keyword in ["회계정책", "소송", "변경", "중요", "특이"]
            ):
                important.append(note)
        return important

    def summarize_footnote(self, footnote: Dict[str, Any]) -> str:
        # 주석 하나를 아주 쉽게 요약해줘요
        # (예: 복잡한 회계 용어도 초등학생이 이해할 수 있게 설명)
        title = footnote.get("title", "")
        content = footnote.get("content", "")
        # 아주 간단하게 핵심만 뽑아서 설명해요
        if "회계정책" in title + content:
            return "회계 처리 방법이 바뀌었어요. 앞으로 숫자가 달라질 수 있어요."
        elif "소송" in title + content:
            return "회사가 소송에 휘말렸어요. 돈을 내야 할 수도 있어요."
        elif "변경" in title + content:
            return "중요한 내용이 바뀌었어요."
        elif "특이" in title + content:
            return "특별히 주의해야 할 내용이 있어요."
        else:
            return "이 주석은 특별한 위험이나 변화가 없어요."

    def detect_risk_in_footnotes(self, footnotes: List[Dict[str, Any]]) -> List[str]:
        # 주석들 중에서 위험 신호(리스크)를 찾아서 알려줘요
        risks = []
        for note in footnotes:
            content = note.get("content", "")
            if any(
                word in content
                for word in ["소송", "손실", "위험", "불확실", "부도", "연체"]
            ):
                risks.append(content)
        return risks

    def find_policy_changes(self, footnotes: List[Dict[str, Any]]) -> List[str]:
        # 주석들 중에서 정책이나 기준이 바뀐 부분을 찾아줘요
        changes = []
        for note in footnotes:
            content = note.get("content", "")
            if "변경" in content or "개정" in content:
                changes.append(content)
        return changes
