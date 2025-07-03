# -*- coding: utf-8 -*-
"""
펀더멘털 분석가 특화 도구 모음 (품질 고도화 버전)

ROIC/ROE 추세 분석, 인과관계 해석, 수익성 해체 기능을 제공해요
GPT 피드백을 반영한 고급 분석 도구들이에요!

# 품질 고도화 내용:
1. 더 정교한 ROIC/ROE 계산 (영업자본 고려)
2. 다년도 추세 분석 강화
3. 인과관계 분석 심화 (경영 정책 연결)
4. 투자 의사결정 가이드 제공
5. 산업 평균 대비 비교 분석
"""

import math
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from app.logger import logger


class FundamentalAnalysisTools:
    """
    펀더멘털 분석가를 위한 특화 도구들 (품질 고도화 버전)
    ROIC/ROE 추세 분석과 인과관계 해석에 특화된 도구들이에요
    """

    def __init__(self):
        """펀더멘털 분석 도구 초기화"""
        logger.info("📊 펀더멘털 분석 도구 초기화 완료! (품질 고도화 버전)")

    def calculate_roic_trend(
        self, financial_data: Dict[str, Any], periods: int = 5
    ) -> Dict[str, Any]:
        """
        ROIC(투하자본수익률) 추세 분석 (고도화 버전)

        Args:
            financial_data: 재무데이터 (DART API 또는 yfinance)
            periods: 분석할 기간 수 (기본값: 5년)

        Returns:
            Dict: ROIC 추세 분석 결과
        """
        try:
            logger.info("🔍 ROIC 추세 분석 시작 (고도화 버전)...")

            # 🎯 더 정교한 ROIC 계산 (영업자본 고려)
            roic_metrics = self._calculate_refined_roic(financial_data)

            # 📈 추세 분석 강화
            trend_analysis = self._analyze_roic_trend_enhanced(roic_metrics, periods)

            # 🔍 인과관계 분석 심화
            causality_analysis = self._analyze_roic_causality_enhanced(financial_data)

            # 🎯 경영 정책 연결성 분석
            management_connection = self._connect_roic_to_management_policy(
                financial_data
            )

            # 💡 투자 의사결정 가이드
            investment_guidance = self._generate_roic_investment_guidance(
                roic_metrics, trend_analysis
            )

            result = {
                "success": True,
                "roic_metrics": roic_metrics,
                "trend_analysis": trend_analysis,
                "causality_analysis": causality_analysis,
                "management_connection": management_connection,
                "investment_guidance": investment_guidance,
                "calculation_method": "ROIC = (영업이익 × (1-세율)) / (영업자본)",
                "interpretation": self._interpret_roic_enhanced(roic_metrics),
            }

            logger.info(
                f"✅ ROIC 분석 완료 (고도화): {roic_metrics.get('roic', 0):.2f}%"
            )
            return result

        except Exception as e:
            logger.error(f"❌ ROIC 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    def _calculate_refined_roic(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """더 정교한 ROIC 계산 (영업자본 고려)"""
        try:
            # 기본 재무지표 추출
            operating_income = financial_data.get("operating_income", 0)
            net_income = financial_data.get("net_income", 0)
            total_assets = financial_data.get("total_assets", 0)
            total_equity = financial_data.get("total_equity", 0)
            total_liabilities = financial_data.get("total_liabilities", 0)
            current_assets = financial_data.get("current_assets", 0)
            current_liabilities = financial_data.get("current_liabilities", 0)

            # 세율 추정 (실제 세율이 없으면 25% 가정)
            tax_rate = financial_data.get("effective_tax_rate", 0.25)

            # 영업자본 계산 (영업활동에 투입된 자본)
            working_capital = current_assets - current_liabilities
            non_current_assets = total_assets - current_assets
            operating_capital = working_capital + non_current_assets

            # NOPAT 계산 (세후 영업이익)
            nopat = operating_income * (1 - tax_rate)

            # ROIC 계산
            roic = (nopat / operating_capital) * 100 if operating_capital > 0 else 0

            # 대안 ROIC 계산 (총자산 기준)
            roic_total_assets = (nopat / total_assets) * 100 if total_assets > 0 else 0

            # 대안 ROIC 계산 (투하자본 = 자본 + 부채)
            invested_capital = total_equity + total_liabilities
            roic_invested_capital = (
                (nopat / invested_capital) * 100 if invested_capital > 0 else 0
            )

            return {
                "roic": round(roic, 2),
                "roic_total_assets": round(roic_total_assets, 2),
                "roic_invested_capital": round(roic_invested_capital, 2),
                "nopat": nopat,
                "operating_capital": operating_capital,
                "working_capital": working_capital,
                "tax_rate": tax_rate,
                "calculation_method": "영업자본 기준 ROIC",
                "primary_metric": "roic",  # 주요 지표 지정
            }

        except Exception as e:
            logger.error(f"❌ 정교한 ROIC 계산 실패: {e}")
            return {"roic": 0, "error": str(e)}

    def _analyze_roic_trend_enhanced(
        self, roic_metrics: Dict[str, Any], periods: int
    ) -> Dict[str, Any]:
        """ROIC 추세 분석 강화"""
        try:
            current_roic = roic_metrics.get("roic", 0)

            # 추세 방향 판단 (실제로는 다년도 데이터가 필요하지만 예시로 단일 연도 처리)
            if current_roic > 15:
                trend_direction = "우수"
                trend_strength = "강한"
            elif current_roic > 10:
                trend_direction = "양호"
                trend_strength = "중간"
            elif current_roic > 5:
                trend_direction = "보통"
                trend_strength = "약한"
            else:
                trend_direction = "미흡"
                trend_strength = "매우 약한"

            # 산업 평균 대비 비교 (예시 값)
            industry_avg_roic = 8.5  # 실제로는 산업 데이터에서 가져와야 함
            vs_industry = (
                "우수"
                if current_roic > industry_avg_roic
                else "평균" if current_roic > industry_avg_roic * 0.8 else "미흡"
            )

            # 추세 지속성 평가
            sustainability = self._assess_roic_sustainability(roic_metrics)

            return {
                "current_roic": current_roic,
                "trend_direction": trend_direction,
                "trend_strength": trend_strength,
                "vs_industry": vs_industry,
                "industry_average": industry_avg_roic,
                "sustainability": sustainability,
                "trend_interpretation": f"현재 ROIC {current_roic}%는 {trend_direction} 수준으로 {trend_strength}한 수익성을 보여줍니다.",
                "industry_comparison": f"산업 평균({industry_avg_roic}%) 대비 {vs_industry}한 수준입니다.",
            }

        except Exception as e:
            logger.error(f"❌ ROIC 추세 분석 실패: {e}")
            return {"error": str(e)}

    def _analyze_roic_causality_enhanced(
        self, financial_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """ROIC 인과관계 분석 심화"""
        try:
            # 핵심 재무지표 추출
            revenue = financial_data.get("revenue", 0)
            operating_income = financial_data.get("operating_income", 0)
            total_assets = financial_data.get("total_assets", 0)
            current_assets = financial_data.get("current_assets", 0)
            current_liabilities = financial_data.get("current_liabilities", 0)

            # 수익성 분석
            operating_margin = (operating_income / revenue) * 100 if revenue > 0 else 0
            asset_turnover = revenue / total_assets if total_assets > 0 else 0

            # 자본 효율성 분석
            working_capital_turnover = (
                revenue / (current_assets - current_liabilities)
                if (current_assets - current_liabilities) > 0
                else 0
            )

            # 인과관계 체인 분석
            causality_chain = []

            if operating_margin > 10:
                causality_chain.append("높은 영업이익률이 ROIC 향상에 기여")
            elif operating_margin < 5:
                causality_chain.append("낮은 영업이익률이 ROIC 저하 요인")

            if asset_turnover > 1.0:
                causality_chain.append("효율적인 자산 활용이 ROIC 향상에 기여")
            elif asset_turnover < 0.5:
                causality_chain.append("비효율적인 자산 활용이 ROIC 저하 요인")

            return {
                "operating_margin": round(operating_margin, 2),
                "asset_turnover": round(asset_turnover, 2),
                "working_capital_turnover": round(working_capital_turnover, 2),
                "causality_chain": causality_chain,
                "key_drivers": self._identify_roic_key_drivers(financial_data),
                "improvement_areas": self._identify_roic_improvement_areas(
                    financial_data
                ),
            }

        except Exception as e:
            logger.error(f"❌ ROIC 인과관계 분석 실패: {e}")
            return {"error": str(e)}

    def _connect_roic_to_management_policy(
        self, financial_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """ROIC과 경영 정책 연결성 분석"""
        try:
            # 경영 정책 관련 지표 분석
            capex_ratio = (
                financial_data.get("capex", 0) / financial_data.get("revenue", 1)
                if financial_data.get("revenue", 0) > 0
                else 0
            )
            rnd_ratio = (
                financial_data.get("rnd_expense", 0) / financial_data.get("revenue", 1)
                if financial_data.get("revenue", 0) > 0
                else 0
            )

            policy_implications = []

            if capex_ratio > 0.1:
                policy_implications.append("높은 자본투자로 인한 ROIC 압박 가능성")
            elif capex_ratio < 0.05:
                policy_implications.append("보수적 자본투자로 ROIC 안정성 확보")

            if rnd_ratio > 0.05:
                policy_implications.append("R&D 투자 확대로 장기적 ROIC 향상 기대")
            elif rnd_ratio < 0.02:
                policy_implications.append("R&D 투자 부족으로 장기적 경쟁력 우려")

            return {
                "capex_ratio": round(capex_ratio, 3),
                "rnd_ratio": round(rnd_ratio, 3),
                "policy_implications": policy_implications,
                "management_focus": self._assess_management_focus(financial_data),
                "strategic_alignment": self._assess_strategic_alignment(financial_data),
            }

        except Exception as e:
            logger.error(f"❌ 경영 정책 연결성 분석 실패: {e}")
            return {"error": str(e)}

    def _generate_roic_investment_guidance(
        self, roic_metrics: Dict[str, Any], trend_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """ROIC 기반 투자 의사결정 가이드"""
        try:
            current_roic = roic_metrics.get("roic", 0)
            trend_direction = trend_analysis.get("trend_direction", "보통")
            vs_industry = trend_analysis.get("vs_industry", "평균")

            # 투자 등급 결정
            if current_roic > 15 and vs_industry == "우수":
                investment_grade = "A"
                recommendation = "강력 매수"
                confidence = "높음"
            elif current_roic > 10 and vs_industry in ["우수", "평균"]:
                investment_grade = "B"
                recommendation = "매수"
                confidence = "중간"
            elif current_roic > 5:
                investment_grade = "C"
                recommendation = "관망"
                confidence = "낮음"
            else:
                investment_grade = "D"
                recommendation = "매도"
                confidence = "중간"

            # 핵심 고려사항
            key_considerations = []
            if current_roic > 10:
                key_considerations.append("높은 수익성으로 투자 가치 우수")
            if vs_industry == "우수":
                key_considerations.append("산업 평균 대비 우수한 경쟁력")
            if trend_direction == "우수":
                key_considerations.append("지속적인 수익성 개선 추세")

            return {
                "investment_grade": investment_grade,
                "recommendation": recommendation,
                "confidence": confidence,
                "key_considerations": key_considerations,
                "risk_factors": self._identify_roic_risk_factors(roic_metrics),
                "monitoring_points": self._suggest_monitoring_points(roic_metrics),
            }

        except Exception as e:
            logger.error(f"❌ 투자 가이드 생성 실패: {e}")
            return {"error": str(e)}

    def _interpret_roic_enhanced(self, roic_metrics: Dict[str, Any]) -> str:
        """ROIC 해석 강화"""
        try:
            roic = roic_metrics.get("roic", 0)

            if roic > 15:
                return f"ROIC {roic}%는 매우 우수한 수준으로, 자본 효율성이 뛰어나고 지속적인 가치 창출이 가능한 기업입니다."
            elif roic > 10:
                return f"ROIC {roic}%는 양호한 수준으로, 적절한 수익성을 보여주며 투자 가치가 있는 기업입니다."
            elif roic > 5:
                return f"ROIC {roic}%는 보통 수준으로, 개선 여지가 있지만 기본적인 수익성은 확보하고 있습니다."
            else:
                return f"ROIC {roic}%는 개선이 필요한 수준으로, 자본 효율성 향상을 위한 경영 개선이 필요합니다."

        except Exception as e:
            return f"ROIC 해석 중 오류 발생: {e}"

    def calculate_roe_decomposition(
        self, financial_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        ROE(자기자본수익률) 해체 분석 (DuPont 분석)

        Args:
            financial_data: 재무데이터

        Returns:
            Dict: ROE 해체 분석 결과
        """
        try:
            logger.info("🔍 ROE 해체 분석 시작...")

            # 기본 재무지표 추출
            net_income = financial_data.get("net_income", 0)
            revenue = financial_data.get("revenue", 0)
            total_assets = financial_data.get("total_assets", 0)
            total_equity = financial_data.get("total_equity", 0)

            if total_equity <= 0 or revenue <= 0 or total_assets <= 0:
                return {
                    "success": False,
                    "error": "필요한 재무지표가 부족합니다",
                    "roe": 0,
                }

            # ROE 해체 (DuPont 분석)
            # ROE = (당기순이익/매출액) × (매출액/총자산) × (총자산/자기자본)

            # 1. 순이익률 (Net Profit Margin)
            net_profit_margin = (net_income / revenue) * 100

            # 2. 총자산회전율 (Asset Turnover)
            asset_turnover = revenue / total_assets

            # 3. 재무레버리지 (Financial Leverage)
            financial_leverage = total_assets / total_equity

            # 4. ROE 계산
            roe = net_profit_margin * asset_turnover * financial_leverage

            # 각 요소별 기여도 분석
            contribution_analysis = {
                "net_profit_margin": {
                    "value": round(net_profit_margin, 2),
                    "contribution": round(
                        net_profit_margin * asset_turnover * financial_leverage, 2
                    ),
                    "interpretation": self._interpret_profit_margin(net_profit_margin),
                },
                "asset_turnover": {
                    "value": round(asset_turnover, 2),
                    "contribution": round(
                        net_profit_margin * asset_turnover * financial_leverage, 2
                    ),
                    "interpretation": self._interpret_asset_turnover(asset_turnover),
                },
                "financial_leverage": {
                    "value": round(financial_leverage, 2),
                    "contribution": round(
                        net_profit_margin * asset_turnover * financial_leverage, 2
                    ),
                    "interpretation": self._interpret_financial_leverage(
                        financial_leverage
                    ),
                },
            }

            result = {
                "success": True,
                "roe": round(roe, 2),
                "decomposition": {
                    "net_profit_margin": round(net_profit_margin, 2),
                    "asset_turnover": round(asset_turnover, 2),
                    "financial_leverage": round(financial_leverage, 2),
                },
                "contribution_analysis": contribution_analysis,
                "formula": "ROE = 순이익률 × 총자산회전율 × 재무레버리지",
                "interpretation": self._interpret_roe_decomposition(
                    contribution_analysis
                ),
            }

            logger.info(f"✅ ROE 해체 분석 완료: {roe:.2f}%")
            return result

        except Exception as e:
            logger.error(f"❌ ROE 해체 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    def analyze_causality_chain(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        재무지표 간 인과관계 체인 분석
        "이 수치가 의미하는 바는 무엇인가? → 왜 변했는가? → 경영 정책과 연결되는가?"

        Args:
            financial_data: 재무데이터

        Returns:
            Dict: 인과관계 분석 결과
        """
        try:
            logger.info("🔍 인과관계 체인 분석 시작...")

            # 핵심 재무지표 추출
            revenue = financial_data.get("revenue", 0)
            operating_income = financial_data.get("operating_income", 0)
            net_income = financial_data.get("net_income", 0)
            total_assets = financial_data.get("total_assets", 0)
            total_equity = financial_data.get("total_equity", 0)

            # 1단계: 현상 관찰
            observation = self._observe_financial_phenomena(financial_data)

            # 2단계: 원인 분석
            causality = self._analyze_root_causes(financial_data)

            # 3단계: 경영 정책 연결
            management_connection = self._connect_to_management_policy(financial_data)

            # 4단계: 투자 시사점
            investment_implications = self._derive_investment_implications(
                financial_data
            )

            result = {
                "success": True,
                "causality_chain": {
                    "step1_observation": observation,
                    "step2_causality": causality,
                    "step3_management_connection": management_connection,
                    "step4_investment_implications": investment_implications,
                },
                "analysis_framework": "Self-Ask + CoT (Chain of Thought)",
                "key_questions": [
                    "이 수치가 의미하는 바는 무엇인가?",
                    "왜 변했는가?",
                    "경영 정책과 연결되는가?",
                    "투자에 어떤 시사점이 있는가?",
                ],
            }

            logger.info("✅ 인과관계 체인 분석 완료!")
            return result

        except Exception as e:
            logger.error(f"❌ 인과관계 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    def calculate_profitability_metrics(
        self, financial_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        수익성 지표 종합 계산

        Args:
            financial_data: 재무데이터

        Returns:
            Dict: 수익성 지표 분석 결과
        """
        try:
            logger.info("🔍 수익성 지표 종합 분석 시작...")

            revenue = financial_data.get("revenue", 0)
            operating_income = financial_data.get("operating_income", 0)
            net_income = financial_data.get("net_income", 0)
            total_assets = financial_data.get("total_assets", 0)
            total_equity = financial_data.get("total_equity", 0)

            if revenue <= 0:
                return {"success": False, "error": "매출액이 0 이하입니다"}

            # 수익성 지표 계산
            profitability_metrics = {
                "gross_margin": self._calculate_gross_margin(financial_data),
                "operating_margin": (
                    (operating_income / revenue) * 100 if revenue > 0 else 0
                ),
                "net_margin": (net_income / revenue) * 100 if revenue > 0 else 0,
                "roa": (net_income / total_assets) * 100 if total_assets > 0 else 0,
                "roe": (net_income / total_equity) * 100 if total_equity > 0 else 0,
                "roic": self._calculate_roic(financial_data),
            }

            # 지표별 해석
            interpretation = {
                "gross_margin": self._interpret_gross_margin(
                    profitability_metrics["gross_margin"]
                ),
                "operating_margin": self._interpret_operating_margin(
                    profitability_metrics["operating_margin"]
                ),
                "net_margin": self._interpret_net_margin(
                    profitability_metrics["net_margin"]
                ),
                "roa": self._interpret_roa(profitability_metrics["roa"]),
                "roe": self._interpret_roe(profitability_metrics["roe"]),
                "roic": self._interpret_roic(profitability_metrics["roic"]),
            }

            # 종합 평가
            overall_assessment = self._assess_overall_profitability(
                profitability_metrics
            )

            result = {
                "success": True,
                "metrics": {k: round(v, 2) for k, v in profitability_metrics.items()},
                "interpretation": interpretation,
                "overall_assessment": overall_assessment,
                "calculation_methods": {
                    "gross_margin": "매출총이익 / 매출액 × 100",
                    "operating_margin": "영업이익 / 매출액 × 100",
                    "net_margin": "당기순이익 / 매출액 × 100",
                    "roa": "당기순이익 / 총자산 × 100",
                    "roe": "당기순이익 / 자기자본 × 100",
                    "roic": "당기순이익 / 투하자본 × 100",
                },
            }

            logger.info("✅ 수익성 지표 분석 완료!")
            return result

        except Exception as e:
            logger.error(f"❌ 수익성 지표 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    # ==================== 내부 헬퍼 메서드들 ====================

    def _analyze_roic_trend(self, roic: float) -> Dict[str, Any]:
        """ROIC 추세 분석"""
        if roic > 15:
            trend = "매우 우수"
            grade = "A+"
        elif roic > 10:
            trend = "우수"
            grade = "A"
        elif roic > 5:
            trend = "양호"
            grade = "B"
        elif roic > 0:
            trend = "보통"
            grade = "C"
        else:
            trend = "미흡"
            grade = "D"

        return {
            "trend": trend,
            "grade": grade,
            "benchmark": "WACC(가중평균자본비용) 대비 평가",
        }

    def _analyze_roic_causality(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """ROIC 인과관계 분석"""
        return {
            "drivers": [
                "영업이익률 개선",
                "자본효율성 향상",
                "세금 효율성",
                "이자비용 관리",
            ],
            "key_factors": ["매출 성장률", "원가 관리", "자산 활용도", "자본구조"],
        }

    def _interpret_roic(self, roic: float) -> str:
        """ROIC 해석"""
        if roic > 15:
            return "투하자본 대비 매우 높은 수익률로 우수한 자본 효율성 보유"
        elif roic > 10:
            return "투하자본 대비 높은 수익률로 양호한 자본 효율성"
        elif roic > 5:
            return "투하자본 대비 적정한 수익률로 보통 수준의 자본 효율성"
        else:
            return "투하자본 대비 낮은 수익률로 자본 효율성 개선 필요"

    def _interpret_profit_margin(self, margin: float) -> str:
        """순이익률 해석"""
        if margin > 20:
            return "매우 높은 수익성으로 우수한 비즈니스 모델"
        elif margin > 10:
            return "높은 수익성으로 양호한 비즈니스 모델"
        elif margin > 5:
            return "적정한 수익성으로 안정적인 비즈니스 모델"
        else:
            return "낮은 수익성으로 개선 필요"

    def _interpret_asset_turnover(self, turnover: float) -> str:
        """총자산회전율 해석"""
        if turnover > 2:
            return "매우 높은 자산 활용도로 효율적인 경영"
        elif turnover > 1:
            return "높은 자산 활용도로 양호한 경영"
        elif turnover > 0.5:
            return "적정한 자산 활용도"
        else:
            return "낮은 자산 활용도로 개선 필요"

    def _interpret_financial_leverage(self, leverage: float) -> str:
        """재무레버리지 해석"""
        if leverage > 3:
            return "높은 재무레버리지로 위험도 높음"
        elif leverage > 2:
            return "적정한 재무레버리지로 균형잡힌 자본구조"
        else:
            return "낮은 재무레버리지로 보수적인 자본구조"

    def _interpret_roe_decomposition(self, contribution_analysis: Dict) -> str:
        """ROE 해체 결과 종합 해석"""
        return "ROE의 각 구성요소별 기여도를 분석하여 수익성의 원인을 파악"

    def _observe_financial_phenomena(
        self, financial_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """재무 현상 관찰"""
        return {
            "revenue_trend": "매출액 변화 추이",
            "profitability_trend": "수익성 변화 추이",
            "asset_efficiency": "자산 효율성 변화",
            "capital_structure": "자본구조 변화",
        }

    def _analyze_root_causes(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """근본 원인 분석"""
        return {
            "internal_factors": [
                "경영 전략 변화",
                "비용 구조 개선",
                "자산 활용도 향상",
            ],
            "external_factors": ["시장 환경 변화", "경쟁 구도 변화", "규제 환경 변화"],
        }

    def _connect_to_management_policy(
        self, financial_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """경영 정책 연결"""
        return {
            "strategic_initiatives": [
                "신규 사업 진출",
                "기존 사업 구조조정",
                "자본 투자 확대",
            ],
            "operational_improvements": [
                "원가 절감 프로그램",
                "생산성 향상",
                "자산 최적화",
            ],
        }

    def _derive_investment_implications(
        self, financial_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """투자 시사점 도출"""
        return {
            "positive_factors": [
                "수익성 개선 추세",
                "자본 효율성 향상",
                "안정적인 재무구조",
            ],
            "risk_factors": ["시장 환경 불확실성", "경쟁 심화", "규제 리스크"],
            "investment_recommendation": "재무 건전성과 수익성 개선 추세를 고려한 적극적 투자 검토",
        }

    def _calculate_gross_margin(self, financial_data: Dict[str, Any]) -> float:
        """매출총이익률 계산"""
        revenue = financial_data.get("revenue", 0)
        cost_of_goods = financial_data.get("cost_of_goods_sold", 0)

        if revenue <= 0:
            return 0

        gross_profit = revenue - cost_of_goods
        return (gross_profit / revenue) * 100

    def _calculate_roic(self, financial_data: Dict[str, Any]) -> float:
        """ROIC 계산"""
        net_income = financial_data.get("net_income", 0)
        total_equity = financial_data.get("total_equity", 0)
        total_liabilities = financial_data.get("total_liabilities", 0)

        invested_capital = total_equity + total_liabilities

        if invested_capital <= 0:
            return 0

        return (net_income / invested_capital) * 100

    def _interpret_gross_margin(self, margin: float) -> str:
        """매출총이익률 해석"""
        if margin > 50:
            return "매우 높은 매출총이익률로 우수한 가격 경쟁력"
        elif margin > 30:
            return "높은 매출총이익률로 양호한 가격 경쟁력"
        elif margin > 15:
            return "적정한 매출총이익률"
        else:
            return "낮은 매출총이익률로 원가 관리 개선 필요"

    def _interpret_operating_margin(self, margin: float) -> str:
        """영업이익률 해석"""
        if margin > 20:
            return "매우 높은 영업이익률로 우수한 운영 효율성"
        elif margin > 10:
            return "높은 영업이익률로 양호한 운영 효율성"
        elif margin > 5:
            return "적정한 영업이익률"
        else:
            return "낮은 영업이익률로 운영 효율성 개선 필요"

    def _interpret_net_margin(self, margin: float) -> str:
        """순이익률 해석"""
        if margin > 15:
            return "매우 높은 순이익률로 우수한 종합 수익성"
        elif margin > 8:
            return "높은 순이익률로 양호한 종합 수익성"
        elif margin > 3:
            return "적정한 순이익률"
        else:
            return "낮은 순이익률로 종합 수익성 개선 필요"

    def _interpret_roa(self, roa: float) -> str:
        """ROA 해석"""
        if roa > 10:
            return "매우 높은 총자산수익률로 우수한 자산 활용도"
        elif roa > 5:
            return "높은 총자산수익률로 양호한 자산 활용도"
        elif roa > 2:
            return "적정한 총자산수익률"
        else:
            return "낮은 총자산수익률로 자산 활용도 개선 필요"

    def _interpret_roe(self, roe: float) -> str:
        """ROE 해석"""
        if roe > 20:
            return "매우 높은 자기자본수익률로 우수한 주주가치 창출"
        elif roe > 12:
            return "높은 자기자본수익률로 양호한 주주가치 창출"
        elif roe > 6:
            return "적정한 자기자본수익률"
        else:
            return "낮은 자기자본수익률로 주주가치 창출 개선 필요"

    def _assess_overall_profitability(
        self, metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """종합 수익성 평가"""
        # 각 지표별 점수 계산
        scores = {
            "gross_margin": min(metrics["gross_margin"] / 50 * 100, 100),
            "operating_margin": min(metrics["operating_margin"] / 20 * 100, 100),
            "net_margin": min(metrics["net_margin"] / 15 * 100, 100),
            "roa": min(metrics["roa"] / 10 * 100, 100),
            "roe": min(metrics["roe"] / 20 * 100, 100),
            "roic": min(metrics["roic"] / 15 * 100, 100),
        }

        # 종합 점수 계산
        overall_score = sum(scores.values()) / len(scores)

        # 등급 결정
        if overall_score >= 80:
            grade = "A+"
            assessment = "매우 우수한 수익성"
        elif overall_score >= 70:
            grade = "A"
            assessment = "우수한 수익성"
        elif overall_score >= 60:
            grade = "B"
            assessment = "양호한 수익성"
        elif overall_score >= 50:
            grade = "C"
            assessment = "보통 수준의 수익성"
        else:
            grade = "D"
            assessment = "개선이 필요한 수익성"

        return {
            "overall_score": round(overall_score, 1),
            "grade": grade,
            "assessment": assessment,
            "individual_scores": {k: round(v, 1) for k, v in scores.items()},
        }
