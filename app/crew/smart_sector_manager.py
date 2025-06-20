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

            # 🔢 토큰 최적화 (새로운 기능!)
            logger.info("🔢 토큰 최적화 시작...")
            optimization_result = self._optimize_data_for_token_limit(
                financial_data=financial_data,
                enhanced_dart_data=enhanced_dart_data,
                manus_collected_data=manus_collected_data,
            )

            # 최적화된 데이터 사용
            optimized_financial = optimization_result["financial_data"]
            optimized_dart = optimization_result["enhanced_dart_data"]
            optimized_manus = optimization_result["manus_collected_data"]

            if optimization_result["optimization_applied"]:
                logger.info("🎯 토큰 최적화 적용됨")
                original_tokens = optimization_result["original_token_estimate"]
                optimized_tokens = optimization_result["optimized_token_estimate"]
                logger.info(
                    f"📊 토큰 최적화: {original_tokens:,} → {optimized_tokens:,}"
                )
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

    def _identify_used_data_sources(
        self,
        financial_data: Dict,
        enhanced_dart_data: Dict = None,
        manus_collected_data: Dict = None,
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
        if manus_collected_data.get("pdf_analysis", {}).get("pdf_detected"):
            used_sources.append("PDF_Analysis")

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

위 전문가들의 분석을 종합하여 다음과 같이 정리해주세요:

1. **핵심 투자 포인트** (3-5개)
2. **주요 리스크 요인** (3-5개)
3. **종합 투자 의견** (매수/보유/매도 + 근거)
4. **목표가 또는 적정가 제시** (가능한 경우)
5. **전문가 의견 일치도** (높음/보통/낮음 + 이유)

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
            # 주석 전문가 특별 처리
            if "주석" in expert.name or "Footnote" in expert.role:
                footnote_sections = pdf_interface.get_sections_by_expert_type(
                    "footnote_specialist"
                )
                if footnote_sections:
                    context_parts.append("📄 **재무제표 주석 섹션 (PDF 완전 분석)**:")
                    section_count = 0
                    total_content_length = 0

                    for section_title, content in footnote_sections.items():
                        # 🚀 주석 전문가는 섹션 제한 없음! 모든 주석 섹션 완전 분석
                        if len(content) > 600000:  # 개별 섹션 60만자 제한으로 확대
                            content = (
                                content[:600000]
                                + "\n...[주석 내용 일부 생략 - 매우 긴 섹션]..."
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
                        if len(content) > 600000:  # 개별 섹션 60만자 제한으로 확대
                            content = (
                                content[:600000]
                                + "\n...[내용 일부 생략 - 매우 긴 섹션]..."
                            )

                        context_parts.append(f"### {section_title}")
                        context_parts.append(content)
                        context_parts.append("")
                        section_count += 1
                        total_content_length += len(content)

                logger.info(
                    f"📄 {expert.name}: {section_count}개 섹션, 총 {total_content_length:,}자 (제한 없음)"
                )

        # 전문가별 추가 데이터 선별 (기존 로직 유지)
        if "재무" in expert.expertise or "Fundamental" in expert.role:
            # 재무 분석 전문가 - 재무데이터 중심
            if financial_data and financial_data.get("success"):
                financial_summary = self._summarize_financial_data(financial_data)
                context_parts.append("📊 재무데이터:")
                context_parts.append(financial_summary)

            if enhanced_dart_data and enhanced_dart_data.get("success"):
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

            if manus_collected_data and manus_collected_data.get("performed"):
                technical_info = self._extract_technical_analysis_info(
                    manus_collected_data
                )
                if technical_info:
                    context_parts.append("🔍 기술분석 관련 정보:")
                    context_parts.append(technical_info)

        # 기타 전문가별 데이터 처리
        if "산업" in expert.expertise or "Industry" in expert.role:
            # 산업 분석 전문가 - 산업 동향 중심
            if manus_collected_data and manus_collected_data.get("performed"):
                industry_info = self._extract_industry_info(manus_collected_data)
                if industry_info:
                    context_parts.append("🏭 산업 동향 정보:")
                    context_parts.append(industry_info)

        elif "밸류" in expert.expertise or "Valuation" in expert.role:
            # 밸류에이션 전문가 - 가치평가 데이터 중심
            if financial_data and financial_data.get("success"):
                valuation_data = self._extract_valuation_data(financial_data)
                if valuation_data:
                    context_parts.append("💰 밸류에이션 데이터:")
                    context_parts.append(valuation_data)

        elif "리스크" in expert.expertise or "Risk" in expert.role:
            # 리스크 평가자 - 위험 요소 중심
            if financial_data and financial_data.get("success"):
                risk_indicators = self._extract_risk_indicators(financial_data)
                if risk_indicators:
                    context_parts.append("⚠️ 리스크 지표:")
                    context_parts.append(risk_indicators)

            if manus_collected_data and manus_collected_data.get("performed"):
                risk_factors = self._extract_risk_factors(manus_collected_data)
                if risk_factors:
                    context_parts.append("🚨 시장 리스크 요소:")
                    context_parts.append(risk_factors)

        final_context = "\n\n".join(context_parts)

        # 토큰 수 확인 및 로깅
        estimated_tokens = self._estimate_tokens(final_context)
        logger.info(
            f"🎯 {expert.name} 통합 컨텍스트: {estimated_tokens:,} 토큰 (PDF 딕셔너리 완전 활용)"
        )

        return final_context

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

        # Dict 타입인 경우 문자열로 변환
        if isinstance(dart_data, dict):
            dart_text = json.dumps(dart_data, ensure_ascii=False, indent=2)
        else:
            dart_text = str(dart_data)

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
            if any(keyword.lower() in line.lower() for keyword in financial_keywords):
                relevant_lines.append(line)

        return "\n".join(relevant_lines) if relevant_lines else ""

    def _extract_price_data_only(self, financial_data) -> str:
        """재무데이터에서 가격/차트 관련 정보만 추출합니다."""
        if not financial_data:
            return ""

        # Dict 타입인 경우 문자열로 변환
        if isinstance(financial_data, dict):
            financial_text = json.dumps(financial_data, ensure_ascii=False, indent=2)
        else:
            financial_text = str(financial_data)

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

    def _extract_technical_analysis_info(self, manus_data) -> str:
        """Manus 데이터에서 기술적 분석 관련 정보만 추출합니다."""
        if not manus_data:
            return ""

        # Dict 타입인 경우 문자열로 변환
        if isinstance(manus_data, dict):
            if manus_data.get("collected_information"):
                manus_text = str(manus_data["collected_information"])
            else:
                manus_text = json.dumps(manus_data, ensure_ascii=False, indent=2)
        else:
            manus_text = str(manus_data)

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
            if any(keyword.lower() in line.lower() for keyword in technical_keywords):
                relevant_lines.append(line)

        return "\n".join(relevant_lines) if relevant_lines else ""

    def _extract_industry_info(self, manus_data) -> str:
        """Manus 데이터에서 산업/경쟁사 관련 정보만 추출합니다."""
        if not manus_data:
            return ""

        # Dict 타입인 경우 문자열로 변환
        if isinstance(manus_data, dict):
            if manus_data.get("collected_information"):
                manus_text = str(manus_data["collected_information"])
            else:
                manus_text = json.dumps(manus_data, ensure_ascii=False, indent=2)
        else:
            manus_text = str(manus_data)

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
            if any(keyword.lower() in line.lower() for keyword in industry_keywords):
                relevant_lines.append(line)

        return "\n".join(relevant_lines) if relevant_lines else ""

    def _extract_risk_factors(self, manus_data) -> str:
        """Manus 데이터에서 리스크 요인 관련 정보만 추출합니다."""
        if not manus_data:
            return ""

        # Dict 타입인 경우 문자열로 변환
        if isinstance(manus_data, dict):
            if manus_data.get("collected_information"):
                manus_text = str(manus_data["collected_information"])
            else:
                manus_text = json.dumps(manus_data, ensure_ascii=False, indent=2)
        else:
            manus_text = str(manus_data)

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

    def _extract_key_insights_only(self, manus_data: str) -> str:
        """Manus 데이터에서 핵심 인사이트만 추출합니다."""
        if not manus_data:
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

        lines = manus_data.split("\n")
        relevant_lines = []

        for line in lines:
            if any(keyword.lower() in line.lower() for keyword in insight_keywords):
                relevant_lines.append(line)

        return "\n".join(relevant_lines) if relevant_lines else ""

    def _extract_valuation_data(self, financial_data) -> str:
        """재무데이터에서 밸류에이션 관련 정보만 추출합니다."""
        if not financial_data:
            return ""

        # Dict 타입인 경우 문자열로 변환
        if isinstance(financial_data, dict):
            financial_text = json.dumps(financial_data, ensure_ascii=False, indent=2)
        else:
            financial_text = str(financial_data)

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
            if any(keyword.lower() in line.lower() for keyword in valuation_keywords):
                relevant_lines.append(line)

        return "\n".join(relevant_lines) if relevant_lines else ""

    def _extract_risk_indicators(self, financial_data) -> str:
        """재무데이터에서 리스크 지표만 추출합니다."""
        if not financial_data:
            return ""

        # Dict 타입인 경우 문자열로 변환
        if isinstance(financial_data, dict):
            financial_text = json.dumps(financial_data, ensure_ascii=False, indent=2)
        else:
            financial_text = str(financial_data)

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

    def _extract_dart_business_info(self, dart_data: str) -> str:
        """DART 데이터에서 사업 관련 정보만 추출합니다."""
        if not dart_data:
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

        lines = dart_data.split("\n")
        relevant_lines = []

        for line in lines:
            if any(keyword.lower() in line.lower() for keyword in business_keywords):
                relevant_lines.append(line)

        return "\n".join(relevant_lines) if relevant_lines else ""

    def _extract_dart_investment_info(self, dart_data: str) -> str:
        """DART 데이터에서 투자 관련 정보만 추출합니다."""
        if not dart_data:
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

        lines = dart_data.split("\n")
        relevant_lines = []

        for line in lines:
            if any(keyword.lower() in line.lower() for keyword in investment_keywords):
                relevant_lines.append(line)

        return "\n".join(relevant_lines) if relevant_lines else ""

    def _create_basic_financial_summary(self, financial_data: str) -> str:
        """재무데이터의 기본 요약을 생성합니다."""
        if not financial_data:
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

        lines = financial_data.split("\n")
        summary_lines = []

        for line in lines:
            if any(metric in line for metric in key_metrics):
                summary_lines.append(line)

        return "\n".join(summary_lines) if summary_lines else financial_data[:1000]

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

    def _optimize_data_for_token_limit(
        self,
        financial_data: Dict,
        enhanced_dart_data: Dict = None,
        manus_collected_data: Dict = None,
        target_token_limit: int = 100000,
    ) -> Dict[str, Any]:
        """
        🎯 토큰 제한에 맞춰 데이터를 최적화합니다.

        Args:
            financial_data: 재무 데이터
            enhanced_dart_data: Enhanced DART 데이터
            manus_collected_data: Manus 수집 데이터
            target_token_limit: 목표 토큰 제한

        Returns:
            Dict: 최적화된 데이터
        """
        logger.info(f"🔢 토큰 최적화 시작 - 목표: {target_token_limit:,} 토큰")

        optimized_data = {
            "financial_data": financial_data,
            "enhanced_dart_data": enhanced_dart_data,
            "manus_collected_data": manus_collected_data,
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

                optimized_data["optimization_applied"] = True

                # 최적화 후 토큰 수 재계산
                optimized_tokens = 0
                for key in [
                    "financial_data",
                    "enhanced_dart_data",
                    "manus_collected_data",
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
