# -*- coding: utf-8 -*-
"""
산업 전문가 특화 도구 모음

산업 구조 분석, 경쟁 구도 파악, 산업 생명주기 분석 기능을 제공해요
ChatGPT 피드백을 반영한 고급 산업 분석 도구들이에요!
"""

import math
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from app.logger import logger


class IndustryAnalysisTools:
    """
    산업 전문가를 위한 특화 도구들
    산업 구조 분석과 경쟁 구도 파악에 특화된 도구들이에요
    """

    def __init__(self):
        """산업 분석 도구 초기화"""
        logger.info("🏭 산업 분석 도구 초기화 완료!")

    def analyze_industry_structure(
        self, company_data: Dict[str, Any], industry_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        산업 구조 분석 (5 Forces Model 기반)

        Args:
            company_data: 대상 기업 데이터
            industry_data: 산업 전체 데이터

        Returns:
            Dict: 산업 구조 분석 결과
        """
        try:
            logger.info("🔍 산업 구조 분석 시작...")

            # 5 Forces Model 분석
            five_forces = self._analyze_five_forces(company_data, industry_data)

            # 산업 집중도 분석
            concentration_analysis = self._analyze_industry_concentration(industry_data)

            # 진입장벽 분석
            entry_barriers = self._analyze_entry_barriers(industry_data)

            # 산업 수익성 분석
            profitability_analysis = self._analyze_industry_profitability(industry_data)

            result = {
                "success": True,
                "five_forces_analysis": five_forces,
                "concentration_analysis": concentration_analysis,
                "entry_barriers": entry_barriers,
                "profitability_analysis": profitability_analysis,
                "overall_assessment": self._assess_industry_attractiveness(
                    five_forces, concentration_analysis, entry_barriers
                ),
                "strategic_implications": self._derive_strategic_implications(
                    five_forces, concentration_analysis
                ),
            }

            logger.info("✅ 산업 구조 분석 완료!")
            return result

        except Exception as e:
            logger.error(f"❌ 산업 구조 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    def analyze_competitive_landscape(
        self, company_data: Dict[str, Any], competitors_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        경쟁 구도 분석

        Args:
            company_data: 대상 기업 데이터
            competitors_data: 경쟁사 데이터 리스트

        Returns:
            Dict: 경쟁 구도 분석 결과
        """
        try:
            logger.info("🔍 경쟁 구도 분석 시작...")

            # 시장 점유율 분석
            market_share_analysis = self._analyze_market_share(
                company_data, competitors_data
            )

            # 경쟁사 포지셔닝 분석
            positioning_analysis = self._analyze_competitor_positioning(
                competitors_data
            )

            # 경쟁 우위 분석
            competitive_advantage = self._analyze_competitive_advantage(
                company_data, competitors_data
            )

            # 경쟁 강도 분석
            competitive_intensity = self._analyze_competitive_intensity(
                competitors_data
            )

            result = {
                "success": True,
                "market_share_analysis": market_share_analysis,
                "positioning_analysis": positioning_analysis,
                "competitive_advantage": competitive_advantage,
                "competitive_intensity": competitive_intensity,
                "competitive_strategy": self._suggest_competitive_strategy(
                    competitive_advantage, positioning_analysis
                ),
            }

            logger.info("✅ 경쟁 구도 분석 완료!")
            return result

        except Exception as e:
            logger.error(f"❌ 경쟁 구도 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    def analyze_industry_lifecycle(
        self, industry_data: Dict[str, Any], historical_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        산업 생명주기 분석

        Args:
            industry_data: 현재 산업 데이터
            historical_data: 과거 산업 데이터 리스트

        Returns:
            Dict: 산업 생명주기 분석 결과
        """
        try:
            logger.info("🔍 산업 생명주기 분석 시작...")

            # 성장률 분석
            growth_analysis = self._analyze_growth_patterns(historical_data)

            # 시장 성숙도 분석
            maturity_analysis = self._analyze_market_maturity(
                industry_data, historical_data
            )

            # 기술 혁신 분석
            innovation_analysis = self._analyze_technology_innovation(industry_data)

            # 생명주기 단계 판단
            lifecycle_stage = self._determine_lifecycle_stage(
                growth_analysis, maturity_analysis, innovation_analysis
            )

            result = {
                "success": True,
                "lifecycle_stage": lifecycle_stage,
                "growth_analysis": growth_analysis,
                "maturity_analysis": maturity_analysis,
                "innovation_analysis": innovation_analysis,
                "future_outlook": self._predict_industry_future(
                    lifecycle_stage, growth_analysis
                ),
                "investment_timing": self._assess_investment_timing(lifecycle_stage),
            }

            logger.info(f"✅ 산업 생명주기 분석 완료: {lifecycle_stage['stage']}")
            return result

        except Exception as e:
            logger.error(f"❌ 산업 생명주기 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    def analyze_industry_trends(
        self, industry_data: Dict[str, Any], market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        산업 트렌드 분석

        Args:
            industry_data: 산업 데이터
            market_data: 시장 데이터

        Returns:
            Dict: 산업 트렌드 분석 결과
        """
        try:
            logger.info("🔍 산업 트렌드 분석 시작...")

            # 기술 트렌드 분석
            technology_trends = self._analyze_technology_trends(industry_data)

            # 소비자 트렌드 분석
            consumer_trends = self._analyze_consumer_trends(market_data)

            # 규제 트렌드 분석
            regulatory_trends = self._analyze_regulatory_trends(industry_data)

            # 글로벌 트렌드 분석
            global_trends = self._analyze_global_trends(industry_data)

            result = {
                "success": True,
                "technology_trends": technology_trends,
                "consumer_trends": consumer_trends,
                "regulatory_trends": regulatory_trends,
                "global_trends": global_trends,
                "trend_impact": self._assess_trend_impact(
                    technology_trends, consumer_trends, regulatory_trends
                ),
                "adaptation_strategy": self._suggest_adaptation_strategy(
                    technology_trends, consumer_trends
                ),
            }

            logger.info("✅ 산업 트렌드 분석 완료!")
            return result

        except Exception as e:
            logger.error(f"❌ 산업 트렌드 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    def _analyze_five_forces(
        self, company_data: Dict[str, Any], industry_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """5 Forces Model 분석"""

        # 기존 경쟁자 분석
        existing_competition = {
            "intensity": self._assess_competition_intensity(industry_data),
            "factors": ["시장 포화도", "성장률", "제품 차별화", "고정비용"],
            "threat_level": "중간",  # 실제로는 더 정교한 계산 필요
        }

        # 신규 진입자 분석
        new_entrants = {
            "barriers": self._assess_entry_barriers(industry_data),
            "factors": ["자본 요구량", "규제 장벽", "브랜드 충성도", "경제적 규모"],
            "threat_level": "낮음",
        }

        # 대체재 분석
        substitutes = {
            "availability": self._assess_substitute_availability(industry_data),
            "factors": ["대체재 가격", "전환 비용", "성능 차이"],
            "threat_level": "중간",
        }

        # 공급자 협상력 분석
        supplier_power = {
            "concentration": self._assess_supplier_concentration(industry_data),
            "factors": ["공급자 집중도", "전환 비용", "차별화 정도"],
            "threat_level": "낮음",
        }

        # 구매자 협상력 분석
        buyer_power = {
            "concentration": self._assess_buyer_concentration(industry_data),
            "factors": ["구매자 집중도", "구매량", "전환 비용"],
            "threat_level": "높음",
        }

        return {
            "existing_competition": existing_competition,
            "new_entrants": new_entrants,
            "substitutes": substitutes,
            "supplier_power": supplier_power,
            "buyer_power": buyer_power,
        }

    def _analyze_industry_concentration(
        self, industry_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """산업 집중도 분석"""

        # HHI (Herfindahl-Hirschman Index) 계산
        market_shares = industry_data.get("market_shares", [])
        hhi = sum([share**2 for share in market_shares]) if market_shares else 0

        concentration_level = "높음" if hhi > 2500 else "중간" if hhi > 1500 else "낮음"

        return {
            "hhi_index": hhi,
            "concentration_level": concentration_level,
            "interpretation": self._interpret_concentration(hhi),
            "market_structure": self._classify_market_structure(hhi),
        }

    def _analyze_entry_barriers(self, industry_data: Dict[str, Any]) -> Dict[str, Any]:
        """진입장벽 분석"""

        barriers = {
            "capital_requirements": industry_data.get("capital_intensity", "중간"),
            "regulatory_barriers": industry_data.get("regulatory_complexity", "높음"),
            "brand_loyalty": industry_data.get("brand_loyalty", "중간"),
            "economies_of_scale": industry_data.get("scale_advantages", "높음"),
            "switching_costs": industry_data.get("switching_costs", "낮음"),
        }

        overall_barrier = self._calculate_overall_barrier(barriers)

        return {
            "barriers": barriers,
            "overall_barrier_level": overall_barrier,
            "interpretation": self._interpret_entry_barriers(overall_barrier),
        }

    def _analyze_industry_profitability(
        self, industry_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """산업 수익성 분석"""

        avg_roa = industry_data.get("average_roa", 0)
        avg_roe = industry_data.get("average_roe", 0)
        avg_margin = industry_data.get("average_margin", 0)

        profitability_level = self._assess_profitability_level(
            avg_roa, avg_roe, avg_margin
        )

        return {
            "average_roa": avg_roa,
            "average_roe": avg_roe,
            "average_margin": avg_margin,
            "profitability_level": profitability_level,
            "drivers": self._identify_profitability_drivers(industry_data),
            "sustainability": self._assess_profitability_sustainability(industry_data),
        }

    def _analyze_market_share(
        self, company_data: Dict[str, Any], competitors_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """시장 점유율 분석"""

        company_share = company_data.get("market_share", 0)
        total_market = (
            sum([comp.get("market_share", 0) for comp in competitors_data])
            + company_share
        )

        if total_market > 0:
            relative_share = company_share / total_market
        else:
            relative_share = 0

        return {
            "company_market_share": company_share,
            "relative_market_share": relative_share,
            "market_position": self._classify_market_position(relative_share),
            "competitors_ranking": self._rank_competitors(competitors_data),
        }

    def _analyze_competitor_positioning(
        self, competitors_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """경쟁사 포지셔닝 분석"""

        positioning_map = {}
        for comp in competitors_data:
            positioning_map[comp.get("name", "Unknown")] = {
                "price_position": comp.get("price_position", "중간"),
                "quality_position": comp.get("quality_position", "중간"),
                "service_position": comp.get("service_position", "중간"),
                "target_segment": comp.get("target_segment", "일반"),
            }

        return {
            "positioning_map": positioning_map,
            "market_gaps": self._identify_market_gaps(positioning_map),
            "opportunity_areas": self._find_opportunity_areas(positioning_map),
        }

    def _analyze_competitive_advantage(
        self, company_data: Dict[str, Any], competitors_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """경쟁 우위 분석"""

        advantages = {
            "cost_advantage": self._assess_cost_advantage(
                company_data, competitors_data
            ),
            "differentiation_advantage": self._assess_differentiation_advantage(
                company_data, competitors_data
            ),
            "technology_advantage": self._assess_technology_advantage(
                company_data, competitors_data
            ),
            "brand_advantage": self._assess_brand_advantage(
                company_data, competitors_data
            ),
        }

        overall_advantage = self._calculate_overall_advantage(advantages)

        return {
            "advantages": advantages,
            "overall_advantage": overall_advantage,
            "sustainability": self._assess_advantage_sustainability(advantages),
            "recommendations": self._suggest_advantage_improvements(advantages),
        }

    def _analyze_growth_patterns(
        self, historical_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """성장 패턴 분석"""

        if not historical_data or len(historical_data) < 2:
            return {"growth_rate": 0, "pattern": "데이터 부족", "volatility": 0}

        # 성장률 계산
        growth_rates = []
        for i in range(1, len(historical_data)):
            current = historical_data[i].get("revenue", 0)
            previous = historical_data[i - 1].get("revenue", 0)
            if previous > 0:
                growth_rate = ((current - previous) / previous) * 100
                growth_rates.append(growth_rate)

        avg_growth = np.mean(growth_rates) if growth_rates else 0
        volatility = np.std(growth_rates) if growth_rates else 0

        return {
            "average_growth_rate": avg_growth,
            "growth_volatility": volatility,
            "growth_pattern": self._classify_growth_pattern(avg_growth, volatility),
            "trend": self._assess_growth_trend(growth_rates),
        }

    def _analyze_market_maturity(
        self, industry_data: Dict[str, Any], historical_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """시장 성숙도 분석"""

        # 시장 포화도 지표들
        penetration_rate = industry_data.get("market_penetration", 0)
        growth_rate = industry_data.get("growth_rate", 0)
        consolidation_level = industry_data.get("consolidation_level", 0)

        maturity_score = self._calculate_maturity_score(
            penetration_rate, growth_rate, consolidation_level
        )
        maturity_level = self._classify_maturity_level(maturity_score)

        return {
            "maturity_score": maturity_score,
            "maturity_level": maturity_level,
            "penetration_rate": penetration_rate,
            "consolidation_level": consolidation_level,
            "characteristics": self._describe_maturity_characteristics(maturity_level),
        }

    def _analyze_technology_innovation(
        self, industry_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """기술 혁신 분석"""

        innovation_indicators = {
            "rd_intensity": industry_data.get("rd_intensity", 0),
            "patent_growth": industry_data.get("patent_growth", 0),
            "technology_cycle": industry_data.get("technology_cycle", "중간"),
            "disruption_risk": industry_data.get("disruption_risk", "낮음"),
        }

        innovation_level = self._assess_innovation_level(innovation_indicators)

        return {
            "innovation_indicators": innovation_indicators,
            "innovation_level": innovation_level,
            "disruption_potential": self._assess_disruption_potential(
                innovation_indicators
            ),
            "adaptation_urgency": self._assess_adaptation_urgency(innovation_level),
        }

    def _determine_lifecycle_stage(
        self, growth_analysis: Dict, maturity_analysis: Dict, innovation_analysis: Dict
    ) -> Dict[str, Any]:
        """생명주기 단계 판단"""

        growth_rate = growth_analysis.get("average_growth_rate", 0)
        maturity_score = maturity_analysis.get("maturity_score", 0)
        innovation_level = innovation_analysis.get("innovation_level", "낮음")

        if growth_rate > 20 and maturity_score < 30:
            stage = "도입기"
        elif growth_rate > 10 and maturity_score < 60:
            stage = "성장기"
        elif growth_rate > 0 and maturity_score < 80:
            stage = "성숙기"
        else:
            stage = "쇠퇴기"

        return {
            "stage": stage,
            "confidence": self._calculate_stage_confidence(
                growth_rate, maturity_score, innovation_level
            ),
            "characteristics": self._describe_stage_characteristics(stage),
            "duration_estimate": self._estimate_stage_duration(stage),
        }

    # 헬퍼 메서드들
    def _assess_industry_attractiveness(
        self, five_forces: Dict, concentration: Dict, barriers: Dict
    ) -> Dict[str, Any]:
        """산업 매력도 종합 평가"""
        attractiveness_score = 0

        # 5 Forces 평가
        if five_forces["existing_competition"]["threat_level"] == "낮음":
            attractiveness_score += 20
        elif five_forces["existing_competition"]["threat_level"] == "중간":
            attractiveness_score += 10

        # 진입장벽 평가
        if barriers["overall_barrier_level"] == "높음":
            attractiveness_score += 20
        elif barriers["overall_barrier_level"] == "중간":
            attractiveness_score += 10

        attractiveness_level = (
            "높음"
            if attractiveness_score >= 30
            else "중간" if attractiveness_score >= 15 else "낮음"
        )

        return {
            "attractiveness_score": attractiveness_score,
            "attractiveness_level": attractiveness_level,
            "key_factors": self._identify_attractiveness_factors(five_forces, barriers),
        }

    def _derive_strategic_implications(
        self, five_forces: Dict, concentration: Dict
    ) -> Dict[str, Any]:
        """전략적 시사점 도출"""
        implications = []

        if five_forces["buyer_power"]["threat_level"] == "높음":
            implications.append("구매자 협상력이 높으므로 차별화 전략 필요")

        if concentration["concentration_level"] == "높음":
            implications.append("시장 집중도가 높으므로 포지셔닝 전략 중요")

        return {
            "implications": implications,
            "priority_actions": self._suggest_priority_actions(implications),
        }

    def _suggest_competitive_strategy(
        self, advantage: Dict, positioning: Dict
    ) -> Dict[str, Any]:
        """경쟁 전략 제안"""
        strategies = []

        if advantage["overall_advantage"] == "높음":
            strategies.append("현재 우위 유지 및 강화")
        else:
            strategies.append("차별화 또는 원가 우위 확보")

        return {
            "recommended_strategies": strategies,
            "implementation_priority": self._prioritize_strategies(strategies),
        }

    def _predict_industry_future(self, lifecycle: Dict, growth: Dict) -> Dict[str, Any]:
        """산업 미래 전망"""
        stage = lifecycle["stage"]

        if stage == "도입기":
            outlook = "높은 성장 잠재력, 혁신 기회 많음"
        elif stage == "성장기":
            outlook = "안정적 성장, 시장 확대 기회"
        elif stage == "성숙기":
            outlook = "안정적 수익, 효율성 중시"
        else:
            outlook = "성장 한계, 혁신 필요"

        return {
            "outlook": outlook,
            "time_horizon": "3-5년",
            "key_drivers": self._identify_future_drivers(stage),
        }

    def _assess_investment_timing(self, lifecycle: Dict) -> Dict[str, Any]:
        """투자 타이밍 평가"""
        stage = lifecycle["stage"]

        if stage == "성장기":
            timing = "최적"
            risk_level = "중간"
        elif stage == "도입기":
            timing = "고위험 고수익"
            risk_level = "높음"
        elif stage == "성숙기":
            timing = "안정적"
            risk_level = "낮음"
        else:
            timing = "회피 권장"
            risk_level = "매우 높음"

        return {
            "timing": timing,
            "risk_level": risk_level,
            "expected_return": self._estimate_expected_return(stage),
        }

    # 해석 및 분류 헬퍼 메서드들
    def _interpret_concentration(self, hhi: float) -> str:
        if hhi > 2500:
            return "높은 시장 집중도로 과점 구조"
        elif hhi > 1500:
            return "중간 수준의 시장 집중도"
        else:
            return "낮은 시장 집중도로 경쟁적 구조"

    def _classify_market_structure(self, hhi: float) -> str:
        if hhi > 2500:
            return "과점"
        elif hhi > 1500:
            return "집중적 과점"
        else:
            return "경쟁적"

    def _calculate_overall_barrier(self, barriers: Dict) -> str:
        high_count = sum(1 for v in barriers.values() if v == "높음")
        if high_count >= 3:
            return "높음"
        elif high_count >= 1:
            return "중간"
        else:
            return "낮음"

    def _interpret_entry_barriers(self, barrier_level: str) -> str:
        if barrier_level == "높음":
            return "신규 진입이 어려운 구조"
        elif barrier_level == "중간":
            return "신규 진입이 보통 수준"
        else:
            return "신규 진입이 상대적으로 쉬운 구조"

    def _assess_profitability_level(self, roa: float, roe: float, margin: float) -> str:
        if roa > 15 and roe > 20 and margin > 20:
            return "매우 높음"
        elif roa > 10 and roe > 15 and margin > 15:
            return "높음"
        elif roa > 5 and roe > 10 and margin > 10:
            return "중간"
        else:
            return "낮음"

    def _classify_market_position(self, relative_share: float) -> str:
        if relative_share > 1.5:
            return "시장 리더"
        elif relative_share > 1.0:
            return "시장 2위"
        elif relative_share > 0.5:
            return "시장 추종자"
        else:
            return "니치 플레이어"

    def _classify_growth_pattern(self, avg_growth: float, volatility: float) -> str:
        if avg_growth > 15:
            return "고성장"
        elif avg_growth > 5:
            return "안정성장"
        elif avg_growth > 0:
            return "저성장"
        else:
            return "성장 정체"

    def _calculate_maturity_score(
        self, penetration: float, growth: float, consolidation: float
    ) -> float:
        # 성숙도 점수 계산 (0-100)
        score = (
            (penetration * 0.4) + (max(0, 20 - growth) * 0.3) + (consolidation * 0.3)
        )
        return min(100, max(0, score))

    def _classify_maturity_level(self, score: float) -> str:
        if score > 80:
            return "매우 성숙"
        elif score > 60:
            return "성숙"
        elif score > 40:
            return "성장"
        else:
            return "초기"

    def _assess_innovation_level(self, indicators: Dict) -> str:
        rd_intensity = indicators["rd_intensity"]
        patent_growth = indicators["patent_growth"]

        if rd_intensity > 10 and patent_growth > 20:
            return "매우 높음"
        elif rd_intensity > 5 and patent_growth > 10:
            return "높음"
        elif rd_intensity > 2 and patent_growth > 5:
            return "중간"
        else:
            return "낮음"

    def _describe_stage_characteristics(self, stage: str) -> List[str]:
        characteristics = {
            "도입기": ["높은 혁신", "불확실성", "초기 투자 필요"],
            "성장기": ["빠른 성장", "시장 확대", "경쟁 심화"],
            "성숙기": ["안정적 성장", "효율성 중시", "차별화 중요"],
            "쇠퇴기": ["성장 정체", "혁신 필요", "전략적 재검토"],
        }
        return characteristics.get(stage, [])

    def _estimate_stage_duration(self, stage: str) -> str:
        durations = {
            "도입기": "2-5년",
            "성장기": "5-15년",
            "성숙기": "10-30년",
            "쇠퇴기": "변동적",
        }
        return durations.get(stage, "불확실")

    def _calculate_stage_confidence(
        self, growth: float, maturity: float, innovation: str
    ) -> str:
        # 신뢰도 계산 로직
        if abs(growth) < 5 and maturity > 50:
            return "높음"
        elif abs(growth) < 10 and maturity > 30:
            return "중간"
        else:
            return "낮음"

    def _identify_attractiveness_factors(
        self, five_forces: Dict, barriers: Dict
    ) -> List[str]:
        factors = []
        if five_forces["existing_competition"]["threat_level"] == "낮음":
            factors.append("낮은 기존 경쟁")
        if barriers["overall_barrier_level"] == "높음":
            factors.append("높은 진입장벽")
        return factors

    def _suggest_priority_actions(self, implications: List[str]) -> List[str]:
        actions = []
        for implication in implications:
            if "차별화" in implication:
                actions.append("브랜드 강화 및 서비스 개선")
            if "포지셔닝" in implication:
                actions.append("시장 세분화 및 타겟팅")
        return actions

    def _prioritize_strategies(self, strategies: List[str]) -> List[str]:
        # 전략 우선순위 결정
        return strategies  # 실제로는 더 정교한 로직 필요

    def _identify_future_drivers(self, stage: str) -> List[str]:
        drivers = {
            "도입기": ["기술 혁신", "시장 교육", "규제 변화"],
            "성장기": ["시장 확대", "기술 발전", "소비자 수용"],
            "성숙기": ["효율성", "차별화", "국제화"],
            "쇠퇴기": ["혁신", "다각화", "전략적 재정비"],
        }
        return drivers.get(stage, [])

    def _estimate_expected_return(self, stage: str) -> str:
        returns = {
            "도입기": "매우 높음 (고위험)",
            "성장기": "높음",
            "성숙기": "중간",
            "쇠퇴기": "낮음",
        }
        return returns.get(stage, "불확실")

    # 추가 헬퍼 메서드들 (실제 구현에서는 더 정교한 로직 필요)
    def _assess_competition_intensity(self, industry_data: Dict[str, Any]) -> str:
        return "중간"  # 실제로는 더 정교한 계산 필요

    def _assess_entry_barriers(self, industry_data: Dict[str, Any]) -> str:
        return "중간"

    def _assess_substitute_availability(self, industry_data: Dict[str, Any]) -> str:
        return "중간"

    def _assess_supplier_concentration(self, industry_data: Dict[str, Any]) -> str:
        return "낮음"

    def _assess_buyer_concentration(self, industry_data: Dict[str, Any]) -> str:
        return "높음"

    def _rank_competitors(
        self, competitors_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        return sorted(
            competitors_data, key=lambda x: x.get("market_share", 0), reverse=True
        )

    def _identify_market_gaps(self, positioning_map: Dict) -> List[str]:
        return ["프리미엄 세그먼트", "저가 세그먼트"]

    def _find_opportunity_areas(self, positioning_map: Dict) -> List[str]:
        return ["서비스 강화", "가격 경쟁력"]

    def _assess_cost_advantage(
        self, company_data: Dict[str, Any], competitors_data: List[Dict[str, Any]]
    ) -> str:
        return "중간"

    def _assess_differentiation_advantage(
        self, company_data: Dict[str, Any], competitors_data: List[Dict[str, Any]]
    ) -> str:
        return "높음"

    def _assess_technology_advantage(
        self, company_data: Dict[str, Any], competitors_data: List[Dict[str, Any]]
    ) -> str:
        return "중간"

    def _assess_brand_advantage(
        self, company_data: Dict[str, Any], competitors_data: List[Dict[str, Any]]
    ) -> str:
        return "높음"

    def _calculate_overall_advantage(self, advantages: Dict) -> str:
        high_count = sum(1 for v in advantages.values() if v == "높음")
        if high_count >= 2:
            return "높음"
        elif high_count >= 1:
            return "중간"
        else:
            return "낮음"

    def _assess_advantage_sustainability(self, advantages: Dict) -> str:
        return "중간"

    def _suggest_advantage_improvements(self, advantages: Dict) -> List[str]:
        return ["기술 투자 확대", "브랜드 강화"]

    def _analyze_competitive_intensity(
        self, competitors_data: List[Dict[str, Any]]
    ) -> str:
        return "중간"

    def _assess_growth_trend(self, growth_rates: List[float]) -> str:
        if not growth_rates:
            return "불확실"
        if len(growth_rates) >= 2:
            if growth_rates[-1] > growth_rates[0]:
                return "가속화"
            elif growth_rates[-1] < growth_rates[0]:
                return "감속화"
        return "안정적"

    def _describe_maturity_characteristics(self, maturity_level: str) -> List[str]:
        characteristics = {
            "매우 성숙": ["높은 포화도", "낮은 성장률", "높은 집중도"],
            "성숙": ["중간 포화도", "안정적 성장", "중간 집중도"],
            "성장": ["낮은 포화도", "높은 성장률", "낮은 집중도"],
            "초기": ["매우 낮은 포화도", "매우 높은 성장률", "매우 낮은 집중도"],
        }
        return characteristics.get(maturity_level, [])

    def _assess_disruption_potential(self, indicators: Dict) -> str:
        if indicators["disruption_risk"] == "높음":
            return "높음"
        elif indicators["technology_cycle"] == "빠름":
            return "중간"
        else:
            return "낮음"

    def _assess_adaptation_urgency(self, innovation_level: str) -> str:
        if innovation_level in ["매우 높음", "높음"]:
            return "높음"
        else:
            return "중간"

    def _identify_profitability_drivers(
        self, industry_data: Dict[str, Any]
    ) -> List[str]:
        return ["규모의 경제", "차별화", "진입장벽"]

    def _assess_profitability_sustainability(
        self, industry_data: Dict[str, Any]
    ) -> str:
        return "중간"

    def _analyze_technology_trends(
        self, industry_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "emerging_technologies": ["AI", "IoT", "블록체인"],
            "adoption_rate": "중간",
            "impact_level": "높음",
        }

    def _analyze_consumer_trends(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "preference_changes": ["디지털화", "개인화", "지속가능성"],
            "adoption_speed": "빠름",
            "impact_level": "높음",
        }

    def _analyze_regulatory_trends(
        self, industry_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "regulatory_changes": ["환경규제", "데이터보호", "소비자보호"],
            "compliance_cost": "중간",
            "impact_level": "중간",
        }

    def _analyze_global_trends(self, industry_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "global_developments": ["글로벌화", "지역화", "디지털 전환"],
            "impact_level": "높음",
            "opportunities": ["신시장 진출", "기술 협력"],
        }

    def _assess_trend_impact(
        self, tech_trends: Dict, consumer_trends: Dict, regulatory_trends: Dict
    ) -> Dict[str, Any]:
        return {
            "overall_impact": "높음",
            "positive_factors": ["기술 혁신", "소비자 수용"],
            "negative_factors": ["규제 부담"],
            "adaptation_required": True,
        }

    def _suggest_adaptation_strategy(
        self, tech_trends: Dict, consumer_trends: Dict
    ) -> Dict[str, Any]:
        return {
            "technology_investment": "확대",
            "consumer_engagement": "강화",
            "digital_transformation": "가속화",
        }
