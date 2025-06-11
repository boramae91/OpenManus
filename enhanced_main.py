#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
개선된 주식 분석 시스템 (Enhanced Main Flow)

새로운 플로우:
1. 프롬프트 입력
2. 종목+종목코드 감지
3. 📊 DART API + yfinance 재무정보 수집
4. 🏷️ Classifier (재무데이터 기반 분류)
5. 📈 분석 에이전트 (재무데이터 기반 상세분석)
6. 💾 JSON 파일 생성 (모든 데이터 포함)
"""

import asyncio
import json
import os
import re

# 환경변수 로딩 (가장 먼저 실행)
from dotenv import load_dotenv

load_dotenv()  # .env 파일에서 환경변수 로딩

# 프로젝트 경로 설정
import sys
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 모듈 import
from app.agent.manus import Manus
from app.agent.stock_classifier import StockClassifier
from app.agent.stock_name_extractor import StockNameExtractor
from app.data_collector import FinancialDataCollector
from app.data_collector.enhanced_financial_data_collector import (
    EnhancedDartDataCollector,
)
from app.llm import LLM
from app.logger import logger

# 🚀 io_logger 모듈을 import해서 일관된 로그 저장을 위해 사용해요
from io_logger import save_interaction_log

# 동적 종목 정보 추출을 위한 AI 에이전트 import
try:
    from app.agent.dynamic_stock_extractor import DynamicStockExtractor

    DYNAMIC_EXTRACTOR_AVAILABLE = True
    logger.info("🚀 동적 종목 추출 에이전트 로드 성공!")
except ImportError as e:
    logger.warning(f"동적 종목 추출 에이전트 로드 실패: {e}")
    DYNAMIC_EXTRACTOR_AVAILABLE = False


class EnhancedStockAnalysisSystem:
    """
    개선된 주식 분석 시스템 클래스
    실제 재무데이터를 기반으로 정확한 분석을 수행해요!
    """

    def __init__(self):
        """시스템 초기화"""
        logger.info("🚀 개선된 주식 분석 시스템 초기화...")

        # 에이전트들 초기화
        self.llm = LLM()
        self.stock_classifier = StockClassifier(llm=self.llm)
        self.manus_agent = Manus(llm=self.llm)

        # 🤖 종목 감지용 AI 에이전트들 초기화
        self.stock_name_extractor = StockNameExtractor()
        if DYNAMIC_EXTRACTOR_AVAILABLE:
            self.dynamic_stock_extractor = DynamicStockExtractor()
            logger.info("🎯 동적 종목 추출 에이전트 초기화 완료")
        else:
            self.dynamic_stock_extractor = None
            logger.warning("⚠️ 동적 종목 추출 에이전트 사용 불가")

        # 재무데이터 수집기 초기화 (DART API 키는 선택사항)
        dart_api_key = os.getenv("DART_API_KEY")  # 환경변수에서 가져오기
        self.financial_collector = FinancialDataCollector(dart_api_key=dart_api_key)

        # 🚀 Enhanced DART API 수집기 초기화 (새로운 기능들)
        self.enhanced_dart_collector = EnhancedDartDataCollector(
            dart_api_key=dart_api_key
        )

        # 결과 저장용
        self.analysis_results = {}

        logger.info("✅ 모든 컴포넌트 초기화 완료!")

        # DART API 상태 로그
        if dart_api_key:
            logger.info("🔑 DART API 키가 설정되었습니다 - Enhanced 기능 사용 가능!")
        else:
            logger.warning("⚠️ DART API 키가 없습니다 - yfinance 데이터만 사용됩니다")

    async def run_enhanced_analysis(self, user_prompt: str) -> Dict[str, Any]:
        """
        개선된 분석 플로우의 메인 실행 함수

        Args:
            user_prompt: 사용자 입력 프롬프트

        Returns:
            Dict: 전체 분석 결과
        """
        logger.info(f"🔍 개선된 분석 시작: {user_prompt}")

        results = {
            "user_prompt": user_prompt,
            "timestamp": datetime.now().isoformat(),
            "analysis_flow": "enhanced",
            "success": False,
            "steps": {},
        }

        try:
            # Step 1: 종목 및 종목코드 감지
            logger.info("📋 Step 1: 종목 및 종목코드 감지")
            stock_info = await self.extract_stock_info(user_prompt)
            results["steps"]["step1_stock_detection"] = stock_info

            if not stock_info["detected"]:
                results["error"] = "종목이나 종목코드를 감지할 수 없습니다"
                logger.warning("⚠️ 종목 감지 실패")
                return results

            logger.info(
                f"✅ 감지된 종목: {stock_info['stock_name']} ({stock_info['stock_code']})"
            )

            # Step 2: 재무데이터 수집 (기본 + Enhanced DART)
            logger.info("📊 Step 2: 실제 재무데이터 수집")

            # 2-1: 기본 재무데이터 수집 (yfinance + 기본 DART)
            financial_data = self.financial_collector.collect_stock_data(
                stock_code=stock_info["stock_code"], stock_name=stock_info["stock_name"]
            )
            results["steps"]["step2_financial_data"] = financial_data

            if not financial_data["success"]:
                logger.warning("⚠️ 기본 재무데이터 수집 실패 - 기존 방식으로 진행")
            else:
                logger.info(
                    f"✅ 기본 재무데이터 수집 완료 (출처: {', '.join(financial_data['data_sources'])})"
                )

            # 2-2: 🚀 Enhanced DART API 데이터 수집 (새로운 기능들)
            enhanced_dart_data = None
            if self.enhanced_dart_collector.is_available() and self._is_korean_stock(
                stock_info["stock_code"]
            ):
                logger.info("🔍 Enhanced DART 데이터 수집 시작...")
                enhanced_dart_data = (
                    self.enhanced_dart_collector.get_comprehensive_company_analysis(
                        stock_code=stock_info["stock_code"],
                        company_name=stock_info.get("stock_name"),
                    )
                )

                if enhanced_dart_data["success"]:
                    results["steps"]["step2_enhanced_dart_data"] = enhanced_dart_data
                    logger.info("✅ Enhanced DART 데이터 수집 완료!")
                else:
                    logger.warning(
                        f"⚠️ Enhanced DART 데이터 수집 실패: {enhanced_dart_data.get('error')}"
                    )
            else:
                logger.info(
                    "ℹ️ Enhanced DART 데이터 수집 생략 (API 키 없음 또는 해외 종목)"
                )

            # Step 3: 재무데이터 기반 종목 분류 (Enhanced 데이터 포함)
            logger.info("🏷️ Step 3: 재무데이터 기반 종목 분류")
            classification_result = await self.perform_enhanced_classification(
                user_prompt, stock_info, financial_data, enhanced_dart_data
            )
            results["steps"]["step3_classification"] = classification_result

            # Step 4: 재무데이터 기반 상세 분석 (Enhanced 데이터 포함)
            logger.info("📈 Step 4: 재무데이터 기반 상세 분석")
            analysis_result = await self.perform_enhanced_analysis(
                user_prompt,
                stock_info,
                financial_data,
                classification_result,
                enhanced_dart_data,
            )
            results["steps"]["step4_detailed_analysis"] = analysis_result

            # Step 5: 종합 결과 정리
            logger.info("📋 Step 5: 종합 결과 정리")
            final_summary = self.create_comprehensive_summary(results)
            results["final_summary"] = final_summary

            # Step 6: JSON 파일 저장
            logger.info("💾 Step 6: 결과 저장")
            saved_file = self.save_enhanced_results(results, stock_info)
            results["saved_file"] = saved_file

            results["success"] = True
            logger.info("🎉 개선된 분석 완료!")

        except Exception as e:
            logger.error(f"❌ 분석 중 오류 발생: {e}")
            results["error"] = str(e)

        return results

    async def extract_stock_info(self, prompt: str) -> Dict[str, Any]:
        """
        🚀 AI 기반 동적 웹검색 우선 종목 정보 추출

        순서:
        1. AI 웹검색 (최우선) - 실시간 웹 검색으로 정확한 종목코드 찾기
        2. 정규식 매핑 (백업) - 빠른 로컬 매칭
        3. 패턴 매칭 (최후 수단) - 기본 패턴 인식

        Args:
            prompt: 사용자 입력

        Returns:
            Dict: 추출된 종목 정보
        """
        result = {
            "detected": False,
            "stock_name": None,
            "stock_code": None,
            "detection_method": None,
        }

        logger.info("🚀 AI 기반 동적 웹검색 우선 종목 감지 시작...")

        try:
            # 🚀 1단계: Manus 에이전트로 AI 기반 동적 웹검색 시도 (최우선!)
            logger.info("🎯 AI 기반 동적 웹검색 시도... (최우선 방법)")

            # 종목 검색을 위한 특별한 프롬프트 구성
            search_prompt = f"""
