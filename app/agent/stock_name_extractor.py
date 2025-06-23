#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
종목명 추출 전용 에이전트
- 사용자 프롬프트에서 정확한 종목명을 추출하는 특화된 에이전트
- AI 응답 분석 대신 입력 시점에서 바로 종목명 감지
"""

import asyncio
import logging
import re
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


class StockNameExtractor:
    """
    사용자 프롬프트에서 종목명과 종목코드를 추출하는 AI 에이전트입니다.

    **개선된 기능:**
    1. 정적 매핑 테이블 우선 시도
    2. 매핑 실패 시 웹검색을 통한 동적 종목 감지
    3. 해외 종목 지원 강화 (록히드마틴, 방산업체 등)
    """

    def __init__(self):
        """종목명 추출 에이전트를 초기화해요"""
        # 한국 주요 종목 리스트 (종목명 -> (한글명, 종목코드))
        self.korean_stocks = {
            # 삼성 계열
            "삼성바이오로직스": ("삼성바이오로직스", "207940"),
            "삼성전자": ("삼성전자", "005930"),
            "삼성SDI": ("삼성SDI", "006400"),
            "삼성화재": ("삼성화재", "000810"),
            "삼성물산": ("삼성물산", "028260"),
            "삼성생명": ("삼성생명", "032830"),
            "삼성중공업": ("삼성중공업", "010140"),
            "삼성카드": ("삼성카드", "029780"),
            "삼성증권": ("삼성증권", "016360"),
            "삼성": ("삼성전자", "005930"),  # 기본값은 삼성전자
            # SK 계열
            "SK하이닉스": ("SK하이닉스", "000660"),
            "SK텔레콤": ("SK텔레콤", "017670"),
            "SK이노베이션": ("SK이노베이션", "096770"),
            "SK바이오팜": ("SK바이오팜", "326030"),
            "SK바이오사이언스": ("SK바이오사이언스", "302440"),
            "SK": ("SK하이닉스", "000660"),  # 기본값은 SK하이닉스
            # LG 계열
            "LG전자": ("LG전자", "066570"),
            "LG화학": ("LG화학", "051910"),
            "LG에너지솔루션": ("LG에너지솔루션", "373220"),
            "LG생활건강": ("LG생활건강", "051900"),
            "LG유플러스": ("LG유플러스", "032640"),
            "LG디스플레이": ("LG디스플레이", "034220"),
            "LG": ("LG전자", "066570"),  # 기본값은 LG전자
            # 현대 계열
            "현대자동차": ("현대자동차", "005380"),
            "현대모비스": ("현대모비스", "012330"),
            "현대중공업": ("현대중공업", "009540"),
            "현대건설": ("현대건설", "000720"),
            "현대차": ("현대차", "005380"),
            "현대": ("현대자동차", "005380"),  # 기본값은 현대자동차
            # 기타 주요 종목
            "기아": ("기아", "000270"),
            "포스코": ("포스코", "005490"),
            "포스코홀딩스": ("포스코홀딩스", "005490"),
            "네이버": ("네이버", "035420"),
            "카카오": ("카카오", "035720"),
            "카카오뱅크": ("카카오뱅크", "323410"),
            "카카오페이": ("카카오페이", "377300"),
            "셀트리온": ("셀트리온", "068270"),
            "셀트리온헬스케어": ("셀트리온헬스케어", "091990"),
            # 한화 계열
            "한화에어로스페이스": ("한화에어로스페이스", "012450"),
            "한화시스템": ("한화시스템", "272210"),
            "한화솔루션": ("한화솔루션", "009830"),
            "한화": ("한화", "000880"),
            # 항공우주 관련
            "한국항공우주": ("한국항공우주", "047810"),
            "한국항공우주산업": ("한국항공우주산업", "047810"),
            "KAI": ("한국항공우주", "047810"),
            # 기타
            "휴니드": ("휴니드", "005870"),
            "한컴라이프케어": ("한컴라이프케어", "372910"),
            "두산": ("두산", "000150"),
            "롯데": ("롯데", "004990"),
            "신한": ("신한", "055550"),
            "KB": ("KB", "105560"),
            "하나": ("하나", "086790"),
            "메리츠증권": ("메리츠증권", "008560"),
        }

        # 해외 주식 매핑 (한글명/영문명 -> (영문명, 티커))
        self.foreign_stocks = {
            # 미국 주식 (한글명)
            "애플": ("APPLE", "AAPL"),
            "마이크로소프트": ("MICROSOFT", "MSFT"),
            "테슬라": ("TESLA", "TSLA"),
            "구글": ("GOOGLE", "GOOGL"),
            "알파벳": ("ALPHABET", "GOOGL"),
            "아마존": ("AMAZON", "AMZN"),
            "메타": ("META", "META"),
            "페이스북": ("FACEBOOK", "META"),
            "넷플릭스": ("NETFLIX", "NFLX"),
            "엔비디아": ("NVIDIA", "NVDA"),
            "인텔": ("INTEL", "INTC"),
            "보잉": ("BOEING", "BA"),
            "코카콜라": ("COCACOLA", "KO"),
            "맥도날드": ("MCDONALDS", "MCD"),
            "월마트": ("WALMART", "WMT"),
            "존슨앤존슨": ("JNJ", "JNJ"),
            "화이자": ("PFIZER", "PFE"),
            # 영문명도 매핑
            "APPLE": ("APPLE", "AAPL"),
            "MICROSOFT": ("MICROSOFT", "MSFT"),
            "TESLA": ("TESLA", "TSLA"),
            "GOOGLE": ("GOOGLE", "GOOGL"),
            "ALPHABET": ("ALPHABET", "GOOGL"),
            "AMAZON": ("AMAZON", "AMZN"),
            "META": ("META", "META"),
            "FACEBOOK": ("FACEBOOK", "META"),
            "NETFLIX": ("NETFLIX", "NFLX"),
            "NVIDIA": ("NVIDIA", "NVDA"),
            "INTEL": ("INTEL", "INTC"),
            "BOEING": ("BOEING", "BA"),
        }

        # 종목코드 패턴
        self.korean_code_pattern = r"\b(\d{6})\b"  # 한국 6자리 종목코드
        self.us_ticker_pattern = r"\b([A-Z]{1,5})\b"  # 미국 티커 (1-5글자 대문자)

        # 웹검색 도구 초기화 (동적 종목 감지용)
        self._web_search_tool = None

        logger.info("종목명 추출 에이전트가 초기화되었습니다.")

    def _get_web_search_tool(self):
        """웹검색 도구를 지연 로딩으로 가져옵니다"""
        if self._web_search_tool is None:
            from app.tool.web_search import WebSearch

            self._web_search_tool = WebSearch()
        return self._web_search_tool

    async def search_stock_dynamically(
        self, query: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        웹검색을 통해 동적으로 종목 정보를 찾습니다.

        Args:
            query: 검색할 종목명 (예: "록히드마틴", "Lockheed Martin" 등)

        Returns:
            Tuple[종목명(영문), 종목코드/티커]: 검색 결과
        """
        try:
            logger.info(f"🌐 웹검색으로 종목 정보 검색 시작: {query}")

            # 검색 쿼리 구성 (다양한 형태로 시도)
            search_queries = [
                f"{query} stock ticker symbol",
                f"{query} 주식 종목코드",
                f"{query} stock price NYSE NASDAQ",
                f'"{query}" stock market ticker',
            ]

            for search_query in search_queries:
                try:
                    # 웹검색 실행
                    web_search = self._get_web_search_tool()
                    search_result = await web_search.execute(
                        query=search_query, num_results=3, fetch_content=False
                    )

                    if search_result and search_result.results:
                        # 검색 결과에서 종목 정보 추출
                        stock_info = self._extract_stock_from_search_results(
                            search_result.results, query
                        )
                        if stock_info[0]:  # 종목명이 발견되면
                            logger.info(
                                f"✅ 웹검색 성공: {query} -> {stock_info[0]} ({stock_info[1]})"
                            )
                            return stock_info

                except Exception as e:
                    logger.warning(f"⚠️ 검색 쿼리 '{search_query}' 실패: {e}")
                    continue

            logger.warning(f"❌ 모든 웹검색 시도 실패: {query}")
            return None, None

        except Exception as e:
            logger.error(f"❌ 동적 종목 검색 중 오류: {e}")
            return None, None

    def _extract_stock_from_search_results(
        self, search_results, original_query: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        검색 결과에서 종목 정보를 추출합니다.

        Args:
            search_results: 웹검색 결과 리스트
            original_query: 원본 검색어

        Returns:
            Tuple[종목명(영문), 종목코드/티커]: 추출된 종목 정보
        """
        import re

        # 종목코드/티커 패턴들
        ticker_patterns = [
            r"\b([A-Z]{1,5})\b",  # 1-5자리 대문자 (미국 티커)
            r"NYSE:\s*([A-Z]{1,5})",  # NYSE:AAPL 형태
            r"NASDAQ:\s*([A-Z]{1,5})",  # NASDAQ:MSFT 형태
            r"Ticker:\s*([A-Z]{1,5})",  # Ticker: LMT 형태
            r"Symbol:\s*([A-Z]{1,5})",  # Symbol: BA 형태
            r"\(([A-Z]{1,5})\)",  # (LMT) 형태
        ]

        # 회사명 정규화 패턴들
        company_patterns = [
            r"(.*?)\s+\([A-Z]{1,5}\)",  # 회사명 (티커) 형태
            r"(.*?)\s+Stock",  # 회사명 Stock 형태
            r"(.*?)\s+Corporation",  # 회사명 Corporation 형태
            r"(.*?)\s+Inc\.",  # 회사명 Inc. 형태
        ]

        found_tickers = []
        found_companies = []

        # 검색 결과에서 정보 추출
        for result in search_results:
            text_to_search = f"{result.title} {result.description}".lower()

            # 원본 쿼리와 유사한지 확인 (관련성 체크)
            query_lower = original_query.lower()
            if (
                query_lower not in text_to_search
                and self._calculate_similarity(query_lower, text_to_search) < 0.3
            ):
                continue  # 관련성이 낮으면 스킵

            # 티커 추출
            for pattern in ticker_patterns:
                matches = re.findall(
                    pattern, result.title + " " + result.description, re.IGNORECASE
                )
                for match in matches:
                    ticker = match.upper()
                    # 일반적인 단어 제외
                    if ticker not in [
                        "THE",
                        "AND",
                        "FOR",
                        "YOU",
                        "ARE",
                        "NOT",
                        "BUT",
                        "CAN",
                        "NEW",
                        "GET",
                    ]:
                        found_tickers.append(ticker)

            # 회사명 추출
            for pattern in company_patterns:
                matches = re.findall(pattern, result.title, re.IGNORECASE)
                for match in matches:
                    company = match.strip()
                    if len(company) > 2:
                        found_companies.append(company)

        # 가장 빈번한 티커와 회사명 선택
        if found_tickers:
            from collections import Counter

            most_common_ticker = Counter(found_tickers).most_common(1)[0][0]

            # 적절한 회사명 찾기
            company_name = None
            if found_companies:
                most_common_company = Counter(found_companies).most_common(1)[0][0]
                company_name = self._normalize_company_name(most_common_company)
            else:
                # 회사명이 없으면 원본 쿼리를 정규화하여 사용
                company_name = self._normalize_company_name(original_query)

            return company_name, most_common_ticker

        return None, None

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """두 텍스트의 유사도를 계산합니다 (간단한 단어 기반)"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union) if union else 0

    def _normalize_company_name(self, name: str) -> str:
        """회사명을 정규화하여 영문 형태로 변환합니다"""
        # 기본 정리
        name = name.strip().upper()

        # 일반적인 기업 접미사 제거
        suffixes = [
            " CORPORATION",
            " CORP",
            " INC",
            " LTD",
            " LIMITED",
            " COMPANY",
            " CO",
        ]
        for suffix in suffixes:
            if name.endswith(suffix):
                name = name[: -len(suffix)].strip()

        # 공백을 언더스코어로 변경
        return name.replace(" ", "_")

    def extract_from_prompt(self, prompt: str) -> Tuple[Optional[str], Optional[str]]:
        """
        사용자 프롬프트에서 종목명과 종목코드를 추출해요

        **개선된 로직:**
        1. 기존 매핑 테이블 우선 시도
        2. 실패 시 웹검색을 통한 동적 감지
        """
        if not prompt or not prompt.strip():
            return None, None

        prompt = prompt.strip()
        logger.info(f"프롬프트에서 종목명 추출 시작: {prompt}")

        # 1. 한국 종목명 직접 매칭 (최우선)
        for korean_name, (english_name, stock_code) in self.korean_stocks.items():
            if korean_name in prompt:
                logger.info(
                    f"한국 종목 발견: {korean_name} -> {english_name} ({stock_code})"
                )

                # 프롬프트에서 추가 종목코드가 있는지 확인
                additional_code = self._extract_stock_code(prompt)
                final_code = additional_code or stock_code

                return english_name, final_code

        # 2. 해외 종목명 매칭
        for foreign_name, (english_name, ticker) in self.foreign_stocks.items():
            if foreign_name in prompt:
                logger.info(
                    f"해외 종목 발견: {foreign_name} -> {english_name} ({ticker})"
                )
                return english_name, ticker

        # 3. 종목코드만 있는 경우
        stock_code = self._extract_stock_code(prompt)
        if stock_code:
            if len(stock_code) == 6 and stock_code.isdigit():
                # 한국 종목코드
                logger.info(f"한국 종목코드 발견: {stock_code}")
                return f"CODE{stock_code}", stock_code
            else:
                # 해외 티커
                logger.info(f"해외 티커 발견: {stock_code}")
                return stock_code, stock_code

        # 4. 🆕 웹검색을 통한 동적 종목 감지
        logger.info("🌐 매핑 테이블에서 찾지 못함, 웹검색 시도...")
        try:
            # 비동기 함수를 동기적으로 실행
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # 프롬프트에서 종목명으로 보이는 부분 추출
            potential_stock_names = self._extract_potential_stock_names(prompt)

            for potential_name in potential_stock_names:
                stock_name, ticker = loop.run_until_complete(
                    self.search_stock_dynamically(potential_name)
                )
                if stock_name and ticker:
                    logger.info(
                        f"✅ 웹검색으로 종목 발견: {potential_name} -> {stock_name} ({ticker})"
                    )
                    return stock_name, ticker

        except Exception as e:
            logger.warning(f"⚠️ 웹검색 중 오류: {e}")
        finally:
            try:
                loop.close()
            except:
                pass

        # 5. 아무것도 찾지 못한 경우
        logger.info("프롬프트에서 종목명을 찾지 못했습니다.")
        return None, None

    def _extract_potential_stock_names(self, prompt: str) -> list:
        """프롬프트에서 종목명으로 보이는 단어들을 추출합니다"""
        import re

        potential_names = []

        # 한글 회사명 패턴 (2-20글자)
        korean_pattern = r"([가-힣]{2,20})"
        korean_matches = re.findall(korean_pattern, prompt)

        # 영문 회사명 패턴 (2-30글자, 대소문자 혼합)
        english_pattern = r"\b([A-Za-z][A-Za-z\s]{1,29})\b"
        english_matches = re.findall(english_pattern, prompt)

        # 제외할 일반적인 단어들
        exclude_korean = {
            "분석",
            "종목",
            "기업",
            "정보",
            "결과",
            "전망",
            "투자",
            "주식",
            "시장",
            "에서",
            "에게",
            "에게서",
            "에는",
            "에도",
            "에만",
            "에서도",
            "대해",
            "대해서",
            "분석해",
            "알려",
            "설명",
            "요약",
            "보고서",
            "리포트",
        }

        exclude_english = {
            "about",
            "analysis",
            "stock",
            "market",
            "company",
            "report",
            "the",
            "and",
            "for",
            "with",
            "analysis",
            "please",
            "tell",
            "me",
            "give",
            "write",
        }

        # 한글 후보 추가
        for match in korean_matches:
            if match not in exclude_korean and len(match) >= 2:
                potential_names.append(match)

        # 영문 후보 추가
        for match in english_matches:
            cleaned = match.strip()
            if cleaned.lower() not in exclude_english and len(cleaned) >= 2:
                potential_names.append(cleaned)

        # 중복 제거 및 길이순 정렬 (긴 것이 더 구체적일 가능성)
        unique_names = list(set(potential_names))
        unique_names.sort(key=len, reverse=True)

        return unique_names[:3]  # 상위 3개만 시도

    def _extract_stock_code(self, text: str) -> Optional[str]:
        """텍스트에서 종목코드 추출"""
        # 한국 6자리 종목코드 찾기
        korean_matches = re.findall(self.korean_code_pattern, text)
        if korean_matches:
            return korean_matches[0]

        # 미국 티커 찾기 (너무 일반적인 단어 제외)
        us_matches = re.findall(self.us_ticker_pattern, text)
        exclude_words = {
            "THE",
            "AND",
            "OR",
            "FOR",
            "IN",
            "ON",
            "AT",
            "TO",
            "A",
            "AN",
            "STEP",
            "BY",
            "WITH",
            "FROM",
            "INTO",
            "OVER",
            "UNDER",
            "ABOUT",
            "AFTER",
            "BEFORE",
            "DURING",
            "WHILE",
            "SINCE",
            "UNTIL",
            "UPON",
            "WITHIN",
            "WITHOUT",
            "THROUGH",
            "ACROSS",
            "ALONG",
            "AROUND",
            "BELOW",
            "ABOVE",
            "BEHIND",
            "BESIDE",
            "BETWEEN",
            "BEYOND",
            "INSIDE",
            "OUTSIDE",
            "TOWARDS",
            "AGAINST",
            "AMONG",
            "BENEATH",
            "EXCEPT",
            "INSTEAD",
            "DESPITE",
            "REGARDING",
            "CONCERNING",
        }

        for match in us_matches:
            if match not in exclude_words and len(match) >= 2:
                return match

        return None

    def _extract_korean_pattern(self, text: str) -> Optional[str]:
        """패턴을 사용해서 한글 종목명 추출"""
        # 회사 접미사가 있는 패턴
        company_pattern = r"([가-힣]{2,}(?:바이오로직스|바이오텍|바이오|전자|전기|화학|물산|생명과학|제약|건설|중공업|해운|카드|증권|보험|생활건강|전력|가스|통신|시스템|솔루션|엔터테인먼트|게임즈|홀딩스|모비스|디스플레이))"

        matches = re.findall(company_pattern, text)
        if matches:
            return matches[0]

        # 일반 한글 회사명 (2-10글자)
        general_pattern = r"([가-힣]{2,10})"
        matches = re.findall(general_pattern, text)

        # 일반적인 단어들 제외 (더 포괄적으로)
        exclude_korean = {
            "분석",
            "종목",
            "기업",
            "정보",
            "결과",
            "전망",
            "투자",
            "주식",
            "시장",
            "에서",
            "에게",
            "달라고",
            "해달라고",
            "분석해",
            "알려",
            "설명",
            "오늘",
            "날씨",
            "어때",
            "상황",
            "전반적인",
            "전략",
            "알려줘",
            "요약해줘",
            "경제",
            "뉴스",
            "코스피",
            "달러",
            "환율",
            "지수",
            "시간",
            "방법",
            "어떻게",
            "무엇",
            "언제",
            "어디",
            "왜",
            "누구",
            "어느",
            "얼마",
            "그리고",
            "하지만",
            "그런데",
            "따라서",
            "그래서",
            "그러면",
            "만약",
            "때문",
            "위해",
            "통해",
            "대해",
            "관해",
            "에게",
            "부터",
            "까지",
            "코스닥",
            "나스닥",
            "거래소",
            "증권",
            "채권",
            "펀드",
            "옵션",
            "선물",
            "리츠",
            "부동산",
            "금리",
            "인플레이션",
            "디플레이션",
        }

        for match in matches:
            if match not in exclude_korean:
                return match

        return None

    def _convert_to_english(self, korean_name: str) -> str:
        """한글 종목명을 영문 티커로 변환"""
        # 이미 매핑에 있는지 확인
        if korean_name in self.korean_stocks:
            return self.korean_stocks[korean_name]

        # 매핑에 없으면 기본 변환 규칙 적용
        # 복잡한 로직 대신 간단하게 처리
        if "삼성" in korean_name:
            return f"SAMSUNG_{korean_name.replace('삼성', '').upper()}"
        elif "SK" in korean_name:
            return f"SK_{korean_name.replace('SK', '').upper()}"
        elif "LG" in korean_name:
            return f"LG_{korean_name.replace('LG', '').upper()}"
        elif "현대" in korean_name:
            return f"HYUNDAI_{korean_name.replace('현대', '').upper()}"
        else:
            # 한글을 로마자로 변환 (간단한 버전)
            return korean_name.upper()

    def is_stock_mentioned(self, prompt: str) -> bool:
        """프롬프트에 종목명이 언급되었는지 확인"""
        stock_name, stock_code = self.extract_from_prompt(prompt)
        return stock_name is not None

    def get_extracted_info(self, prompt: str) -> dict:
        """추출된 종목 정보를 딕셔너리로 반환 (티커 정보 포함)"""
        stock_name, ticker = self.extract_from_prompt(prompt)

        # 종목 타입 판별 - 실제 매핑 테이블을 기반으로 정확하게 판별
        stock_type = "unknown"
        market = "unknown"

        if stock_name and ticker:
            # 1. 한국 종목인지 확인 (매핑 테이블 기반)
            is_korean_stock = False
            for korean_name, (mapped_name, mapped_code) in self.korean_stocks.items():
                if stock_name == mapped_name or ticker == mapped_code:
                    is_korean_stock = True
                    break

            if is_korean_stock:
                stock_type = "korean"
                market = "KRX"
            else:
                # 2. 해외 종목인지 확인 (매핑 테이블 기반)
                is_foreign_stock = False
                for foreign_name, (
                    mapped_name,
                    mapped_ticker,
                ) in self.foreign_stocks.items():
                    if stock_name == mapped_name or ticker == mapped_ticker:
                        is_foreign_stock = True
                        break

                if is_foreign_stock:
                    stock_type = "foreign"
                    market = "US"
                else:
                    # 3. 패턴 기반 추론
                    if len(ticker) == 6 and ticker.isdigit():
                        stock_type = "korean"
                        market = "KRX"
                    elif ticker.startswith("CODE") and len(ticker) == 10:
                        stock_type = "korean"
                        market = "KRX"
                    elif len(ticker) <= 5 and ticker.isalpha() and ticker.isupper():
                        stock_type = "foreign"
                        market = "US"
                    else:
                        stock_type = "other"

        return {
            "stock_name": stock_name,  # 영문 종목명
            "ticker": ticker,  # 거래소 티커/종목코드
            "stock_code": ticker,  # 하위 호환성을 위해 유지
            "found": stock_name is not None,
            "stock_type": stock_type,  # korean, foreign, other
            "market": market,  # KRX, US, etc.
            "prompt": prompt,
        }
