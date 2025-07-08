# -*- coding: utf-8 -*-
"""
🚀 One-Hot Sector Activation 핵심 시스템

90% 비용 절감을 실현하는 혁신적인 섹터별 전문가 활성화 시스템!
기존 55개 에이전트 대신 5개 에이전트만 선택적으로 활성화해요.
"""

import hashlib
import json
import time
from dataclasses import dataclass
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
        logger.info("💰 One-Hot Activation으로 90% 비용 절감 준비 완료!")

    async def analyze_with_optimal_team(
        self,
        user_prompt: str,
        stock_name: str,
        stock_code: str,
        financial_data: Dict[str, Any],
        analysis_depth: AnalysisDepth = AnalysisDepth.STANDARD,
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

            # 🚀 5. 종합 데이터로 전문가별 분석 수행 (최적화된 데이터 사용!)
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
                    expert, financial_data, enhanced_dart_data, manus_collected_data
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
- **경쟁사 3개 기업** ROE, PER, EBITDA 마진, 매출성장률 비교 테이블 작성
- **상대적 순위** 제시: "업계 3위/7개사" 형태로 명시
- **격차 분석**: "경쟁사 대비 ROE 2.3%p 낮음" 등 구체적 수치

## 📊 **STEP 2: 3년 시계열 트렌드 분석** (필수)
- **ROE 추이**: "2021년 15.2% → 2022년 12.8% → 2023년 9.1%" 정확한 연도별 수치
- **매출성장률 추이**: 3년간 변화와 **구체적 원인** (반도체 사이클, 환율 등)
- **트렌드 방향성**: 개선/악화 여부를 수치로 입증

## 📊 **STEP 3: WACC vs ROIC 정량 분석** (필수)
- **WACC 직접 계산**: 자기자본비용 + 타인자본비용 (가중평균)
- **ROIC 계산**: NOPAT ÷ Invested Capital
- **Value Creation**: ROIC - WACC = +/- X.X% (가치창출/파괴 명확히 판단)

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

각 분석 단계에서 **단계별 사고 과정**을 거쳐 논리적 결론을 도출하세요:

**사고 과정 구조**:
1. **데이터 수집 및 정리**: 수집된 재무데이터, 시장정보, 경쟁사 데이터 정리
2. **패턴 인식**: 과거 트렌드와 현재 상황 비교 분석
3. **인과관계 분석**: 수치 변화의 근본 원인과 영향 요인 파악
4. **시나리오 구축**: 다양한 가정 하에서의 미래 전망 시뮬레이션
5. **리스크 평가**: 각 시나리오별 발생 확률과 영향도 계산
6. **종합 판단**: 모든 분석을 종합한 투자 의견 도출

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
- Bull/Base/Bear 시나리오별 재무지표 변화 예측
- 불확실성을 고려한 확률적 전망 제시



## 🎯 **Executive Summary** (최종 결론):

### 📈 **투자 스코어카드** (5점 만점):
- 수익성: X.X/5.0점 (ROE, ROIC 기준)
- 성장성: X.X/5.0점 (매출/이익 성장률 기준)
- 안전성: X.X/5.0점 (부채비율, FCF 기준)
- 밸류에이션: X.X/5.0점 (PER, PBR 기준)
- **종합점수**: X.X/5.0점

### 💡 **투자 실행 전략**:
- **BUY/HOLD/SELL**: 명확한 투자 의견 + 목표주가
- **매수 시점**: "지금 즉시" / "X% 하락 시" / "실적 개선 확인 후"
- **투자 기간**: 단기(3개월) / 중기(1년) / 장기(3년)

### ⚠️ **핵심 리스크 2가지**:
1. **[구체적 리스크명]**: 발생 확률 X%, 예상 주가 영향 -X%
2. **[구체적 리스크명]**: 발생 확률 X%, 예상 주가 영향 -X%

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

                # 🔧 단순화된 LLM 호출 (웹검색은 이미 완료)
                try:
                    # 웹검색 없이 순수 분석만 수행
                    analysis_result = await llm_instance.ask(
                        prompt=prompt, temperature=0.3, max_tokens=4000
                    )

                    # 결과 처리
                    if not analysis_result:
                        raise ValueError("LLM 분석 결과가 None 또는 빈 값")

                    # 텍스트 추출
                    analysis_text = str(analysis_result)

                    # 최소 길이 검증
                    if len(analysis_text.strip()) < 200:
                        raise ValueError(
                            f"분석 결과가 너무 짧음: {len(analysis_text)}자"
                        )

                    logger.info(f"✅ {expert.name} 분석 완료: {len(analysis_text):,}자")

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

                    return {
                        "expert_name": expert.name,
                        "expert_role": expert.role,
                        "expertise": expert.expertise,
                        "analysis_result": analysis_text,
                        "analysis_timestamp": datetime.now().isoformat(),
                        "attempt_number": attempt + 1,
                        "success": True,
                        "web_search_performed": web_search_performed,
                        "web_search_count": web_search_count,
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

        expert_results = []
        analysis_start_time = time.time()

        for expert in experts:
            try:
                logger.info(f"👨‍💼 전문가 분석 시작: {expert.name}")

                # 🚀 종합 분석용 프롬프트 구성
                comprehensive_prompt = await self._create_expert_specific_context(
                    expert,
                    prompt,
                    stock_name,
                    stock_code,
                    financial_data,
                    enhanced_dart_data,
                    manus_collected_data,
                    (
                        manus_collected_data.get("pdf_analysis", {}).get(
                            "pdf_dictionary_interface"
                        )
                        if manus_collected_data
                        else None
                    ),  # 🚀 PDF 인터페이스 전달
                    technical_analysis_data,  # 🎯 기술적 분석 데이터 추가!
                    dart_reports_dictionary,  # 🚀 DART 보고서 딕셔너리 추가!
                )

                # 🚀 향상된 분석 시스템 (CoT + 5Why + 7Why) 사용
                # (삭제)
                # 기존 분석 시스템만 사용
                    logger.info(f"📝 {expert.name} 기존 LLM 방식 사용")
                    analysis_result = await self._call_llm_for_analysis(
                        comprehensive_prompt
                    )

                expert_results.append(
                    {
                        "expert_name": expert.name,
                        "expertise_area": expert.expertise,
                        "analysis_result": analysis_result,
                        "data_sources_used": self._identify_used_data_sources(
                            financial_data,
                            enhanced_dart_data,
                            manus_collected_data,
                            technical_analysis_data,
                            dart_reports_dictionary,
                        ),
                        "analysis_timestamp": time.time(),
                    }
                )

                logger.info(f"✅ {expert.name} 분석 완료")

            except Exception as e:
                logger.error(f"❌ {expert.name} 분석 실패: {e}")
                expert_results.append(
                    {
                        "expert_name": expert.name,
                        "expertise_area": expert.expertise,
                        "analysis_result": f"분석 실패: {str(e)}",
                        "error": True,
                    }
                )

        # 🚀 전문가 분석 결과 종합
        synthesis_result = await self._synthesize_expert_insights(
            expert_results, prompt
        )

        total_analysis_time = time.time() - analysis_start_time

        return {
            "individual_expert_analyses": expert_results,
            "expert_count": len(experts),
            "successful_analyses": len(
                [r for r in expert_results if not r.get("error")]
            ),
            "synthesis_result": synthesis_result,
            "total_analysis_time": f"{total_analysis_time:.2f}초",
            "data_integration_type": "comprehensive_multi_source",
        }

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

🎯 위 전문가들의 분석을 종합하여 다음과 같이 정리해주세요 (Chat GPT 피드백 완전 반영):

## 🚀 Chat GPT 피드백 반영 - 시니어 애널리스트 수준 통합 분석

### 1. **전문가 간 분석 결과 일관성 검토** (Chat GPT 피드백 핵심)
- **일치하는 의견**: 여러 전문가가 동일하게 제시한 강점/약점 (신뢰도 높음)
- **상반된 의견**: 전문가 간 모순되는 결론과 그 원인 분석
  * 예: 기술적 분석(단기 하락) vs 밸류에이션(매수 권장)의 차이점
- **의견 불일치 해결**: 상반된 의견에 대한 종합적 판단과 우선순위

### 2. **시간적 프레임별 투자 전략** (Chat GPT 피드백 핵심)
- **단기 전략 (1-3개월)**: 기술적 분석 + 이벤트 기반 요인
- **중기 전략 (3-12개월)**: 펀더멘털 + 산업 트렌드 + 밸류에이션
- **장기 전략 (1-3년)**: 구조적 경쟁력 + ESG + 기술 혁신 주기

### 3. **시나리오별 대응 전략** (Chat GPT 피드백 핵심)
- **Bull Case (30% 확률)**: 최적 시나리오에서의 목표가와 대응 전략
- **Base Case (40% 확률)**: 기본 시나리오에서의 투자 접근법
- **Bear Case (30% 확률)**: 악재 시나리오에서의 리스크 관리 방안

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

            return {
                "synthesis_success": True,
                "expert_count": len(expert_results),
                "successful_count": len(successful_analyses),
                "failed_count": len(expert_results) - len(successful_analyses),
                "synthesis_content": synthesis_result,
                "synthesis_timestamp": time.time(),
                "data_sources_integrated": self._count_unique_data_sources(
                    expert_results
                ),
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

        # 기본 정보 (모든 전문가 공통)
        context_parts.append(f"분석 대상: {stock_name} ({stock_code})")
        context_parts.append(f"사용자 질문: {user_prompt}")
        context_parts.append(f"전문가 역할: {expert.name}")
        context_parts.append(f"분석 포커스: {expert.analysis_focus}")

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

                # 해당 전문가에게 적합한 섹션 가져오기
                relevant_sections = section_categories.get(expert_key, [])
                if expert_key != "general":
                    relevant_sections.extend(section_categories.get("general", [])[:2])

                # 실제 섹션 내용 추가
                if relevant_sections and pdf_dictionary:
                    context_parts.append(
                        f"📄 **{expert.name} 관련 PDF 섹션 (딕셔너리 처리)**:"
                    )
                    section_count = 0
                    total_content_length = 0

                    for section_title in relevant_sections[:5]:  # 최대 5개 섹션
                        if section_title in pdf_dictionary:
                            content = pdf_dictionary[section_title]

                            # 🚀 200만자 제한으로 확장
                            if len(content) > 2000000:
                                content = (
                                    content[:2000000]
                                    + "\n...[200만자 제한으로 내용 일부 생략]..."
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
                # 주석 전문가 특별 처리
                if "주석" in expert.name or "Footnote" in expert.role:
                    footnote_sections = pdf_interface.get_sections_by_expert_type(
                        # "footnote_specialist"  # 🚫 비활성화 (개발 시간 절약)
                    )
                    if footnote_sections:
                        context_parts.append(
                            "📄 **재무제표 주석 섹션 (PDF 완전 분석)**:"
                        )
                        section_count = 0
                        total_content_length = 0

                        for section_title, content in footnote_sections.items():
                            # 🚀 주석 전문가는 섹션 제한 없음! 모든 주석 섹션 완전 분석
                            if (
                                len(content) > 2000000
                            ):  # 🚀 개별 섹션 200만자 제한으로 확대
                                content = (
                                    content[:2000000]
                                    + "\n...[200만자 제한으로 내용 일부 생략]..."
                                )

                            context_parts.append(f"### {section_title}")
                            context_parts.append(content)
                            context_parts.append("")
                            section_count += 1
                            total_content_length += len(content)

                        logger.info(
                            f"📝 주석 전문가: {section_count}개 섹션, 총 {total_content_length:,}자 (제한 없음)"
                        )
                    else:
                        logger.info("📝 PDF에서 주석 섹션을 찾지 못했습니다")

                # 다른 전문가들 처리
                else:
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
                            # 🚀 모든 전문가 섹션 제한 제거! 필요한 모든 섹션 활용
                            if (
                                len(content) > 2000000
                            ):  # 🚀 개별 섹션 200만자 제한으로 확대
                                content = (
                                    content[:2000000]
                                    + "\n...[200만자 제한으로 내용 일부 생략]..."
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
            logger.info("📄 PDF 딕셔너리 인터페이스가 제공되지 않았습니다")

        # 🚀 분리된 DART 보고서 딕셔너리 처리 (NEW!)
        if dart_reports_dictionary and dart_reports_dictionary.get("success"):
            logger.info("📋 분리된 DART 보고서 딕셔너리 처리 시작...")

            # 분리된 딕셔너리들 가져오기
            business_report_dict = dart_reports_dictionary.get(
                "business_report_dictionary", {}
            )
            quarterly_report_dict = dart_reports_dictionary.get(
                "quarterly_report_dictionary", {}
            )

            if business_report_dict or quarterly_report_dict:
                # 전문가별 키워드 매핑
                expert_keywords = {
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
                        # 회사개요/사업내용 관련 (하이브리드 방식 추가)
                        "사업",
                        "개요",
                        "기업",
                        "회사",
                        "업종",
                        "산업",
                        "시장",
                        "경쟁",
                    ],
                    "technical_analyst": [
                        "기술적",
                        "차트",
                        "지표",
                        "추세",
                        "거래량",
                        "변동성",
                        "이동평균",
                        "RSI",
                        "MACD",
                        "볼린저밴드",
                        "스토캐스틱",
                    ],
                }

                # 전문가 타입 결정 (더 정확한 매칭)
                expert_type = "technical_analyst"  # 기본값

                # 통합 재무분석가 매칭 (펀더멘털 + 밸류에이션 통합)
                if any(
                    keyword in expert.name.lower() or keyword in expert.role.lower()
                    for keyword in [
                        "통합",
                        "재무",
                        "펀더멘털",
                        "fundamental",
                        "integrated",
                    ]
                ):
                    expert_type = "integrated_financial_analyst"
                elif any(
                    keyword in expert.name.lower() or keyword in expert.role.lower()
                    for keyword in ["technical", "기술적"]
                ):
                    expert_type = "technical_analyst"

                keywords = expert_keywords.get(
                    expert_type, expert_keywords["integrated_financial_analyst"]
                )

                # 🎯 사업보고서에서 관련 섹션 찾기
                business_sections = []
                if business_report_dict:
                    logger.info(f"📄 사업보고서에서 {expert.name} 관련 섹션 검색...")
                    for section_title, content in business_report_dict.items():
                        score = 0
                        # 제목에서 키워드 매칭 (가중치 3)
                        for keyword in keywords:
                            if keyword in section_title:
                                score += 3
                        # 내용에서 키워드 매칭 (가중치 1, 처음 1000자만 검사)
                        content_sample = content[:1000]
                        for keyword in keywords:
                            if keyword in content_sample:
                                score += 1

                        # 🚀 하이브리드 방식: 회사개요/사업내용 섹션에 추가 가중치 부여
                        if "회사개요" in section_title or "사업내용" in section_title:
                            score += 5  # 추가 가중치 5점 부여
                            logger.info(
                                f"📋 {expert.name}: 회사개요/사업내용 섹션 추가 가중치 적용 - {section_title}"
                            )

                        if score >= 2:
                            business_sections.append((section_title, content, score))

                    business_sections.sort(key=lambda x: x[2], reverse=True)
                    # 섹션 제한 없음 - 관련도 높은 모든 섹션 사용

                # 🎯 분기보고서에서 관련 섹션 찾기
                quarterly_sections = []
                if quarterly_report_dict:
                    logger.info(f"📈 분기보고서에서 {expert.name} 관련 섹션 검색...")
                    for section_title, content in quarterly_report_dict.items():
                        score = 0
                        # 제목에서 키워드 매칭 (가중치 3)
                        for keyword in keywords:
                            if keyword in section_title:
                                score += 3
                        # 내용에서 키워드 매칭 (가중치 1, 처음 1000자만 검사)
                        content_sample = content[:1000]
                        for keyword in keywords:
                            if keyword in content_sample:
                                score += 1

                        # 🚀 하이브리드 방식: 회사개요/사업내용 섹션에 추가 가중치 부여
                        if "회사개요" in section_title or "사업내용" in section_title:
                            score += 5  # 추가 가중치 5점 부여
                            logger.info(
                                f"📋 {expert.name}: 회사개요/사업내용 섹션 추가 가중치 적용 - {section_title}"
                            )

                        if score >= 2:
                            quarterly_sections.append((section_title, content, score))

                    quarterly_sections.sort(key=lambda x: x[2], reverse=True)
                    # 섹션 제한 없음 - 관련도 높은 모든 섹션 사용

                # 🚀 분리된 섹션들을 컨텍스트에 추가
                total_dart_content_length = 0

                if business_sections:
                    context_parts.append(
                        f"📄 **{expert.name} 관련 사업보고서 섹션 (연간 종합정보)**:"
                    )
                    for section_title, content, score in business_sections:
                        if (
                            len(content) > 2000000
                        ):  # 🚀 사업보고서 200만자 제한으로 확장
                            content = (
                                content[:2000000]
                                + "\n...[사업보고서 내용 일부 생략 (200만자 제한)]..."
                            )
                        context_parts.append(f"### {section_title} (관련도: {score}점)")
                        context_parts.append(content)
                        context_parts.append("")
                        total_dart_content_length += len(content)

                    logger.info(
                        f"📄 {expert.name}: 사업보고서 {len(business_sections)}개 섹션 선택"
                    )

                if quarterly_sections:
                    context_parts.append(
                        f"📈 **{expert.name} 관련 분기보고서 섹션 (최신 분기정보)**:"
                    )
                    for section_title, content, score in quarterly_sections:
                        if (
                            len(content) > 2000000
                        ):  # 🚀 분기보고서 200만자 제한으로 확장
                            content = (
                                content[:2000000]
                                + "\n...[분기보고서 내용 일부 생략 (200만자 제한)]..."
                            )
                        context_parts.append(f"### {section_title} (관련도: {score}점)")
                        context_parts.append(content)
                        context_parts.append("")
                        total_dart_content_length += len(content)

                    logger.info(
                        f"📈 {expert.name}: 분기보고서 {len(quarterly_sections)}개 섹션 선택"
                    )

                if business_sections or quarterly_sections:
                    logger.info(
                        f"📋 {expert.name}: 총 {len(business_sections) + len(quarterly_sections)}개 DART 섹션, {total_dart_content_length:,}자"
                    )
                    context_parts.append(
                        "🔍 **분석 지침**: 사업보고서는 연간 종합정보이고, 분기보고서는 최신 분기 실적입니다. 시기적 차이를 고려하여 분석해주세요."
                    )
                    context_parts.append("")
                else:
                    logger.info(
                        f"📋 {expert.name}: 관련 DART 보고서 섹션을 찾지 못했습니다"
                    )
            else:
                logger.warning("⚠️ DART 보고서 딕셔너리가 비어있습니다")
        else:
            logger.info("📋 DART 보고서 딕셔너리가 제공되지 않았습니다")

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
                    f"**📊 사용 가능한 데이터 소스**: {', '.join(available_sources)}"
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
            context_parts.append(
                    "- 재무비율을 통한 멀티플 분석 (PER, PBR, EV/EBITDA)"
                )
                context_parts.append("- 민감도 분석 (WACC, 성장률 변동 시 영향도)")
                context_parts.append("- DART 데이터를 활용한 현금흐름 분석")
            context_parts.append("- 웹검색 데이터를 활용한 시장 동향 및 멀티플 비교")
            context_parts.append("- DART 보고서 딕셔너리에서 상세 현금흐름 정보 활용")

            context_parts.append("")

            # 실제 데이터 기반 밸류에이션 분석 방법론
            context_parts.append("**💰 실제 데이터 기반 밸류에이션 분석 방법론**:")
            if financial_data and financial_data.get("success"):
                context_parts.append("- 재무데이터를 활용한 DCF 분석 (현금흐름 할인)")
            context_parts.append(
                    "- 재무비율을 통한 멀티플 분석 (PER, PBR, EV/EBITDA)"
                )
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
                    f"**📊 사용 가능한 데이터 소스**: {', '.join(available_sources)}"
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
        data_source_guidelines = """

📊 **데이터 출처 명시 규칙** (모든 수치에 필수 적용):
모든 수치 뒤에 반드시 출처를 표기해주세요:
- **[재무데이터]**: 제공된 재무제표에서 직접 계산한 수치
- **[사업보고서]**: DART 사업보고서에서 추출한 정보
- **[웹검색]**: 웹검색을 통해 수집한 외부 데이터
- **[추정]**: 애널리스트 자체 추정 또는 가정 수치
- **[업계평균]**: 웹검색으로 확인한 동종업계 평균값
- **[재무데이터 기반 계산]**: 재무제표 데이터를 사용한 직접 계산 (WACC, ROIC 등)

**예시**: "ROE 12.5% **[재무데이터]**, 업계 평균 10.2% **[웹검색]**"

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

        safe_context_parts.append(data_source_guidelines)

        full_context = "\n".join(safe_context_parts)

        # 토큰 수 계산 및 로깅
        estimated_tokens = self._estimate_tokens(full_context)
        logger.info(
            f"🎯 {expert.name} 통합 컨텍스트: {estimated_tokens:,} 토큰 (PDF 딕셔너리 완전 활용 + 출처 명시 규칙)"
        )

        return full_context

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
            return "기술적 분석 데이터가 제공되지 않았습니다."

        try:
            formatted_lines = []
            formatted_lines.append("📊 **실제 계산된 기술적 지표 (최신 값)**:")
            formatted_lines.append("")

            # 현재 주가 정보
            current_snapshot = technical_analysis_data.get("current_snapshot", {})
            if current_snapshot:
                current_price = current_snapshot.get("price")
                current_volume = current_snapshot.get("volume")
                current_date = current_snapshot.get("date", "알 수 없음")

                if current_price:
                    formatted_lines.append(
                        f"**현재 주가**: {current_price:,.0f}원 ({current_date})"
                    )
                if current_volume:
                    formatted_lines.append(f"**현재 거래량**: {current_volume:,}주")
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
                formatted_lines.append("**📈 이동평균선**:")
                try:
                    for period, value in ma_data.items():
                        if value is not None:
                            formatted_lines.append(f"  • {period}: {value:,.0f}원")
                        else:
                            formatted_lines.append(f"  • {period}: 계산 불가")
                except Exception as ma_error:
                    logger.error(f"❌ 이동평균선 처리 오류: {ma_error}")
                    formatted_lines.append("  • 이동평균선 데이터 처리 중 오류")
                formatted_lines.append("")

            # 2. RSI 지표 처리
            rsi_data = indicators.get("rsi", {})
            if isinstance(rsi_data, dict) and rsi_data:
                formatted_lines.append("**📊 RSI (상대강도지수)**:")
                try:
                    current_rsi = rsi_data.get("current_value")
                    interpretation = rsi_data.get("interpretation", "알 수 없음")
                    signal = rsi_data.get("signal", "알 수 없음")

                    if current_rsi is not None:
                        formatted_lines.append(f"  • 현재 RSI: {current_rsi:.2f}")
                        formatted_lines.append(f"  • 해석: {interpretation}")
                        formatted_lines.append(f"  • 신호: {signal}")
                    else:
                        formatted_lines.append("  • RSI 계산 불가")
                except Exception as rsi_error:
                    logger.error(f"❌ RSI 처리 오류: {rsi_error}")
                    formatted_lines.append("  • RSI 데이터 처리 중 오류")
                formatted_lines.append("")

            # 3. MACD 지표 처리
            macd_data = indicators.get("macd", {})
            if isinstance(macd_data, dict) and macd_data:
                formatted_lines.append("**📈 MACD**:")
                try:
                    # MACD_line과 macd_line 모두 지원 (호환성)
                    macd_line = macd_data.get("MACD_line") or macd_data.get("macd_line")
                    signal_line = macd_data.get("signal_line")
                    histogram = macd_data.get("histogram")
                    signal_interpretation = macd_data.get(
                        "signal_interpretation", "알 수 없음"
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
                    formatted_lines.append("  • MACD 데이터 처리 중 오류")
                formatted_lines.append("")

            # 4. 볼린저 밴드 처리
            bb_data = indicators.get("bollinger_bands", {})
            if isinstance(bb_data, dict) and bb_data:
                formatted_lines.append("**📊 볼린저 밴드**:")
                try:
                    upper_band = bb_data.get("upper_band")
                    middle_band = bb_data.get("middle_band")
                    lower_band = bb_data.get("lower_band")
                    position_analysis = bb_data.get("position_analysis", "알 수 없음")
                    bb_signal = bb_data.get("signal", "알 수 없음")

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
                    formatted_lines.append("  • 볼린저 밴드 데이터 처리 중 오류")
                formatted_lines.append("")

            # 5. 스토캐스틱 처리
            stoch_data = indicators.get("stochastic", {})
            if isinstance(stoch_data, dict) and stoch_data:
                formatted_lines.append("**📈 스토캐스틱**:")
                try:
                    k_percent = stoch_data.get("K_percent") or stoch_data.get(
                        "k_percent"
                    )
                    d_percent = stoch_data.get("D_percent") or stoch_data.get(
                        "d_percent"
                    )
                    stoch_interpretation = stoch_data.get(
                        "interpretation", "알 수 없음"
                    )
                    stoch_signal = stoch_data.get("signal", "알 수 없음")

                    if k_percent is not None:
                        formatted_lines.append(f"  • %K: {k_percent:.2f}")
                    if d_percent is not None:
                        formatted_lines.append(f"  • %D: {d_percent:.2f}")
                    formatted_lines.append(f"  • 해석: {stoch_interpretation}")
                    formatted_lines.append(f"  • 신호: {stoch_signal}")
                except Exception as stoch_error:
                    logger.error(f"❌ 스토캐스틱 처리 오류: {stoch_error}")
                    formatted_lines.append("  • 스토캐스틱 데이터 처리 중 오류")
                formatted_lines.append("")

            # 6. Williams %R 처리
            wr_data = indicators.get("williams_r", {})
            if isinstance(wr_data, dict) and wr_data:
                formatted_lines.append("**📊 Williams %R**:")
                try:
                    wr_value = wr_data.get("current_value")
                    wr_interpretation = wr_data.get("interpretation", "알 수 없음")
                    wr_signal = wr_data.get("signal", "알 수 없음")

                    if wr_value is not None:
                        formatted_lines.append(f"  • 현재 값: {wr_value:.2f}")
                        formatted_lines.append(f"  • 해석: {wr_interpretation}")
                        formatted_lines.append(f"  • 신호: {wr_signal}")
                    else:
                        formatted_lines.append("  • Williams %R 계산 불가")
                except Exception as wr_error:
                    logger.error(f"❌ Williams %R 처리 오류: {wr_error}")
                    formatted_lines.append("  • Williams %R 데이터 처리 중 오류")
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
                    formatted_lines.append("  • 거래량 지표 처리 중 오류")
                formatted_lines.append("")

            # 8. OBV 지표 처리
            obv_data = indicators.get("obv", {})
            if isinstance(obv_data, dict) and obv_data:
                formatted_lines.append("**📈 OBV (On Balance Volume)**:")
                try:
                    obv_value = obv_data.get("current_value")
                    obv_trend = obv_data.get("trend", "알 수 없음")

                    if obv_value is not None:
                        formatted_lines.append(f"  • 현재 OBV: {obv_value:,.0f}")
                        formatted_lines.append(f"  • 추세: {obv_trend}")
                    else:
                        formatted_lines.append("  • OBV 계산 불가")
                except Exception as obv_error:
                    logger.error(f"❌ OBV 처리 오류: {obv_error}")
                    formatted_lines.append("  • OBV 데이터 처리 중 오류")
                formatted_lines.append("")

            # 9. 매매 신호 종합
            trading_signals = technical_analysis_data.get("trading_signals", {})
            if isinstance(trading_signals, dict) and trading_signals:
                formatted_lines.append("**🎯 종합 매매 신호**:")
                try:
                    overall_signal = trading_signals.get("overall_signal", "알 수 없음")
                    signal_strength = trading_signals.get(
                        "signal_strength", "알 수 없음"
                    )
                    recommendation = trading_signals.get("recommendation", "알 수 없음")

                    formatted_lines.append(f"  • 종합 신호: {overall_signal}")
                    formatted_lines.append(f"  • 신호 강도: {signal_strength}")
                    formatted_lines.append(f"  • 추천: {recommendation}")
                except Exception as signal_error:
                    logger.error(f"❌ 매매 신호 처리 오류: {signal_error}")
                    formatted_lines.append("  • 매매 신호 처리 중 오류")
                formatted_lines.append("")

            # 데이터 수집 정보
            total_days = technical_analysis_data.get("total_days", 0)
            last_update = technical_analysis_data.get("last_update", "알 수 없음")
            if total_days > 0:
                formatted_lines.append(
                    f"**📊 데이터 정보**: {total_days}일치 데이터 (최종 업데이트: {last_update})"
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

        # 더 정확한 토큰 추정 (GPT-4o 기준)
        # 한국어: 약 2.5자당 1토큰, 영어: 약 4자당 1토큰
        # 혼재된 텍스트를 고려하여 3자당 1토큰으로 계산
        estimated_tokens = len(text) // 3

        # 실제 토큰 수는 보통 추정치보다 10-20% 많을 수 있음
        # 안전 마진을 위해 15% 추가
        return max(1, int(estimated_tokens * 1.15))

    def _optimize_data_for_token_limit(
        self,
        financial_data: Dict,
        enhanced_dart_data: Dict = None,
        manus_collected_data: Dict = None,
        dart_reports_dictionary: Dict = None,  # 🚀 DART 딕셔너리 추가!
        target_token_limit: int = 120000,  # 2명 체제에 맞게 증가 (기존 100K → 120K)
    ) -> Dict[str, Any]:
        """
        🎯 토큰 제한에 맞춰 데이터를 최적화합니다.

        Args:
            financial_data: 재무 데이터
            enhanced_dart_data: Enhanced DART 데이터
            manus_collected_data: Manus 수집 데이터
            dart_reports_dictionary: DART 보고서 딕셔너리
            target_token_limit: 목표 토큰 제한

        Returns:
            Dict: 최적화된 데이터
        """
        logger.info(f"🔢 토큰 최적화 시작 - 목표: {target_token_limit:,} 토큰")

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
            # 현재 토큰 수 추정
            current_tokens = 0

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

            # 토큰 제한을 초과하는 경우 최적화 적용
            if current_tokens > target_token_limit:
                logger.info(
                    f"⚠️ 토큰 제한 초과: {current_tokens:,} > {target_token_limit:,}"
                )

                # 각 데이터 소스별 우선순위에 따라 압축
                compression_ratio = target_token_limit / current_tokens

                # 재무데이터 압축 (가장 중요하므로 80% 유지)
                if financial_data:
                    optimized_data["financial_data"] = self._compress_financial_data(
                        financial_data, compression_ratio * 0.8
                    )

                # Enhanced DART 데이터 압축 (70% 유지)
                if enhanced_dart_data:
                    optimized_data["enhanced_dart_data"] = self._compress_dart_data(
                        enhanced_dart_data, compression_ratio * 0.7
                    )

                # Manus 데이터 압축 (60% 유지)
                if manus_collected_data:
                    optimized_data["manus_collected_data"] = self._compress_manus_data(
                        manus_collected_data, compression_ratio * 0.6
                    )

                # 🚀 DART 딕셔너리 압축 (50% 유지 - 가장 큰 데이터)
                if dart_reports_dictionary:
                    optimized_data["dart_reports_dictionary"] = (
                        self._compress_dart_dictionary(
                            dart_reports_dictionary, compression_ratio * 0.5
                        )
                    )

                optimized_data["optimization_applied"] = True

                # 최적화 후 토큰 수 재계산
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

                optimized_data["optimized_token_estimate"] = optimized_tokens

                logger.info(
                    f"✅ 토큰 최적화 완료: {current_tokens:,} → {optimized_tokens:,}"
                )

            else:
                logger.info(f"✅ 토큰 제한 내: {current_tokens:,} 토큰")
                optimized_data["optimized_token_estimate"] = current_tokens

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

        compressed = {}

        # 사업보고서와 분기보고서를 각각 압축
        if "business_report_dictionary" in dart_dict:
            business_report = dart_dict["business_report_dictionary"]
            compressed_business = {}

            # 🎯 스마트 섹션 선택: 중요도 기반
            section_importance = {
                "01_회사개요_및_사업내용": 10,  # 최고 중요도
                "02_재무정보": 9,
                "03_사업내용": 8,
                "04_재무상태표": 9,
                "05_손익계산서": 9,
                "06_현금흐름표": 8,
                "07_주요재무비율": 8,
                "08_재무상태": 7,
                "09_경영진": 6,
                "10_지배구조": 6,
                "11_리스크": 7,
                "12_투자": 6,
                "13_기타": 4,
                "14_부속명세서": 5,
            }

            # 중요도 순으로 정렬
            sorted_sections = sorted(
                business_report.items(),
                key=lambda x: section_importance.get(x[0], 0),
                reverse=True,
            )

            # 🎯 토큰 제한에 맞춰 스마트 선택
            available_tokens = int(100000 * ratio)  # 사업보고서용 토큰 할당
            used_tokens = 0

            for section_name, section_content in sorted_sections:
                if used_tokens >= available_tokens:
                    break

                # 🎯 섹션별 적응적 압축
                importance = section_importance.get(section_name, 5)

                if importance >= 8:  # 고중요도 섹션
                    max_chars = 50000  # 50,000자 유지
                elif importance >= 6:  # 중중요도 섹션
                    max_chars = 30000  # 30,000자 유지
                else:  # 저중요도 섹션
                    max_chars = 15000  # 15,000자 유지

                # 🎯 스마트 자르기: 문장 단위로 자르기
                if len(section_content) > max_chars:
                    # 마지막 완전한 문장까지 유지
                    truncated = section_content[:max_chars]
                    last_period = truncated.rfind(".")
                    last_exclamation = truncated.rfind("!")
                    last_question = truncated.rfind("?")

                    cut_point = max(last_period, last_exclamation, last_question)
                    if cut_point > max_chars * 0.8:  # 80% 이상이면 문장 단위로 자르기
                        compressed_content = section_content[: cut_point + 1]
                    else:
                        compressed_content = truncated

                    compressed_content += f"\n...[중요도 {importance}/10 섹션, {len(section_content):,}자 중 {len(compressed_content):,}자 표시]..."
                else:
                    compressed_content = section_content

                compressed_business[section_name] = compressed_content
                used_tokens += self._estimate_tokens(compressed_content)

            compressed["business_report_dictionary"] = compressed_business

        if "quarterly_report_dictionary" in dart_dict:
            quarterly_report = dart_dict["quarterly_report_dictionary"]
            compressed_quarterly = {}

            # 분기보고서는 더 적극적으로 압축 (최신 정보 우선)
            available_tokens = int(50000 * ratio)  # 분기보고서용 토큰 할당
            used_tokens = 0

            for section_name, section_content in quarterly_report.items():
                if used_tokens >= available_tokens:
                    break

                # 분기보고서는 20,000자로 제한
                if len(section_content) > 20000:
                    truncated = section_content[:20000]
                    last_period = truncated.rfind(".")
                    if last_period > 16000:  # 80% 이상이면 문장 단위로 자르기
                        compressed_content = section_content[: last_period + 1]
                    else:
                        compressed_content = truncated

                    compressed_content += f"\n...[분기보고서 섹션, {len(section_content):,}자 중 {len(compressed_content):,}자 표시]..."
                else:
                    compressed_content = section_content

                compressed_quarterly[section_name] = compressed_content
                used_tokens += self._estimate_tokens(compressed_content)

            compressed["quarterly_report_dictionary"] = compressed_quarterly

        return compressed

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