다음 질문에서 종목명과 종목코드를 찾아주세요:
"{prompt}"

웹에서 검색해서 정확한 종목명과 6자리 종목코드를 찾아주세요.
한국 주식이면 6자리 숫자 종목코드를, 해외 주식이면 티커를 찾아주세요.

결과는 다음 형식으로 출력해주세요:
종목명: [회사명]
종목코드: [6자리 숫자 또는 티커]

예시:
종목명: 삼성전자
종목코드: 005930

예시:
종목명: Apple
종목코드: AAPL
"""

            # 메모리 초기화
            self.manus_agent.memory.clear()
            self.manus_agent.update_memory("user", search_prompt)

            # AI 에이전트 실행
            search_result = await self.manus_agent.run()

            # 결과 처리
            if hasattr(search_result, "__aiter__"):
                ai_response = ""
                async for response in search_result:
                    ai_response += response + "\n"
            else:
                ai_response = str(search_result)

            # AI 응답에서 종목 정보 추출
            extracted_info = self._parse_ai_stock_response(
                ai_response, "ai_web_search_priority"
            )
            if extracted_info["detected"]:
                result.update(extracted_info)
                logger.info(
                    f"🎉 AI 웹검색 성공 (최우선): {result['stock_name']} ({result['stock_code']})"
                )
                return result
            else:
                logger.info("⚠️ AI 웹검색에서 종목 감지 실패, 백업 방법 시도...")

            # 2단계: StockNameExtractor로 빠른 매핑 시도 (백업)
            logger.info("📝 StockNameExtractor 백업 시도...")
            extracted_name, extracted_code = (
                self.stock_name_extractor.extract_from_prompt(prompt)
            )

            if extracted_name and extracted_code:
                result["detected"] = True
                result["stock_name"] = extracted_name
                result["stock_code"] = extracted_code
                result["detection_method"] = "stock_name_extractor_backup"
                logger.info(
                    f"✅ StockNameExtractor 백업 성공: {result['stock_name']} ({result['stock_code']})"
                )
                return result
            else:
                logger.info("⚠️ StockNameExtractor 백업에서도 종목 감지 실패")

            # 3단계: 마지막 수단으로 정규식 패턴 매칭
            logger.info("🔍 정규식 패턴 매칭 시도...")
            fallback_result = self._fallback_pattern_matching(prompt)
            if fallback_result["detected"]:
                result.update(fallback_result)
                logger.info(
                    f"✅ 패턴 매칭 성공: {result['stock_name']} ({result['stock_code']})"
                )
                return result

            logger.warning("❌ 모든 방법으로 종목 감지 실패")
            return result

        except Exception as e:
            logger.error(f"❌ 종목 감지 중 오류 발생: {e}")

            # 오류 발생시 폴백으로 정규식 시도
            logger.info("🔄 오류 발생으로 폴백 패턴 매칭 시도...")
            fallback_result = self._fallback_pattern_matching(prompt)
            if fallback_result["detected"]:
                result.update(fallback_result)
                logger.info(
                    f"✅ 폴백 매칭 성공: {result['stock_name']} ({result['stock_code']})"
                )

            return result

    def _parse_ai_stock_response(self, ai_response: str, method: str) -> Dict[str, Any]:
        """AI 에이전트 응답에서 종목 정보 파싱"""
        result = {
            "detected": False,
            "stock_name": None,
            "stock_code": None,
            "detection_method": f"ai_{method}",
        }

        if not ai_response:
            return result

        # main.py의 extract_stock_code_from_browser_results 로직 활용
        # 브라우저 검색 결과에서 종목코드 패턴들
        browser_patterns = [
            # Company Guide 패턴: "한화오션(A042660) | 업종분석"
            r"([가-힣A-Za-z0-9\s&\-\.]+)\(A([0-9]{6})\)\s*\|\s*업종분석",
            # 일반 괄호 패턴: "삼성전자(005930)"
            r"([가-힣A-Za-z0-9\s&\-\.]+)\(A?([0-9]{6})\)",
            # URL 패턴: "gicode=A042660"
            r"gicode=A([0-9]{6})",
            # 브라우저 출력 패턴: "한화오션 042660"
            r"([가-힣A-Za-z0-9\s&\-\.]+)\s+([0-9]{6})",
            # 직접 언급 패턴: "종목코드: 042660"
            r"종목코드:\s*([0-9]{6})",
            # Step 결과 패턴에서 추출
            r"Step\s+\d+:.*?([0-9]{6})",
        ]

        found_codes = []
        found_names = []

        for pattern in browser_patterns:
            matches = re.findall(pattern, ai_response, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) == 2:
                        name, code = match
                        found_names.append(name.strip())
                        found_codes.append(code)
                    else:
                        # 마지막 요소가 종목코드
                        code = match[-1]
                        found_codes.append(code)
                else:
                    found_codes.append(match)

        # 가장 자주 나타나는 종목코드 선택
        if found_codes:
            from collections import Counter

            most_common_code = Counter(found_codes).most_common(1)[0][0]

            # 종목코드 유효성 검사
            if len(most_common_code) == 6 and most_common_code.isdigit():
                if most_common_code.startswith(("0", "1", "2", "3")):
                    result["detected"] = True
                    result["stock_code"] = most_common_code

                    # 매칭되는 회사명이 있으면 사용
                    if found_names:
                        most_common_name = Counter(found_names).most_common(1)[0][0]
                        result["stock_name"] = most_common_name.strip()

                    return result

        return result

    def _fallback_pattern_matching(self, prompt: str) -> Dict[str, Any]:
        """폴백용 정규식 패턴 매칭"""
        result = {
            "detected": False,
            "stock_name": None,
            "stock_code": None,
            "detection_method": "pattern_fallback",
        }

        # 1. 6자리 종목코드 패턴 검색 (한국 주식)
        korean_code_pattern = r"\b(\d{6})\b"
        korean_codes = re.findall(korean_code_pattern, prompt)

        if korean_codes:
            result["detected"] = True
            result["stock_code"] = korean_codes[0]
            result["detection_method"] = "korean_stock_code_fallback"
            return result

        # 2. 해외 티커 패턴 검색 (2-5자리 대문자)
        ticker_pattern = r"\b([A-Z]{2,5})\b"
        tickers = re.findall(ticker_pattern, prompt.upper())

        if tickers:
            # 일반적인 단어 제외
            excluded_words = {"THE", "AND", "FOR", "YOU", "ARE", "NOT", "BUT", "CAN"}
            valid_tickers = [t for t in tickers if t not in excluded_words]

            if valid_tickers:
                result["detected"] = True
                result["stock_code"] = valid_tickers[0]
                result["detection_method"] = "ticker_symbol_fallback"
                return result

                # 3. 주요 한국 회사명 패턴 검색 (폴백용 간소화된 목록)
        korean_companies = {
            "삼성전자": "005930",
            "삼성증권": "016360",
            "SK하이닉스": "000660",
            "LG전자": "066570",
            "현대자동차": "005380",
            "카카오": "035720",
            "네이버": "035420",
            "한화에어로스페이스": "012450",
            "한화오션": "042660",
        }

        for company, code in korean_companies.items():
            if company in prompt:
                result["detected"] = True
                result["stock_name"] = company
                result["stock_code"] = code
                result["detection_method"] = "company_name_fallback"
                return result

        return result

    def _is_korean_stock(self, stock_code: str) -> bool:
        """한국 주식인지 확인해요 (6자리 숫자면 한국 주식)"""
        if not stock_code:
            return False
        return len(stock_code) == 6 and stock_code.isdigit()

    async def perform_enhanced_classification(
        self,
        user_prompt: str,
        stock_info: Dict,
        financial_data: Dict,
        enhanced_dart_data: Dict = None,
    ) -> Dict[str, Any]:
        """
        재무데이터를 활용한 개선된 종목 분류

        Args:
            user_prompt: 사용자 질문
            stock_info: 감지된 종목 정보
            financial_data: 수집된 재무데이터

        Returns:
            Dict: 분류 결과
        """
        try:
            # 분류 키워드 감지
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
            ]

            should_classify = any(
                keyword in user_prompt.lower() for keyword in classification_keywords
            )

            if not should_classify:
                # 종목이 감지되면 자동으로 분류 실행
                should_classify = stock_info["detected"]

            if should_classify:
                logger.info("🏷️ 종목 분류 실행...")

                # 재무데이터가 있으면 포함해서 분류
                if financial_data.get("success"):
                    financial_summary = self.financial_collector.get_analysis_summary(
                        financial_data
                    )

                    # Enhanced DART 데이터 요약 생성
                    dart_summary = ""
                    if enhanced_dart_data and enhanced_dart_data.get("success"):
                        dart_summary = self._create_dart_summary(enhanced_dart_data)

                    enhanced_prompt = f"""
