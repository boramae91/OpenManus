# 재무데이터 수집 모듈
# DART API와 yfinance를 사용해서 실제 재무정보를 가져오는 도구상자예요!

import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
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
                dart_data = self._collect_dart_data(stock_code, stock_name)
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

        # 종목코드가 None인 경우 처리
        if not stock_code:
            return {"success": False, "errors": ["종목코드가 제공되지 않았습니다"]}

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

    def _collect_dart_data(
        self, stock_code: str, stock_name: str = None
    ) -> Dict[str, Any]:
        """
        DART API를 사용해서 한국 기업의 상세 재무제표를 수집해요

        Args:
            stock_code: 6자리 종목코드
            stock_name: 회사명 (동적 검색용)

        Returns:
            Dict: DART에서 수집한 데이터
        """
        if not self.dart_api_key:
            logger.info("DART API 키가 없어서 yfinance 데이터만 사용합니다")
            return {"success": False, "errors": ["DART API 키가 설정되지 않았습니다"]}

        logger.info(f"📋 DART API에서 {stock_code} ({stock_name}) 데이터 수집 중...")

        try:
            # DART API 호출 지연
            time.sleep(self.api_delay)

            # 1. 기업개요 정보 수집 (회사명 포함)
            company_info = self._get_dart_company_info(stock_code, stock_name)

            # 2. 최근 재무제표 수집 (회사명 포함)
            financial_statements = self._get_dart_financial_statements(
                stock_code, stock_name
            )

            # 3. 최근 사업보고서 주요 정보 (회사명 포함)
            business_report = self._get_dart_business_report(stock_code, stock_name)

            return {
                "success": True,
                "company_info": company_info,
                "financial_statements": financial_statements,
                "business_report": business_report,
            }

        except Exception as e:
            logger.error(f"DART API 데이터 수집 실패: {e}")
            return {"success": False, "errors": [f"DART API 오류: {str(e)}"]}

    def _get_dart_company_info(
        self, stock_code: str, company_name: str = None
    ) -> Dict[str, Any]:
        """DART API에서 기업개요 정보를 가져와요 (회사명 동적 검색 지원)"""
        try:
            # 🚀 종목코드와 회사명을 이용해 법인고유번호 동적 검색
            corp_code = self._get_corp_code_from_stock_code(stock_code, company_name)
            if not corp_code:
                logger.warning(
                    f"종목코드 {stock_code} ({company_name})에 대한 법인고유번호를 찾을 수 없습니다"
                )
                return self._get_fallback_company_info(stock_code)

            # DART API 호출
            url = "https://opendart.fss.or.kr/api/company.json"
            params = {
                "crtfc_key": self.dart_api_key,
                "corp_code": corp_code,
            }

            response = self.session.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "000":
                    company_data = data
                    return {
                        "corp_name": company_data.get("corp_name", "정보없음"),
                        "corp_code": corp_code,
                        "business_summary": company_data.get("bizr_no", "정보없음"),
                        "established_date": company_data.get("est_dt", "정보없음"),
                        "listing_date": company_data.get("acc_mt", "정보없음"),
                        "ceo_name": company_data.get("ceo_nm", "정보없음"),
                        "address": company_data.get("adres", "정보없음"),
                    }
                else:
                    logger.warning(f"DART API 오류: {data.get('message')}")
                    return self._get_fallback_company_info(stock_code)
            else:
                logger.warning(f"DART API 호출 실패: HTTP {response.status_code}")
                return self._get_fallback_company_info(stock_code)

        except Exception as e:
            logger.error(f"DART 기업개요 수집 중 오류: {e}")
            return self._get_fallback_company_info(stock_code)

    def _get_dart_financial_statements(
        self, stock_code: str, company_name: str = None
    ) -> Dict[str, Any]:
        """DART API에서 실제 재무제표 숫자 데이터를 가져와요 (회사명 동적 검색 지원)"""
        try:
            # 🚀 종목코드와 회사명을 이용해 법인고유번호 동적 검색
            corp_code = self._get_corp_code_from_stock_code(stock_code, company_name)
            if not corp_code:
                logger.warning(
                    f"종목코드 {stock_code} ({company_name})에 대한 법인고유번호를 찾을 수 없습니다"
                )
                return self._get_fallback_financial_data()

            # 🚀 실제 DART API에서 단일회사 주요계정 조회
            current_year = datetime.now().year - 1  # 작년 데이터
            url = "https://opendart.fss.or.kr/api/fnlttSinglAcnt.json"
            params = {
                "crtfc_key": self.dart_api_key,
                "corp_code": corp_code,
                "bsns_year": str(current_year),
                "reprt_code": "11011",  # 사업보고서
            }

            response = self.session.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "000":
                    # 재무제표 데이터 파싱
                    accounts = data.get("list", [])
                    financial_data = self._parse_dart_financial_data(accounts)

                    if financial_data:
                        logger.info(
                            f"✅ DART 실제 재무데이터 수집 성공: {len(accounts)}개 계정"
                        )
                        return financial_data
                    else:
                        logger.warning("DART 데이터 파싱 실패")
                        return self._get_fallback_financial_data()
                else:
                    logger.warning(f"DART API 오류: {data.get('message')}")
                    return self._get_fallback_financial_data()
            else:
                logger.warning(f"DART API 호출 실패: HTTP {response.status_code}")
                return self._get_fallback_financial_data()

        except Exception as e:
            logger.error(f"DART 재무제표 수집 중 오류: {e}")
            return self._get_fallback_financial_data()

    def _parse_dart_financial_data(self, accounts: list) -> Dict[str, Any]:
        """DART API 응답을 실제 숫자 데이터로 파싱해요"""
        financial_data = {}

        # 주요 계정과목 매핑 (한국어 → 영어)
        account_mapping = {
            "매출액": "revenue",
            "영업이익": "operating_profit",
            "영업이익(손실)": "operating_profit",
            "당기순이익": "net_income",
            "당기순이익(손실)": "net_income",
            "자산총계": "total_assets",
            "부채총계": "total_liabilities",
            "자본총계": "total_equity",
            "현금및현금성자산": "cash_and_equivalents",
            "유동자산": "current_assets",
            "비유동자산": "non_current_assets",
            "유동부채": "current_liabilities",
            "비유동부채": "non_current_liabilities",
        }

        for account in accounts:
            account_name = account.get("account_nm", "")
            current_amount = account.get("thstrm_amount", "0")

            # 매핑된 계정과목인지 확인
            if account_name in account_mapping:
                key = account_mapping[account_name]

                # 숫자로 변환 (단위: 원, 콤마 제거)
                try:
                    if current_amount and current_amount != "-":
                        # 콤마 제거하고 정수로 변환
                        amount_value = int(current_amount.replace(",", ""))
                        financial_data[key] = amount_value
                        logger.debug(f"📊 {account_name}: {amount_value:,}원")
                    else:
                        financial_data[key] = 0
                except ValueError:
                    logger.warning(f"숫자 변환 실패: {account_name} = {current_amount}")
                    financial_data[key] = 0

        # 기본 계산값들 추가
        if financial_data:
            # 부채비율 계산
            if (
                "total_liabilities" in financial_data
                and "total_equity" in financial_data
            ):
                if financial_data["total_equity"] > 0:
                    debt_ratio = (
                        financial_data["total_liabilities"]
                        / financial_data["total_equity"]
                    )
                    financial_data["debt_ratio"] = round(debt_ratio, 2)

            # 영업이익률 계산
            if "operating_profit" in financial_data and "revenue" in financial_data:
                if financial_data["revenue"] > 0:
                    operating_margin = (
                        financial_data["operating_profit"] / financial_data["revenue"]
                    )
                    financial_data["operating_margin"] = round(operating_margin, 4)

            # 순이익률 계산
            if "net_income" in financial_data and "revenue" in financial_data:
                if financial_data["revenue"] > 0:
                    net_margin = (
                        financial_data["net_income"] / financial_data["revenue"]
                    )
                    financial_data["net_margin"] = round(net_margin, 4)

        return financial_data

    def _get_dart_business_report(
        self, stock_code: str, company_name: str = None
    ) -> Dict[str, Any]:
        """DART API에서 사업보고서 주요 정보를 가져와요 (회사명 동적 검색 지원)"""
        try:
            corp_code = self._get_corp_code_from_stock_code(stock_code, company_name)
            if not corp_code:
                return {
                    "main_business": "DART 연결 실패",
                    "business_risks": "정보없음",
                    "future_plans": "정보없음",
                }

            # 실제로는 더 복잡한 사업보고서 파싱이 필요하지만,
            # 기본적인 구조만 반환
            return {
                "main_business": f"법인고유번호 {corp_code} 기업의 주요사업",
                "business_risks": "시장변동성, 경쟁심화 등",
                "future_plans": "사업확장 및 기술개발 계획",
            }

        except Exception as e:
            logger.error(f"DART 사업보고서 수집 중 오류: {e}")
            return {
                "main_business": "정보 수집 실패",
                "business_risks": "정보없음",
                "future_plans": "정보없음",
            }

    def _get_corp_code_from_stock_code(
        self, stock_code: str, company_name: str = None
    ) -> str:
        """종목코드와 회사명을 이용해 법인고유번호를 동적으로 검색해요"""

        # 🚀 1단계: 회사명이 있으면 DART API로 동적 검색 (최우선!)
        if company_name:
            logger.info(
                f"🔍 회사명 '{company_name}'으로 DART 법인고유번호 동적 검색 시도..."
            )
            corp_code = self._search_corp_code_by_company_name(company_name, stock_code)
            if corp_code:
                logger.info(f"✅ 동적 검색 성공: {company_name} → {corp_code}")
                return corp_code
            else:
                logger.warning(f"⚠️ 회사명 '{company_name}' 동적 검색 실패")

        # 🗂️ 2단계: 백업용 하드코딩 매핑 테이블 (주요 종목만)
        logger.info(f"📋 종목코드 {stock_code} 백업 매핑 테이블 검색...")
        stock_to_corp_mapping = {
            "005930": "00126380",  # 삼성전자
            "000660": "00164779",  # SK하이닉스
            "035420": "00401731",  # NAVER
            "005380": "00164742",  # 현대자동차
            "051910": "00260985",  # LG화학
            "006400": "00119635",  # 삼성SDI
            "035720": "00401731",  # 카카오
            "207940": "00550917",  # 삼성바이오로직스
            "068270": "00346008",  # 셀트리온
            "012330": "00266463",  # 현대모비스
            "042660": "00138766",  # 한화오션
            "000270": "00326103",  # 기아
            "003550": "00120925",  # LG
            "066570": "00184904",  # LG전자
            "096770": "00384049",  # SK이노베이션
            "009150": "00142316",  # 삼성전기
            "034730": "00263014",  # SK
            "008770": "00134164",  # 호텔신라
            "000830": "00123368",  # 삼성물산
            "010950": "00140777",  # S-Oil
        }

        backup_corp_code = stock_to_corp_mapping.get(stock_code, "")
        if backup_corp_code:
            logger.info(f"✅ 백업 매핑 성공: {stock_code} → {backup_corp_code}")
            return backup_corp_code

        # ❌ 3단계: 모든 방법 실패
        logger.warning(
            f"❌ 법인고유번호 검색 실패: 종목코드({stock_code}), 회사명({company_name})"
        )
        return ""

    def _search_corp_code_by_company_name(
        self, company_name: str, stock_code: str = None
    ) -> str:
        """DART API를 사용해서 회사명으로 법인고유번호를 검색해요"""
        try:
            # 🧹 회사명 정제 (접두사 및 불필요한 문자 제거)
            cleaned_name = self._clean_company_name(company_name)
            logger.info(f"🧹 회사명 정제: '{company_name}' → '{cleaned_name}'")

            # DART API의 고유번호 검색 API 호출 (ZIP 압축 파일)
            url = "https://opendart.fss.or.kr/api/corpCode.xml"
            params = {
                "crtfc_key": self.dart_api_key,
            }

            response = self.session.get(url, params=params, timeout=30)

            if response.status_code == 200:
                # ZIP 파일 압축 해제
                import io
                import xml.etree.ElementTree as ET
                import zipfile

                # ZIP 내용을 메모리에서 압축 해제
                zip_content = io.BytesIO(response.content)
                with zipfile.ZipFile(zip_content, "r") as zip_file:
                    # CORPCODE.xml 파일 읽기
                    xml_filename = zip_file.namelist()[0]  # 첫 번째 파일
                    xml_content = zip_file.read(xml_filename).decode("utf-8")

                # XML 파싱
                root = ET.fromstring(xml_content)
                companies = []

                # 🔍 모든 회사 정보 파싱
                for company in root.findall(".//list"):
                    corp_code = company.findtext("corp_code", "")
                    corp_name = company.findtext("corp_name", "")
                    stock_code = company.findtext("stock_code", "")

                    if corp_code and corp_name:
                        companies.append(
                            {
                                "corp_code": corp_code,
                                "corp_name": corp_name.strip(),
                                "stock_code": stock_code.strip() if stock_code else "",
                            }
                        )

                logger.info(f"📋 DART에서 {len(companies)}개 기업 정보 로드 완료")

                # 🎯 매칭 점수 계산하여 최적 회사 찾기
                best_match = None
                best_score = 0

                # 1차: 정제된 이름으로 직접 매칭
                for company in companies:
                    score = self._calculate_match_score(
                        cleaned_name, company["corp_name"]
                    )

                    # 🚀 종목코드가 있는 경우 추가 보너스 점수 (정확한 매칭 보장)
                    if company.get("stock_code") == stock_code:
                        score += 1000  # 종목코드 완전 매칭시 최고 점수
                        logger.info(
                            f"🎯 종목코드 완전 매칭: {company['corp_name']} ({company['stock_code']})"
                        )

                    if score > best_score:
                        best_score = score
                        best_match = company

                # 2차: 대체 표기법 시도 (점수가 낮은 경우)
                if best_score < 90:
                    alternative_names = self._try_alternative_company_names(
                        cleaned_name
                    )
                    for alt_name in alternative_names:
                        logger.info(f"🔄 대체 표기법 시도: '{alt_name}'")
                        for company in companies:
                            score = self._calculate_match_score(
                                alt_name, company["corp_name"]
                            )

                            # 🚀 종목코드가 있는 경우 추가 보너스 점수
                            if company.get("stock_code") == stock_code:
                                score += 1000  # 종목코드 완전 매칭시 최고 점수
                                logger.info(
                                    f"🎯 종목코드 완전 매칭 (대체명): {company['corp_name']} ({company['stock_code']})"
                                )

                            if score > best_score:
                                best_score = score
                                best_match = company
                                logger.info(
                                    f"✅ 대체 표기법 매칭 성공: {alt_name} → {company['corp_name']} (점수: {score})"
                                )

                if best_match and best_score >= 70:  # 최소 70% 매칭
                    logger.info(
                        f"🎯 최고 매칭: {best_match['corp_name']} (점수: {best_score})"
                    )
                    return best_match["corp_code"]
                else:
                    logger.warning(f"⚠️ 매칭 점수 부족: 최고 점수 {best_score} < 70")
                    return ""

            else:
                logger.error(f"DART API 호출 실패: HTTP {response.status_code}")
                return ""

        except Exception as e:
            logger.error(f"DART 회사명 검색 중 오류: {e}")
            return ""

    def _clean_company_name(self, company_name: str) -> str:
        """회사명에서 불필요한 접두사와 문자를 제거해요"""
        import re

        # 원본 보존
        cleaned = company_name.strip()

        # 🧹 1단계: 숫자+점+공백 접두사 제거 (예: "1. 삼성생명" → "삼성생명")
        cleaned = re.sub(r"^\d+\.\s*", "", cleaned)

        # 🧹 2단계: 괄호와 내용 제거 (예: "삼성생명(주)" → "삼성생명")
        cleaned = re.sub(r"\([^)]*\)", "", cleaned)

        # 🧹 3단계: 다양한 회사 표기 정리
        # "㈜" → "주식회사"로 정규화 (하지만 검색시에는 둘 다 시도)

        # 🧹 4단계: 여러 공백을 하나로 합치기
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        logger.debug(f"🧹 회사명 정제: '{company_name}' → '{cleaned}'")
        return cleaned

    def _try_alternative_company_names(self, company_name: str) -> List[str]:
        """다양한 대체 표기법을 생성해요"""
        alternatives = []

        # 원본 추가
        alternatives.append(company_name)

        # 🔄 "주식회사" 관련 변형
        if "주식회사" in company_name:
            # "주식회사 ABC" → "ABC"
            alternatives.append(company_name.replace("주식회사", "").strip())
            # "주식회사 ABC" → "㈜ABC"
            alternatives.append(company_name.replace("주식회사", "㈜"))
        else:
            # "ABC" → "주식회사 ABC"
            alternatives.append(f"주식회사 {company_name}")
            # "ABC" → "㈜ABC"
            alternatives.append(f"㈜{company_name}")

        # 🔄 특별한 케이스들
        special_cases = {
            "삼성생명": [
                "삼성생명보험",
                "삼성생명보험주식회사",
                "주식회사 삼성생명보험",
            ],
            "삼성전자": ["삼성전자주식회사", "주식회사 삼성전자"],
            "LG전자": ["LG전자주식회사", "주식회사 LG전자"],
            "SK하이닉스": ["SK하이닉스주식회사", "에스케이하이닉스"],
        }

        if company_name in special_cases:
            alternatives.extend(special_cases[company_name])

        # 중복 제거하면서 순서 보존
        seen = set()
        unique_alternatives = []
        for alt in alternatives:
            if alt not in seen:
                seen.add(alt)
                unique_alternatives.append(alt)

        logger.debug(f"🔄 대체 표기법: {unique_alternatives}")
        return unique_alternatives

    def _calculate_match_score(self, target: str, corp: str) -> int:
        """회사명 매칭 점수를 계산해요 (높을수록 더 정확한 매치)"""
        score = 0

        # 🎯 1단계: 정확한 일치 (최고점)
        if target == corp:
            score += 100

        # 🎯 2단계: 완전히 포함되는 경우
        elif target in corp:
            # 정확한 부분 문자열인지 확인 (예: "삼성생명"이 "삼성생명보험"에 포함)
            if corp.startswith(target) or corp.endswith(target):
                score += 90
            else:
                score += 70

        elif corp in target:
            score += 60

        # 🎯 3단계: 키워드 기반 매칭
        target_keywords = target.split()
        corp_keywords = corp.split()

        # 공통 키워드 개수에 따른 점수
        common_keywords = set(target_keywords) & set(corp_keywords)
        if common_keywords:
            score += len(common_keywords) * 20

        return score

    def _is_korean_stock(self, stock_code: str) -> bool:
        """한국 주식인지 확인해요 (6자리 숫자면 한국 주식)"""
        if not stock_code:  # None 체크 추가
            return False
        return len(stock_code) == 6 and stock_code.isdigit()

    def _get_fallback_company_info(self, stock_code: str) -> Dict[str, Any]:
        """DART API 실패시 폴백 데이터"""
        return {
            "corp_name": f"종목코드_{stock_code}",
            "corp_code": "정보없음",
            "business_summary": "DART API 연결 실패",
            "established_date": "정보없음",
            "listing_date": "정보없음",
            "ceo_name": "정보없음",
            "address": "정보없음",
        }

    def _get_fallback_financial_data(self) -> Dict[str, Any]:
        """DART API 실패시 폴백 재무데이터"""
        return {
            "revenue": 0,
            "operating_profit": 0,
            "net_income": 0,
            "total_assets": 0,
            "total_liabilities": 0,
            "total_equity": 0,
            "cash_and_equivalents": 0,
            "data_source": "fallback_no_dart_connection",
            "note": "DART API 연결 실패로 기본값 사용",
        }

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

    def get_technical_analysis_data(
        self, stock_code: str, period: str = "1y"
    ) -> Dict[str, Any]:
        """
        🎯 기술적 분석을 위한 상세 주가 데이터와 계산된 지표들을 제공합니다.

        이 함수는 기술적 분석가가 실제 수치 기반의 구체적인 분석을 할 수 있도록
        1년치 일일 거래 데이터와 모든 주요 기술적 지표를 계산해서 제공해요.

        Args:
            stock_code: 종목코드 (예: "005930" 또는 "AAPL")
            period: 데이터 수집 기간 (기본값: "1y")

        Returns:
            Dict: 기술적 분석용 완전한 데이터셋
        """
        logger.info(f"📊 {stock_code} 기술적 분석용 데이터 수집 및 지표 계산 시작...")

        try:
            # 한국 주식과 해외 주식 구분해서 티커 설정
            if self._is_korean_stock(stock_code):
                ticker_symbol = f"{stock_code}.KS"
                if stock_code.startswith(("0", "1", "2")):
                    # KOSPI
                    ticker_symbol = f"{stock_code}.KS"
                else:
                    # KOSDAQ
                    ticker_symbol = f"{stock_code}.KQ"
            else:
                ticker_symbol = stock_code

            # yfinance로 상세 데이터 수집
            ticker = yf.Ticker(ticker_symbol)

            # 📈 1년치 일일 데이터 수집 (OHLCV)
            hist_data = ticker.history(period=period)

            if hist_data.empty:
                logger.warning(f"⚠️ {stock_code} 주가 데이터를 찾을 수 없습니다")
                return {"success": False, "error": "주가 데이터 없음"}

            logger.info(f"✅ {len(hist_data)}일치 주가 데이터 수집 완료")

            # 🧮 기술적 지표 계산
            technical_indicators = self._calculate_technical_indicators(hist_data)

            # 📊 지지/저항선 계산
            support_resistance = self._calculate_support_resistance(hist_data)

            # 🎯 매매 신호 분석
            trading_signals = self._analyze_trading_signals(
                hist_data, technical_indicators
            )

            # 📈 차트 패턴 분석
            chart_patterns = self._analyze_chart_patterns(hist_data)

            # 현재 시점의 주요 값들
            current_price = float(hist_data["Close"].iloc[-1])
            current_volume = int(hist_data["Volume"].iloc[-1])

            return {
                "success": True,
                "stock_code": stock_code,
                "ticker_symbol": ticker_symbol,
                "data_period": period,
                "total_days": len(hist_data),
                "last_update": hist_data.index[-1].strftime("%Y-%m-%d"),
                # 🎯 현재 시점 핵심 정보
                "current_snapshot": {
                    "price": current_price,
                    "volume": current_volume,
                    "date": hist_data.index[-1].strftime("%Y-%m-%d"),
                },
                # 📊 계산된 기술적 지표들 (실제 값!)
                "technical_indicators": technical_indicators,
                # 🎯 지지/저항선
                "support_resistance": support_resistance,
                # 📈 매매 신호
                "trading_signals": trading_signals,
                # 📊 차트 패턴
                "chart_patterns": chart_patterns,
                # 📈 원본 데이터 (필요시 추가 분석용)
                "raw_data_summary": {
                    "start_date": hist_data.index[0].strftime("%Y-%m-%d"),
                    "end_date": hist_data.index[-1].strftime("%Y-%m-%d"),
                    "price_range": {
                        "high": float(hist_data["High"].max()),
                        "low": float(hist_data["Low"].min()),
                        "volatility": float(
                            hist_data["Close"].pct_change().std() * 100
                        ),
                    },
                },
            }

        except Exception as e:
            logger.error(f"❌ 기술적 분석 데이터 수집 실패: {e}")
            return {"success": False, "error": str(e)}

    def _calculate_technical_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        📊 주요 기술적 지표들을 실제로 계산합니다.

        모든 지표의 현재 값과 최근 추세를 제공해요!
        """
        try:
            indicators = {}

            # 🔢 이동평균선 계산 (5일, 20일, 60일, 120일, 200일)
            indicators["moving_averages"] = {
                "MA_5": (
                    float(df["Close"].rolling(window=5).mean().iloc[-1])
                    if len(df) >= 5
                    else None
                ),
                "MA_20": (
                    float(df["Close"].rolling(window=20).mean().iloc[-1])
                    if len(df) >= 20
                    else None
                ),
                "MA_60": (
                    float(df["Close"].rolling(window=60).mean().iloc[-1])
                    if len(df) >= 60
                    else None
                ),
                "MA_120": (
                    float(df["Close"].rolling(window=120).mean().iloc[-1])
                    if len(df) >= 120
                    else None
                ),
                "MA_200": (
                    float(df["Close"].rolling(window=200).mean().iloc[-1])
                    if len(df) >= 200
                    else None
                ),
            }

            # 📈 RSI 계산 (14일)
            indicators["RSI"] = self._calculate_rsi(df["Close"], period=14)

            # 📊 MACD 계산 (12, 26, 9)
            indicators["MACD"] = self._calculate_macd(df["Close"])

            # 📈 볼린저 밴드 계산 (20일, 2표준편차)
            indicators["bollinger_bands"] = self._calculate_bollinger_bands(df["Close"])

            # 📊 스토캐스틱 계산 (14, 3, 3)
            indicators["stochastic"] = self._calculate_stochastic(df)

            # 📈 Williams %R 계산 (14일)
            indicators["williams_r"] = self._calculate_williams_r(df)

            # 📊 거래량 지표
            indicators["volume_indicators"] = {
                "OBV": self._calculate_obv(df),
                "volume_MA_20": (
                    float(df["Volume"].rolling(window=20).mean().iloc[-1])
                    if len(df) >= 20
                    else None
                ),
                "volume_ratio": (
                    float(
                        df["Volume"].iloc[-1]
                        / df["Volume"].rolling(window=20).mean().iloc[-1]
                    )
                    if len(df) >= 20
                    else None
                ),
            }

            logger.info("✅ 모든 기술적 지표 계산 완료")
            return indicators

        except Exception as e:
            logger.error(f"❌ 기술적 지표 계산 실패: {e}")
            return {}

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> Dict[str, float]:
        """RSI(상대강도지수) 계산 - 실제 수치 제공!"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

            current_rsi = float(rsi.iloc[-1])

            # RSI 해석
            if current_rsi >= 70:
                interpretation = "과매수"
                signal = "매도 고려"
            elif current_rsi <= 30:
                interpretation = "과매도"
                signal = "매수 고려"
            else:
                interpretation = "중립"
                signal = "관망"

            return {
                "current_value": current_rsi,
                "interpretation": interpretation,
                "signal": signal,
                "period": period,
            }
        except Exception as e:
            logger.error(f"RSI 계산 실패: {e}")
            return {"current_value": None, "interpretation": "계산 실패"}

    def _calculate_macd(
        self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Dict[str, Any]:
        """MACD 계산 - 실제 수치와 신호 제공!"""
        try:
            # EMA 계산
            ema_fast = prices.ewm(span=fast).mean()
            ema_slow = prices.ewm(span=slow).mean()

            # MACD 라인
            macd_line = ema_fast - ema_slow

            # 시그널 라인
            signal_line = macd_line.ewm(span=signal).mean()

            # 히스토그램
            histogram = macd_line - signal_line

            # 현재 값들
            current_macd = float(macd_line.iloc[-1])
            current_signal = float(signal_line.iloc[-1])
            current_histogram = float(histogram.iloc[-1])

            # 매매 신호 판단
            if current_macd > current_signal and histogram.iloc[-2] <= 0:
                signal_interpretation = "매수 신호 (상향 돌파)"
            elif current_macd < current_signal and histogram.iloc[-2] >= 0:
                signal_interpretation = "매도 신호 (하향 돌파)"
            elif current_macd > current_signal:
                signal_interpretation = "상승 추세 지속"
            else:
                signal_interpretation = "하락 추세 지속"

            return {
                "MACD_line": current_macd,
                "signal_line": current_signal,
                "histogram": current_histogram,
                "signal_interpretation": signal_interpretation,
                "parameters": f"({fast}, {slow}, {signal})",
            }
        except Exception as e:
            logger.error(f"MACD 계산 실패: {e}")
            return {"MACD_line": None, "signal_interpretation": "계산 실패"}

    def _calculate_bollinger_bands(
        self, prices: pd.Series, period: int = 20, std_dev: int = 2
    ) -> Dict[str, Any]:
        """볼린저 밴드 계산 - 실제 수치와 위치 분석!"""
        try:
            # 중간선 (20일 이동평균)
            middle_band = prices.rolling(window=period).mean()

            # 표준편차
            std = prices.rolling(window=period).std()

            # 상단/하단 밴드
            upper_band = middle_band + (std * std_dev)
            lower_band = middle_band - (std * std_dev)

            # 현재 값들
            current_price = float(prices.iloc[-1])
            current_upper = float(upper_band.iloc[-1])
            current_middle = float(middle_band.iloc[-1])
            current_lower = float(lower_band.iloc[-1])

            # 밴드 폭 (변동성 지표)
            band_width = ((current_upper - current_lower) / current_middle) * 100

            # 현재 위치 분석
            if current_price >= current_upper:
                position = "상단 밴드 근처 (과매수 가능)"
                signal = "매도 고려"
            elif current_price <= current_lower:
                position = "하단 밴드 근처 (과매도 가능)"
                signal = "매수 고려"
            else:
                position = "밴드 내부 (정상 범위)"
                signal = "관망"

            return {
                "upper_band": current_upper,
                "middle_band": current_middle,
                "lower_band": current_lower,
                "current_price": current_price,
                "band_width_percent": band_width,
                "position_analysis": position,
                "signal": signal,
                "parameters": f"({period}일, {std_dev}σ)",
            }
        except Exception as e:
            logger.error(f"볼린저 밴드 계산 실패: {e}")
            return {"upper_band": None, "position_analysis": "계산 실패"}

    def _calculate_stochastic(
        self, df: pd.DataFrame, k_period: int = 14, d_period: int = 3
    ) -> Dict[str, Any]:
        """스토캐스틱 오실레이터 계산"""
        try:
            # %K 계산
            lowest_low = df["Low"].rolling(window=k_period).min()
            highest_high = df["High"].rolling(window=k_period).max()
            k_percent = 100 * ((df["Close"] - lowest_low) / (highest_high - lowest_low))

            # %D 계산 (smoothed %K)
            d_percent = k_percent.rolling(window=d_period).mean()

            current_k = float(k_percent.iloc[-1])
            current_d = float(d_percent.iloc[-1])

            # 신호 해석
            if current_k >= 80 and current_d >= 80:
                interpretation = "과매수"
                signal = "매도 고려"
            elif current_k <= 20 and current_d <= 20:
                interpretation = "과매도"
                signal = "매수 고려"
            elif current_k > current_d:
                interpretation = "상승 모멘텀"
                signal = "매수 신호"
            else:
                interpretation = "하락 모멘텀"
                signal = "매도 신호"

            return {
                "K_percent": current_k,
                "D_percent": current_d,
                "interpretation": interpretation,
                "signal": signal,
                "parameters": f"({k_period}, {d_period})",
            }
        except Exception as e:
            logger.error(f"스토캐스틱 계산 실패: {e}")
            return {"K_percent": None, "interpretation": "계산 실패"}

    def _calculate_williams_r(
        self, df: pd.DataFrame, period: int = 14
    ) -> Dict[str, Any]:
        """Williams %R 계산"""
        try:
            highest_high = df["High"].rolling(window=period).max()
            lowest_low = df["Low"].rolling(window=period).min()

            williams_r = -100 * (
                (highest_high - df["Close"]) / (highest_high - lowest_low)
            )
            current_wr = float(williams_r.iloc[-1])

            # 신호 해석
            if current_wr >= -20:
                interpretation = "과매수"
                signal = "매도 고려"
            elif current_wr <= -80:
                interpretation = "과매도"
                signal = "매수 고려"
            else:
                interpretation = "중립"
                signal = "관망"

            return {
                "current_value": current_wr,
                "interpretation": interpretation,
                "signal": signal,
                "period": period,
            }
        except Exception as e:
            logger.error(f"Williams %R 계산 실패: {e}")
            return {"current_value": None, "interpretation": "계산 실패"}

    def _calculate_obv(self, df: pd.DataFrame) -> Dict[str, Any]:
        """OBV (On Balance Volume) 계산"""
        try:
            obv = []
            obv_value = 0

            for i in range(len(df)):
                if i == 0:
                    obv.append(df["Volume"].iloc[i])
                    obv_value = df["Volume"].iloc[i]
                else:
                    if df["Close"].iloc[i] > df["Close"].iloc[i - 1]:
                        obv_value += df["Volume"].iloc[i]
                    elif df["Close"].iloc[i] < df["Close"].iloc[i - 1]:
                        obv_value -= df["Volume"].iloc[i]
                    # 가격이 같으면 OBV 변화 없음
                    obv.append(obv_value)

            current_obv = obv[-1]

            # OBV 추세 분석 (최근 20일)
            if len(obv) >= 20:
                recent_obv_trend = obv[-1] - obv[-20]
                if recent_obv_trend > 0:
                    trend = "상승 (매수세 우세)"
                elif recent_obv_trend < 0:
                    trend = "하락 (매도세 우세)"
                else:
                    trend = "횡보 (균형)"
            else:
                trend = "데이터 부족"

            return {
                "current_value": int(current_obv),
                "trend_analysis": trend,
                "description": "거래량 누적 지표",
            }
        except Exception as e:
            logger.error(f"OBV 계산 실패: {e}")
            return {"current_value": None, "trend_analysis": "계산 실패"}

    def _calculate_support_resistance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """지지선과 저항선 자동 계산"""
        try:
            # 최근 3개월 데이터로 지지/저항선 계산
            recent_data = df.tail(90) if len(df) >= 90 else df

            # 고점과 저점 찾기
            highs = recent_data["High"]
            lows = recent_data["Low"]

            # 저항선 후보 (상위 고점들)
            resistance_candidates = []
            for i in range(2, len(highs) - 2):
                if (
                    highs.iloc[i] > highs.iloc[i - 1]
                    and highs.iloc[i] > highs.iloc[i - 2]
                    and highs.iloc[i] > highs.iloc[i + 1]
                    and highs.iloc[i] > highs.iloc[i + 2]
                ):
                    resistance_candidates.append(float(highs.iloc[i]))

            # 지지선 후보 (하위 저점들)
            support_candidates = []
            for i in range(2, len(lows) - 2):
                if (
                    lows.iloc[i] < lows.iloc[i - 1]
                    and lows.iloc[i] < lows.iloc[i - 2]
                    and lows.iloc[i] < lows.iloc[i + 1]
                    and lows.iloc[i] < lows.iloc[i + 2]
                ):
                    support_candidates.append(float(lows.iloc[i]))

            # 주요 지지/저항선 선별 (빈도 기준)
            current_price = float(df["Close"].iloc[-1])

            # 현재가 위의 저항선들
            resistance_levels = [r for r in resistance_candidates if r > current_price]
            resistance_levels = sorted(list(set(resistance_levels)))[:3]  # 상위 3개

            # 현재가 아래의 지지선들
            support_levels = [s for s in support_candidates if s < current_price]
            support_levels = sorted(list(set(support_levels)), reverse=True)[
                :3
            ]  # 상위 3개

            return {
                "support_levels": support_levels,
                "resistance_levels": resistance_levels,
                "current_price": current_price,
                "analysis_period": f"최근 {len(recent_data)}일",
                "nearest_support": support_levels[0] if support_levels else None,
                "nearest_resistance": (
                    resistance_levels[0] if resistance_levels else None
                ),
            }
        except Exception as e:
            logger.error(f"지지/저항선 계산 실패: {e}")
            return {"support_levels": [], "resistance_levels": []}

    def _analyze_trading_signals(
        self, df: pd.DataFrame, indicators: Dict
    ) -> Dict[str, Any]:
        """종합적인 매매 신호 분석"""
        try:
            signals = []
            signal_strength = 0  # -5 (강한 매도) ~ +5 (강한 매수)

            # RSI 신호
            rsi_data = indicators.get("RSI", {})
            if rsi_data.get("current_value"):
                rsi_val = rsi_data["current_value"]
                if rsi_val <= 30:
                    signals.append("RSI 과매도 (매수 신호)")
                    signal_strength += 2
                elif rsi_val >= 70:
                    signals.append("RSI 과매수 (매도 신호)")
                    signal_strength -= 2

            # MACD 신호
            macd_data = indicators.get("MACD", {})
            if "매수" in macd_data.get("signal_interpretation", ""):
                signals.append("MACD 매수 신호")
                signal_strength += 2
            elif "매도" in macd_data.get("signal_interpretation", ""):
                signals.append("MACD 매도 신호")
                signal_strength -= 2

            # 이동평균선 배열
            ma_data = indicators.get("moving_averages", {})
            current_price = float(df["Close"].iloc[-1])

            if ma_data.get("MA_20") and ma_data.get("MA_60"):
                if (
                    ma_data["MA_20"] > ma_data["MA_60"]
                    and current_price > ma_data["MA_20"]
                ):
                    signals.append("이동평균선 정배열 (상승 추세)")
                    signal_strength += 1
                elif (
                    ma_data["MA_20"] < ma_data["MA_60"]
                    and current_price < ma_data["MA_20"]
                ):
                    signals.append("이동평균선 역배열 (하락 추세)")
                    signal_strength -= 1

            # 볼린저 밴드 신호
            bb_data = indicators.get("bollinger_bands", {})
            if "매수" in bb_data.get("signal", ""):
                signals.append("볼린저 밴드 매수 신호")
                signal_strength += 1
            elif "매도" in bb_data.get("signal", ""):
                signals.append("볼린저 밴드 매도 신호")
                signal_strength -= 1

            # 종합 신호 판단
            if signal_strength >= 3:
                overall_signal = "강한 매수"
            elif signal_strength >= 1:
                overall_signal = "매수"
            elif signal_strength <= -3:
                overall_signal = "강한 매도"
            elif signal_strength <= -1:
                overall_signal = "매도"
            else:
                overall_signal = "중립"

            return {
                "individual_signals": signals,
                "signal_strength_score": signal_strength,
                "overall_signal": overall_signal,
                "confidence": min(abs(signal_strength) * 20, 100),  # 0-100%
                "recommendation": self._get_trading_recommendation(
                    overall_signal, signal_strength
                ),
            }
        except Exception as e:
            logger.error(f"매매 신호 분석 실패: {e}")
            return {"overall_signal": "분석 실패", "individual_signals": []}

    def _analyze_chart_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """기본적인 차트 패턴 분석"""
        try:
            patterns = []

            # 최근 20일 데이터로 패턴 분석
            recent_data = df.tail(20)
            closes = recent_data["Close"]

            # 상승/하락 추세 분석
            if len(closes) >= 10:
                first_half_avg = closes.iloc[:10].mean()
                second_half_avg = closes.iloc[10:].mean()

                change_percent = (
                    (second_half_avg - first_half_avg) / first_half_avg
                ) * 100

                if change_percent > 5:
                    patterns.append("상승 추세 (최근 20일)")
                elif change_percent < -5:
                    patterns.append("하락 추세 (최근 20일)")
                else:
                    patterns.append("횡보 추세 (최근 20일)")

            # 변동성 분석
            volatility = closes.pct_change().std() * 100
            if volatility > 3:
                patterns.append("고변동성")
            elif volatility < 1:
                patterns.append("저변동성")
            else:
                patterns.append("보통 변동성")

            return {
                "detected_patterns": patterns,
                "trend_analysis": (
                    f"최근 20일 변동률: {change_percent:.2f}%"
                    if "change_percent" in locals()
                    else "데이터 부족"
                ),
                "volatility_level": (
                    f"{volatility:.2f}%" if "volatility" in locals() else "계산 불가"
                ),
            }
        except Exception as e:
            logger.error(f"차트 패턴 분석 실패: {e}")
            return {"detected_patterns": [], "trend_analysis": "분석 실패"}

    def _get_trading_recommendation(self, signal: str, strength: int) -> str:
        """매매 신호에 따른 구체적인 추천사항"""
        recommendations = {
            "강한 매수": "적극적인 매수 포지션 고려. 단, 리스크 관리 필수.",
            "매수": "분할 매수 전략 권장. 점진적 포지션 확대.",
            "중립": "관망 또는 기존 포지션 유지. 추가 신호 대기.",
            "매도": "일부 매도 또는 수익 실현 고려.",
            "강한 매도": "포지션 정리 검토. 손절매 고려.",
        }
        return recommendations.get(signal, "신중한 접근 필요")
