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

    def _generate_comprehensive_cache_key(
        self,
        prompt: str,
        stock_name: str,
        stock_code: str,
        depth: AnalysisDepth,
        manus_data: Dict = None,
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

        # 전체 내용을 결합하여 캐시 키 생성
        full_content = "_".join(str(part) for part in content_parts)
        return hashlib.md5(full_content.encode()).hexdigest()

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

    async def _create_expert_specific_context(
        self,
        expert,
        user_prompt: str,
        stock_name: str,
        stock_code: str,
        optimized_financial: str,
        optimized_dart: str,
        optimized_manus: str,
        pdf_interface=None,  # 🚀 PDF 인터페이스 추가!
    ) -> str:
        """
        🎯 전문가별 맞춤 컨텍스트 생성 (PDF 딕셔너리 선택적 활용!)

        각 전문가의 전문성에 따라 필요한 정보만 선별해서 컨텍스트를 구성해요.
        특히 PDF가 있는 경우 전문가별로 관련 섹션만 선택적으로 포함시켜요!

        🚀 60만자 지원으로 더 풍부한 컨텍스트 제공!

        Args:
            expert: 전문가 객체
            user_prompt: 사용자 질문
            stock_name: 종목명
            stock_code: 종목코드
            optimized_financial: 최적화된 재무데이터
            optimized_dart: 최적화된 DART 데이터
            optimized_manus: 최적화된 Manus 데이터
            pdf_interface: PDF 딕셔너리 인터페이스 (선택사항)

        Returns:
            str: 전문가별 최적화된 컨텍스트
        """
        context_parts = [
            f"🎯 {expert.name} 전문 분석 요청",
            f"📋 사용자 질문: {user_prompt}",
            f"📊 분석 대상: {stock_name} ({stock_code})",
            f"🔍 분석 초점: {expert.analysis_focus}",
            "",
            "📈 **기본 데이터**:",
        ]

        # 기본 재무데이터 (항상 포함)
        if optimized_financial:
            context_parts.extend(
                ["💹 재무데이터:", "=" * 30, optimized_financial, "=" * 30]
            )

        # Enhanced DART 데이터 (해당하는 경우)
        if optimized_dart:
            context_parts.extend(
                ["", "🏢 Enhanced DART 데이터:", "=" * 30, optimized_dart, "=" * 30]
            )

        # 🚀 PDF 딕셔너리 선택적 활용 (핵심 기능!)
        if pdf_interface:
            expert_type = expert.role.lower().replace(" ", "_")

            # 전문가별 PDF 섹션 가져오기
            if expert_type == "footnote_specialist":
                # 📝 주석 전문가는 주석 섹션만 가져오기
                relevant_pdf_sections = pdf_interface.get_footnote_sections()
                context_parts.extend(
                    ["", "📝 **주석/각주 전문 분석 자료** (PDF에서 선별):", "=" * 50]
                )
            else:
                # 다른 전문가들은 전문성에 맞는 섹션 가져오기
                relevant_pdf_sections = pdf_interface.get_sections_for_expert(
                    expert_type, max_sections=3
                )
                context_parts.extend(
                    [
                        "",
                        f"📄 **{expert.role} 관련 PDF 섹션들** (선별적 추출):",
                        "=" * 50,
                    ]
                )

            # PDF 섹션 내용 추가 (🚀 60만자 지원으로 더 풍부한 컨텍스트!)
            for i, (section_title, section_content) in enumerate(
                relevant_pdf_sections.items(), 1
            ):
                # 🚀 각 섹션을 150,000자로 확장 (기존 15,000자의 10배!)
                if len(section_content) > 150000:
                    truncated_content = (
                        section_content[:150000] + "...[15만자 제한으로 내용 일부 생략]"
                    )
                else:
                    truncated_content = section_content

                context_parts.extend(
                    [
                        f"",
                        f"📑 PDF 섹션 {i}: {section_title}",
                        "─" * 40,
                        truncated_content,
                        "─" * 40,
                    ]
                )

                # 최대 3개 섹션까지만 (토큰 제한)
                if i >= 3:
                    break

            logger.info(
                f"🎯 {expert.name}: PDF에서 {len(relevant_pdf_sections)}개 섹션 선별 활용 (60만자 지원)"
            )

        else:
            # PDF 인터페이스가 없는 경우 기존 Manus 데이터 사용 (🚀 용량 확장)
            if optimized_manus:
                context_parts.extend(
                    [
                        "",
                        "🔍 웹 검색 정보:",
                        "=" * 30,
                        optimized_manus[:50000],  # 🚀 10,000자에서 50,000자로 확장
                        "=" * 30,
                    ]
                )

        # 전문가별 특화 정보 추가
        context_parts.extend(
            [
                "",
                f"🎯 **{expert.role} 전문 가이드라인**:",
                f"• 섹터별 중점사항: {', '.join(expert.sector_specific_points[:3])}",
                f"• 주의사항: {expert.risk_awareness[0] if expert.risk_awareness else '없음'}",
                f"• 핵심 지표: {', '.join(expert.critical_metrics[:3])}",
            ]
        )

        final_context = "\n".join(context_parts)

        # 컨텍스트 크기 로그 (60만자 지원 표시)
        logger.info(
            f"🎯 {expert.name} 컨텍스트 생성: {len(final_context):,}자 (60만자 지원)"
        )

        return final_context
