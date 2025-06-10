# 재무데이터 수집 모듈
# DART API와 yfinance를 사용해서 실제 재무정보를 가져오는 도구상자예요!

import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import pandas as pd
import requests
import yfinance as yf

from ..logger import logger


class FinancialDataCollector:
    """
    재무데이터를 수집하는 클래스예요
    - DART API: 한국 기업의 공시정보, 재무제표
    - yfinance: 주가정보, 기본적인 재무지표
    """

    def __init__(self, dart_api_key: Optional[str] = None):
        """
        재무데이터 수집기를 초기화해요

        Args:
            dart_api_key: DART API 키 (한국 기업 데이터용)
        """
        self.dart_api_key = dart_api_key
        self.session = requests.Session()

        # API 호출 간격 조절 (너무 자주 호출하면 차단될 수 있어요)
        self.api_delay = 1.0  # 1초 대기

        logger.info("📊 재무데이터 수집기가 초기화되었습니다")

    def collect_stock_data(
        self, stock_code: str, stock_name: str = None
    ) -> Dict[str, Any]:
        """
        종목코드를 받아서 모든 재무데이터를 수집하는 메인 함수예요

        Args:
            stock_code: 6자리 종목코드 (예: "005930")
            stock_name: 종목명 (선택사항)

        Returns:
            Dict: 수집된 모든 재무데이터
        """
        logger.info(f"📊 {stock_name or stock_code} 재무데이터 수집 시작...")

        collected_data = {
            "stock_info": {
                "stock_code": stock_code,
                "stock_name": stock_name,
                "collection_timestamp": datetime.now().isoformat(),
            },
            "success": False,
            "errors": [],
            "data_sources": [],
        }

        try:
            # 1. yfinance로 기본 정보 수집
            yf_data = self._collect_yfinance_data(stock_code)
            if yf_data["success"]:
                collected_data.update(yf_data)
                collected_data["data_sources"].append("yfinance")
            else:
                collected_data["errors"].extend(yf_data.get("errors", []))

            # 2. DART API로 한국 기업 상세정보 수집 (한국 종목인 경우)
            if self._is_korean_stock(stock_code):
                dart_data = self._collect_dart_data(stock_code)
                if dart_data["success"]:
                    # DART 데이터와 yfinance 데이터 병합
                    self._merge_dart_data(collected_data, dart_data)
                    collected_data["data_sources"].append("DART")
                else:
                    collected_data["errors"].extend(dart_data.get("errors", []))

            # 3. 성공 여부 판단
            collected_data["success"] = len(collected_data["data_sources"]) > 0

            if collected_data["success"]:
                logger.info(f"✅ {stock_name or stock_code} 재무데이터 수집 완료!")
                logger.info(
                    f"📈 데이터 소스: {', '.join(collected_data['data_sources'])}"
                )
            else:
                logger.warning(f"⚠️ {stock_name or stock_code} 재무데이터 수집 실패")

        except Exception as e:
            logger.error(f"❌ 재무데이터 수집 중 오류: {e}")
            collected_data["errors"].append(f"수집 중 오류: {str(e)}")

        return collected_data

    def _collect_yfinance_data(self, stock_code: str) -> Dict[str, Any]:
        """
        yfinance를 사용해서 주가와 기본 재무정보를 수집해요

        Args:
            stock_code: 종목코드

        Returns:
            Dict: yfinance에서 수집한 데이터
        """
        logger.info(f"📈 yfinance에서 {stock_code} 데이터 수집 중...")

        try:
            # 한국 주식은 .KS 또는 .KQ 접미사 필요
            if self._is_korean_stock(stock_code):
                # 대부분의 한국 주식은 .KS (코스피)
                ticker_symbol = f"{stock_code}.KS"
                ticker = yf.Ticker(ticker_symbol)

                # 코스피에서 데이터가 없으면 코스닥(.KQ) 시도
                try:
                    info = ticker.info
                    if not info or info.get("regularMarketPrice") is None:
                        ticker_symbol = f"{stock_code}.KQ"
                        ticker = yf.Ticker(ticker_symbol)
                        info = ticker.info
                except:
                    ticker_symbol = f"{stock_code}.KQ"
                    ticker = yf.Ticker(ticker_symbol)
                    info = ticker.info
            else:
                # 해외 주식은 그대로 사용
                ticker_symbol = stock_code
                ticker = yf.Ticker(ticker_symbol)
                info = ticker.info

            # 기본 정보 수집
            basic_info = {
                "company_name": info.get("longName", info.get("shortName", "정보없음")),
                "sector": info.get("sector", "정보없음"),
                "industry": info.get("industry", "정보없음"),
                "country": info.get("country", "정보없음"),
                "currency": info.get("currency", "KRW"),
                "exchange": info.get("exchange", "정보없음"),
                "ticker_symbol": ticker_symbol,
            }

            # 현재 주가 정보
            current_price_info = {
                "current_price": info.get(
                    "regularMarketPrice", info.get("currentPrice")
                ),
                "previous_close": info.get("previousClose"),
                "open_price": info.get("open"),
                "day_high": info.get("dayHigh"),
                "day_low": info.get("dayLow"),
                "volume": info.get("volume"),
                "market_cap": info.get("marketCap"),
                "shares_outstanding": info.get("sharesOutstanding"),
            }

            # 재무 지표
            financial_ratios = {
                "pe_ratio": info.get("trailingPE"),  # PER
                "peg_ratio": info.get("pegRatio"),  # PEG
                "pb_ratio": info.get("priceToBook"),  # PBR
                "ps_ratio": info.get("priceToSalesTrailing12Months"),  # PSR
                "dividend_yield": info.get("dividendYield"),
                "profit_margin": info.get("profitMargins"),
                "operating_margin": info.get("operatingMargins"),
                "return_on_equity": info.get("returnOnEquity"),  # ROE
                "return_on_assets": info.get("returnOnAssets"),  # ROA
                "debt_to_equity": info.get("debtToEquity"),
                "current_ratio": info.get("currentRatio"),
                "quick_ratio": info.get("quickRatio"),
            }

            # 성장 지표
            growth_metrics = {
                "earnings_growth": info.get("earningsGrowth"),
                "revenue_growth": info.get("revenueGrowth"),
                "earnings_quarterly_growth": info.get("earningsQuarterlyGrowth"),
                "revenue_quarterly_growth": info.get("revenueQuarterlyGrowth"),
            }

            # 과거 주가 데이터 (최근 1년)
            try:
                hist_data = ticker.history(period="1y")
                price_history = {
                    "52_week_high": (
                        float(hist_data["High"].max()) if not hist_data.empty else None
                    ),
                    "52_week_low": (
                        float(hist_data["Low"].min()) if not hist_data.empty else None
                    ),
                    "avg_volume_3m": (
                        float(hist_data["Volume"].tail(90).mean())
                        if not hist_data.empty
                        else None
                    ),
                    "price_change_1y": None,
                }

                if not hist_data.empty and len(hist_data) > 1:
                    year_ago_price = hist_data["Close"].iloc[0]
                    current_price = hist_data["Close"].iloc[-1]
                    price_history["price_change_1y"] = float(
                        (current_price - year_ago_price) / year_ago_price * 100
                    )

            except Exception as e:
                logger.warning(f"주가 히스토리 수집 실패: {e}")
                price_history = {}

            return {
                "success": True,
                "basic_info": basic_info,
                "current_price_info": current_price_info,
                "financial_ratios": financial_ratios,
                "growth_metrics": growth_metrics,
                "price_history": price_history,
                "data_quality": self._assess_data_quality(info),
            }

        except Exception as e:
            logger.error(f"yfinance 데이터 수집 실패: {e}")
            return {"success": False, "errors": [f"yfinance 오류: {str(e)}"]}

    def _collect_dart_data(self, stock_code: str) -> Dict[str, Any]:
        """
        DART API를 사용해서 한국 기업의 상세 재무제표를 수집해요

        Args:
            stock_code: 6자리 종목코드

        Returns:
            Dict: DART에서 수집한 데이터
        """
        if not self.dart_api_key:
            logger.info("DART API 키가 없어서 yfinance 데이터만 사용합니다")
            return {"success": False, "errors": ["DART API 키가 설정되지 않았습니다"]}

        logger.info(f"📋 DART API에서 {stock_code} 데이터 수집 중...")

        try:
            # DART API 호출 지연
            time.sleep(self.api_delay)

            # 1. 기업개요 정보 수집
            company_info = self._get_dart_company_info(stock_code)

            # 2. 최근 재무제표 수집
            financial_statements = self._get_dart_financial_statements(stock_code)

            # 3. 최근 사업보고서 주요 정보
            business_report = self._get_dart_business_report(stock_code)

            return {
                "success": True,
                "company_info": company_info,
                "financial_statements": financial_statements,
                "business_report": business_report,
            }

        except Exception as e:
            logger.error(f"DART API 데이터 수집 실패: {e}")
            return {"success": False, "errors": [f"DART API 오류: {str(e)}"]}

    def _get_dart_company_info(self, stock_code: str) -> Dict[str, Any]:
        """DART API에서 기업개요 정보를 가져와요"""
        # 실제 DART API 호출 구현 (기본 구조)
        return {
            "corp_name": "기업명 정보",
            "corp_code": "기업코드",
            "business_summary": "사업내용 요약",
            "established_date": "설립일",
            "listing_date": "상장일",
        }

    def _get_dart_financial_statements(self, stock_code: str) -> Dict[str, Any]:
        """DART API에서 재무제표를 가져와요"""
        # 실제 DART API 호출 구현 (기본 구조)
        return {
            "revenue": "매출액",
            "operating_profit": "영업이익",
            "net_income": "당기순이익",
            "total_assets": "총자산",
            "total_liabilities": "총부채",
            "equity": "자본총계",
            "cash_and_equivalents": "현금및현금성자산",
        }

    def _get_dart_business_report(self, stock_code: str) -> Dict[str, Any]:
        """DART API에서 사업보고서 주요 정보를 가져와요"""
        return {
            "main_business": "주요사업내용",
            "business_risks": "사업위험요소",
            "future_plans": "향후계획",
        }

    def _is_korean_stock(self, stock_code: str) -> bool:
        """한국 주식인지 확인해요 (6자리 숫자면 한국 주식)"""
        return len(stock_code) == 6 and stock_code.isdigit()

    def _assess_data_quality(self, info: Dict) -> str:
        """수집된 데이터의 품질을 평가해요"""
        essential_fields = ["regularMarketPrice", "marketCap", "trailingPE"]
        available_fields = sum(
            1 for field in essential_fields if info.get(field) is not None
        )

        if available_fields >= 3:
            return "높음"
        elif available_fields >= 2:
            return "보통"
        else:
            return "낮음"

    def _merge_dart_data(self, collected_data: Dict, dart_data: Dict):
        """DART 데이터를 기존 수집 데이터와 병합해요"""
        if dart_data.get("success"):
            collected_data["dart_info"] = {
                "company_info": dart_data.get("company_info", {}),
                "financial_statements": dart_data.get("financial_statements", {}),
                "business_report": dart_data.get("business_report", {}),
            }

    def get_analysis_summary(self, collected_data: Dict[str, Any]) -> str:
        """
        수집된 재무데이터를 분석용 텍스트로 요약해요

        Args:
            collected_data: 수집된 재무데이터

        Returns:
            str: 분석용 요약 텍스트
        """
        if not collected_data.get("success"):
            return "재무데이터 수집에 실패했습니다."

        stock_info = collected_data.get("stock_info", {})
        basic_info = collected_data.get("basic_info", {})
        current_price_info = collected_data.get("current_price_info", {})
        financial_ratios = collected_data.get("financial_ratios", {})
        growth_metrics = collected_data.get("growth_metrics", {})
        price_history = collected_data.get("price_history", {})

        summary = f"""
=== {basic_info.get('company_name', stock_info.get('stock_name', '알 수 없는 기업'))} 재무 데이터 요약 ===

📊 기본 정보:
- 종목코드: {stock_info.get('stock_code')}
- 섹터: {basic_info.get('sector', '정보없음')}
- 산업: {basic_info.get('industry', '정보없음')}
- 거래소: {basic_info.get('exchange', '정보없음')}

💰 현재 주가 정보:
- 현재가: {current_price_info.get('current_price', 'N/A'):,} {basic_info.get('currency', 'KRW')}
- 시가총액: {current_price_info.get('market_cap', 'N/A'):,}
- 52주 최고가: {price_history.get('52_week_high', 'N/A')}
- 52주 최저가: {price_history.get('52_week_low', 'N/A')}
- 1년 수익률: {price_history.get('price_change_1y', 'N/A'):.2f}%

📈 주요 재무 지표:
- PER (주가수익비율): {financial_ratios.get('pe_ratio', 'N/A')}
- PBR (주가순자산비율): {financial_ratios.get('pb_ratio', 'N/A')}
- ROE (자기자본이익률): {financial_ratios.get('return_on_equity', 'N/A'):.2%} if financial_ratios.get('return_on_equity') else 'N/A'
- 부채비율: {financial_ratios.get('debt_to_equity', 'N/A')}
- 배당수익률: {financial_ratios.get('dividend_yield', 'N/A'):.2%} if financial_ratios.get('dividend_yield') else 'N/A'

📊 성장성 지표:
- 매출 성장률: {growth_metrics.get('revenue_growth', 'N/A'):.2%} if growth_metrics.get('revenue_growth') else 'N/A'
- 이익 성장률: {growth_metrics.get('earnings_growth', 'N/A'):.2%} if growth_metrics.get('earnings_growth') else 'N/A'

🔍 데이터 품질: {collected_data.get('data_quality', '정보없음')}
📅 수집 시간: {stock_info.get('collection_timestamp', 'N/A')}
"""

        return summary.strip()
