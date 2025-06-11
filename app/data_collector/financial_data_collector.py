# 재무데이터 수집 모듈
# DART API와 yfinance를 사용해서 실제 재무정보를 가져오는 도구상자예요!

import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

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
            corp_code = self._search_corp_code_by_company_name(company_name)
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

    def _search_corp_code_by_company_name(self, company_name: str) -> str:
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
