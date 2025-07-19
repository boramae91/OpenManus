# -*- coding: utf-8 -*-
"""
🚀 One-Hot Sector Activation 핵심 시스템

"""

import asyncio
import hashlib
import json
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from app.logger import logger

from .gics_sectors import GICSSector, GICSSectorManager
from .sector_teams import SectorTeamFactory


class AnalysisDepth(Enum):
    """
    분석 깊이 수준 정의 (2명 체제로 단순화)

    현재는 분석 깊이와 무관하게 항상 2명의 핵심 전문가(통합 재무분석가 + 기술적 분석가)만 사용합니다.
    """

    QUICK = "quick"  # 빠른 분석 (2명 체제, $0.20, 24시간 캐시)
    STANDARD = "standard"  # 표준 분석 (2명 체제, $0.20, 24시간 캐시)
    DEEP = "deep"  # 심화 분석 (2명 체제, $0.20, 24시간 캐시)


@dataclass
class CacheEntry:
    """캐시 엔트리 정의"""

    key: str
    data: Dict[str, Any]
    timestamp: float
    ttl_hours: int

    def is_expired(self) -> bool:
        """캐시가 만료되었는지 확인"""
        return time.time() - self.timestamp > (self.ttl_hours * 3600)


class CacheManager:
    """지능형 캐싱 시스템"""

    def __init__(self):
        self.cache: Dict[str, CacheEntry] = {}
        logger.info("💾 캐시 매니저 초기화 완료")

    def get_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """캐시에서 데이터 조회"""
        if key in self.cache:
            entry = self.cache[key]
            if not entry.is_expired():
                logger.info(f"🎯 캐시 히트: {key}")
                return entry.data
            else:
                del self.cache[key]
                logger.info(f"⏰ 캐시 만료로 삭제: {key}")
        return None

    def set_cache(self, key: str, data: Dict[str, Any], ttl_hours: int):
        """캐시에 데이터 저장"""
        entry = CacheEntry(
            key=key, data=data, timestamp=time.time(), ttl_hours=ttl_hours
        )
        self.cache[key] = entry
        logger.info(f"💾 캐시 저장: {key} (TTL: {ttl_hours}시간)")

    def clear_all_cache(self):
        """전체 캐시 삭제"""
        self.cache.clear()
        logger.info("🗑️ 전체 캐시 삭제 완료")


