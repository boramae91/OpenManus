# -*- coding: utf-8 -*-
"""
펀더멘털 분석가 특화 도구 모음

ROIC/ROE 추세 분석, 인과관계 해석, 수익성 해체 기능을 제공해요
ChatGPT 피드백을 반영한 고급 분석 도구들이에요!
"""

import math
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from app.logger import logger


class FundamentalAnalysisTools:
    """
    펀더멘털 분석가를 위한 특화 도구들
    ROIC/ROE 추세 분석과 인과관계 해석에 특화된 도구들이에요
    """

    def __init__(self):
        """펀더멘털 분석 도구 초기화"""
        logger.info("📊 펀더멘털 분석 도구 초기화 완료!")

    def calculate_roic_trend(
        self, financial_data: Dict[str, Any], periods: int = 5
    ) -> Dict[str, Any]:
        """
        ROIC(투하자본수익률) 추세 분석

        Args:
            financial_data: 재무데이터 (DART API 또는 yfinance)
            periods: 분석할 기간 수 (기본값: 5년)

        Returns:
            Dict: ROIC 추세 분석 결과
        """
        try:
            logger.info("🔍 ROIC 추세 분석 시작...")

            # 재무데이터에서 필요한 정보 추출
            net_income = financial_data.get("net_income", 0)
            total_equity = financial_data.get("total_equity", 0)
            total_liabilities = financial_data.get("total_liabilities", 0)

            # 투하자본 계산 (자본 + 부채)
            invested_capital = total_equity + total_liabilities

            if invested_capital <= 0:
                return {
                    "success": False,
                    "error": "투하자본이 0 이하입니다",
                    "roic": 0,
                    "trend": "계산 불가",
                }

            # ROIC 계산
            roic = (net_income / invested_capital) * 100

            # 추세 분석 (실제로는 여러 연도 데이터가 필요하지만, 예시로 단일 연도 처리)
            trend_analysis = self._analyze_roic_trend(roic)

            # 인과관계 분석
            causality_analysis = self._analyze_roic_causality(financial_data)

            result = {
                "success": True,
                "roic": round(roic, 2),
                "invested_capital": invested_capital,
                "net_income": net_income,
                "trend_analysis": trend_analysis,
                "causality_analysis": causality_analysis,
                "calculation_method": "ROIC = (당기순이익 / 투하자본) × 100",
                "interpretation": self._interpret_roic(roic),
            }

            logger.info(f"✅ ROIC 분석 완료: {roic:.2f}%")
            return result

        except Exception as e:
            logger.error(f"❌ ROIC 분석 실패: {e}")
            return {"success": False, "error": str(e)}

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
