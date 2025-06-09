import logging
import re
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class DynamicStockExtractor:
    """AI 응답에서 종목명과 종목코드를 동적으로 추출하는 에이전트"""

    def __init__(self):
        # 제외할 일반적인 단어들 (오탐 방지)
        self.exclude_words = {
            "분석",
            "종목",
            "기업",
            "정보",
            "결과",
            "전망",
            "투자",
            "주식",
            "시장",
            "Company",
            "Stock",
            "Market",
            "Analysis",
            "Report",
            "Industry",
            "PDF",
            "URL",
            "Description",
            "Metadata",
            "Search",
            "results",
            "http",
            "https",
            "www",
            "com",
            "html",
            "Step",
            "Observed",
        }
        logger.info("동적 종목 정보 추출 에이전트가 초기화되었습니다! 🚀")

    def extract_and_compare(self, ai_response: str, user_prompt: str = "") -> Dict:
        """AI 응답에서 종목명과 종목코드를 추출해요"""

        if not ai_response or not ai_response.strip():
            return self._create_empty_result(user_prompt)

        # 패턴 1: "종목명: XXX" 찾기 (다양한 형태 지원)
        name_patterns = [
            r"종목명\s*[:：]\s*([가-힣A-Za-z0-9\s&\-\.]{2,20})(?=\s*(?:\(|$|\n|,))",
            r"회사명\s*[:：]\s*([가-힣A-Za-z0-9\s&\-\.]{2,20})(?=\s*(?:\(|$|\n|,))",
            # JSON에서 발견된 패턴: "**종목명 및 종목코드**: 한화오션 (종목코드: 042660)"
            r"\*\*종목명[^:]*\*\*:\s*([가-힣A-Za-z0-9\s&\-\.]{2,20})(?=\s*\()",
            r"종목명\s*및\s*종목코드\**\s*[:：]\s*([가-힣A-Za-z0-9\s&\-\.]{2,20})(?=\s*\()",
        ]

        name_matches = []
        for pattern in name_patterns:
            matches = re.findall(pattern, ai_response, re.IGNORECASE)
            name_matches.extend(matches)

        # 패턴 2: "종목코드: XXXXXX" 찾기 (다양한 형태 지원)
        code_patterns = [
            r"종목코드\s*[:：]\s*([A-Z]?[0-9]{2,6})(?=\s*(?:\n|$|[가-힣]*[:：]|\s*-\s*))",
            r"코드\s*[:：]\s*([A-Z]?[0-9]{2,6})",
            # JSON에서 발견된 패턴: "(종목코드: 042660)"
            r"\(\s*종목코드\s*[:：]\s*([0-9]{6})\s*\)",
        ]

        code_matches = []
        for pattern in code_patterns:
            matches = re.findall(pattern, ai_response, re.IGNORECASE)
            code_matches.extend(matches)

        # 이름과 코드 매칭
        if name_matches and code_matches:
            for name in name_matches:
                name = name.strip()
                for code in code_matches:
                    code = code.strip()
                    if self._is_valid_candidate(name, code):
                        logger.info(f"✅ 구조화된 패턴에서 추출 성공: {name} ({code})")
                        return self._create_success_result(
                            name, code, "structured_info", 0.9
                        )

        # 패턴 2: "삼성전자(005930)" 형태
        bracket_pattern = r"([가-힣A-Za-z0-9\s&\-\.]+)\s*\(\s*([A-Z]?[0-9]{2,6})\s*\)"
        matches = re.findall(bracket_pattern, ai_response, re.IGNORECASE)

        for match in matches:
            stock_name = match[0].strip()
            stock_code = match[1].strip()

            if self._is_valid_candidate(stock_name, stock_code):
                logger.info(f"✅ 괄호 패턴에서 추출 성공: {stock_name} ({stock_code})")
                return self._create_success_result(
                    stock_name, stock_code, "bracket_pattern", 0.8
                )

        logger.warning("AI 응답에서 종목 정보를 찾지 못했습니다.")
        return self._create_empty_result(user_prompt)

    def _is_valid_candidate(self, stock_name: str, stock_code: str) -> bool:
        """종목명과 코드가 유효한지 검증해요"""
        return self._is_valid_name(stock_name) and self._is_valid_code(stock_code)

    def _is_valid_name(self, name: str) -> bool:
        """종목명이 유효한지 검증해요"""
        if not name or len(name.strip()) < 2:
            return False

        name = name.strip()

        # 제외 단어 체크
        if name in self.exclude_words:
            return False

        # 길이 체크
        if len(name) < 2 or len(name) > 50:
            return False

        # 숫자만인 경우 제외
        if name.isdigit():
            return False

        return True

    def _is_valid_code(self, code: str) -> bool:
        """종목코드가 유효한지 검증해요"""
        if not code or len(code.strip()) < 2:
            return False

        code = code.strip()

        # 한국 종목코드 (6자리 숫자)
        if re.match(r"^\d{6}$", code):
            return True

        # 해외 티커 (2-5글자 알파벳)
        if re.match(r"^[A-Z]{2,5}$", code):
            return True

        return False

    def _create_success_result(
        self, stock_name: str, stock_code: str, pattern: str, confidence: float
    ) -> Dict:
        """추출 성공 시 결과를 생성해요"""
        return {
            "stock_name": stock_name,
            "stock_code": stock_code,
            "ticker": stock_code,
            "found": True,
            "confidence": confidence,
            "pattern": pattern,
            "final_score": confidence,
            "extraction_method": "dynamic_ai_response",
        }

    def _create_empty_result(self, prompt: str = "") -> Dict:
        """추출 실패 시 빈 결과를 생성해요"""
        return {
            "stock_name": None,
            "stock_code": None,
            "ticker": None,
            "found": False,
            "confidence": 0.0,
            "pattern": None,
            "final_score": 0.0,
            "extraction_method": "dynamic_ai_response",
            "original_prompt": prompt,
        }