다음 종목에 대한 분류를 수행해주세요:

사용자 질문: {user_prompt}

실제 재무데이터:
{financial_summary}

{dart_summary}

위 실제 재무정보를 바탕으로 정확한 분류를 수행해주세요.
"""
                else:
                    enhanced_prompt = (
                        f"다음 종목에 대한 분류를 수행해주세요: {user_prompt}"
                    )

                # Stock Classifier 실행
                # reset() 대신 memory.clear() 사용
                self.stock_classifier.memory.clear()
                self.stock_classifier.update_memory("user", enhanced_prompt)

                classification_response = ""
                # run()을 await으로 호출하고 결과를 직접 사용
                run_result = await self.stock_classifier.run()
                # run_result가 제너레이터라면 반복하여 수집
                if hasattr(run_result, "__aiter__"):
                    async for response in run_result:
                        classification_response += response + "\n"
                else:
                    # 단일 결과라면 바로 사용
                    classification_response = str(run_result)

                return {
                    "performed": True,
                    "method": (
                        "enhanced_with_financial_data"
                        if financial_data.get("success")
                        else "standard"
                    ),
                    "response": classification_response.strip(),
                    "financial_data_used": financial_data.get("success", False),
                }
            else:
                return {
                    "performed": False,
                    "reason": "분류 키워드나 종목이 감지되지 않음",
                }

        except Exception as e:
            logger.error(f"분류 중 오류: {e}")
            return {"performed": False, "error": str(e)}

    def _create_dart_summary(self, enhanced_dart_data: Dict) -> str:
        """Enhanced DART 데이터 요약 생성"""
        if not enhanced_dart_data or not enhanced_dart_data.get("success"):
            return ""

        summary_parts = ["📊 추가 DART 상세 정보:"]

        # 재무분석 정보
        if "financial_analysis" in enhanced_dart_data:
            financial = enhanced_dart_data["financial_analysis"]
            if financial.get("success"):
                summary_parts.append("• 상세 재무제표 데이터 포함")

        # 지배구조 정보
        if "governance_analysis" in enhanced_dart_data:
            governance = enhanced_dart_data["governance_analysis"]
            if governance.get("success") and "major_shareholders" in governance:
                shareholders = governance["major_shareholders"][:3]  # 상위 3명만
                summary_parts.append("• 주요 주주 정보:")
                for shareholder in shareholders:
                    name = shareholder.get("shareholder_name", "")
                    ratio = shareholder.get("ownership_ratio", 0)
                    if name and ratio:
                        summary_parts.append(f"  - {name}: {ratio}%")

        # 투자정보
        if "investment_analysis" in enhanced_dart_data:
            investment = enhanced_dart_data["investment_analysis"]
            if investment.get("success") and "dividend_info" in investment:
                summary_parts.append("• 배당 정보 포함")

        # 공시정보
        if "disclosure_monitoring" in enhanced_dart_data:
            disclosure = enhanced_dart_data["disclosure_monitoring"]
            if disclosure.get("success") and "recent_disclosures" in disclosure:
                recent_count = len(disclosure["recent_disclosures"])
                summary_parts.append(f"• 최근 공시: {recent_count}건")

        return "\n".join(summary_parts) if len(summary_parts) > 1 else ""

    def _create_comprehensive_dart_analysis(self, enhanced_dart_data: Dict) -> str:
        """Enhanced DART 데이터의 포괄적 분석 생성"""
        if not enhanced_dart_data or not enhanced_dart_data.get("success"):
            return ""

        analysis_parts = ["📊 **Enhanced DART 종합 분석**:"]

        # 1. 재무분석 상세 정보
        if "financial_analysis" in enhanced_dart_data:
            financial = enhanced_dart_data["financial_analysis"]
            if financial.get("success"):
                analysis_parts.append("\n🏦 **상세 재무분석**:")

                # 개별재무제표 정보
                if "individual_statements" in financial:
                    individual = financial["individual_statements"]
                    if individual.get("assets"):
                        total_assets = individual["assets"].get("total_assets", 0)
                        analysis_parts.append(f"• 개별 총자산: {total_assets:,}원")
                    if individual.get("liabilities"):
                        total_debt = individual["liabilities"].get(
                            "total_liabilities", 0
                        )
                        analysis_parts.append(f"• 개별 총부채: {total_debt:,}원")
                    if individual.get("equity"):
                        total_equity = individual["equity"].get("total_equity", 0)
                        analysis_parts.append(f"• 개별 총자본: {total_equity:,}원")

                # 연결재무제표 정보
                if "consolidated_statements" in financial:
                    consolidated = financial["consolidated_statements"]
                    if consolidated.get("assets"):
                        total_assets = consolidated["assets"].get("total_assets", 0)
                        analysis_parts.append(f"• 연결 총자산: {total_assets:,}원")
                    if consolidated.get("equity"):
                        total_equity = consolidated["equity"].get("total_equity", 0)
                        analysis_parts.append(f"• 연결 총자본: {total_equity:,}원")

                # 분기별 실적
                if "quarterly_performance" in financial:
                    quarterly = financial["quarterly_performance"]
                    if quarterly:
                        analysis_parts.append(
                            f"• 분기별 실적 데이터: {len(quarterly)}분기"
                        )

        # 2. 지배구조 상세 정보
        if "governance_analysis" in enhanced_dart_data:
            governance = enhanced_dart_data["governance_analysis"]
            if governance.get("success"):
                analysis_parts.append("\n🏢 **기업지배구조 분석**:")

                # 주요 주주 정보
                if "major_shareholders" in governance:
                    shareholders = governance["major_shareholders"][:3]  # 상위 3명
                    analysis_parts.append("• 주요 주주:")
                    for i, shareholder in enumerate(shareholders, 1):
                        name = shareholder.get("shareholder_name", "")
                        ratio = shareholder.get("ownership_ratio", 0)
                        if name and ratio:
                            analysis_parts.append(f"  {i}. {name}: {ratio}%")

                # 임원 정보
                if "executives" in governance:
                    executives = governance["executives"]
                    if executives:
                        analysis_parts.append(f"• 등록임원 수: {len(executives)}명")

                # 이사 보수
                if "director_compensation" in governance:
                    compensation = governance["director_compensation"]
                    if compensation:
                        total_compensation = sum(
                            comp.get("total_compensation", 0) for comp in compensation
                        )
                        analysis_parts.append(
                            f"• 이사 총 보수: {total_compensation:,}원"
                        )

                # 사외이사
                if "outside_directors" in governance:
                    outside = governance["outside_directors"]
                    if outside:
                        analysis_parts.append(f"• 사외이사 수: {len(outside)}명")

        # 3. 투자정보 상세 분석
        if "investment_analysis" in enhanced_dart_data:
            investment = enhanced_dart_data["investment_analysis"]
            if investment.get("success"):
                analysis_parts.append("\n💰 **투자정보 분석**:")

                # 배당 정보
                if "dividend_info" in investment:
                    dividend = investment["dividend_info"]
                    if dividend:
                        latest_dividend = dividend[0] if dividend else {}
                        dividend_rate = latest_dividend.get("dividend_rate", 0)
                        dividend_amount = latest_dividend.get("dividend_amount", 0)
                        if dividend_rate or dividend_amount:
                            analysis_parts.append(f"• 최근 배당률: {dividend_rate}%")
                            analysis_parts.append(f"• 최근 배당금: {dividend_amount}원")

                # 증자감자 정보
                if "capital_changes" in investment:
                    capital = investment["capital_changes"]
                    if capital:
                        analysis_parts.append(f"• 자본변동 이력: {len(capital)}건")

                # 자기주식 정보
                if "treasury_stock" in investment:
                    treasury = investment["treasury_stock"]
                    if treasury:
                        latest_treasury = treasury[0] if treasury else {}
                        stock_count = latest_treasury.get("stock_count", 0)
                        if stock_count:
                            analysis_parts.append(f"• 자기주식 보유: {stock_count:,}주")

                # 타법인 출자
                if "investments" in investment:
                    investments = investment["investments"]
                    if investments:
                        analysis_parts.append(f"• 타법인 출자: {len(investments)}건")

        # 4. 공시 모니터링 정보
        if "disclosure_monitoring" in enhanced_dart_data:
            disclosure = enhanced_dart_data["disclosure_monitoring"]
            if disclosure.get("success"):
                analysis_parts.append("\n📢 **실시간 공시 모니터링**:")

                # 최근 공시
                if "recent_disclosures" in disclosure:
                    recent = disclosure["recent_disclosures"]
                    if recent:
                        analysis_parts.append(f"• 최근 30일 공시: {len(recent)}건")

                        # 최신 3개 공시 표시
                        for i, disc in enumerate(recent[:3], 1):
                            report_name = disc.get("report_name", "")
                            receipt_date = disc.get("receipt_date", "")
                            if report_name:
                                analysis_parts.append(
                                    f"  {i}. {report_name} ({receipt_date})"
                                )

                # 중요 공시
                if "important_notices" in disclosure:
                    important = disclosure["important_notices"]
                    if important:
                        analysis_parts.append(f"• 중요 공시: {len(important)}건")

                # 정정 공시
                if "corrections" in disclosure:
                    corrections = disclosure["corrections"]
                    if corrections:
                        analysis_parts.append(f"• 정정 공시: {len(corrections)}건")

        analysis_parts.append("\n💡 **Enhanced DART 특별 인사이트**:")
        analysis_parts.append(
            "• 위 정보는 일반 재무데이터에서는 얻을 수 없는 DART 전용 상세 정보입니다"
        )
        analysis_parts.append(
            "• 특히 지배구조, 배당정책, 실시간 공시는 투자 의사결정에 중요한 차별화 정보입니다"
        )

        return "\n".join(analysis_parts)

    async def perform_enhanced_analysis(
        self,
        user_prompt: str,
        stock_info: Dict,
        financial_data: Dict,
        classification_result: Dict,
        enhanced_dart_data: Dict = None,
    ) -> Dict[str, Any]:
        """
        재무데이터를 활용한 개선된 상세 분석

        Args:
            user_prompt: 사용자 질문
            stock_info: 감지된 종목 정보
            financial_data: 수집된 재무데이터
            classification_result: 분류 결과

        Returns:
            Dict: 상세 분석 결과
        """
        try:
            logger.info("📊 통합 재무데이터 기반 상세 분석 실행...")

            # 🚀 통합 분석용 프롬프트 구성
            analysis_prompt = f"사용자 질문: {user_prompt}\n\n"

            # 📊 Step 2-1: 기본 재무데이터 (yfinance + 기본 DART)
            basic_financial_included = False
            if financial_data.get("success"):
                financial_summary = self.financial_collector.get_analysis_summary(
                    financial_data
                )
                analysis_prompt += f"""
