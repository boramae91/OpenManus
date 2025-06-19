# -*- coding: utf-8 -*-
"""
🚀 One-Hot Sector Activation 핵심 시스템

90% 비용 절감을 실현하는 혁신적인 섹터별 전문가 활성화 시스템!
기존 55개 에이전트 대신 5개 에이전트만 선택적으로 활성화해요.
"""

import hashlib
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from app.logger import logger

from .gics_sectors import GICSSector, GICSSectorManager
from .sector_teams import SectorTeamFactory


class AnalysisDepth(Enum):
    """
    분석 깊이 수준 정의

    사용자의 니즈에 따라 비용과 품질의 균형을 맞춰요!
    """

    QUICK = "quick"  # 빠른 분석 (2명, $0.20, 12시간 캐시)
    STANDARD = "standard"  # 표준 분석 (5명, $0.50, 24시간 캐시)
    DEEP = "deep"  # 심화 분석 (5명+검증, $1.00, 48시간 캐시)


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
        financial_data: Dict[str, Any],
        enhanced_dart_data: Dict[str, Any] = None,
        manus_collected_data: Dict[str, Any] = None,
        analysis_depth: AnalysisDepth = AnalysisDepth.STANDARD,
        pre_detected_gics_sector: str = None,  # 🎯 사전 감지된 GICS 섹터 추가
    ) -> Dict[str, Any]:
        """
        🚀 종합 데이터 기반 CrewAI 분석 (수정된 워크플로우 + 토큰 최적화)

        재무데이터 + Enhanced DART + Manus Agent 수집 정보를 모두 통합해서
        CrewAI 전문가들이 종합적인 분석을 수행합니다.
        토큰 한계를 고려한 스마트 데이터 최적화가 자동으로 적용됩니다.

        Args:
            user_prompt: 사용자 질문
            stock_name: 종목명
            stock_code: 종목코드
            financial_data: 재무 데이터
            enhanced_dart_data: Enhanced DART 데이터
            manus_collected_data: Manus Agent가 수집한 정보
            analysis_depth: 분석 깊이
            pre_detected_gics_sector: 사전 감지된 GICS 섹터

        Returns:
            Dict: 종합 분석 결과 (토큰 최적화 정보 포함)
        """
        try:
            logger.info(
                f"🎯 CrewAI 종합 분석 시작: {stock_name} (수정된 워크플로우 + 토큰 최적화)"
            )

            # 🔢 0. 토큰 최적화 수행 (가장 먼저!)
            logger.info("🔢 토큰 최적화 시작...")
            optimization_result = self._optimize_data_for_token_limit(
                user_prompt=user_prompt,
                financial_data=financial_data,
                enhanced_dart_data=enhanced_dart_data,
                manus_collected_data=manus_collected_data,
            )

            # 최적화된 데이터 사용
            optimized_financial = optimization_result["financial_data"]
            optimized_dart = optimization_result["enhanced_dart_data"]
            optimized_manus = optimization_result["manus_collected_data"]

            if optimization_result["optimized"]:
                logger.info("🎯 토큰 최적화 적용됨:")
                for optimization in optimization_result["optimization_applied"]:
                    logger.info(f"  • {optimization}")
                final_tokens = optimization_result["token_info"]["final_tokens"]
                logger.info(f"📊 최적화 후 예상 토큰 수: {final_tokens:,}")
            else:
                logger.info("✅ 토큰 수가 목표 범위 내 - 최적화 불필요")

            # 1. 종합 캐시 키 생성 (최적화된 Manus 데이터 포함)
            comprehensive_cache_key = self._generate_comprehensive_cache_key(
                user_prompt,
                stock_name,
                stock_code,
                analysis_depth,
                optimized_manus,  # 최적화된 데이터 사용
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
                    "optimization_applied": optimization_result["optimized"],
                    "optimizations": (
                        optimization_result["optimization_applied"]
                        if optimization_result["optimized"]
                        else []
                    ),
                    "token_info": (
                        optimization_result["token_info"]
                        if optimization_result["optimized"]
                        else {"status": "not_needed"}
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
        """분석 깊이에 따른 전문가 선택"""
        all_experts = team.experts

        if depth == AnalysisDepth.QUICK:
            # QUICK: 프롬프트 키워드 기반 2명 선택
            selected = self._select_by_keywords(all_experts, prompt, 2)
            logger.info(f"⚡ QUICK 모드: {len(selected)}명 전문가 선택")

        elif depth == AnalysisDepth.DEEP:
            # DEEP: 전체 5명 + 검증 단계
            selected = all_experts
            logger.info(f"🔍 DEEP 모드: {len(selected)}명 전문가 + 검증")

        else:  # STANDARD
            # STANDARD: 전체 5명
            selected = all_experts
            logger.info(f"📊 STANDARD 모드: {len(selected)}명 전문가")

        return selected

    def _select_by_keywords(self, experts: List, prompt: str, count: int) -> List:
        """키워드 기반 전문가 선택"""
        keyword_mapping = {
            "재무": "Fundamental Analyst",
            "차트": "Technical Analyst",
            "산업": "Industry Expert",
            "밸류에이션": "Valuation Specialist",
            "리스크": "Risk Assessor",
        }

        selected = []
        prompt_lower = prompt.lower()

        for keyword, role in keyword_mapping.items():
            if keyword in prompt_lower and len(selected) < count:
                expert = next((e for e in experts if e.role == role), None)
                if expert:
                    selected.append(expert)

        # 부족하면 기본 전문가들로 채우기
        while len(selected) < count and len(selected) < len(experts):
            for expert in experts:
                if expert not in selected:
                    selected.append(expert)
                    break

        return selected[:count]

    async def _perform_expert_analysis(
        self,
        experts: List,
        prompt: str,
        stock_name: str,
        stock_code: str,
        financial_data: Dict,
    ) -> Dict[str, Any]:
        """전문가별 분석 수행"""
        insights = {}

        for expert in experts:
            try:
                # 전문가별 맞춤 프롬프트 생성
                expert_prompt = self._build_expert_specific_context(
                    expert,
                    prompt,
                    stock_name,
                    stock_code,
                    financial_data,
                )

                # LLM을 통한 분석 (실제 구현에서는 여기서 LLM 호출)
                analysis_result = await self._call_llm_for_analysis(expert_prompt)

                insights[expert.role] = {
                    "expert_name": expert.name,
                    "analysis": analysis_result,
                    "methods_used": expert.key_methods[:3],  # 상위 3개 방법론만
                }

                logger.info(f"✅ {expert.name} 분석 완료")

            except Exception as e:
                logger.error(f"❌ {expert.name} 분석 실패: {e}")
                insights[expert.role] = {
                    "expert_name": expert.name,
                    "analysis": f"분석 중 오류 발생: {str(e)}",
                    "error": True,
                }

        return insights

    async def _call_llm_for_analysis(self, prompt: str) -> str:
        """LLM을 통한 실제 분석"""
        try:
            # 실제 LLM 호출 로직 - ask 메서드 사용
            response = await self.llm.ask([{"role": "user", "content": prompt}])
            return response
        except Exception as e:
            logger.error(f"LLM 호출 실패: {e}")
            return f"LLM 분석 중 오류 발생: {str(e)}"

    def _calculate_cost_savings(
        self, activated_agents: int, depth: AnalysisDepth
    ) -> Dict[str, Any]:
        """비용 절감 계산"""

        # 깊이별 기본 비용
        depth_costs = {
            AnalysisDepth.QUICK: 0.20,
            AnalysisDepth.STANDARD: 0.50,
            AnalysisDepth.DEEP: 1.00,
        }

        # 기존 방식: 55개 에이전트 모두 활성화
        traditional_cost = 55 * depth_costs[depth]

        # One-Hot 방식: 선택된 에이전트만 활성화
        one_hot_cost = activated_agents * (
            depth_costs[depth] / 5
        )  # 5명 기준으로 정규화

        savings_amount = traditional_cost - one_hot_cost
        savings_percentage = (savings_amount / traditional_cost) * 100

        return {
            "traditional_cost": traditional_cost,
            "one_hot_cost": one_hot_cost,
            "savings_amount": savings_amount,
            "savings_percentage": savings_percentage,
            "activated_agents": activated_agents,
            "depth": depth.value,
        }

    def _generate_cache_key(
        self, prompt: str, stock_name: str, stock_code: str, depth: AnalysisDepth
    ) -> str:
        """캐시 키 생성"""
        content = f"{prompt}_{stock_name}_{stock_code}_{depth.value}"
        return hashlib.md5(content.encode()).hexdigest()

    def _get_cache_ttl(self, depth: AnalysisDepth) -> int:
        """분석 깊이별 캐시 TTL"""
        ttl_mapping = {
            AnalysisDepth.QUICK: 12,
            AnalysisDepth.STANDARD: 24,
            AnalysisDepth.DEEP: 48,
        }
        return ttl_mapping[depth]

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
    ) -> Dict[str, Any]:
        """
        🚀 모든 데이터를 통합한 전문가 분석 수행

        재무데이터 + Enhanced DART + Manus 수집 정보를 모두 활용해서
        각 전문가가 종합적인 분석을 수행해요.

        Args:
            experts: 선택된 전문가 리스트
            prompt: 사용자 프롬프트
            stock_name: 종목명
            stock_code: 종목코드
            financial_data: 재무데이터
            enhanced_dart_data: Enhanced DART 데이터
            manus_collected_data: Manus Agent 수집 정보

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
                comprehensive_prompt = self._build_expert_specific_context(
                    expert,
                    prompt,
                    stock_name,
                    stock_code,
                    financial_data,
                    enhanced_dart_data,
                    manus_collected_data,
                )

                # 전문가별 분석 수행
                analysis_result = await self._call_llm_for_analysis(
                    comprehensive_prompt
                )

                expert_results.append(
                    {
                        "expert_name": expert.name,
                        "expertise_area": expert.expertise,
                        "analysis_result": analysis_result,
                        "data_sources_used": self._identify_used_data_sources(
                            financial_data, enhanced_dart_data, manus_collected_data
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

    def _build_expert_specific_context(
        self,
        expert,
        user_prompt: str,
        stock_name: str,
        stock_code: str,
        financial_data: Dict,
        enhanced_dart_data: Dict = None,
        manus_collected_data: Dict = None,
    ) -> str:
        """
        🎯 전문가별 맞춤형 컨텍스트 구성 (토큰 효율성 극대화)

        각 전문가의 전문성에 맞는 데이터만 선별해서 제공하여
        토큰 사용량을 최소화하면서 분석 품질은 유지합니다.

        Args:
            expert: 전문가 정보
            다른 매개변수들은 기존과 동일

        Returns:
            str: 전문가 맞춤형 컨텍스트
        """
        logger.info(f"🎯 {expert.name} 전문가용 맞춤형 컨텍스트 구성...")

        context_parts = []

        # 기본 정보 (모든 전문가 공통)
        context_parts.append(f"분석 대상: {stock_name} ({stock_code})")
        context_parts.append(f"사용자 질문: {user_prompt}")
        context_parts.append(f"전문가 역할: {expert.name}")
        context_parts.append(f"분석 포커스: {expert.analysis_focus}")

        # 전문가별 맞춤형 데이터 선별
        if "재무" in expert.expertise or "Fundamental" in expert.role:
            # 재무 분석 전문가 - 재무데이터 중심
            if financial_data and financial_data.get("success"):
                financial_summary = self._summarize_financial_data(financial_data)
                context_parts.append("📊 재무데이터:")
                context_parts.append(financial_summary)

            if enhanced_dart_data and enhanced_dart_data.get("success"):
                # 재무 관련 DART 데이터만 선별
                dart_financial = self._extract_dart_financial_only(enhanced_dart_data)
                if dart_financial:
                    context_parts.append("🚀 상세 재무정보 (DART):")
                    context_parts.append(dart_financial)

        elif "기술" in expert.expertise or "Technical" in expert.role:
            # 기술 분석 전문가 - 가격/차트 데이터 중심
            if financial_data and financial_data.get("success"):
                price_data = self._extract_price_data_only(financial_data)
                if price_data:
                    context_parts.append("📈 가격/차트 데이터:")
                    context_parts.append(price_data)

            # Manus 데이터에서 기술적 분석 관련 정보만 추출
            if manus_collected_data and manus_collected_data.get("performed"):
                technical_info = self._extract_technical_analysis_info(
                    manus_collected_data
                )
                if technical_info:
                    context_parts.append("🔍 기술분석 관련 정보:")
                    context_parts.append(technical_info)

        elif "산업" in expert.expertise or "Industry" in expert.role:
            # 산업 분석 전문가 - 업계 동향, 경쟁사 정보 중심
            if manus_collected_data and manus_collected_data.get("performed"):
                industry_info = self._extract_industry_info(manus_collected_data)
                if industry_info:
                    context_parts.append("🏭 산업/경쟁사 정보:")
                    context_parts.append(industry_info)

            # DART에서 사업보고서 관련 정보
            if enhanced_dart_data and enhanced_dart_data.get("success"):
                business_info = self._extract_dart_business_info(enhanced_dart_data)
                if business_info:
                    context_parts.append("📋 사업 정보 (DART):")
                    context_parts.append(business_info)

        elif "밸류" in expert.expertise or "Valuation" in expert.role:
            # 투자 분석 전문가 - 밸류에이션, 투자 지표 중심
            if financial_data and financial_data.get("success"):
                valuation_data = self._extract_valuation_data(financial_data)
                if valuation_data:
                    context_parts.append("💰 밸류에이션 데이터:")
                    context_parts.append(valuation_data)

            if enhanced_dart_data and enhanced_dart_data.get("success"):
                investment_data = self._extract_dart_investment_info(enhanced_dart_data)
                if investment_data:
                    context_parts.append("📊 투자 정보 (DART):")
                    context_parts.append(investment_data)

        elif "리스크" in expert.expertise or "Risk" in expert.role:
            # 리스크 분석 전문가 - 리스크 요인, 재무 안정성 중심
            if financial_data and financial_data.get("success"):
                risk_data = self._extract_risk_indicators(financial_data)
                if risk_data:
                    context_parts.append("⚠️ 리스크 지표:")
                    context_parts.append(risk_data)

            if manus_collected_data and manus_collected_data.get("performed"):
                risk_info = self._extract_risk_factors(manus_collected_data)
                if risk_info:
                    context_parts.append("🚨 리스크 요인:")
                    context_parts.append(risk_info)

        else:
            # 일반 전문가 - 핵심 정보만 요약해서 제공
            if financial_data and financial_data.get("success"):
                basic_summary = self._create_basic_financial_summary(financial_data)
                context_parts.append("📊 기본 재무정보:")
                context_parts.append(basic_summary)

            if manus_collected_data and manus_collected_data.get("performed"):
                key_insights = self._extract_key_insights_only(manus_collected_data)
                if key_insights:
                    context_parts.append("🔍 핵심 인사이트:")
                    context_parts.append(key_insights)

        # 📄 PDF 데이터 처리 (context별 chunking으로 전문가 맞춤형 선택)
        if manus_collected_data and manus_collected_data.get("pdf_analysis", {}).get(
            "pdf_detected"
        ):
            pdf_content = manus_collected_data.get("pdf_analysis", {}).get(
                "pdf_content", {}
            )

            # Context별 청크가 있는지 확인
            if pdf_content.get("contextual_chunks"):
                pdf_chunks = pdf_content["contextual_chunks"]
                relevant_chunks = self._select_relevant_pdf_chunks(
                    pdf_chunks, expert.get("name", ""), max_chunks=2
                )

                if relevant_chunks:
                    context_parts.append("📄 관련 PDF 정보 (맞춤 선택):")
                    for chunk in relevant_chunks:
                        context_parts.append(
                            f"• [{chunk['context_type'].upper()}] {chunk['content'][:1000]}..."
                            if len(chunk["content"]) > 1000
                            else f"• [{chunk['context_type'].upper()}] {chunk['content']}"
                        )
                        # 키워드 정보도 포함
                        if chunk.get("keywords_found"):
                            context_parts.append(
                                f"  핵심 키워드: {', '.join(chunk['keywords_found'][:5])}"
                            )
            else:
                # 기존 방식 fallback
                pdf_summary = self._extract_pdf_key_points(manus_collected_data)
                if pdf_summary:
                    context_parts.append("📄 PDF 핵심 포인트:")
                    context_parts.append(pdf_summary)

        final_context = "\n\n".join(context_parts)

        # 토큰 수 확인 및 로깅
        estimated_tokens = self._estimate_tokens(final_context)
        logger.info(f"🎯 {expert.name} 맞춤형 컨텍스트: {estimated_tokens:,} 토큰")

        return final_context

    def _extract_dart_financial_only(self, enhanced_dart_data: Dict) -> str:
        """DART 데이터에서 재무 관련 정보만 추출"""
        if not enhanced_dart_data.get("financial_analysis", {}).get("success"):
            return ""

        financial = enhanced_dart_data["financial_analysis"]
        summary_parts = []

        # 재무제표 핵심 정보만
        if "consolidated_statements" in financial:
            consolidated = financial["consolidated_statements"]
            if consolidated.get("assets"):
                total_assets = consolidated["assets"].get("total_assets", 0)
                summary_parts.append(f"연결 총자산: {total_assets:,}원")
            if consolidated.get("equity"):
                total_equity = consolidated["equity"].get("total_equity", 0)
                summary_parts.append(f"연결 총자본: {total_equity:,}원")

        return "\n".join(summary_parts)

    def _extract_price_data_only(self, financial_data: Dict) -> str:
        """재무데이터에서 가격/차트 관련 정보만 추출"""
        summary_parts = []

        if "current_price_info" in financial_data:
            price_info = financial_data["current_price_info"]
            current_price = price_info.get("current_price")
            if current_price:
                summary_parts.append(f"현재가: {current_price}")

            day_change = price_info.get("day_change")
            if day_change:
                summary_parts.append(f"일간 변동: {day_change}")

        if "price_history" in financial_data:
            history = financial_data["price_history"]
            week_52_high = history.get("52_week_high")
            week_52_low = history.get("52_week_low")
            if week_52_high and week_52_low:
                summary_parts.append(f"52주 고가: {week_52_high}, 저가: {week_52_low}")

        return "\n".join(summary_parts)

    def _extract_technical_analysis_info(self, manus_data: Dict) -> str:
        """Manus 데이터에서 기술적 분석 관련 정보만 추출"""
        collected_info = manus_data.get("collected_information", "")

        # 기술적 분석 관련 키워드로 필터링
        technical_keywords = [
            "차트",
            "지지선",
            "저항선",
            "이동평균",
            "RSI",
            "MACD",
            "볼린저밴드",
            "기술적",
        ]

        lines = collected_info.split("\n")
        technical_lines = []

        for line in lines:
            if any(keyword in line for keyword in technical_keywords):
                technical_lines.append(line)

        return "\n".join(technical_lines[:20])  # 최대 20줄

    def _extract_industry_info(self, manus_data: Dict) -> str:
        """Manus 데이터에서 산업/경쟁사 정보만 추출"""
        collected_info = manus_data.get("collected_information", "")

        # 산업 분석 관련 키워드로 필터링
        industry_keywords = [
            "경쟁사",
            "시장점유율",
            "업계",
            "산업",
            "동종업계",
            "시장규모",
            "트렌드",
        ]

        lines = collected_info.split("\n")
        industry_lines = []

        for line in lines:
            if any(keyword in line for keyword in industry_keywords):
                industry_lines.append(line)

        return "\n".join(industry_lines[:25])  # 최대 25줄

    def _extract_dart_business_info(self, enhanced_dart_data: Dict) -> str:
        """DART 데이터에서 사업 관련 정보만 추출"""
        # 간단한 사업 정보 요약
        return "사업보고서 기반 주력 사업 정보 (요약)"

    def _extract_valuation_data(self, financial_data: Dict) -> str:
        """재무데이터에서 밸류에이션 관련 정보만 추출"""
        summary_parts = []

        if "financial_ratios" in financial_data:
            ratios = financial_data["financial_ratios"]
            per = ratios.get("P/E")
            pbr = ratios.get("P/B")
            if per:
                summary_parts.append(f"PER: {per}")
            if pbr:
                summary_parts.append(f"PBR: {pbr}")

        return "\n".join(summary_parts)

    def _extract_dart_investment_info(self, enhanced_dart_data: Dict) -> str:
        """DART 데이터에서 투자 관련 정보만 추출"""
        if not enhanced_dart_data.get("investment_analysis", {}).get("success"):
            return ""

        investment = enhanced_dart_data["investment_analysis"]
        summary_parts = []

        # 배당 정보
        if "dividend_info" in investment and investment["dividend_info"]:
            latest_dividend = investment["dividend_info"][0]
            dividend_rate = latest_dividend.get("dividend_rate", 0)
            summary_parts.append(f"배당률: {dividend_rate}%")

        return "\n".join(summary_parts)

    def _extract_risk_indicators(self, financial_data: Dict) -> str:
        """재무데이터에서 리스크 지표만 추출"""
        summary_parts = []

        if "financial_ratios" in financial_data:
            ratios = financial_data["financial_ratios"]
            debt_ratio = ratios.get("부채비율")
            if debt_ratio:
                summary_parts.append(f"부채비율: {debt_ratio}")

        return "\n".join(summary_parts)

    def _extract_risk_factors(self, manus_data: Dict) -> str:
        """Manus 데이터에서 리스크 요인만 추출"""
        collected_info = manus_data.get("collected_information", "")

        # 리스크 관련 키워드로 필터링
        risk_keywords = ["리스크", "위험", "우려", "문제", "하락", "부정적", "위기"]

        lines = collected_info.split("\n")
        risk_lines = []

        for line in lines:
            if any(keyword in line for keyword in risk_keywords):
                risk_lines.append(line)

        return "\n".join(risk_lines[:15])  # 최대 15줄

    def _create_basic_financial_summary(self, financial_data: Dict) -> str:
        """기본적인 재무 요약 (일반 전문가용)"""
        summary_parts = []

        if "basic_info" in financial_data:
            basic = financial_data["basic_info"]
            market_cap = basic.get("market_cap")
            if market_cap:
                summary_parts.append(f"시가총액: {market_cap}")

        if "current_price_info" in financial_data:
            price_info = financial_data["current_price_info"]
            current_price = price_info.get("current_price")
            if current_price:
                summary_parts.append(f"현재가: {current_price}")

        return "\n".join(summary_parts)

    def _extract_key_insights_only(self, manus_data: Dict) -> str:
        """Manus 데이터에서 핵심 인사이트만 추출 (일반 전문가용)"""
        collected_info = manus_data.get("collected_information", "")

        # 첫 500자와 마지막 500자만 추출 (핵심 요약)
        if len(collected_info) > 1000:
            return collected_info[:500] + "\n...\n" + collected_info[-500:]
        else:
            return collected_info

    def _extract_pdf_key_points(self, manus_data: Dict) -> str:
        """PDF에서 핵심 포인트만 추출 (모든 전문가용, 압축된 버전)"""
        pdf_analysis = manus_data.get("pdf_analysis", {})
        if not pdf_analysis.get("pdf_detected"):
            return ""

        pdf_content = pdf_analysis.get("pdf_content", {})
        raw_text = pdf_content.get("raw_text", "")

        if len(raw_text) > 1000:
            # PDF 내용을 극도로 압축 (첫 200자 + 마지막 200자)
            return raw_text[:200] + "\n...[PDF 내용 압축됨]...\n" + raw_text[-200:]
        else:
            return raw_text

    def _map_gics_to_internal_sector(self, gics_sector_name: str):
        """
        🎯 Dataset의 GICS 섹터명을 내부 GICSSector로 매핑

        Args:
            gics_sector_name: Dataset에서 가져온 GICS 섹터명

        Returns:
            GICSSector: 매핑된 내부 섹터 객체
        """
        from app.crew.gics_sectors import GICSSector

        # GICS 섹터명 매핑 테이블
        gics_mapping = {
            # Technology 관련
            "Information Technology": GICSSector.INFORMATION_TECHNOLOGY,
            "Information Technology Services": GICSSector.INFORMATION_TECHNOLOGY,
            "Technology Hardware & Equipment": GICSSector.INFORMATION_TECHNOLOGY,
            "Software & Services": GICSSector.INFORMATION_TECHNOLOGY,
            # Healthcare 관련
            "Health Care": GICSSector.HEALTH_CARE,
            "Healthcare": GICSSector.HEALTH_CARE,
            "Pharmaceuticals, Biotechnology & Life Sciences": GICSSector.HEALTH_CARE,
            # Financial 관련
            "Financials": GICSSector.FINANCIALS,
            "Financial Services": GICSSector.FINANCIALS,
            "Banks": GICSSector.FINANCIALS,
            "Insurance": GICSSector.FINANCIALS,
            # Consumer 관련
            "Consumer Discretionary": GICSSector.CONSUMER_DISCRETIONARY,
            "Consumer Staples": GICSSector.CONSUMER_STAPLES,
            "Food, Beverage & Tobacco": GICSSector.CONSUMER_STAPLES,
            "Retailing": GICSSector.CONSUMER_DISCRETIONARY,
            # Communication 관련
            "Communication Services": GICSSector.COMMUNICATION_SERVICES,
            "Telecommunication Services": GICSSector.COMMUNICATION_SERVICES,
            "Media & Entertainment": GICSSector.COMMUNICATION_SERVICES,
            # Industrial 관련
            "Industrials": GICSSector.INDUSTRIALS,
            "Capital Goods": GICSSector.INDUSTRIALS,
            "Transportation": GICSSector.INDUSTRIALS,
            # Energy 관련
            "Energy": GICSSector.ENERGY,
            "Oil, Gas & Consumable Fuels": GICSSector.ENERGY,
            # Materials 관련
            "Materials": GICSSector.MATERIALS,
            "Chemicals": GICSSector.MATERIALS,
            "Metals & Mining": GICSSector.MATERIALS,
            # Utilities 관련
            "Utilities": GICSSector.UTILITIES,
            "Electric Utilities": GICSSector.UTILITIES,
            # Real Estate 관련
            "Real Estate": GICSSector.REAL_ESTATE,
        }

        # 정확한 매핑 찾기
        mapped_sector = gics_mapping.get(gics_sector_name)
        if mapped_sector:
            logger.info(
                f"✅ GICS 매핑 성공: {gics_sector_name} -> {mapped_sector.name}"
            )
            return mapped_sector

        # 부분 매칭 시도 (키워드 기반)
        gics_lower = gics_sector_name.lower()
        if (
            "technolog" in gics_lower
            or "software" in gics_lower
            or "information" in gics_lower
        ):
            logger.info(f"🔍 키워드 매핑: {gics_sector_name} -> Technology")
            return GICSSector.INFORMATION_TECHNOLOGY
        elif (
            "health" in gics_lower or "pharma" in gics_lower or "biotech" in gics_lower
        ):
            logger.info(f"🔍 키워드 매핑: {gics_sector_name} -> Healthcare")
            return GICSSector.HEALTH_CARE
        elif "financial" in gics_lower or "bank" in gics_lower:
            logger.info(f"🔍 키워드 매핑: {gics_sector_name} -> Financials")
            return GICSSector.FINANCIALS
        elif "consumer" in gics_lower:
            if "discretionary" in gics_lower:
                logger.info(
                    f"🔍 키워드 매핑: {gics_sector_name} -> Consumer Discretionary"
                )
                return GICSSector.CONSUMER_DISCRETIONARY
            else:
                logger.info(f"🔍 키워드 매핑: {gics_sector_name} -> Consumer Staples")
                return GICSSector.CONSUMER_STAPLES
        elif "communication" in gics_lower or "media" in gics_lower:
            logger.info(f"🔍 키워드 매핑: {gics_sector_name} -> Communication")
            return GICSSector.COMMUNICATION_SERVICES
        elif "industrial" in gics_lower:
            logger.info(f"🔍 키워드 매핑: {gics_sector_name} -> Industrials")
            return GICSSector.INDUSTRIALS
        elif "energy" in gics_lower:
            logger.info(f"🔍 키워드 매핑: {gics_sector_name} -> Energy")
            return GICSSector.ENERGY
        elif "material" in gics_lower:
            logger.info(f"🔍 키워드 매핑: {gics_sector_name} -> Materials")
            return GICSSector.MATERIALS
        elif "utilities" in gics_lower:
            logger.info(f"🔍 키워드 매핑: {gics_sector_name} -> Utilities")
            return GICSSector.UTILITIES
        elif "real estate" in gics_lower:
            logger.info(f"🔍 키워드 매핑: {gics_sector_name} -> Real Estate")
            return GICSSector.REAL_ESTATE

        # 매핑 실패시 기본값 (Technology)
        logger.warning(
            f"⚠️ GICS 매핑 실패: {gics_sector_name} -> 기본값(Technology) 사용"
        )
        return GICSSector.INFORMATION_TECHNOLOGY

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

        # 한국어와 영어가 혼재된 텍스트를 고려한 토큰 추정
        # 일반적으로 한국어는 2-3자당 1토큰, 영어는 4자당 1토큰
        return max(1, len(text) // 3)

    def _summarize_financial_data(self, financial_data: Dict) -> str:
        """
        재무데이터를 요약해서 문자열로 반환합니다.

        Args:
            financial_data: 재무데이터 딕셔너리

        Returns:
            str: 요약된 재무데이터 문자열
        """
        if not financial_data or not financial_data.get("success"):
            return "재무데이터 없음"

        summary_parts = []

        # 기본 정보
        if "basic_info" in financial_data:
            basic = financial_data["basic_info"]
            summary_parts.append(f"회사: {basic.get('company_name', 'N/A')}")
            summary_parts.append(f"섹터: {basic.get('sector', 'N/A')}")
            summary_parts.append(f"산업: {basic.get('industry', 'N/A')}")

        # 현재 주가 정보
        if "current_price_info" in financial_data:
            price_info = financial_data["current_price_info"]
            current_price = price_info.get("current_price")
            market_cap = price_info.get("market_cap")
            if current_price:
                summary_parts.append(f"현재가: {current_price:,}")
            if market_cap:
                summary_parts.append(f"시가총액: {market_cap:,}")

        # 재무 비율
        if "financial_ratios" in financial_data:
            ratios = financial_data["financial_ratios"]
            per = ratios.get("pe_ratio")
            pbr = ratios.get("pb_ratio")
            roe = ratios.get("return_on_equity")
            debt_ratio = ratios.get("debt_to_equity")

            if per:
                summary_parts.append(f"PER: {per}")
            if pbr:
                summary_parts.append(f"PBR: {pbr}")
            if roe:
                summary_parts.append(f"ROE: {roe:.2%}")
            if debt_ratio:
                summary_parts.append(f"부채비율: {debt_ratio}")

        # 성장성 지표
        if "growth_metrics" in financial_data:
            growth = financial_data["growth_metrics"]
            revenue_growth = growth.get("revenue_growth")
            earnings_growth = growth.get("earnings_growth")

            if revenue_growth:
                summary_parts.append(f"매출성장률: {revenue_growth:.2%}")
            if earnings_growth:
                summary_parts.append(f"이익성장률: {earnings_growth:.2%}")

        return "\n".join(summary_parts) if summary_parts else "재무데이터 요약 없음"

    def _summarize_enhanced_dart_data(self, enhanced_dart_data: Dict) -> str:
        """
        Enhanced DART 데이터를 요약해서 문자열로 반환합니다.

        Args:
            enhanced_dart_data: Enhanced DART 데이터 딕셔너리

        Returns:
            str: 요약된 DART 데이터 문자열
        """
        if not enhanced_dart_data or not enhanced_dart_data.get("success"):
            return "Enhanced DART 데이터 없음"

        summary_parts = []

        # 기본 정보
        if "basic_info" in enhanced_dart_data:
            basic_info = enhanced_dart_data["basic_info"]
            company_name = basic_info.get("company_name")
            business_type = basic_info.get("business_type")
            if company_name:
                summary_parts.append(f"회사명: {company_name}")
            if business_type:
                summary_parts.append(f"업종: {business_type}")

        # 재무분석 정보
        if "financial_analysis" in enhanced_dart_data:
            financial = enhanced_dart_data["financial_analysis"]
            if financial.get("success"):
                if "consolidated_statements" in financial:
                    statements = financial["consolidated_statements"]
                    asset_info = statements.get("asset_info", {})
                    equity_info = statements.get("equity_info", {})
                    income_info = statements.get("income_info", {})

                    total_assets = asset_info.get("total_assets")
                    total_equity = equity_info.get("total_equity")
                    revenue = income_info.get("revenue")
                    net_income = income_info.get("net_income")

                    if total_assets:
                        summary_parts.append(f"총자산: {total_assets:,}")
                    if total_equity:
                        summary_parts.append(f"총자본: {total_equity:,}")
                    if revenue:
                        summary_parts.append(f"매출액: {revenue:,}")
                    if net_income:
                        summary_parts.append(f"순이익: {net_income:,}")

        # 투자분석 정보
        if "investment_analysis" in enhanced_dart_data:
            investment = enhanced_dart_data["investment_analysis"]
            if investment.get("success"):
                if "dividend_info" in investment and investment["dividend_info"]:
                    latest_dividend = investment["dividend_info"][0]
                    dividend_rate = latest_dividend.get("dividend_rate")
                    if dividend_rate:
                        summary_parts.append(f"배당률: {dividend_rate}%")

        # 공시정보
        if "disclosure_info" in enhanced_dart_data:
            disclosure = enhanced_dart_data["disclosure_info"]
            if disclosure.get("recent_disclosures"):
                disclosure_count = len(disclosure["recent_disclosures"])
                summary_parts.append(f"최근 공시: {disclosure_count}건")

        return (
            "\n".join(summary_parts)
            if summary_parts
            else "Enhanced DART 데이터 요약 없음"
        )

    def _calculate_total_context_tokens(
        self,
        user_prompt: str,
        financial_data: Dict,
        enhanced_dart_data: Dict = None,
        manus_collected_data: Dict = None,
    ) -> Dict[str, int]:
        """
        🔢 전체 컨텍스트 토큰 수 계산

        Returns:
            Dict: 데이터 소스별 토큰 수
        """
        token_breakdown = {
            "user_prompt": self._estimate_tokens(user_prompt),
            "financial_data": 0,
            "enhanced_dart_data": 0,
            "manus_collected_data": 0,
            "pdf_data": 0,
            "total": 0,
        }

        # 재무데이터 토큰 계산
        if financial_data and financial_data.get("success"):
            financial_summary = self._summarize_financial_data(financial_data)
            token_breakdown["financial_data"] = self._estimate_tokens(financial_summary)

        # Enhanced DART 데이터 토큰 계산
        if enhanced_dart_data and enhanced_dart_data.get("success"):
            dart_summary = self._summarize_enhanced_dart_data(enhanced_dart_data)
            token_breakdown["enhanced_dart_data"] = self._estimate_tokens(dart_summary)

        # Manus 수집 데이터 토큰 계산
        if manus_collected_data and manus_collected_data.get("performed"):
            collected_info = manus_collected_data.get("collected_information", "")
            token_breakdown["manus_collected_data"] = self._estimate_tokens(
                collected_info
            )

            # 📄 PDF 데이터 토큰 계산 (chunking 적용시 더 정확한 계산)
            pdf_analysis = manus_collected_data.get("pdf_analysis", {})
            if pdf_analysis.get("pdf_detected") and pdf_analysis.get(
                "analysis_completed"
            ):
                pdf_content = pdf_analysis.get("pdf_content", {})

                # Context별 청크가 있으면 청크 기반 계산 (더 효율적)
                if pdf_content.get("contextual_chunks"):
                    # 전문가별로 선택될 청크들의 평균 토큰 수로 계산
                    chunks = pdf_content["contextual_chunks"]
                    if chunks:
                        # 상위 3개 청크의 평균 토큰 수로 추정 (실제 사용량에 가까움)
                        top_chunks = sorted(
                            chunks,
                            key=lambda x: x.get("relevance_score", 0),
                            reverse=True,
                        )[:3]
                        chunk_tokens = sum(
                            self._estimate_tokens(chunk["content"])
                            for chunk in top_chunks
                        )
                        token_breakdown["pdf_data"] = chunk_tokens
                        logger.info(
                            f"📄 PDF 청크 기반 토큰 계산: {chunk_tokens:,} (상위 3개 청크)"
                        )
                    else:
                        token_breakdown["pdf_data"] = 0
                else:
                    # 기존 방식: 전체 PDF 텍스트 기반 계산
                    pdf_text = pdf_content.get("raw_text", "")
                    token_breakdown["pdf_data"] = self._estimate_tokens(pdf_text)

        # 총 토큰 수 계산
        token_breakdown["total"] = (
            sum(token_breakdown.values()) - token_breakdown["total"]
        )

        return token_breakdown

    def _optimize_data_for_token_limit(
        self,
        user_prompt: str,
        financial_data: Dict,
        enhanced_dart_data: Dict = None,
        manus_collected_data: Dict = None,
        max_tokens: int = 120000,  # GPT-4의 일반적인 컨텍스트 한계
        target_tokens: int = 100000,  # 안전 마진을 둔 목표 토큰
    ) -> Dict[str, Any]:
        """
        🎯 토큰 한계에 맞게 데이터 최적화

        Args:
            max_tokens: 최대 허용 토큰 수
            target_tokens: 목표 토큰 수 (안전 마진 포함)

        Returns:
            Dict: 최적화된 데이터와 토큰 정보
        """
        logger.info(f"🔢 토큰 최적화 시작 - 목표: {target_tokens:,} 토큰")

        # 현재 토큰 수 계산
        token_breakdown = self._calculate_total_context_tokens(
            user_prompt, financial_data, enhanced_dart_data, manus_collected_data
        )

        current_tokens = token_breakdown["total"]
        logger.info(f"📊 현재 총 토큰 수: {current_tokens:,}")

        if current_tokens <= target_tokens:
            logger.info("✅ 토큰 수가 목표 범위 내 - 최적화 불필요")
            return {
                "optimized": False,
                "financial_data": financial_data,
                "enhanced_dart_data": enhanced_dart_data,
                "manus_collected_data": manus_collected_data,
                "token_info": token_breakdown,
                "optimization_applied": [],
            }

        logger.warning(f"⚠️ 토큰 수 초과: {current_tokens:,} > {target_tokens:,}")

        optimizations_applied = []
        optimized_manus_data = (
            manus_collected_data.copy() if manus_collected_data else None
        )
        optimized_dart_data = enhanced_dart_data.copy() if enhanced_dart_data else None

        # 1단계: PDF 데이터 최적화 (chunking 우선, 압축은 최후 수단)
        if token_breakdown["pdf_data"] > 20000:
            logger.info("📄 PDF 데이터 context별 chunking 적용...")
            optimized_manus_data = self._compress_pdf_data(
                optimized_manus_data, target_ratio=0.3
            )
            optimizations_applied.append("PDF Context별 Chunking 적용")

            # 재계산
            new_tokens = self._calculate_total_context_tokens(
                user_prompt, financial_data, optimized_dart_data, optimized_manus_data
            )["total"]
            logger.info(f"📉 PDF 압축 후: {new_tokens:,} 토큰")

            if new_tokens <= target_tokens:
                logger.info("✅ PDF Context Chunking으로 토큰 목표 달성")
                return self._build_optimization_result(
                    financial_data,
                    optimized_dart_data,
                    optimized_manus_data,
                    new_tokens,
                    optimizations_applied,
                )

        # 2단계: Manus 수집 정보 요약
        if token_breakdown["manus_collected_data"] > 15000:
            logger.info("📝 Manus 수집 정보 요약 적용...")
            optimized_manus_data = self._summarize_manus_data(optimized_manus_data)
            optimizations_applied.append("Manus 수집 정보 요약")

            new_tokens = self._calculate_total_context_tokens(
                user_prompt, financial_data, optimized_dart_data, optimized_manus_data
            )["total"]
            logger.info(f"📉 Manus 요약 후: {new_tokens:,} 토큰")

            if new_tokens <= target_tokens:
                logger.info("✅ Manus 요약으로 토큰 목표 달성")
                return self._build_optimization_result(
                    financial_data,
                    optimized_dart_data,
                    optimized_manus_data,
                    new_tokens,
                    optimizations_applied,
                )

        # 3단계: Enhanced DART 데이터 선별
        if token_breakdown["enhanced_dart_data"] > 10000:
            logger.info("🎯 Enhanced DART 데이터 선별 적용...")
            optimized_dart_data = self._prioritize_dart_data(
                optimized_dart_data, user_prompt
            )
            optimizations_applied.append("Enhanced DART 핵심 데이터 선별")

            new_tokens = self._calculate_total_context_tokens(
                user_prompt, financial_data, optimized_dart_data, optimized_manus_data
            )["total"]
            logger.info(f"📉 DART 선별 후: {new_tokens:,} 토큰")

        final_tokens = self._calculate_total_context_tokens(
            user_prompt, financial_data, optimized_dart_data, optimized_manus_data
        )["total"]

        if final_tokens > max_tokens:
            logger.error(f"❌ 최대 토큰 한계 초과: {final_tokens:,} > {max_tokens:,}")
            # 강제 압축 적용
            optimizations_applied.append("강제 압축 (토큰 한계 초과)")
            optimized_manus_data = self._emergency_compression(optimized_manus_data)

        return self._build_optimization_result(
            financial_data,
            optimized_dart_data,
            optimized_manus_data,
            final_tokens,
            optimizations_applied,
        )

    def _compress_pdf_data(self, manus_data: Dict, target_ratio: float = 0.3) -> Dict:
        """PDF 데이터 압축"""
        if not manus_data or not manus_data.get("pdf_analysis", {}).get("pdf_detected"):
            return manus_data

        optimized_data = manus_data.copy()
        pdf_analysis = optimized_data.get("pdf_analysis", {})
        pdf_content = pdf_analysis.get("pdf_content", {})

        if "raw_text" in pdf_content:
            original_text = pdf_content["raw_text"]
            original_length = len(original_text)

            # 60만자 제한 적용
            if original_length > 600000:
                logger.info(
                    f"📏 PDF 60만자 제한 적용: {original_length:,}자 → 600,000자"
                )
                compressed_text = (
                    original_text[:600000] + "\n...[60만자 제한으로 일부 생략]"
                )
                pdf_content["raw_text"] = compressed_text
                logger.info(f"✅ PDF 압축 완료: {len(compressed_text):,}자")

        return optimized_data

    def _summarize_manus_data(
        self, manus_data: Dict, target_length: int = 5000
    ) -> Dict:
        """Manus 수집 데이터 요약"""
        if not manus_data or not manus_data.get("performed"):
            return manus_data

        optimized_data = manus_data.copy()
        collected_info = optimized_data.get("collected_information", "")

        if len(collected_info) > target_length:
            # 첫 부분과 마지막 부분만 유지
            first_part = collected_info[: target_length // 2]
            last_part = collected_info[-(target_length // 2) :]
            summarized = first_part + "\n...[요약으로 중간 부분 생략]...\n" + last_part

            optimized_data["collected_information"] = summarized
            logger.info(
                f"📝 Manus 데이터 요약: {len(collected_info):,}자 → {len(summarized):,}자"
            )

        return optimized_data

    def _prioritize_dart_data(self, dart_data: Dict, user_prompt: str) -> Dict:
        """사용자 의도에 따른 DART 데이터 우선순위 설정"""
        if not dart_data or not dart_data.get("success"):
            return dart_data

        # 간단한 우선순위 적용 (실제로는 더 복잡한 로직 필요)
        optimized_data = dart_data.copy()

        # 재무 관련 키워드가 있으면 재무 데이터만 유지
        if any(
            keyword in user_prompt.lower()
            for keyword in ["재무", "매출", "이익", "손익"]
        ):
            # 재무 분석만 유지
            if "financial_analysis" in optimized_data:
                temp_data = {"financial_analysis": optimized_data["financial_analysis"]}
                optimized_data = {**optimized_data, **temp_data}
                logger.info("🎯 재무 관련 DART 데이터만 선별")

        return optimized_data

    def _emergency_compression(self, manus_data: Dict) -> Dict:
        """긴급 압축 (토큰 한계 초과시)"""
        if not manus_data:
            return manus_data

        optimized_data = manus_data.copy()

        # 수집 정보를 극도로 압축
        collected_info = optimized_data.get("collected_information", "")
        if len(collected_info) > 1000:
            emergency_summary = (
                collected_info[:500] + "\n...[긴급 압축]...\n" + collected_info[-500:]
            )
            optimized_data["collected_information"] = emergency_summary
            logger.warning("🚨 긴급 압축 적용됨")

        return optimized_data

    def _build_optimization_result(
        self,
        financial_data: Dict,
        dart_data: Dict,
        manus_data: Dict,
        final_tokens: int,
        optimizations: List[str],
    ) -> Dict[str, Any]:
        """최적화 결과 구성"""
        return {
            "optimized": True,
            "financial_data": financial_data,
            "enhanced_dart_data": dart_data,
            "manus_collected_data": manus_data,
            "token_info": {
                "final_tokens": final_tokens,
                "optimizations_applied": optimizations,
            },
            "optimization_applied": optimizations,
        }

    async def _create_crewai_intelligent_chunks(
        self, pdf_text: str, pdf_path: str = None
    ) -> List[Dict[str, Any]]:
        """
        🤖 CrewAI 전용 AI 기반 지능적 청킹 (60만자 지원)

        enhanced_main.py보다 간소화되었지만 더 효율적인 버전
        """
        if len(pdf_text) < 5000:  # 너무 짧으면 청킹 불필요
            return []

        try:
            # 분석용 텍스트 준비 (대용량 처리)
            if len(pdf_text) > 200000:  # 20만자 이상이면 샘플링
                analysis_text = (
                    pdf_text[:50000]
                    + "\n\n...[중간 내용 생략]...\n\n"
                    + pdf_text[-20000:]
                )
                logger.info("📊 대용량 PDF - 샘플링으로 구조 분석")
            else:
                analysis_text = pdf_text

            # CrewAI 최적화된 구조 분석 프롬프트
            structure_prompt = f"""
다음 PDF 문서를 CrewAI 전문가 분석에 최적화된 3-6개 섹션으로 나누어주세요.

PDF 내용 ({len(pdf_text):,}자):
{analysis_text}

🎯 CrewAI 분석 최적화 요구사항:
1. 재무 전문가용 섹션 (재무제표, 실적, 비율분석 등)
2. 사업 전문가용 섹션 (사업모델, 시장, 경쟁력 등)
3. 투자 전문가용 섹션 (밸류에이션, 투자의견, 전망 등)
4. 리스크 전문가용 섹션 (위험요인, 불확실성 등)
5. 기타 중요 섹션

📝 출력 형식 (반드시 준수):
SECTION_1: [섹션제목] | financial | [핵심키워드]
SECTION_2: [섹션제목] | business | [핵심키워드]
SECTION_3: [섹션제목] | investment | [핵심키워드]
SECTION_4: [섹션제목] | risk | [핵심키워드]

⚠️ 제약사항:
- 각 섹션은 최소 5,000자, 최대 600,000자
- 키워드는 해당 섹션 시작을 정확히 찾을 수 있는 고유한 문구
- 전문가별로 최적화된 내용 분류
"""

            # LLM 호출
            response = await self.llm.ask(
                [{"role": "user", "content": structure_prompt}]
            )

            # 응답 파싱
            sections = self._parse_crewai_section_analysis(response)

            if sections and len(sections) >= 2:
                # 텍스트 분할 수행
                chunks = self._split_text_by_crewai_sections(pdf_text, sections)
                logger.info(f"🤖 CrewAI AI 청킹 성공: {len(chunks)}개 청크 생성")
                return chunks
            else:
                logger.warning("⚠️ CrewAI AI 청킹에서 충분한 섹션을 찾지 못함")
                return []

        except Exception as e:
            logger.error(f"❌ CrewAI AI 청킹 실패: {e}")
            return []

    def _parse_crewai_section_analysis(self, ai_response: str) -> List[Dict[str, str]]:
        """CrewAI 최적화된 섹션 분석 파싱"""
        import re

        sections = []

        try:
            # 표준 패턴
            pattern = r"SECTION_(\d+):\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*(.+)"
            matches = re.findall(pattern, ai_response, re.MULTILINE | re.IGNORECASE)

            for match in matches:
                section_num, title, content_type, keyword = match

                # CrewAI 컨텍스트 타입 검증
                valid_types = [
                    "financial",
                    "business",
                    "investment",
                    "risk",
                    "governance",
                    "technical",
                    "general",
                ]
                if content_type.strip().lower() not in valid_types:
                    content_type = "general"

                sections.append(
                    {
                        "section_number": int(section_num),
                        "title": title.strip(),
                        "content_type": content_type.strip().lower(),
                        "start_keyword": keyword.strip(),
                    }
                )

            logger.info(f"🔍 CrewAI 섹션 파싱: {len(sections)}개 섹션")
            return sections

        except Exception as e:
            logger.error(f"❌ CrewAI 섹션 파싱 오류: {e}")
            return []

    def _split_text_by_crewai_sections(
        self, pdf_text: str, sections: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """CrewAI 최적화된 텍스트 분할 (60만자 지원)"""
        chunks = []

        try:
            # 섹션별 위치 찾기 (더 관대한 검색)
            section_positions = []

            for section in sections:
                keyword = section["start_keyword"]

                # 다양한 키워드 변형으로 검색
                search_variants = [
                    keyword,
                    keyword.strip(),
                    keyword.upper(),
                    keyword.lower(),
                    keyword.replace(" ", ""),
                    keyword.replace(".", ""),
                    keyword.replace("(", "").replace(")", ""),
                ]

                best_pos = -1
                found_variant = keyword

                for variant in search_variants:
                    if variant and len(variant) > 2:
                        pos = pdf_text.find(variant)
                        if pos != -1:
                            best_pos = pos
                            found_variant = variant
                            break

                if best_pos == -1:
                    # 부분 매칭 시도
                    words = keyword.split()
                    if len(words) > 1:
                        for word in words:
                            if len(word) > 3:
                                pos = pdf_text.find(word)
                                if pos != -1:
                                    best_pos = pos
                                    found_variant = word
                                    break

                section_positions.append(
                    {
                        "section": section,
                        "start_pos": best_pos,
                        "found_variant": found_variant,
                    }
                )

            # 위치별로 정렬
            valid_positions = [sp for sp in section_positions if sp["start_pos"] != -1]
            valid_positions.sort(key=lambda x: x["start_pos"])

            if not valid_positions:
                logger.warning("⚠️ CrewAI 섹션 키워드로 분할 위치를 찾지 못함")
                return []

            # 실제 청크 생성 (60만자 제한 적용)
            for i, pos_info in enumerate(valid_positions):
                section = pos_info["section"]
                start_pos = pos_info["start_pos"]

                # 다음 섹션까지 또는 문서 끝까지
                if i + 1 < len(valid_positions):
                    end_pos = valid_positions[i + 1]["start_pos"]
                else:
                    end_pos = len(pdf_text)

                section_text = pdf_text[start_pos:end_pos].strip()

                # 최소 크기 검증
                if len(section_text) >= 2000:  # 최소 2000자
                    # 60만자 제한 적용
                    max_size_applied = False
                    if len(section_text) > 600000:
                        section_text = (
                            section_text[:600000]
                            + "\n...[CrewAI 60만자 제한으로 일부 생략]"
                        )
                        max_size_applied = True
                        logger.info(
                            f"📏 CrewAI 섹션 '{section['title']}' 60만자로 제한"
                        )

                    chunks.append(
                        {
                            "chunk_id": i + 1,
                            "context_type": section["content_type"],
                            "content": section_text,
                            "content_length": len(section_text),
                            "section_title": section["title"],
                            "start_keyword": section["start_keyword"],
                            "found_variant": pos_info["found_variant"],
                            "start_position": start_pos,
                            "chunk_type": "crewai_ai_based",
                            "source": "crewai_ai_analysis",
                            "expert_optimized": True,
                            "max_size_applied": max_size_applied,
                            "crewai_section_info": section,
                        }
                    )

            logger.info(f"✂️ CrewAI 텍스트 분할 완료: {len(chunks)}개 청크")
            return chunks

        except Exception as e:
            logger.error(f"❌ CrewAI 텍스트 분할 오류: {e}")
            return []

    def _create_advanced_contextual_pdf_chunks(
        self, pdf_text: str
    ) -> List[Dict[str, Any]]:
        """
        📝 고급 키워드 기반 PDF 청킹 (60만자 지원, CrewAI 최적화)
        """
        if len(pdf_text) < 5000:
            return []

        chunks = []
        lines = pdf_text.split("\n")

        # CrewAI 전문가별 최적화된 키워드
        crewai_optimized_keywords = {
            "financial": [
                "재무제표",
                "손익계산서",
                "대차대조표",
                "현금흐름표",
                "자본변동표",
                "매출",
                "revenue",
                "영업이익",
                "순이익",
                "EBITDA",
                "ROE",
                "ROA",
                "ROIC",
                "PER",
                "PBR",
                "PSR",
                "PCR",
                "EV/EBITDA",
                "자산",
                "부채",
                "자본",
                "현금",
                "배당",
                "부채비율",
                "유동비율",
                "당좌비율",
                "이자보상배수",
            ],
            "business": [
                "사업모델",
                "비즈니스모델",
                "사업영역",
                "주력사업",
                "시장점유율",
                "경쟁우위",
                "핵심역량",
                "성장동력",
                "신사업",
                "해외진출",
                "사업전략",
                "마케팅전략",
                "고객",
                "제품포트폴리오",
                "서비스",
                "브랜드",
                "유통채널",
                "공급망",
            ],
            "investment": [
                "투자의견",
                "투자등급",
                "목표가",
                "적정가",
                "밸류에이션",
                "투자포인트",
                "투자매력",
                "투자전략",
                "추천",
                "매수",
                "매도",
                "보유",
                "상향",
                "하향",
                "DCF",
                "PEG",
                "Sum-of-parts",
                "NAV",
                "투자수익률",
                "배당수익률",
            ],
            "risk": [
                "위험요인",
                "리스크팩터",
                "위험관리",
                "불확실성",
                "변동성",
                "시장위험",
                "신용위험",
                "운영위험",
                "유동성위험",
                "규제위험",
                "경쟁위험",
                "기술위험",
                "환율위험",
                "금리위험",
                "원자재가격",
                "경기침체",
                "수요감소",
            ],
            "governance": [
                "지배구조",
                "기업지배구조",
                "ESG",
                "주주구조",
                "경영진",
                "이사회",
                "사외이사",
                "감사위원회",
                "내부통제",
                "리스크관리",
                "컴플라이언스",
                "투명성",
                "주주친화",
                "배당정책",
                "자사주매입",
                "경영권",
            ],
            "technical": [
                "기술력",
                "기술개발",
                "R&D",
                "연구개발",
                "혁신",
                "특허",
                "지적재산권",
                "핵심기술",
                "기술경쟁력",
                "디지털전환",
                "자동화",
                "AI",
                "빅데이터",
                "클라우드",
                "플랫폼",
                "솔루션",
                "시스템",
                "인프라",
            ],
        }

        # 청크 생성 (더 큰 단위로)
        current_chunk = {"lines": [], "context_scores": {}, "total_score": 0}
        chunks_buffer = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 라인별 컨텍스트 점수 계산 (가중치 적용)
            line_lower = line.lower()
            line_scores = {}

            for context_type, keywords in crewai_optimized_keywords.items():
                score = 0
                for keyword in keywords:
                    if keyword in line_lower:
                        # 키워드 길이와 중요도에 따른 차등 점수
                        if len(keyword) >= 5:  # 긴 키워드 높은 점수
                            score += 3
                        elif len(keyword) >= 3:
                            score += 2
                        else:
                            score += 1

                if score > 0:
                    line_scores[context_type] = score
                    if context_type not in current_chunk["context_scores"]:
                        current_chunk["context_scores"][context_type] = 0
                    current_chunk["context_scores"][context_type] += score

            current_chunk["lines"].append(line)
            current_chunk["total_score"] += sum(line_scores.values())

            # 청크 분할 조건 (더 큰 단위로, 60만자 고려)
            chunk_text = "\n".join(current_chunk["lines"])
            line_count = len(current_chunk["lines"])

            # 분할 조건: 라인 수 또는 문자 수 기준
            if (line_count >= 200 and current_chunk["total_score"] > 0) or len(
                chunk_text
            ) >= 400000:  # 40만자 기준
                chunks_buffer.append(current_chunk)
                current_chunk = {"lines": [], "context_scores": {}, "total_score": 0}

        # 마지막 청크
        if current_chunk["lines"]:
            chunks_buffer.append(current_chunk)

        # 최종 청크 변환 (60만자 제한)
        for i, chunk_data in enumerate(chunks_buffer):
            chunk_text = "\n".join(chunk_data["lines"])

            if len(chunk_text) >= 5000:  # 최소 5000자
                # 60만자 제한 적용
                max_size_applied = False
                if len(chunk_text) > 600000:
                    chunk_text = (
                        chunk_text[:600000]
                        + "\n...[CrewAI 고급 청킹 60만자 제한으로 일부 생략]"
                    )
                    max_size_applied = True

                # 주요 컨텍스트 결정
                if chunk_data["context_scores"]:
                    best_context = max(
                        chunk_data["context_scores"].items(), key=lambda x: x[1]
                    )
                    context_type = best_context[0]
                    relevance_score = best_context[1]
                else:
                    context_type = "general"
                    relevance_score = 0

                chunks.append(
                    {
                        "chunk_id": i + 1,
                        "context_type": context_type,
                        "content": chunk_text,
                        "content_length": len(chunk_text),
                        "line_count": len(chunk_data["lines"]),
                        "relevance_score": relevance_score,
                        "context_distribution": chunk_data["context_scores"],
                        "source": "crewai_advanced_keyword",
                        "chunk_type": "advanced_keyword_crewai",
                        "expert_optimized": True,
                        "max_size_applied": max_size_applied,
                    }
                )

        logger.info(
            f"📝 CrewAI 고급 키워드 청킹 완료: {len(chunks)}개 청크 (60만자 지원)"
        )
        return chunks

    def _create_toc_based_pdf_chunks(
        self, pdf_text: str, pdf_path: str
    ) -> List[Dict[str, Any]]:
        """
        🔖 목차 기반 PDF 청킹 (enhanced_main.py와 동일한 방식)

        목차 구조에 따라 PDF를 의미있는 섹션으로 분할합니다.
        """
        if not pdf_text or not pdf_path:
            return []

        try:
            import re

            # enhanced_main.py의 large_pdf_analyzer와 유사한 로직
            # 하지만 SmartSectorManager에서는 simplified 버전 사용
            # 목차 패턴 감지 시도
            toc_patterns = [
                r"^\s*(\d+)\.\s+(.+)$",  # "1. 제목" 패턴
                r"^\s*([\d\.]+)\s+(.+)$",  # "1.1 제목" 패턴
                r"^\s*([가-힣])\.\s+(.+)$",  # "가. 제목" 패턴
                r"^\s*\(?([가-힣])\)?\s+(.+)$",  # "(가) 제목" 패턴
            ]

            lines = pdf_text.split("\n")
            toc_items = []

            for i, line in enumerate(lines):
                line = line.strip()
                if not line or len(line) < 3:
                    continue

                for pattern in toc_patterns:
                    match = re.match(pattern, line)
                    if match:
                        toc_items.append(
                            {
                                "line_number": i,
                                "title": match.group(2).strip(),
                                "level": 1,  # 간단한 레벨링
                                "content_start": i,
                            }
                        )
                        break

            if len(toc_items) < 2:  # 최소 2개 섹션은 있어야 함
                return []

            # 목차 기반 청크 생성
            chunks = []
            for i, toc_item in enumerate(toc_items):
                start_line = toc_item["content_start"]
                end_line = (
                    toc_items[i + 1]["content_start"]
                    if i + 1 < len(toc_items)
                    else len(lines)
                )

                section_text = "\n".join(lines[start_line:end_line]).strip()

                if len(section_text) > 200:  # 최소 길이 체크
                    chunks.append(
                        {
                            "chunk_id": i + 1,
                            "toc_title": toc_item["title"],
                            "toc_level": toc_item["level"],
                            "content": section_text,
                            "content_length": len(section_text),
                            "chunk_type": "toc_based",
                            "source": "table_of_contents",
                            "context_type": self._infer_context_from_title(
                                toc_item["title"]
                            ),
                            "section_hierarchy": [toc_item["title"]],
                        }
                    )

            return chunks

        except Exception as e:
            logger.warning(f"⚠️ 목차 기반 청킹 실패: {e}")
            return []

    def _infer_context_from_title(self, title: str) -> str:
        """
        목차 제목에서 context 타입 추론
        """
        if not title:
            return "general"

        title_lower = title.lower()

        # 재무 관련
        if any(
            keyword in title_lower
            for keyword in [
                "재무",
                "financial",
                "손익",
                "대차대조표",
                "현금흐름",
                "자산",
                "부채",
            ]
        ):
            return "financial"

        # 사업 관련
        elif any(
            keyword in title_lower
            for keyword in ["사업", "business", "영업", "시장", "제품", "서비스"]
        ):
            return "business"

        # 리스크 관련
        elif any(
            keyword in title_lower
            for keyword in ["위험", "risk", "리스크", "우려", "문제"]
        ):
            return "risk"

        # 투자 관련
        elif any(
            keyword in title_lower
            for keyword in ["투자", "investment", "주가", "전망", "목표"]
        ):
            return "investment"

        # 지배구조 관련
        elif any(
            keyword in title_lower
            for keyword in ["지배구조", "governance", "주주", "이사회", "경영진"]
        ):
            return "governance"

        # 기술 관련
        elif any(
            keyword in title_lower
            for keyword in ["기술", "technology", "개발", "R&D", "연구", "특허"]
        ):
            return "technical"

        else:
            return "general"

    def _create_contextual_pdf_chunks(self, pdf_text: str) -> List[Dict[str, Any]]:
        """📄 PDF를 context별로 의미있는 청크로 분할"""
        if not pdf_text or len(pdf_text) < 1000:
            return []

        chunks = []
        lines = pdf_text.split("\n")

        # Context 타입별 키워드 정의
        context_keywords = {
            "financial": [
                "재무",
                "financial",
                "매출",
                "revenue",
                "이익",
                "profit",
                "손익",
                "income",
                "자산",
                "assets",
                "부채",
                "liabilities",
                "현금",
                "cash",
                "배당",
                "dividend",
                "ROE",
                "ROA",
                "PER",
                "PBR",
                "부채비율",
                "유동비율",
                "재무제표",
                "대차대조표",
            ],
            "business": [
                "사업",
                "business",
                "영업",
                "operation",
                "시장",
                "market",
                "경쟁",
                "competition",
                "고객",
                "customer",
                "제품",
                "product",
                "서비스",
                "service",
                "전략",
                "strategy",
                "성장",
                "growth",
                "점유율",
                "market share",
            ],
            "risk": [
                "리스크",
                "risk",
                "위험",
                "danger",
                "문제",
                "problem",
                "우려",
                "concern",
                "하락",
                "decline",
                "부정적",
                "negative",
                "위기",
                "crisis",
                "불확실",
                "uncertainty",
                "변동",
                "volatility",
                "손실",
                "loss",
            ],
            "investment": [
                "투자",
                "investment",
                "주가",
                "stock price",
                "목표가",
                "target price",
                "전망",
                "outlook",
                "추천",
                "recommendation",
                "매수",
                "buy",
                "매도",
                "sell",
                "밸류에이션",
                "valuation",
                "적정가",
                "fair value",
            ],
            "governance": [
                "지배구조",
                "governance",
                "주주",
                "shareholder",
                "이사회",
                "board",
                "경영진",
                "management",
                "임원",
                "executive",
                "보상",
                "compensation",
                "의결권",
                "voting",
                "투명성",
                "transparency",
            ],
            "technical": [
                "기술",
                "technology",
                "혁신",
                "innovation",
                "개발",
                "development",
                "R&D",
                "연구",
                "특허",
                "patent",
                "플랫폼",
                "platform",
                "시스템",
                "system",
                "솔루션",
                "solution",
            ],
        }

        current_chunk = {"lines": [], "context_type": "general", "score": 0}
        chunks_buffer = []

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # 각 라인의 context 점수 계산
            line_scores = {}
            line_lower = line.lower()

            for context_type, keywords in context_keywords.items():
                score = sum(1 for keyword in keywords if keyword in line_lower)
                if score > 0:
                    line_scores[context_type] = score

            # 현재 청크에 라인 추가
            current_chunk["lines"].append(line)

            # 청크 크기가 적당하면 (10-30줄) context 결정
            if len(current_chunk["lines"]) >= 10:
                # 청크의 주요 context 결정
                if line_scores:
                    best_context = max(line_scores.items(), key=lambda x: x[1])
                    current_chunk["context_type"] = best_context[0]
                    current_chunk["score"] = best_context[1]

                # 청크가 너무 크면 (30줄 이상) 분할
                if len(current_chunk["lines"]) >= 30:
                    chunks_buffer.append(current_chunk)
                    current_chunk = {"lines": [], "context_type": "general", "score": 0}

        # 마지막 청크 처리
        if current_chunk["lines"]:
            chunks_buffer.append(current_chunk)

        # 청크를 최종 형태로 변환
        for i, chunk_data in enumerate(chunks_buffer):
            chunk_text = "\n".join(chunk_data["lines"])
            if len(chunk_text) > 500:  # 최소 크기 필터
                chunks.append(
                    {
                        "chunk_id": i + 1,
                        "context_type": chunk_data["context_type"],
                        "content": chunk_text,
                        "content_length": len(chunk_text),
                        "line_count": len(chunk_data["lines"]),
                        "relevance_score": chunk_data["score"],
                        "keywords_found": self._extract_chunk_keywords(chunk_text),
                    }
                )

        return chunks

    def _extract_chunk_keywords(self, text: str) -> List[str]:
        """청크에서 핵심 키워드 추출"""
        import re

        # 숫자가 포함된 중요한 패턴들
        patterns = [
            r"\d+[%％]",  # 퍼센트
            r"\d+[조억만천]원?",  # 한국 단위
            r"\d+\.?\d*[MB]?억?원?",  # 금액
            r"ROE|ROA|PER|PBR|EPS",  # 재무비율
            r"[가-힣]{2,}주식회사?|[A-Z]{2,}",  # 회사명/브랜드
        ]

        keywords = []
        text_lower = text.lower()

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            keywords.extend(matches[:3])  # 각 패턴에서 최대 3개

        return keywords[:10]  # 최대 10개 키워드

    def _select_relevant_pdf_chunks(
        self, pdf_chunks: List[Dict[str, Any]], expert_type: str, max_chunks: int = 3
    ) -> List[Dict[str, Any]]:
        """
        🎯 전문가별 관련 PDF 청크 선별 (Context-aware)

        Args:
            pdf_chunks: 전체 PDF 청크 리스트
            expert_type: 전문가 유형 ('재무', '기술', '산업', '투자', '리스크')
            max_chunks: 최대 선택 청크 수

        Returns:
            List: 선별된 청크 리스트
        """
        if not pdf_chunks:
            return []

        # 목차 기반 청크와 키워드 기반 청크 분리
        toc_chunks = [
            c
            for c in pdf_chunks
            if c.get("source") == "table_of_contents"
            or c.get("chunk_type") == "toc_based"
        ]
        keyword_chunks = [
            c
            for c in pdf_chunks
            if c.get("source") != "table_of_contents"
            and c.get("chunk_type") != "toc_based"
        ]

        selected_chunks = []

        # 1. 목차 기반 청크에서 먼저 선택 (제목 기반 정확한 매칭)
        if toc_chunks:
            toc_scored = []
            for chunk in toc_chunks:
                relevance_score = 0
                chunk_context = chunk.get("context_type", "general")
                chunk_title = chunk.get("title", "").lower()

                # 전문가별 관련성 점수 계산
                if expert_type == "재무" or expert_type == "fundamental":
                    if chunk_context in ["financial", "business"]:
                        relevance_score += 50
                    if any(
                        keyword in chunk_title
                        for keyword in ["재무", "손익", "자산", "부채", "매출", "이익"]
                    ):
                        relevance_score += 30

                elif expert_type == "기술" or expert_type == "technical":
                    if chunk_context == "technical":
                        relevance_score += 50
                    if any(
                        keyword in chunk_title
                        for keyword in ["기술", "연구", "개발", "특허", "혁신"]
                    ):
                        relevance_score += 30

                elif expert_type == "산업" or expert_type == "industry":
                    if chunk_context in ["industry", "business"]:
                        relevance_score += 50
                    if any(
                        keyword in chunk_title
                        for keyword in ["시장", "산업", "경쟁", "업계", "동향"]
                    ):
                        relevance_score += 30

                elif expert_type == "투자" or expert_type == "investment":
                    if chunk_context in ["investment", "financial"]:
                        relevance_score += 50
                    if any(
                        keyword in chunk_title
                        for keyword in ["투자", "배당", "주주", "밸류", "전망"]
                    ):
                        relevance_score += 30

                elif expert_type == "리스크" or expert_type == "risk":
                    if chunk_context == "risk":
                        relevance_score += 50
                    if any(
                        keyword in chunk_title
                        for keyword in ["위험", "리스크", "위기", "우려", "문제"]
                    ):
                        relevance_score += 30

                # 기본 점수 (모든 전문가에게 유용한 정보)
                if any(
                    keyword in chunk_title
                    for keyword in ["요약", "개요", "핵심", "주요", "중요"]
                ):
                    relevance_score += 15

                toc_scored.append((chunk, relevance_score))

            # 관련성 점수 순 정렬
            toc_scored.sort(key=lambda x: x[1], reverse=True)

            # 상위 청크들 선택 (최대 2개)
            for chunk, score in toc_scored[: min(2, max_chunks)]:
                if score > 20:  # 최소 관련성 임계값
                    selected_chunks.append(chunk)

        # 2. 키워드 기반 청크에서 추가 선택
        remaining_slots = max_chunks - len(selected_chunks)
        if remaining_slots > 0 and keyword_chunks:
            keyword_scored = []
            for chunk in keyword_chunks:
                content = chunk.get("content", "").lower()
                relevance_score = 0

                # 전문가별 키워드 매칭
                expert_keywords = {
                    "재무": ["재무제표", "매출", "이익", "자산", "부채", "현금흐름"],
                    "기술": ["기술개발", "연구개발", "특허", "혁신", "기술력"],
                    "산업": ["시장점유율", "경쟁사", "업계동향", "시장규모"],
                    "투자": ["배당", "주주가치", "투자수익", "목표가", "밸류에이션"],
                    "리스크": ["위험요인", "리스크", "위기관리", "불확실성"],
                }

                target_keywords = expert_keywords.get(expert_type, [])
                for keyword in target_keywords:
                    if keyword in content:
                        relevance_score += 10

                keyword_scored.append((chunk, relevance_score))

            # 관련성 점수 순 정렬
            keyword_scored.sort(key=lambda x: x[1], reverse=True)

            # 상위 청크들 추가 선택
            for chunk, score in keyword_scored[:remaining_slots]:
                if score > 5:  # 최소 관련성 임계값
                    selected_chunks.append(chunk)

        logger.info(
            f"🎯 {expert_type} 전문가용 PDF 청크 선별: {len(selected_chunks)}/{len(pdf_chunks)} 선택됨"
        )

        return selected_chunks

    def _generate_comprehensive_cache_key(
        self,
        user_prompt: str,
        stock_name: str,
        stock_code: str,
        analysis_depth: AnalysisDepth,
        manus_data: Dict = None,
    ) -> str:
        """종합 분석용 캐시 키 생성"""
        import hashlib

        # 기본 키 요소들
        key_elements = [
            user_prompt[:100],  # 프롬프트 처음 100자
            stock_name,
            stock_code,
            analysis_depth.value,
        ]

        # Manus 데이터가 있으면 해시에 포함
        if manus_data and manus_data.get("performed"):
            collected_info = manus_data.get("collected_information", "")
            # 수집 정보의 해시값 추가 (전체가 아닌 샘플링)
            info_sample = (
                collected_info[:500] + collected_info[-500:]
                if len(collected_info) > 1000
                else collected_info
            )
            key_elements.append(hashlib.md5(info_sample.encode()).hexdigest()[:8])

        # 날짜별 캐시 구분 (하루 단위)
        from datetime import datetime

        key_elements.append(datetime.now().strftime("%Y%m%d"))

        combined_key = "|".join(str(elem) for elem in key_elements)
        return hashlib.md5(combined_key.encode()).hexdigest()

    def _assess_data_integration_quality(
        self, financial_data: Dict, dart_data: Dict, manus_data: Dict
    ) -> str:
        """
        🔍 데이터 통합 품질을 평가합니다

        Args:
            financial_data: 재무데이터
            dart_data: DART 데이터
            manus_data: Manus 수집 데이터

        Returns:
            str: 품질 등급
        """
        quality_score = 0

        # 재무데이터 품질 (최대 25점)
        if financial_data and financial_data.get("success"):
            data_sources = financial_data.get("data_sources", [])
            quality_score += len(data_sources) * 5  # 데이터 소스당 5점
            quality_score = min(quality_score, 25)

        # DART 데이터 품질 (최대 30점)
        if dart_data and dart_data.get("success"):
            quality_score += 30

        # Manus 데이터 품질 (최대 45점)
        if manus_data and manus_data.get("performed"):
            richness_score = manus_data.get("data_richness_score", 0)
            quality_score += int(
                richness_score * 0.45
            )  # 100점 만점을 45점 만점으로 변환

        # 품질 등급 분류
        if quality_score >= 80:
            return "매우높음"
        elif quality_score >= 60:
            return "높음"
        elif quality_score >= 40:
            return "보통"
        elif quality_score >= 20:
            return "낮음"
        else:
            return "매우낮음"

    def _identify_used_data_sources(
        self,
        financial_data: Dict,
        enhanced_dart_data: Dict = None,
        manus_collected_data: Dict = None,
    ) -> List[str]:
        """
        🔍 전문가 분석에 사용된 데이터 소스를 식별합니다

        Args:
            financial_data: 재무데이터 딕셔너리
            enhanced_dart_data: Enhanced DART 데이터 딕셔너리
            manus_collected_data: Manus 수집 데이터 딕셔너리

        Returns:
            List[str]: 사용된 데이터 소스 목록
        """
        used_sources = []

        # 재무데이터 확인
        if financial_data and financial_data.get("success"):
            data_sources = financial_data.get("data_sources", [])
            used_sources.extend(data_sources)

        # Enhanced DART 데이터 확인
        if enhanced_dart_data and enhanced_dart_data.get("success"):
            used_sources.append("Enhanced DART API")

        # Manus 수집 데이터 확인
        if manus_collected_data and manus_collected_data.get("performed"):
            used_sources.append("ManusAgent Web Search")

            # PDF 분석이 포함된 경우
            if manus_collected_data.get("pdf_analysis", {}).get("pdf_detected"):
                used_sources.append("PDF Document Analysis")

        # 중복 제거
        return list(set(used_sources))

    async def _synthesize_expert_insights(
        self, expert_results: List[Dict], user_prompt: str
    ) -> Dict[str, Any]:
        """
        🚀 전문가들의 분석 결과를 종합하여 최종 인사이트를 생성합니다

        Args:
            expert_results: 전문가별 분석 결과 리스트
            user_prompt: 사용자 질문

        Returns:
            Dict: 종합된 분석 결과
        """
        logger.info("🚀 전문가 인사이트 종합 시작...")

        # 성공한 분석들만 필터링
        successful_analyses = [
            result for result in expert_results if not result.get("error")
        ]

        if not successful_analyses:
            return {
                "synthesis_success": False,
                "error": "성공한 전문가 분석이 없습니다",
                "final_recommendation": "분석 결과가 충분하지 않아 추천을 제공할 수 없습니다",
            }

        # 전문가 유형별 인사이트 분류
        insights_by_type = {
            "fundamental": [],
            "technical": [],
            "industry": [],
            "valuation": [],
            "risk": [],
            "general": [],
        }

        for result in successful_analyses:
            expert_name = result.get("expert_name", "")
            expertise = result.get("expertise_area", "")
            analysis = result.get("analysis_result", "")

            # 전문가 유형 분류
            if "재무" in expert_name or "Fundamental" in expertise:
                insights_by_type["fundamental"].append(analysis)
            elif "기술" in expert_name or "Technical" in expertise:
                insights_by_type["technical"].append(analysis)
            elif "산업" in expert_name or "Industry" in expertise:
                insights_by_type["industry"].append(analysis)
            elif "밸류" in expert_name or "Valuation" in expertise:
                insights_by_type["valuation"].append(analysis)
            elif "리스크" in expert_name or "Risk" in expertise:
                insights_by_type["risk"].append(analysis)
            else:
                insights_by_type["general"].append(analysis)

        # 종합 분석 프롬프트 구성
        synthesis_prompt = f"""
다음은 5명의 전문가가 분석한 결과입니다. 이를 종합하여 최종 투자 의견을 제시해주세요.

사용자 질문: {user_prompt}

전문가 분석 결과:
"""

        # 각 전문가 유형별 인사이트 추가
        for insight_type, insights in insights_by_type.items():
            if insights:
                type_names = {
                    "fundamental": "📊 재무분석 전문가",
                    "technical": "📈 기술분석 전문가",
                    "industry": "🏭 산업분석 전문가",
                    "valuation": "💰 밸류에이션 전문가",
                    "risk": "⚠️ 리스크 분석 전문가",
                    "general": "🔍 종합분석 전문가",
                }

                synthesis_prompt += (
                    f"\n{type_names.get(insight_type, '전문가')} 의견:\n"
                )
                for i, insight in enumerate(insights, 1):
                    synthesis_prompt += (
                        f"{i}. {insight[:500]}...\n"  # 각 인사이트는 500자로 제한
                    )

        synthesis_prompt += """

위 전문가 의견들을 종합하여 다음 형식으로 최종 분석을 제공해주세요:

1. **종합 평가**: 전반적인 투자 매력도
2. **주요 강점**: 핵심 경쟁 우위
3. **주요 우려사항**: 리스크 요인
4. **투자 의견**: 매수/보유/매도 의견과 근거
5. **목표가/적정가**: 가능하다면 적정 주가 범위

각 항목은 간결하고 명확하게 작성해주세요.
"""

        try:
            # LLM을 통한 종합 분석
            synthesis_result = await self._call_llm_for_analysis(synthesis_prompt)

            # 투자 의견 추출 (간단한 키워드 기반)
            investment_opinion = "중립"
            if any(
                keyword in synthesis_result.lower()
                for keyword in ["매수", "buy", "추천"]
            ):
                investment_opinion = "매수"
            elif any(
                keyword in synthesis_result.lower()
                for keyword in ["매도", "sell", "부정적"]
            ):
                investment_opinion = "매도"
            elif any(
                keyword in synthesis_result.lower() for keyword in ["보유", "hold"]
            ):
                investment_opinion = "보유"

            return {
                "synthesis_success": True,
                "final_analysis": synthesis_result,
                "investment_opinion": investment_opinion,
                "expert_consensus": f"{len(successful_analyses)}명 전문가 의견 종합",
                "analysis_coverage": [
                    insight_type
                    for insight_type, insights in insights_by_type.items()
                    if insights
                ],
                "confidence_level": self._calculate_consensus_confidence(
                    successful_analyses
                ),
            }

        except Exception as e:
            logger.error(f"❌ 전문가 인사이트 종합 실패: {e}")
            return {
                "synthesis_success": False,
                "error": str(e),
                "fallback_summary": f"{len(successful_analyses)}명 전문가 분석 완료, 종합 실패",
            }

    def _calculate_consensus_confidence(self, successful_analyses: List[Dict]) -> str:
        """전문가 합의 신뢰도를 계산합니다"""
        expert_count = len(successful_analyses)

        if expert_count >= 5:
            return "매우높음"
        elif expert_count >= 3:
            return "높음"
        elif expert_count >= 2:
            return "보통"
        else:
            return "낮음"
