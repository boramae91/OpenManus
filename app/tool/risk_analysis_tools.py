# -*- coding: utf-8 -*-
"""
리스크 전문가 특화 도구 모음

이 파일은 재무, 시장, 운영, 산업, 규제 등 다양한 리스크를 초보자도 이해할 수 있게 분석해주는 도구들이에요.
각 함수와 로직에는 아주 쉬운 한국어 주석이 달려 있어요!
"""

from typing import Any, Dict, List

from app.logger import logger


class RiskAnalysisTools:
    """
    리스크 전문가를 위한 특화 도구
    여러 가지 위험(리스크)을 쉽게 분석할 수 있어요.
    """

    def __init__(self):
        # 도구가 처음 만들어질 때 한 번 실행돼요
        logger.info("⚠️ 리스크 분석 도구가 준비됐어요!")

    def analyze_financial_risk(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        # 재무 리스크(돈과 관련된 위험)를 분석해요
        # (예: 부채비율, 유동비율, 이자보상배율 등)
        try:
            logger.info("🔍 재무 리스크 분석 시작!")
            debt_ratio = financial_data.get("debt_ratio", 0)  # 부채비율
            current_ratio = financial_data.get("current_ratio", 0)  # 유동비율
            interest_coverage = financial_data.get(
                "interest_coverage", 0
            )  # 이자보상배율

            # 각각의 수치가 위험한지 해석해요
            debt_risk = self._interpret_debt_ratio(debt_ratio)
            liquidity_risk = self._interpret_current_ratio(current_ratio)
            interest_risk = self._interpret_interest_coverage(interest_coverage)

            # 전체적으로 종합해서 위험 수준을 알려줘요
            overall = self._overall([debt_risk, liquidity_risk, interest_risk])

            return {
                "success": True,
                "debt_ratio": debt_ratio,
                "current_ratio": current_ratio,
                "interest_coverage": interest_coverage,
                "debt_risk": debt_risk,
                "liquidity_risk": liquidity_risk,
                "interest_risk": interest_risk,
                "overall_financial_risk": overall,
            }
        except Exception as e:
            logger.error(f"❌ 재무 리스크 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    def analyze_market_risk(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        # 시장 리스크(주가, 환율, 금리 등 외부 환경의 위험)를 분석해요
        try:
            logger.info("🔍 시장 리스크 분석 시작!")
            volatility = market_data.get("volatility", 0)  # 주가 변동성
            exchange_rate = market_data.get("exchange_rate", 0)  # 환율
            interest_rate = market_data.get("interest_rate", 0)  # 금리

            volatility_risk = self._interpret_volatility(volatility)
            fx_risk = self._interpret_exchange_rate(exchange_rate)
            rate_risk = self._interpret_interest_rate(interest_rate)

            overall = self._overall([volatility_risk, fx_risk, rate_risk])

            return {
                "success": True,
                "volatility": volatility,
                "exchange_rate": exchange_rate,
                "interest_rate": interest_rate,
                "volatility_risk": volatility_risk,
                "fx_risk": fx_risk,
                "rate_risk": rate_risk,
                "overall_market_risk": overall,
            }
        except Exception as e:
            logger.error(f"❌ 시장 리스크 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    def analyze_operational_risk(
        self, operation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        # 운영 리스크(공급망, 인력, IT 등 회사 내부의 위험)를 분석해요
        try:
            logger.info("🔍 운영 리스크 분석 시작!")
            supply_chain = operation_data.get("supply_chain", "정상")
            workforce = operation_data.get("workforce", "안정")
            it_system = operation_data.get("it_system", "안정")

            supply_risk = self._interpret_supply_chain(supply_chain)
            workforce_risk = self._interpret_workforce(workforce)
            it_risk = self._interpret_it_system(it_system)

            overall = self._overall([supply_risk, workforce_risk, it_risk])

            return {
                "success": True,
                "supply_chain": supply_chain,
                "workforce": workforce,
                "it_system": it_system,
                "supply_risk": supply_risk,
                "workforce_risk": workforce_risk,
                "it_risk": it_risk,
                "overall_operational_risk": overall,
            }
        except Exception as e:
            logger.error(f"❌ 운영 리스크 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    def analyze_industry_risk(self, industry_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        산업 리스크 분석 함수
        Args:
            industry_data: 산업 데이터 (예: 경쟁강도, 진입장벽, 대체재 등)
        Returns:
            Dict: 산업 리스크 분석 결과
        """
        try:
            logger.info("🔍 산업 리스크 분석 시작...")
            competition = industry_data.get("competition", "중간")
            entry_barrier = industry_data.get("entry_barrier", "중간")
            substitutes = industry_data.get("substitutes", "중간")

            competition_risk = self._interpret_competition(competition)
            entry_risk = self._interpret_entry_barrier(entry_barrier)
            substitute_risk = self._interpret_substitutes(substitutes)

            result = {
                "success": True,
                "competition": competition,
                "entry_barrier": entry_barrier,
                "substitutes": substitutes,
                "competition_risk": competition_risk,
                "entry_risk": entry_risk,
                "substitute_risk": substitute_risk,
                "overall_industry_risk": self._assess_overall_industry_risk(
                    competition_risk, entry_risk, substitute_risk
                ),
            }
            logger.info("✅ 산업 리스크 분석 완료!")
            return result
        except Exception as e:
            logger.error(f"❌ 산업 리스크 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    def analyze_regulatory_risk(
        self, regulatory_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        규제 리스크 분석 함수
        Args:
            regulatory_data: 규제 데이터 (예: 환경, 세금, 법률 등)
        Returns:
            Dict: 규제 리스크 분석 결과
        """
        try:
            logger.info("🔍 규제 리스크 분석 시작...")
            environment = regulatory_data.get("environment", "보통")
            tax = regulatory_data.get("tax", "보통")
            law = regulatory_data.get("law", "보통")

            env_risk = self._interpret_environment(environment)
            tax_risk = self._interpret_tax(tax)
            law_risk = self._interpret_law(law)

            result = {
                "success": True,
                "environment": environment,
                "tax": tax,
                "law": law,
                "env_risk": env_risk,
                "tax_risk": tax_risk,
                "law_risk": law_risk,
                "overall_regulatory_risk": self._assess_overall_regulatory_risk(
                    env_risk, tax_risk, law_risk
                ),
            }
            logger.info("✅ 규제 리스크 분석 완료!")
            return result
        except Exception as e:
            logger.error(f"❌ 규제 리스크 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    # 아래는 각 리스크별 해석 함수들이에요
    def _interpret_debt_ratio(self, ratio: float) -> str:
        # 부채비율이 높으면 위험해요
        if ratio > 200:
            return "위험"
        elif ratio > 100:
            return "주의"
        else:
            return "안정"

    def _interpret_current_ratio(self, ratio: float) -> str:
        # 유동비율이 낮으면 위험해요
        if ratio < 100:
            return "위험"
        elif ratio < 150:
            return "주의"
        else:
            return "안정"

    def _interpret_interest_coverage(self, coverage: float) -> str:
        # 이자보상배율이 낮으면 위험해요
        if coverage < 1:
            return "위험"
        elif coverage < 3:
            return "주의"
        else:
            return "안정"

    def _interpret_volatility(self, vol: float) -> str:
        # 변동성이 크면 위험해요
        if vol > 30:
            return "위험"
        elif vol > 15:
            return "주의"
        else:
            return "안정"

    def _interpret_exchange_rate(self, fx: float) -> str:
        # 환율이 높으면 위험해요
        if fx > 1300:
            return "위험"
        elif fx > 1200:
            return "주의"
        else:
            return "안정"

    def _interpret_interest_rate(self, rate: float) -> str:
        # 금리가 높으면 위험해요
        if rate > 5:
            return "위험"
        elif rate > 3:
            return "주의"
        else:
            return "안정"

    def _interpret_supply_chain(self, status: str) -> str:
        # 공급망에 문제가 있으면 위험해요
        if status == "불안정":
            return "위험"
        elif status == "주의":
            return "주의"
        else:
            return "안정"

    def _interpret_workforce(self, status: str) -> str:
        # 인력 상황이 불안정하면 위험해요
        if status == "이탈":
            return "위험"
        elif status == "주의":
            return "주의"
        else:
            return "안정"

    def _interpret_it_system(self, status: str) -> str:
        # IT 시스템에 장애가 있으면 위험해요
        if status == "장애":
            return "위험"
        elif status == "주의":
            return "주의"
        else:
            return "안정"

    def _overall(self, risks: list) -> str:
        # 위험이 하나라도 있으면 '고위험', 주의가 있으면 '중간위험', 아니면 '저위험'으로 알려줘요
        if "위험" in risks:
            return "고위험"
        elif "주의" in risks:
            return "중간위험"
        else:
            return "저위험"

    def _interpret_competition(self, level: str) -> str:
        if level == "높음":
            return "위험: 경쟁이 매우 치열해요."
        elif level == "중간":
            return "주의: 경쟁이 다소 치열해요."
        else:
            return "안정: 경쟁이 완만해요."

    def _interpret_entry_barrier(self, level: str) -> str:
        if level == "낮음":
            return "위험: 진입장벽이 낮아요."
        elif level == "중간":
            return "주의: 진입장벽이 보통이에요."
        else:
            return "안정: 진입장벽이 높아요."

    def _interpret_substitutes(self, level: str) -> str:
        if level == "높음":
            return "위험: 대체재 위협이 커요."
        elif level == "중간":
            return "주의: 대체재 위협이 보통이에요."
        else:
            return "안정: 대체재 위협이 낮아요."

    def _assess_overall_industry_risk(self, comp: str, entry: str, sub: str) -> str:
        if "위험" in [comp, entry, sub]:
            return "고위험"
        elif "주의" in [comp, entry, sub]:
            return "중간위험"
        else:
            return "저위험"

    def _interpret_environment(self, env: str) -> str:
        if env == "높음":
            return "위험: 환경 규제 부담이 커요."
        elif env == "보통":
            return "주의: 환경 규제가 보통이에요."
        else:
            return "안정: 환경 규제가 낮아요."

    def _interpret_tax(self, tax: str) -> str:
        if tax == "높음":
            return "위험: 세금 부담이 커요."
        elif tax == "보통":
            return "주의: 세금 부담이 보통이에요."
        else:
            return "안정: 세금 부담이 낮아요."

    def _interpret_law(self, law: str) -> str:
        if law == "높음":
            return "위험: 법률 리스크가 커요."
        elif law == "보통":
            return "주의: 법률 리스크가 보통이에요."
        else:
            return "안정: 법률 리스크가 낮아요."

    def _assess_overall_regulatory_risk(self, env: str, tax: str, law: str) -> str:
        if "위험" in [env, tax, law]:
            return "고위험"
        elif "주의" in [env, tax, law]:
            return "중간위험"
        else:
            return "저위험"
