# -*- coding: utf-8 -*-
"""
전문가 분석 통합 도구

이 파일은 모든 전문가 도구들을 하나로 모아서 쉽게 사용할 수 있게 해주는 통합 도구예요.
각 전문가(펀더멘털, 기술적, 밸류에이션, 산업, 리스크, 주석)의 특화 기능을 한 번에 호출할 수 있어요!

# [3단계 확장] 리스크 분석 시 산업/주석 결과를 참고할 수 있도록 구조를 확장했어요.
"""

import asyncio
from typing import Any, Dict, List, Optional

from app.logger import logger
from app.tool.footnote_analysis_tools import FootnoteAnalysisTools

# 🚀 모든 전문가 도구들을 가져와요
from app.tool.fundamental_analysis_tools import FundamentalAnalysisTools
from app.tool.industry_analysis_tools import IndustryAnalysisTools
from app.tool.risk_analysis_tools import RiskAnalysisTools
from app.tool.technical_analysis_tools import TechnicalAnalysisTools
from app.tool.valuation_analysis_tools import ValuationAnalysisTools


class ExpertAnalysisIntegration:
    """
    모든 전문가 도구들을 통합해서 사용할 수 있는 클래스예요.
    각 전문가의 특화 기능을 쉽게 호출할 수 있어요!
    """

    def __init__(self):
        """통합 도구 초기화 - 모든 전문가 도구들을 준비해요"""
        logger.info("🚀 전문가 분석 통합 도구 초기화 시작...")

        # 각 전문가 도구들을 만들어요
        self.fundamental_expert = FundamentalAnalysisTools()
        self.technical_expert = TechnicalAnalysisTools()
        self.valuation_expert = ValuationAnalysisTools()
        self.industry_expert = IndustryAnalysisTools()
        self.risk_expert = RiskAnalysisTools()
        self.footnote_expert = FootnoteAnalysisTools()

        logger.info("✅ 모든 전문가 도구 초기화 완료!")

    def analyze_fundamental(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        펀더멘털 전문가에게 재무 분석을 맡겨요
        Args:
            financial_data: 재무 데이터 (예: yfinance, DART API 데이터)
        Returns:
            Dict: 펀더멘털 분석 결과
        """
        try:
            logger.info("📊 펀더멘털 전문가 분석 시작...")

            # ROIC 추세 분석
            roic_analysis = self.fundamental_expert.calculate_roic_trend(financial_data)

            # ROE 해체 분석
            roe_analysis = self.fundamental_expert.calculate_roe_decomposition(
                financial_data
            )

            # 수익성 지표 분석
            profitability_analysis = (
                self.fundamental_expert.calculate_profitability_metrics(financial_data)
            )

            # 인과관계 체인 분석
            causality_analysis = self.fundamental_expert.analyze_causality_chain(
                financial_data
            )

            result = {
                "success": True,
                "expert_type": "펀더멘털 전문가",
                "roic_analysis": roic_analysis,
                "roe_analysis": roe_analysis,
                "profitability_analysis": profitability_analysis,
                "causality_analysis": causality_analysis,
                "summary": "재무 건전성과 수익성을 종합적으로 분석했어요",
            }

            logger.info("✅ 펀더멘털 분석 완료!")
            return result

        except Exception as e:
            logger.error(f"❌ 펀더멘털 분석 실패: {e}")
            return {"success": False, "error": str(e), "expert_type": "펀더멘털 전문가"}

    def analyze_technical(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        기술적 전문가에게 시장 분석을 맡겨요
        Args:
            market_data: 시장 데이터 (예: 주가, 거래량 등)
        Returns:
            Dict: 기술적 분석 결과
        """
        try:
            logger.info("📈 기술적 전문가 분석 시작...")

            # 기술적 지표 분석
            technical_indicators = self.technical_expert.analyze_technical_indicators(
                market_data
            )

            # 차트 패턴 분석
            chart_patterns = self.technical_expert.analyze_chart_patterns(market_data)

            # 추세 분석
            trend_analysis = self.technical_expert.analyze_trends(market_data)

            # 지지/저항 분석
            support_resistance = self.technical_expert.analyze_support_resistance(
                market_data
            )

            result = {
                "success": True,
                "expert_type": "기술적 전문가",
                "technical_indicators": technical_indicators,
                "chart_patterns": chart_patterns,
                "trend_analysis": trend_analysis,
                "support_resistance": support_resistance,
                "summary": "주가 움직임과 시장 패턴을 분석했어요",
            }

            logger.info("✅ 기술적 분석 완료!")
            return result

        except Exception as e:
            logger.error(f"❌ 기술적 분석 실패: {e}")
            return {"success": False, "error": str(e), "expert_type": "기술적 전문가"}

    def analyze_valuation(
        self, financial_data: Dict[str, Any], market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        밸류에이션 전문가에게 기업 가치 분석을 맡겨요
        Args:
            financial_data: 재무 데이터
            market_data: 시장 데이터
        Returns:
            Dict: 밸류에이션 분석 결과
        """
        try:
            logger.info("💰 밸류에이션 전문가 분석 시작...")

            # DCF 모델 분석
            dcf_analysis = self.valuation_expert.perform_dcf_analysis(financial_data)

            # 상대가치 분석
            relative_valuation = self.valuation_expert.perform_relative_valuation(
                financial_data, market_data
            )

            # 자산가치 분석
            asset_based_valuation = self.valuation_expert.perform_asset_based_valuation(
                financial_data
            )

            # 종합 가치 평가
            comprehensive_valuation = (
                self.valuation_expert.perform_comprehensive_valuation(
                    financial_data, market_data
                )
            )

            result = {
                "success": True,
                "expert_type": "밸류에이션 전문가",
                "dcf_analysis": dcf_analysis,
                "relative_valuation": relative_valuation,
                "asset_based_valuation": asset_based_valuation,
                "comprehensive_valuation": comprehensive_valuation,
                "summary": "기업의 내재가치와 투자 가치를 종합적으로 평가했어요",
            }

            logger.info("✅ 밸류에이션 분석 완료!")
            return result

        except Exception as e:
            logger.error(f"❌ 밸류에이션 분석 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "expert_type": "밸류에이션 전문가",
            }

    def analyze_industry(
        self, company_data: Dict[str, Any], industry_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        산업 전문가에게 산업 분석을 맡겨요
        Args:
            company_data: 대상 기업 데이터
            industry_data: 산업 전체 데이터
        Returns:
            Dict: 산업 분석 결과
        """
        try:
            logger.info("🏭 산업 전문가 분석 시작...")

            # 산업 구조 분석
            industry_structure = self.industry_expert.analyze_industry_structure(
                company_data, industry_data
            )

            # 경쟁 구도 분석
            competitive_landscape = self.industry_expert.analyze_competitive_landscape(
                company_data, industry_data.get("competitors", [])
            )

            # 산업 생명주기 분석
            lifecycle_analysis = self.industry_expert.analyze_industry_lifecycle(
                industry_data, industry_data.get("historical_data", [])
            )

            # 산업 트렌드 분석
            trend_analysis = self.industry_expert.analyze_industry_trends(
                industry_data, industry_data
            )

            result = {
                "success": True,
                "expert_type": "산업 전문가",
                "industry_structure": industry_structure,
                "competitive_landscape": competitive_landscape,
                "lifecycle_analysis": lifecycle_analysis,
                "trend_analysis": trend_analysis,
                "summary": "산업 구조와 경쟁 환경을 종합적으로 분석했어요",
                "risk_signals": self._extract_industry_risk_signals(
                    industry_structure,
                    competitive_landscape,
                    lifecycle_analysis,
                    trend_analysis,
                ),
            }

            logger.info("✅ 산업 분석 완료!")
            return result

        except Exception as e:
            logger.error(f"❌ 산업 분석 실패: {e}")
            return {"success": False, "error": str(e), "expert_type": "산업 전문가"}

    def analyze_risk(
        self,
        financial_data: Dict[str, Any],
        market_data: Dict[str, Any],
        operation_data: Dict[str, Any],
        industry_result: Optional[Dict[str, Any]] = None,
        footnote_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        리스크 전문가에게 위험 분석을 맡겨요
        Args:
            financial_data: 재무 데이터
            market_data: 시장 데이터
            operation_data: 운영 데이터
            industry_result: 산업 전문가 분석 결과(위험 신호 참고용)
            footnote_result: 주석 전문가 분석 결과(위험 신호 참고용)
        Returns:
            Dict: 리스크 분석 결과
        """
        try:
            logger.info("⚠️ 리스크 전문가 분석 시작...")

            # 재무 리스크 분석
            financial_risk = self.risk_expert.analyze_financial_risk(financial_data)

            # 시장 리스크 분석
            market_risk = self.risk_expert.analyze_market_risk(market_data)

            # 운영 리스크 분석
            operational_risk = self.risk_expert.analyze_operational_risk(operation_data)

            # [확장] 산업/주석 위험 신호를 종합해서 전체 리스크에 반영해요
            extra_risks = []
            if industry_result and industry_result.get("risk_signals"):
                extra_risks.extend(industry_result["risk_signals"])
            if footnote_result and footnote_result.get("risks"):
                extra_risks.extend(footnote_result["risks"])

            # 위험 신호가 있으면 전체 리스크를 한 단계 높게 평가해요
            overall_risk_level = self._combine_risk_levels(
                [
                    financial_risk.get("overall_financial_risk"),
                    market_risk.get("overall_market_risk"),
                    operational_risk.get("overall_operational_risk"),
                ],
                extra_risks,
            )

            result = {
                "success": True,
                "expert_type": "리스크 전문가",
                "financial_risk": financial_risk,
                "market_risk": market_risk,
                "operational_risk": operational_risk,
                "extra_risks": extra_risks,
                "overall_risk_level": overall_risk_level,
                "summary": f"재무, 시장, 운영 리스크와 외부 위험 신호({len(extra_risks)}건)를 종합적으로 평가했어요",
            }

            logger.info("✅ 리스크 분석 완료!")
            return result

        except Exception as e:
            logger.error(f"❌ 리스크 분석 실패: {e}")
            return {"success": False, "error": str(e), "expert_type": "리스크 전문가"}

    def analyze_footnotes(self, footnotes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        주석 전문가에게 주석 분석을 맡겨요
        Args:
            footnotes: 주석 데이터 리스트
        Returns:
            Dict: 주석 분석 결과
        """
        try:
            logger.info("📝 주석 전문가 분석 시작...")

            # 중요한 주석 추출
            important_footnotes = self.footnote_expert.extract_important_footnotes(
                footnotes
            )

            # 주석 요약
            summaries = []
            for footnote in important_footnotes:
                summary = self.footnote_expert.summarize_footnote(footnote)
                summaries.append(summary)

            # 위험 신호 감지
            risks = self.footnote_expert.detect_risk_in_footnotes(footnotes)

            # 정책 변경 감지
            policy_changes = self.footnote_expert.find_policy_changes(footnotes)

            result = {
                "success": True,
                "expert_type": "주석 전문가",
                "important_footnotes": important_footnotes,
                "summaries": summaries,
                "risks": risks,
                "policy_changes": policy_changes,
                "summary": "주석에서 중요한 정보와 위험 신호를 찾아냈어요",
            }

            logger.info("✅ 주석 분석 완료!")
            return result

        except Exception as e:
            logger.error(f"❌ 주석 분석 실패: {e}")
            return {"success": False, "error": str(e), "expert_type": "주석 전문가"}

    async def perform_comprehensive_analysis(
        self, all_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        모든 전문가에게 종합 분석을 맡겨요 (한 번에 모든 분석 수행)
        Args:
            all_data: 모든 데이터 (재무, 시장, 산업, 운영, 주석 등)
        Returns:
            Dict: 모든 전문가의 종합 분석 결과
        """
        try:
            logger.info("🎯 모든 전문가 종합 분석 시작...")

            # 1. 각 전문가별 분석을 동시에 실행해요!
            # asyncio.gather를 사용하면 여러 작업을 한 번에 시작할 수 있어요.
            (
                fundamental_result,
                technical_result,
                valuation_result,
                industry_result,
                footnote_result,
            ) = await asyncio.gather(
                asyncio.to_thread(
                    self.analyze_fundamental, all_data.get("financial_data", {})
                ),
                asyncio.to_thread(
                    self.analyze_technical, all_data.get("market_data", {})
                ),
                asyncio.to_thread(
                    self.analyze_valuation,
                    all_data.get("financial_data", {}),
                    all_data.get("market_data", {}),
                ),
                asyncio.to_thread(
                    self.analyze_industry,
                    all_data.get("company_data", {}),
                    all_data.get("industry_data", {}),
                ),
                asyncio.to_thread(
                    self.analyze_footnotes, all_data.get("footnotes", [])
                ),
            )
            # 리스크 분석은 산업/주석 결과가 필요하니 마지막에 따로 실행해요
            risk_result = await asyncio.to_thread(
                self.analyze_risk,
                all_data.get("financial_data", {}),
                all_data.get("market_data", {}),
                all_data.get("operation_data", {}),
                industry_result=industry_result,
                footnote_result=footnote_result,
            )

            # 3. 종합 결과 정리 (위험 신호도 함께)
            comprehensive_result = {
                "success": True,
                "analysis_timestamp": all_data.get("timestamp", ""),
                "expert_analyses": {
                    "fundamental": fundamental_result,
                    "technical": technical_result,
                    "valuation": valuation_result,
                    "industry": industry_result,
                    "risk": risk_result,
                    "footnote": footnote_result,
                },
                "summary": "모든 전문가의 분석이 완료되었어요!",
                "recommendations": self._generate_integrated_recommendations(
                    [
                        fundamental_result,
                        technical_result,
                        valuation_result,
                        industry_result,
                        risk_result,
                        footnote_result,
                    ],
                    risk_result.get("extra_risks", []),
                ),
            }
            logger.info("✅ 모든 전문가 종합 분석 완료!")
            return comprehensive_result

        except Exception as e:
            logger.error(f"❌ 종합 분석 실패: {e}")
            return {"success": False, "error": str(e)}

    def _extract_industry_risk_signals(
        self,
        industry_structure,
        competitive_landscape,
        lifecycle_analysis,
        trend_analysis,
    ) -> List[str]:
        # 산업 분석 결과에서 위험 신호(예: 진입장벽 낮음, 경쟁 심화 등)를 뽑아내요
        signals = []
        try:
            if (
                industry_structure
                and industry_structure.get("entry_barriers", {}).get(
                    "overall_barrier_level"
                )
                == "낮음"
            ):
                signals.append("진입장벽이 낮아 신규 경쟁자 위험이 높아요.")
            if (
                competitive_landscape
                and competitive_landscape.get("competitive_intensity") == "높음"
            ):
                signals.append("경쟁 강도가 매우 높아요.")
            if (
                lifecycle_analysis
                and lifecycle_analysis.get("lifecycle_stage", {}).get("stage")
                == "쇠퇴기"
            ):
                signals.append("산업이 쇠퇴기에 진입했어요.")
            if (
                trend_analysis
                and trend_analysis.get("trend_impact", {}).get("overall_impact")
                == "높음"
            ):
                signals.append("산업 트렌드 변화가 크니 주의가 필요해요.")
        except Exception:
            pass
        return signals

    def _combine_risk_levels(
        self, risk_levels: List[str], extra_risks: List[str]
    ) -> str:
        # 여러 위험 수준과 외부 위험 신호를 종합해서 최종 위험도를 결정해요
        if extra_risks:
            return "고위험 (외부 위험 신호 감지됨)"
        if "고위험" in risk_levels:
            return "고위험"
        if "중간위험" in risk_levels:
            return "중간위험"
        return "저위험"

    def _generate_integrated_recommendations(
        self, expert_results: List[Dict[str, Any]], extra_risks: List[str]
    ) -> List[str]:
        # 모든 전문가의 분석 결과와 위험 신호를 종합해서 투자 추천을 만들어요
        recommendations = []
        successful_results = [
            result for result in expert_results if result.get("success", False)
        ]
        if not successful_results:
            return ["분석 데이터가 부족해서 구체적인 추천을 드릴 수 없어요."]
        for result in successful_results:
            expert_type = result.get("expert_type", "알 수 없음")
            summary = result.get("summary", "")
            if summary:
                recommendations.append(f"[{expert_type}] {summary}")
        # [확장] 위험 신호가 있으면 별도 경고 메시지 추가
        if extra_risks:
            recommendations.append(
                f"⚠️ 외부 위험 신호 감지: {len(extra_risks)}건. 세부 내용: {extra_risks}"
            )
        if len(successful_results) >= 3:
            recommendations.append(
                "여러 전문가의 분석 결과를 종합해보니, 이 종목에 대한 종합적인 평가가 가능해요."
            )
        else:
            recommendations.append(
                "일부 전문가의 분석만 가능했어요. 더 많은 데이터가 있으면 더 정확한 분석이 가능해요."
            )
        return recommendations