📊 **기본 재무데이터 (yfinance + 기본 DART)**:
{financial_summary}

"""
                basic_financial_included = True
                logger.info("✅ 기본 재무데이터를 분석에 포함했습니다")

            # 🚀 Step 2-2: Enhanced DART 상세 데이터 (한국 주식 전용)
            enhanced_dart_included = False
            if enhanced_dart_data and enhanced_dart_data.get("success"):
                enhanced_summary = self._create_comprehensive_dart_analysis(
                    enhanced_dart_data
                )
                if enhanced_summary:
                    analysis_prompt += f"""
🚀 **Enhanced DART 상세 분석**:
{enhanced_summary}

"""
                    enhanced_dart_included = True
                    logger.info("✅ Enhanced DART 데이터를 분석에 포함했습니다")

            # 🏷️ 분류 결과 포함
            if classification_result.get("performed"):
                analysis_prompt += f"""
🏷️ **AI 종목 분류 결과**:
{classification_result.get('response', '')}

"""

            # 🎯 통합 분석 지시사항
            analysis_method = "통합분석"
            if basic_financial_included and enhanced_dart_included:
                analysis_method = "완전통합분석"
                analysis_prompt += """
🎯 **통합 분석 지시사항**:
위의 기본 재무데이터와 Enhanced DART 상세 정보를 모두 종합하여 다음 관점에서 상세 분석해주세요:

