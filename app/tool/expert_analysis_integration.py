# -*- coding: utf-8 -*-
"""
전문가 분석 통합 도구

이 파일은 모든 전문가 도구들을 하나로 모아서 쉽게 사용할 수 있게 해주는 통합 도구예요.
각 전문가(펀더멘털, 기술적, 밸류에이션, 산업, 리스크, 주석)의 특화 기능을 한 번에 호출할 수 있어요!

# [3단계 확장] 리스크 분석 시 산업/주석 결과를 참고할 수 있도록 구조를 확장했어요.
"""

import asyncio
from datetime import datetime
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
        ⚠️ 중요: 실제 계산된 데이터를 우선적으로 사용하고, 가정값은 보조적으로만 사용해요!

        Args:
            financial_data: 재무 데이터 (예: yfinance, DART API 데이터)
        Returns:
            Dict: 펀더멘털 분석 결과
        """
        try:
            logger.info("📊 펀더멘털 전문가 분석 시작...")

            # 🎯 데이터 일관성 보장: 실제 계산된 값들을 먼저 추출
            calculated_metrics = self._extract_calculated_metrics(financial_data)

            # 실제 계산된 ROIC가 있으면 사용, 없으면 계산
            if calculated_metrics.get("roic") is not None:
                roic_value = calculated_metrics["roic"]
                logger.info(f"📊 실제 계산된 ROIC 사용: {roic_value}%")
            else:
                roic_analysis = self.fundamental_expert.calculate_roic_trend(
                    financial_data
                )
                roic_value = (
                    roic_analysis.get("roic", 0) if roic_analysis.get("success") else 0
                )
                logger.info(f"📊 새로 계산된 ROIC: {roic_value}%")

            # 실제 계산된 ROE가 있으면 사용, 없으면 계산
            if calculated_metrics.get("roe") is not None:
                roe_value = calculated_metrics["roe"]
                logger.info(f"📊 실제 계산된 ROE 사용: {roe_value}%")
            else:
                roe_analysis = self.fundamental_expert.calculate_roe_decomposition(
                    financial_data
                )
                roe_value = (
                    roe_analysis.get("roe", 0) if roe_analysis.get("success") else 0
                )
                logger.info(f"📊 새로 계산된 ROE: {roe_value}%")

            # ROIC 추세 분석 (실제 계산된 값 사용)
            roic_analysis = self.fundamental_expert.calculate_roic_trend(financial_data)
            if roic_analysis.get("success"):
                roic_analysis["roic"] = roic_value  # 일관성 보장

            # ROE 해체 분석 (실제 계산된 값 사용)
            roe_analysis = self.fundamental_expert.calculate_roe_decomposition(
                financial_data
            )
            if roe_analysis.get("success"):
                roe_analysis["roe"] = roe_value  # 일관성 보장

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
                "calculated_metrics": calculated_metrics,  # 실제 계산된 값들
                "roic_analysis": roic_analysis,
                "roe_analysis": roe_analysis,
                "profitability_analysis": profitability_analysis,
                "causality_analysis": causality_analysis,
                "summary": f"재무 건전성과 수익성을 종합적으로 분석했어요 (ROIC: {roic_value}%, ROE: {roe_value}%)",
                "data_source": "실제 계산된 데이터 우선 사용",
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
        ⚠️ 중요: 실제 계산된 데이터를 우선적으로 사용하고, 가정값은 보조적으로만 사용해요!

        Args:
            financial_data: 재무 데이터
            market_data: 시장 데이터
        Returns:
            Dict: 밸류에이션 분석 결과
        """
        try:
            logger.info("💰 밸류에이션 전문가 분석 시작...")

            # 🎯 데이터 일관성 보장: 실제 계산된 값들을 먼저 추출
            calculated_metrics = self._extract_calculated_metrics(financial_data)

            # 실제 계산된 ROIC와 WACC가 있으면 사용
            roic_value = calculated_metrics.get("roic")
            wacc_value = calculated_metrics.get("wacc")

            if roic_value is not None and wacc_value is not None:
                logger.info(
                    f"💰 실제 계산된 ROIC: {roic_value}%, WACC: {wacc_value}% 사용"
                )
                # ROIC vs WACC 비교 분석
                roic_wacc_analysis = {
                    "roic": roic_value,
                    "wacc": wacc_value,
                    "spread": roic_value - wacc_value,
                    "value_creation": roic_value > wacc_value,
                    "interpretation": f"ROIC({roic_value}%) {'>' if roic_value > wacc_value else '<'} WACC({wacc_value}%) - 가치창출 {'가능' if roic_value > wacc_value else '어려움'}",
                }
            else:
                logger.warning("⚠️ ROIC/WACC 계산값이 없어 가정값 사용")
                roic_wacc_analysis = {
                    "roic": 12.5,  # 가정값
                    "wacc": 8.0,  # 가정값
                    "spread": 4.5,
                    "value_creation": True,
                    "interpretation": "가정값 사용 - 실제 계산된 값 확인 필요",
                }

            # DCF 모델 분석 (실제 계산된 값 우선 사용)
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
                "calculated_metrics": calculated_metrics,  # 실제 계산된 값들
                "roic_wacc_analysis": roic_wacc_analysis,  # ROIC vs WACC 비교
                "dcf_analysis": dcf_analysis,
                "relative_valuation": relative_valuation,
                "asset_based_valuation": asset_based_valuation,
                "comprehensive_valuation": comprehensive_valuation,
                "summary": f"기업의 내재가치와 투자 가치를 종합적으로 평가했어요 (ROIC: {roic_wacc_analysis['roic']}%, WACC: {roic_wacc_analysis['wacc']}%)",
                "data_source": "실제 계산된 데이터 우선 사용",
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

    def _extract_calculated_metrics(
        self, financial_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        실제 계산된 지표들을 추출해요
        실제 데이터를 우선적으로 사용하고, 가정값은 보조적으로만 사용해요!
        """
        calculated_metrics = {}

        # 1. 실제 계산된 ROIC 추출
        if "calculated_roic" in financial_data:
            calculated_metrics["roic"] = financial_data["calculated_roic"]
        elif "roic" in financial_data:
            calculated_metrics["roic"] = financial_data["roic"]
        elif "fundamental_analysis" in financial_data:
            fundamental = financial_data["fundamental_analysis"]
            if "roic_analysis" in fundamental and fundamental["roic_analysis"].get(
                "success"
            ):
                calculated_metrics["roic"] = fundamental["roic_analysis"].get("roic", 0)

        # 2. 실제 계산된 ROE 추출
        if "calculated_roe" in financial_data:
            calculated_metrics["roe"] = financial_data["calculated_roe"]
        elif "roe" in financial_data:
            calculated_metrics["roe"] = financial_data["roe"]
        elif "fundamental_analysis" in financial_data:
            fundamental = financial_data["fundamental_analysis"]
            if "roe_analysis" in fundamental and fundamental["roe_analysis"].get(
                "success"
            ):
                calculated_metrics["roe"] = fundamental["roe_analysis"].get("roe", 0)

        # 3. 실제 계산된 WACC 추출
        if "calculated_wacc" in financial_data:
            calculated_metrics["wacc"] = financial_data["calculated_wacc"]
        elif "wacc" in financial_data:
            calculated_metrics["wacc"] = financial_data["wacc"]
        elif "valuation_analysis" in financial_data:
            valuation = financial_data["valuation_analysis"]
            if "wacc" in valuation:
                calculated_metrics["wacc"] = valuation["wacc"]

        # 4. 기타 실제 계산된 지표들
        for key in [
            "revenue",
            "operating_income",
            "net_income",
            "total_assets",
            "total_equity",
            "current_price",
        ]:
            if key in financial_data:
                calculated_metrics[key] = financial_data[key]

        logger.info(f"📊 추출된 실제 계산 지표: {list(calculated_metrics.keys())}")
        return calculated_metrics

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

    def perform_comprehensive_analysis_sync(
        self, user_input: str, options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        동기 방식의 종합 분석 수행

        Args:
            user_input: 사용자 입력
            options: 분석 옵션

        Returns:
            Dict: 종합 분석 결과
        """
        try:
            logger.info("🎯 모든 전문가 종합 분석 시작...")

            # 실제 데이터 사용 (샘플 데이터 제거)
            # 실제 분석에서는 all_data에서 실제 수집된 데이터를 사용해야 함
            logger.warning("⚠️ 실제 데이터가 제공되지 않아 기본 분석만 수행합니다.")

            # 기본 분석용 최소 데이터 구조
            financial_data = {}
            market_data = {}
            industry_data = {}

            # 각 전문가 분석 실행
            expert_results = []

            # 1. 펀더멘털 분석
            if "펀더멘털 분석" in options.get("analysis_types", []):
                fundamental_result = self.analyze_fundamental(financial_data)
                expert_results.append(fundamental_result)

            # 2. 기술적 분석
            if "기술적 분석" in options.get("analysis_types", []):
                technical_result = self.analyze_technical(market_data)
                expert_results.append(technical_result)

            # 3. 밸류에이션 분석
            if "밸류에이션 분석" in options.get("analysis_types", []):
                valuation_result = self.analyze_valuation(financial_data, market_data)
                expert_results.append(valuation_result)

            # 4. 산업 분석
            if "산업 분석" in options.get("analysis_types", []):
                industry_result = self.analyze_industry(financial_data, industry_data)
                expert_results.append(industry_result)

            # 5. 리스크 평가
            if "리스크 평가" in options.get("analysis_types", []):
                risk_result = self.analyze_risk(financial_data, market_data, {})
                expert_results.append(risk_result)

            # 6. 재무제표 주석 분석
            if "재무제표 주석 분석" in options.get("analysis_types", []):
                footnote_result = self.analyze_footnotes([])
                expert_results.append(footnote_result)

            # 결과 통합
            successful_analyses = [r for r in expert_results if r.get("success")]
            failed_analyses = [r for r in expert_results if not r.get("success")]

            # 종합 추천 생성
            recommendations = self._generate_integrated_recommendations(
                expert_results, []
            )

            result = {
                "success": len(successful_analyses) > 0,
                "input": user_input,
                "options": options,
                "expert_results": expert_results,
                "successful_count": len(successful_analyses),
                "failed_count": len(failed_analyses),
                "recommendations": recommendations,
                "recommendation": self._get_final_recommendation(recommendations),
                "confidence": self._calculate_confidence(successful_analyses),
                "summary": f"'{user_input}' 종목에 대한 {len(successful_analyses)}개 전문가 분석이 완료되었습니다.",
                "timestamp": datetime.now().isoformat(),
            }

            logger.info("✅ 모든 전문가 종합 분석 완료!")
            return result

        except Exception as e:
            logger.error(f"❌ 종합 분석 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "input": user_input,
                "timestamp": datetime.now().isoformat(),
            }

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

    def _get_final_recommendation(self, recommendations: List[str]) -> str:
        """최종 추천 결정"""
        if not recommendations:
            return "관망"

        first_recommendation = recommendations[0]
        if "매수" in first_recommendation:
            return "매수"
        elif "매도" in first_recommendation:
            return "매도"
        else:
            return "관망"

    def _calculate_confidence(self, successful_analyses: List[Dict[str, Any]]) -> str:
        """신뢰도 계산"""
        if len(successful_analyses) >= 4:
            return "높음"
        elif len(successful_analyses) >= 2:
            return "중간"
        else:
            return "낮음"
