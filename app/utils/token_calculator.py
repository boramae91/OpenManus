# -*- coding: utf-8 -*-
"""
🔢 토큰 계산기 유틸리티

섹션별로 입력 토큰 수를 계산해서 CrewAI 분석 시
토큰 제한을 미리 확인할 수 있게 도와주는 도구예요!

GPT-4o 모델 기준으로 정확한 토큰 수를 계산해요.
"""

import json
from typing import Any, Dict, List, Optional, Tuple

import tiktoken

from app.logger import logger


class SectionTokenCalculator:
    """
    📊 섹션별 토큰 계산기

    주요 기능:
    1. 섹션별 토큰 수 계산
    2. 전문가별 필요 섹션 토큰 수 계산
    3. 여러 섹션 조합의 총 토큰 수 계산
    4. 토큰 제한 초과 여부 확인
    5. 토큰 사용량 최적화 제안
    """

    def __init__(self, model_name: str = "gpt-4o"):
        """
        토큰 계산기 초기화

        Args:
            model_name: 사용할 모델명 (기본값: gpt-4o)
        """
        self.model_name = model_name

        # GPT-4o 모델용 토크나이저 초기화
        try:
            self.tokenizer = tiktoken.encoding_for_model(model_name)
            logger.info(f"🔢 토큰 계산기 초기화 완료: {model_name}")
        except KeyError:
            # 모델이 tiktoken에 없으면 cl100k_base 사용 (GPT-4 계열 기본)
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
            logger.warning(f"⚠️ {model_name} 토크나이저 미발견, cl100k_base 사용")

        # 모델별 토큰 제한 설정
        self.token_limits = {
            "gpt-4o": 128000,  # GPT-4o 최대 토큰 수
            "gpt-4": 8192,  # GPT-4 기본
            "gpt-4-32k": 32768,  # GPT-4 32K
            "gpt-3.5-turbo": 4096,  # GPT-3.5 기본
        }

        # 안전 여유분 (응답 생성용 토큰 확보)
        self.safety_margin = 4000  # 응답 생성용 4K 토큰 확보

        logger.info(f"📏 모델 토큰 제한: {self.get_max_tokens():,}토큰")
        logger.info(f"🛡️ 안전 여유분: {self.safety_margin:,}토큰")

    def count_tokens(self, text: str) -> int:
        """
        텍스트의 토큰 수를 계산해요

        Args:
            text: 토큰을 계산할 텍스트

        Returns:
            int: 토큰 수
        """
        if not text:
            return 0

        try:
            return len(self.tokenizer.encode(text))
        except Exception as e:
            logger.error(f"❌ 토큰 계산 실패: {e}")
            # 대략적인 계산 (1토큰 ≈ 4글자)
            return len(text) // 4

    def analyze_sections_tokens(self, sections_dict: Dict[str, str]) -> Dict[str, Any]:
        """
        섹션별 토큰 수를 분석해요

        Args:
            sections_dict: 섹션명과 내용이 담긴 딕셔너리

        Returns:
            Dict: 섹션별 토큰 분석 결과
        """
        logger.info(f"🔍 {len(sections_dict)}개 섹션의 토큰 수 분석 시작...")

        section_tokens = {}
        total_tokens = 0

        for section_name, content in sections_dict.items():
            if isinstance(content, str):
                token_count = self.count_tokens(content)
                section_tokens[section_name] = {
                    "token_count": token_count,
                    "character_count": len(content),
                    "tokens_per_char": (
                        token_count / len(content) if len(content) > 0 else 0
                    ),
                }
                total_tokens += token_count
            else:
                logger.warning(
                    f"⚠️ 섹션 '{section_name}'의 내용이 문자열이 아님: {type(content)}"
                )
                section_tokens[section_name] = {
                    "token_count": 0,
                    "character_count": 0,
                    "tokens_per_char": 0,
                    "error": "내용이 문자열이 아님",
                }

        # 통계 정보 계산
        token_counts = [info["token_count"] for info in section_tokens.values()]

        result = {
            "total_sections": len(sections_dict),
            "total_tokens": total_tokens,
            "total_characters": sum(
                len(content)
                for content in sections_dict.values()
                if isinstance(content, str)
            ),
            "section_details": section_tokens,
            "statistics": {
                "max_tokens_per_section": max(token_counts) if token_counts else 0,
                "min_tokens_per_section": min(token_counts) if token_counts else 0,
                "avg_tokens_per_section": (
                    sum(token_counts) / len(token_counts) if token_counts else 0
                ),
                "median_tokens_per_section": (
                    sorted(token_counts)[len(token_counts) // 2] if token_counts else 0
                ),
            },
            "model_limits": {
                "max_input_tokens": self.get_max_tokens(),
                "safety_margin": self.safety_margin,
                "available_tokens": self.get_available_tokens(),
                "can_fit_all_sections": total_tokens <= self.get_available_tokens(),
            },
        }

        logger.info(
            f"✅ 토큰 분석 완료: 총 {total_tokens:,}토큰 ({len(sections_dict)}개 섹션)"
        )

        return result

    def calculate_expert_tokens(
        self, expert_sections: Dict[str, List[str]], all_sections: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        전문가별로 필요한 섹션들의 토큰 수를 계산해요

        Args:
            expert_sections: 전문가별 필요 섹션 리스트
            all_sections: 모든 섹션 내용

        Returns:
            Dict: 전문가별 토큰 분석 결과
        """
        logger.info(f"👨‍💼 {len(expert_sections)}명 전문가의 토큰 수 분석 시작...")

        expert_analysis = {}

        for expert_name, section_names in expert_sections.items():
            expert_tokens = 0
            expert_sections_detail = {}

            for section_name in section_names:
                if section_name in all_sections:
                    content = all_sections[section_name]
                    if isinstance(content, str):
                        token_count = self.count_tokens(content)
                        expert_tokens += token_count
                        expert_sections_detail[section_name] = {
                            "token_count": token_count,
                            "character_count": len(content),
                        }
                    else:
                        logger.warning(f"⚠️ 섹션 '{section_name}' 내용이 문자열이 아님")
                else:
                    logger.warning(f"⚠️ 섹션 '{section_name}'을 찾을 수 없음")

            expert_analysis[expert_name] = {
                "total_tokens": expert_tokens,
                "section_count": len(section_names),
                "sections_detail": expert_sections_detail,
                "can_fit_in_context": expert_tokens <= self.get_available_tokens(),
                "token_usage_percentage": (expert_tokens / self.get_available_tokens())
                * 100,
            }

        logger.info(f"✅ 전문가별 토큰 분석 완료: {len(expert_sections)}명")

        return expert_analysis

    def find_optimal_section_combination(
        self, sections_dict: Dict[str, str], max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        토큰 제한 내에서 최적의 섹션 조합을 찾아요

        Args:
            sections_dict: 모든 섹션 딕셔너리
            max_tokens: 최대 토큰 수 (기본값: 사용 가능 토큰)

        Returns:
            Dict: 최적 조합 분석 결과
        """
        if max_tokens is None:
            max_tokens = self.get_available_tokens()

        logger.info(f"🎯 최적 섹션 조합 찾기: 최대 {max_tokens:,}토큰")

        # 섹션별 토큰 수 계산 및 정렬 (토큰 수 기준 내림차순)
        section_tokens = []
        for name, content in sections_dict.items():
            if isinstance(content, str):
                tokens = self.count_tokens(content)
                section_tokens.append((name, tokens, content))

        # 토큰 수 기준 정렬
        section_tokens.sort(key=lambda x: x[1], reverse=True)

        # 탐욕적 알고리즘으로 최적 조합 찾기
        selected_sections = []
        current_tokens = 0

        for name, tokens, content in section_tokens:
            if current_tokens + tokens <= max_tokens:
                selected_sections.append(
                    {"name": name, "tokens": tokens, "characters": len(content)}
                )
                current_tokens += tokens
            else:
                # 남은 공간에 맞게 일부 내용만 포함 가능한지 확인
                remaining_tokens = max_tokens - current_tokens
                if remaining_tokens > 100:  # 최소 100토큰은 있어야 의미있음
                    # 대략적으로 내용을 잘라서 포함
                    chars_per_token = len(content) / tokens
                    max_chars = int(
                        remaining_tokens * chars_per_token * 0.9
                    )  # 안전여유 10%
                    if max_chars > 500:  # 최소 500자는 있어야 의미있음
                        truncated_content = content[:max_chars]
                        actual_tokens = self.count_tokens(truncated_content)
                        if current_tokens + actual_tokens <= max_tokens:
                            selected_sections.append(
                                {
                                    "name": name,
                                    "tokens": actual_tokens,
                                    "characters": len(truncated_content),
                                    "truncated": True,
                                    "original_tokens": tokens,
                                    "original_characters": len(content),
                                }
                            )
                            current_tokens += actual_tokens
                break

        result = {
            "max_tokens_limit": max_tokens,
            "selected_sections": selected_sections,
            "total_selected_tokens": current_tokens,
            "total_selected_sections": len(selected_sections),
            "token_utilization": (current_tokens / max_tokens) * 100,
            "excluded_sections": [
                {"name": name, "tokens": tokens}
                for name, tokens, _ in section_tokens
                if not any(s["name"] == name for s in selected_sections)
            ],
        }

        logger.info(
            f"✅ 최적 조합 완료: {len(selected_sections)}개 섹션, {current_tokens:,}토큰 ({result['token_utilization']:.1f}%)"
        )

        return result

    def get_max_tokens(self) -> int:
        """모델의 최대 토큰 수를 반환해요"""
        return self.token_limits.get(self.model_name, 128000)

    def get_available_tokens(self) -> int:
        """실제 사용 가능한 토큰 수를 반환해요 (안전 여유분 제외)"""
        return self.get_max_tokens() - self.safety_margin

    def check_token_limit(self, text: str) -> Dict[str, Any]:
        """
        텍스트가 토큰 제한을 초과하는지 확인해요

        Args:
            text: 확인할 텍스트

        Returns:
            Dict: 토큰 제한 확인 결과
        """
        tokens = self.count_tokens(text)
        available = self.get_available_tokens()

        return {
            "text_tokens": tokens,
            "available_tokens": available,
            "max_tokens": self.get_max_tokens(),
            "safety_margin": self.safety_margin,
            "is_within_limit": tokens <= available,
            "token_usage_percentage": (tokens / available) * 100,
            "excess_tokens": max(0, tokens - available),
        }

    def suggest_token_optimization(
        self, sections_analysis: Dict[str, Any]
    ) -> List[str]:
        """
        토큰 사용량 최적화 제안을 해요

        Args:
            sections_analysis: analyze_sections_tokens 결과

        Returns:
            List[str]: 최적화 제안 리스트
        """
        suggestions = []

        total_tokens = sections_analysis["total_tokens"]
        available_tokens = self.get_available_tokens()

        if total_tokens <= available_tokens:
            suggestions.append("✅ 모든 섹션이 토큰 제한 내에 있어요!")
        else:
            excess = total_tokens - available_tokens
            suggestions.append(
                f"⚠️ 토큰 초과: {excess:,}토큰 ({(excess/available_tokens)*100:.1f}%)"
            )

            # 가장 큰 섹션들 식별
            sections = sections_analysis["section_details"]
            large_sections = [
                (name, info["token_count"])
                for name, info in sections.items()
                if info["token_count"] > available_tokens * 0.1
            ]  # 10% 이상 차지하는 섹션

            if large_sections:
                large_sections.sort(key=lambda x: x[1], reverse=True)
                suggestions.append("📊 큰 섹션들:")
                for name, tokens in large_sections[:3]:  # 상위 3개만
                    percentage = (tokens / total_tokens) * 100
                    suggestions.append(
                        f"   • {name}: {tokens:,}토큰 ({percentage:.1f}%)"
                    )

            # 최적화 방법 제안
            suggestions.append("\n💡 최적화 방법:")
            suggestions.append("1. 전문가별로 필요한 섹션만 선택하기")
            suggestions.append("2. 큰 섹션을 여러 개의 작은 섹션으로 분할하기")
            suggestions.append("3. 중요도가 낮은 섹션 제외하기")
            suggestions.append("4. 섹션 내용을 요약해서 사용하기")

        return suggestions

    def create_section_summary_report(self, sections_dict: Dict[str, str]) -> str:
        """
        섹션 토큰 분석 요약 보고서를 생성해요

        Args:
            sections_dict: 섹션 딕셔너리

        Returns:
            str: 보고서 텍스트
        """
        analysis = self.analyze_sections_tokens(sections_dict)
        suggestions = self.suggest_token_optimization(analysis)

        report = f"""
🔢 섹션별 토큰 분석 보고서
========================================

📊 전체 현황:
• 총 섹션 수: {analysis['total_sections']:,}개
• 총 토큰 수: {analysis['total_tokens']:,}토큰
• 총 글자 수: {analysis['total_characters']:,}자

📏 모델 제한:
• 사용 모델: {self.model_name}
• 최대 토큰: {self.get_max_tokens():,}토큰
• 사용 가능: {self.get_available_tokens():,}토큰 (안전여유 {self.safety_margin:,}토큰 제외)
• 토큰 적합성: {'✅ 적합' if analysis['model_limits']['can_fit_all_sections'] else '❌ 초과'}

📈 섹션 통계:
• 평균 토큰/섹션: {analysis['statistics']['avg_tokens_per_section']:,.0f}토큰
• 최대 토큰/섹션: {analysis['statistics']['max_tokens_per_section']:,}토큰
• 최소 토큰/섹션: {analysis['statistics']['min_tokens_per_section']:,}토큰
• 중간값 토큰/섹션: {analysis['statistics']['median_tokens_per_section']:,}토큰

📋 섹션별 상세 (토큰 수 기준 정렬):
"""

        # 섹션별 상세 정보 (토큰 수 기준 정렬)
        sorted_sections = sorted(
            analysis["section_details"].items(),
            key=lambda x: x[1]["token_count"],
            reverse=True,
        )

        for i, (name, info) in enumerate(sorted_sections[:10], 1):  # 상위 10개만 표시
            percentage = (info["token_count"] / analysis["total_tokens"]) * 100
            report += f"{i:2d}. {name}\n"
            report += f"    • 토큰: {info['token_count']:,}개 ({percentage:.1f}%)\n"
            report += f"    • 글자: {info['character_count']:,}자\n"
            report += f"    • 비율: {info['tokens_per_char']:.3f}토큰/글자\n\n"

        if len(sorted_sections) > 10:
            report += f"... 외 {len(sorted_sections) - 10}개 섹션\n\n"

        # 최적화 제안
        report += "💡 최적화 제안:\n"
        for suggestion in suggestions:
            report += f"{suggestion}\n"

        return report