1. **재무건전성 분석**:
   - 기본 재무비율과 상세 재무제표 비교 분석
   - 개별 vs 연결재무제표 차이점 분석
   - 분기별 실적 트렌드 분석

2. **기업지배구조 평가**:
   - 주요 주주 구조와 지분 안정성
   - 경영진 역량과 보상체계 적정성
   - 사외이사 독립성과 전문성

3. **투자자 친화 정책**:
   - 배당 정책과 주주환원 의지
   - 자기주식 운용과 자본 효율성
   - 증자감자 등 자본 정책 변화

4. **실시간 리스크 평가**:
   - 최근 공시사항과 주가 영향 요인
   - 중요 공시와 투자 의사결정 포인트
   - 정정공시 등 주의사항

5. **종합 투자 의견**:
   - 모든 데이터를 종합한 투자 추천 등급
   - 목표 주가와 투자 기간 제시
   - 핵심 리스크와 기회 요소 정리

특히 기본 재무데이터로는 알 수 없는 Enhanced DART만의 독특한 인사이트를 강조해주세요.
"""
            elif basic_financial_included:
                analysis_method = "기본재무분석"
                analysis_prompt += """
📊 **기본 재무분석 지시사항**:
기본 재무데이터를 중심으로 상세한 투자 분석을 수행해주세요.
특히 실제 재무데이터가 있다면 이를 중심으로 분석해주세요.
"""
            else:
                analysis_method = "일반분석"
                analysis_prompt += """