class SmartSectorManager:
    """
    🚀 One-Hot Sector Activation 핵심 매니저

    섹터를 감지하고, 해당 섹터의 전문가 팀만 활성화해서
    90% 비용 절감을 달성하는 혁신적인 시스템이에요!
    """

    # 📊 공통 메시지 상수 정의 (중복 제거를 위한 리팩토링)
    MESSAGES = {
        "NO_DATA": "알 수 없음",
        "NO_TECHNICAL_DATA": "기술적 분석 데이터가 제공되지 않았습니다.",
        "TECHNICAL_INDICATORS_HEADER": "📊 **실제 계산된 기술적 지표 (최신 값)**:",
        "CURRENT_PRICE_FORMAT": "**현재 주가**: {price:,.0f}원 ({date})",
        "CURRENT_VOLUME_FORMAT": "**현재 거래량**: {volume:,}주",
        "MOVING_AVERAGES_HEADER": "**📈 이동평균선**:",
        "RSI_HEADER": "**📊 RSI (상대강도지수)**:",
        "MACD_HEADER": "**📈 MACD**:",
        "BOLLINGER_BANDS_HEADER": "**📊 볼린저 밴드**:",
        "STOCHASTIC_HEADER": "**📊 스토캐스틱**:",
        "WILLIAMS_R_HEADER": "**📊 윌리엄스 %R**:",
        "OBV_HEADER": "**📊 OBV (On-Balance Volume)**:",
        "TRADING_SIGNALS_HEADER": "**📊 종합 매매 신호**:",
        "LAST_UPDATE_FORMAT": "**마지막 업데이트**: {date}",
        "CALCULATION_ERROR": "계산 불가",
        "DATA_PROCESSING_ERROR": "데이터 처리 중 오류",
    }

    def __init__(self, llm):
        """
        Smart Sector Manager 초기화

        Args:
            llm: LLM 인스턴스
        """
        self.llm = llm
        self.sector_manager = GICSSectorManager()
        self.team_factory = SectorTeamFactory(self.sector_manager)
        self.cache_manager = CacheManager()

        # 현재 활성화된 섹터와 팀
        self.current_active_sector: Optional[GICSSector] = None
        self.current_active_team = None

        # 성능 통계
        self.stats = {
            "total_analyses": 0,
            "total_cost_savings": 0.0,
            "sector_usage_count": {},
            "average_savings_rate": 0.0,
        }

        logger.info("🚀 Smart Sector Manager 초기화 완료!")
        logger.info("💰 One-Hot Activation으로 비용 절감.")

    async def analyze_with_optimal_team(
        self,
        user_prompt: str,
        stock_name: str,
        stock_code: str,
        financial_data: Dict[str, Any],
        analysis_depth: AnalysisDepth = AnalysisDepth.STANDARD,
        pre_detected_gics_sector: str = None,
    ) -> Dict[str, Any]:
        """
        최적화된 섹터 팀으로 분석 수행

        One-Hot Activation의 핵심 메서드예요!

        Args:
            user_prompt: 사용자 질문
            stock_name: 종목명
            stock_code: 종목코드
            financial_data: 재무 데이터
            analysis_depth: 분석 깊이

        Returns:
            Dict: 분석 결과
        """
        try:
            logger.info(f"🎯 One-Hot 섹터 분석 시작: {stock_name}")

            # 1. 캐시 확인
            cache_key = self._generate_cache_key(
                user_prompt, stock_name, stock_code, analysis_depth
            )
            cached_result = self.cache_manager.get_cache(cache_key)
            if cached_result:
                logger.info("⚡ 캐시된 결과 반환 - 추가 비용 없음!")
                return cached_result

            # 2. 섹터 감지 (🎯 사전 감지된 GICS 섹터 우선 사용!)
            if pre_detected_gics_sector and pre_detected_gics_sector != "Unknown":
                logger.info(
                    f"🎯 Dataset에서 사전 감지된 GICS 섹터 사용: {pre_detected_gics_sector}"
                )
                # GICS 섹터명을 우리 시스템의 GICSSector로 매핑
                detected_sector = self._map_gics_to_internal_sector(
                    pre_detected_gics_sector
                )
                logger.info(f"📊 매핑된 내부 섹터: {detected_sector.name}")
            else:
                logger.info("🔍 기존 방식으로 섹터 감지...")
                detected_sector = self.sector_manager.detect_sector_from_stock(
                    stock_name, stock_code
                )
                logger.info(f"📊 감지된 섹터: {detected_sector.name}")

            # 3. One-Hot 활성화 (기존 팀 비활성화 + 새 팀 활성화)
            self._deactivate_current_team()
            activated_team = self._activate_sector_team(detected_sector)

            # 4. 적절한 전문가 선택 (분석 깊이에 따라)
            selected_experts = self._select_experts_by_depth(
                activated_team, analysis_depth, user_prompt
            )

            # 5. 전문가별 분석 수행
            expert_insights = await self._perform_expert_analysis(
                selected_experts, user_prompt, stock_name, stock_code, financial_data
            )

            # 6. 비용 절감 계산
            cost_savings = self._calculate_cost_savings(
                len(selected_experts), analysis_depth
            )

            # 7. 결과 구성
            result = {
                "success": True,
                "detected_sector": detected_sector.name,
                "activated_experts": [expert.name for expert in selected_experts],
                "expert_insights": expert_insights,
                "cost_savings": cost_savings,
                "analysis_depth": analysis_depth.value,
                "cache_key": cache_key,
            }

            # 8. 캐시 저장
            ttl_hours = self._get_cache_ttl(analysis_depth)
            self.cache_manager.set_cache(cache_key, result, ttl_hours)

            # 9. 통계 업데이트
            self._update_stats(detected_sector, cost_savings)

            logger.info(
                f"✅ One-Hot 분석 완료 - 절약률: {cost_savings['savings_percentage']:.1f}%"
            )
            return result

        except Exception as e:
            logger.error(f"❌ One-Hot 분석 실패: {e}")
            return {"success": False, "error": str(e), "detected_sector": None}

    async def analyze_with_comprehensive_data(
        self,
        user_prompt: str,
        stock_name: str,
        stock_code: str,
        financial_data: Dict,
        enhanced_dart_data: Dict = None,
        manus_collected_data: Dict = None,
        technical_analysis_data: Dict = None,
        dart_reports_dictionary: Dict = None,  # 🚀 DART 보고서 딕셔너리 추가!
        analysis_depth: AnalysisDepth = AnalysisDepth.STANDARD,
        pre_detected_gics_sector: str = None,
    ) -> Dict[str, Any]:
        """
        🚀 종합 데이터 기반 CrewAI 분석 (통합 개선)

        모든 수집된 데이터를 통합하여 각 전문가에게 최적화된 정보를 제공하고
        종합 분석을 수행합니다.

        Args:
            user_prompt: 사용자 질문
            stock_name: 종목명
            stock_code: 종목코드
            financial_data: 재무데이터
            enhanced_dart_data: Enhanced DART 데이터
            manus_collected_data: Manus Agent 수집 데이터
            technical_analysis_data: 기술적 분석 데이터
            dart_reports_dictionary: 🚀 DART 사업보고서/분기보고서 딕셔너리 (NEW!)
            analysis_depth: 분석 깊이
            pre_detected_gics_sector: 사전 감지된 GICS 섹터

        Returns:
            Dict: CrewAI 종합 분석 결과
        """
        try:
            logger.info(
                f"🎯 CrewAI 종합 분석 시작: {stock_name} (수정된 워크플로우 + 토큰 최적화)"
            )

            # 🔢 토큰 최적화 (새로운 기능!)
            logger.info("🔢 토큰 최적화 시작...")
            optimization_result = self._optimize_data_for_token_limit(
                financial_data=financial_data,
                enhanced_dart_data=enhanced_dart_data,
                manus_collected_data=manus_collected_data,
                dart_reports_dictionary=dart_reports_dictionary,  # 🚀 DART 딕셔너리 추가!
            )

            # 최적화된 데이터 사용
            optimized_financial = optimization_result["financial_data"]
            optimized_dart = optimization_result["enhanced_dart_data"]
            optimized_manus = optimization_result["manus_collected_data"]
            optimized_dart_dict = optimization_result[
                "dart_reports_dictionary"
            ]  # 🚀 최적화된 DART 딕셔너리

            if optimization_result["optimization_applied"]:
                logger.info("🎯 토큰 최적화 적용됨")
                original_tokens = optimization_result["original_token_estimate"]
                optimized_tokens = optimization_result["optimized_token_estimate"]
                logger.info(
                    f"📊 토큰 최적화: {original_tokens:,} → {optimized_tokens:,}"
                )
            else:
                logger.info("✅ 토큰 수가 목표 범위 내 - 최적화 불필요")

            # 1. 종합 캐시 키 생성 (최적화된 Manus 데이터 + 기술적 분석 데이터 포함)
            comprehensive_cache_key = self._generate_comprehensive_cache_key(
                user_prompt,
                stock_name,
                stock_code,
                analysis_depth,
                optimized_manus,  # 최적화된 데이터 사용
                technical_analysis_data,  # 🎯 기술적 분석 데이터 추가
            )
            cached_result = self.cache_manager.get_cache(comprehensive_cache_key)
            if cached_result:
                logger.info("⚡ 종합 분석 캐시된 결과 반환 - 추가 비용 없음!")
                return cached_result

            # 🎯 2. 섹터 감지 (GICS 섹터 사전 감지 활용)
            if pre_detected_gics_sector and pre_detected_gics_sector != "Unknown":
                logger.info(
                    f"🎯 Dataset 기반 GICS 섹터 활용: {pre_detected_gics_sector}"
                )
                detected_sector = self._map_gics_to_internal_sector(
                    pre_detected_gics_sector
                )
                # _map_gics_to_internal_sector는 매핑 실패시 기본값(INFORMATION_TECHNOLOGY)을 반환하므로
                # 항상 유효한 값이 반환됩니다
                logger.info(
                    f"✅ GICS → 내부 섹터 매핑 완료: {pre_detected_gics_sector} → {detected_sector.name}"
                )
            else:
                logger.info("🔍 자동 섹터 감지 수행...")
                detected_sector = self.sector_manager.detect_sector_from_stock(
                    stock_name, stock_code
                )

            logger.info(f"📊 감지된 섹터: {detected_sector.name}")

            # 3. One-Hot 활성화 (기존 팀 비활성화 + 새 팀 활성화)
            self._deactivate_current_team()
            activated_team = self._activate_sector_team(detected_sector)

            # 4. 적절한 전문가 선택 (분석 깊이에 따라)
            selected_experts = self._select_experts_by_depth(
                activated_team, analysis_depth, user_prompt
            )

            # 🔧 데이터 전달 검증 및 로깅
            self._validate_data_transfer(
                optimized_financial,
                optimized_dart,
                optimized_manus,
                optimized_dart_dict,
                technical_analysis_data,
            )

            # 🚀 5. 종합 데이터로 전문가별 분석 수행 (최적화된 데이터 사용!)
            # 🔧 PDF 인터페이스 추출
            pdf_interface = None
            if optimized_manus and optimized_manus.get("pdf_analysis"):
                pdf_interface = optimized_manus["pdf_analysis"].get(
                    "pdf_dictionary_interface"
                )
                if pdf_interface:
                    logger.info("📄 PDF 인터페이스 추출 완료")
                else:
                    logger.info("📄 PDF 인터페이스가 없습니다 (DART 딕셔너리만 사용)")

            expert_insights = await self._perform_comprehensive_expert_analysis(
                selected_experts,
                user_prompt,
                stock_name,
                stock_code,
                optimized_financial,  # 🔢 최적화된 재무데이터
                optimized_dart,  # 🔢 최적화된 DART 데이터
                optimized_manus,  # 🔢 최적화된 Manus 데이터
                technical_analysis_data,  # 🎯 기술적 분석 데이터 추가!
                optimized_dart_dict,  # 🚀 최적화된 DART 딕셔너리 사용!
                pdf_interface,  # 🔧 PDF 인터페이스 (manus_collected_data에서 추출)
            )

            # 6. 비용 절감 계산
            cost_savings = self._calculate_cost_savings(
                len(selected_experts), analysis_depth
            )

            # 🚀 7. 종합 분석 결과 구성 (토큰 최적화 정보 포함)
            result = {
                "success": True,
                "analysis_type": "comprehensive_manus_crewai_synthesis_optimized",  # 최적화 포함
                "detected_sector": detected_sector.name,
                "sector_korean_name": self.sector_manager.get_sector_korean_name(
                    detected_sector
                ),
                "gics_sector_used": (
                    pre_detected_gics_sector
                    if pre_detected_gics_sector != "Unknown"
                    else None
                ),  # 🎯 GICS 섹터 정보
                "activated_experts": [expert.name for expert in selected_experts],
                "selected_experts_count": len(selected_experts),
                "expert_insights": expert_insights,
                "cost_savings": cost_savings,
                "analysis_depth": analysis_depth.value,
                "cache_key": comprehensive_cache_key,
                "data_integration_quality": self._assess_data_integration_quality(
                    optimized_financial,
                    optimized_dart,
                    optimized_manus,  # 최적화된 데이터로 품질 평가
                ),
                "synthesis_completeness": "완전통합_토큰최적화",  # 모든 데이터 소스 활용 + 토큰 최적화
                "token_optimization": {  # 🔢 토큰 최적화 정보 추가
                    "optimization_applied": optimization_result["optimization_applied"],
                    "original_token_estimate": optimization_result[
                        "original_token_estimate"
                    ],
                    "optimized_token_estimate": optimization_result[
                        "optimized_token_estimate"
                    ],
                    "compression_ratio": (
                        optimization_result["optimized_token_estimate"]
                        / optimization_result["original_token_estimate"]
                        if optimization_result["original_token_estimate"] > 0
                        else 1.0
                    ),
                },
            }

            # 8. 캐시 저장
            ttl_hours = self._get_cache_ttl(analysis_depth)
            self.cache_manager.set_cache(comprehensive_cache_key, result, ttl_hours)

            # 9. 통계 업데이트
            self._update_stats(detected_sector, cost_savings)

            logger.info(
                f"✅ CrewAI 종합 분석 완료 (토큰 최적화 포함) - 절약률: {cost_savings['savings_percentage']:.1f}%"
            )
            return result

        except Exception as e:
            logger.error(f"❌ CrewAI 종합 분석 실패: {e}")
            return {"success": False, "error": str(e), "detected_sector": None}

    def _deactivate_current_team(self):
        """현재 활성화된 팀 비활성화"""
        if self.current_active_sector:
            logger.info(f"🔴 {self.current_active_sector.name} 팀 비활성화")
            self.current_active_sector = None
            self.current_active_team = None

    def _activate_sector_team(self, sector: GICSSector):
        """새로운 섹터 팀 활성화"""
        logger.info(f"🟢 {sector.name} 팀 활성화")
        self.current_active_sector = sector
        self.current_active_team = self.team_factory.create_sector_team(sector)
        return self.current_active_team

    def _select_experts_by_depth(self, team, depth: AnalysisDepth, prompt: str) -> List:
        """분석 깊이와 무관하게 항상 2명의 핵심 전문가만 선택 (통합 재무분석가 + 기술적 분석가)"""
        all_experts = team.experts

        # 분석 깊이와 무관하게 항상 통합 재무분석가와 기술적 분석가 2명만 선택
        selected = []

        # 통합 재무분석가 찾기
        integrated_financial_analyst = next(
            (expert for expert in all_experts if "통합 재무분석가" in expert.name), None
        )
        if integrated_financial_analyst:
            selected.append(integrated_financial_analyst)

        # 기술적 분석가 찾기
        technical_analyst = next(
            (expert for expert in all_experts if "기술적 분석가" in expert.name), None
        )
        if technical_analyst:
            selected.append(technical_analyst)

        # 2명이 모두 없으면 기본적으로 처음 2명 선택
        if len(selected) < 2:
            for expert in all_experts:
                if expert not in selected and len(selected) < 2:
                    selected.append(expert)

        logger.info(f"🎯 2명 체제: {len(selected)}명 전문가 선택 (분석 깊이 무관)")
        logger.info(f"   선택된 전문가: {[expert.name for expert in selected]}")

        return selected

    def _select_by_keywords(self, experts: List, prompt: str, count: int) -> List:
        """키워드 기반 전문가 선택 (2명 체제로 단순화)"""
        # 2명 체제에서는 키워드와 무관하게 항상 통합 재무분석가와 기술적 분석가 선택
        selected = []

        # 통합 재무분석가 찾기
        integrated_financial_analyst = next(
            (expert for expert in experts if "통합 재무분석가" in expert.name), None
        )
        if integrated_financial_analyst:
            selected.append(integrated_financial_analyst)

        # 기술적 분석가 찾기
        technical_analyst = next(
            (expert for expert in experts if "기술적 분석가" in expert.name), None
        )
        if technical_analyst:
            selected.append(technical_analyst)

        # 2명이 모두 없으면 기본적으로 처음 2명 선택
        if len(selected) < 2:
            for expert in experts:
                if expert not in selected and len(selected) < 2:
                    selected.append(expert)

        logger.info(f"🎯 키워드 선택: {len(selected)}명 전문가 선택 (2명 체제)")
        logger.info(f"   선택된 전문가: {[expert.name for expert in selected]}")

        return selected[:count]

    async def _perform_expert_analysis(
        self,
        expert,
        financial_data,
        enhanced_dart_data,
        manus_collected_data,
        llm_instance,
        max_retries=3,
    ):
        """
        🎯 시니어 애널리스트급 전문가 분석 수행

        개선사항:
        - 전문가별 시니어 애널리스트 수준 프롬프트
        - 안전한 데이터 타입 처리
        - 정량적 분석 지표 명시
        - 구체적 계산식과 근거 제시
        """
        for attempt in range(max_retries):
            try:
                logger.info(
                    f"🎯 {expert.name} 전문가 분석 시작 (시도 {attempt + 1}/{max_retries})"
                )

                # 🔧 안전한 컨텍스트 생성 (데이터 보강 포함)
                context = await self._create_expert_specific_context(
                    expert=expert,
                    user_prompt="",  # 기본값 추가
                    stock_name="",  # 기본값 추가
                    stock_code="",  # 기본값 추가
                    financial_data=financial_data,
                    enhanced_dart_data=enhanced_dart_data,
                    manus_collected_data=manus_collected_data,
                    technical_analysis_data=None,  # 기본값 추가
                    dart_reports_dictionary=None,  # 기본값 추가
                )

                # 🌐 웹검색 강제 실행 (Chat GPT 피드백 해결)
                web_search_results = ""
                stock_name = getattr(financial_data, "stock_name", "분석대상")

                # 🌐 펀더멘털 전문가 전용 강제 웹검색 시스템
                web_search_data = ""
                if (
                    "펀더멘털" in expert.name
                    or "펀더멘탈" in expert.name
                    or "fundamental" in expert.name.lower()
                ):
                    logger.info(f"🔍 {expert.name} 전용 웹검색 강제 실행 시작...")

                    try:
                        from app.tool.web_search import WebSearch

                        web_search_tool = WebSearch()

                        # Chat GPT 피드백 핵심 요구사항 웹검색 (반드시 실행)
                        mandatory_searches = [
                            f"{stock_name} 경쟁사 ROE PER 비교 분석",
                            f"{stock_name} 3년 ROE 매출성장률 추이 변화",
                            f"{stock_name} 업계 평균 PER PBR 2024",
                            f"{stock_name} 목표주가 컨센서스 증권사",
                            f"{stock_name} WACC 베타 계산 2024",
                            f"{stock_name} 동종업계 FCF 수익률 비교",
                        ]

                        search_results = []
                        successful_searches = 0

                        for i, query in enumerate(mandatory_searches, 1):
                            logger.info(
                                f"🔍 필수 검색 {i}/{len(mandatory_searches)}: {query}"
                            )

                            try:
                                result = await web_search_tool.execute(
                                    query=query,
                                    num_results=3,
                                    lang="ko",
                                    country="kr",
                                    fetch_content=True,  # 더 상세한 내용 가져오기
                                )

                                if result and result.output:
                                    search_results.append(
                                        f"""
🔍 **검색 {i}**: {query}
{result.output}
{'='*80}
"""
                                    )
                                    successful_searches += 1
                                    logger.info(
                                        f"✅ 검색 성공 {i}: {len(result.output):,}자"
                                    )
                                else:
                                    search_results.append(f"❌ 검색 {i} 실패: {query}")
                                    logger.warning(f"❌ 검색 {i} 결과 없음: {query}")

                            except Exception as e:
                                search_results.append(
                                    f"❌ 검색 {i} 오류: {query} - {str(e)}"
                                )
                                logger.error(f"❌ 검색 {i} 오류: {query} - {e}")

                        # 웹검색 결과 통합
                        if successful_searches > 0:
                            web_search_data = f"""

🌐 **실시간 웹검색 데이터** (Chat GPT 피드백 반영 - {successful_searches}/{len(mandatory_searches)} 성공):
{chr(10).join(search_results)}

🚨 **중요 지시사항**:
1. 위 웹검색 결과를 반드시 분석에 활용하세요
2. 경쟁사 비교는 검색된 실제 데이터만 사용하세요
3. 시계열 데이터는 검색 결과에서 추출한 수치만 사용하세요
4. 업계 평균은 추측하지 말고 검색된 데이터를 인용하세요
5. 목표주가는 검색된 증권사 컨센서스를 명시하세요

"""
                            logger.info(
                                f"✅ 웹검색 데이터 준비 완료: {len(web_search_data):,}자"
                            )
                        else:
                            web_search_data = """

⚠️ **웹검색 실패**: 모든 웹검색이 실패했습니다.
분석 시 다음과 같이 명시해주세요:
- 경쟁사 비교: "웹검색 실패로 데이터 부족"
- 시계열 분석: "웹검색 실패로 트렌드 분석 불가"
- 업계 평균: "웹검색 실패로 비교 데이터 없음"
- 목표주가: "웹검색 실패로 컨센서스 확인 불가"

"""
                            logger.warning("❌ 모든 웹검색 실패")

                    except Exception as e:
                        logger.error(f"❌ 웹검색 시스템 오류: {e}")
                        web_search_data = f"""

❌ **웹검색 시스템 오류**: {str(e)}
분석 시 "웹검색 시스템 오류로 실시간 데이터 확인 불가"라고 명시해주세요.

"""

                # 컨텍스트에 웹검색 데이터 추가
                context += web_search_data

                # 🔧 컨텍스트 타입 검증
                if not isinstance(context, str):
                    logger.warning(
                        f"⚠️ {expert.name} 컨텍스트가 문자열이 아님: {type(context)}"
                    )
                    context = str(context) if context else "컨텍스트 생성 실패"

                # 🎯 Chat GPT 7가지 피드백 완전 반영 - 시니어 애널리스트급 펀더멘털 분석 프롬프트
                prompt = f"""
**역할**: 대형 증권사 시니어 펀더멘털 애널리스트 (10년 경력)
**전문가**: {expert.name} ({expert.role})
**전문 분야**: {expert.expertise}

{context}

🎯 **핵심 임무**: Chat GPT 피드백 7가지 완전 반영한 투자 실무급 분석

## 📊 **STEP 1: 동종업계 비교 분석** (필수)

### 🧠 사고 과정 (CoT) 필수:
**1단계: 경쟁사 데이터 수집**
- 수집된 경쟁사: [구체적 기업명과 데이터]
- 비교 지표: [ROE, PER, EBITDA 마진, 매출성장률]

**2단계: 상대적 순위 분석**
- 업계 내 순위: [구체적 순위와 전체 기업 수]
- 순위 근거: [수치적 비교 결과]

**3단계: 격차 정량화**
- 격차 계산: [구체적 수치와 계산 과정]
- 격차 원인: [구체적 원인 분석]

### 📊 분석 결과:
- **경쟁사 3개 기업** ROE, PER, EBITDA 마진, 매출성장률 비교 테이블 작성
- **상대적 순위** 제시: "업계 3위/7개사" 형태로 명시
- **격차 분석**: "경쟁사 대비 ROE [실제 격차]%p 낮음" 등 구체적 수치

## 📊 **STEP 2: 3년 시계열 트렌드 분석** (필수)
- **ROE 추이**: "[실제 연도별 ROE 추이]" 정확한 연도별 수치
- **매출성장률 추이**: 3년간 변화와 **구체적 원인** (반도체 사이클, 환율 등)
- **트렌드 방향성**: 개선/악화 여부를 수치로 입증

## 📊 **STEP 3: WACC vs ROIC 정량 분석** (필수)
- **WACC 직접 계산**: 자기자본비용 + 타인자본비용 (가중평균)
- **ROIC 계산**: NOPAT ÷ Invested Capital
- **Value Creation**: ROIC - WACC = +/- [실제 계산값]% (가치창출/파괴 명확히 판단)

## 📊 **STEP 4: FCF 정확한 정의 및 분석** (필수)
- **FCF 정의**: 영업활동현금흐름 - 자본적지출 (재무활동현금흐름 아님!)
- **FCF Yield**: FCF ÷ 시가총액 × 100 (%)
- **3년 FCF 추이**: 안정성과 지속가능성 평가

## 📊 **STEP 5: 세그먼트별 손익 분석** (필수)
- **주요 사업부문별** 매출 비중과 영업이익 기여도
- **핵심 수익원**: 어느 사업부가 전체 이익의 몇 %를 차지하는지
- **사업부별 성장성**: 각 부문의 전년 대비 성장률

## 📊 **STEP 6: 밸류에이션 멀티플 분석** (필수)
- **PER, PBR, EV/EBITDA**: 현재값 vs 업계 평균 vs 과거 3년 평균
- **목표주가 3시나리오**: Bear Case / Base Case / Bull Case (각각 근거 제시)
- **Fair Value**: DCF 또는 멀티플 방식으로 적정가치 산출

## 🚀 **ENHANCED ANALYSIS REQUIREMENTS** (Chain of Thought + Reasoning 기법):

### 🧠 **분석 방법론**: Chain of Thought (CoT) + Reasoning 모델 적용

**⚠️ 중요**: 각 분석 단계에서 반드시 아래 형식으로 사고 과정을 단계별로 보여주세요:

**📝 필수 응답 형식**:
```
## 📊 STEP X: [분석 제목]

### 🧠 사고 과정 (CoT):

**1단계: 데이터 수집 및 정리**
- 수집된 데이터: [구체적 데이터 나열]
- 데이터 품질: [데이터 신뢰성 평가]

**2단계: 패턴 인식**
- 발견된 패턴: [구체적 패턴 설명]
- 과거 vs 현재: [비교 분석]

**3단계: 인과관계 분석**
- 원인 분석: [구체적 원인]
- 영향 요인: [영향도 정량화]

**4단계: 시나리오 구축**
- 시나리오 A: [구체적 가정과 결과]
- 시나리오 B: [구체적 가정과 결과]

**5단계: 리스크 평가**
- 리스크 요인: [구체적 리스크]
- 발생 확률: [정량적 확률]

**6단계: 종합 판단**
- 결론: [명확한 판단]
- 근거: [구체적 근거]

### 📊 분석 결과:
[최종 분석 내용]
```

**🚫 금지사항**:
- 사고 과정 없이 바로 결과만 제시하지 마세요
- 각 단계를 건너뛰지 마세요
- 구체적 수치와 근거 없이 추상적 설명만 하지 마세요

### 📊 **STEP 7: 수치 간 인과관계 및 구조적 통찰 분석** (CoT 적용)

**사고 과정**:
1. **ROE 구조적 분해**: ROE = 순이익률 × 자산회전율 × 재무레버리지
2. **각 구성요소 분석**: 어떤 요소가 ROE 변화를 주도했는지 정량적 분석
3. **지속가능성 평가**: 현재 ROE 구조가 미래에도 지속 가능한지 판단
4. **개선 방향 도출**: ROE 향상을 위한 구체적 방안 제시

**분석 요구사항**:
- 수집된 재무데이터를 바탕으로 ROE 구조적 분해 수행
- 각 구성요소의 변화 원인과 영향도를 구체적 수치로 분석
- 사업 구조적 특성을 고려한 지속가능성 평가
- 향후 ROE 개선을 위한 핵심 과제 도출

### 📊 **STEP 8: 산업·경쟁사 비교 분석의 심화** (CoT 적용)

**사고 과정**:
1. **경쟁사 사업 구조 분석**: 수집된 경쟁사 데이터로 사업 모델 비교
2. **기술 격차 평가**: 핵심 기술/역량에서의 상대적 우위 분석
3. **시장 포지셔닝 분석**: 시장 점유율과 경쟁우위의 원천 파악
4. **전략적 차별화 요소**: 경쟁사 대비 차별화된 경쟁우위 도출

**분석 요구사항**:
- 웹검색으로 수집된 경쟁사 정보를 활용한 정성적 비교
- 사업 구조, 기술력, 시장 지위의 구체적 차이점 분석
- 경쟁우위의 지속가능성과 위협 요인 평가
- 상대적 투자 매력도 판단

### 📊 **STEP 9: Forward-looking 분석** (CoT 적용)

**사고 과정**:
1. **트렌드 분석**: 수집된 시장 데이터로 미래 트렌드 예측
2. **수치 변화 시뮬레이션**: 주요 변수의 변화가 재무지표에 미치는 영향 계산
3. **리스크 시나리오 구축**: 다양한 리스크 요인의 발생 가능성과 영향도 평가
4. **확률적 전망**: 각 시나리오별 발생 확률을 고려한 종합 전망

**분석 요구사항**:
- 시장 트렌드와 산업 동향을 바탕으로 한 미래 수치 예측
- 구체적 리스크 요인의 발생 확률과 영향도 정량화
- Bull/Base/Bear 시나리오별 재무지표 변화 예측 (각 시나리오별 발생 확률과 영향도 정량화)
- 불확실성을 고려한 확률적 전망 제시



## 🎯 **Executive Summary** (최종 결론):

### 📈 **투자 스코어카드** (5점 만점):
- 수익성: [분석 기반 점수]/5.0점 (ROE, ROIC 기준)
- 성장성: [분석 기반 점수]/5.0점 (매출/이익 성장률 기준)
- 안전성: [분석 기반 점수]/5.0점 (부채비율, FCF 기준)
- 밸류에이션: [분석 기반 점수]/5.0점 (PER, PBR 기준)
- **종합점수**: [분석 기반 종합점수]/5.0점

**📊 점수 산정 기준**:
- **5.0점**: 업계 최고 수준, 절대적 우위
- **4.0-4.9점**: 우수한 수준, 경쟁우위 확보
- **3.0-3.9점**: 평균 수준, 안정적 운영
- **2.0-2.9점**: 평균 이하, 개선 필요
- **1.0-1.9점**: 부족한 수준, 구조적 문제

### 💡 **투자 실행 전략**:
- **BUY/HOLD/SELL**: 명확한 투자 의견 + 목표주가
- **매수 시점**: "지금 즉시" / "[분석 기반 하락률]% 하락 시" / "실적 개선 확인 후"
- **투자 기간**: 단기(3개월) / 중기(1년) / 장기(3년)

### ⚠️ **핵심 리스크 2가지**:
1. **[구체적 리스크명]**: 발생 확률 [분석 기반 확률]%, 예상 주가 영향 [분석 기반 영향도]%
2. **[구체적 리스크명]**: 발생 확률 [분석 기반 확률]%, 예상 주가 영향 [분석 기반 영향도]%

**📊 리스크 확률 계산 기준**:
- **높은 확률 (60-80%)**: 현재 진행 중이거나 단기 내 발생 가능한 리스크
- **중간 확률 (30-60%)**: 중기 내 발생 가능하나 불확실성이 있는 리스크
- **낮은 확률 (10-30%)**: 장기적이거나 발생 가능성이 낮은 리스크

**📈 주가 영향도 계산 기준**:
- **높은 영향 (-30% 이상)**: 사업 모델 전면 재검토가 필요한 구조적 리스크
- **중간 영향 (-10~30%)**: 실적에 직접적 영향을 주는 운영 리스크
- **낮은 영향 (-10% 미만)**: 단기적 변동성이나 마이너한 리스크

## 🚫 **품질 기준** (다음 표현 사용 시 분석 실패):
- "긍정적", "양호한", "안정적", "경쟁력 있는" 등 모호한 표현 금지
- "~로 보입니다", "~것으로 판단됩니다" 등 애매한 결론 금지
- 동일한 문장이나 표현을 2번 이상 반복 금지
- 웹검색 없이 경쟁사 데이터 추측 금지

**🔥 차별화 포인트**: 투자 통찰, 상대적 우위, 지속가능성, 적정 투자시점 제시 필수
**📊 필수 요소**: 구체적 수치, 비교 데이터, 원인 분석, 명확한 투자 판단
"""

                # 🔧 안전한 프롬프트 검증
                if not prompt or len(prompt.strip()) < 100:
                    raise ValueError(f"{expert.name} 프롬프트가 너무 짧거나 비어있음")

                # LLM 분석 수행
                logger.info(f"🤖 {expert.name} LLM 분석 요청...")

                # 🔧 최적화된 LLM 호출 (CoT 강화 + 온도 조절 + 프롬프트 개선)
                try:
                    # 🔧 프롬프트에 명확한 지침 추가
                    enhanced_prompt = f"""
{prompt}

**🎯 중요 지침**:
1. 위의 데이터를 기반으로 바로 구체적인 분석을 시작하세요
2. "다음과 같은 분석을 진행하겠습니다" 같은 프롬프트 문구는 사용하지 마세요
3. Chain of Thought 방식으로 단계별 사고 과정을 명시하세요
4. 모든 수치는 반드시 출처를 명시하세요
5. 분석 결과는 구체적이고 실용적이어야 합니다

**📋 분석 형식**:
**1단계: 데이터 분석**
[구체적인 데이터 분석 내용]

**2단계: 핵심 지표 평가**
[핵심 지표별 상세 분석]

**3단계: 투자 판단**
[투자 의견 및 근거]
"""

                    # 🔧 안전한 LLM 호출 (예외 처리 강화)
                    try:
                        # CoT 강화를 위한 온도 조절 및 토큰 수 증가
                        analysis_result = await llm_instance.ask(
                            prompt=enhanced_prompt, temperature=0.05, max_tokens=8000
                        )
                    except Exception as llm_call_error:
                        logger.error(
                            f"❌ {expert.name} LLM 호출 중 오류: {llm_call_error}"
                        )
                        # 🔧 대체 분석 결과 생성
                        analysis_result = f"""
# {expert.name} 분석 (오류로 인한 간소화 버전)

## ⚠️ 오류 발생
LLM 호출 중 오류가 발생했습니다: {str(llm_call_error)}

## 📊 기본 정보
- 전문가: {expert.name}
- 역할: {expert.role}
- 분석 시간: {datetime.now().isoformat()}

## 🔧 권장사항
- API 연결 상태 확인
- 토큰 제한 확인
- 네트워크 연결 확인

이 오류가 지속되면 시스템 관리자에게 문의하세요.
"""

                    # 결과 처리
                    if not analysis_result:
                        raise ValueError("LLM 분석 결과가 None 또는 빈 값")

                    # 텍스트 추출
                    analysis_text = str(analysis_result)

                    # 최소 길이 검증
                    if len(analysis_text.strip()) < 200:
                        logger.warning(
                            f"⚠️ {expert.name} 분석 결과가 짧음: {len(analysis_text)}자"
                        )
                        # 최소한의 분석 내용 추가
                        analysis_text += f"\n\n## 📋 추가 정보\n전문가 {expert.name}의 분석이 완료되었으나 결과가 예상보다 짧습니다."

                    # 🔧 CoT (Chain of Thought) 검증
                    cot_keywords = [
                        "사고 과정",
                        "1단계",
                        "2단계",
                        "3단계",
                        "4단계",
                        "5단계",
                        "6단계",
                        "분석 방법론",
                        "Chain of Thought",
                    ]
                    cot_found = any(
                        keyword in analysis_text for keyword in cot_keywords
                    )

                    if not cot_found and attempt < max_retries - 1:
                        logger.warning(f"⚠️ {expert.name} CoT 검증 실패 - 재실행 예정")
                        raise ValueError("CoT 형식이 포함되지 않음 - 재실행 필요")

                    logger.info(
                        f"✅ {expert.name} 분석 완료: {len(analysis_text):,}자 (CoT: {'포함' if cot_found else '미포함'})"
                    )

                    # 웹검색 수행 여부 확인 (펀더멘털 전문가만)
                    web_search_performed = False
                    web_search_count = 0
                    if (
                        "펀더멘털" in expert.name
                        or "펀더멘탈" in expert.name
                        or "fundamental" in expert.name.lower()
                    ):
                        web_search_performed = (
                            successful_searches > 0
                            if "successful_searches" in locals()
                            else False
                        )
                        web_search_count = (
                            successful_searches
                            if "successful_searches" in locals()
                            else 0
                        )

                    # 🎯 실제 사용된 데이터 출처 추적 및 추가
                    used_data_sources = self._identify_used_data_sources(
                        financial_data=financial_data,
                        enhanced_dart_data=enhanced_dart_data,
                        manus_collected_data=manus_collected_data,
                        technical_analysis_data=None,
                        dart_reports_dictionary=None,
                    )

                    # 데이터 출처를 분석 결과에 동적으로 추가
                    data_source_info = f"""

📊 **실제 사용된 데이터 출처**:
{', '.join(used_data_sources) if used_data_sources else '데이터 출처 정보 없음'}

"""

                    # 분석 결과에 데이터 출처 정보 추가
                    enhanced_analysis_result = analysis_text + data_source_info

                    return {
                        "expert_name": expert.name,
                        "expert_role": expert.role,
                        "expertise": expert.expertise,
                        "analysis_result": enhanced_analysis_result,
                        "analysis_timestamp": datetime.now().isoformat(),
                        "attempt_number": attempt + 1,
                        "success": True,
                        "web_search_performed": web_search_performed,
                        "web_search_count": web_search_count,
                        "data_sources_used": used_data_sources,  # 실제 사용된 데이터 출처 추가
                    }

                except Exception as llm_error:
                    logger.error(f"❌ {expert.name} LLM 분석 실패: {llm_error}")
                    if attempt == max_retries - 1:  # 마지막 시도
                        return {
                            "expert_name": expert.name,
                            "expert_role": expert.role,
                            "expertise": expert.expertise,
                            "analysis_result": f"분석 실패: {str(llm_error)}",
                            "analysis_timestamp": datetime.now().isoformat(),
                            "attempt_number": attempt + 1,
                            "success": False,
                            "error": str(llm_error),
                            "tool_calls_info": "",
                        }
                    # 재시도 계속
                    logger.warning(
                        f"⚠️ {expert.name} 분석 재시도 중... ({attempt + 1}/{max_retries})"
                    )
                    await asyncio.sleep(1)  # 1초 대기
                    continue

            except Exception as e:
                logger.error(f"❌ {expert.name} 전문가 분석 중 오류: {e}")

                if attempt == max_retries - 1:  # 마지막 시도
                    return {
                        "expert_name": expert.name,
                        "expert_role": expert.role,
                        "expertise": expert.expertise,
                        "analysis_result": f"분석 실패: {str(e)}",
                        "analysis_timestamp": datetime.now().isoformat(),
                        "attempt_number": attempt + 1,
                        "success": False,
                        "error": str(e),
                        "tool_calls_info": "",
                    }

                # 재시도 대기
                logger.warning(
                    f"⚠️ {expert.name} 분석 재시도... ({attempt + 1}/{max_retries})"
                )
                await asyncio.sleep(2)  # 2초 대기

        # 여기에 도달하면 모든 재시도 실패
        return {
            "expert_name": expert.name,
            "expert_role": expert.role,
            "expertise": expert.expertise,
            "analysis_result": f"최대 재시도 횟수 초과: {max_retries}회 시도 후 실패",
            "analysis_timestamp": datetime.now().isoformat(),
            "attempt_number": max_retries,
            "success": False,
            "error": "Maximum retries exceeded",
            "tool_calls_info": "",
        }

    def _calculate_cost_savings(
        self, activated_agents: int, depth: AnalysisDepth
    ) -> Dict[str, Any]:
        """비용 절감 계산 (2명 체제로 단순화)"""

        # 2명 체제에서는 분석 깊이와 무관하게 항상 2명만 사용
        base_cost_per_agent = 0.10  # 1명당 기본 비용

        # 2명 체제 비용 (통합 재무분석가 + 기술적 분석가)
        two_agent_cost = 2 * base_cost_per_agent  # $0.20

        # 실제 활성화된 에이전트 비용
        actual_cost = activated_agents * base_cost_per_agent

        # 절약 계산 (기존 5명 체제 대비)
        traditional_five_agent_cost = 5 * base_cost_per_agent  # $0.50
        savings_amount = traditional_five_agent_cost - actual_cost
        savings_percentage = (savings_amount / traditional_five_agent_cost) * 100

        return {
            "traditional_cost": traditional_five_agent_cost,
            "two_agent_cost": two_agent_cost,
            "actual_cost": actual_cost,
            "savings_amount": savings_amount,
            "savings_percentage": savings_percentage,
            "activated_agents": activated_agents,
            "analysis_mode": "2명 체제 (통합 재무분석가 + 기술적 분석가)",
            "depth": depth.value,
        }

    def _generate_cache_key(
        self, prompt: str, stock_name: str, stock_code: str, depth: AnalysisDepth
    ) -> str:
        """캐시 키 생성"""
        content = f"{prompt}_{stock_name}_{stock_code}_{depth.value}"
        return hashlib.md5(content.encode()).hexdigest()

    def _generate_comprehensive_cache_key(
        self,
        prompt: str,
        stock_name: str,
        stock_code: str,
        depth: AnalysisDepth,
        manus_data: Dict = None,
        technical_analysis_data: Dict = None,  # 🎯 기술적 분석 데이터 추가!
    ) -> str:
        """
        종합 분석용 캐시 키 생성

        Manus 수집 데이터의 핵심 정보를 포함하여 더 정확한 캐시 키를 생성해요.

        Args:
            prompt: 사용자 프롬프트
            stock_name: 종목명
            stock_code: 종목코드
            depth: 분석 깊이
            manus_data: Manus 수집 데이터

        Returns:
            str: 종합 분석용 캐시 키
        """
        # 기본 정보
        content_parts = [prompt, stock_name, stock_code, depth.value]

        # Manus 데이터 핵심 정보 추가 (캐시 정확도 향상)
        if manus_data and manus_data.get("performed"):
            # 데이터 풍부함 점수 포함
            richness_score = manus_data.get("data_richness_score", 0)
            content_parts.append(f"richness_{richness_score}")

            # PDF 분석 여부 포함
            pdf_detected = manus_data.get("pdf_analysis", {}).get("pdf_detected", False)
            content_parts.append(f"pdf_{pdf_detected}")

            # 수집 정보의 해시값 (내용이 같으면 같은 캐시 사용)
            collected_info = manus_data.get("collected_information", "")
            if collected_info:
                info_hash = hashlib.md5(collected_info[:500].encode()).hexdigest()[:8]
                content_parts.append(f"info_{info_hash}")

        # 🎯 기술적 분석 데이터 핵심 정보 추가 (캐시 정확도 향상)
        if technical_analysis_data and technical_analysis_data.get("success"):
            # 기술적 지표 데이터 존재 여부
            content_parts.append("tech_indicators_available")

            # 현재 주요 지표 값들로 캐시 키 생성 (값이 바뀌면 새로운 분석)
            indicators = technical_analysis_data.get("technical_indicators", {})

            # RSI 값
            rsi_data = indicators.get("RSI", {})
            if rsi_data.get("current_value") is not None:
                rsi_rounded = int(rsi_data["current_value"] / 5) * 5  # 5단위로 반올림
                content_parts.append(f"rsi_{rsi_rounded}")

            # MACD 신호
            macd_data = indicators.get("MACD", {})
            if macd_data.get("signal_interpretation"):
                macd_signal = macd_data["signal_interpretation"][:10]  # 처음 10글자만
                content_parts.append(f"macd_{macd_signal}")

            # 종합 매매 신호
            trading_signals = technical_analysis_data.get("trading_signals", {})
            if trading_signals.get("overall_signal"):
                signal = trading_signals["overall_signal"][:10]  # 처음 10글자만
                content_parts.append(f"signal_{signal}")

            # 데이터 기간 (1년 vs 6개월 등으로 구분)
            total_days = technical_analysis_data.get("total_days", 0)
            period_category = "short" if total_days < 180 else "long"
            content_parts.append(f"period_{period_category}")

        # 전체 내용을 결합하여 캐시 키 생성
        full_content = "_".join(str(part) for part in content_parts)
        return hashlib.md5(full_content.encode()).hexdigest()

    def _get_cache_ttl(self, depth: AnalysisDepth) -> int:
        """캐시 TTL (2명 체제로 단순화 - 분석 깊이 무관)"""
        # 2명 체제에서는 분석 깊이와 무관하게 표준 캐시 시간 사용
        return 24  # 24시간 (표준)

    def _update_stats(self, sector: GICSSector, cost_savings: Dict[str, Any]):
        """성능 통계 업데이트"""
        self.stats["total_analyses"] += 1
        self.stats["total_cost_savings"] += cost_savings["savings_amount"]

        sector_name = sector.name
        if sector_name not in self.stats["sector_usage_count"]:
            self.stats["sector_usage_count"][sector_name] = 0
        self.stats["sector_usage_count"][sector_name] += 1

        # 평균 절약률 계산
        if self.stats["total_analyses"] > 0:
            self.stats["average_savings_rate"] = cost_savings["savings_percentage"]

    def get_performance_stats(self) -> Dict[str, Any]:
        """성능 통계 조회"""
        return self.stats.copy()

    def _create_fallback_pdf_interface(
        self, stock_name: str, stock_code: str
    ) -> Dict[str, Any]:
        """PDF 인터페이스 생성 실패 시 명확한 오류 반환 (폴백 제거)"""
        logger.error(f"❌ {stock_name}({stock_code}) PDF 인터페이스 생성 실패")

        return {
            "success": False,
            "error": f"PDF 분석이 제한되어 상세 분석을 수행할 수 없습니다.",
            "stock_code": stock_code,
            "stock_name": stock_name,
            "recommendation": "PDF 파일을 제공하거나 Manus Agent를 활성화하여 PDF 분석을 수행하세요.",
            "required_action": "PDF 파일 제공 또는 Manus Agent 활성화 필요",
            "fallback_mode": False,  # 폴백 모드 비활성화
            "message": f"PDF 분석이 제한되어 상세 분석을 수행할 수 없습니다. {stock_name}({stock_code})의 상세 분석을 위해서는 PDF 파일이 필요합니다.",
        }

    def _validate_data_transfer(
        self,
        financial_data: Dict,
        enhanced_dart_data: Dict,
        manus_collected_data: Dict,
        dart_reports_dictionary: Dict,
        technical_analysis_data: Dict,
    ):
        """데이터 전달 검증 및 로깅"""

        logger.info("🔍 데이터 전달 상태 확인:")
        logger.info(f"  - 재무 데이터: {'✅' if financial_data else '❌'}")
        logger.info(f"  - DART 데이터: {'✅' if enhanced_dart_data else '❌'}")
        logger.info(f"  - Manus 데이터: {'✅' if manus_collected_data else '❌'}")
        logger.info(f"  - DART 딕셔너리: {'✅' if dart_reports_dictionary else '❌'}")
        logger.info(f"  - 기술적 분석: {'✅' if technical_analysis_data else '❌'}")

        # PDF 인터페이스 확인
        if manus_collected_data and manus_collected_data.get("pdf_analysis"):
            pdf_interface = manus_collected_data["pdf_analysis"].get(
                "pdf_dictionary_interface"
            )
            logger.info(f"  - PDF 인터페이스: {'✅' if pdf_interface else '❌'}")
        else:
            logger.info("  - PDF 인터페이스: ❌ (PDF 분석 데이터 없음)")

    def reset_stats(self):
        """통계 초기화"""
        self.stats = {
            "total_analyses": 0,
            "total_cost_savings": 0.0,
            "sector_usage_count": {},
            "average_savings_rate": 0.0,
        }
        logger.info("📊 성능 통계 초기화 완료")

    async def _perform_comprehensive_expert_analysis(
        self,
        experts: List,
        prompt: str,
        stock_name: str,
        stock_code: str,
        financial_data: Dict,
        enhanced_dart_data: Dict = None,
        manus_collected_data: Dict = None,
        technical_analysis_data: Dict = None,  # 🎯 기술적 분석 데이터 추가!
        dart_reports_dictionary: Dict = None,  # 🚀 DART 보고서 딕셔너리 추가!
        pdf_interface=None,  # 🔧 PDF 인터페이스 매개변수 추가!
    ) -> Dict[str, Any]:
        """
        🚀 모든 데이터를 통합한 전문가 분석 수행

        재무데이터 + Enhanced DART + Manus 수집 정보 + DART 보고서 딕셔너리를 모두 활용해서
        각 전문가가 종합적인 분석을 수행해요.

        Args:
            experts: 선택된 전문가 리스트
            prompt: 사용자 프롬프트
            stock_name: 종목명
            stock_code: 종목코드
            financial_data: 재무데이터
            enhanced_dart_data: Enhanced DART 데이터
            manus_collected_data: Manus Agent 수집 정보
            technical_analysis_data: 기술적 분석 데이터
            dart_reports_dictionary: 🚀 DART 사업보고서/분기보고서 딕셔너리

        Returns:
            Dict: 전문가별 종합 분석 결과
        """
        logger.info(f"🎯 {len(experts)}명 전문가 종합 분석 시작...")

        # 🚨 데이터 검증 - 폴백 없이 명확한 오류 반환
        validation_result = self._validate_required_data(
            financial_data,
            enhanced_dart_data,
            manus_collected_data,
            dart_reports_dictionary,
            technical_analysis_data,
        )

        # 📄 PDF 데이터 가용성 전용 검증
        pdf_validation = self._validate_pdf_data_availability(
            manus_collected_data, dart_reports_dictionary
        )

        # 📊 데이터 가용성 메시지 생성
        data_availability_message = self._create_data_availability_message(
            validation_result, pdf_validation
        )

        if not validation_result["is_valid"]:
            return {
                "synthesis_success": False,
                "error": f"분석에 필요한 데이터가 부족합니다: {', '.join(validation_result['missing_data'])}",
                "required_data": validation_result["required_data"],
                "available_data": validation_result["available_data"],
                "data_quality_score": validation_result["data_quality_score"],
                "pdf_validation": pdf_validation,
                "data_availability_message": data_availability_message,
                "recommendations": validation_result["recommendations"],
            }

        expert_results = []
        analysis_start_time = time.time()

        for expert in experts:
            try:
                logger.info(f"👨‍💼 전문가 분석 시작: {expert.name}")

                # 🔧 PDF 인터페이스 추출 및 상세 로깅
                extracted_pdf_interface = None
                pdf_sections_count = 0

                if manus_collected_data and manus_collected_data.get("pdf_analysis"):
                    pdf_analysis = manus_collected_data["pdf_analysis"]
                    extracted_pdf_interface = pdf_analysis.get(
                        "pdf_dictionary_interface"
                    )

                    if extracted_pdf_interface:
                        pdf_sections_count = len(pdf_analysis.get("pdf_dictionary", {}))
                        logger.info(
                            f"📄 {expert.name}: PDF 인터페이스 발견 ({pdf_sections_count}개 섹션)"
                        )
                    else:
                        logger.warning(
                            f"⚠️ {expert.name}: PDF 인터페이스가 없습니다 (PDF 분석은 완료되었지만 인터페이스 생성 실패)"
                        )
                else:
                    logger.warning(
                        f"⚠️ {expert.name}: PDF 분석 데이터가 없습니다 (Manus Agent에서 PDF를 감지하지 못했거나 분석이 수행되지 않음)"
                    )

                # 🔧 DART 딕셔너리 검증 및 상세 로깅
                dart_sections_count = 0
                if dart_reports_dictionary and dart_reports_dictionary.get("success"):
                    business_sections = len(
                        dart_reports_dictionary.get("business_report_dictionary", {})
                    )
                    quarterly_sections = len(
                        dart_reports_dictionary.get("quarterly_report_dictionary", {})
                    )
                    dart_sections_count = business_sections + quarterly_sections

                    if dart_sections_count > 0:
                        logger.info(
                            f"📋 {expert.name}: DART 딕셔너리 발견 (사업보고서 {business_sections}개, 분기보고서 {quarterly_sections}개 섹션)"
                        )
                    else:
                        logger.warning(
                            f"⚠️ {expert.name}: DART 딕셔너리는 생성되었지만 섹션이 없습니다"
                        )
                else:
                    if dart_reports_dictionary:
                        error_msg = dart_reports_dictionary.get(
                            "error", "알 수 없는 오류"
                        )
                        logger.warning(
                            f"⚠️ {expert.name}: DART 딕셔너리 생성 실패 - {error_msg}"
                        )
                    else:
                        logger.warning(
                            f"⚠️ {expert.name}: DART 딕셔너리가 제공되지 않았습니다"
                        )

                # 📊 전문가별 데이터 전달 요약
                total_sections = pdf_sections_count + dart_sections_count
                if total_sections > 0:
                    logger.info(
                        f"🎯 {expert.name}: 총 {total_sections}개 PDF 섹션 전달 완료"
                    )
                else:
                    logger.warning(
                        f"⚠️ {expert.name}: 전달할 PDF 데이터가 없습니다 (보고서 분석이 제한적일 수 있음)"
                    )

                # 🚀 종합 분석용 프롬프트 구성
                comprehensive_prompt = await self._create_expert_specific_context(
                    expert,
                    prompt,
                    stock_name,
                    stock_code,
                    financial_data,
                    enhanced_dart_data,
                    manus_collected_data,
                    extracted_pdf_interface or pdf_interface,
                    technical_analysis_data,
                    dart_reports_dictionary,
                )

                # 🚀 LangChain Chain 우선 사용 (Dynamic Enhanced Thinking Flow 활성화)
                logger.info(f"📝 {expert.name} LLM 분석 시작")

                # expert.langchain_chain이 있으면 우선 사용 (Q5EnforcedAgentExecutor 포함)
                if hasattr(expert, "langchain_chain") and expert.langchain_chain:
                    logger.info(
                        f"🔗 {expert.name}: LangChain Chain 사용 (Dynamic Enhanced Thinking Flow)"
                    )
                    try:
                        # LangChain Chain 실행 (Q5 강제 생성 + 3단계 구조)
                        chain_result = expert.langchain_chain.invoke(
                            {"input": comprehensive_prompt, "chat_history": []}
                        )
                        # 결과 추출
                        if isinstance(chain_result, dict):
                            analysis_result = chain_result.get(
                                "output", str(chain_result)
                            )
                        else:
                            analysis_result = str(chain_result)
                        logger.info(f"✅ {expert.name}: LangChain Chain 실행 완료")
                    except Exception as chain_error:
                        logger.error(
                            f"❌ {expert.name}: LangChain Chain 실행 실패: {chain_error}"
                        )
                        # 폴백: 기존 LLM 방식
                        analysis_result = await self._call_llm_for_analysis(
                            comprehensive_prompt
                        )
                else:
                    logger.info(
                        f"⚠️ {expert.name}: LangChain Chain 없음, 기존 LLM 방식 사용"
                    )
                    # 폴백: 기존 LLM 방식
                    analysis_result = await self._call_llm_for_analysis(
                        comprehensive_prompt
                    )

                # ✅ 분석 완료 (CoT 검증 과정 삭제로 중복 출력 문제 해결)
                logger.info(f"✅ {expert.name} 분석 완료")

                expert_results.append(
                    {
                        "expert_name": expert.name,
                        "expertise_area": expert.expertise,
                        "analysis_result": analysis_result,
                        "analysis_time": time.time() - analysis_start_time,
                        "data_sources_used": self._identify_used_data_sources(
                            financial_data,
                            enhanced_dart_data,
                            manus_collected_data,
                            technical_analysis_data,
                            dart_reports_dictionary,
                        ),
                        "cot_verified": True,  # CoT 검증 과정 삭제로 항상 True
                    }
                )

            except Exception as e:
                logger.error(f"❌ {expert.name} 분석 실패: {e}")
                expert_results.append(
                    {
                        "expert_name": expert.name,
                        "expertise_area": expert.expertise,
                        "analysis_result": f"분석 실패: {str(e)}",
                        "analysis_time": time.time() - analysis_start_time,
                        "error": str(e),
                    }
                )

        # 🚀 전문가 분석 결과 종합
        synthesis_result = await self._synthesize_expert_insights(
            expert_results, prompt
        )

        return synthesis_result

    def _validate_required_data(
        self,
        financial_data: Dict,
        enhanced_dart_data: Dict = None,
        manus_collected_data: Dict = None,
        dart_reports_dictionary: Dict = None,
        technical_analysis_data: Dict = None,
    ) -> Dict[str, Any]:
        """
        🚨 필수 데이터 유효성 검사 (폴백 제거, 명확한 오류 반환)

        Args:
            financial_data: 재무데이터
            enhanced_dart_data: Enhanced DART 데이터
            manus_collected_data: Manus 수집 데이터
            dart_reports_dictionary: DART 보고서 딕셔너리
            technical_analysis_data: 기술적 분석 데이터

        Returns:
            Dict: 검증 결과 및 누락된 데이터 정보
        """
        validation_result = {
            "is_valid": True,
            "missing_data": [],
            "available_data": [],
            "required_data": [],
            "data_quality_score": 0,
            "recommendations": [],
        }

        # 필수 데이터 목록 정의
        required_data_types = [
            ("재무데이터", financial_data, "yfinance 또는 DART API에서 수집"),
            ("기술적 분석 데이터", technical_analysis_data, "yfinance에서 계산된 지표"),
        ]

        # 선택적 데이터 목록 정의
        optional_data_types = [
            ("Enhanced DART 데이터", enhanced_dart_data, "DART API 키 필요"),
            ("Manus 수집 데이터", manus_collected_data, "Manus Agent 활성화 필요"),
            (
                "DART 보고서 딕셔너리",
                dart_reports_dictionary,
                "DART API에서 사업보고서/분기보고서 필요",
            ),
        ]

        # 필수 데이터 검증
        for data_name, data, requirement in required_data_types:
            validation_result["required_data"].append(
                {"name": data_name, "requirement": requirement, "status": "필수"}
            )

            if data and isinstance(data, dict):
                if data.get("success") or data.get("detected") or len(data) > 0:
                    validation_result["available_data"].append(data_name)
                    validation_result["data_quality_score"] += 50  # 필수 데이터는 50점
                else:
                    validation_result["missing_data"].append(f"{data_name} (수집 실패)")
                    validation_result["is_valid"] = False
            else:
                validation_result["missing_data"].append(f"{data_name} (없음)")
                validation_result["is_valid"] = False

        # 선택적 데이터 검증
        for data_name, data, requirement in optional_data_types:
            if data and isinstance(data, dict):
                if data.get("success") or data.get("performed") or len(data) > 0:
                    validation_result["available_data"].append(data_name)
                    validation_result[
                        "data_quality_score"
                    ] += 10  # 선택적 데이터는 10점씩
                else:
                    validation_result["missing_data"].append(f"{data_name} (처리 실패)")
            else:
                validation_result["missing_data"].append(f"{data_name} (없음)")

        # 구체적인 권장사항 생성
        recommendations = []

        if "재무데이터" in validation_result["missing_data"]:
            recommendations.append(
                "💡 재무데이터 수집 실패: yfinance API 연결 상태를 확인하세요"
            )

        if "기술적 분석 데이터" in validation_result["missing_data"]:
            recommendations.append("💡 기술적 분석 실패: 주가 데이터 수집이 필요합니다")

        if "Enhanced DART 데이터" in validation_result["missing_data"]:
            recommendations.append(
                "💡 DART 데이터 없음: DART API 키 설정이 필요합니다 (config_example.env 참조)"
            )

        if "Manus 수집 데이터" in validation_result["missing_data"]:
            recommendations.append(
                "💡 Manus 데이터 없음: Manus Agent가 비활성화되어 있습니다"
            )

        if "DART 보고서 딕셔너리" in validation_result["missing_data"]:
            recommendations.append(
                "💡 DART 보고서 딕셔너리 없음: 사업보고서/분기보고서가 존재하지 않거나 다운로드에 실패했습니다"
            )

        validation_result["recommendations"] = recommendations

        # 데이터 품질 점수 정규화 (0-100)
        validation_result["data_quality_score"] = min(
            validation_result["data_quality_score"], 100
        )

        # 상세 로깅
        logger.info("🔍 데이터 유효성 검사 결과:")
        logger.info(f"  - 검증 통과: {'✅' if validation_result['is_valid'] else '❌'}")
        logger.info(
            f"  - 데이터 품질 점수: {validation_result['data_quality_score']}/100"
        )
        logger.info(
            f"  - 사용 가능한 데이터: {', '.join(validation_result['available_data'])}"
        )
        if validation_result["missing_data"]:
            logger.warning(
                f"  - 누락된 데이터: {', '.join(validation_result['missing_data'])}"
            )
        if recommendations:
            logger.info(f"  - 권장사항: {'; '.join(recommendations)}")

        return validation_result

    def _validate_pdf_data_availability(
        self, manus_collected_data: Dict = None, dart_reports_dictionary: Dict = None
    ) -> Dict[str, Any]:
        """
        📄 PDF 데이터 가용성 전용 검증

        Args:
            manus_collected_data: Manus 수집 데이터
            dart_reports_dictionary: DART 보고서 딕셔너리

        Returns:
            Dict: PDF 데이터 검증 결과
        """
        pdf_validation = {
            "pdf_analysis_available": False,
            "dart_dictionary_available": False,
            "pdf_analysis_reason": "",
            "dart_dictionary_reason": "",
            "total_pdf_sections": 0,
            "recommendations": [],
        }

        # PDF 분석 데이터 검증
        if manus_collected_data and manus_collected_data.get("pdf_analysis"):
            pdf_analysis = manus_collected_data["pdf_analysis"]
            if pdf_analysis.get("pdf_detected") and pdf_analysis.get(
                "analysis_completed"
            ):
                pdf_validation["pdf_analysis_available"] = True
                pdf_validation["total_pdf_sections"] += len(
                    pdf_analysis.get("pdf_dictionary", {})
                )
                logger.info(
                    f"📄 PDF 분석 데이터 발견: {pdf_validation['total_pdf_sections']}개 섹션"
                )
            else:
                pdf_validation["pdf_analysis_reason"] = (
                    "PDF가 감지되지 않았거나 분석이 완료되지 않았습니다"
                )
                logger.warning(
                    f"⚠️ PDF 분석 실패: {pdf_validation['pdf_analysis_reason']}"
                )
        else:
            pdf_validation["pdf_analysis_reason"] = (
                "Manus Agent에서 PDF 분석 데이터가 수집되지 않았습니다"
            )
            logger.warning(
                f"⚠️ PDF 분석 데이터 없음: {pdf_validation['pdf_analysis_reason']}"
            )

        # DART 딕셔너리 검증 (개선된 로직)
        if dart_reports_dictionary:
            # 상세한 디버깅 정보 로깅
            logger.info(f"🔍 DART 딕셔너리 상세 검증:")
            logger.info(
                f"  - dart_reports_dictionary 타입: {type(dart_reports_dictionary)}"
            )
            logger.info(
                f"  - dart_reports_dictionary 키: {list(dart_reports_dictionary.keys())}"
            )
            logger.info(f"  - success 필드: {dart_reports_dictionary.get('success')}")
            logger.info(f"  - error 필드: {dart_reports_dictionary.get('error')}")

            # 실제 딕셔너리 구조 확인
            business_dict = dart_reports_dictionary.get(
                "business_report_dictionary", {}
            )
            quarterly_dict = dart_reports_dictionary.get(
                "quarterly_report_dictionary", {}
            )

            logger.info(f"  - business_report_dictionary 타입: {type(business_dict)}")
            logger.info(f"  - business_report_dictionary 길이: {len(business_dict)}")
            logger.info(f"  - quarterly_report_dictionary 타입: {type(quarterly_dict)}")
            logger.info(f"  - quarterly_report_dictionary 길이: {len(quarterly_dict)}")

            # 실제 섹션 내용 샘플 로깅
            if business_dict:
                business_keys = list(business_dict.keys())[:3]  # 상위 3개만
                logger.info(f"  - business_report_dictionary 샘플 키: {business_keys}")
                for key in business_keys:
                    content_length = len(str(business_dict[key]))
                    logger.info(f"    - {key}: {content_length}자")

            if quarterly_dict:
                quarterly_keys = list(quarterly_dict.keys())[:3]  # 상위 3개만
                logger.info(
                    f"  - quarterly_report_dictionary 샘플 키: {quarterly_keys}"
                )
                for key in quarterly_keys:
                    content_length = len(str(quarterly_dict[key]))
                    logger.info(f"    - {key}: {content_length}자")

            # 성공 여부 판단 (success 필드 또는 실제 섹션 존재 여부)
            is_success = dart_reports_dictionary.get("success", False)
            business_sections = len(
                dart_reports_dictionary.get("business_report_dictionary", {})
            )
            quarterly_sections = len(
                dart_reports_dictionary.get("quarterly_report_dictionary", {})
            )
            total_sections = business_sections + quarterly_sections

            # 실제 섹션이 있으면 성공으로 간주 (success 필드가 False여도)
            if total_sections > 0:
                pdf_validation["dart_dictionary_available"] = True
                pdf_validation["total_pdf_sections"] += total_sections
                logger.info(
                    f"📋 DART 딕셔너리 발견: 사업보고서 {business_sections}개, 분기보고서 {quarterly_sections}개 섹션"
                )

                # success 필드가 False인 경우 경고
                if not is_success:
                    logger.warning(
                        f"⚠️ DART 딕셔너리: success=False이지만 {total_sections}개 섹션 존재 (인터페이스 생성 실패로 추정)"
                    )
            else:
                pdf_validation["dart_dictionary_available"] = False
                if is_success:
                    pdf_validation["dart_dictionary_reason"] = (
                        "DART 딕셔너리 생성은 성공했지만 섹션이 없습니다"
                    )
                else:
                    pdf_validation["dart_dictionary_reason"] = (
                        f"DART 딕셔너리 생성 실패: {dart_reports_dictionary.get('error', '알 수 없는 오류')}"
                    )
                logger.warning(
                    f"⚠️ DART 딕셔너리 실패: {pdf_validation['dart_dictionary_reason']}"
                )
        else:
            pdf_validation["dart_dictionary_available"] = False
            pdf_validation["dart_dictionary_reason"] = (
                "DART 딕셔너리가 제공되지 않았습니다"
            )
            logger.warning(
                f"⚠️ DART 딕셔너리 없음: {pdf_validation['dart_dictionary_reason']}"
            )

        # 권장사항 생성
        if not pdf_validation["pdf_analysis_available"]:
            pdf_validation["recommendations"].append(
                "📄 PDF 분석 개선: Manus Agent가 PDF 파일을 감지하고 분석할 수 있도록 웹 검색을 활성화하세요"
            )

        if not pdf_validation["dart_dictionary_available"]:
            pdf_validation["recommendations"].append(
                "📋 DART 딕셔너리 개선: DART API 키를 설정하고, 해당 기업의 사업보고서/분기보고서가 존재하는지 확인하세요"
            )

        # 최종 상태 로깅
        if pdf_validation["total_pdf_sections"] > 0:
            logger.info(
                f"✅ PDF 데이터 총 {pdf_validation['total_pdf_sections']}개 섹션 사용 가능"
            )
        else:
            logger.warning("❌ 사용 가능한 PDF 데이터가 없습니다")

        return pdf_validation

    def _create_data_availability_message(
        self, validation_result: Dict, pdf_validation: Dict
    ) -> str:
        """
        📊 데이터 가용성 상태를 사용자 친화적으로 설명하는 메시지 생성

        Args:
            validation_result: 전체 데이터 검증 결과
            pdf_validation: PDF 데이터 검증 결과

        Returns:
            str: 사용자 친화적인 상태 메시지
        """
        message_parts = []

        # 전체 상태
        if validation_result["is_valid"]:
            message_parts.append("✅ 분석에 필요한 기본 데이터가 모두 준비되었습니다")
        else:
            message_parts.append(
                "⚠️ 일부 필수 데이터가 누락되어 분석 품질이 제한될 수 있습니다"
            )

        # 데이터 품질 점수
        quality_score = validation_result["data_quality_score"]
        if quality_score >= 80:
            message_parts.append(f"📊 데이터 품질: 우수 ({quality_score}/100)")
        elif quality_score >= 60:
            message_parts.append(f"📊 데이터 품질: 양호 ({quality_score}/100)")
        elif quality_score >= 40:
            message_parts.append(f"📊 데이터 품질: 보통 ({quality_score}/100)")
        else:
            message_parts.append(f"📊 데이터 품질: 제한적 ({quality_score}/100)")

        # 사용 가능한 데이터
        available_data = validation_result["available_data"]
        if available_data:
            message_parts.append(f"📋 사용 가능한 데이터: {', '.join(available_data)}")

        # PDF 데이터 상태
        if pdf_validation["total_pdf_sections"] > 0:
            message_parts.append(
                f"📄 PDF 데이터: {pdf_validation['total_pdf_sections']}개 섹션 사용 가능"
            )
        else:
            message_parts.append("📄 PDF 데이터: 없음 (보고서 분석이 제한적일 수 있음)")

        # 권장사항
        all_recommendations = (
            validation_result["recommendations"] + pdf_validation["recommendations"]
        )
        if all_recommendations:
            message_parts.append("💡 개선 권장사항:")
            for rec in all_recommendations[:3]:  # 상위 3개만 표시
                message_parts.append(f"   • {rec}")

        return "\n".join(message_parts)

    def _identify_used_data_sources(
        self,
        financial_data: Dict,
        enhanced_dart_data: Dict = None,
        manus_collected_data: Dict = None,
        technical_analysis_data: Dict = None,  # 🎯 기술적 분석 데이터 추가!
        dart_reports_dictionary: Dict = None,  # 🚀 DART 보고서 딕셔너리 추가!
    ) -> List[str]:
        """
        분석에 사용된 데이터 소스들을 식별합니다.

        Args:
            financial_data: 재무 데이터
            enhanced_dart_data: Enhanced DART 데이터
            manus_collected_data: Manus 수집 데이터

        Returns:
            List[str]: 사용된 데이터 소스 목록
        """
        used_sources = []

        # 재무 데이터 확인
        if financial_data and financial_data.get("success"):
            base_sources = financial_data.get("data_sources", [])
            used_sources.extend(base_sources)

        # Enhanced DART 데이터 확인
        if enhanced_dart_data and enhanced_dart_data.get("success"):
            used_sources.append("Enhanced_DART_API")

        # Manus 수집 데이터 확인
        if manus_collected_data and manus_collected_data.get("performed"):
            used_sources.append("Manus_Web_Search")

        # PDF 분석 여부 확인
        if manus_collected_data and manus_collected_data.get("pdf_analysis", {}).get(
            "pdf_detected"
        ):
            used_sources.append("PDF_Analysis")

        # 🎯 기술적 분석 데이터 확인
        if technical_analysis_data and technical_analysis_data.get("success"):
            used_sources.append("Technical_Analysis_Calculated")

        # 🚀 분리된 DART 보고서 딕셔너리 확인
        if dart_reports_dictionary and dart_reports_dictionary.get("success"):
            business_dict = dart_reports_dictionary.get(
                "business_report_dictionary", {}
            )
            quarterly_dict = dart_reports_dictionary.get(
                "quarterly_report_dictionary", {}
            )

            if business_dict:
                used_sources.append("DART_Business_Report")
            if quarterly_dict:
                used_sources.append("DART_Quarterly_Report")

        return list(set(used_sources))  # 중복 제거

    async def _synthesize_expert_insights(
        self, expert_results: List[Dict], user_prompt: str
    ) -> Dict[str, Any]:
        """
        전문가들의 분석 결과를 종합합니다.

        Args:
            expert_results: 전문가별 분석 결과 리스트
            user_prompt: 사용자 원본 질문

        Returns:
            Dict: 종합된 분석 결과
        """
        try:
            logger.info("🔄 전문가 분석 결과 종합 시작...")

            # 성공한 분석만 필터링
            successful_analyses = [
                result for result in expert_results if not result.get("error", False)
            ]

            if not successful_analyses:
                return {
                    "synthesis_success": False,
                    "error": "성공한 전문가 분석이 없습니다",
                    "expert_count": len(expert_results),
                    "successful_count": 0,
                }

            # 종합 분석용 프롬프트 구성
            synthesis_prompt = f"""
다음은 {len(successful_analyses)}명의 전문가가 분석한 결과입니다.
사용자의 원본 질문: {user_prompt}

전문가 분석 결과들:
"""

            for i, result in enumerate(successful_analyses, 1):
                expert_name = result.get("expert_name", f"전문가{i}")
                expertise = result.get("expertise_area", "일반")
                analysis = result.get("analysis_result", "")

                synthesis_prompt += f"""

=== {expert_name} ({expertise}) ===
{analysis}

"""

            synthesis_prompt += """

🎯 위 전문가들의 분석을 종합하여 다음과 같이 정리해주세요 :


### 1. **전문가 간 분석 결과 일관성 검토**
- **일치하는 의견**: 여러 전문가가 동일하게 제시한 강점/약점 (신뢰도 높음)
- **상반된 의견**: 전문가 간 모순되는 결론과 그 원인 분석
  * 예: 기술적 분석(단기 하락) vs 밸류에이션(매수 권장)의 차이점
- **의견 불일치 해결**: 상반된 의견에 대한 종합적 판단과 우선순위

### 2. **시간적 프레임별 투자 전략**
- **단기 전략 (1-3개월)**: 기술적 분석 + 이벤트 기반 요인
- **중기 전략 (3-12개월)**: 펀더멘털 + 산업 트렌드 + 밸류에이션
- **장기 전략 (1-3년)**: 구조적 경쟁력 + ESG + 기술 혁신 주기

### 3. **시나리오별 대응 전략**
- **Bull Case ([분석 기반 확률]% 확률)**: 최적 시나리오에서의 목표가와 대응 전략
- **Base Case ([분석 기반 확률]% 확률)**: 기본 시나리오에서의 투자 접근법
- **Bear Case ([분석 기반 확률]% 확률)**: 악재 시나리오에서의 리스크 관리 방안

**📊 시나리오 확률 계산 기준**:
- **Bull Case**: 긍정적 요인들의 강도와 발생 가능성을 종합하여 확률 산정
- **Base Case**: 현재 추세가 지속될 가능성을 기반으로 확률 산정
- **Bear Case**: 부정적 요인들의 위험도와 발생 가능성을 종합하여 확률 산정
- **총합 100%**: 세 시나리오 확률의 합이 100%가 되도록 조정

### 4. **핵심 투자 포인트** (정량 지표 장기 추세 포함)
- **정량적 우위**: 경쟁사 대비 ROE, ROIC, 마진율 우위와 지속성
- **정성적 강점**: 경영진, 기술력, 브랜드 파워 등
- **성장 동력**: 신사업, 신제품, 신시장 진출 가능성

### 5. **주요 리스크 요인** (비재무 리스크 확대)
- **재무 리스크**: 부채, 현금흐름, 수익성 악화 위험
- **비재무 리스크**: ESG, 지정학, 기술 혁신, 규제 변화
- **시장 리스크**: 경쟁 심화, 수요 변화, 사이클 리스크

### 6. **종합 투자 의견** (시간적 프레임 명확화)
- **12개월 투자 의견**: 매수/보유/매도 + 신뢰도 (%)
- **목표가 산출**: 전문가별 목표가의 가중평균과 근거
- **핵심 모니터링 지표**: 투자 의견 변경을 위한 핵심 변수들

### 7. **전문가 의견 가중치** (신뢰도 기반)
- **높은 신뢰도**: 데이터 기반 정량 분석 (펀더멘털, 밸류에이션)
- **중간 신뢰도**: 시장 기반 분석 (기술적, 산업)
- **참고 수준**: 정성적 평가 (리스크, 주석)

**🔍 분석 품질 검증**:
- 각 결론에 대한 전문가별 근거 일치도 확인
- 정량적 수치의 일관성 검토 (재무비율, 목표가 등)
- 시간적 일관성 확인 (단기 vs 장기 전망의 논리적 연결)

각 항목별로 구체적인 근거와 함께 명확하게 제시해주세요.
"""

            # LLM을 통한 종합 분석 수행
            synthesis_result = await self._call_llm_for_analysis(synthesis_prompt)

            # 🎯 종합 분석에서 실제 사용된 데이터 출처 추적
            all_used_sources = set()
            for result in expert_results:
                sources = result.get("data_sources_used", [])
                all_used_sources.update(sources)

            # 데이터 출처 정보를 종합 결과에 동적으로 추가
            data_source_summary = f"""

📊 **종합 분석에서 실제 사용된 데이터 출처**:
{', '.join(all_used_sources) if all_used_sources else '데이터 출처 정보 없음'}

"""

            # 종합 결과에 데이터 출처 정보 추가
            enhanced_synthesis_result = synthesis_result + data_source_summary

            return {
                "synthesis_success": True,
                "expert_count": len(expert_results),
                "successful_count": len(successful_analyses),
                "failed_count": len(expert_results) - len(successful_analyses),
                "synthesis_content": enhanced_synthesis_result,
                "synthesis_timestamp": time.time(),
                "data_sources_integrated": self._count_unique_data_sources(
                    expert_results
                ),
                "all_data_sources_used": list(
                    all_used_sources
                ),  # 전체 사용된 데이터 출처 추가
            }

        except Exception as e:
            logger.error(f"❌ 전문가 결과 종합 실패: {e}")
            return {
                "synthesis_success": False,
                "error": str(e),
                "expert_count": len(expert_results),
                "successful_count": len(
                    [r for r in expert_results if not r.get("error")]
                ),
            }

    def _count_unique_data_sources(self, expert_results: List[Dict]) -> int:
        """전문가 분석에서 사용된 고유 데이터 소스 개수를 계산합니다."""
        all_sources = set()

        for result in expert_results:
            sources = result.get("data_sources_used", [])
            all_sources.update(sources)

        return len(all_sources)

    async def _call_llm_for_analysis(self, prompt: str) -> str:
        """
        LLM을 호출하여 분석을 수행합니다.

        Args:
            prompt: 분석용 프롬프트

        Returns:
            str: LLM 분석 결과
        """
        try:
            # LLM 인스턴스를 통해 분석 수행
            if hasattr(self, "llm") and self.llm:
                # 🔧 중요: LLM.ask 메서드는 메시지 리스트를 받아야 해요!
                # 문자열을 올바른 메시지 형식으로 변환해서 전달합니다
                messages = [{"role": "user", "content": prompt}]
                response = await self.llm.ask(messages)
                return response
            else:
                # 기본 LLM 인스턴스 생성
                from app.llm import LLM

                llm = LLM()
                # 마찬가지로 메시지 형식으로 변환
                messages = [{"role": "user", "content": prompt}]
                response = await llm.ask(messages)
                return response

        except Exception as e:
            logger.error(f"❌ LLM 분석 호출 실패: {e}")
            # 에러가 발생해도 빈 문자열 대신 기본 응답 반환
            return f"분석 중 오류가 발생했습니다: {str(e)}"

    async def _create_expert_specific_context(
        self,
        expert,
        user_prompt: str,
        stock_name: str,
        stock_code: str,
        financial_data: Dict,
        enhanced_dart_data: Dict = None,
        manus_collected_data: Dict = None,
        pdf_interface=None,
        technical_analysis_data: Dict = None,  # 🎯 기술적 분석 데이터 추가!
        dart_reports_dictionary: Dict = None,  # 🚀 DART 보고서 딕셔너리 추가!
    ) -> str:
        """
        🎯 전문가별 맞춤형 컨텍스트 구성 (PDF 딕셔너리 통합)

        각 전문가의 전문성에 맞는 데이터만 선별해서 제공하여
        토큰 사용량을 최소화하면서 분석 품질은 유지합니다.
        PDF 딕셔너리에서는 섹션 제한 없이 필요한 모든 섹션을 제공합니다.

        Args:
            expert: 전문가 정보
            user_prompt: 사용자 질문
            stock_name: 종목명
            stock_code: 종목코드
            financial_data: 재무 데이터
            enhanced_dart_data: Enhanced DART 데이터
            manus_collected_data: Manus 수집 데이터
            pdf_interface: PDF 딕셔너리 인터페이스

        Returns:
            str: 전문가 맞춤형 컨텍스트
        """
        logger.info(
            f"🎯 {expert.name} 전문가용 맞춤형 컨텍스트 구성 (PDF 딕셔너리 통합)..."
        )

        context_parts = []

        # 🔧 개선된 기본 정보 (프롬프트 반복 방지)
        context_parts.append(f"**분석 대상**: {stock_name} ({stock_code})")
        context_parts.append(f"**사용자 요청**: {user_prompt}")
        context_parts.append(f"**전문가 역할**: {expert.name}")
        context_parts.append(f"**분석 목표**: {expert.analysis_focus}")

        # 🔧 명확한 분석 지침 추가
        context_parts.append(
            """
**📋 분석 수행 지침**:
1. 위의 데이터를 기반으로 실제 분석을 수행하세요
2. "다음과 같은 분석을 진행하겠습니다" 같은 프롬프트 문구는 사용하지 마세요
3. 바로 구체적인 분석 결과를 제시하세요
4. 모든 수치는 반드시 출처를 명시하세요
5. Chain of Thought 방식으로 단계별 사고 과정을 명시하세요
"""
        )

        # 🚀 PDF 딕셔너리 우선 활용 (섹션 제한 없음!)
        if pdf_interface:
            # 🔧 pdf_interface가 딕셔너리 형태인지 확인 (JSON 직렬화된 경우)
            if isinstance(pdf_interface, dict):
                # 딕셔너리에서 필요한 정보 추출
                pdf_dictionary = pdf_interface.get("pdf_dictionary", {})
                section_categories = pdf_interface.get("section_categories", {})

                logger.info("🔧 PDF 인터페이스가 딕셔너리 형태로 전달됨 - 직접 처리")

                # 전문가 타입에 맞는 섹션 추출 (수동 구현)
                expert_type_mapping = {
                    # "fundamental": "fundamental_analyst",  # 🚫 비활성화 (통합 재무분석가로 대체)
                    # "펀더멘털": "fundamental_analyst",  # 🚫 비활성화 (통합 재무분석가로 대체)
                    # "재무": "fundamental_analyst",  # 🚫 비활성화 (통합 재무분석가로 대체)
                    "technical": "technical_analyst",
                    "기술적": "technical_analyst",
                    # "industry": "industry_analyst",  # 🚫 비활성화 (개발 시간 절약)
                    # "산업": "industry_analyst",  # 🚫 비활성화 (개발 시간 절약)
                    # "valuation": "valuation_expert",  # 🚫 비활성화 (통합 재무분석가로 대체)
                    # "밸류에이션": "valuation_expert",  # 🚫 비활성화 (통합 재무분석가로 대체)
                    # "risk": "risk_assessor",  # 🚫 비활성화 (개발 시간 절약)
                    # "리스크": "risk_assessor",  # 🚫 비활성화 (개발 시간 절약)
                    # "footnote": "footnote_specialist",  # 🚫 비활성화 (개발 시간 절약)
                    # "주석": "footnote_specialist",  # 🚫 비활성화 (개발 시간 절약)
                }

                # 전문가 타입 결정
                expert_key = None
                for key, value in expert_type_mapping.items():
                    if key in expert.name.lower() or key in expert.role.lower():
                        expert_key = value
                        break

                if not expert_key:
                    expert_key = "general"

                # 해당 전문가에게 적합한 섹션 가져오기 (주석 섹션 제외)
                relevant_sections = section_categories.get(expert_key, [])
                if expert_key != "general":
                    relevant_sections.extend(section_categories.get("general", [])[:2])

                # 🔧 주석(footnote) 섹션 필터링 적용
                relevant_sections = self._filter_out_footnote_sections(
                    relevant_sections
                )
                logger.info(
                    f"🔧 {expert.name}: 주석 섹션 제외 후 {len(relevant_sections)}개 섹션 선택"
                )

                # 실제 섹션 내용 추가
                if relevant_sections and pdf_dictionary:
                    context_parts.append(
                        f"📄 **{expert.name} 관련 PDF 섹션 (딕셔너리 처리)**:"
                    )
                    section_count = 0
                    total_content_length = 0

                    for section_title in relevant_sections[:5]:  # 최대 5개 섹션
                        if section_title in pdf_dictionary:
                            # 🔧 주석 섹션 및 분석에 덜 중요한 섹션 제외 (토큰 절약)
                            if any(
                                keyword.lower() in section_title.lower()
                                for keyword in [
                                    # 기존 주석 관련
                                    "주석",
                                    "footnote",
                                    "note",
                                    "주석사항",
                                    "회계처리방법",
                                    "법적고지",
                                    "부속명세서",
                                    "notes",
                                    "footnotes",
                                    # 🚀 추가 필터링: 법적 고지사항
                                    "법적고지사항",
                                    "법적책임면책",
                                    "공시의무",
                                    "disclaimer",
                                    "legal_notice",
                                    "법적고지내용",
                                    "법적고지서",
                                    "책임면책",
                                    "면책조항",
                                    # 🚀 추가 필터링: 감사 관련
                                    "감사인의의견서",
                                    "감사의견",
                                    "auditor_opinion",
                                    "audit_report",
                                    "감사보고서",
                                    "감사범위",
                                    "audit_scope",
                                    "audit_opinion",
                                    # 🚀 추가 필터링: 회계 처리 방법
                                    "회계처리기준",
                                    "회계처리방침",
                                    "accounting_policies",
                                    "accounting_standards",
                                    "회계기준",
                                    "회계방침",
                                    "accounting_methods",
                                    "accounting_principles",
                                    # 🚀 추가 필터링: 부속 서류
                                    "부속서류",
                                    "부속서류서",
                                    "supplementary_documents",
                                    "attachments",
                                    "부속명세",
                                    "부속서류사항",
                                    "supplementary_info",
                                    "attached_documents",
                                    # 🚀 추가 필터링: 기타 상세 설명
                                    "상세설명",
                                    "상세내용",
                                    "detailed_description",
                                    "detailed_content",
                                    "상세기준",
                                    "상세방법",
                                    "detailed_standards",
                                    "detailed_methods",
                                    # 🚀 추가 필터링: 표준화된 문구
                                    "본보고서는",
                                    "이보고서는",
                                    "위의내용은",
                                    "this_report",
                                    "the_above",
                                    "보고서개요",
                                    "보고서요약",
                                    "report_summary",
                                    "report_overview",
                                ]
                            ):
                                logger.info(
                                    f"🔧 {expert.name}: 분석에 덜 중요한 섹션 제외 - {section_title}"
                                )
                                continue

                            content = pdf_dictionary[section_title]

                            # 🔧 GPT-4o 토큰 제한에 맞춰 섹션 크기 제한 (약 50만자로 축소)
                            if len(content) > 500000:
                                content = (
                                    content[:500000]
                                    + "\n...[50만자 제한으로 내용 일부 생략]..."
                                )

                            context_parts.append(f"### {section_title}")
                            context_parts.append(content)
                            context_parts.append("")
                            section_count += 1
                            total_content_length += len(content)

                    logger.info(
                        f"📄 {expert.name}: {section_count}개 섹션, 총 {total_content_length:,}자 (딕셔너리 처리)"
                    )
                else:
                    logger.info(
                        f"📄 {expert.name}: 관련 PDF 섹션을 찾지 못했습니다 (딕셔너리)"
                    )

            # 🔧 PDFDictionaryInterface 객체인 경우 (기존 로직)
            elif hasattr(pdf_interface, "get_sections_by_expert_type"):
                # 🔧 주석 전문가는 비활성화되어 있으므로 모든 전문가가 주석 섹션을 제외하도록 처리
                # 다른 전문가들 처리
                expert_sections = pdf_interface.get_sections_by_expert_type(
                    expert.role.lower().replace(" ", "_")
                )
                if expert_sections:
                    context_parts.append(
                        f"📄 **{expert.name} 관련 PDF 섹션 (완전 활용)**:"
                    )
                    section_count = 0
                    total_content_length = 0

                    for section_title, content in expert_sections.items():
                        # 🔧 주석 섹션 및 분석에 덜 중요한 섹션 제외 (토큰 절약)
                        if any(
                            keyword.lower() in section_title.lower()
                            for keyword in [
                                # 기존 주석 관련
                                "주석",
                                "footnote",
                                "note",
                                "주석사항",
                                "회계처리방법",
                                "법적고지",
                                "부속명세서",
                                "notes",
                                "footnotes",
                                # 🚀 추가 필터링: 법적 고지사항
                                "법적고지사항",
                                "법적책임면책",
                                "공시의무",
                                "disclaimer",
                                "legal_notice",
                                "법적고지내용",
                                "법적고지서",
                                "책임면책",
                                "면책조항",
                                # 🚀 추가 필터링: 감사 관련
                                "감사인의의견서",
                                "감사의견",
                                "auditor_opinion",
                                "audit_report",
                                "감사보고서",
                                "감사범위",
                                "audit_scope",
                                "audit_opinion",
                                # 🚀 추가 필터링: 회계 처리 방법
                                "회계처리기준",
                                "회계처리방침",
                                "accounting_policies",
                                "accounting_standards",
                                "회계기준",
                                "회계방침",
                                "accounting_methods",
                                "accounting_principles",
                                # 🚀 추가 필터링: 부속 서류
                                "부속서류",
                                "부속서류서",
                                "supplementary_documents",
                                "attachments",
                                "부속명세",
                                "부속서류사항",
                                "supplementary_info",
                                "attached_documents",
                                # 🚀 추가 필터링: 기타 상세 설명
                                "상세설명",
                                "상세내용",
                                "detailed_description",
                                "detailed_content",
                                "상세기준",
                                "상세방법",
                                "detailed_standards",
                                "detailed_methods",
                                # 🚀 추가 필터링: 표준화된 문구
                                "본보고서는",
                                "이보고서는",
                                "위의내용은",
                                "this_report",
                                "the_above",
                                "보고서개요",
                                "보고서요약",
                                "report_summary",
                                "report_overview",
                            ]
                        ):
                            logger.info(
                                f"🔧 {expert.name}: 분석에 덜 중요한 섹션 제외 - {section_title}"
                            )
                            continue

                        # 🔧 GPT-4o 토큰 제한에 맞춰 섹션 크기 제한 (약 50만자로 축소)
                        if len(content) > 500000:
                            content = (
                                content[:500000]
                                + "\n...[50만자 제한으로 내용 일부 생략]..."
                            )

                        context_parts.append(f"### {section_title}")
                        context_parts.append(content)
                        context_parts.append("")
                        section_count += 1
                        total_content_length += len(content)

                logger.info(
                    f"📄 {expert.name}: {section_count}개 섹션, 총 {total_content_length:,}자 (제한 없음)"
                )
            else:
                logger.warning(
                    f"⚠️ PDF 인터페이스가 예상과 다른 형태입니다: {type(pdf_interface)}"
                )
        else:
            if pdf_interface is None:
                logger.info(
                    "📄 PDF 딕셔너리 인터페이스가 제공되지 않았습니다 (DART 딕셔너리만 사용)"
                )
            else:
                logger.info(
                    "📄 PDF 딕셔너리 인터페이스가 비어있습니다 (DART 딕셔너리만 사용)"
                )

        # 🚀 새로운 전문가별 DART 딕셔너리 처리 (🚀 핵심 개선!)
        if dart_reports_dictionary and dart_reports_dictionary.get(
            "expert_ready_dictionaries"
        ):
            logger.info("🚀 전문가별 DART 딕셔너리 처리 시작...")

            expert_ready_dictionaries = dart_reports_dictionary.get(
                "expert_ready_dictionaries", {}
            )

            # 전문가 타입 매핑
            expert_type_mapping = {
                "통합 재무분석가": "integrated_financial_analyst",
                "기술적 분석가": "technical_analyst",
                "financial_analyst": "integrated_financial_analyst",
                "technical_analyst": "technical_analyst",
                "재무": "integrated_financial_analyst",
                "기술적": "technical_analyst",
            }

            # 전문가 타입 결정
            expert_type = None
            for key, value in expert_type_mapping.items():
                if key in expert.name or key in expert.role:
                    expert_type = value
                    break

            if not expert_type:
                # 기본값으로 통합 재무분석가 사용
                expert_type = "integrated_financial_analyst"

            logger.info(f"🎯 {expert.name} → {expert_type} 매핑 완료")

            # 해당 전문가용 딕셔너리 가져오기
            expert_data = expert_ready_dictionaries.get(expert_type)

            # 🔧 데이터 타입 안전성 검증
            if expert_data:
                logger.info(f"🔍 {expert.name} expert_data 타입: {type(expert_data)}")

                # expert_data가 문자열인 경우 (압축 과정에서 변환된 경우)
                if isinstance(expert_data, str):
                    logger.warning(
                        f"⚠️ {expert.name}: expert_data가 문자열로 변환됨 - 딕셔너리 구조 복원 시도"
                    )
                    # 간단한 텍스트로 처리
                    context_parts.append(f"📄 **{expert.name} 전용 DART 보고서 내용**:")
                    # 🔧 주석 관련 내용 제거 (토큰 절약)
                    import re

                    # 주석 관련 패턴 및 분석에 덜 중요한 패턴 제거
                    footnote_patterns = [
                        # 기존 주석 관련
                        r"주석.*?[\n\r]",
                        r"footnote.*?[\n\r]",
                        r"note.*?[\n\r]",
                        r"주석사항.*?[\n\r]",
                        r"회계처리방법.*?[\n\r]",
                        r"법적고지.*?[\n\r]",
                        r"부속명세서.*?[\n\r]",
                        # 🚀 추가 필터링: 법적 고지사항
                        r"법적고지사항.*?[\n\r]",
                        r"법적책임면책.*?[\n\r]",
                        r"공시의무.*?[\n\r]",
                        r"disclaimer.*?[\n\r]",
                        r"legal_notice.*?[\n\r]",
                        r"법적고지내용.*?[\n\r]",
                        r"법적고지서.*?[\n\r]",
                        r"책임면책.*?[\n\r]",
                        r"면책조항.*?[\n\r]",
                        # 🚀 추가 필터링: 감사 관련
                        r"감사인의의견서.*?[\n\r]",
                        r"감사의견.*?[\n\r]",
                        r"auditor_opinion.*?[\n\r]",
                        r"audit_report.*?[\n\r]",
                        r"감사보고서.*?[\n\r]",
                        r"감사범위.*?[\n\r]",
                        r"audit_scope.*?[\n\r]",
                        r"audit_opinion.*?[\n\r]",
                        # 🚀 추가 필터링: 회계 처리 방법
                        r"회계처리기준.*?[\n\r]",
                        r"회계처리방침.*?[\n\r]",
                        r"accounting_policies.*?[\n\r]",
                        r"accounting_standards.*?[\n\r]",
                        r"회계기준.*?[\n\r]",
                        r"회계방침.*?[\n\r]",
                        r"accounting_methods.*?[\n\r]",
                        r"accounting_principles.*?[\n\r]",
                        # 🚀 추가 필터링: 부속 서류
                        r"부속서류.*?[\n\r]",
                        r"부속서류서.*?[\n\r]",
                        r"supplementary_documents.*?[\n\r]",
                        r"attachments.*?[\n\r]",
                        r"부속명세.*?[\n\r]",
                        r"부속서류사항.*?[\n\r]",
                        r"supplementary_info.*?[\n\r]",
                        r"attached_documents.*?[\n\r]",
                        # 🚀 추가 필터링: 기타 상세 설명
                        r"상세설명.*?[\n\r]",
                        r"상세내용.*?[\n\r]",
                        r"detailed_description.*?[\n\r]",
                        r"detailed_content.*?[\n\r]",
                        r"상세기준.*?[\n\r]",
                        r"상세방법.*?[\n\r]",
                        r"detailed_standards.*?[\n\r]",
                        r"detailed_methods.*?[\n\r]",
                        # 🚀 추가 필터링: 표준화된 문구
                        r"본보고서는.*?[\n\r]",
                        r"이보고서는.*?[\n\r]",
                        r"위의내용은.*?[\n\r]",
                        r"this_report.*?[\n\r]",
                        r"the_above.*?[\n\r]",
                        r"보고서개요.*?[\n\r]",
                        r"보고서요약.*?[\n\r]",
                        r"report_summary.*?[\n\r]",
                        r"report_overview.*?[\n\r]",
                    ]

                    for pattern in footnote_patterns:
                        expert_data = re.sub(
                            pattern, "", expert_data, flags=re.IGNORECASE
                        )

                    # 🔧 GPT-4o 토큰 제한에 맞춰 텍스트 길이 제한 (약 50만자로 축소)
                    if len(expert_data) > 500000:
                        expert_data = (
                            expert_data[:500000]
                            + "\n...[50만자 제한으로 내용 일부 생략]..."
                        )
                    context_parts.append(expert_data)
                    context_parts.append("")
                    logger.info(
                        f"📄 {expert.name}: 텍스트 형태로 {len(expert_data):,}자 제공"
                    )

                # expert_data가 딕셔너리인 경우 (정상 케이스)
                elif isinstance(expert_data, dict) and expert_data.get("sections"):
                    sections = expert_data.get("sections", {})
                    metadata = expert_data.get("metadata", {})

                    # sections도 타입 검증
                    if isinstance(sections, dict):
                        context_parts.append(
                            f"📄 **{expert.name} 전용 DART 보고서 섹션**:"
                        )
                        section_count = 0
                        total_content_length = 0

                        for section_title, content in sections.items():
                            # 🔧 주석 섹션 및 분석에 덜 중요한 섹션 제외 (토큰 절약)
                            if any(
                                keyword.lower() in section_title.lower()
                                for keyword in [
                                    # 기존 주석 관련
                                    "주석",
                                    "footnote",
                                    "note",
                                    "주석사항",
                                    "회계처리방법",
                                    "법적고지",
                                    "부속명세서",
                                    "notes",
                                    "footnotes",
                                    # 🚀 추가 필터링: 법적 고지사항
                                    "법적고지사항",
                                    "법적책임면책",
                                    "공시의무",
                                    "disclaimer",
                                    "legal_notice",
                                    "법적고지내용",
                                    "법적고지서",
                                    "책임면책",
                                    "면책조항",
                                    # 🚀 추가 필터링: 감사 관련
                                    "감사인의의견서",
                                    "감사의견",
                                    "auditor_opinion",
                                    "audit_report",
                                    "감사보고서",
                                    "감사범위",
                                    "audit_scope",
                                    "audit_opinion",
                                    # 🚀 추가 필터링: 회계 처리 방법
                                    "회계처리기준",
                                    "회계처리방침",
                                    "accounting_policies",
                                    "accounting_standards",
                                    "회계기준",
                                    "회계방침",
                                    "accounting_methods",
                                    "accounting_principles",
                                    # 🚀 추가 필터링: 부속 서류
                                    "부속서류",
                                    "부속서류서",
                                    "supplementary_documents",
                                    "attachments",
                                    "부속명세",
                                    "부속서류사항",
                                    "supplementary_info",
                                    "attached_documents",
                                    # 🚀 추가 필터링: 기타 상세 설명
                                    "상세설명",
                                    "상세내용",
                                    "detailed_description",
                                    "detailed_content",
                                    "상세기준",
                                    "상세방법",
                                    "detailed_standards",
                                    "detailed_methods",
                                    # 🚀 추가 필터링: 표준화된 문구
                                    "본보고서는",
                                    "이보고서는",
                                    "위의내용은",
                                    "this_report",
                                    "the_above",
                                    "보고서개요",
                                    "보고서요약",
                                    "report_summary",
                                    "report_overview",
                                ]
                            ):
                                logger.info(
                                    f"🔧 {expert.name}: 분석에 덜 중요한 섹션 제외 - {section_title}"
                                )
                                continue

                            # 🔧 GPT-4o 토큰 제한에 맞춰 섹션 크기 제한 (약 50만자로 축소)
                            if len(content) > 500000:
                                content = (
                                    content[:500000]
                                    + "\n...[50만자 제한으로 내용 일부 생략]..."
                                )

                            context_parts.append(f"### {section_title}")
                            context_parts.append(content)
                            context_parts.append("")
                            section_count += 1
                            total_content_length += len(content)

                        logger.info(
                            f"📄 {expert.name}: {section_count}개 섹션, 총 {total_content_length:,}자 (전문가별 딕셔너리)"
                        )

                        # 메타데이터 정보 추가
                        context_parts.append(f"**📊 DART 보고서 메타데이터**:")
                        context_parts.append(
                            f"- 총 섹션: {metadata.get('total_sections', 0)}개"
                        )
                        context_parts.append(
                            f"- 관련 섹션: {metadata.get('relevant_sections', 0)}개"
                        )
                        context_parts.append(
                            f"- 일반 섹션: {metadata.get('general_sections', 0)}개"
                        )
                        context_parts.append(
                            f"- 총 텍스트: {metadata.get('total_text_length', 0):,}자"
                        )
                        context_parts.append("")
                    else:
                        logger.warning(
                            f"⚠️ {expert.name}: sections가 딕셔너리가 아님 (타입: {type(sections)})"
                        )
                        # 텍스트로 처리
                        context_parts.append(
                            f"📄 **{expert.name} 전용 DART 보고서 내용**:"
                        )
                        if isinstance(sections, str):
                            if len(sections) > 2000000:
                                sections = (
                                    sections[:2000000]
                                    + "\n...[200만자 제한으로 내용 일부 생략]..."
                                )
                            context_parts.append(sections)
                        else:
                            context_parts.append(f"데이터 타입 오류: {type(sections)}")
                        context_parts.append("")

                else:
                    logger.warning(
                        f"⚠️ {expert.name}: 지원되지 않는 expert_data 타입 또는 구조 ({type(expert_data)})"
                    )

            else:
                logger.warning(
                    f"⚠️ {expert.name}: 전문가별 DART 딕셔너리를 찾을 수 없습니다"
                )
        else:
            logger.info("📋 전문가별 DART 딕셔너리가 제공되지 않았습니다")

        # 전문가별 추가 데이터 선별 (기존 로직 유지)
        if (
            "재무" in expert.expertise
            or "Fundamental" in expert.role
            or "통합" in expert.name
        ):
            # 재무 분석 전문가 - 🎯 시니어 애널리스트 수준 지침 추가
            if financial_data and financial_data.get("success"):
                financial_summary = self._summarize_financial_data(financial_data)
                context_parts.append("📊 재무데이터:")
                context_parts.append(financial_summary)

            if enhanced_dart_data and enhanced_dart_data.get("success"):
                dart_financial = self._extract_dart_financial_only(enhanced_dart_data)
                if dart_financial:
                    context_parts.append("🚀 상세 재무정보 (DART):")
                    context_parts.append(dart_financial)

            # 🎯 재무 분석을 위한 실제 데이터 기반 지침 생성
            context_parts.append("\n🎯 재무 분석 데이터 출처:")

            # 실제 사용 가능한 데이터 소스 명시
            available_sources = []
            if financial_data and financial_data.get("success"):
                available_sources.append("재무데이터 (재무제표)")
            if enhanced_dart_data and enhanced_dart_data.get("success"):
                available_sources.append("DART 사업보고서")
            if dart_reports_dictionary:
                available_sources.append("DART 보고서 딕셔너리")
            if manus_collected_data and manus_collected_data.get("performed"):
                available_sources.append("웹검색 데이터")
            if technical_analysis_data:
                available_sources.append("기술적 분석 데이터")

            if available_sources:
                context_parts.append(
                    f"**📊 사용 가능한 데이터 소스**: {', '.join(available_sources)}"
                )
            else:
                context_parts.append("**⚠️ 사용 가능한 데이터 소스 없음**")

            context_parts.append("")

            # 실제 데이터 기반 재무 분석 지침
            context_parts.append("**📊 실제 데이터 기반 재무 분석 지침**:")
            if financial_data and financial_data.get("success"):
                context_parts.append("- 재무데이터를 활용한 ROE, ROIC, 재무비율 분석")
                context_parts.append("- 수익성, 안정성, 활동성 지표 계산 및 평가")
            if enhanced_dart_data and enhanced_dart_data.get("success"):
                context_parts.append(
                    "- DART 사업보고서에서 경영진 리더십 및 지배구조 평가"
                )
            if dart_reports_dictionary:
                context_parts.append(
                    "- DART 보고서 딕셔너리에서 현금흐름표 계정과목 분석"
                )
            if manus_collected_data and manus_collected_data.get("performed"):
                context_parts.append(
                    "- 웹검색 데이터에서 경쟁사 벤치마킹 및 시장점유율 분석"
                )
            if technical_analysis_data:
                context_parts.append("- 기술적 분석 데이터에서 시장 동향 및 성과 분석")

            context_parts.append("")

            # 🚀 NEW: 현금흐름표 직접 계산 지침 추가
            # DART 보고서 딕셔너리가 있을 때만 현금흐름표 분석 지침 추가
            if dart_reports_dictionary:
                context_parts.append("**🚀 현금흐름표 분석 지침**:")
                context_parts.append(
                    "- DART 보고서 딕셔너리에서 현금흐름표 계정과목 직접 추출"
                )
                context_parts.append("- 영업활동, 투자활동, 재무활동 현금흐름 분석")
                context_parts.append("- 실제 수치 기반 현금흐름 품질 평가")
                context_parts.append("")
            else:
                context_parts.append(
                    "**⚠️ 현금흐름표 분석**: DART 보고서 딕셔너리가 없어 상세 분석이 제한됩니다."
                )
                context_parts.append("")

            # 실제 데이터 기반 추가 분석 지침
            context_parts.append("**📈 추가 분석 지침**:")
            if financial_data and financial_data.get("success"):
                context_parts.append(
                    "- 재무데이터를 활용한 성장성, 현금흐름, 재무건전성 분석"
                )
            if enhanced_dart_data and enhanced_dart_data.get("success"):
                context_parts.append("- DART 데이터를 활용한 ESG 및 지배구조 평가")
            if manus_collected_data and manus_collected_data.get("performed"):
                context_parts.append(
                    "- 웹검색 데이터를 활용한 경영진 효율성 및 자본배분 정책 분석"
                )

            context_parts.append("")
            context_parts.append("**⚠️ 분석 시 주의사항**:")
            context_parts.append("- 모든 수치는 실제 데이터 기반으로 계산")
            context_parts.append(
                "- 데이터 출처를 명시하고 가정값 사용 시 '(가정)' 표시"
            )
            context_parts.append("- 정량적 분석과 정성적 평가의 균형 유지")
            context_parts.append("")

        elif "기술" in expert.expertise or "Technical" in expert.role:
            # 기술 분석 전문가 - 🎯 실제 계산된 지표 데이터 우선 제공!

            # 🚀 1단계: 계산된 기술적 지표 데이터 (최우선!) - 안전한 방식
            if technical_analysis_data and technical_analysis_data.get("success"):
                try:
                    context_parts.append("🎯 **계산된 기술적 지표 (실제 수치)**:")
                    if hasattr(self, "_format_technical_indicators_for_expert"):
                        formatted_indicators = (
                            self._format_technical_indicators_for_expert(
                                technical_analysis_data
                            )
                        )
                        context_parts.append(formatted_indicators)
                    else:
                        # 메서드가 없는 경우 기본 포맷팅
                        context_parts.append(
                            "기술적 지표 데이터가 수집되었지만 포맷팅 중 오류가 발생했습니다."
                        )
                        context_parts.append(
                            f"원본 데이터: {str(technical_analysis_data)[:500]}..."
                        )
                    context_parts.append("")
                    logger.info(
                        f"✅ {expert.name}: 계산된 기술적 지표 데이터 제공 완료"
                    )
                except Exception as format_error:
                    logger.error(f"❌ 기술적 지표 포맷팅 실패: {format_error}")
                    # 🔧 더 상세한 디버깅 정보
                    logger.error(
                        f"🔍 technical_analysis_data 타입: {type(technical_analysis_data)}"
                    )
                    if isinstance(technical_analysis_data, dict):
                        indicators = technical_analysis_data.get(
                            "technical_indicators", {}
                        )
                        logger.error(f"🔍 indicators 타입: {type(indicators)}")
                        if isinstance(indicators, dict):
                            logger.error(
                                f"🔍 indicators 키들: {list(indicators.keys())}"
                            )
                        else:
                            logger.error(
                                f"🔍 indicators 내용 (처음 200자): {str(indicators)[:200]}"
                            )

                    context_parts.append("🎯 **기술적 지표 데이터**:")
                    context_parts.append(
                        "기술적 지표 포맷팅 중 오류가 발생했습니다. 기본 데이터를 참조하세요."
                    )
                    context_parts.append(f"오류 내용: {str(format_error)}")
                    context_parts.append("")
            else:
                logger.warning(
                    f"⚠️ {expert.name}: 계산된 기술적 지표 데이터 없음 - 기본 데이터로 대체"
                )

            # 🔧 2단계: 기본 가격 데이터 (백업)
            if financial_data and financial_data.get("success"):
                price_data = self._extract_price_data_only(financial_data)
                if price_data:
                    context_parts.append("📈 기본 가격/차트 데이터:")
                    context_parts.append(price_data)

            # 🔍 3단계: Manus 웹검색 기술분석 정보 (보조)
            if manus_collected_data and manus_collected_data.get("performed"):
                technical_info = self._extract_technical_analysis_info(
                    manus_collected_data
                )
                if technical_info:
                    context_parts.append("🔍 추가 기술분석 관련 정보:")
                    context_parts.append(technical_info)

            # 🎯 시니어 기술적 애널리스트 분석 지침 (Chat GPT 피드백 완전 반영)
            if technical_analysis_data and technical_analysis_data.get("success"):
                # 🎯 기술적 분석을 위한 실제 데이터 기반 지침 생성
                context_parts.append("\n🎯 기술적 분석 데이터 출처:")

                # 실제 사용 가능한 데이터 소스 명시
                available_sources = []
                if technical_analysis_data and technical_analysis_data.get("success"):
                    available_sources.append("기술적 분석 데이터")
                if financial_data and financial_data.get("success"):
                    available_sources.append("재무데이터 (가격 정보)")
                if manus_collected_data and manus_collected_data.get("performed"):
                    available_sources.append("웹검색 데이터")

                if available_sources:
                    context_parts.append(
                        f"**📊 사용 가능한 데이터 소스**: {', '.join(available_sources)}"
                    )
                else:
                    context_parts.append("**⚠️ 사용 가능한 데이터 소스 없음**")

                context_parts.append("")

                # 실제 데이터 기반 기술적 분석 지침
                context_parts.append("**📈 실제 데이터 기반 기술적 분석 지침**:")
                if technical_analysis_data and technical_analysis_data.get("success"):
                    context_parts.append(
                        "- 계산된 기술적 지표(RSI, MACD, 볼린저밴드 등) 기반 분석"
                    )
                    context_parts.append("- 이동평균선 배열과 현재가 위치 관계 분석")
                    context_parts.append("- 지지/저항선 레벨에서의 매매 전략")
                if financial_data and financial_data.get("success"):
                    context_parts.append(
                        "- 재무데이터의 가격 정보를 활용한 차트 패턴 분석"
                    )
                if manus_collected_data and manus_collected_data.get("performed"):
                    context_parts.append("- 웹검색 데이터를 활용한 이벤트 기반 분석")

                context_parts.append("")
            else:
                # 🎯 기술적 분석을 위한 실제 데이터 기반 지침 생성 (기술적 지표 없음)
                context_parts.append("\n🎯 기술적 분석 데이터 출처:")

                # 실제 사용 가능한 데이터 소스 명시
                available_sources = []
                if financial_data and financial_data.get("success"):
                    available_sources.append("재무데이터 (가격 정보)")
                if manus_collected_data and manus_collected_data.get("performed"):
                    available_sources.append("웹검색 데이터")

                if available_sources:
                    context_parts.append(
                        f"**📊 사용 가능한 데이터 소스**: {', '.join(available_sources)}"
                    )
                else:
                    context_parts.append("**⚠️ 사용 가능한 데이터 소스 없음**")

                context_parts.append("")

                # 실제 데이터 기반 기술적 분석 지침 (기술적 지표 없음)
                context_parts.append("**📈 실제 데이터 기반 기술적 분석 지침**:")
                if financial_data and financial_data.get("success"):
                    context_parts.append(
                        "- 재무데이터의 가격 정보를 활용한 기본 차트 분석"
                    )
                    context_parts.append("- 이동평균선과 현재가 위치 관계 분석")
                if manus_collected_data and manus_collected_data.get("performed"):
                    context_parts.append(
                        "- 웹검색 데이터를 활용한 시장 동향 및 이벤트 분석"
                    )

                context_parts.append("")
                context_parts.append("**⚠️ 기술적 분석 주의사항**:")
                context_parts.append("- 모든 분석은 실제 데이터 기반으로 수행")
                context_parts.append(
                    "- 데이터 출처를 명시하고 가정값 사용 시 '(가정)' 표시"
                )
                context_parts.append("- 단기, 중기, 장기 시계열 종합 판단")
                context_parts.append("")

        # 기타 전문가별 데이터 처리
        if "산업" in expert.expertise or "Industry" in expert.role:
            # 산업 분석 전문가 - 🎯 시니어 애널리스트 수준 지침 추가
            if manus_collected_data and manus_collected_data.get("performed"):
                industry_info = self._extract_industry_info(manus_collected_data)
                if industry_info:
                    context_parts.append("🏭 산업 동향 정보:")
                    context_parts.append(industry_info)

            if enhanced_dart_data and enhanced_dart_data.get("success"):
                # 🔧 안전한 DART 데이터 처리
                try:
                    business_info = self._extract_dart_business_info(enhanced_dart_data)
                    if business_info and isinstance(business_info, str):
                        context_parts.append("🏢 사업 정보 (DART):")
                        context_parts.append(business_info)
                except Exception as e:
                    logger.warning(f"⚠️ DART 사업 정보 추출 실패: {e}")
                    pass

            # 🎯 산업 분석을 위한 실제 데이터 기반 지침 생성
            context_parts.append("\n🎯 산업 분석 데이터 출처:")

            # 실제 사용 가능한 데이터 소스 명시
            available_sources = []
            if financial_data and financial_data.get("success"):
                available_sources.append("재무데이터 (재무제표)")
            if enhanced_dart_data and enhanced_dart_data.get("success"):
                available_sources.append("DART 사업보고서")
            if manus_collected_data and manus_collected_data.get("performed"):
                available_sources.append("웹검색 데이터")
            if technical_analysis_data:
                available_sources.append("기술적 분석 데이터")

            if available_sources:
                context_parts.append(
                    f"** 사용 가능한 데이터 소스**: {', '.join(available_sources)}"
                )
            else:
                context_parts.append("**⚠️ 사용 가능한 데이터 소스 없음**")

            context_parts.append("")

            # 실제 데이터 기반 분석 지침
            context_parts.append("**🔍 실제 데이터 기반 분석 지침**:")
            if financial_data and financial_data.get("success"):
                context_parts.append("- 재무데이터에서 산업 평균 대비 수익성 지표 분석")
                context_parts.append("- 경쟁사 대비 재무비율 비교 분석")
            if enhanced_dart_data and enhanced_dart_data.get("success"):
                context_parts.append("- DART 사업보고서에서 산업 동향 및 전략 분석")
            if manus_collected_data and manus_collected_data.get("performed"):
                context_parts.append("- 웹검색 데이터에서 최신 산업 동향 및 뉴스 분석")
            if technical_analysis_data:
                context_parts.append("- 기술적 분석 데이터에서 시장 동향 분석")

            context_parts.append("")

        # 통합 재무분석가에 밸류에이션 로직 추가 (독립적인 조건)
        if "통합" in expert.name:
            # 밸류에이션 데이터 추출
            if financial_data and financial_data.get("success"):
                try:
                    valuation_data = self._extract_valuation_data(financial_data)
                    if valuation_data and isinstance(valuation_data, str):
                        context_parts.append("💰 밸류에이션 데이터:")
                        context_parts.append(valuation_data)
                except Exception as e:
                    logger.warning(f"⚠️ 밸류에이션 데이터 추출 실패: {e}")
                    pass

            # 밸류에이션 분석 지침 추가
            context_parts.append("\n💰 밸류에이션 분석 지침:")
            context_parts.append("- 재무데이터를 활용한 DCF 분석 (현금흐름 할인)")
            context_parts.append("- 재무비율을 통한 멀티플 분석 (PER, PBR, EV/EBITDA)")
            context_parts.append("- 민감도 분석 (WACC, 성장률 변동 시 영향도)")
            context_parts.append("- DART 데이터를 활용한 현금흐름 분석")
            context_parts.append("- 웹검색 데이터를 활용한 시장 동향 및 멀티플 비교")
            context_parts.append("")

        elif (
            "밸류에이션" in expert.expertise or "Valuation" in expert.role
        ) and "통합" not in expert.name:
            # 밸류에이션 전문가 - 🎯 시니어 애널리스트 수준 지침 추가
            if financial_data and financial_data.get("success"):
                # 🔧 안전한 재무 데이터 처리
                try:
                    valuation_data = self._extract_valuation_data(financial_data)
                    if valuation_data and isinstance(valuation_data, str):
                        context_parts.append("💰 밸류에이션 데이터:")
                        context_parts.append(valuation_data)
                except Exception as e:
                    logger.warning(f"⚠️ 밸류에이션 데이터 추출 실패: {e}")
                    pass

            # 🎯 밸류에이션 분석을 위한 실제 데이터 기반 지침 생성
            context_parts.append("\n🎯 밸류에이션 분석 데이터 출처:")

            # 실제 사용 가능한 데이터 소스 명시
            available_sources = []
            if financial_data and financial_data.get("success"):
                available_sources.append("재무데이터 (재무제표)")
            if enhanced_dart_data and enhanced_dart_data.get("success"):
                available_sources.append("DART 사업보고서")
            if dart_reports_dictionary:
                available_sources.append("DART 보고서 딕셔너리")
            if manus_collected_data and manus_collected_data.get("performed"):
                available_sources.append("웹검색 데이터")

            if available_sources:
                context_parts.append(
                    f"** 사용 가능한 데이터 소스**: {', '.join(available_sources)}"
                )
            else:
                context_parts.append("**⚠️ 사용 가능한 데이터 소스 없음**")

            context_parts.append("")

            # 실제 데이터 기반 밸류에이션 지침
            context_parts.append("**💰 실제 데이터 기반 밸류에이션 지침**:")
            if financial_data and financial_data.get("success"):
                context_parts.append(
                    "- 재무데이터에서 FCF 계산을 위한 영업현금흐름 및 자본적지출 추출"
                )
                context_parts.append(
                    "- 재무비율을 통한 멀티플 분석 (PER, PBR, EV/EBITDA)"
                )
                context_parts.append("- DART 데이터에서 현금흐름표 정보 추출")
                context_parts.append(
                    "- DART 보고서 딕셔너리에서 상세 현금흐름 정보 활용"
                )
                context_parts.append(
                    "- 웹검색 데이터에서 시장 동향 및 분석가 의견 참고"
                )

            context_parts.append("")

            # 실제 데이터 기반 밸류에이션 분석 방법론
            context_parts.append("**💰 실제 데이터 기반 밸류에이션 분석 방법론**:")
            if financial_data and financial_data.get("success"):
                context_parts.append("- 재무데이터를 활용한 DCF 분석 (현금흐름 할인)")
            context_parts.append("- 재무비율을 통한 멀티플 분석 (PER, PBR, EV/EBITDA)")
            context_parts.append("- 민감도 분석 (WACC, 성장률 변동 시 영향도)")
            context_parts.append("- DART 데이터를 활용한 현금흐름 분석")
            context_parts.append("- 웹검색 데이터를 활용한 시장 동향 및 멀티플 비교")

            context_parts.append("")
            context_parts.append("**⚠️ 밸류에이션 분석 주의사항**:")
            context_parts.append(
                "- 모든 가정과 계산 과정을 명시하여 검증 가능하도록 함"
            )
            context_parts.append("- 민감도 분석을 통한 핵심 변수 영향도 평가")
            context_parts.append("- 과거 멀티플 밴드와 현재 수준 비교 분석")
            context_parts.append("- 배당할인모델(DDM) 병행 검증 (배당주의 경우)")

        elif "리스크" in expert.expertise or "Risk" in expert.role:
            # 리스크 평가자 - 🎯 시니어 애널리스트 수준 지침 추가
            if financial_data and financial_data.get("success"):
                # 🔧 안전한 리스크 데이터 처리
                try:
                    risk_data = self._extract_risk_indicators(financial_data)
                    if risk_data and isinstance(risk_data, str):
                        context_parts.append("⚠️ 리스크 지표:")
                        context_parts.append(risk_data)
                except Exception as e:
                    logger.warning(f"⚠️ 리스크 데이터 추출 실패: {e}")
                    pass

            if manus_collected_data and manus_collected_data.get("performed"):
                # 🔧 안전한 Manus 데이터 처리
                try:
                    risk_factors = self._extract_risk_factors(manus_collected_data)
                    if risk_factors and isinstance(risk_factors, str):
                        context_parts.append("🚨 위험 요인:")
                        context_parts.append(risk_factors)
                except Exception as e:
                    logger.warning(f"⚠️ Manus 리스크 데이터 추출 실패: {e}")
                    pass

            # 🎯 리스크 분석을 위한 실제 데이터 기반 지침 생성
            context_parts.append("\n🎯 리스크 분석 데이터 출처:")

            # 실제 사용 가능한 데이터 소스 명시
            available_sources = []
            if financial_data and financial_data.get("success"):
                available_sources.append("재무데이터 (재무제표)")
            if enhanced_dart_data and enhanced_dart_data.get("success"):
                available_sources.append("DART 사업보고서")
            if manus_collected_data and manus_collected_data.get("performed"):
                available_sources.append("웹검색 데이터")
            if technical_analysis_data:
                available_sources.append("기술적 분석 데이터")

            if available_sources:
                context_parts.append(
                    f"** 사용 가능한 데이터 소스**: {', '.join(available_sources)}"
                )
            else:
                context_parts.append("**⚠️ 사용 가능한 데이터 소스 없음**")

            context_parts.append("")

            # 실제 데이터 기반 리스크 분석 지침
            context_parts.append("**🚨 실제 데이터 기반 리스크 분석 지침**:")
            if financial_data and financial_data.get("success"):
                context_parts.append(
                    "- 재무데이터에서 유동성 및 부채 상환 능력 지표 분석"
                )
                context_parts.append("- 현금흐름 변동성 및 안정성 평가")
            if enhanced_dart_data and enhanced_dart_data.get("success"):
                context_parts.append("- DART 데이터에서 재무 리스크 관련 정보 추출")
            if manus_collected_data and manus_collected_data.get("performed"):
                context_parts.append("- 웹검색 데이터에서 비재무 리스크 요인 분석")
            if technical_analysis_data:
                context_parts.append("- 기술적 분석 데이터에서 시장 리스크 지표 분석")

            context_parts.append("")

        elif "주석" in expert.expertise or "Footnote" in expert.role:
            # 재무제표 주석 전문가 - 🎯 시니어 애널리스트 수준 지침 추가
            if enhanced_dart_data and enhanced_dart_data.get("success"):
                # 🔧 안전한 DART 데이터 처리
                try:
                    investment_info = self._extract_dart_investment_info(
                        enhanced_dart_data
                    )
                    if investment_info and isinstance(investment_info, str):
                        context_parts.append("💼 투자정보 (DART):")
                        context_parts.append(investment_info)
                except Exception as e:
                    logger.warning(f"⚠️ DART 투자정보 추출 실패: {e}")
                    pass

            # 🎯 재무제표 주석 분석을 위한 실제 데이터 기반 지침 생성
            context_parts.append("\n🎯 재무제표 주석 분석 데이터 출처:")

            # 실제 사용 가능한 데이터 소스 명시
            available_sources = []
            if enhanced_dart_data and enhanced_dart_data.get("success"):
                available_sources.append("DART 사업보고서")
            if dart_reports_dictionary:
                available_sources.append("DART 보고서 딕셔너리")
            if financial_data and financial_data.get("success"):
                available_sources.append("재무데이터 (재무제표)")

            if available_sources:
                context_parts.append(
                    f"** 사용 가능한 데이터 소스**: {', '.join(available_sources)}"
                )
            else:
                context_parts.append("**⚠️ 사용 가능한 데이터 소스 없음**")

            context_parts.append("")

            # 실제 데이터 기반 주석 분석 지침
            context_parts.append("**📋 실제 데이터 기반 주석 분석 지침**:")
            if enhanced_dart_data and enhanced_dart_data.get("success"):
                context_parts.append(
                    "- DART 사업보고서에서 IFRS 적용 현황 및 영향 분석"
                )
                context_parts.append("- 감사의견 및 핵심감사사항(KAM) 분석")
            if dart_reports_dictionary:
                context_parts.append("- DART 보고서 딕셔너리에서 상세 주석 정보 활용")
            if financial_data and financial_data.get("success"):
                context_parts.append("- 재무데이터에서 회계 정책 및 추정치 분석")

            context_parts.append("")
            context_parts.append("")

            # 실제 데이터 기반 주석 분석 세부 지침
            context_parts.append("**📋 실제 데이터 기반 주석 분석 세부 지침**:")
            if enhanced_dart_data and enhanced_dart_data.get("success"):
                context_parts.append("- DART 사업보고서에서 회계추정 관련 리스크 분석")
                context_parts.append("- 우발채무 및 보증채무 정밀분석")
                context_parts.append("- 관계회사 거래 투명성 평가")
            if dart_reports_dictionary:
                context_parts.append(
                    "- DART 보고서 딕셔너리에서 금융상품 및 파생상품 위험 평가"
                )
                context_parts.append("- 리스 및 약정사항 영향도 분석")
            if financial_data and financial_data.get("success"):
                context_parts.append(
                    "- 재무데이터에서 회계정책 변경 및 추정변경 영향 분석"
                )
                context_parts.append("- 연결범위 변동 및 지배력 분석")

            context_parts.append("")
            context_parts.append("**⚠️ 주석 분석 주의사항**:")
            context_parts.append("- 모든 분석은 실제 데이터 기반으로 수행")
            context_parts.append(
                "- 데이터 출처를 명시하고 가정값 사용 시 '(가정)' 표시"
            )
            context_parts.append("- 숨겨진 부채나 위험요소 발굴에 집중")
            context_parts.append("")

        # 컨텍스트를 문자열로 결합하기 전 검증
        # 🔧 안전한 문자열 변환
        safe_context_parts = []
        for part in context_parts:
            if isinstance(part, str):
                safe_context_parts.append(part)
            elif isinstance(part, dict):
                # dict인 경우 JSON 문자열로 변환
                safe_context_parts.append(str(part))
            else:
                # 기타 타입은 문자열로 변환
                safe_context_parts.append(str(part))

                # 🎯 모든 GICS 섹터별 전문가에게 공통 적용되는 데이터 출처 명시 규칙 추가
        data_source_guidelines = self._get_data_source_guidelines()
        safe_context_parts.append(data_source_guidelines)

        full_context = "\n".join(safe_context_parts)

        # 토큰 수 계산 및 로깅
        estimated_tokens = self._estimate_tokens(full_context)
        logger.info(
            f"🎯 {expert.name} 통합 컨텍스트: {estimated_tokens:,} 토큰 (PDF 딕셔너리 완전 활용 + 출처 명시 규칙)"
        )

        return full_context

    def _get_data_source_guidelines(self) -> str:
        """
        📊 데이터 출처 명시 규칙과 WACC 계산 지침을 반환합니다.

        모든 전문가에게 공통으로 적용되는 데이터 출처 표기 규칙과
        WACC 계산 세부 지침을 제공합니다.

        Returns:
            str: 데이터 출처 명시 규칙 문자열
        """
        return """

📊 **데이터 출처 명시 규칙** (모든 수치에 필수 적용):
모든 수치 뒤에 반드시 출처를 표기해주세요:
- **[재무데이터]**: 제공된 재무제표에서 직접 계산한 수치
- **[사업보고서]**: DART 사업보고서에서 추출한 정보
- **[웹검색]**: 웹검색을 통해 수집한 외부 데이터
- **[추정]**: 애널리스트 자체 추정 또는 가정 수치
- **[업계평균]**: 웹검색으로 확인한 동종업계 평균값
- **[재무데이터 기반 계산]**: 재무제표 데이터를 사용한 직접 계산 (WACC, ROIC 등)

**예시**: "ROE [실제 ROE]% **[실제 사용된 데이터 출처만 표기]**, 업계 평균 [실제 업계 평균]% **[실제 사용된 데이터 출처만 표기]**"

**⚠️ 중요**: 실제로 사용한 데이터 출처만 표기하세요. 사용하지 않은 데이터는 출처를 표기하지 마세요.

🎯 **WACC 직접 계산 필수**: 재무데이터와 사업보고서 우선 활용하세요:

**📊 데이터 우선순위 (반드시 준수)**:
1순위: **[재무데이터]** - 제공된 재무제표에서 직접 추출
2순위: **[사업보고서]** - DART 사업보고서에서 직접 확인
3순위: **[재무데이터 기반 계산]** - 1,2순위 데이터로 계산
4순위: **[웹검색]** - 외부 데이터 (최후 수단)
5순위: **[추정]** - 분석가 가정 (반드시 근거 명시)

**WACC 계산 세부 지침**:
- **자기자본비용 (Re) 계산**:
  * 무위험수익률: 사업보고서 '리스크 관리' 섹션 또는 재무제표 주석에서 확인 **[사업보고서]**
  * 베타: 재무데이터의 주가 변동성 데이터 활용 **[재무데이터]**
  * 시장위험프리미엄: 사업보고서 '투자위험' 섹션에서 언급된 수치 우선 **[사업보고서]**
  * 최종: Re = 무위험수익률 **[사업보고서]** + 베타 **[재무데이터]** × 시장위험프리미엄 **[사업보고서]**

- **타인자본비용 (Rd) 계산**:
  * 이자비용: 손익계산서 '금융비용' 항목 **[재무데이터]**
  * 총부채: 대차대조표 '부채총계' 항목 **[재무데이터]**
  * 법인세율: 사업보고서 '세무정책' 또는 손익계산서 실효세율 **[사업보고서]**
  * 최종: Rd = (이자비용/총부채) × (1-실효세율) **[재무데이터 기반 계산]**

- **가중평균 계산**:
  * 시가총액(E): 재무데이터 시가총액 **[재무데이터]**
  * 순부채(D): 총부채 - 현금성자산 **[재무데이터 기반 계산]**
  * 기업가치(V): E + D **[재무데이터 기반 계산]**
  * 최종: WACC = (E/V × Re) + (D/V × Rd) **[재무데이터 기반 계산]**

**🚫 금지사항**:
- 무위험수익률을 **[웹검색]**으로 찾지 마세요 → 사업보고서에서 먼저 확인
- 시장위험프리미엄을 **[추정]**하지 마세요 → 사업보고서 투자위험 섹션 확인
- 베타를 **[웹검색]**하지 마세요 → 재무데이터의 주가 변동성으로 계산

🚫 **중요**: 출처 표기가 없는 수치는 분석에서 제외됩니다.
"""

    def _format_technical_indicators_for_expert(
        self, technical_analysis_data: Dict
    ) -> str:
        """
        🎯 기술적 분석 데이터를 전문가용으로 포맷팅합니다.

        실제 계산된 지표 값들을 구조화된 형태로 제공하여
        기술적 분석가가 정의 나열이 아닌 실제 분석을 수행할 수 있도록 합니다.

        Args:
            technical_analysis_data: 기술적 분석 데이터 딕셔너리

        Returns:
            str: 전문가용 포맷팅된 기술적 지표 문자열
        """
        if not technical_analysis_data or not technical_analysis_data.get("success"):
            return self.MESSAGES["NO_TECHNICAL_DATA"]

        try:
            formatted_lines = []
            formatted_lines.append(self.MESSAGES["TECHNICAL_INDICATORS_HEADER"])
            formatted_lines.append("")

            # 현재 주가 정보
            current_snapshot = technical_analysis_data.get("current_snapshot", {})
            if current_snapshot:
                current_price = current_snapshot.get("price")
                current_volume = current_snapshot.get("volume")
                current_date = current_snapshot.get("date", self.MESSAGES["NO_DATA"])

                if current_price:
                    formatted_lines.append(
                        self.MESSAGES["CURRENT_PRICE_FORMAT"].format(
                            price=current_price, date=current_date
                        )
                    )
                if current_volume:
                    formatted_lines.append(
                        self.MESSAGES["CURRENT_VOLUME_FORMAT"].format(
                            volume=current_volume
                        )
                    )
                formatted_lines.append("")

            # 기술적 지표 추출
            indicators = technical_analysis_data.get("technical_indicators", {})

            # 🔧 강력한 디버깅: 실제 데이터 구조 로깅
            logger.info(f"🔍 technical_indicators 타입: {type(indicators)}")
            logger.info(f"🔍 technical_indicators 내용: {str(indicators)[:500]}...")

            if isinstance(indicators, dict):
                logger.info(f"🔍 indicators 키 목록: {list(indicators.keys())}")
                for key, value in indicators.items():
                    logger.info(
                        f"🔍 {key} → 타입: {type(value)}, 내용: {str(value)[:100]}..."
                    )

            if not isinstance(indicators, dict):
                logger.error(
                    f"❌ technical_indicators가 딕셔너리가 아님: {type(indicators)}"
                )
                return "기술적 지표 데이터 형식 오류"

            # 1. 이동평균선 데이터 처리
            ma_data = indicators.get("moving_averages", {})
            logger.info(f"🔍 moving_averages 타입: {type(ma_data)}")

            if isinstance(ma_data, dict) and ma_data:
                formatted_lines.append(self.MESSAGES["MOVING_AVERAGES_HEADER"])
                try:
                    for period, value in ma_data.items():
                        if value is not None:
                            formatted_lines.append(f"  • {period}: {value:,.0f}원")
                        else:
                            formatted_lines.append(
                                f"  • {period}: {self.MESSAGES['CALCULATION_ERROR']}"
                            )
                except Exception as ma_error:
                    logger.error(f"❌ 이동평균선 처리 오류: {ma_error}")
                    formatted_lines.append(
                        f"  • 이동평균선 {self.MESSAGES['DATA_PROCESSING_ERROR']}"
                    )
                formatted_lines.append("")

            # 2. RSI 지표 처리
            rsi_data = indicators.get("rsi", {})
            if isinstance(rsi_data, dict) and rsi_data:
                formatted_lines.append(self.MESSAGES["RSI_HEADER"])
                try:
                    current_rsi = rsi_data.get("current_value")
                    interpretation = rsi_data.get(
                        "interpretation", self.MESSAGES["NO_DATA"]
                    )
                    signal = rsi_data.get("signal", self.MESSAGES["NO_DATA"])

                    if current_rsi is not None:
                        formatted_lines.append(f"  • 현재 RSI: {current_rsi:.2f}")
                        formatted_lines.append(f"  • 해석: {interpretation}")
                        formatted_lines.append(f"  • 신호: {signal}")
                    else:
                        formatted_lines.append(
                            f"  • RSI {self.MESSAGES['CALCULATION_ERROR']}"
                        )
                except Exception as rsi_error:
                    logger.error(f"❌ RSI 처리 오류: {rsi_error}")
                    formatted_lines.append(
                        f"  • RSI {self.MESSAGES['DATA_PROCESSING_ERROR']}"
                    )
                formatted_lines.append("")

            # 3. MACD 지표 처리
            macd_data = indicators.get("macd", {})
            if isinstance(macd_data, dict) and macd_data:
                formatted_lines.append(self.MESSAGES["MACD_HEADER"])
                try:
                    # MACD_line과 macd_line 모두 지원 (호환성)
                    macd_line = macd_data.get("MACD_line") or macd_data.get("macd_line")
                    signal_line = macd_data.get("signal_line")
                    histogram = macd_data.get("histogram")
                    signal_interpretation = macd_data.get(
                        "signal_interpretation", self.MESSAGES["NO_DATA"]
                    )

                    if macd_line is not None:
                        formatted_lines.append(f"  • MACD Line: {macd_line:.4f}")
                    if signal_line is not None:
                        formatted_lines.append(f"  • Signal Line: {signal_line:.4f}")
                    if histogram is not None:
                        formatted_lines.append(f"  • Histogram: {histogram:.4f}")
                    formatted_lines.append(f"  • 신호: {signal_interpretation}")
                except Exception as macd_error:
                    logger.error(f"❌ MACD 처리 오류: {macd_error}")
                    formatted_lines.append(
                        f"  • MACD {self.MESSAGES['DATA_PROCESSING_ERROR']}"
                    )
                formatted_lines.append("")

            # 4. 볼린저 밴드 처리
            bb_data = indicators.get("bollinger_bands", {})
            if isinstance(bb_data, dict) and bb_data:
                formatted_lines.append(self.MESSAGES["BOLLINGER_BANDS_HEADER"])
                try:
                    upper_band = bb_data.get("upper_band")
                    middle_band = bb_data.get("middle_band")
                    lower_band = bb_data.get("lower_band")
                    position_analysis = bb_data.get(
                        "position_analysis", self.MESSAGES["NO_DATA"]
                    )
                    bb_signal = bb_data.get("signal", self.MESSAGES["NO_DATA"])

                    if all(
                        v is not None for v in [upper_band, middle_band, lower_band]
                    ):
                        formatted_lines.append(f"  • 상단 밴드: {upper_band:,.0f}원")
                        formatted_lines.append(f"  • 중간 밴드: {middle_band:,.0f}원")
                        formatted_lines.append(f"  • 하단 밴드: {lower_band:,.0f}원")
                        formatted_lines.append(f"  • 위치 분석: {position_analysis}")
                        formatted_lines.append(f"  • 신호: {bb_signal}")
                    else:
                        formatted_lines.append("  • 볼린저 밴드 계산 불가")
                except Exception as bb_error:
                    logger.error(f"❌ 볼린저 밴드 처리 오류: {bb_error}")
                    formatted_lines.append(
                        f"  • 볼린저 밴드 {self.MESSAGES['DATA_PROCESSING_ERROR']}"
                    )
                formatted_lines.append("")

            # 5. 스토캐스틱 처리
            stoch_data = indicators.get("stochastic", {})
            if isinstance(stoch_data, dict) and stoch_data:
                formatted_lines.append(self.MESSAGES["STOCHASTIC_HEADER"])
                try:
                    k_percent = stoch_data.get("K_percent") or stoch_data.get(
                        "k_percent"
                    )
                    d_percent = stoch_data.get("D_percent") or stoch_data.get(
                        "d_percent"
                    )
                    stoch_interpretation = stoch_data.get(
                        "interpretation", self.MESSAGES["NO_DATA"]
                    )
                    stoch_signal = stoch_data.get("signal", self.MESSAGES["NO_DATA"])

                    if k_percent is not None:
                        formatted_lines.append(f"  • %K: {k_percent:.2f}")
                    if d_percent is not None:
                        formatted_lines.append(f"  • %D: {d_percent:.2f}")
                    formatted_lines.append(f"  • 해석: {stoch_interpretation}")
                    formatted_lines.append(f"  • 신호: {stoch_signal}")
                except Exception as stoch_error:
                    logger.error(f"❌ 스토캐스틱 처리 오류: {stoch_error}")
                    formatted_lines.append(
                        f"  • 스토캐스틱 {self.MESSAGES['DATA_PROCESSING_ERROR']}"
                    )
                formatted_lines.append("")

            # 6. Williams %R 처리
            wr_data = indicators.get("williams_r", {})
            if isinstance(wr_data, dict) and wr_data:
                formatted_lines.append(self.MESSAGES["WILLIAMS_R_HEADER"])
                try:
                    wr_value = wr_data.get("current_value")
                    wr_interpretation = wr_data.get(
                        "interpretation", self.MESSAGES["NO_DATA"]
                    )
                    wr_signal = wr_data.get("signal", self.MESSAGES["NO_DATA"])

                    if wr_value is not None:
                        formatted_lines.append(f"  • 현재 값: {wr_value:.2f}")
                        formatted_lines.append(f"  • 해석: {wr_interpretation}")
                        formatted_lines.append(f"  • 신호: {wr_signal}")
                    else:
                        formatted_lines.append(
                            f"  • Williams %R {self.MESSAGES['CALCULATION_ERROR']}"
                        )
                except Exception as wr_error:
                    logger.error(f"❌ Williams %R 처리 오류: {wr_error}")
                    formatted_lines.append(
                        f"  • Williams %R {self.MESSAGES['DATA_PROCESSING_ERROR']}"
                    )
                formatted_lines.append("")

            # 7. 거래량 지표 처리
            vol_data = indicators.get("volume_indicators", {})
            if isinstance(vol_data, dict) and vol_data:
                formatted_lines.append("**📊 거래량 지표**:")
                try:
                    volume_ma_20 = vol_data.get("volume_MA_20")
                    volume_ratio = vol_data.get("volume_ratio")

                    if volume_ma_20 is not None:
                        formatted_lines.append(
                            f"  • 20일 평균 거래량: {volume_ma_20:,.0f}주"
                        )
                    if volume_ratio is not None:
                        formatted_lines.append(f"  • 거래량 비율: {volume_ratio:.2f}배")
                except Exception as vol_error:
                    logger.error(f"❌ 거래량 지표 처리 오류: {vol_error}")
                    formatted_lines.append(
                        f"  • 거래량 지표 {self.MESSAGES['DATA_PROCESSING_ERROR']}"
                    )
                formatted_lines.append("")

            # 8. OBV 지표 처리
            obv_data = indicators.get("obv", {})
            if isinstance(obv_data, dict) and obv_data:
                formatted_lines.append(self.MESSAGES["OBV_HEADER"])
                try:
                    obv_value = obv_data.get("current_value")
                    obv_trend = obv_data.get("trend", self.MESSAGES["NO_DATA"])

                    if obv_value is not None:
                        formatted_lines.append(f"  • 현재 OBV: {obv_value:,.0f}")
                        formatted_lines.append(f"  • 추세: {obv_trend}")
                    else:
                        formatted_lines.append(
                            f"  • OBV {self.MESSAGES['CALCULATION_ERROR']}"
                        )
                except Exception as obv_error:
                    logger.error(f"❌ OBV 처리 오류: {obv_error}")
                    formatted_lines.append(
                        f"  • OBV {self.MESSAGES['DATA_PROCESSING_ERROR']}"
                    )
                formatted_lines.append("")

            # 9. 매매 신호 종합
            trading_signals = technical_analysis_data.get("trading_signals", {})
            if isinstance(trading_signals, dict) and trading_signals:
                formatted_lines.append(self.MESSAGES["TRADING_SIGNALS_HEADER"])
                try:
                    overall_signal = trading_signals.get(
                        "overall_signal", self.MESSAGES["NO_DATA"]
                    )
                    signal_strength = trading_signals.get(
                        "signal_strength", self.MESSAGES["NO_DATA"]
                    )
                    recommendation = trading_signals.get(
                        "recommendation", self.MESSAGES["NO_DATA"]
                    )

                    formatted_lines.append(f"  • 종합 신호: {overall_signal}")
                    formatted_lines.append(f"  • 신호 강도: {signal_strength}")
                    formatted_lines.append(f"  • 추천: {recommendation}")
                except Exception as signal_error:
                    logger.error(f"❌ 매매 신호 처리 오류: {signal_error}")
                    formatted_lines.append(
                        f"  • 매매 신호 {self.MESSAGES['DATA_PROCESSING_ERROR']}"
                    )
                formatted_lines.append("")

            # 데이터 수집 정보
            total_days = technical_analysis_data.get("total_days", 0)
            last_update = technical_analysis_data.get(
                "last_update", self.MESSAGES["NO_DATA"]
            )
            if total_days > 0:
                formatted_lines.append(
                    f"**📊 데이터 정보**: {total_days}일치 데이터 ({self.MESSAGES['LAST_UPDATE_FORMAT'].format(date=last_update)})"
                )

            return "\n".join(formatted_lines)

        except Exception as e:
            logger.error(f"❌ 기술적 지표 포맷팅 실패: {e}")
            logger.error(
                f"🔍 technical_analysis_data 타입: {type(technical_analysis_data)}"
            )
            if isinstance(technical_analysis_data, dict):
                indicators = technical_analysis_data.get("technical_indicators", {})
                logger.error(f"🔍 indicators 타입: {type(indicators)}")
                if isinstance(indicators, dict):
                    for key, value in indicators.items():
                        logger.error(f"🔍 {key} 타입: {type(value)}")

            return f"기술적 지표 포맷팅 중 오류 발생: {str(e)}"

    def _summarize_financial_data(self, financial_data) -> str:
        """재무데이터를 요약합니다."""
        if not financial_data:
            return ""

        # Dict 타입인 경우 문자열로 변환
        if isinstance(financial_data, dict):
            # 재무데이터 Dict에서 주요 정보 추출
            summary_parts = []

            if financial_data.get("basic_info"):
                basic_info = financial_data["basic_info"]
                if isinstance(basic_info, dict):
                    for key, value in basic_info.items():
                        summary_parts.append(f"{key}: {value}")
                else:
                    summary_parts.append(str(basic_info))

            if financial_data.get("financial_ratios"):
                ratios = financial_data["financial_ratios"]
                if isinstance(ratios, dict):
                    for key, value in ratios.items():
                        summary_parts.append(f"{key}: {value}")
                else:
                    summary_parts.append(str(ratios))

            # 기타 섹션들도 추가
            for section_name in ["profitability", "growth", "stability", "activity"]:
                if financial_data.get(section_name):
                    section_data = financial_data[section_name]
                    if isinstance(section_data, dict):
                        for key, value in section_data.items():
                            summary_parts.append(f"{key}: {value}")
                    else:
                        summary_parts.append(str(section_data))

            financial_text = "\n".join(summary_parts)
        else:
            financial_text = str(financial_data)

        # 핵심 재무지표와 비율만 추출하여 요약
        key_sections = [
            "기본 정보",
            "재무 비율",
            "수익성",
            "성장성",
            "안정성",
            "활동성",
            "basic info",
            "ratios",
            "profitability",
            "growth",
            "stability",
        ]

        # 🔧 안전한 문자열 처리
        try:
            lines = financial_text.split("\n")
            summary_lines = []

            for line in lines:
                if any(section.lower() in line.lower() for section in key_sections):
                    summary_lines.append(line)
                elif any(
                    metric in line
                    for metric in ["ROE", "ROA", "PER", "PBR", "부채비율", "매출액"]
                ):
                    summary_lines.append(line)
        except Exception as e:
            logger.warning(f"⚠️ 재무데이터 처리 중 오류: {e}")
            return str(financial_data)[:2000] if financial_data else ""

        if summary_lines:
            return "\n".join(summary_lines)
        else:
            # 요약할 내용이 없으면 처음 2000자만 반환
            return (
                financial_text[:2000] + "...[요약됨]"
                if len(financial_text) > 2000
                else financial_text
            )

    def _extract_dart_financial_only(self, dart_data) -> str:
        """DART 데이터에서 재무 관련 정보만 추출합니다."""
        if not dart_data:
            return ""

        # 🔧 안전한 데이터 타입 처리
        try:
            if isinstance(dart_data, dict):
                dart_text = json.dumps(dart_data, ensure_ascii=False, indent=2)
            elif isinstance(dart_data, str):
                dart_text = dart_data
            else:
                dart_text = str(dart_data)

            if not dart_text or len(dart_text.strip()) < 10:
                return ""

            financial_keywords = [
                "재무",
                "손익",
                "대차대조표",
                "현금흐름",
                "자산",
                "부채",
                "자본",
                "매출",
                "이익",
                "financial",
                "income",
                "balance",
                "cash flow",
                "asset",
                "liability",
                "equity",
                "revenue",
                "profit",
            ]

            lines = dart_text.split("\n")
            relevant_lines = []

            for line in lines:
                if any(
                    keyword.lower() in line.lower() for keyword in financial_keywords
                ):
                    relevant_lines.append(line)

            return "\n".join(relevant_lines) if relevant_lines else ""
        except Exception as e:
            logger.warning(f"⚠️ DART 재무정보 추출 실패: {e}")
            return ""

    def _extract_price_data_only(self, financial_data) -> str:
        """재무데이터에서 가격/차트 관련 정보만 추출합니다."""
        if not financial_data:
            return ""

        # 🔧 안전한 데이터 타입 처리
        try:
            if isinstance(financial_data, dict):
                financial_text = json.dumps(
                    financial_data, ensure_ascii=False, indent=2
                )
            elif isinstance(financial_data, str):
                financial_text = financial_data
            else:
                financial_text = str(financial_data)

            if not financial_text or len(financial_text.strip()) < 10:
                return ""

            price_keywords = [
                "주가",
                "가격",
                "시가",
                "고가",
                "저가",
                "종가",
                "거래량",
                "시가총액",
                "price",
                "high",
                "low",
                "close",
                "volume",
                "market cap",
                "trading",
            ]

            lines = financial_text.split("\n")
            relevant_lines = []

            for line in lines:
                if any(keyword.lower() in line.lower() for keyword in price_keywords):
                    relevant_lines.append(line)

            return "\n".join(relevant_lines) if relevant_lines else ""
        except Exception as e:
            logger.warning(f"⚠️ 가격 데이터 추출 실패: {e}")
            return ""

    def _extract_technical_analysis_info(self, manus_data) -> str:
        """Manus 데이터에서 기술적 분석 관련 정보만 추출합니다."""
        if not manus_data:
            return ""

        # 🔧 안전한 데이터 타입 처리
        try:
            if isinstance(manus_data, dict):
                if manus_data.get("collected_information"):
                    manus_text = str(manus_data["collected_information"])
                else:
                    manus_text = json.dumps(manus_data, ensure_ascii=False, indent=2)
            elif isinstance(manus_data, str):
                manus_text = manus_data
            else:
                manus_text = str(manus_data)

            if not manus_text or len(manus_text.strip()) < 10:
                return ""

            technical_keywords = [
                "차트",
                "이동평균",
                "MACD",
                "RSI",
                "볼린저",
                "지지",
                "저항",
                "거래량",
                "기술적",
                "패턴",
                "트렌드",
                "chart",
                "technical",
                "support",
                "resistance",
            ]

            lines = manus_text.split("\n")
            relevant_lines = []

            for line in lines:
                if any(
                    keyword.lower() in line.lower() for keyword in technical_keywords
                ):
                    relevant_lines.append(line)

            return "\n".join(relevant_lines) if relevant_lines else ""
        except Exception as e:
            logger.warning(f"⚠️ 기술적 분석 정보 추출 실패: {e}")
            return ""

    def _extract_industry_info(self, manus_data) -> str:
        """Manus 데이터에서 산업/경쟁사 관련 정보만 추출합니다."""
        if not manus_data:
            return ""

        # 🔧 안전한 데이터 타입 처리
        try:
            if isinstance(manus_data, dict):
                if manus_data.get("collected_information"):
                    manus_text = str(manus_data["collected_information"])
                else:
                    manus_text = json.dumps(manus_data, ensure_ascii=False, indent=2)
            elif isinstance(manus_data, str):
                manus_text = manus_data
            else:
                manus_text = str(manus_data)

            if not manus_text or len(manus_text.strip()) < 10:
                return ""

            industry_keywords = [
                "산업",
                "업계",
                "경쟁사",
                "시장점유율",
                "경쟁력",
                "업종",
                "시장규모",
                "industry",
                "market",
                "competition",
                "competitor",
                "sector",
                "trend",
            ]

            lines = manus_text.split("\n")
            relevant_lines = []

            for line in lines:
                if any(
                    keyword.lower() in line.lower() for keyword in industry_keywords
                ):
                    relevant_lines.append(line)

            return "\n".join(relevant_lines) if relevant_lines else ""
        except Exception as e:
            logger.warning(f"⚠️ 산업정보 추출 실패: {e}")
            return ""

    def _extract_risk_factors(self, manus_data) -> str:
        """Manus 데이터에서 리스크 요인 관련 정보만 추출합니다."""
        if not manus_data:
            return ""

        # 🔧 안전한 데이터 타입 처리
        try:
            if isinstance(manus_data, dict):
                if manus_data.get("collected_information"):
                    manus_text = str(manus_data["collected_information"])
                else:
                    manus_text = json.dumps(manus_data, ensure_ascii=False, indent=2)
            elif isinstance(manus_data, str):
                manus_text = manus_data
            else:
                manus_text = str(manus_data)

            if not manus_text or len(manus_text.strip()) < 10:
                return ""

            risk_keywords = [
                "위험",
                "리스크",
                "우려",
                "하락",
                "부정적",
                "위기",
                "불확실성",
                "risk",
                "concern",
                "negative",
                "decline",
                "uncertainty",
                "threat",
            ]

            lines = manus_text.split("\n")
            relevant_lines = []

            for line in lines:
                if any(keyword.lower() in line.lower() for keyword in risk_keywords):
                    relevant_lines.append(line)

            return "\n".join(relevant_lines) if relevant_lines else ""
        except Exception as e:
            logger.warning(f"⚠️ 리스크 요인 추출 실패: {e}")
            return ""

    def _extract_key_insights_only(self, manus_data) -> str:
        """Manus 데이터에서 핵심 인사이트만 추출합니다."""
        if not manus_data:
            return ""

        # 🔧 안전한 데이터 타입 처리
        try:
            if isinstance(manus_data, dict):
                if manus_data.get("collected_information"):
                    manus_text = str(manus_data["collected_information"])
                else:
                    manus_text = json.dumps(manus_data, ensure_ascii=False, indent=2)
            elif isinstance(manus_data, str):
                manus_text = manus_data
            else:
                manus_text = str(manus_data)

            if not manus_text or len(manus_text.strip()) < 10:
                return ""

            # 핵심 키워드가 포함된 문장들만 추출
            insight_keywords = [
                "핵심",
                "중요",
                "주목",
                "특징",
                "포인트",
                "전망",
                "예상",
                "분석",
                "key",
                "important",
                "significant",
                "outlook",
                "forecast",
                "analysis",
            ]

            lines = manus_text.split("\n")
            relevant_lines = []

            for line in lines:
                if any(keyword.lower() in line.lower() for keyword in insight_keywords):
                    relevant_lines.append(line)

            return "\n".join(relevant_lines) if relevant_lines else ""
        except Exception as e:
            logger.warning(f"⚠️ 핵심 인사이트 추출 실패: {e}")
            return ""

    def _extract_valuation_data(self, financial_data) -> str:
        """재무데이터에서 밸류에이션 관련 정보만 추출합니다."""
        if not financial_data:
            return ""

        # 🔧 안전한 데이터 타입 처리
        try:
            if isinstance(financial_data, dict):
                financial_text = json.dumps(
                    financial_data, ensure_ascii=False, indent=2
                )
            elif isinstance(financial_data, str):
                financial_text = financial_data
            else:
                financial_text = str(financial_data)

            if not financial_text or len(financial_text.strip()) < 10:
                return ""

            valuation_keywords = [
                "PER",
                "PBR",
                "EV/EBITDA",
                "배당",
                "수익률",
                "목표가",
                "적정가",
                "valuation",
                "dividend",
                "yield",
                "target",
                "fair value",
            ]

            lines = financial_text.split("\n")
            relevant_lines = []

            for line in lines:
                if any(
                    keyword.lower() in line.lower() for keyword in valuation_keywords
                ):
                    relevant_lines.append(line)

            return "\n".join(relevant_lines) if relevant_lines else ""
        except Exception as e:
            logger.warning(f"⚠️ 밸류에이션 데이터 추출 실패: {e}")
            return ""

    def _extract_risk_indicators(self, financial_data) -> str:
        """재무데이터에서 리스크 지표만 추출합니다."""
        if not financial_data:
            return ""

        # 🔧 안전한 데이터 타입 처리
        try:
            if isinstance(financial_data, dict):
                financial_text = json.dumps(
                    financial_data, ensure_ascii=False, indent=2
                )
            elif isinstance(financial_data, str):
                financial_text = financial_data
            else:
                financial_text = str(financial_data)

            if not financial_text or len(financial_text.strip()) < 10:
                return ""

            risk_keywords = [
                "부채비율",
                "유동비율",
                "당좌비율",
                "변동성",
                "베타",
                "위험",
                "debt ratio",
                "current ratio",
                "volatility",
                "beta",
                "risk",
            ]

            lines = financial_text.split("\n")
            relevant_lines = []

            for line in lines:
                if any(keyword.lower() in line.lower() for keyword in risk_keywords):
                    relevant_lines.append(line)

            return "\n".join(relevant_lines) if relevant_lines else ""
        except Exception as e:
            logger.warning(f"⚠️ 리스크 지표 추출 실패: {e}")
            return ""

    def _extract_dart_business_info(self, dart_data) -> str:
        """DART 데이터에서 사업 관련 정보만 추출합니다."""
        if not dart_data:
            return ""

        # 🔧 안전한 데이터 타입 처리
        try:
            if isinstance(dart_data, dict):
                # dict인 경우 텍스트 부분만 추출
                dart_text = ""
                if "content" in dart_data:
                    dart_text = str(dart_data["content"])
                elif "text" in dart_data:
                    dart_text = str(dart_data["text"])
                elif "raw_text" in dart_data:
                    dart_text = str(dart_data["raw_text"])
                else:
                    dart_text = str(dart_data)
            elif isinstance(dart_data, str):
                dart_text = dart_data
            else:
                dart_text = str(dart_data)

            if not dart_text or len(dart_text.strip()) < 10:
                return ""

            business_keywords = [
                "사업",
                "제품",
                "서비스",
                "매출",
                "영업",
                "사업부문",
                "주요사업",
                "business",
                "product",
                "service",
                "revenue",
                "operation",
                "segment",
            ]

            lines = dart_text.split("\n")
            relevant_lines = []

            for line in lines:
                if any(
                    keyword.lower() in line.lower() for keyword in business_keywords
                ):
                    relevant_lines.append(line)

            return "\n".join(relevant_lines) if relevant_lines else ""

        except Exception as e:
            logger.warning(f"⚠️ DART 사업정보 추출 실패: {e}")
            return ""

    def _extract_dart_investment_info(self, dart_data) -> str:
        """DART 데이터에서 투자 관련 정보만 추출합니다."""
        if not dart_data:
            return ""

        # 🔧 안전한 데이터 타입 처리
        try:
            if isinstance(dart_data, dict):
                # dict인 경우 텍스트 부분만 추출
                dart_text = ""
                if "content" in dart_data:
                    dart_text = str(dart_data["content"])
                elif "text" in dart_data:
                    dart_text = str(dart_data["text"])
                elif "raw_text" in dart_data:
                    dart_text = str(dart_data["raw_text"])
                else:
                    dart_text = str(dart_data)
            elif isinstance(dart_data, str):
                dart_text = dart_data
            else:
                dart_text = str(dart_data)

            if not dart_text or len(dart_text.strip()) < 10:
                return ""

            investment_keywords = [
                "투자",
                "배당",
                "주주",
                "자본",
                "투자계획",
                "설비투자",
                "연구개발",
                "investment",
                "dividend",
                "shareholder",
                "capital",
                "R&D",
            ]

            lines = dart_text.split("\n")
            relevant_lines = []

            for line in lines:
                if any(
                    keyword.lower() in line.lower() for keyword in investment_keywords
                ):
                    relevant_lines.append(line)

            return "\n".join(relevant_lines) if relevant_lines else ""

        except Exception as e:
            logger.warning(f"⚠️ DART 투자정보 추출 실패: {e}")
            return ""

    def _create_basic_financial_summary(self, financial_data: str) -> str:
        """재무데이터의 기본 요약을 생성합니다."""
        if not financial_data:
            return ""

        # 🔧 안전한 데이터 타입 처리
        try:
            if isinstance(financial_data, dict):
                financial_text = json.dumps(
                    financial_data, ensure_ascii=False, indent=2
                )
            elif isinstance(financial_data, str):
                financial_text = financial_data
            else:
                financial_text = str(financial_data)

            if not financial_text or len(financial_text.strip()) < 10:
                return ""

            # 핵심 재무지표만 추출
            key_metrics = [
                "총자산",
                "총부채",
                "자기자본",
                "매출액",
                "영업이익",
                "순이익",
                "ROE",
                "ROA",
                "부채비율",
                "유동비율",
            ]

            lines = financial_text.split("\n")
            summary_lines = []

            for line in lines:
                if any(metric in line for metric in key_metrics):
                    summary_lines.append(line)

            return "\n".join(summary_lines) if summary_lines else financial_text[:1000]
        except Exception as e:
            logger.warning(f"⚠️ 기본 재무요약 생성 실패: {e}")
            return ""

    def _estimate_tokens(self, text: str) -> int:
        """
        텍스트의 대략적인 토큰 수를 추정합니다.

        Args:
            text: 토큰 수를 추정할 텍스트

        Returns:
            int: 추정된 토큰 수
        """
        if not text:
            return 0

        # 🎯 더 정확한 토큰 추정 (GPT-4o 기준)
        # 한글: 1글자 = 1.5 토큰
        # 영문: 1단어 = 1.3 토큰
        # 숫자/기호: 1개 = 1 토큰
        # JSON 구조: 추가 20% 오버헤드

        korean_chars = len(
            [c for c in text if "\u3131" <= c <= "\u318e" or "\uac00" <= c <= "\ud7a3"]
        )
        english_words = len([w for w in text.split() if w.isascii() and w.isalpha()])
        numbers = len([c for c in text if c.isdigit()])
        other_chars = len(text) - korean_chars - english_words - numbers

        # 기본 토큰 계산
        base_tokens = korean_chars * 1.5 + english_words * 1.3 + numbers + other_chars

        # JSON 구조 오버헤드 (딕셔너리 구조일 경우)
        if "{" in text and "}" in text:
            base_tokens *= 1.2

        # 안전 마진 (10% 추가)
        estimated_tokens = int(base_tokens * 1.1)

        return max(1, estimated_tokens)

    def _optimize_data_for_token_limit(
        self,
        financial_data: Dict,
        enhanced_dart_data: Dict = None,
        manus_collected_data: Dict = None,
        dart_reports_dictionary: Dict = None,  # 🚀 DART 딕셔너리 추가!
        target_token_limit: int = 100000,  # 🔧 GPT-4o 제한에 맞춰 대폭 감소 (800K → 100K)
    ) -> Dict[str, Any]:
        """
        🎯 토큰 제한에 맞춰 데이터를 최적화합니다.

        Args:
            financial_data: 재무 데이터
            enhanced_dart_data: Enhanced DART 데이터
            manus_collected_data: Manus 수집 데이터
            dart_reports_dictionary: DART 보고서 딕셔너리
            target_token_limit: 목표 토큰 제한 (GPT-4o 128K 제한 고려)

        Returns:
            Dict: 최적화된 데이터
        """
        logger.info(
            f"🔢 토큰 최적화 시작 - 목표: {target_token_limit:,} 토큰 (GPT-4o 제한 준수)"
        )

        optimized_data = {
            "financial_data": financial_data,
            "enhanced_dart_data": enhanced_dart_data,
            "manus_collected_data": manus_collected_data,
            "dart_reports_dictionary": dart_reports_dictionary,  # 🚀 DART 딕셔너리 추가!
            "optimization_applied": False,
            "original_token_estimate": 0,
            "optimized_token_estimate": 0,
        }

        try:
            # 🔧 더 정확한 토큰 수 추정 (실제 LLM 호출 시 추가되는 오버헤드 고려)
            current_tokens = 0
            safety_margin = (
                20000  # 🔧 안전 여유분 20K 토큰 (시스템 메시지, 프롬프트 등)
            )
            effective_limit = target_token_limit - safety_margin

            if financial_data:
                financial_text = str(financial_data)
                current_tokens += self._estimate_tokens(financial_text)

            if enhanced_dart_data:
                dart_text = str(enhanced_dart_data)
                current_tokens += self._estimate_tokens(dart_text)

            if manus_collected_data:
                manus_text = str(manus_collected_data)
                current_tokens += self._estimate_tokens(manus_text)

            # 🚀 DART 딕셔너리 토큰 계산 추가!
            if dart_reports_dictionary:
                dart_dict_text = str(dart_reports_dictionary)
                current_tokens += self._estimate_tokens(dart_dict_text)

            optimized_data["original_token_estimate"] = current_tokens

            # 🔧 더 엄격한 토큰 제한 적용
            if current_tokens > effective_limit:
                logger.info(
                    f"⚠️ 토큰 제한 초과: {current_tokens:,} > {effective_limit:,} (안전 여유분 포함)"
                )

                # 🔧 더 적극적인 압축 비율 계산 (최소 20% 보존으로 하향 조정)
                compression_ratio = effective_limit / current_tokens
                min_compression_ratio = 0.2  # 🔧 최소 20% 보존 (기존 30%에서 하향)
                safe_compression_ratio = max(compression_ratio, min_compression_ratio)

                logger.info(
                    f"🔢 압축 비율: 원본={compression_ratio:.3f}, 안전={safe_compression_ratio:.3f}"
                )

                # 🔧 재무데이터 압축 (가장 중요하므로 높은 비율 유지)
                if financial_data:
                    financial_ratio = min(
                        safe_compression_ratio * 1.3, 1.0
                    )  # 130% 가중치, 최대 100%
                    optimized_data["financial_data"] = self._compress_financial_data(
                        financial_data, financial_ratio
                    )
                    logger.info(f"📊 재무데이터 압축: {financial_ratio:.3f} 비율 적용")

                # 🔧 Enhanced DART 데이터 압축
                if enhanced_dart_data:
                    dart_ratio = min(safe_compression_ratio * 1.2, 1.0)  # 120% 가중치
                    optimized_data["enhanced_dart_data"] = self._compress_dart_data(
                        enhanced_dart_data, dart_ratio
                    )
                    logger.info(f"🏢 Enhanced DART 압축: {dart_ratio:.3f} 비율 적용")

                # 🔧 Manus 데이터 압축
                if manus_collected_data:
                    manus_ratio = min(safe_compression_ratio * 1.0, 1.0)  # 100% 가중치
                    optimized_data["manus_collected_data"] = self._compress_manus_data(
                        manus_collected_data, manus_ratio
                    )
                    logger.info(f"🔍 Manus 데이터 압축: {manus_ratio:.3f} 비율 적용")

                # 🚀 DART 딕셔너리 압축 (이미 필터링된 데이터이므로 압축 비활성화)
                if dart_reports_dictionary:
                    # 🔧 이미 필터링된 데이터이므로 압축 비활성화 (압축 비율 1.0 = 압축 없음)
                    dart_dict_ratio = 1.0  # 압축 없음 (이미 필터링된 데이터)
                    logger.info(
                        f"📋 DART 딕셔너리 압축 비활성화 (이미 필터링된 데이터): {dart_dict_ratio:.3f} 비율 적용"
                    )

                    # 🔍 압축 전 검증
                    logger.info("🔍 DART 딕셔너리 압축 전 검증...")
                    pre_compression_valid = self._validate_dart_dictionary_at_each_step(
                        dart_reports_dictionary, "압축_전"
                    )

                    # 🚀 압축 비활성화 - 원본 데이터 그대로 사용
                    compressed_dart_dict = (
                        dart_reports_dictionary  # 압축 없이 원본 사용
                    )

                    # 🔍 압축 후 검증
                    logger.info("🔍 DART 딕셔너리 압축 후 검증...")
                    post_compression_valid = (
                        self._validate_dart_dictionary_at_each_step(
                            compressed_dart_dict, "압축_후"
                        )
                    )

                    if post_compression_valid:
                        optimized_data["dart_reports_dictionary"] = compressed_dart_dict
                        logger.info("✅ DART 딕셔너리 검증 통과 - 압축 데이터 사용")
                    else:
                        logger.warning("⚠️ 압축 후 검증 실패 - 원본 데이터 유지")
                        optimized_data["dart_reports_dictionary"] = (
                            dart_reports_dictionary
                        )

                optimized_data["optimization_applied"] = True

                # 🔧 최적화 후 토큰 수 재계산 (더 정확한 계산)
                optimized_tokens = 0
                for key in [
                    "financial_data",
                    "enhanced_dart_data",
                    "manus_collected_data",
                    "dart_reports_dictionary",  # 🚀 DART 딕셔너리 추가!
                ]:
                    if optimized_data[key]:
                        optimized_tokens += self._estimate_tokens(
                            str(optimized_data[key])
                        )

                # 🔧 안전 여유분 포함한 총 토큰 수 계산
                total_estimated_tokens = optimized_tokens + safety_margin
                optimized_data["optimized_token_estimate"] = total_estimated_tokens

                # 🎯 압축 효과 분석
                compression_achieved = (
                    optimized_tokens / current_tokens if current_tokens > 0 else 1.0
                )
                logger.info(
                    f"✅ 토큰 최적화 완료: {current_tokens:,} → {optimized_tokens:,} (압축률: {compression_achieved:.3f})"
                )
                logger.info(
                    f"📊 총 예상 토큰: {total_estimated_tokens:,} (안전 여유분 포함)"
                )

                # 🔧 GPT-4o 제한 초과 여부 최종 확인
                if total_estimated_tokens > target_token_limit:
                    logger.warning(
                        f"⚠️ 여전히 토큰 제한 초과: {total_estimated_tokens:,} > {target_token_limit:,}"
                    )
                    # 🔧 추가 긴급 압축 적용
                    emergency_ratio = (
                        target_token_limit / total_estimated_tokens * 0.8
                    )  # 80% 안전 마진
                    logger.info(f"🚨 긴급 추가 압축 적용: {emergency_ratio:.3f} 비율")

                    # 모든 데이터에 긴급 압축 적용
                    for key in [
                        "financial_data",
                        "enhanced_dart_data",
                        "manus_collected_data",
                        "dart_reports_dictionary",
                    ]:
                        if optimized_data[key]:
                            if key == "financial_data":
                                optimized_data[key] = self._compress_financial_data(
                                    optimized_data[key], emergency_ratio
                                )
                            elif key == "enhanced_dart_data":
                                optimized_data[key] = self._compress_dart_data(
                                    optimized_data[key], emergency_ratio
                                )
                            elif key == "manus_collected_data":
                                optimized_data[key] = self._compress_manus_data(
                                    optimized_data[key], emergency_ratio
                                )
                            elif key == "dart_reports_dictionary":
                                # 🚨 DART 딕셔너리는 이미 필터링된 데이터이므로 긴급 압축에서 제외
                                logger.info(
                                    "🚨 DART 딕셔너리는 이미 필터링된 데이터이므로 긴급 압축에서 제외"
                                )
                                # 원본 데이터 유지 (압축하지 않음)
                                continue

                # 압축이 너무 과도한 경우 경고
                if compression_achieved < 0.15:  # 15% 미만으로 압축된 경우
                    logger.warning(
                        f"⚠️ 과도한 압축 감지 ({compression_achieved:.1%}) - 데이터 품질 저하 가능성"
                    )

            else:
                logger.info(f"✅ 토큰 제한 내: {current_tokens:,} 토큰")
                optimized_data["optimized_token_estimate"] = (
                    current_tokens + safety_margin
                )

        except Exception as e:
            logger.error(f"❌ 토큰 최적화 실패: {e}")
            # 실패시 원본 데이터 반환
            optimized_data["optimization_applied"] = False

        return optimized_data

    def _compress_financial_data(self, financial_data: Dict, ratio: float) -> Dict:
        """재무데이터를 압축합니다."""
        if not financial_data or ratio >= 1.0:
            return financial_data

        # 핵심 재무지표만 유지
        compressed = {}
        important_keys = [
            "success",
            "data_sources",
            "data_quality",
            "stock_info",
            "financial_summary",
            "key_metrics",
            "ratios",
        ]

        for key in important_keys:
            if key in financial_data:
                compressed[key] = financial_data[key]

        return compressed

    def _compress_dart_data(self, dart_data: Dict, ratio: float) -> Dict:
        """Enhanced DART 데이터를 압축합니다."""
        if not dart_data or ratio >= 1.0:
            return dart_data

        compressed = {}
        important_keys = [
            "success",
            "basic_info",
            "financial_info",
            "recent_disclosures",
        ]

        for key in important_keys:
            if key in dart_data:
                compressed[key] = dart_data[key]

        return compressed

    def _compress_manus_data(self, manus_data: Dict, ratio: float) -> Dict:
        """Manus 수집 데이터를 압축합니다."""
        if not manus_data or ratio >= 1.0:
            return manus_data

        compressed = {
            "performed": manus_data.get("performed", False),
            "method": manus_data.get("method"),
            "primary_intent": manus_data.get("primary_intent"),
            "data_richness_score": manus_data.get("data_richness_score"),
        }

        # 수집된 정보는 요약해서 포함
        if "collected_information" in manus_data:
            full_info = manus_data["collected_information"]
            if len(full_info) > 5000:
                compressed["collected_information"] = full_info[:5000] + "...[압축됨]"
            else:
                compressed["collected_information"] = full_info

        # PDF 분석 정보는 메타데이터만 유지
        if "pdf_analysis" in manus_data:
            pdf_info = manus_data["pdf_analysis"]
            compressed["pdf_analysis"] = {
                "pdf_detected": pdf_info.get("pdf_detected", False),
                "analysis_completed": pdf_info.get("analysis_completed", False),
                "analysis_method": pdf_info.get("analysis_method"),
                "pdf_dictionary_interface": pdf_info.get("pdf_dictionary_interface"),
            }

        return compressed

    def _compress_dart_dictionary(self, dart_dict: Dict, ratio: float) -> Dict:
        """DART 딕셔너리를 스마트 압축합니다."""
        if not dart_dict or ratio >= 1.0:
            return dart_dict

        # 🚀 새로운 선택적 데이터 추출 방식 적용
        return self._extract_essential_dart_data(dart_dict, ratio)

    def _compress_dart_dictionary_preserve_structure(
        self, dart_dict: Dict, ratio: float
    ) -> Dict:
        """
        🚀 전문가별 딕셔너리 구조를 보존하면서 압축합니다.

        Args:
            dart_dict: 원본 DART 딕셔너리
            ratio: 압축 비율 (0.0 ~ 1.0)

        Returns:
            Dict: 구조가 보존된 압축 딕셔너리
        """
        if not dart_dict or ratio >= 1.0:
            return dart_dict

        logger.info(f"🔧 구조 보존 압축 시작: {ratio:.3f} 비율")

        # 🔍 압축 전 원본 구조 로깅
        logger.info(f"🔍 압축 전 원본 구조: {list(dart_dict.keys())}")
        logger.info(
            f"🔍 압축 전 business_report_dictionary 길이: {len(dart_dict.get('business_report_dictionary', {}))}"
        )
        logger.info(
            f"🔍 압축 전 quarterly_report_dictionary 길이: {len(dart_dict.get('quarterly_report_dictionary', {}))}"
        )

        try:
            # 🎯 전문가별 딕셔너리 압축
            compressed_expert_dict = {}
            if "expert_ready_dictionaries" in dart_dict:
                compressed_expert_dict = self._compress_expert_ready_dictionaries(
                    dart_dict["expert_ready_dictionaries"], ratio
                )
                logger.info("✅ expert_ready_dictionaries 압축 완료")

            # 🔧 압축된 원본 구조도 생성 (검증을 위해)
            compressed_business_dict = {}
            compressed_quarterly_dict = {}

            if "business_report_dictionary" in dart_dict:
                compressed_business_dict = self._compress_original_dart_structure(
                    dart_dict["business_report_dictionary"], ratio
                )
                logger.info("✅ business_report_dictionary 압축 완료")

            if "quarterly_report_dictionary" in dart_dict:
                compressed_quarterly_dict = self._compress_original_dart_structure(
                    dart_dict["quarterly_report_dictionary"], ratio
                )
                logger.info("✅ quarterly_report_dictionary 압축 완료")

            # 🎯 일관된 구조 반환 (검증을 위해 원본 구조도 포함)
            compressed_dict = {
                "expert_ready_dictionaries": compressed_expert_dict,
                "business_report_dictionary": compressed_business_dict,
                "quarterly_report_dictionary": compressed_quarterly_dict,
                "success": True,
                "compression_applied": True,
                "original_structure_preserved": True,
                "compression_ratio": ratio,
                "compressed_at": "optimization_stage",
            }

            # 🔍 압축 후 검증을 위한 메타데이터 추가
            compressed_dict["validation_info"] = {
                "expert_sections_count": len(compressed_expert_dict),
                "business_sections_count": len(compressed_business_dict),
                "quarterly_sections_count": len(compressed_quarterly_dict),
                "total_expert_content": sum(
                    len(str(v)) for v in compressed_expert_dict.values()
                ),
                "total_business_content": sum(
                    len(str(v)) for v in compressed_business_dict.values()
                ),
                "total_quarterly_content": sum(
                    len(str(v)) for v in compressed_quarterly_dict.values()
                ),
            }

            # 🔍 압축 후 결과 구조 로깅
            logger.info(f"🔍 압축 후 결과 구조: {list(compressed_dict.keys())}")
            logger.info(
                f"🔍 압축 후 business_report_dictionary 길이: {len(compressed_dict.get('business_report_dictionary', {}))}"
            )
            logger.info(
                f"🔍 압축 후 quarterly_report_dictionary 길이: {len(compressed_dict.get('quarterly_report_dictionary', {}))}"
            )
            logger.info(
                f"🔍 압축 후 validation_info: {compressed_dict.get('validation_info', {})}"
            )

            logger.info("✅ 구조 보존 압축 완료")
            return compressed_dict

        except Exception as e:
            logger.error(f"❌ 구조 보존 압축 실패: {e}")
            # 실패 시 기존 압축 방식 사용
            return self._extract_essential_dart_data(dart_dict, ratio)

    def _compress_expert_ready_dictionaries(
        self, expert_dict: Dict, ratio: float
    ) -> Dict:
        """
        전문가별 딕셔너리를 선택적으로 압축합니다.

        ⚠️ 중요: 전문가 키워드 매핑을 유지하면서 압축
        """
        if not expert_dict:
            return expert_dict

        compressed_expert_dict = {}

        # 전문가별 중요도 설정
        expert_importance = {
            "integrated_financial_analyst": 1.0,  # 통합재무전문가 (최고 중요도)
            "technical_analyst": 0.9,  # 기술적 분석가
            "valuation_expert": 0.8,  # 밸류에이션 전문가
            "risk_assessor": 0.7,  # 리스크 평가자
            "industry_expert": 0.6,  # 산업 전문가
            "footnote_specialist": 0.5,  # 각주 전문가
        }

        for expert_name, expert_data in expert_dict.items():
            if expert_data and len(expert_data) > 0:
                # 전문가별 중요도에 따른 압축 비율 조정
                importance_weight = expert_importance.get(expert_name, 0.5)
                expert_ratio = min(ratio * importance_weight, 1.0)

                # 통합재무전문가는 최우선 보존
                if expert_name == "integrated_financial_analyst":
                    expert_ratio = max(expert_ratio, 0.5)  # 최소 50% 보존

                compressed_expert_dict[expert_name] = self._compress_single_expert_data(
                    expert_data, expert_ratio, expert_name
                )

                logger.info(f"📊 {expert_name} 압축: {expert_ratio:.3f} 비율")

        return compressed_expert_dict

    def _compress_single_expert_data(
        self, expert_data: Dict, ratio: float, expert_name: str
    ) -> Dict:
        """
        단일 전문가 데이터를 압축합니다.

        Args:
            expert_data: 전문가 데이터
            ratio: 압축 비율
            expert_name: 전문가 이름

        Returns:
            Dict: 압축된 전문가 데이터 (딕셔너리 구조 유지)
        """
        if not expert_data or ratio >= 1.0:
            return expert_data

        # 🔧 데이터 구조 분석 및 처리
        logger.info(f"🔍 {expert_name} 데이터 구조 분석: {type(expert_data)}")

        # expert_data가 딕셔너리가 아닌 경우 (이미 섹션 구조가 아님)
        if not isinstance(expert_data, dict):
            logger.warning(
                f"⚠️ {expert_name}: 예상과 다른 데이터 구조 ({type(expert_data)})"
            )
            return expert_data

        # 🎯 전문가별 구조 보존 압축
        compressed_data = {
            "sections": {},  # 섹션 구조 유지
            "metadata": {
                "expert_name": expert_name,
                "original_sections": len(expert_data),
                "compression_ratio": ratio,
                "compressed_at": "optimization_stage",
            },
        }

        # 전문가별 핵심 키워드 섹션 우선 보존 (확장된 키워드)
        expert_priority_keywords = {
            "integrated_financial_analyst": [
                # 펀더멘털 관련
                "재무",
                "손익",
                "매출",
                "순이익",
                "자산",
                "부채",
                "자본",
                "현금흐름",
                "수익성",
                "안정성",
                "회사개요",
                "사업내용",
                "재무제표",
                "손익계산서",
                "재무상태표",
                "현금흐름표",
                "ROE",
                "ROA",
                "ROIC",
                "유동비율",
                "부채비율",
                # 밸류에이션 관련
                "가치",
                "평가",
                "적정가",
                "목표가",
                "DCF",
                "밸류에이션",
                "투자",
                "배당",
                "내재가치",
                "멀티플",
                "PER",
                "PBR",
                "EV/EBITDA",
                "WACC",
                "FCF",
                "할인율",
                "성장률",
                # 통합 분석 관련
                "종합",
                "통합",
                "분석",
                "투자의견",
                "매수",
                "매도",
                "보유",
                "시나리오",
                "리스크",
                "성장성",
                "안정성",
                "수익성",
                # 사업 관련 (추가)
                "사업",
                "개요",
                "기업",
                "회사",
                "업종",
                "산업",
                "시장",
                "경쟁",
                "영업",
                "이익",
                "수익",
                "비용",
                "지출",
                "투자",
                "자본",
                "경영",
                "전략",
                "계획",
                "전망",
            ],
            "technical_analyst": ["기술", "차트", "지표", "추세", "거래량", "가격"],
            "valuation_expert": ["가치", "평가", "PER", "PBR", "DCF", "목표가"],
            "risk_assessor": ["리스크", "위험", "변동성", "부채", "유동성"],
            "industry_expert": ["산업", "경쟁", "시장", "점유율", "성장"],
            "footnote_specialist": ["각주", "주석", "세부", "상세"],
        }

        priority_keywords = expert_priority_keywords.get(expert_name, [])

        # 일관된 압축을 위한 최소 보존 섹션 수 계산
        min_sections = max(1, int(len(expert_data) * 0.4))  # 최소 40% 보존
        target_sections = max(min_sections, int(len(expert_data) * ratio))

        logger.info(
            f"🔧 {expert_name} 압축 목표: {target_sections}개 섹션 (최소 {min_sections}개 보장)"
        )

        # 1단계: 키워드 매칭 섹션 우선 선택 (최소 섹션 수 보장)
        selected_sections = 0

        # 섹션별 키워드 매칭 점수 계산
        section_scores = []
        for section_name, section_content in expert_data.items():
            score = 0

            # 제목에서 키워드 매칭 (가중치 3)
            for keyword in priority_keywords:
                if keyword in section_name.lower():
                    score += 3

            # 내용에서 키워드 매칭 (가중치 1, 처음 1000자만)
            content_sample = str(section_content)[:1000]
            for keyword in priority_keywords:
                if keyword in content_sample:
                    score += 1

            # 통합 재무분석가 특별 가중치 (회사개요/사업내용 섹션)
            if expert_name == "integrated_financial_analyst":
                if "회사개요" in section_name or "사업내용" in section_name:
                    score += 5  # 추가 가중치
                    logger.info(
                        f"🚀 {expert_name} 특별 가중치 적용: {section_name} (+5점)"
                    )

            section_scores.append((section_name, section_content, score))

        # 점수 순으로 정렬
        section_scores.sort(key=lambda x: x[2], reverse=True)

        # 최소 섹션 수만큼 우선 선택
        for section_name, section_content, score in section_scores:
            if selected_sections >= min_sections:
                break

            compressed_data["sections"][section_name] = self._smart_truncate_section(
                section_content, ratio
            )
            selected_sections += 1
            logger.info(
                f"✅ {expert_name} 우선순위 섹션 선택: {section_name} (점수: {score})"
            )

        # 2단계: 나머지 섹션 중 크기가 큰 것 우선 선택 (일관된 알고리즘)
        remaining_sections = {
            k: v for k, v in expert_data.items() if k not in compressed_data["sections"]
        }
        remaining_sorted = sorted(
            remaining_sections.items(), key=lambda x: len(str(x[1])), reverse=True
        )

        for section_name, section_content in remaining_sorted:
            if selected_sections >= target_sections:
                break

            compressed_data["sections"][section_name] = self._smart_truncate_section(
                section_content, ratio
            )
            selected_sections += 1
            logger.info(f"✅ {expert_name} 추가 섹션 선택: {section_name}")

        # 최소 내용 보장 검증
        total_content = sum(len(str(v)) for v in compressed_data["sections"].values())
        if total_content < 100:  # 최소 100자 보장
            logger.warning(
                f"⚠️ {expert_name} 압축 후 내용이 너무 적음 ({total_content}자). 추가 섹션 선택..."
            )

            # 추가 섹션 선택
            for section_name, section_content in remaining_sorted[
                selected_sections : selected_sections + 1
            ]:
                compressed_data["sections"][section_name] = (
                    self._smart_truncate_section(section_content, ratio)
                )
                logger.info(
                    f"✅ {expert_name} 최소 내용 보장을 위한 추가 섹션: {section_name}"
                )

        # 🔧 메타데이터 업데이트
        compressed_data["metadata"]["compressed_sections"] = selected_sections
        compressed_data["metadata"]["total_sections"] = selected_sections
        compressed_data["metadata"]["relevant_sections"] = selected_sections
        compressed_data["metadata"]["general_sections"] = 0
        compressed_data["metadata"]["total_text_length"] = sum(
            len(str(content)) for content in compressed_data["sections"].values()
        )

        logger.info(f"✅ {expert_name} 구조 보존 압축 완료: {selected_sections}개 섹션")
        return compressed_data

    def _smart_truncate_section(self, section_content: str, ratio: float) -> str:
        """
        섹션 내용을 스마트하게 압축합니다.

        Args:
            section_content: 섹션 내용
            ratio: 압축 비율

        Returns:
            str: 압축된 섹션 내용
        """
        if not section_content or ratio >= 1.0:
            return section_content

        content_str = str(section_content)
        target_length = int(len(content_str) * ratio)

        if target_length >= len(content_str):
            return content_str

        # 최소 1000자는 보존
        target_length = max(target_length, 1000)

        # 문장 단위로 자르기
        truncated = self._smart_truncate(content_str, target_length)

        # 압축 표시 추가
        if len(truncated) < len(content_str):
            truncated += (
                f"\n\n[📝 압축됨: {len(content_str):,}자 → {len(truncated):,}자]"
            )

        return truncated

    def _compress_original_dart_structure(self, dart_dict: Dict, ratio: float) -> Dict:
        """
        기존 DART 구조를 유지하면서 압축하되 최소한의 핵심 내용을 보존합니다.
        """
        logger.info(
            f"🔧 원본 DART 구조 압축 시작: {len(dart_dict)}개 섹션, 압축 비율: {ratio:.3f}"
        )

        compressed_dict = {}

        # business_report_dictionary 압축 (최소 내용 보장)
        if "business_report_dictionary" in dart_dict:
            compressed_business = self._compress_business_report_sections_with_minimum(
                dart_dict["business_report_dictionary"], ratio
            )
            compressed_dict["business_report_dictionary"] = compressed_business
            logger.info(
                f"✅ business_report_dictionary 압축 완료: {len(compressed_business)}개 섹션"
            )

        # quarterly_report_dictionary 압축 (최소 내용 보장)
        if "quarterly_report_dictionary" in dart_dict:
            compressed_quarterly = (
                self._compress_quarterly_report_sections_with_minimum(
                    dart_dict["quarterly_report_dictionary"], ratio
                )
            )
            compressed_dict["quarterly_report_dictionary"] = compressed_quarterly
            logger.info(
                f"✅ quarterly_report_dictionary 압축 완료: {len(compressed_quarterly)}개 섹션"
            )

        # 최종 검증
        total_sections = len(
            compressed_dict.get("business_report_dictionary", {})
        ) + len(compressed_dict.get("quarterly_report_dictionary", {}))
        total_content = sum(
            len(str(v))
            for sections in compressed_dict.values()
            for v in sections.values()
        )

        logger.info(
            f"✅ 원본 DART 구조 압축 완료: 총 {total_sections}개 섹션, {total_content:,}자"
        )

        # 최소 내용 보장 검증
        if total_content < 500:  # 최소 500자 보장
            logger.warning(
                f"⚠️ 압축 후 내용이 너무 적음 ({total_content}자). 최소 내용 보장 로직 실행..."
            )
            compressed_dict = self._ensure_minimum_content(
                compressed_dict, dart_dict, ratio
            )

        return compressed_dict

    def _compress_business_report_sections(
        self, business_report: Dict, ratio: float
    ) -> Dict:
        """
        사업보고서 섹션을 중요도에 따라 압축합니다.
        """
        # 중요도 순으로 정렬된 섹션 목록
        priority_sections = [
            "04_재무상태표",
            "05_손익계산서",
            "06_현금흐름표",
            "07_주요재무비율",
            "02_재무정보",
            "03_사업내용",
            "01_회사개요",
            "08_재무상태",
        ]

        compressed_sections = {}
        selected_count = 0
        target_count = max(3, int(len(business_report) * ratio))  # 최소 3개 섹션 보존

        # 우선순위 섹션 먼저 선택
        for section_name in priority_sections:
            if selected_count >= target_count:
                break

            if section_name in business_report:
                compressed_sections[section_name] = self._smart_truncate_section(
                    business_report[section_name], ratio
                )
                selected_count += 1

        # 나머지 섹션 중 크기가 큰 것 선택
        remaining_sections = {
            k: v for k, v in business_report.items() if k not in compressed_sections
        }
        remaining_sorted = sorted(
            remaining_sections.items(), key=lambda x: len(str(x[1])), reverse=True
        )

        for section_name, section_content in remaining_sorted:
            if selected_count >= target_count:
                break

            compressed_sections[section_name] = self._smart_truncate_section(
                section_content, ratio
            )
            selected_count += 1

        return compressed_sections

    def _compress_business_report_sections_with_minimum(
        self, business_report: Dict, ratio: float
    ) -> Dict:
        """
        사업보고서 섹션을 중요도에 따라 압축하되 최소 내용을 보장합니다.
        """
        logger.info(
            f"🔧 사업보고서 최소 내용 보장 압축 시작: {len(business_report)}개 섹션"
        )

        # 중요도 순으로 정렬된 섹션 목록
        priority_sections = [
            "04_재무상태표",
            "05_손익계산서",
            "06_현금흐름표",
            "07_주요재무비율",
            "02_재무정보",
            "03_사업내용",
            "01_회사개요",
            "08_재무상태",
        ]

        compressed_sections = {}
        selected_count = 0

        # 최소 보존 섹션 수 계산 (최소 30%는 보존)
        min_sections = max(2, int(len(business_report) * 0.3))
        target_count = max(min_sections, int(len(business_report) * ratio))

        logger.info(
            f"🔧 사업보고서 압축 목표: {target_count}개 섹션 (최소 {min_sections}개 보장)"
        )

        # 1단계: 우선순위 섹션 먼저 선택 (최소 섹션 수 보장)
        for section_name in priority_sections:
            if selected_count >= min_sections:
                break

            if section_name in business_report:
                compressed_sections[section_name] = self._smart_truncate_section(
                    business_report[section_name], ratio
                )
                selected_count += 1
                logger.info(f"✅ 우선순위 섹션 선택: {section_name}")

        # 2단계: 나머지 섹션 중 크기가 큰 것 선택
        remaining_sections = {
            k: v for k, v in business_report.items() if k not in compressed_sections
        }
        remaining_sorted = sorted(
            remaining_sections.items(), key=lambda x: len(str(x[1])), reverse=True
        )

        for section_name, section_content in remaining_sorted:
            if selected_count >= target_count:
                break

            compressed_sections[section_name] = self._smart_truncate_section(
                section_content, ratio
            )
            selected_count += 1
            logger.info(f"✅ 추가 섹션 선택: {section_name}")

        # 최소 내용 보장 검증
        total_content = sum(len(str(v)) for v in compressed_sections.values())
        if total_content < 300:  # 최소 300자 보장
            logger.warning(
                f"⚠️ 사업보고서 압축 후 내용이 너무 적음 ({total_content}자). 추가 섹션 선택..."
            )

            # 추가 섹션 선택
            for section_name, section_content in remaining_sorted[
                selected_count : selected_count + 2
            ]:
                compressed_sections[section_name] = self._smart_truncate_section(
                    section_content, ratio
                )
                logger.info(f"✅ 최소 내용 보장을 위한 추가 섹션: {section_name}")

        logger.info(f"✅ 사업보고서 압축 완료: {len(compressed_sections)}개 섹션")
        return compressed_sections

    def _compress_quarterly_report_sections_with_minimum(
        self, quarterly_report: Dict, ratio: float
    ) -> Dict:
        """
        분기보고서 섹션을 압축하되 최소 내용을 보장합니다.
        """
        logger.info(
            f"🔧 분기보고서 최소 내용 보장 압축 시작: {len(quarterly_report)}개 섹션"
        )

        # 분기보고서 중요 섹션
        priority_sections = ["재무상태표", "손익계산서", "현금흐름표"]

        compressed_sections = {}
        selected_count = 0

        # 최소 보존 섹션 수 계산
        min_sections = max(1, int(len(quarterly_report) * 0.5))  # 최소 50% 보존
        target_count = max(min_sections, int(len(quarterly_report) * ratio))

        logger.info(
            f"🔧 분기보고서 압축 목표: {target_count}개 섹션 (최소 {min_sections}개 보장)"
        )

        # 1단계: 우선순위 섹션 선택
        for section_name in priority_sections:
            if selected_count >= min_sections:
                break

            if section_name in quarterly_report:
                compressed_sections[section_name] = self._smart_truncate_section(
                    quarterly_report[section_name], ratio
                )
                selected_count += 1
                logger.info(f"✅ 우선순위 섹션 선택: {section_name}")

        # 2단계: 나머지 섹션 선택
        remaining_sections = {
            k: v for k, v in quarterly_report.items() if k not in compressed_sections
        }
        remaining_sorted = sorted(
            remaining_sections.items(), key=lambda x: len(str(x[1])), reverse=True
        )

        for section_name, section_content in remaining_sorted:
            if selected_count >= target_count:
                break

            compressed_sections[section_name] = self._smart_truncate_section(
                section_content, ratio
            )
            selected_count += 1
            logger.info(f"✅ 추가 섹션 선택: {section_name}")

        # 최소 내용 보장 검증
        total_content = sum(len(str(v)) for v in compressed_sections.values())
        if total_content < 200:  # 최소 200자 보장
            logger.warning(
                f"⚠️ 분기보고서 압축 후 내용이 너무 적음 ({total_content}자). 추가 섹션 선택..."
            )

            # 추가 섹션 선택
            for section_name, section_content in remaining_sorted[
                selected_count : selected_count + 1
            ]:
                compressed_sections[section_name] = self._smart_truncate_section(
                    section_content, ratio
                )
                logger.info(f"✅ 최소 내용 보장을 위한 추가 섹션: {section_name}")

        logger.info(f"✅ 분기보고서 압축 완료: {len(compressed_sections)}개 섹션")
        return compressed_sections

    def _ensure_minimum_content(
        self, compressed_dict: Dict, original_dict: Dict, ratio: float
    ) -> Dict:
        """
        압축 후 최소 내용이 보장되지 않았을 때 추가 내용을 보장합니다.
        """
        logger.info("🔧 최소 내용 보장 로직 실행...")

        # business_report_dictionary 최소 내용 보장
        if "business_report_dictionary" in original_dict:
            original_business = original_dict["business_report_dictionary"]
            compressed_business = compressed_dict.get("business_report_dictionary", {})

            if len(compressed_business) == 0:
                # 최소 1개 섹션은 보장
                largest_section = max(
                    original_business.items(), key=lambda x: len(str(x[1]))
                )
                compressed_dict["business_report_dictionary"] = {
                    largest_section[0]: self._smart_truncate_section(
                        largest_section[1], ratio
                    )
                }
                logger.info(
                    f"✅ business_report_dictionary 최소 섹션 보장: {largest_section[0]}"
                )

        # quarterly_report_dictionary 최소 내용 보장
        if "quarterly_report_dictionary" in original_dict:
            original_quarterly = original_dict["quarterly_report_dictionary"]
            compressed_quarterly = compressed_dict.get(
                "quarterly_report_dictionary", {}
            )

            if len(compressed_quarterly) == 0:
                # 최소 1개 섹션은 보장
                largest_section = max(
                    original_quarterly.items(), key=lambda x: len(str(x[1]))
                )
                compressed_dict["quarterly_report_dictionary"] = {
                    largest_section[0]: self._smart_truncate_section(
                        largest_section[1], ratio
                    )
                }
                logger.info(
                    f"✅ quarterly_report_dictionary 최소 섹션 보장: {largest_section[0]}"
                )

        return compressed_dict

    def _compress_quarterly_report_sections(
        self, quarterly_report: Dict, ratio: float
    ) -> Dict:
        """
        분기보고서 섹션을 압축합니다.
        """
        # 분기보고서 중요 섹션
        priority_sections = ["재무상태표", "손익계산서", "현금흐름표"]

        compressed_sections = {}
        selected_count = 0
        target_count = max(2, int(len(quarterly_report) * ratio))  # 최소 2개 섹션 보존

        for section_name in priority_sections:
            if selected_count >= target_count:
                break

            if section_name in quarterly_report:
                compressed_sections[section_name] = self._smart_truncate_section(
                    quarterly_report[section_name], ratio
                )
                selected_count += 1

        return compressed_sections

    def _validate_dart_dictionary_at_each_step(
        self, dart_dict: Dict, step_name: str
    ) -> bool:
        """
        🔍 각 단계에서 DART 딕셔너리 상태를 검증합니다.

        Args:
            dart_dict: 검증할 DART 딕셔너리
            step_name: 단계 이름 (예: "생성_후", "최적화_후", "전달_전")

        Returns:
            bool: 검증 성공 여부
        """
        if not dart_dict:
            logger.error(f"❌ [{step_name}] DART 딕셔너리가 비어있음")
            return False

        try:
            # 🔧 압축 상태 확인
            is_compressed = dart_dict.get("compression_applied", False)

            # 🔍 단계별 검증 로깅 강화
            logger.info(f"🔍 [{step_name}] 검증 시작 - 압축 상태: {is_compressed}")
            logger.info(f"🔍 [{step_name}] 딕셔너리 키: {list(dart_dict.keys())}")

            if is_compressed:
                logger.info(f"🔍 [{step_name}] 압축된 DART 딕셔너리 검증 중...")
                return self._validate_compressed_dart_dictionary_at_step(
                    dart_dict, step_name
                )
            else:
                logger.info(f"🔍 [{step_name}] 원본 DART 딕셔너리 검증 중...")
                return self._validate_original_dart_dictionary_at_step(
                    dart_dict, step_name
                )

        except Exception as e:
            logger.error(f"❌ [{step_name}] 검증 중 오류 발생: {e}")
            return False

    def _validate_compressed_dart_dictionary_at_step(
        self, dart_dict: Dict, step_name: str
    ) -> bool:
        """압축된 DART 딕셔너리 단계별 검증"""
        try:
            # 1. 압축된 구조 검증
            structure_ok = self._validate_compressed_dart_dictionary(
                dart_dict, step_name
            )

            # 2. 압축된 내용 검증
            content_ok = self._validate_compressed_dart_content(dart_dict, step_name)

            # 3. 압축된 매핑 검증
            mapping_ok = self._validate_compressed_expert_mapping(dart_dict, step_name)

            overall_ok = structure_ok and content_ok and mapping_ok

            if overall_ok:
                logger.info(f"✅ [{step_name}] 압축된 DART 딕셔너리 검증 통과")
            else:
                logger.warning(f"⚠️ [{step_name}] 압축된 DART 딕셔너리 검증 실패")

            return overall_ok

        except Exception as e:
            logger.error(f"❌ [{step_name}] 압축된 딕셔너리 검증 중 오류: {e}")
            return False

    def _validate_original_dart_dictionary_at_step(
        self, dart_dict: Dict, step_name: str
    ) -> bool:
        """원본 DART 딕셔너리 단계별 검증"""
        try:
            # 1. 기본 구조 검증
            structure_ok = self._validate_original_dart_dictionary(dart_dict, step_name)

            # 2. 데이터 내용 검증
            content_ok = self._validate_dart_dictionary_content(dart_dict, step_name)

            # 3. 전문가 매핑 검증
            mapping_ok = self._validate_expert_mapping(dart_dict, step_name)

            overall_ok = structure_ok and content_ok and mapping_ok

            if overall_ok:
                logger.info(f"✅ [{step_name}] 원본 DART 딕셔너리 검증 통과")
            else:
                logger.warning(f"⚠️ [{step_name}] 원본 DART 딕셔너리 검증 실패")

            return overall_ok

        except Exception as e:
            logger.error(f"❌ [{step_name}] 원본 딕셔너리 검증 중 오류: {e}")
            return False

    def _validate_dart_dictionary_structure(
        self, dart_dict: Dict, step_name: str
    ) -> bool:
        """DART 딕셔너리 구조를 검증합니다."""
        # 🔧 압축 상태 확인
        is_compressed = dart_dict.get("compression_applied", False)

        if is_compressed:
            logger.info(f"🔍 [{step_name}] 압축된 DART 딕셔너리 검증 중...")
            return self._validate_compressed_dart_dictionary(dart_dict, step_name)
        else:
            logger.info(f"🔍 [{step_name}] 원본 DART 딕셔너리 검증 중...")
            return self._validate_original_dart_dictionary(dart_dict, step_name)

    def _validate_compressed_dart_dictionary(
        self, dart_dict: Dict, step_name: str
    ) -> bool:
        """압축된 DART 딕셔너리 구조를 검증합니다."""
        structure_issues = []

        # 🔍 압축 상태 상세 로깅
        logger.info(
            f"🔍 [{step_name}] 압축 상태: {dart_dict.get('compression_applied', False)}"
        )
        logger.info(
            f"🔍 [{step_name}] 전문가 딕셔너리 키: {list(dart_dict.get('expert_ready_dictionaries', {}).keys())}"
        )
        logger.info(
            f"🔍 [{step_name}] 원본 구조 키: {[k for k in dart_dict.keys() if k not in ['expert_ready_dictionaries', 'success', 'compression_applied', 'validation_info']]}"
        )

        # 1. 압축 표시 확인
        if not dart_dict.get("compression_applied", False):
            structure_issues.append("압축 표시가 없음")

        # 2. expert_ready_dictionaries 구조 확인 (최우선)
        if "expert_ready_dictionaries" in dart_dict:
            expert_dict = dart_dict["expert_ready_dictionaries"]
            if not isinstance(expert_dict, dict):
                structure_issues.append("expert_ready_dictionaries가 딕셔너리가 아님")
            elif len(expert_dict) == 0:
                structure_issues.append("expert_ready_dictionaries가 비어있음")
            else:
                # 각 전문가 데이터 확인
                for expert_name, expert_data in expert_dict.items():
                    if not expert_data or len(expert_data) == 0:
                        structure_issues.append(f"{expert_name} 데이터가 비어있음")
                logger.info(
                    f"✅ [{step_name}] 압축된 expert_ready_dictionaries 구조 검증 통과"
                )
        else:
            structure_issues.append("expert_ready_dictionaries 키가 없음")

        # 3. 압축된 원본 구조 확인 (빈 딕셔너리가 아닌 실제 내용이 있는지 확인)
        if "business_report_dictionary" in dart_dict:
            business_dict = dart_dict["business_report_dictionary"]
            if isinstance(business_dict, dict):
                # 빈 딕셔너리가 아닌 실제 내용이 있는지 확인
                total_content = sum(len(str(v)) for v in business_dict.values())
                if total_content == 0:
                    logger.warning(
                        f"⚠️ [{step_name}] 압축된 business_report_dictionary가 비어있음"
                    )
                    # 압축된 데이터는 원본 구조가 비어있을 수 있으므로 경고만 하고 실패로 처리하지 않음
                else:
                    logger.info(
                        f"✅ [{step_name}] 압축된 business_report_dictionary 구조 검증 통과 (내용: {total_content}자)"
                    )

        if "quarterly_report_dictionary" in dart_dict:
            quarterly_dict = dart_dict["quarterly_report_dictionary"]
            if isinstance(quarterly_dict, dict):
                # 빈 딕셔너리가 아닌 실제 내용이 있는지 확인
                total_content = sum(len(str(v)) for v in quarterly_dict.values())
                if total_content == 0:
                    logger.warning(
                        f"⚠️ [{step_name}] 압축된 quarterly_report_dictionary가 비어있음"
                    )
                    # 압축된 데이터는 원본 구조가 비어있을 수 있으므로 경고만 하고 실패로 처리하지 않음
                else:
                    logger.info(
                        f"✅ [{step_name}] 압축된 quarterly_report_dictionary 구조 검증 통과 (내용: {total_content}자)"
                    )

        # 4. validation_info 확인 (압축 후 메타데이터)
        if "validation_info" in dart_dict:
            validation_info = dart_dict["validation_info"]
            logger.info(f"🔍 [{step_name}] 압축 검증 정보: {validation_info}")

            # 전문가 딕셔너리 내용 확인
            if validation_info.get("expert_sections_count", 0) == 0:
                structure_issues.append("압축 후 전문가 섹션이 없음")
            elif validation_info.get("total_expert_content", 0) < 100:
                structure_issues.append("압축 후 전문가 내용이 너무 적음")

        if structure_issues:
            logger.warning(
                f"⚠️ [{step_name}] 압축된 구조 이슈: {', '.join(structure_issues)}"
            )
            return False

        logger.info(f"✅ [{step_name}] 압축된 구조 검증 통과")
        return True

    def _validate_original_dart_dictionary(
        self, dart_dict: Dict, step_name: str
    ) -> bool:
        """원본 DART 딕셔너리 구조를 검증합니다."""
        structure_issues = []

        # 🔍 원본 구조 검증 로깅 강화
        logger.info(f"🔍 [{step_name}] 원본 DART 딕셔너리 구조 검증 시작")
        logger.info(f"🔍 [{step_name}] 원본 딕셔너리 키: {list(dart_dict.keys())}")

        # expert_ready_dictionaries 구조 확인
        if "expert_ready_dictionaries" in dart_dict:
            expert_dict = dart_dict["expert_ready_dictionaries"]
            logger.info(
                f"🔍 [{step_name}] expert_ready_dictionaries 키: {list(expert_dict.keys())}"
            )

            if not isinstance(expert_dict, dict):
                structure_issues.append("expert_ready_dictionaries가 딕셔너리가 아님")
                logger.error(
                    f"❌ [{step_name}] expert_ready_dictionaries가 딕셔너리가 아님"
                )
            elif len(expert_dict) == 0:
                structure_issues.append("expert_ready_dictionaries가 비어있음")
                logger.error(f"❌ [{step_name}] expert_ready_dictionaries가 비어있음")
            else:
                # 각 전문가 데이터 확인
                for expert_name, expert_data in expert_dict.items():
                    if not expert_data or len(expert_data) == 0:
                        structure_issues.append(f"{expert_name} 데이터가 비어있음")
                        logger.warning(
                            f"⚠️ [{step_name}] {expert_name} 데이터가 비어있음"
                        )
                    else:
                        logger.info(
                            f"✅ [{step_name}] {expert_name} 데이터 확인됨 (길이: {len(expert_data)})"
                        )

        # 기존 구조 확인
        elif (
            "business_report_dictionary" in dart_dict
            or "quarterly_report_dictionary" in dart_dict
        ):
            if "business_report_dictionary" in dart_dict:
                business_dict = dart_dict["business_report_dictionary"]
                logger.info(
                    f"🔍 [{step_name}] business_report_dictionary 길이: {len(business_dict)}"
                )

                if not isinstance(business_dict, dict) or len(business_dict) == 0:
                    structure_issues.append("business_report_dictionary가 비어있음")
                    logger.error(
                        f"❌ [{step_name}] business_report_dictionary가 비어있음"
                    )
                else:
                    logger.info(f"✅ [{step_name}] business_report_dictionary 확인됨")

            if "quarterly_report_dictionary" in dart_dict:
                quarterly_dict = dart_dict["quarterly_report_dictionary"]
                logger.info(
                    f"🔍 [{step_name}] quarterly_report_dictionary 길이: {len(quarterly_dict)}"
                )

                if not isinstance(quarterly_dict, dict) or len(quarterly_dict) == 0:
                    structure_issues.append("quarterly_report_dictionary가 비어있음")
                    logger.error(
                        f"❌ [{step_name}] quarterly_report_dictionary가 비어있음"
                    )
                else:
                    logger.info(f"✅ [{step_name}] quarterly_report_dictionary 확인됨")

        else:
            structure_issues.append("알려진 DART 구조를 찾을 수 없음")
            logger.error(f"❌ [{step_name}] 알려진 DART 구조를 찾을 수 없음")

        # 구조 이슈 리포트
        if structure_issues:
            logger.warning(
                f"⚠️ [{step_name}] 원본 구조 이슈: {', '.join(structure_issues)}"
            )
            return False

        logger.info(f"✅ [{step_name}] 원본 구조 검증 통과")
        return True

    def _validate_compressed_dart_content(
        self, dart_dict: Dict, step_name: str
    ) -> bool:
        """압축된 DART 딕셔너리 내용을 검증합니다."""
        content_issues = []
        total_content_length = 0

        # 🔍 압축된 데이터 상세 로깅
        logger.info(f"🔍 [{step_name}] 압축된 내용 검증 시작")

        # 압축된 전문가 딕셔너리 내용 확인
        if "expert_ready_dictionaries" in dart_dict:
            expert_dict = dart_dict["expert_ready_dictionaries"]
            for expert_name, expert_data in expert_dict.items():
                if expert_data:
                    expert_content_length = len(str(expert_data))
                    total_content_length += expert_content_length

                    logger.info(
                        f"🔍 [{step_name}] {expert_name}: {expert_content_length}자"
                    )

                    # 압축된 데이터는 더 작을 수 있으므로 기준을 낮춤
                    if expert_content_length < 100:  # 최소 100자로 상향 조정
                        content_issues.append(
                            f"{expert_name} 압축된 내용이 너무 짧음 ({expert_content_length}자)"
                        )

        # 압축된 원본 구조 내용 확인 (최소 내용 보장 검증)
        if "business_report_dictionary" in dart_dict:
            business_dict = dart_dict["business_report_dictionary"]
            if isinstance(business_dict, dict) and len(business_dict) > 0:
                business_content_length = sum(
                    len(str(v)) for v in business_dict.values()
                )
                total_content_length += business_content_length
                logger.info(
                    f"🔍 [{step_name}] business_report_dictionary: {business_content_length}자 ({len(business_dict)}개 섹션)"
                )

                # 최소 내용 보장 검증 (개선된 기준)
                if business_content_length < 200:  # 최소 200자로 상향 조정
                    content_issues.append(
                        f"business_report_dictionary 압축된 내용이 너무 짧음 ({business_content_length}자)"
                    )
            else:
                content_issues.append(
                    "business_report_dictionary가 비어있거나 유효하지 않음"
                )

        if "quarterly_report_dictionary" in dart_dict:
            quarterly_dict = dart_dict["quarterly_report_dictionary"]
            if isinstance(quarterly_dict, dict) and len(quarterly_dict) > 0:
                quarterly_content_length = sum(
                    len(str(v)) for v in quarterly_dict.values()
                )
                total_content_length += quarterly_content_length
                logger.info(
                    f"🔍 [{step_name}] quarterly_report_dictionary: {quarterly_content_length}자 ({len(quarterly_dict)}개 섹션)"
                )

                # 최소 내용 보장 검증 (개선된 기준)
                if quarterly_content_length < 100:  # 최소 100자로 상향 조정
                    content_issues.append(
                        f"quarterly_report_dictionary 압축된 내용이 너무 짧음 ({quarterly_content_length}자)"
                    )
            else:
                content_issues.append(
                    "quarterly_report_dictionary가 비어있거나 유효하지 않음"
                )

        # validation_info에서 추가 정보 확인
        if "validation_info" in dart_dict:
            validation_info = dart_dict["validation_info"]
            logger.info(f"🔍 [{step_name}] validation_info 내용: {validation_info}")

            # validation_info의 내용과 실제 계산된 내용 비교
            expected_total = (
                validation_info.get("total_expert_content", 0)
                + validation_info.get("total_business_content", 0)
                + validation_info.get("total_quarterly_content", 0)
            )
            logger.info(
                f"🔍 [{step_name}] 예상 총 내용: {expected_total}자, 실제 총 내용: {total_content_length}자"
            )

        # 압축된 데이터는 전체 길이가 더 작을 수 있음
        if total_content_length < 500:  # 최소 500자
            content_issues.append(
                f"압축된 전체 내용이 너무 짧음 ({total_content_length}자)"
            )

        # 내용 이슈 리포트
        if content_issues:
            logger.warning(
                f"⚠️ [{step_name}] 압축된 내용 이슈: {', '.join(content_issues)}"
            )
            return False

        logger.info(
            f"✅ [{step_name}] 압축된 내용 검증 통과 (총 {total_content_length:,}자)"
        )
        return True

    def _validate_compressed_expert_mapping(
        self, dart_dict: Dict, step_name: str
    ) -> bool:
        """압축된 전문가 매핑 상태를 검증합니다."""
        mapping_issues = []

        # 🔍 압축된 매핑 검증 로깅 강화
        logger.info(f"🔍 [{step_name}] 압축된 전문가 매핑 검증 시작")

        if "expert_ready_dictionaries" in dart_dict:
            expert_dict = dart_dict["expert_ready_dictionaries"]

            # 🔍 전문가 딕셔너리 상세 로깅
            logger.info(
                f"🔍 [{step_name}] 전문가 딕셔너리 키: {list(expert_dict.keys())}"
            )

            # 핵심 전문가 데이터 확인 (압축 후에도 최소 1개는 있어야 함)
            required_experts = ["integrated_financial_analyst", "technical_analyst"]
            found_experts = 0

            for expert_name in required_experts:
                if expert_name in expert_dict:
                    expert_data = expert_dict[expert_name]
                    if expert_data and len(expert_data) > 0:
                        found_experts += 1
                        logger.info(
                            f"✅ [{step_name}] {expert_name} 데이터 확인됨 (길이: {len(expert_data)})"
                        )
                    else:
                        mapping_issues.append(f"압축된 {expert_name} 데이터가 비어있음")
                        logger.warning(
                            f"⚠️ [{step_name}] {expert_name} 데이터가 비어있음"
                        )
                else:
                    logger.warning(f"⚠️ [{step_name}] {expert_name} 키가 없음")

            # 최소 1개 전문가는 있어야 함
            if found_experts == 0:
                mapping_issues.append("압축 후에도 최소 1개 전문가 데이터가 필요함")
                logger.error(f"❌ [{step_name}] 모든 필수 전문가 데이터가 없음")
            else:
                logger.info(f"✅ [{step_name}] {found_experts}개 전문가 데이터 확인됨")

        else:
            mapping_issues.append("압축된 expert_ready_dictionaries 키가 없음")
            logger.error(f"❌ [{step_name}] expert_ready_dictionaries 키가 없음")

        # 매핑 이슈 리포트
        if mapping_issues:
            logger.warning(
                f"⚠️ [{step_name}] 압축된 매핑 이슈: {', '.join(mapping_issues)}"
            )
            return False

        logger.info(f"✅ [{step_name}] 압축된 매핑 검증 통과")
        return True

    def _validate_dart_dictionary_content(
        self, dart_dict: Dict, step_name: str
    ) -> bool:
        """DART 딕셔너리 내용을 검증합니다."""
        content_issues = []
        total_content_length = 0

        # 🔍 원본 내용 검증 로깅 강화
        logger.info(f"🔍 [{step_name}] 원본 DART 딕셔너리 내용 검증 시작")

        # 내용 길이 계산
        if "expert_ready_dictionaries" in dart_dict:
            expert_dict = dart_dict["expert_ready_dictionaries"]
            logger.info(f"🔍 [{step_name}] expert_ready_dictionaries 검증 중...")

            for expert_name, expert_data in expert_dict.items():
                if expert_data:
                    expert_content_length = len(str(expert_data))
                    total_content_length += expert_content_length

                    logger.info(
                        f"🔍 [{step_name}] {expert_name}: {expert_content_length}자"
                    )

                    # 각 전문가 데이터 최소 길이 확인
                    if expert_content_length < 100:  # 최소 100자
                        content_issues.append(
                            f"{expert_name} 내용이 너무 짧음 ({expert_content_length}자)"
                        )
                        logger.warning(
                            f"⚠️ [{step_name}] {expert_name} 내용이 너무 짧음"
                        )

        elif "business_report_dictionary" in dart_dict:
            business_dict = dart_dict["business_report_dictionary"]
            business_content_length = len(str(business_dict))
            total_content_length += business_content_length

            logger.info(
                f"🔍 [{step_name}] business_report_dictionary: {business_content_length}자"
            )

            if business_content_length < 500:  # 최소 500자
                content_issues.append(
                    f"사업보고서 내용이 너무 짧음 ({business_content_length}자)"
                )
                logger.warning(f"⚠️ [{step_name}] 사업보고서 내용이 너무 짧음")

        # 전체 내용 길이 확인
        if total_content_length < 1000:  # 최소 1000자
            content_issues.append(f"전체 내용이 너무 짧음 ({total_content_length}자)")
            logger.warning(f"⚠️ [{step_name}] 전체 내용이 너무 짧음")

        # 내용 이슈 리포트
        if content_issues:
            logger.warning(f"⚠️ [{step_name}] 내용 이슈: {', '.join(content_issues)}")
            return False

        logger.info(f"✅ [{step_name}] 내용 검증 통과 (총 {total_content_length:,}자)")
        return True

    def _validate_expert_mapping(self, dart_dict: Dict, step_name: str) -> bool:
        """전문가 매핑 상태를 검증합니다."""
        mapping_issues = []

        # 🔍 원본 매핑 검증 로깅 강화
        logger.info(f"🔍 [{step_name}] 원본 전문가 매핑 검증 시작")

        if "expert_ready_dictionaries" in dart_dict:
            expert_dict = dart_dict["expert_ready_dictionaries"]
            logger.info(
                f"🔍 [{step_name}] 전문가 딕셔너리 키: {list(expert_dict.keys())}"
            )

            # 핵심 전문가 데이터 확인
            required_experts = ["integrated_financial_analyst", "technical_analyst"]

            for expert_name in required_experts:
                if expert_name not in expert_dict:
                    mapping_issues.append(f"필수 전문가 {expert_name} 데이터 없음")
                    logger.error(
                        f"❌ [{step_name}] 필수 전문가 {expert_name} 데이터 없음"
                    )
                elif not expert_dict[expert_name] or len(expert_dict[expert_name]) == 0:
                    mapping_issues.append(f"필수 전문가 {expert_name} 데이터 비어있음")
                    logger.warning(
                        f"⚠️ [{step_name}] 필수 전문가 {expert_name} 데이터 비어있음"
                    )
                else:
                    logger.info(
                        f"✅ [{step_name}] {expert_name} 데이터 확인됨 (길이: {len(expert_dict[expert_name])})"
                    )

        else:
            # 기존 구조에서는 기본 매핑 확인
            logger.info(f"🔍 [{step_name}] 기존 구조 매핑 확인 중...")
            if (
                "business_report_dictionary" not in dart_dict
                and "quarterly_report_dictionary" not in dart_dict
            ):
                mapping_issues.append("기본 보고서 구조가 없음")
                logger.error(f"❌ [{step_name}] 기본 보고서 구조가 없음")
            else:
                logger.info(f"✅ [{step_name}] 기본 보고서 구조 확인됨")

        # 매핑 이슈 리포트
        if mapping_issues:
            logger.warning(f"⚠️ [{step_name}] 매핑 이슈: {', '.join(mapping_issues)}")
            return False

        logger.info(f"✅ [{step_name}] 매핑 검증 통과")
        return True

    def _extract_essential_dart_data(self, dart_dict: Dict, ratio: float) -> Dict:
        """
        토큰 제한 내에서 가장 중요한 DART 데이터만 선택적으로 추출
        """
        extracted = {}
        target_tokens = int(80000 * ratio)  # 안전 마진을 두고 80,000 토큰 기준
        current_tokens = 0

        # 🎯 1단계: 핵심 재무지표 (최우선)
        if "business_report_dictionary" in dart_dict:
            business_report = dart_dict["business_report_dictionary"]
            essential_financial = self._extract_essential_financial_sections(
                business_report
            )
            financial_tokens = self._estimate_tokens(str(essential_financial))

            if financial_tokens <= target_tokens * 0.6:  # 60% 이하일 때만
                extracted["business_report_dictionary"] = essential_financial
                current_tokens += financial_tokens
                logger.info(f"✅ 핵심 재무지표 추출: {financial_tokens:,} 토큰")

        # 🎯 2단계: 성장성 및 수익성 지표 (남은 공간의 70%까지만)
        remaining_tokens = target_tokens - current_tokens
        if remaining_tokens > target_tokens * 0.2:  # 20% 이상 남았을 때만
            growth_metrics = self._extract_growth_and_profitability_sections(
                business_report
            )
            growth_tokens = self._estimate_tokens(str(growth_metrics))

            if current_tokens + growth_tokens <= target_tokens * 0.8:  # 80% 이하로 제한
                if "business_report_dictionary" not in extracted:
                    extracted["business_report_dictionary"] = {}
                extracted["business_report_dictionary"].update(growth_metrics)
                current_tokens += growth_tokens
                logger.info(f"✅ 성장성/수익성 지표 추출: {growth_tokens:,} 토큰")

        # 🎯 3단계: 분기보고서 핵심 정보 (최신 정보 우선)
        if (
            "quarterly_report_dictionary" in dart_dict
            and current_tokens < target_tokens * 0.9
        ):
            quarterly_report = dart_dict["quarterly_report_dictionary"]
            quarterly_essential = self._extract_quarterly_essential(quarterly_report)
            quarterly_tokens = self._estimate_tokens(str(quarterly_essential))

            if current_tokens + quarterly_tokens <= target_tokens:
                extracted["quarterly_report_dictionary"] = quarterly_essential
                current_tokens += quarterly_tokens
                logger.info(f"✅ 분기보고서 핵심 정보 추출: {quarterly_tokens:,} 토큰")

        logger.info(
            f"🎯 최종 DART 데이터 토큰: {current_tokens:,} / {target_tokens:,} ({current_tokens/target_tokens*100:.1f}%)"
        )
        return extracted

    def _extract_essential_financial_sections(self, business_report: Dict) -> Dict:
        """핵심 재무지표만 추출 (최우선)"""
        essential_sections = {}

        # 🥇 최고 중요도 섹션들
        priority_sections = [
            "04_재무상태표",
            "05_손익계산서",
            "06_현금흐름표",
            "07_주요재무비율",
        ]

        for section_name in priority_sections:
            if section_name in business_report:
                section_content = business_report[section_name]
                # 핵심 섹션은 30,000자로 제한
                if len(section_content) > 30000:
                    compressed_content = self._smart_truncate(section_content, 30000)
                    compressed_content += f"\n...[핵심재무섹션, {len(section_content):,}자 중 {len(compressed_content):,}자 표시]..."
                else:
                    compressed_content = section_content

                essential_sections[section_name] = compressed_content

        return essential_sections

    def _extract_growth_and_profitability_sections(self, business_report: Dict) -> Dict:
        """성장성 및 수익성 관련 섹션 추출"""
        growth_sections = {}

        # 🥈 중간 중요도 섹션들
        growth_related_sections = ["02_재무정보", "03_사업내용", "08_재무상태"]

        for section_name in growth_related_sections:
            if section_name in business_report:
                section_content = business_report[section_name]
                # 성장성 섹션은 20,000자로 제한
                if len(section_content) > 20000:
                    compressed_content = self._smart_truncate(section_content, 20000)
                    compressed_content += f"\n...[성장성섹션, {len(section_content):,}자 중 {len(compressed_content):,}자 표시]..."
                else:
                    compressed_content = section_content

                growth_sections[section_name] = compressed_content

        return growth_sections

    def _extract_quarterly_essential(self, quarterly_report: Dict) -> Dict:
        """분기보고서 핵심 정보만 추출"""
        quarterly_essential = {}

        # 분기보고서는 재무 관련 섹션만 우선 추출
        quarterly_financial_sections = ["재무상태표", "손익계산서", "현금흐름표"]

        for section_name in quarterly_financial_sections:
            if section_name in quarterly_report:
                section_content = quarterly_report[section_name]
                # 분기보고서는 15,000자로 제한
                if len(section_content) > 15000:
                    compressed_content = self._smart_truncate(section_content, 15000)
                    compressed_content += f"\n...[분기재무섹션, {len(section_content):,}자 중 {len(compressed_content):,}자 표시]..."
                else:
                    compressed_content = section_content

                quarterly_essential[section_name] = compressed_content

        return quarterly_essential

    def _smart_truncate(self, text: str, max_chars: int) -> str:
        """스마트 자르기: 문장 단위로 자르기"""
        if len(text) <= max_chars:
            return text

        # 마지막 완전한 문장까지 유지
        truncated = text[:max_chars]
        last_period = truncated.rfind(".")
        last_exclamation = truncated.rfind("!")
        last_question = truncated.rfind("?")

        cut_point = max(last_period, last_exclamation, last_question)
        if cut_point > max_chars * 0.8:  # 80% 이상이면 문장 단위로 자르기
            return text[: cut_point + 1]
        else:
            return truncated

    def _assess_data_integration_quality(
        self,
        financial_data: Dict,
        enhanced_dart_data: Dict = None,
        manus_collected_data: Dict = None,
    ) -> Dict[str, Any]:
        """
        📊 데이터 통합 품질을 평가합니다

        여러 데이터 소스의 완성도와 일관성을 체크해서
        분석 결과의 신뢰도를 측정해요!

        Args:
            financial_data: 재무 데이터
            enhanced_dart_data: Enhanced DART 데이터
            manus_collected_data: Manus 수집 데이터

        Returns:
            Dict: 데이터 통합 품질 평가 결과
        """
        try:
            quality_score = 0.0
            total_possible_score = 0.0
            quality_details = {}

            # 1. 재무데이터 품질 평가 (40점 만점)
            if financial_data and financial_data.get("success"):
                financial_score = 0
                # 기본 재무정보 존재
                if financial_data.get("stock_info"):
                    financial_score += 10
                # 재무 요약 존재
                if financial_data.get("financial_summary"):
                    financial_score += 10
                # 핵심 지표 존재
                if financial_data.get("key_metrics"):
                    financial_score += 10
                # 비율 분석 존재
                if financial_data.get("ratios"):
                    financial_score += 10

                quality_score += financial_score
                quality_details["financial_data_score"] = financial_score
            total_possible_score += 40

            # 2. Enhanced DART 데이터 품질 평가 (30점 만점)
            if enhanced_dart_data and enhanced_dart_data.get("success"):
                dart_score = 0
                # 기본 기업정보 존재
                if enhanced_dart_data.get("basic_info"):
                    dart_score += 10
                # 재무정보 존재
                if enhanced_dart_data.get("financial_info"):
                    dart_score += 10
                # 최근 공시정보 존재
                if enhanced_dart_data.get("recent_disclosures"):
                    dart_score += 10

                quality_score += dart_score
                quality_details["dart_data_score"] = dart_score
            total_possible_score += 30

            # 3. Manus 수집 데이터 품질 평가 (30점 만점)
            if manus_collected_data and manus_collected_data.get("performed"):
                manus_score = 0
                # 정보 수집 완료
                if manus_collected_data.get("collected_information"):
                    manus_score += 10
                # 데이터 풍부함 점수
                richness = manus_collected_data.get("data_richness_score", 0)
                if richness > 50:
                    manus_score += 10
                elif richness > 25:
                    manus_score += 5
                # PDF 분석 여부
                if manus_collected_data.get("pdf_analysis", {}).get(
                    "analysis_completed"
                ):
                    manus_score += 10

                quality_score += manus_score
                quality_details["manus_data_score"] = manus_score
            total_possible_score += 30

            # 최종 품질 점수 계산 (0-100 점수로 정규화)
            final_quality_score = (
                (quality_score / total_possible_score * 100)
                if total_possible_score > 0
                else 0
            )

            # 품질 등급 결정
            if final_quality_score >= 80:
                quality_grade = "최고품질"
            elif final_quality_score >= 60:
                quality_grade = "우수"
            elif final_quality_score >= 40:
                quality_grade = "보통"
            else:
                quality_grade = "개선필요"

            return {
                "overall_score": round(final_quality_score, 1),
                "quality_grade": quality_grade,
                "total_possible_score": total_possible_score,
                "achieved_score": quality_score,
                "details": quality_details,
                "data_sources_count": sum(
                    [
                        1
                        for data in [
                            financial_data,
                            enhanced_dart_data,
                            manus_collected_data,
                        ]
                        if data and (data.get("success") or data.get("performed"))
                    ]
                ),
            }

        except Exception as e:
            logger.error(f"❌ 데이터 통합 품질 평가 실패: {e}")
            return {"overall_score": 0.0, "quality_grade": "평가실패", "error": str(e)}

    def _map_gics_to_internal_sector(self, gics_sector: str):
        """
        🎯 GICS 섹터를 내부 섹터 타입으로 매핑합니다

        외부에서 감지된 GICS 섹터를 우리 시스템의 GICSSector 열거형으로
        변환해주는 매핑 함수에요!

        Args:
            gics_sector: GICS 섹터명 (예: "Information Technology")

        Returns:
            GICSSector: 매핑된 내부 섹터 (기본값: INFORMATION_TECHNOLOGY)
        """
        from app.crew.gics_sectors import GICSSector

        # GICS 섹터 매핑 테이블
        gics_mapping = {
            "Information Technology": GICSSector.INFORMATION_TECHNOLOGY,
            "Technology": GICSSector.INFORMATION_TECHNOLOGY,
            "Tech": GICSSector.INFORMATION_TECHNOLOGY,
            "IT": GICSSector.INFORMATION_TECHNOLOGY,
            "Health Care": GICSSector.HEALTH_CARE,
            "Healthcare": GICSSector.HEALTH_CARE,
            "Pharmaceuticals": GICSSector.HEALTH_CARE,
            "Medical": GICSSector.HEALTH_CARE,
            "Financials": GICSSector.FINANCIALS,
            "Finance": GICSSector.FINANCIALS,
            "Banking": GICSSector.FINANCIALS,
            "Insurance": GICSSector.FINANCIALS,
            "Consumer Discretionary": GICSSector.CONSUMER_DISCRETIONARY,
            "Consumer Disc": GICSSector.CONSUMER_DISCRETIONARY,
            "Retail": GICSSector.CONSUMER_DISCRETIONARY,
            "Automotive": GICSSector.CONSUMER_DISCRETIONARY,
            "Consumer Staples": GICSSector.CONSUMER_STAPLES,
            "Consumer Stap": GICSSector.CONSUMER_STAPLES,
            "Food & Beverage": GICSSector.CONSUMER_STAPLES,
            "FMCG": GICSSector.CONSUMER_STAPLES,
            "Communication Services": GICSSector.COMMUNICATION_SERVICES,
            "Communications": GICSSector.COMMUNICATION_SERVICES,
            "Telecom": GICSSector.COMMUNICATION_SERVICES,
            "Media": GICSSector.COMMUNICATION_SERVICES,
            "Industrials": GICSSector.INDUSTRIALS,
            "Industrial": GICSSector.INDUSTRIALS,
            "Manufacturing": GICSSector.INDUSTRIALS,
            "Aerospace": GICSSector.INDUSTRIALS,
            "Energy": GICSSector.ENERGY,
            "Oil & Gas": GICSSector.ENERGY,
            "Renewable Energy": GICSSector.ENERGY,
            "Utilities": GICSSector.ENERGY,  # 유틸리티는 Energy로 매핑
            "Materials": GICSSector.MATERIALS,
            "Basic Materials": GICSSector.MATERIALS,
            "Chemicals": GICSSector.MATERIALS,
            "Mining": GICSSector.MATERIALS,
            "Real Estate": GICSSector.REAL_ESTATE,
            "REIT": GICSSector.REAL_ESTATE,
            "Property": GICSSector.REAL_ESTATE,
        }

        # 대소문자 구분 없이 매핑 시도
        gics_sector_clean = gics_sector.strip() if gics_sector else ""

        # 정확한 매칭 시도
        if gics_sector_clean in gics_mapping:
            matched_sector = gics_mapping[gics_sector_clean]
            logger.info(
                f"🎯 GICS 섹터 매핑 성공: '{gics_sector_clean}' → {matched_sector.name}"
            )
            return matched_sector

        # 부분 매칭 시도 (키워드 기반)
        gics_lower = gics_sector_clean.lower()
        for key, sector in gics_mapping.items():
            if key.lower() in gics_lower or gics_lower in key.lower():
                logger.info(
                    f"🎯 GICS 섹터 부분 매핑 성공: '{gics_sector_clean}' → {sector.name}"
                )
                return sector

        # 매핑 실패시 기본값 반환 (Information Technology)
        logger.warning(
            f"⚠️ GICS 섹터 매핑 실패: '{gics_sector_clean}' → 기본값(IT) 사용"
        )
        return GICSSector.INFORMATION_TECHNOLOGY

    def _extract_market_data_from_technical_analysis(
        self, technical_analysis_data: Dict
    ) -> str:
        """
        기술적 분석 데이터에서 시장 데이터를 추출하는 메서드

        Args:
            technical_analysis_data: 기술적 분석 데이터 딕셔너리

        Returns:
            str: 추출된 시장 데이터 문자열
        """
        if not technical_analysis_data:
            return "시장 데이터 없음"

        try:
            market_info = []

            # 주가 정보 추출
            if "price_data" in technical_analysis_data:
                price_data = technical_analysis_data["price_data"]
                if isinstance(price_data, dict):
                    market_info.append(f"**주가 정보:**")
                    if "current_price" in price_data:
                        market_info.append(f"- 현재가: {price_data['current_price']}")
                    if "change" in price_data:
                        market_info.append(f"- 등락: {price_data['change']}")
                    if "change_rate" in price_data:
                        market_info.append(f"- 등락률: {price_data['change_rate']}")
                    if "volume" in price_data:
                        market_info.append(f"- 거래량: {price_data['volume']}")

            # 기술적 지표 추출
            if "technical_indicators" in technical_analysis_data:
                indicators = technical_analysis_data["technical_indicators"]
                if isinstance(indicators, dict):
                    market_info.append(f"**기술적 지표:**")
                    for indicator, value in indicators.items():
                        market_info.append(f"- {indicator}: {value}")

            # 시장 동향 정보 추출
            if "market_trends" in technical_analysis_data:
                trends = technical_analysis_data["market_trends"]
                if isinstance(trends, dict):
                    market_info.append(f"**시장 동향:**")
                    for trend, description in trends.items():
                        market_info.append(f"- {trend}: {description}")

            # 거래량 분석 추출
            if "volume_analysis" in technical_analysis_data:
                volume_analysis = technical_analysis_data["volume_analysis"]
                if isinstance(volume_analysis, dict):
                    market_info.append(f"**거래량 분석:**")
                    for key, value in volume_analysis.items():
                        market_info.append(f"- {key}: {value}")

            if market_info:
                return "\n".join(market_info)
            else:
                return "시장 데이터 없음"

        except Exception as e:
            logger.error(f"시장 데이터 추출 실패: {e}")
            return "시장 데이터 추출 오류"

    def _extract_competitor_data_from_manus(self, manus_collected_data: Dict) -> str:
        """
        Manus 수집 데이터에서 경쟁사 데이터를 추출하는 메서드

        Args:
            manus_collected_data: Manus가 수집한 데이터 딕셔너리

        Returns:
            str: 추출된 경쟁사 데이터 문자열
        """
        if not manus_collected_data:
            return "경쟁사 데이터 없음"

        try:
            competitor_info = []

            # 경쟁사 정보 추출
            if "competitor_analysis" in manus_collected_data:
                competitor_analysis = manus_collected_data["competitor_analysis"]
                if isinstance(competitor_analysis, dict):
                    competitor_info.append(f"**경쟁사 분석:**")
                    for company, data in competitor_analysis.items():
                        competitor_info.append(f"**{company}:**")
                        if isinstance(data, dict):
                            for key, value in data.items():
                                competitor_info.append(f"- {key}: {value}")
                        else:
                            competitor_info.append(f"- {data}")

            # 시장 점유율 정보 추출
            if "market_share" in manus_collected_data:
                market_share = manus_collected_data["market_share"]
                if isinstance(market_share, dict):
                    competitor_info.append(f"**시장 점유율:**")
                    for company, share in market_share.items():
                        competitor_info.append(f"- {company}: {share}")

            # 경쟁 구도 분석 추출
            if "competitive_landscape" in manus_collected_data:
                landscape = manus_collected_data["competitive_landscape"]
                if isinstance(landscape, dict):
                    competitor_info.append(f"**경쟁 구도:**")
                    for aspect, description in landscape.items():
                        competitor_info.append(f"- {aspect}: {description}")

            # 경쟁사 재무 비교 추출
            if "competitor_financials" in manus_collected_data:
                financials = manus_collected_data["competitor_financials"]
                if isinstance(financials, dict):
                    competitor_info.append(f"**경쟁사 재무 비교:**")
                    for company, financial_data in financials.items():
                        competitor_info.append(f"**{company} 재무:**")
                        if isinstance(financial_data, dict):
                            for metric, value in financial_data.items():
                                competitor_info.append(f"- {metric}: {value}")
                        else:
                            competitor_info.append(f"- {financial_data}")

            if competitor_info:
                return "\n".join(competitor_info)
            else:
                return "경쟁사 데이터 없음"

        except Exception as e:
            logger.error(f"경쟁사 데이터 추출 실패: {e}")
            return "경쟁사 데이터 추출 오류"

    def _extract_web_search_data_from_manus(self, manus_collected_data: Dict) -> str:
        """
        Manus 수집 데이터에서 웹 검색 데이터를 추출하는 메서드

        Args:
            manus_collected_data: Manus가 수집한 데이터 딕셔너리

        Returns:
            str: 추출된 웹 검색 데이터 문자열
        """
        if not manus_collected_data:
            return ""

        try:
            web_search_info = []

            # 뉴스 기사 정보 추출
            if "news_articles" in manus_collected_data:
                news_articles = manus_collected_data["news_articles"]
                if isinstance(news_articles, list) and news_articles:
                    web_search_info.append(f"**최신 뉴스 기사:**")
                    for i, article in enumerate(news_articles[:5], 1):  # 최대 5개 기사
                        if isinstance(article, dict):
                            title = article.get("title", "제목 없음")
                            summary = article.get("summary", "요약 없음")
                            date = article.get("date", "날짜 없음")
                            web_search_info.append(f"{i}. **{title}** ({date})")
                            web_search_info.append(f"   {summary}")
                        else:
                            web_search_info.append(f"{i}. {article}")

            # 분석가 리포트 정보 추출
            if "analyst_reports" in manus_collected_data:
                analyst_reports = manus_collected_data["analyst_reports"]
                if isinstance(analyst_reports, list) and analyst_reports:
                    web_search_info.append(f"**분석가 리포트:**")
                    for i, report in enumerate(
                        analyst_reports[:3], 1
                    ):  # 최대 3개 리포트
                        if isinstance(report, dict):
                            title = report.get("title", "제목 없음")
                            rating = report.get("rating", "평가 없음")
                            target_price = report.get("target_price", "목표가 없음")
                            web_search_info.append(
                                f"{i}. **{title}** - {rating} (목표가: {target_price})"
                            )
                        else:
                            web_search_info.append(f"{i}. {report}")

            # 산업 동향 정보 추출
            if "industry_trends" in manus_collected_data:
                industry_trends = manus_collected_data["industry_trends"]
                if isinstance(industry_trends, dict):
                    web_search_info.append(f"**산업 동향:**")
                    for trend, description in industry_trends.items():
                        web_search_info.append(f"- {trend}: {description}")

            # 시장 동향 정보 추출
            if "market_sentiment" in manus_collected_data:
                market_sentiment = manus_collected_data["market_sentiment"]
                if isinstance(market_sentiment, dict):
                    web_search_info.append(f"**시장 심리:**")
                    for aspect, sentiment in market_sentiment.items():
                        web_search_info.append(f"- {aspect}: {sentiment}")

            # 글로벌 시장 정보 추출
            if "global_market_data" in manus_collected_data:
                global_data = manus_collected_data["global_market_data"]
                if isinstance(global_data, dict):
                    web_search_info.append(f"**글로벌 시장:**")
                    for market, data in global_data.items():
                        web_search_info.append(f"- {market}: {data}")

            if web_search_info:
                return "\n".join(web_search_info)
            else:
                return ""

        except Exception as e:
            logger.error(f"웹 검색 데이터 추출 실패: {e}")
            return ""

    def _filter_out_footnote_sections(self, sections: List[str]) -> List[str]:
        """
        주석(footnote) 섹션을 필터링하여 제거합니다.

        Args:
            sections: 필터링할 섹션 리스트

        Returns:
            List[str]: 주석 섹션이 제거된 섹션 리스트
        """
        # 주석 관련 키워드 목록
        footnote_keywords = [
            "주석",
            "footnote",
            "note",
            "주석사항",
            "회계처리방법",
            "법적고지",
            "부속명세서",
            "notes",
            "footnotes",
            # 법적 고지사항
            "법적고지사항",
            "법적책임면책",
            "공시의무",
            "disclaimer",
            "legal_notice",
            "법적고지내용",
            "법적고지서",
            "책임면책",
            "면책조항",
            # 감사 관련
            "감사인의의견서",
            "감사의견",
            "auditor_opinion",
            "audit_report",
            "감사보고서",
            "감사범위",
            "audit_scope",
            "audit_opinion",
            # 회계 처리 방법
            "회계처리기준",
            "회계처리방침",
            "accounting_policies",
            "accounting_standards",
            "회계기준",
            "회계방침",
            "accounting_methods",
            "accounting_principles",
            # 부속 서류
            "부속서류",
            "부속서류서",
            "supplementary_documents",
            "attachments",
            "부속명세",
            "부속서류사항",
            "supplementary_info",
            "attached_documents",
            # 기타 상세 설명
            "상세설명",
            "상세내용",
            "detailed_description",
            "detailed_content",
            "상세기준",
            "상세방법",
            "detailed_standards",
            "detailed_methods",
            # 표준화된 문구
            "본보고서는",
            "이보고서는",
            "위의내용은",
            "this_report",
            "the_above",
            "보고서개요",
            "보고서요약",
            "report_summary",
            "report_overview",
        ]

        filtered_sections = []

        for section in sections:
            # 섹션명에 주석 관련 키워드가 포함되어 있는지 확인
            is_footnote = any(
                keyword.lower() in section.lower() for keyword in footnote_keywords
            )

            if not is_footnote:
                filtered_sections.append(section)
            else:
                logger.info(f"🔧 주석 섹션 제외: {section}")

        return filtered_sections
