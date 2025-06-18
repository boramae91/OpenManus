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

            # 🔍 디버깅: 전체 API 응답 로깅
            logger.info(
                f"📋 DART API 전체 응답: status={data.get('status')}, message={data.get('message')}"
            )
            logger.info(f"📊 DART API 주주 데이터 개수: {len(data.get('list', []))}")

            shareholders_data = []
            for item in data.get("list", []):
                # ✅ 올바른 DART API 필드명 사용
                hold_stock_co_raw = item.get("trmend_posesn_stock_co", "0")
                hold_stock_rt_raw = item.get("trmend_posesn_stock_qota_rt", "0")

                shareholder = {
                    "shareholder_name": item.get("nm", ""),
                    "relationship": item.get("relate", ""),
                    "shares_held": self._safe_int(hold_stock_co_raw),
                    "ownership_ratio": self._safe_float(hold_stock_rt_raw),
                    "report_date": item.get("stlm_dt", ""),  # 결산일자 사용
                }
                shareholders_data.append(shareholder)

            logger.info(f"✅ 주주정보 {len(shareholders_data)}명 수집 완료")

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
                    "current_year": self._safe_float(item.get("thstrm", "0")),  # 당기
                    "previous_year": self._safe_float(item.get("frmtrm", "0")),  # 전기
                    "two_years_ago": self._safe_float(item.get("lwfr", "0")),  # 전전기
                    "settlement_date": item.get("stlm_dt", ""),  # 결산일자
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
                    "change_type": item.get(
                        "isu_dcrs_mstvdv_amount", ""
                    ),  # 증자감자구분
                    "settlement_date": item.get("stlm_dt", ""),  # 결산일자
                    "note": (
                        "증자감자 실적이 없는 경우 '-' 표시"
                        if item.get("isu_dcrs_mstvdv_amount") == "-"
                        else ""
                    ),
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
                    "first_acquisition_date": item.get(
                        "frst_acqs_de", ""
                    ),  # 최초취득일자
                    "investment_purpose": item.get("invstmnt_purps", ""),  # 투자목적
                    "first_acquisition_amount": self._safe_int(
                        item.get("frst_acqs_amount", "0")
                    ),  # 최초취득금액
                    "ending_shares": self._safe_int(
                        item.get("trmend_blce_qy", "0")
                    ),  # 기말보유수량
                    "ownership_ratio": self._safe_float(
                        item.get("trmend_blce_qota_rt", "0")
                    ),  # 기말지분율
                    "book_value": self._safe_int(
                        item.get("trmend_blce_acntbk_amount", "0")
                    ),  # 기말장부금액
                    "settlement_date": item.get("stlm_dt", ""),  # 결산일자
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

    def get_corp_code_from_stock_code(
        self, stock_code: str, company_name: str = None
    ) -> Optional[str]:
        """
        종목코드와 회사명으로부터 DART 기업고유코드 조회 (동적 검색 지원)

        Args:
            stock_code: 6자리 종목코드 (예: "005930")
            company_name: 회사명 (동적 검색용, 선택사항)

        Returns:
            str: 8자리 기업고유코드 또는 None
        """
        if not self.is_available():
            return None

        try:
            # 🚀 1단계: 회사명이 있으면 DART API로 동적 검색 (최우선!)
            if company_name:
                logger.info(
                    f"🔍 Enhanced DART: 회사명 '{company_name}'으로 동적 검색 시도..."
                )
                corp_code = self._search_corp_code_by_company_name(company_name)
                if corp_code:
                    logger.info(
                        f"✅ Enhanced DART 동적 검색 성공: {company_name} → {corp_code}"
                    )
                    return corp_code
                else:
                    logger.warning(
                        f"⚠️ Enhanced DART 회사명 '{company_name}' 동적 검색 실패"
                    )

            # 🗂️ 2단계: 백업용 하드코딩 매핑 테이블 (주요 종목만)
            logger.info(
                f"📋 Enhanced DART: 종목코드 {stock_code} 백업 매핑 테이블 검색..."
            )
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
                "032830": "00126256",  # 삼성생명 (추가)
                "272210": "00356535",  # 한화시스템 (추가)
                "012450": "00178253",  # 한화에어로스페이스 (추가)
            }

            backup_corp_code = stock_to_corp_mapping.get(stock_code)
            if backup_corp_code:
                logger.info(
                    f"✅ Enhanced DART 백업 매핑 성공: {stock_code} → {backup_corp_code}"
                )
                return backup_corp_code

            # ❌ 3단계: 모든 방법 실패
            logger.warning(
                f"❌ Enhanced DART 법인고유번호 검색 실패: 종목코드({stock_code}), 회사명({company_name})"
            )
            return None

        except Exception as e:
            logger.error(f"Enhanced DART 종목코드 변환 실패: {e}")
            return None

    def _search_corp_code_by_company_name(self, company_name: str) -> Optional[str]:
        """DART API를 사용해서 회사명으로 법인고유번호를 검색해요 (Enhanced 버전)"""
        try:
            # 🧹 회사명 정제 (접두사 및 불필요한 문자 제거)
            cleaned_name = self._clean_company_name(company_name)
            logger.info(
                f"🧹 Enhanced DART 회사명 정제: '{company_name}' → '{cleaned_name}'"
            )

            # DART API의 고유번호 검색 API 호출 (ZIP 압축 파일)
            url = "https://opendart.fss.or.kr/api/corpCode.xml"
            params = {
                "crtfc_key": self.dart_api_key,
            }

            response = requests.get(url, params=params, timeout=30)

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

                logger.info(
                    f"📋 Enhanced DART에서 {len(companies)}개 기업 정보 로드 완료"
                )

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
                        logger.info(f"🔄 Enhanced DART 대체 표기법 시도: '{alt_name}'")
                        for company in companies:
                            score = self._calculate_match_score(
                                alt_name, company["corp_name"]
                            )
                            if score > best_score:
                                best_score = score
                                best_match = company
                                logger.info(
                                    f"✅ Enhanced DART 대체 표기법 매칭 성공: {alt_name} → {company['corp_name']} (점수: {score})"
                                )

                if best_match and best_score >= 70:  # 최소 70% 매칭
                    logger.info(
                        f"🎯 Enhanced DART 최고 매칭: {best_match['corp_name']} (점수: {best_score})"
                    )
                    return best_match["corp_code"]
                else:
                    logger.warning(
                        f"⚠️ Enhanced DART 매칭 점수 부족: 최고 점수 {best_score} < 70"
                    )
                    return None

            else:
                logger.error(
                    f"Enhanced DART API 호출 실패: HTTP {response.status_code}"
                )
                return None

        except Exception as e:
            logger.error(f"Enhanced DART 회사명 검색 중 오류: {e}")
            return None

    def _clean_company_name(self, company_name: str) -> str:
        """회사명에서 불필요한 접두사와 문자를 제거해요 (Enhanced 버전)"""
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

        logger.debug(f"🧹 Enhanced DART 회사명 정제: '{company_name}' → '{cleaned}'")
        return cleaned

    def _try_alternative_company_names(self, company_name: str) -> List[str]:
        """다양한 대체 표기법을 생성해요 (Enhanced 버전)"""
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
            "한화에어로스페이스": [
                "한화에어로스페이스주식회사",
                "주식회사 한화에어로스페이스",
            ],
            "한화시스템": ["한화시스템주식회사", "주식회사 한화시스템"],
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

        logger.debug(f"🔄 Enhanced DART 대체 표기법: {unique_alternatives}")
        return unique_alternatives

    def _calculate_match_score(self, target: str, corp: str) -> int:
        """회사명 매칭 점수를 계산해요 (Enhanced 버전)"""
        score = 0

        # 🎯 1단계: 정확한 일치 (최고점)
        if target == corp:
            score += 100

        # 🎯 2단계: 완전히 포함되는 경우
        elif target in corp:
            # 정확한 부분 문자열인지 확인 (예: "한화에어로스페이스"가 "한화에어로스페이스주식회사"에 포함)
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

    def get_comprehensive_company_analysis(
        self, stock_code: str, company_name: str = None, bsns_year: str = None
    ) -> Dict[str, Any]:
        """
        종합 기업 분석 (모든 기능 통합) - 회사명 지원 추가

        Args:
            stock_code: 6자리 종목코드
            company_name: 회사명 (동적 검색용, 선택사항)
            bsns_year: 사업연도

        Returns:
            Dict: 종합 분석 결과
        """
        if not self.is_available():
            return {"success": False, "error": "DART API 키가 설정되지 않았습니다"}

        # 종목코드 + 회사명 → 기업고유코드 변환 (동적 검색 지원)
        corp_code = self.get_corp_code_from_stock_code(stock_code, company_name)
        if not corp_code:
            return {
                "success": False,
                "error": f"종목코드 {stock_code} ({company_name})에 대한 기업고유코드를 찾을 수 없습니다",
            }

        logger.info(
            f"🔍 Enhanced DART: {stock_code} ({company_name}) 종합 기업 분석 시작"
        )

        result = {
            "success": True,
            "stock_code": stock_code,
            "company_name": company_name,
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

            logger.info(
                f"✅ Enhanced DART: {stock_code} ({company_name}) 종합 기업 분석 완료"
            )
            return result

        except Exception as e:
            logger.error(f"❌ Enhanced DART 종합 기업 분석 실패: {e}")
            result["success"] = False
            result["error"] = str(e)
            return result