📝 **일반 분석 지시사항**:
사용 가능한 정보를 바탕으로 투자 분석을 수행해주세요.
"""

            logger.info(f"🎯 분석 방법: {analysis_method}")
            logger.info(f"📊 기본 재무데이터 포함: {basic_financial_included}")
            logger.info(f"🚀 Enhanced DART 포함: {enhanced_dart_included}")

            # Manus 에이전트 실행
            # reset() 대신 memory.clear() 사용
            self.manus_agent.memory.clear()
            self.manus_agent.update_memory("user", analysis_prompt)

            analysis_response = ""
            # run()을 await으로 호출하고 결과를 직접 사용
            run_result = await self.manus_agent.run()
            # run_result가 제너레이터라면 반복하여 수집
            if hasattr(run_result, "__aiter__"):
                async for response in run_result:
                    analysis_response += response + "\n"
            else:
                # 단일 결과라면 바로 사용
                analysis_response = str(run_result)

            return {
                "performed": True,
                "method": analysis_method,
                "response": analysis_response.strip(),
                "basic_financial_data_used": basic_financial_included,
                "enhanced_dart_data_used": enhanced_dart_included,
                "classification_included": classification_result.get(
                    "performed", False
                ),
                "analysis_completeness": (
                    "완전통합"
                    if (basic_financial_included and enhanced_dart_included)
                    else (
                        "부분통합"
                        if (basic_financial_included or enhanced_dart_included)
                        else "기본"
                    )
                ),
            }

        except Exception as e:
            logger.error(f"상세 분석 중 오류: {e}")
            return {"performed": False, "error": str(e)}

    def create_comprehensive_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """전체 분석 결과의 종합 요약을 생성해요"""
        stock_info = results["steps"].get("step1_stock_detection", {})
        financial_data = results["steps"].get("step2_financial_data", {})
        classification = results["steps"].get("step3_classification", {})
        analysis = results["steps"].get("step4_detailed_analysis", {})

        return {
            "analyzed_stock": {
                "name": stock_info.get("stock_name"),
                "code": stock_info.get("stock_code"),
                "detection_method": stock_info.get("detection_method"),
            },
            "data_sources": {
                "financial_data_collected": financial_data.get("success", False),
                "data_sources": financial_data.get("data_sources", []),
                "data_quality": financial_data.get("data_quality", "없음"),
            },
            "analysis_quality": {
                "classification_performed": classification.get("performed", False),
                "detailed_analysis_performed": analysis.get("performed", False),
                "financial_data_enhanced": financial_data.get("success", False),
            },
            "key_insights": self.extract_key_insights(classification, analysis),
        }

    def extract_key_insights(
        self, classification: Dict, analysis: Dict
    ) -> Dict[str, Any]:
        """분석 결과에서 핵심 인사이트를 추출해요"""
        insights = {
            "classification": None,
            "investment_outlook": None,
            "risk_factors": None,
            "recommendation": None,
        }

        # 분류 결과에서 핵심 정보 추출
        if classification.get("performed"):
            class_response = classification.get("response", "")
            # 간단한 키워드 기반 추출 (실제로는 더 정교한 NLP 처리 필요)
            if "우량주" in class_response:
                insights["classification"] = "우량주"
            elif "고성장주" in class_response:
                insights["classification"] = "고성장주"
            elif "자산주" in class_response:
                insights["classification"] = "자산주"

        # 분석 결과에서 투자 전망 추출
        if analysis.get("performed"):
            analysis_response = analysis.get("response", "")
            if "긍정적" in analysis_response or "매수" in analysis_response:
                insights["investment_outlook"] = "긍정적"
            elif "부정적" in analysis_response or "매도" in analysis_response:
                insights["investment_outlook"] = "부정적"
            else:
                insights["investment_outlook"] = "중립적"

        return insights

    def save_enhanced_results(
        self, results: Dict[str, Any], stock_info: Dict[str, Any]
    ) -> str:
        """🚀 io_logger를 사용해서 개선된 분석 결과를 일관된 형식으로 저장해요 (원본 데이터 포함)"""
        try:
            # 사용자 프롬프트와 최종 응답 추출
            user_prompt = results.get("user_prompt", "")

            # 최종 응답 구성 (단계별 결과를 종합)
            final_response = []

            # 종목 감지 결과
            if "step1_stock_detection" in results.get("steps", {}):
                stock_detection = results["steps"]["step1_stock_detection"]
                if stock_detection.get("detected"):
                    final_response.append(
                        f"📊 감지된 종목: {stock_detection.get('stock_name')} ({stock_detection.get('stock_code')})"
                    )

            # 분류 결과
            if "step3_classification" in results.get("steps", {}):
                classification = results["steps"]["step3_classification"]
                if classification.get("performed"):
                    final_response.append("🏷️ 종목 분류:")
                    final_response.append(classification.get("response", ""))

            # 상세 분석 결과
            if "step4_detailed_analysis" in results.get("steps", {}):
                analysis = results["steps"]["step4_detailed_analysis"]
                if analysis.get("performed"):
                    final_response.append("📈 상세 분석:")
                    final_response.append(analysis.get("response", ""))

            # 종합 요약
            if "final_summary" in results:
                final_response.append("📋 종합 요약:")
                final_response.append(str(results["final_summary"]))

            response_text = "\n\n".join(final_response)

            # 🚀 첨부된 JSON 파일과 동일한 형식의 단계별 정보 구성
            steps_text = []
            steps_text.append("")  # 첫 번째는 빈 문자열

            # 각 단계별 결과를 문자열로 변환
            for step_key, step_data in results.get("steps", {}).items():
                if step_key == "step1_stock_detection" and step_data.get("detected"):
                    steps_text.append(
                        f"📊 감지된 종목: {step_data.get('stock_name')} ({step_data.get('stock_code')})"
                    )
                elif step_key == "step2_financial_data" and step_data.get("success"):
                    steps_text.append(
                        f"📈 재무데이터 수집 성공: {', '.join(step_data.get('data_sources', []))}"
                    )
                elif step_key == "step2_enhanced_dart_data" and step_data.get(
                    "success"
                ):
                    steps_text.append("🚀 Enhanced DART 데이터 수집 성공")
                elif step_key == "step3_classification" and step_data.get("performed"):
                    steps_text.append("🏷️ 종목 분류 완료")
                elif step_key == "step4_detailed_analysis" and step_data.get(
                    "performed"
                ):
                    steps_text.append("📊 상세 분석 완료")

            steps_text.append(response_text)  # 전체 응답 내용
            steps_text.append("")  # 마지막은 빈 문자열

            # 📊 원본 데이터 추가 준비
            raw_data_section = self._prepare_raw_data_for_json(results)

            # 메타데이터 구성 (원본 데이터 포함)
            meta_data = {
                "analysis_flow": results.get("analysis_flow", "enhanced"),
                "success": results.get("success", False),
                "timestamp": results.get("timestamp"),
                "stock_info": stock_info,
                "data_quality": results.get("steps", {})
                .get("step2_financial_data", {})
                .get("data_quality", "없음"),
                "enhanced_features": {
                    "financial_data_used": results.get("steps", {})
                    .get("step2_financial_data", {})
                    .get("success", False),
                    "enhanced_dart_used": "step2_enhanced_dart_data"
                    in results.get("steps", {}),
                    "classification_performed": results.get("steps", {})
                    .get("step3_classification", {})
                    .get("performed", False),
                    "detailed_analysis_performed": results.get("steps", {})
                    .get("step4_detailed_analysis", {})
                    .get("performed", False),
                },
                # 🚀 원본 데이터 섹션 추가
                "raw_data": raw_data_section,
            }

            # 🚀 io_logger를 사용해서 첨부된 JSON 파일과 동일한 형식으로 저장
            filepath = save_interaction_log(
                prompt=user_prompt,
                response=response_text,
                steps=steps_text,
                meta=meta_data,
            )

            logger.info(f"💾 Enhanced 분석 결과 저장 (원본 데이터 포함): {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"결과 저장 중 오류: {e}")
            return None

    def _prepare_raw_data_for_json(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        JSON 저장을 위한 원본 데이터 준비
        yfinance와 DART에서 가져온 모든 원본 데이터를 정리해요
        """
        raw_data = {
            "data_sources_summary": {
                "yfinance_data_available": False,
                "dart_basic_data_available": False,
                "enhanced_dart_data_available": False,
            },
            "yfinance_raw_data": {},
            "dart_basic_raw_data": {},
            "enhanced_dart_raw_data": {},
        }

        try:
            # 1. 🔍 yfinance 원본 데이터 추출
            financial_data = results.get("steps", {}).get("step2_financial_data", {})
            if financial_data.get("success"):
                raw_data["data_sources_summary"]["yfinance_data_available"] = True

                # yfinance에서 수집한 모든 데이터를 포함
                yfinance_data = {
                    "basic_info": financial_data.get("basic_info", {}),
                    "current_price_info": financial_data.get("current_price_info", {}),
                    "financial_ratios": financial_data.get("financial_ratios", {}),
                    "growth_metrics": financial_data.get("growth_metrics", {}),
                    "price_history": financial_data.get("price_history", {}),
                    "data_quality": financial_data.get("data_quality", "정보없음"),
                    "data_sources": financial_data.get("data_sources", []),
                    "collection_info": {
                        "success": financial_data.get("success", False),
                        "errors": financial_data.get("errors", []),
                        "stock_info": financial_data.get("stock_info", {}),
                    },
                }

                # DART 기본 정보가 포함되어 있다면 분리
                if "dart_info" in financial_data:
                    raw_data["data_sources_summary"]["dart_basic_data_available"] = True
                    raw_data["dart_basic_raw_data"] = financial_data["dart_info"]

                raw_data["yfinance_raw_data"] = yfinance_data
                logger.info("✅ yfinance 원본 데이터 JSON 준비 완료")

            # 2. 🚀 Enhanced DART 원본 데이터 추출
            enhanced_dart_data = results.get("steps", {}).get(
                "step2_enhanced_dart_data", {}
            )
            if enhanced_dart_data.get("success"):
                raw_data["data_sources_summary"]["enhanced_dart_data_available"] = True

                # Enhanced DART에서 수집한 모든 데이터를 포함
                enhanced_dart_raw = {
                    "collection_info": {
                        "success": enhanced_dart_data.get("success", False),
                        "stock_code": enhanced_dart_data.get("stock_code", ""),
                        "collected_at": enhanced_dart_data.get("collected_at", ""),
                        "error": enhanced_dart_data.get("error", ""),
                    },
                    "financial_analysis": enhanced_dart_data.get(
                        "financial_analysis", {}
                    ),
                    "governance_analysis": enhanced_dart_data.get(
                        "governance_analysis", {}
                    ),
                    "investment_analysis": enhanced_dart_data.get(
                        "investment_analysis", {}
                    ),
                    "disclosure_monitoring": enhanced_dart_data.get(
                        "disclosure_monitoring", {}
                    ),
                }

                raw_data["enhanced_dart_raw_data"] = enhanced_dart_raw
                logger.info("✅ Enhanced DART 원본 데이터 JSON 준비 완료")

            # 3. 📊 데이터 소스별 통계 정보 추가
            raw_data["data_statistics"] = self._calculate_data_statistics(raw_data)

            logger.info("📊 원본 데이터 JSON 준비 완료")

        except Exception as e:
            logger.error(f"❌ 원본 데이터 준비 중 오류: {e}")
            raw_data["preparation_error"] = str(e)

        return raw_data

    def _calculate_data_statistics(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """원본 데이터의 통계 정보를 계산해요"""
        stats = {
            "total_data_points": 0,
            "yfinance_data_points": 0,
            "enhanced_dart_data_points": 0,
            "data_completeness": "정보없음",
        }

        try:
            # yfinance 데이터 포인트 계산
            yfinance_data = raw_data.get("yfinance_raw_data", {})
            if yfinance_data:
                yfinance_count = 0
                for section_name, section_data in yfinance_data.items():
                    if isinstance(section_data, dict):
                        # None이 아닌 값들만 카운트
                        yfinance_count += sum(
                            1 for v in section_data.values() if v is not None
                        )
                stats["yfinance_data_points"] = yfinance_count

            # Enhanced DART 데이터 포인트 계산
            enhanced_dart_data = raw_data.get("enhanced_dart_raw_data", {})
            if enhanced_dart_data:
                dart_count = 0
                for section_name, section_data in enhanced_dart_data.items():
                    if isinstance(section_data, dict):
                        dart_count += self._count_nested_dict_values(section_data)
                stats["enhanced_dart_data_points"] = dart_count

            # 총 데이터 포인트
            stats["total_data_points"] = (
                stats["yfinance_data_points"] + stats["enhanced_dart_data_points"]
            )

            # 데이터 완성도 평가
            if stats["total_data_points"] > 100:
                stats["data_completeness"] = "매우높음"
            elif stats["total_data_points"] > 50:
                stats["data_completeness"] = "높음"
            elif stats["total_data_points"] > 20:
                stats["data_completeness"] = "보통"
            else:
                stats["data_completeness"] = "낮음"

        except Exception as e:
            logger.error(f"데이터 통계 계산 오류: {e}")
            stats["calculation_error"] = str(e)

        return stats

    def _count_nested_dict_values(
        self, data: Dict, max_depth: int = 3, current_depth: int = 0
    ) -> int:
        """중첩된 딕셔너리의 값 개수를 재귀적으로 계산해요"""
        if current_depth > max_depth:
            return 0

        count = 0
        for value in data.values():
            if isinstance(value, dict):
                count += self._count_nested_dict_values(
                    value, max_depth, current_depth + 1
                )
            elif isinstance(value, list):
                count += len(value)
            elif value is not None:
                count += 1
        return count


async def main():
    """메인 실행 함수 - 한 번 실행하고 자동 종료"""
    print("🚀 개선된 주식 분석 시스템에 오신 것을 환영합니다!")
    print("=" * 60)
    print("📊 새로운 기능:")
    print("  ✅ 실제 재무데이터 기반 분석 (yfinance + DART API)")
    print("  ✅ 정량적 지표 기반 정밀 분류")
    print("  ✅ 데이터 품질 평가 및 신뢰도 측정")
    print("  ✅ 종합적인 결과 저장")
    print("=" * 60)

    # 시스템 초기화
    system = EnhancedStockAnalysisSystem()

    try:
        # 사용자 입력 받기 (한 번만)
        print("\n" + "=" * 50)
        user_input = input("📝 질문을 입력하세요: ").strip()

        if not user_input:
            print("❌ 빈 입력입니다. 프로그램을 종료합니다.")
            return

        print(f"\n🔍 분석 시작: {user_input}")
        print("-" * 50)

        # 개선된 분석 실행
        results = await system.run_enhanced_analysis(user_input)

        # 결과 출력
        if results["success"]:
            print("\n✅ 분석 완료!")

            # 종합 요약 출력
            summary = results.get("final_summary", {})
            analyzed_stock = summary.get("analyzed_stock", {})
            data_sources = summary.get("data_sources", {})

            print(
                f"📊 분석 대상: {analyzed_stock.get('name', '정보없음')} ({analyzed_stock.get('code', '정보없음')})"
            )
            print(
                f"📈 데이터 수집: {'성공' if data_sources.get('financial_data_collected') else '실패'}"
            )
            if data_sources.get("data_sources"):
                print(f"🗂️ 데이터 출처: {', '.join(data_sources['data_sources'])}")
            print(f"🔍 데이터 품질: {data_sources.get('data_quality', '정보없음')}")

            # 저장된 파일 정보
            if results.get("saved_file"):
                print(f"💾 결과 저장: {results['saved_file']}")

            print("\n📁 상세 결과는 저장된 JSON 파일을 확인해주세요!")
            print("🎉 분석이 완료되었습니다. 프로그램을 종료합니다.")

        else:
            print(f"❌ 분석 실패: {results.get('error', '알 수 없는 오류')}")
            print("⚠️ 프로그램을 종료합니다.")

    except KeyboardInterrupt:
        print("\n👋 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"❌ 시스템 오류: {e}")
        print("⚠️ 프로그램을 종료합니다.")


if __name__ == "__main__":
    asyncio.run(main())
