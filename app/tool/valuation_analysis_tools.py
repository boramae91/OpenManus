# -*- coding: utf-8 -*-
"""
밸류에이션 전문가 특화 도구 모음

DCF, 멀티플, FCF Yield 계산 기능을 제공해요
ChatGPT 피드백을 반영한 고급 밸류에이션 도구들이에요!
"""

import math
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from app.logger import logger


class ValuationAnalysisTools:
    """
    밸류에이션 전문가를 위한 특화 도구들
    DCF, 멀티플, FCF Yield 계산에 특화된 도구들이에요
    """

    def __init__(self):
        """밸류에이션 분석 도구 초기화"""
        logger.info("💰 밸류에이션 분석 도구 초기화 완료!")

    def calculate_dcf_valuation(
        self,
        financial_data: Dict[str, Any],
        growth_rate: float = 0.05,
        discount_rate: float = 0.10,
        terminal_growth: float = 0.02,
        projection_years: int = 5,
    ) -> Dict[str, Any]:
        """
        DCF(현금흐름할인) 모델을 통한 기업가치 평가

        Args:
            financial_data: 재무데이터
            growth_rate: 성장률 (기본값: 5%)
            discount_rate: 할인율 (기본값: 10%)
            terminal_growth: 터미널 성장률 (기본값: 2%)
            projection_years: 예측 기간 (기본값: 5년)

        Returns:
            Dict: DCF 분석 결과
        """
        try:
            logger.info("🔍 DCF 밸류에이션 분석 시작...")

            # 기본 재무지표 추출
            revenue = financial_data.get("revenue", 0)
            operating_income = financial_data.get("operating_income", 0)
            net_income = financial_data.get("net_income", 0)
            total_assets = financial_data.get("total_assets", 0)
            total_equity = financial_data.get("total_equity", 0)

            if revenue <= 0 or net_income <= 0:
                return {"success": False, "error": "매출액 또는 순이익이 0 이하입니다"}

            # FCF 계산
            fcf = self._calculate_fcf(financial_data)

            # 예측 기간별 FCF 계산
            projected_fcf = []
            current_fcf = fcf

            for year in range(1, projection_years + 1):
                projected_fcf.append(
                    {
                        "year": year,
                        "fcf": current_fcf,
                        "discount_factor": 1 / ((1 + discount_rate) ** year),
                        "present_value": current_fcf / ((1 + discount_rate) ** year),
                    }
                )
                current_fcf *= 1 + growth_rate

            # 터미널 가치 계산
            terminal_fcf = projected_fcf[-1]["fcf"] * (1 + terminal_growth)
            terminal_value = terminal_fcf / (discount_rate - terminal_growth)
            terminal_value_pv = terminal_value / (
                (1 + discount_rate) ** projection_years
            )

            # 기업가치 계산
            fcf_present_values = sum(pv["present_value"] for pv in projected_fcf)
            enterprise_value = fcf_present_values + terminal_value_pv

            # 주주가치 계산 (부채 차감)
            total_liabilities = financial_data.get("total_liabilities", 0)
            equity_value = enterprise_value - total_liabilities

            # 주가 계산 (발행주식수 가정)
            shares_outstanding = self._estimate_shares_outstanding(financial_data)
            target_price = (
                equity_value / shares_outstanding if shares_outstanding > 0 else 0
            )

            # 현재 주가와 비교
            current_price = financial_data.get("current_price", 0)
            upside_potential = (
                ((target_price - current_price) / current_price * 100)
                if current_price > 0
                else 0
            )

            result = {
                "success": True,
                "dcf_components": {
                    "projected_fcf": projected_fcf,
                    "terminal_value": {
                        "value": round(terminal_value, 0),
                        "present_value": round(terminal_value_pv, 0),
                    },
                    "fcf_present_values": round(fcf_present_values, 0),
                },
                "valuation_results": {
                    "enterprise_value": round(enterprise_value, 0),
                    "equity_value": round(equity_value, 0),
                    "target_price": round(target_price, 2),
                    "current_price": current_price,
                    "upside_potential": round(upside_potential, 2),
                },
                "assumptions": {
                    "growth_rate": growth_rate,
                    "discount_rate": discount_rate,
                    "terminal_growth": terminal_growth,
                    "projection_years": projection_years,
                },
                "sensitivity_analysis": self._perform_sensitivity_analysis(
                    fcf, growth_rate, discount_rate, terminal_growth, projection_years
                ),
                "interpretation": self._interpret_dcf_results(
                    target_price, current_price, upside_potential
                ),
            }

            logger.info(f"✅ DCF 분석 완료: 목표가 {target_price:.2f}원")
            return result

        except Exception as e:
            logger.error(f"❌ DCF 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    def calculate_multiple_valuation(
        self, financial_data: Dict[str, Any], sector_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        멀티플 기반 기업가치 평가

        Args:
            financial_data: 재무데이터
            sector_data: 섹터 평균 데이터 (선택사항)

        Returns:
            Dict: 멀티플 분석 결과
        """
        try:
            logger.info("🔍 멀티플 밸류에이션 분석 시작...")

            # 기본 재무지표 추출
            revenue = financial_data.get("revenue", 0)
            operating_income = financial_data.get("operating_income", 0)
            net_income = financial_data.get("net_income", 0)
            total_assets = financial_data.get("total_assets", 0)
            total_equity = financial_data.get("total_equity", 0)
            current_price = financial_data.get("current_price", 0)

            if revenue <= 0 or net_income <= 0:
                return {"success": False, "error": "매출액 또는 순이익이 0 이하입니다"}

            # 발행주식수 추정
            shares_outstanding = self._estimate_shares_outstanding(financial_data)
            if shares_outstanding <= 0:
                return {"success": False, "error": "발행주식수를 추정할 수 없습니다"}

            # 시가총액 계산
            market_cap = current_price * shares_outstanding

            # 주요 멀티플 계산
            multiples = {
                "P/E": round(market_cap / net_income, 2) if net_income > 0 else 0,
                "P/B": round(market_cap / total_equity, 2) if total_equity > 0 else 0,
                "P/S": round(market_cap / revenue, 2) if revenue > 0 else 0,
                "EV/EBITDA": self._calculate_ev_ebitda(financial_data),
                "ROE": (
                    round((net_income / total_equity) * 100, 2)
                    if total_equity > 0
                    else 0
                ),
                "ROA": (
                    round((net_income / total_assets) * 100, 2)
                    if total_assets > 0
                    else 0
                ),
            }

            # 섹터 비교 분석
            sector_comparison = self._compare_with_sector(multiples, sector_data)

            # 적정 멀티플 기반 목표가 계산
            target_prices = self._calculate_target_prices_by_multiple(
                multiples, financial_data
            )

            # 종합 목표가 계산
            avg_target_price = (
                sum(target_prices.values()) / len(target_prices) if target_prices else 0
            )
            upside_potential = (
                ((avg_target_price - current_price) / current_price * 100)
                if current_price > 0
                else 0
            )

            result = {
                "success": True,
                "current_multiples": multiples,
                "sector_comparison": sector_comparison,
                "target_prices_by_multiple": target_prices,
                "valuation_summary": {
                    "average_target_price": round(avg_target_price, 2),
                    "current_price": current_price,
                    "upside_potential": round(upside_potential, 2),
                    "recommendation": self._get_multiple_recommendation(
                        upside_potential
                    ),
                },
                "interpretation": self._interpret_multiple_valuation(
                    multiples, sector_comparison
                ),
            }

            logger.info(f"✅ 멀티플 분석 완료: 평균 목표가 {avg_target_price:.2f}원")
            return result

        except Exception as e:
            logger.error(f"❌ 멀티플 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    def calculate_fcf_yield_analysis(
        self, financial_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        FCF Yield 분석

        Args:
            financial_data: 재무데이터

        Returns:
            Dict: FCF Yield 분석 결과
        """
        try:
            logger.info("🔍 FCF Yield 분석 시작...")

            # FCF 계산
            fcf = self._calculate_fcf(financial_data)

            # 시가총액 추정
            current_price = financial_data.get("current_price", 0)
            shares_outstanding = self._estimate_shares_outstanding(financial_data)
            market_cap = current_price * shares_outstanding

            if market_cap <= 0:
                return {"success": False, "error": "시가총액을 계산할 수 없습니다"}

            # FCF Yield 계산
            fcf_yield = (fcf / market_cap) * 100 if market_cap > 0 else 0

            # FCF Yield 해석
            yield_interpretation = self._interpret_fcf_yield(fcf_yield)

            # FCF 성장성 분석
            fcf_growth_analysis = self._analyze_fcf_growth(financial_data)

            # FCF 안정성 분석
            fcf_stability_analysis = self._analyze_fcf_stability(financial_data)

            result = {
                "success": True,
                "fcf_analysis": {
                    "fcf": round(fcf, 0),
                    "market_cap": round(market_cap, 0),
                    "fcf_yield": round(fcf_yield, 2),
                    "yield_interpretation": yield_interpretation,
                },
                "fcf_growth_analysis": fcf_growth_analysis,
                "fcf_stability_analysis": fcf_stability_analysis,
                "investment_implications": self._get_fcf_investment_implications(
                    fcf_yield, fcf_growth_analysis
                ),
                "calculation_method": "FCF Yield = (자유현금흐름 / 시가총액) × 100",
            }

            logger.info(f"✅ FCF Yield 분석 완료: {fcf_yield:.2f}%")
            return result

        except Exception as e:
            logger.error(f"❌ FCF Yield 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    def perform_scenario_analysis(
        self, financial_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        시나리오별 DCF 분석 (낙관/기준/비관)

        Args:
            financial_data: 재무데이터

        Returns:
            Dict: 시나리오 분석 결과
        """
        try:
            logger.info("🔍 시나리오별 DCF 분석 시작...")

            # 기본 FCF 계산
            base_fcf = self._calculate_fcf(financial_data)

            # 시나리오별 가정
            scenarios = {
                "optimistic": {
                    "growth_rate": 0.08,  # 8% 성장
                    "discount_rate": 0.08,  # 8% 할인율
                    "terminal_growth": 0.03,  # 3% 터미널 성장
                    "description": "낙관적 시나리오",
                },
                "base": {
                    "growth_rate": 0.05,  # 5% 성장
                    "discount_rate": 0.10,  # 10% 할인율
                    "terminal_growth": 0.02,  # 2% 터미널 성장
                    "description": "기준 시나리오",
                },
                "pessimistic": {
                    "growth_rate": 0.02,  # 2% 성장
                    "discount_rate": 0.12,  # 12% 할인율
                    "terminal_growth": 0.01,  # 1% 터미널 성장
                    "description": "비관적 시나리오",
                },
            }

            scenario_results = {}

            for scenario_name, assumptions in scenarios.items():
                # 각 시나리오별 DCF 계산
                dcf_result = self.calculate_dcf_valuation(
                    financial_data,
                    growth_rate=assumptions["growth_rate"],
                    discount_rate=assumptions["discount_rate"],
                    terminal_growth=assumptions["terminal_growth"],
                )

                if dcf_result.get("success"):
                    scenario_results[scenario_name] = {
                        "assumptions": assumptions,
                        "target_price": dcf_result["valuation_results"]["target_price"],
                        "upside_potential": dcf_result["valuation_results"][
                            "upside_potential"
                        ],
                        "enterprise_value": dcf_result["valuation_results"][
                            "enterprise_value"
                        ],
                    }

            # 시나리오별 결과 요약
            current_price = financial_data.get("current_price", 0)
            price_range = {
                "min": min(
                    [result["target_price"] for result in scenario_results.values()]
                ),
                "max": max(
                    [result["target_price"] for result in scenario_results.values()]
                ),
                "avg": sum(
                    [result["target_price"] for result in scenario_results.values()]
                )
                / len(scenario_results),
            }

            # 확률 가중 목표가 (기준 시나리오에 높은 가중치)
            weighted_price = (
                scenario_results["pessimistic"]["target_price"] * 0.2
                + scenario_results["base"]["target_price"] * 0.6
                + scenario_results["optimistic"]["target_price"] * 0.2
            )

            result = {
                "success": True,
                "scenario_results": scenario_results,
                "price_range": {
                    "min": round(price_range["min"], 2),
                    "max": round(price_range["max"], 2),
                    "average": round(price_range["avg"], 2),
                    "weighted": round(weighted_price, 2),
                },
                "current_price": current_price,
                "investment_recommendation": self._get_scenario_recommendation(
                    current_price, price_range, weighted_price
                ),
                "risk_assessment": self._assess_scenario_risk(scenario_results),
            }

            logger.info("✅ 시나리오별 DCF 분석 완료!")
            return result

        except Exception as e:
            logger.error(f"❌ 시나리오 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    def calculate_intrinsic_value(
        self, financial_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        내재가치 종합 계산 (여러 방법론 통합)

        Args:
            financial_data: 재무데이터

        Returns:
            Dict: 내재가치 종합 분석 결과
        """
        try:
            logger.info("🔍 내재가치 종합 분석 시작...")

            # 1. DCF 분석
            dcf_result = self.calculate_dcf_valuation(financial_data)

            # 2. 멀티플 분석
            multiple_result = self.calculate_multiple_valuation(financial_data)

            # 3. FCF Yield 분석
            fcf_result = self.calculate_fcf_yield_analysis(financial_data)

            # 4. 시나리오 분석
            scenario_result = self.perform_scenario_analysis(financial_data)

            # 종합 내재가치 계산
            valuation_methods = []

            if dcf_result.get("success"):
                valuation_methods.append(
                    {
                        "method": "DCF",
                        "target_price": dcf_result["valuation_results"]["target_price"],
                        "weight": 0.4,
                    }
                )

            if multiple_result.get("success"):
                valuation_methods.append(
                    {
                        "method": "Multiple",
                        "target_price": multiple_result["valuation_summary"][
                            "average_target_price"
                        ],
                        "weight": 0.3,
                    }
                )

            if scenario_result.get("success"):
                valuation_methods.append(
                    {
                        "method": "Scenario",
                        "target_price": scenario_result["price_range"]["weighted"],
                        "weight": 0.3,
                    }
                )

            # 가중 평균 내재가치 계산
            weighted_intrinsic_value = 0
            total_weight = 0

            for method in valuation_methods:
                weighted_intrinsic_value += method["target_price"] * method["weight"]
                total_weight += method["weight"]

            final_intrinsic_value = (
                weighted_intrinsic_value / total_weight if total_weight > 0 else 0
            )

            # 현재 주가와 비교
            current_price = financial_data.get("current_price", 0)
            upside_potential = (
                ((final_intrinsic_value - current_price) / current_price * 100)
                if current_price > 0
                else 0
            )

            result = {
                "success": True,
                "valuation_methods": valuation_methods,
                "intrinsic_value": {
                    "final_value": round(final_intrinsic_value, 2),
                    "current_price": current_price,
                    "upside_potential": round(upside_potential, 2),
                    "margin_of_safety": (
                        round(
                            (final_intrinsic_value - current_price)
                            / final_intrinsic_value
                            * 100,
                            2,
                        )
                        if final_intrinsic_value > 0
                        else 0
                    ),
                },
                "detailed_analysis": {
                    "dcf": dcf_result,
                    "multiple": multiple_result,
                    "fcf_yield": fcf_result,
                    "scenario": scenario_result,
                },
                "investment_recommendation": self._get_final_recommendation(
                    upside_potential
                ),
                "confidence_level": self._calculate_valuation_confidence(
                    valuation_methods
                ),
                "risk_factors": self._identify_valuation_risks(financial_data),
            }

            logger.info(f"✅ 내재가치 종합 분석 완료: {final_intrinsic_value:.2f}원")
            return result

        except Exception as e:
            logger.error(f"❌ 내재가치 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    # ==================== 내부 헬퍼 메서드들 ====================

    def _calculate_fcf(self, financial_data: Dict[str, Any]) -> float:
        """자유현금흐름(FCF) 계산"""
        operating_income = financial_data.get("operating_income", 0)
        depreciation = financial_data.get("depreciation", 0)  # 감가상각비
        capex = financial_data.get("capital_expenditure", 0)  # 자본지출
        working_capital_change = financial_data.get(
            "working_capital_change", 0
        )  # 운전자본 변화

        # 간단한 FCF 계산 (실제로는 더 복잡한 계산 필요)
        fcf = operating_income + depreciation - capex - working_capital_change

        return max(fcf, 0)  # FCF는 음수가 될 수 있지만, 평가 목적으로는 0으로 처리

    def _estimate_shares_outstanding(self, financial_data: Dict[str, Any]) -> float:
        """발행주식수 추정"""
        # 시가총액과 주가로부터 역산
        current_price = financial_data.get("current_price", 0)
        market_cap = financial_data.get("market_cap", 0)

        if current_price > 0 and market_cap > 0:
            return market_cap / current_price
        elif current_price > 0:
            # 시가총액이 없는 경우 자본금으로 추정
            capital_stock = financial_data.get("capital_stock", 0)
            if capital_stock > 0:
                return capital_stock / 1000  # 액면가 1,000원 가정
            else:
                return 1000000  # 기본값 100만주
        else:
            return 1000000  # 기본값 100만주

    def _calculate_ev_ebitda(self, financial_data: Dict[str, Any]) -> float:
        """EV/EBITDA 계산"""
        current_price = financial_data.get("current_price", 0)
        shares_outstanding = self._estimate_shares_outstanding(financial_data)
        market_cap = current_price * shares_outstanding

        total_liabilities = financial_data.get("total_liabilities", 0)
        cash = financial_data.get("cash_and_equivalents", 0)

        enterprise_value = market_cap + total_liabilities - cash

        operating_income = financial_data.get("operating_income", 0)
        depreciation = financial_data.get("depreciation", 0)
        ebitda = operating_income + depreciation

        return round(enterprise_value / ebitda, 2) if ebitda > 0 else 0

    def _compare_with_sector(
        self, multiples: Dict[str, float], sector_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """섹터 평균과 비교"""
        if not sector_data:
            return {"available": False}

        comparison = {}
        for multiple_name, company_value in multiples.items():
            sector_value = sector_data.get(f"sector_{multiple_name}", 0)
            if sector_value > 0:
                comparison[multiple_name] = {
                    "company": company_value,
                    "sector": sector_value,
                    "difference": round(company_value - sector_value, 2),
                    "premium": round(
                        (company_value - sector_value) / sector_value * 100, 2
                    ),
                }

        return {"available": True, "comparison": comparison}

    def _calculate_target_prices_by_multiple(
        self, multiples: Dict[str, float], financial_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """멀티플별 목표가 계산"""
        target_prices = {}

        # P/E 기반 목표가
        if multiples["P/E"] > 0:
            net_income = financial_data.get("net_income", 0)
            shares_outstanding = self._estimate_shares_outstanding(financial_data)
            target_prices["P/E"] = (
                (net_income / shares_outstanding) * multiples["P/E"]
                if shares_outstanding > 0
                else 0
            )

        # P/B 기반 목표가
        if multiples["P/B"] > 0:
            total_equity = financial_data.get("total_equity", 0)
            shares_outstanding = self._estimate_shares_outstanding(financial_data)
            target_prices["P/B"] = (
                (total_equity / shares_outstanding) * multiples["P/B"]
                if shares_outstanding > 0
                else 0
            )

        # P/S 기반 목표가
        if multiples["P/S"] > 0:
            revenue = financial_data.get("revenue", 0)
            shares_outstanding = self._estimate_shares_outstanding(financial_data)
            target_prices["P/S"] = (
                (revenue / shares_outstanding) * multiples["P/S"]
                if shares_outstanding > 0
                else 0
            )

        return target_prices

    def _get_multiple_recommendation(self, upside_potential: float) -> str:
        """멀티플 기반 투자 추천"""
        if upside_potential > 30:
            return "강력 매수"
        elif upside_potential > 15:
            return "매수"
        elif upside_potential > 5:
            return "약한 매수"
        elif upside_potential > -5:
            return "중립"
        elif upside_potential > -15:
            return "약한 매도"
        else:
            return "매도"

    def _interpret_multiple_valuation(
        self, multiples: Dict[str, float], sector_comparison: Dict[str, Any]
    ) -> str:
        """멀티플 밸류에이션 해석"""
        interpretation = []

        # P/E 해석
        if multiples["P/E"] > 0:
            if multiples["P/E"] < 15:
                interpretation.append("P/E가 낮아 저평가 가능성")
            elif multiples["P/E"] > 25:
                interpretation.append("P/E가 높아 고평가 가능성")

        # P/B 해석
        if multiples["P/B"] > 0:
            if multiples["P/B"] < 1:
                interpretation.append("P/B가 1 미만으로 자산 대비 저평가")
            elif multiples["P/B"] > 3:
                interpretation.append("P/B가 높아 자산 대비 고평가")

        # ROE 해석
        if multiples["ROE"] > 15:
            interpretation.append("높은 ROE로 우수한 수익성")
        elif multiples["ROE"] < 5:
            interpretation.append("낮은 ROE로 수익성 개선 필요")

        return (
            "; ".join(interpretation) if interpretation else "멀티플 분석 결과 중립적"
        )

    def _interpret_fcf_yield(self, fcf_yield: float) -> str:
        """FCF Yield 해석"""
        if fcf_yield > 8:
            return "매우 높은 FCF Yield로 강력한 매수 신호"
        elif fcf_yield > 5:
            return "높은 FCF Yield로 매수 신호"
        elif fcf_yield > 3:
            return "적정한 FCF Yield"
        elif fcf_yield > 1:
            return "낮은 FCF Yield로 매수 신호 약함"
        else:
            return "매우 낮은 FCF Yield로 매수 신호 없음"

    def _analyze_fcf_growth(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """FCF 성장성 분석"""
        # 실제로는 과거 데이터가 필요하지만, 예시로 기본값 사용
        return {
            "growth_rate": "분석 불가 (과거 데이터 부족)",
            "stability": "분석 불가 (과거 데이터 부족)",
            "quality": "분석 불가 (과거 데이터 부족)",
        }

    def _analyze_fcf_stability(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """FCF 안정성 분석"""
        return {
            "volatility": "분석 불가 (과거 데이터 부족)",
            "predictability": "분석 불가 (과거 데이터 부족)",
            "sustainability": "분석 불가 (과거 데이터 부족)",
        }

    def _get_fcf_investment_implications(
        self, fcf_yield: float, growth_analysis: Dict[str, Any]
    ) -> str:
        """FCF 투자 시사점"""
        if fcf_yield > 5:
            return "높은 FCF Yield로 현금 창출 능력 우수, 배당 증가 가능성"
        elif fcf_yield > 3:
            return "적정한 FCF Yield로 안정적인 현금 창출"
        else:
            return "낮은 FCF Yield로 현금 창출 능력 제한적"

    def _perform_sensitivity_analysis(
        self,
        fcf: float,
        growth_rate: float,
        discount_rate: float,
        terminal_growth: float,
        projection_years: int,
    ) -> Dict[str, Any]:
        """민감도 분석"""
        # 성장률 변화에 따른 영향
        growth_scenarios = {
            "low_growth": growth_rate * 0.8,
            "base_growth": growth_rate,
            "high_growth": growth_rate * 1.2,
        }

        # 할인율 변화에 따른 영향
        discount_scenarios = {
            "low_discount": discount_rate * 0.9,
            "base_discount": discount_rate,
            "high_discount": discount_rate * 1.1,
        }

        return {
            "growth_sensitivity": growth_scenarios,
            "discount_sensitivity": discount_scenarios,
            "key_drivers": ["성장률", "할인율", "터미널 성장률"],
        }

    def _interpret_dcf_results(
        self, target_price: float, current_price: float, upside_potential: float
    ) -> str:
        """DCF 결과 해석"""
        if upside_potential > 30:
            return "DCF 모델 기준으로 강력한 매수 신호"
        elif upside_potential > 15:
            return "DCF 모델 기준으로 매수 신호"
        elif upside_potential > 5:
            return "DCF 모델 기준으로 약한 매수 신호"
        elif upside_potential > -5:
            return "DCF 모델 기준으로 공정가치"
        else:
            return "DCF 모델 기준으로 매도 신호"

    def _get_scenario_recommendation(
        self, current_price: float, price_range: Dict[str, float], weighted_price: float
    ) -> str:
        """시나리오별 투자 추천"""
        if current_price < price_range["min"]:
            return "강력 매수 (모든 시나리오에서 상승 가능)"
        elif current_price < weighted_price:
            return "매수 (가중 평균 대비 저평가)"
        elif current_price < price_range["max"]:
            return "중립 (시나리오별 결과 혼재)"
        else:
            return "매도 (모든 시나리오에서 하락 가능)"

    def _assess_scenario_risk(self, scenario_results: Dict[str, Any]) -> Dict[str, Any]:
        """시나리오별 리스크 평가"""
        price_range = max(
            [result["target_price"] for result in scenario_results.values()]
        ) - min([result["target_price"] for result in scenario_results.values()])

        if price_range > 50:
            risk_level = "높음"
        elif price_range > 20:
            risk_level = "중간"
        else:
            risk_level = "낮음"

        return {
            "risk_level": risk_level,
            "price_range": round(price_range, 2),
            "uncertainty": (
                "높음"
                if risk_level == "높음"
                else "중간" if risk_level == "중간" else "낮음"
            ),
        }

    def _get_final_recommendation(self, upside_potential: float) -> Dict[str, Any]:
        """최종 투자 추천"""
        if upside_potential > 30:
            return {
                "action": "강력 매수",
                "confidence": "높음",
                "reasoning": "여러 밸류에이션 방법에서 일관된 상승 가능성",
            }
        elif upside_potential > 15:
            return {
                "action": "매수",
                "confidence": "중간",
                "reasoning": "대부분의 밸류에이션 방법에서 상승 가능성",
            }
        elif upside_potential > 5:
            return {
                "action": "약한 매수",
                "confidence": "낮음",
                "reasoning": "일부 밸류에이션 방법에서 상승 가능성",
            }
        elif upside_potential > -5:
            return {
                "action": "중립",
                "confidence": "낮음",
                "reasoning": "밸류에이션 결과 혼재",
            }
        else:
            return {
                "action": "매도",
                "confidence": "중간",
                "reasoning": "대부분의 밸류에이션 방법에서 하락 가능성",
            }

    def _calculate_valuation_confidence(
        self, valuation_methods: List[Dict[str, Any]]
    ) -> str:
        """밸류에이션 신뢰도 계산"""
        if len(valuation_methods) >= 3:
            return "높음"
        elif len(valuation_methods) >= 2:
            return "중간"
        else:
            return "낮음"

    def _identify_valuation_risks(self, financial_data: Dict[str, Any]) -> List[str]:
        """밸류에이션 리스크 요소 식별"""
        risks = []

        # 재무 건전성 리스크
        if financial_data.get("debt_ratio", 0) > 200:
            risks.append("높은 부채비율")

        # 수익성 리스크
        if financial_data.get("operating_margin", 0) < 5:
            risks.append("낮은 영업이익률")

        # 성장성 리스크
        if financial_data.get("revenue", 0) <= 0:
            risks.append("매출 성장 부족")

        return risks if risks else ["특별한 리스크 요소 없음"]
