# -*- coding: utf-8 -*-
"""
Enhanced DART API 재무데이터 수집기
실제 DART API를 활용한 한국 기업 상세 정보 수집 도구

주요 기능:
1. 상세한 재무정보 (단일회사 주요계정, 연결재무제표 등)
2. 기업 지배구조 정보 (임원, 주주, 보수 등)
3. 투자정보 (배당, 증자감자, 자기주식 등)
4. 실시간 공시 모니터링 (최신 공시, 중요 공시 등)
"""

import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests

from app.logger import logger


class EnhancedDartDataCollector:
    """
    DART API를 활용한 확장 재무데이터 수집기
    실제 DART 엔드포인트들을 호출해서 상세한 기업 정보를 수집해요!
    """

    def __init__(self, dart_api_key: Optional[str] = None):
        """
        Enhanced DART API 수집기 초기화

        Args:
            dart_api_key: DART API 키
        """
        self.dart_api_key = dart_api_key
        self.base_url = "https://opendart.fss.or.kr/api"
        self.api_delay = 0.1  # API 호출 간격 (초)

        # DART API 엔드포인트 정의
        self.endpoints = {
            # 재무정보
            "single_account": "/fnlttSinglAcnt.json",  # 단일회사 주요계정
            "multi_account": "/fnlttMultiAcnt.json",  # 다중회사 주요계정
            "company_info": "/company.json",  # 기업개황
            # 지배구조 정보
            "executives": "/exctvSttus.json",  # 임원현황
            "major_shareholders": "/hyslrSttus.json",  # 최대주주현황
            "director_compensation": "/rmunSttus.json",  # 이사보수현황
            "outside_directors": "/otcpSttus.json",  # 사외이사현황
            # 투자정보
            "dividends": "/alotMatter.json",  # 배당정보
            "capital_changes": "/irdsSttus.json",  # 증자감자현황
            "treasury_stock": "/tsstk.json",  # 자기주식현황
            "investments": "/otrCprInvstmntSttus.json",  # 타법인출자현황
            # 공시정보
            "disclosures": "/list.json",  # 공시검색
            "corp_code": "/corpCode.xml",  # 고유번호
        }

        logger.info("📊 Enhanced DART API 수집기가 초기화되었습니다")

    def is_available(self) -> bool:
        """DART API 사용 가능 여부 확인"""
        return self.dart_api_key is not None

    # ==================== 1️⃣ 상세한 재무정보 ====================

    def get_detailed_financial_data(
        self, corp_code: str, bsns_year: str = None
    ) -> Dict[str, Any]:
        """
        상세한 재무정보를 수집해요

        Args:
            corp_code: 기업 고유코드 (8자리)
            bsns_year: 사업연도 (기본값: 작년)

        Returns:
            Dict: 상세 재무정보
        """
        if not self.is_available():
            return {"success": False, "error": "DART API 키가 설정되지 않았습니다"}

        if not bsns_year:
            bsns_year = str(datetime.now().year - 1)

        logger.info(f"📊 {corp_code} 상세 재무정보 수집 시작 ({bsns_year}년)")

        try:
            result = {
                "success": True,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "collected_at": datetime.now().isoformat(),
            }

            # 단일회사 주요계정 (개별재무제표)
            single_accounts = self._get_single_company_accounts(corp_code, bsns_year)
            if single_accounts["success"]:
                result["individual_statements"] = single_accounts["data"]

            # 다중회사 주요계정 (연결재무제표)
            multi_accounts = self._get_multi_company_accounts(corp_code, bsns_year)
            if multi_accounts["success"]:
                result["consolidated_statements"] = multi_accounts["data"]

            # 분기별 실적 (최근 4분기)
            quarterly_data = self._get_quarterly_performance(corp_code, bsns_year)
            if quarterly_data["success"]:
                result["quarterly_performance"] = quarterly_data["data"]

            logger.info(f"✅ {corp_code} 상세 재무정보 수집 완료")
            return result

        except Exception as e:
            logger.error(f"❌ 상세 재무정보 수집 실패: {e}")
            return {"success": False, "error": str(e)}

    def _get_single_company_accounts(
        self, corp_code: str, bsns_year: str
    ) -> Dict[str, Any]:
        """단일회사 주요계정 조회 (개별재무제표)"""
        try:
            time.sleep(self.api_delay)

            params = {
                "crtfc_key": self.dart_api_key,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "reprt_code": "11011",  # 사업보고서
            }

            response = requests.get(
                self.base_url + self.endpoints["single_account"], params=params
            )

            if response.status_code != 200:
                return {"success": False, "error": f"HTTP 오류: {response.status_code}"}

            data = response.json()

            if data.get("status") != "000":
                return {"success": False, "error": f"API 오류: {data.get('message')}"}

            # 주요 계정과목 추출
            accounts = data.get("list", [])
            financial_data = self._parse_financial_statements(accounts)

            return {"success": True, "data": financial_data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_multi_company_accounts(
        self, corp_code: str, bsns_year: str
    ) -> Dict[str, Any]:
        """다중회사 주요계정 조회 (연결재무제표)"""
        try:
            time.sleep(self.api_delay)

            params = {
                "crtfc_key": self.dart_api_key,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "reprt_code": "11011",  # 사업보고서
            }

            response = requests.get(
                self.base_url + self.endpoints["multi_account"], params=params
            )

            if response.status_code != 200:
                return {"success": False, "error": f"HTTP 오류: {response.status_code}"}

            data = response.json()

            if data.get("status") != "000":
                return {"success": False, "error": f"API 오류: {data.get('message')}"}

            # 연결재무제표 정보 추출
            accounts = data.get("list", [])
            consolidated_data = self._parse_financial_statements(accounts)

            return {"success": True, "data": consolidated_data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_quarterly_performance(
        self, corp_code: str, bsns_year: str
    ) -> Dict[str, Any]:
        """분기별 실적 조회"""
        try:
            quarterly_data = []

            # 최근 4분기 데이터 수집
            quarters = [
                "11013",
                "11012",
                "11014",
                "11011",
            ]  # 1분기, 반기, 3분기, 사업보고서
            quarter_names = ["1분기", "반기", "3분기", "연간"]

            for quarter_code, quarter_name in zip(quarters, quarter_names):
                time.sleep(self.api_delay)

                params = {
                    "crtfc_key": self.dart_api_key,
                    "corp_code": corp_code,
                    "bsns_year": bsns_year,
                    "reprt_code": quarter_code,
                }

                response = requests.get(
                    self.base_url + self.endpoints["single_account"], params=params
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "000":
                        accounts = data.get("list", [])
                        quarter_financials = self._parse_financial_statements(accounts)
                        quarter_financials["period"] = quarter_name
                        quarterly_data.append(quarter_financials)

            return {"success": True, "data": quarterly_data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _parse_financial_statements(self, accounts: List[Dict]) -> Dict[str, Any]:
        """재무제표 데이터 파싱"""
        parsed_data = {
            "asset_info": {},  # 자산 정보
            "liability_info": {},  # 부채 정보
            "equity_info": {},  # 자본 정보
            "income_info": {},  # 손익 정보
        }

        # 주요 계정과목 매핑
        account_mapping = {
            # 자산
            "자산총계": "total_assets",
            "유동자산": "current_assets",
            "비유동자산": "non_current_assets",
            "현금및현금성자산": "cash_and_equivalents",
            # 부채
            "부채총계": "total_liabilities",
            "유동부채": "current_liabilities",
            "비유동부채": "non_current_liabilities",
            # 자본
            "자본총계": "total_equity",
            "자본금": "capital_stock",
            "이익잉여금": "retained_earnings",
            # 손익
            "매출액": "revenue",
            "영업이익": "operating_income",
            "당기순이익": "net_income",
            "영업비용": "operating_expenses",
        }

        for account in accounts:
            account_name = account.get("account_nm", "")
            current_amount = account.get("thstrm_amount", "0")

            # 숫자로 변환 (콤마 제거)
            try:
                amount = (
                    int(current_amount.replace(",", "")) if current_amount != "-" else 0
                )
            except:
                amount = 0

            # 계정과목별 분류
            if account_name in account_mapping:
                key = account_mapping[account_name]

                if "자산" in account_name:
                    parsed_data["asset_info"][key] = amount
                elif "부채" in account_name:
                    parsed_data["liability_info"][key] = amount
                elif "자본" in account_name:
                    parsed_data["equity_info"][key] = amount
                elif account_name in ["매출액", "영업이익", "당기순이익", "영업비용"]:
                    parsed_data["income_info"][key] = amount

        return parsed_data

    # ==================== 2️⃣ 기업 지배구조 정보 ====================

    def get_governance_info(
        self, corp_code: str, bsns_year: str = None
    ) -> Dict[str, Any]:
        """
        기업 지배구조 정보를 수집해요

        Args:
            corp_code: 기업 고유코드
            bsns_year: 사업연도

        Returns:
            Dict: 지배구조 정보
        """
        if not self.is_available():
            return {"success": False, "error": "DART API 키가 설정되지 않았습니다"}

        if not bsns_year:
            bsns_year = str(datetime.now().year - 1)

        logger.info(f"👥 {corp_code} 지배구조 정보 수집 시작")

        try:
            result = {
                "success": True,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "collected_at": datetime.now().isoformat(),
            }

            # 최대주주 현황
            shareholders = self._get_major_shareholders(corp_code, bsns_year)
            if shareholders["success"]:
                result["major_shareholders"] = shareholders["data"]

            # 임원 현황
            executives = self._get_executives_info(corp_code, bsns_year)
            if executives["success"]:
                result["executives"] = executives["data"]

            # 이사 보수 현황
            compensation = self._get_director_compensation(corp_code, bsns_year)
            if compensation["success"]:
                result["director_compensation"] = compensation["data"]

            # 사외이사 현황
            outside_directors = self._get_outside_directors(corp_code, bsns_year)
            if outside_directors["success"]:
                result["outside_directors"] = outside_directors["data"]

            logger.info(f"✅ {corp_code} 지배구조 정보 수집 완료")
            return result

        except Exception as e:
            logger.error(f"❌ 지배구조 정보 수집 실패: {e}")
            return {"success": False, "error": str(e)}

    def _get_major_shareholders(self, corp_code: str, bsns_year: str) -> Dict[str, Any]:
        """최대주주 현황 조회"""
        try:
            time.sleep(self.api_delay)

            params = {
                "crtfc_key": self.dart_api_key,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "reprt_code": "11011",
            }

            response = requests.get(
                self.base_url + self.endpoints["major_shareholders"], params=params
            )

            if response.status_code != 200:
                return {"success": False, "error": f"HTTP 오류: {response.status_code}"}

            data = response.json()

            if data.get("status") != "000":
                return {"success": False, "error": f"API 오류: {data.get('message')}"}

            shareholders_data = []
            for item in data.get("list", []):
                shareholder = {
                    "shareholder_name": item.get("nm", ""),
                    "relationship": item.get("relate", ""),
                    "shares_held": self._safe_int(item.get("hold_stock_co", "0")),
                    "ownership_ratio": self._safe_float(item.get("hold_stock_rt", "0")),
                    "report_date": item.get("trmend_dt", ""),
                }
                shareholders_data.append(shareholder)

            return {"success": True, "data": shareholders_data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_executives_info(self, corp_code: str, bsns_year: str) -> Dict[str, Any]:
        """임원 현황 조회"""
        try:
            time.sleep(self.api_delay)

            params = {
                "crtfc_key": self.dart_api_key,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "reprt_code": "11011",
            }

            response = requests.get(
                self.base_url + self.endpoints["executives"], params=params
            )

            if response.status_code != 200:
                return {"success": False, "error": f"HTTP 오류: {response.status_code}"}

            data = response.json()

            if data.get("status") != "000":
                return {"success": False, "error": f"API 오류: {data.get('message')}"}

            executives_data = []
            for item in data.get("list", []):
                executive = {
                    "name": item.get("nm", ""),
                    "position": item.get("sexdsgnm", ""),
                    "career": item.get("career", ""),
                    "main_career": item.get("main_career", ""),
                    "tenure": item.get("tenure", ""),
                }
                executives_data.append(executive)

            return {"success": True, "data": executives_data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_director_compensation(
        self, corp_code: str, bsns_year: str
    ) -> Dict[str, Any]:
        """이사 보수 현황 조회"""
        try:
            time.sleep(self.api_delay)

            params = {
                "crtfc_key": self.dart_api_key,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "reprt_code": "11011",
            }

            response = requests.get(
                self.base_url + self.endpoints["director_compensation"], params=params
            )

            if response.status_code != 200:
                return {"success": False, "error": f"HTTP 오류: {response.status_code}"}

            data = response.json()

            if data.get("status") != "000":
                return {"success": False, "error": f"API 오류: {data.get('message')}"}

            compensation_data = []
            for item in data.get("list", []):
                compensation = {
                    "classification": item.get("job", ""),
                    "number_of_people": self._safe_int(item.get("nmpr", "0")),
                    "total_compensation": self._safe_int(item.get("pymnt_totamt", "0")),
                    "average_compensation": self._safe_int(item.get("pymnt_avrg", "0")),
                }
                compensation_data.append(compensation)

            return {"success": True, "data": compensation_data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_outside_directors(self, corp_code: str, bsns_year: str) -> Dict[str, Any]:
        """사외이사 현황 조회"""
        try:
            time.sleep(self.api_delay)

            params = {
                "crtfc_key": self.dart_api_key,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "reprt_code": "11011",
            }

            response = requests.get(
                self.base_url + self.endpoints["outside_directors"], params=params
            )

            if response.status_code != 200:
                return {"success": False, "error": f"HTTP 오류: {response.status_code}"}

            data = response.json()

            if data.get("status") != "000":
                return {"success": False, "error": f"API 오류: {data.get('message')}"}

            directors_data = []
            for item in data.get("list", []):
                director = {
                    "name": item.get("nm", ""),
                    "appointment_date": item.get("apnt_dt", ""),
                    "tenure": item.get("tenure", ""),
                    "independence_criteria": item.get("indpnc_stat", ""),
                }
                directors_data.append(director)

            return {"success": True, "data": directors_data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # ==================== 3️⃣ 투자정보 ====================

    def get_investment_info(
        self, corp_code: str, bsns_year: str = None
    ) -> Dict[str, Any]:
        """
        투자 관련 정보를 수집해요

        Args:
            corp_code: 기업 고유코드
            bsns_year: 사업연도

        Returns:
            Dict: 투자정보
        """
        if not self.is_available():
            return {"success": False, "error": "DART API 키가 설정되지 않았습니다"}

        if not bsns_year:
            bsns_year = str(datetime.now().year - 1)

        logger.info(f"💰 {corp_code} 투자정보 수집 시작")

        try:
            result = {
                "success": True,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "collected_at": datetime.now().isoformat(),
            }

            # 배당 정보
            dividends = self._get_dividend_info(corp_code, bsns_year)
            if dividends["success"]:
                result["dividend_info"] = dividends["data"]

            # 증자감자 현황
            capital_changes = self._get_capital_changes(corp_code, bsns_year)
            if capital_changes["success"]:
                result["capital_changes"] = capital_changes["data"]

            # 자기주식 현황
            treasury_stock = self._get_treasury_stock(corp_code, bsns_year)
            if treasury_stock["success"]:
                result["treasury_stock"] = treasury_stock["data"]

            # 타법인 출자현황
            investments = self._get_investments(corp_code, bsns_year)
            if investments["success"]:
                result["other_investments"] = investments["data"]

            logger.info(f"✅ {corp_code} 투자정보 수집 완료")
            return result

        except Exception as e:
            logger.error(f"❌ 투자정보 수집 실패: {e}")
            return {"success": False, "error": str(e)}

    def _get_dividend_info(self, corp_code: str, bsns_year: str) -> Dict[str, Any]:
        """배당 정보 조회"""
        try:
            time.sleep(self.api_delay)

            params = {
                "crtfc_key": self.dart_api_key,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "reprt_code": "11011",
            }

            response = requests.get(
                self.base_url + self.endpoints["dividends"], params=params
            )

            if response.status_code != 200:
                return {"success": False, "error": f"HTTP 오류: {response.status_code}"}

            data = response.json()

            if data.get("status") != "000":
                return {"success": False, "error": f"API 오류: {data.get('message')}"}

            dividend_data = []
            for item in data.get("list", []):
                dividend = {
                    "dividend_classification": item.get("se", ""),
                    "dividend_per_share": self._safe_int(item.get("stock_knd", "0")),
                    "dividend_rate": self._safe_float(item.get("thstrm", "0")),
                    "record_date": item.get("record_date", ""),
                    "payment_date": item.get("payment_date", ""),
                }
                dividend_data.append(dividend)

            return {"success": True, "data": dividend_data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_capital_changes(self, corp_code: str, bsns_year: str) -> Dict[str, Any]:
        """증자감자 현황 조회"""
        try:
            time.sleep(self.api_delay)

            params = {
                "crtfc_key": self.dart_api_key,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "reprt_code": "11011",
            }

            response = requests.get(
                self.base_url + self.endpoints["capital_changes"], params=params
            )

            if response.status_code != 200:
                return {"success": False, "error": f"HTTP 오류: {response.status_code}"}

            data = response.json()

            if data.get("status") != "000":
                return {"success": False, "error": f"API 오류: {data.get('message')}"}

            capital_data = []
            for item in data.get("list", []):
                capital = {
                    "date": item.get("isu_dt", ""),
                    "type": item.get("isu_dcrs_de", ""),
                    "issued_shares": self._safe_int(item.get("isu_stock_co", "0")),
                    "issue_price": self._safe_int(item.get("isu_prc", "0")),
                    "issue_amount": self._safe_int(item.get("isu_amount", "0")),
                }
                capital_data.append(capital)

            return {"success": True, "data": capital_data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_treasury_stock(self, corp_code: str, bsns_year: str) -> Dict[str, Any]:
        """자기주식 현황 조회"""
        try:
            time.sleep(self.api_delay)

            params = {
                "crtfc_key": self.dart_api_key,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "reprt_code": "11011",
            }

            response = requests.get(
                self.base_url + self.endpoints["treasury_stock"], params=params
            )

            if response.status_code != 200:
                return {"success": False, "error": f"HTTP 오류: {response.status_code}"}

            data = response.json()

            if data.get("status") != "000":
                return {"success": False, "error": f"API 오류: {data.get('message')}"}

            treasury_data = []
            for item in data.get("list", []):
                treasury = {
                    "acquisition_date": item.get("acqs_dt", ""),
                    "acquisition_method": item.get("acqs_mth", ""),
                    "shares_acquired": self._safe_int(item.get("acqs_stock_co", "0")),
                    "acquisition_amount": self._safe_int(item.get("acqs_amount", "0")),
                    "disposal_method": item.get("dsps_mth", ""),
                }
                treasury_data.append(treasury)

            return {"success": True, "data": treasury_data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_investments(self, corp_code: str, bsns_year: str) -> Dict[str, Any]:
        """타법인 출자현황 조회"""
        try:
            time.sleep(self.api_delay)

            params = {
                "crtfc_key": self.dart_api_key,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "reprt_code": "11011",
            }

            response = requests.get(
                self.base_url + self.endpoints["investments"], params=params
            )

            if response.status_code != 200:
                return {"success": False, "error": f"HTTP 오류: {response.status_code}"}

            data = response.json()

            if data.get("status") != "000":
                return {"success": False, "error": f"API 오류: {data.get('message')}"}

            investment_data = []
            for item in data.get("list", []):
                investment = {
                    "company_name": item.get("inv_prm", ""),
                    "business_type": item.get("bsns", ""),
                    "investment_amount": self._safe_int(
                        item.get("invstmnt_amount", "0")
                    ),
                    "ownership_ratio": self._safe_float(item.get("hold_stock_rt", "0")),
                    "acquisition_date": item.get("acqs_dt", ""),
                }
                investment_data.append(investment)

            return {"success": True, "data": investment_data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # ==================== 4️⃣ 실시간 공시 모니터링 ====================

    def monitor_disclosures(
        self, corp_code: str = None, days: int = 7
    ) -> Dict[str, Any]:
        """
        실시간 공시 모니터링

        Args:
            corp_code: 기업 고유코드 (None이면 전체 공시)
            days: 조회 기간 (일)

        Returns:
            Dict: 공시 모니터링 결과
        """
        if not self.is_available():
            return {"success": False, "error": "DART API 키가 설정되지 않았습니다"}

        logger.info(f"📰 공시 모니터링 시작 (최근 {days}일)")

        try:
            result = {
                "success": True,
                "monitoring_period": f"최근 {days}일",
                "collected_at": datetime.now().isoformat(),
            }

            # 최근 공시 목록
            recent_disclosures = self._get_recent_disclosures(corp_code, days)
            if recent_disclosures["success"]:
                result["recent_disclosures"] = recent_disclosures["data"]

            # 중요 공시 알림
            important_notices = self._get_important_notices(corp_code, days)
            if important_notices["success"]:
                result["important_notices"] = important_notices["data"]

            # 정정공시 목록
            corrections = self._get_corrections(corp_code, days)
            if corrections["success"]:
                result["corrections"] = corrections["data"]

            logger.info(f"✅ 공시 모니터링 완료")
            return result

        except Exception as e:
            logger.error(f"❌ 공시 모니터링 실패: {e}")
            return {"success": False, "error": str(e)}

    def _get_recent_disclosures(self, corp_code: str, days: int) -> Dict[str, Any]:
        """최근 공시 목록 조회"""
        try:
            time.sleep(self.api_delay)

            # 날짜 범위 설정
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            params = {
                "crtfc_key": self.dart_api_key,
                "bgn_de": start_date.strftime("%Y%m%d"),
                "end_de": end_date.strftime("%Y%m%d"),
                "page_no": "1",
                "page_count": "100",
            }

            if corp_code:
                params["corp_code"] = corp_code

            response = requests.get(
                self.base_url + self.endpoints["disclosures"], params=params
            )

            if response.status_code != 200:
                return {"success": False, "error": f"HTTP 오류: {response.status_code}"}

            data = response.json()

            if data.get("status") != "000":
                return {"success": False, "error": f"API 오류: {data.get('message')}"}

            disclosure_data = []
            for item in data.get("list", []):
                disclosure = {
                    "corp_name": item.get("corp_name", ""),
                    "report_name": item.get("report_nm", ""),
                    "receipt_number": item.get("rcept_no", ""),
                    "receipt_date": item.get("rcept_dt", ""),
                    "submitter": item.get("flr_nm", ""),
                    "remarks": item.get("rm", ""),
                }
                disclosure_data.append(disclosure)

            return {"success": True, "data": disclosure_data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_important_notices(self, corp_code: str, days: int) -> Dict[str, Any]:
        """중요 공시 알림 (주요사항보고서, 공정공시 등)"""
        try:
            # 중요 공시 키워드
            important_keywords = [
                "주요사항보고서",
                "공정공시",
                "증자",
                "감자",
                "합병",
                "분할",
                "유상증자",
                "무상증자",
                "배당",
                "영업양도",
                "영업양수",
            ]

            recent_disclosures = self._get_recent_disclosures(corp_code, days)
            if not recent_disclosures["success"]:
                return recent_disclosures

            important_disclosures = []
            for disclosure in recent_disclosures["data"]:
                report_name = disclosure.get("report_name", "")

                # 중요 공시 필터링
                for keyword in important_keywords:
                    if keyword in report_name:
                        disclosure["importance_reason"] = f"'{keyword}' 관련 공시"
                        important_disclosures.append(disclosure)
                        break

            return {"success": True, "data": important_disclosures}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_corrections(self, corp_code: str, days: int) -> Dict[str, Any]:
        """정정공시 목록 조회"""
        try:
            recent_disclosures = self._get_recent_disclosures(corp_code, days)
            if not recent_disclosures["success"]:
                return recent_disclosures

            correction_keywords = ["정정", "첨부정정", "기재정정"]
            corrections = []

            for disclosure in recent_disclosures["data"]:
                report_name = disclosure.get("report_name", "")

                # 정정공시 필터링
                for keyword in correction_keywords:
                    if keyword in report_name:
                        disclosure["correction_type"] = keyword
                        corrections.append(disclosure)
                        break

            return {"success": True, "data": corrections}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # ==================== 유틸리티 함수 ====================

    def _safe_int(self, value: str) -> int:
        """안전한 정수 변환"""
        try:
            return int(value.replace(",", "")) if value and value != "-" else 0
        except:
            return 0

    def _safe_float(self, value: str) -> float:
        """안전한 실수 변환"""
        try:
            return float(value.replace(",", "")) if value and value != "-" else 0.0
        except:
            return 0.0

    def get_corp_code_from_stock_code(self, stock_code: str) -> Optional[str]:
        """
        종목코드로부터 DART 기업고유코드 조회

        Args:
            stock_code: 6자리 종목코드 (예: "005930")

        Returns:
            str: 8자리 기업고유코드 또는 None
        """
        if not self.is_available():
            return None

        try:
            # 간단한 매핑 테이블 (실제로는 DART 고유번호 API를 사용해야 함)
            stock_to_corp_mapping = {
                "005930": "00126380",  # 삼성전자
                "000660": "00164779",  # SK하이닉스
                "035420": "00401731",  # NAVER
                "035720": "00258801",  # 카카오
                "207940": "00356370",  # 삼성바이오로직스
                "006400": "00102148",  # 삼성SDI
                "051910": "00135199",  # LG화학
                "028260": "00344976",  # 삼성물산
                "066570": "00186136",  # LG전자
                "096770": "00173054",  # SK이노베이션
            }

            return stock_to_corp_mapping.get(stock_code)

        except Exception as e:
            logger.error(f"종목코드 변환 실패: {e}")
            return None

    def get_comprehensive_company_analysis(
        self, stock_code: str, bsns_year: str = None
    ) -> Dict[str, Any]:
        """
        종합 기업 분석 (모든 기능 통합)

        Args:
            stock_code: 6자리 종목코드
            bsns_year: 사업연도

        Returns:
            Dict: 종합 분석 결과
        """
        if not self.is_available():
            return {"success": False, "error": "DART API 키가 설정되지 않았습니다"}

        # 종목코드 → 기업고유코드 변환
        corp_code = self.get_corp_code_from_stock_code(stock_code)
        if not corp_code:
            return {
                "success": False,
                "error": f"종목코드 {stock_code}에 대한 기업고유코드를 찾을 수 없습니다",
            }

        logger.info(f"🔍 {stock_code} 종합 기업 분석 시작")

        result = {
            "success": True,
            "stock_code": stock_code,
            "corp_code": corp_code,
            "analysis_date": datetime.now().isoformat(),
        }

        try:
            # 1. 상세한 재무정보
            financial_data = self.get_detailed_financial_data(corp_code, bsns_year)
            if financial_data["success"]:
                result["financial_analysis"] = financial_data

            # 2. 기업 지배구조 정보
            governance_data = self.get_governance_info(corp_code, bsns_year)
            if governance_data["success"]:
                result["governance_analysis"] = governance_data

            # 3. 투자정보
            investment_data = self.get_investment_info(corp_code, bsns_year)
            if investment_data["success"]:
                result["investment_analysis"] = investment_data

            # 4. 최근 공시 모니터링 (최근 30일)
            disclosure_data = self.monitor_disclosures(corp_code, days=30)
            if disclosure_data["success"]:
                result["disclosure_monitoring"] = disclosure_data

            logger.info(f"✅ {stock_code} 종합 기업 분석 완료")
            return result

        except Exception as e:
            logger.error(f"❌ 종합 기업 분석 실패: {e}")
            result["success"] = False
            result["error"] = str(e)
            return result
