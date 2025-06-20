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

                # 🔧 안전한 컨텍스트 생성
                context = await self._create_expert_specific_context(
                    expert, financial_data, enhanced_dart_data, manus_collected_data
                )

                # 🔧 컨텍스트 타입 검증
                if not isinstance(context, str):
                    logger.warning(
                        f"⚠️ {expert.name} 컨텍스트가 문자열이 아님: {type(context)}"
                    )
                    context = str(context) if context else "컨텍스트 생성 실패"

                # 🎯 시니어 애널리스트급 프롬프트 생성
                prompt = f"""
**전문가**: {expert.name} ({expert.role})
**전문 분야**: {expert.expertise}

{context}

🎯 **시니어 애널리스트 분석 지침**:
위의 데이터를 바탕으로 실제 증권사 시니어 애널리스트 수준의 전문적이고 정량적인 분석을 수행해주세요.

**필수 포함 요소**:
1. 구체적인 수치와 계산 과정
2. 정량적 지표와 기준값 명시
3. 시나리오별 확률과 근거
4. 투자 결정에 직접 활용 가능한 구체적 권고

**분석 품질 기준**:
- 모든 주장에 대한 정량적 근거 제시
- 계산 과정과 전제 조건 명시
- 리스크와 기회요인 균형 분석
- 실무진이 즉시 활용 가능한 구체성

전문가로서의 깊이 있는 인사이트와 실행 가능한 분석을 제공해주세요.
"""

                # 🔧 안전한 프롬프트 검증
                if not prompt or len(prompt.strip()) < 100:
                    raise ValueError(f"{expert.name} 프롬프트가 너무 짧거나 비어있음")

                # LLM 분석 수행
                logger.info(f"🤖 {expert.name} LLM 분석 요청...")

                # 🔧 안전한 LLM 호출
                try:
                    analysis_result = await llm_instance.agenerate(prompt)

                    # 결과 타입 검증
                    if not analysis_result:
                        raise ValueError("LLM 분석 결과가 None 또는 빈 값")

                    # 문자열로 변환 (안전한 처리)
                    if isinstance(analysis_result, str):
                        analysis_text = analysis_result
                    elif hasattr(analysis_result, "content"):
                        analysis_text = str(analysis_result.content)
                    elif hasattr(analysis_result, "text"):
                        analysis_text = str(analysis_result.text)
                    else:
                        analysis_text = str(analysis_result)

                    # 최소 길이 검증
                    if len(analysis_text.strip()) < 50:
                        raise ValueError(
                            f"분석 결과가 너무 짧음: {len(analysis_text)}자"
                        )

                    logger.info(f"✅ {expert.name} 분석 완료: {len(analysis_text):,}자")

                    return {
                        "expert_name": expert.name,
                        "expert_role": expert.role,
                        "expertise": expert.expertise,
                        "analysis_result": analysis_text,
                        "analysis_timestamp": datetime.now().isoformat(),
                        "attempt_number": attempt + 1,
                        "success": True,
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
        }

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

            # 🎯 시니어 펀더멘털 애널리스트 분석 지침 (구체적 산출식 포함)
            context_parts.append("\n🎯 펀더멘털 분석 필수 수행사항:")
            context_parts.append("1. 재무비율 종합분석:")
            context_parts.append(
                "   - ROE = 순이익/평균자기자본 (3년 트렌드와 동종업계 Percentile)"
            )
            context_parts.append(
                "   - DuPont 3단계: ROE = 순이익률 × 자산회전율 × 레버리지"
            )
            context_parts.append("   - ROIC = NOPAT/(차입금+자기자본) vs WACC 비교")
            context_parts.append("   - 유동비율 = 유동자산/유동부채 (안전성 지표)")
            context_parts.append("")
            context_parts.append("2. 현금흐름 정밀분석:")
            context_parts.append("   - FCF = 영업CF - 자본적지출 (3년 평균 산출)")
            context_parts.append("   - FCF Yield = FCF/시가총액 × 100 (%)")
            context_parts.append("   - Cash Conversion Cycle = DIO + DSO - DPO")
            context_parts.append("   - Working Capital 변동이 OCF에 미치는 영향 정량화")
            context_parts.append("")
            context_parts.append("3. 수익성 및 성장성 심화분석:")
            context_parts.append(
                "   - 매출 성장률 = (당기매출-전기매출)/전기매출 × 100"
            )
            context_parts.append("   - 영업레버리지 = 영업이익 증가율/매출 증가율")
            context_parts.append("   - EBITDA 마진 = EBITDA/매출 × 100 (현금창출력)")
            context_parts.append("   - Asset Turnover = 매출/평균총자산 (자산효율성)")
            context_parts.append("")
            context_parts.append("4. 재무건전성 스트레스 테스트:")
            context_parts.append(
                "   - Interest Coverage = EBIT/이자비용 (이자지급능력)"
            )
            context_parts.append("   - Debt Service Coverage = OCF/(원금상환+이자지급)")
            context_parts.append("   - Net Debt/EBITDA 비율 (부채상환 소요연수)")
            context_parts.append("   - 경기침체 시나리오 하에서 부채상환능력 평가")
            context_parts.append("")
            context_parts.append("⚠️ 분석 시 주의사항:")
            context_parts.append("- 모든 비율은 반드시 3년 트렌드로 분석")
            context_parts.append("- 동종업계 상위 25%, 50%, 75% 대비 위치 명시")
            context_parts.append("- 계절성/일회성 요인 제거한 정상화 수치 병기")
            context_parts.append("- 연결재무제표 기준으로 분석 (별도 재무제표 참고)")

        elif "기술" in expert.expertise or "Technical" in expert.role:
            # 기술 분석 전문가 - 🎯 시니어 애널리스트 수준 지침 추가
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

            # 🎯 시니어 기술적 애널리스트 분석 지침 (구체적 계산식 포함)
            context_parts.append("\n🎯 기술적 분석 필수 수행사항:")
            context_parts.append("1. 주요 이동평균선 분석:")
            context_parts.append("   - 5일선 vs 20일선 Golden/Dead Cross 여부와 시점")
            context_parts.append("   - 20일선 vs 60일선 중기 추세 전환 신호")
            context_parts.append("   - 60일선 vs 120일선 장기 추세 방향성")
            context_parts.append("   - 현재가의 이평선 배열 상태 (정배열/역배열/혼재)")
            context_parts.append("")
            context_parts.append("2. 모멘텀 지표 정밀분석:")
            context_parts.append(
                "   - MACD(12,26,9): Signal Line 교차와 히스토그램 변화율"
            )
            context_parts.append(
                "   - RSI(14): 과매수(70이상)/과매도(30이하) 구간과 Divergence"
            )
            context_parts.append("   - Stochastic(%K,%D): 80이상 과매수, 20이하 과매도")
            context_parts.append("   - Williams %R: -20이상 과매수, -80이하 과매도")
            context_parts.append("")
            context_parts.append("3. 지지저항 및 목표가 산출:")
            context_parts.append("   - 주요 지지선/저항선 레벨 식별 (최근 6개월 기준)")
            context_parts.append("   - Fibonacci Retracement: 38.2%, 50%, 61.8% 되돌림")
            context_parts.append(
                "   - 돌파시 목표가 = 저항선 + (저항선-지지선) [측정이론]"
            )
            context_parts.append("   - 하락시 목표가 = 지지선 - (저항선-지지선)")
            context_parts.append("")
            context_parts.append("4. 거래량 및 섹터 분석:")
            context_parts.append(
                "   - 거래량 동반 여부 (20일 평균 대비 150% 이상시 유의미)"
            )
            context_parts.append("   - OBV (On Balance Volume) 추세와 주가 Divergence")
            context_parts.append(
                "   - 섹터 상대강도 = (개별주/섹터지수) / (전일 개별주/전일 섹터지수)"
            )
            context_parts.append("   - 시장 대비 Beta 계수와 변동성 비교")
            context_parts.append("")
            context_parts.append("⚠️ 기술적 분석 주의사항:")
            context_parts.append("- 모든 신호는 거래량 동반 여부 필수 확인")
            context_parts.append(
                "- False Breakout 가능성 (저항선 돌파 후 3일 지속성 관찰)"
            )
            context_parts.append("- 공시나 이벤트 전후 기술적 신호 신뢰도 하락")
            context_parts.append(
                "- 단기(1주), 중기(1개월), 장기(3개월) 시계열 종합 판단"
            )

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

            # 🎯 시니어 산업 애널리스트 분석 지침 (정량적 지표 포함)
            context_parts.append("\n🎯 산업 분석 필수 수행사항:")
            context_parts.append("1. Porter 5 Forces 정량평가:")
            context_parts.append(
                "   - 신규진입 위협도 (1-5점): 진입장벽, 자본요구, 규제환경"
            )
            context_parts.append(
                "   - 공급업체 교섭력 (1-5점): 공급업체 집중도, 전환비용"
            )
            context_parts.append("   - 구매자 교섭력 (1-5점): 고객 집중도, 가격민감도")
            context_parts.append(
                "   - 대체재 위협도 (1-5점): 대체재 성능-가격, 전환 가능성"
            )
            context_parts.append(
                "   - 기존 경쟁강도 (1-5점): 경쟁사 수, 시장성장률, 차별화"
            )
            context_parts.append("   - 종합 점수 = 각 Force별 점수 합계 (최대 25점)")
            context_parts.append("")
            context_parts.append("2. 시장구조 분석:")
            context_parts.append("   - HHI 지수 = Σ(시장점유율%)² (독과점 정도 측정)")
            context_parts.append("   - Top 3 집중도 = 상위 3사 시장점유율 합계")
            context_parts.append(
                "   - 시장 성장률 = (당기 시장규모 - 전기) / 전기 × 100"
            )
            context_parts.append(
                "   - 시장 포화도 = 현재 시장규모 / 잠재 시장규모 × 100"
            )
            context_parts.append("")
            context_parts.append("3. 경쟁우위 지속성 (Economic Moat):")
            context_parts.append("   - 네트워크 효과: 사용자 증가 → 가치 증가 선순환")
            context_parts.append("   - 전환비용: 고객이 타사로 변경시 발생 비용")
            context_parts.append("   - 무형자산: 브랜드, 특허, 라이선스 가치")
            context_parts.append("   - 비용우위: 규모의 경제, 독점적 자원")
            context_parts.append("   - R&D 집약도 = R&D비용 / 매출 × 100 (%)")
            context_parts.append("")
            context_parts.append("4. 산업 라이프사이클 진단:")
            context_parts.append(
                "   - 도입기: 높은 성장률(30%+), 높은 변동성, 적자 가능"
            )
            context_parts.append("   - 성장기: 중간 성장률(10-30%), 수익성 개선")
            context_parts.append("   - 성숙기: 낮은 성장률(5-10%), 안정적 수익성")
            context_parts.append("   - 쇠퇴기: 마이너스 성장률, 구조조정 필요")
            context_parts.append("")
            context_parts.append("⚠️ 산업 분석 주의사항:")
            context_parts.append("- 글로벌 vs 국내 시장 분리 분석")
            context_parts.append("- 정부 정책 변화가 산업에 미치는 영향도 정량화")
            context_parts.append("- 기술 혁신 주기와 산업 내 위치 매핑")
            context_parts.append("- ESG 규제 강화가 산업 구조에 미치는 영향")

        elif "밸류에이션" in expert.expertise or "Valuation" in expert.role:
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

            # 🎯 시니어 밸류에이션 애널리스트 구체적 분석 지침
            context_parts.append("\n🎯 밸류에이션 분석 필수 수행사항:")
            context_parts.append("1. DCF 분석 (구체적 산출식 제시):")
            context_parts.append("   - 자유현금흐름(FCF) 5년 예측값과 근거")
            context_parts.append(
                "   - 할인율(WACC) 산출 과정: WACC = (E/V)×Re + (D/V)×Rd×(1-T)"
            )
            context_parts.append(
                "   - 영구성장률 가정과 근거 (GDP성장률 + 인플레이션 고려)"
            )
            context_parts.append("   - 잔존가치 = FCF₅×(1+g)/(WACC-g)")
            context_parts.append("   - 최종 내재가치 = Σ(FCF_t/(1+WACC)^t) + 잔존가치")
            context_parts.append("")
            context_parts.append("2. 멀티플 분석 (동종업계 비교):")
            context_parts.append("   - 동종업계 평균 PER, PBR, EV/EBITDA 데이터 제시")
            context_parts.append(
                "   - 프리미엄/디스카운트 근거 (성장성, 수익성, 안정성)"
            )
            context_parts.append("   - 멀티플 × 해당지표 = 목표가 (계산과정 상세)")
            context_parts.append("")
            context_parts.append("3. 종합 목표가 산출 (가중평균):")
            context_parts.append("   - DCF 목표가 (가중치 40%)")
            context_parts.append("   - PER 목표가 (가중치 30%)")
            context_parts.append("   - PBR 목표가 (가중치 30%)")
            context_parts.append("   - 최종 목표가 = (DCF×0.4 + PER×0.3 + PBR×0.3)")
            context_parts.append("")
            context_parts.append("4. 시나리오 분석 (확률 배정):")
            context_parts.append("   - 낙관 시나리오 (확률 25%): 최고 실적 가정")
            context_parts.append("   - 기본 시나리오 (확률 50%): 컨센서스 기반")
            context_parts.append("   - 비관 시나리오 (확률 25%): 악재 반영")
            context_parts.append("   - 확률가중 목표가 = Σ(시나리오별 목표가 × 확률)")
            context_parts.append("")
            context_parts.append("⚠️ 밸류에이션 주의사항:")
            context_parts.append("- 모든 가정과 계산 과정 명시 (검증 가능하도록)")
            context_parts.append("- 민감도 분석: 핵심 변수 ±10% 변동 시 목표가 변화")
            context_parts.append("- 과거 멀티플 밴드와 현재 수준 비교")
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

            # 🎯 시니어 리스크 애널리스트 정량적 분석 지침
            context_parts.append("\n🎯 리스크 분석 필수 수행사항:")
            context_parts.append("1. 정량적 리스크 지표 산출:")
            context_parts.append("   - VaR (95% 신뢰구간): 1일, 10일, 1개월 VaR 계산")
            context_parts.append("   - CVaR (Conditional VaR): VaR 초과 손실의 평균")
            context_parts.append("   - Maximum Drawdown: 고점 대비 최대 하락률")
            context_parts.append("   - Sharpe Ratio = (수익률-무위험수익률)/표준편차")
            context_parts.append("   - Information Ratio = 초과수익률/추적오차")
            context_parts.append("")
            context_parts.append("2. 시나리오 분석 및 확률 산정:")
            context_parts.append("   - Base Case (50% 확률): 현재 추세 연장")
            context_parts.append("   - Bull Case (25% 확률): 긍정적 변화 시나리오")
            context_parts.append("   - Bear Case (25% 확률): 부정적 변화 시나리오")
            context_parts.append("   - Black Swan (5% 확률): 극단적 위기 시나리오")
            context_parts.append("   - 확률가중 기댓값 = Σ(시나리오별 손실 × 확률)")
            context_parts.append("")
            context_parts.append("3. 민감도 분석 (핵심 변수 영향도):")
            context_parts.append("   - 매출성장률 ±10%, ±20% 변화시 목표가 영향도")
            context_parts.append("   - 마진 ±10%, ±20% 변화시 수익성 영향도")
            context_parts.append("   - 할인율 ±1%, ±2% 변화시 밸류에이션 영향도")
            context_parts.append("   - 시장 베타 변화시 주가 변동성 영향도")
            context_parts.append("")
            context_parts.append("4. 스트레스 테스트:")
            context_parts.append("   - 2008년 금융위기급 시나리오 (예상 손실률)")
            context_parts.append("   - 2020년 팬데믹급 시나리오 (예상 손실률)")
            context_parts.append("   - 섹터별 특화 스트레스 (기술혁신 실패 등)")
            context_parts.append("   - 유동성 위기: 매도 가능 시간, 슬리피지 추정")
            context_parts.append("")
            context_parts.append("5. ESG 및 기타 리스크:")
            context_parts.append("   - ESG Score 하락시 주가 영향도 (정량화)")
            context_parts.append("   - Altman Z-Score: 신용위험 평가")
            context_parts.append("   - 집중도 리스크: 고객, 지역, 제품 다변화 수준")
            context_parts.append("   - 지정학적 리스크: 공급망, 수출의존도 영향")
            context_parts.append("")
            context_parts.append("⚠️ 리스크 분석 주의사항:")
            context_parts.append("- 모든 리스크 시나리오에 확률과 손실규모 정량화")
            context_parts.append("- 상관관계 고려: 동시 발생 가능한 리스크 조합")
            context_parts.append("- 시점별 리스크: 단기(3개월), 중기(1년), 장기(3년)")
            context_parts.append(
                "- 헤지 가능성: 파생상품, 보험 등을 통한 리스크 완화 방안"
            )

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

            # 🎯 시니어 재무제표 주석 전문가 상세 분석 지침
            context_parts.append("\n🎯 재무제표 주석 분석 필수 수행사항:")
            context_parts.append("1. 우발채무 및 보증채무 정밀분석:")
            context_parts.append("   - 우발채무 총액과 발생가능성 평가")
            context_parts.append("   - 우발채무/총자산 비율 (5% 이상시 주의)")
            context_parts.append("   - 보증채무 잔액과 대상 (관계회사, 임직원 등)")
            context_parts.append("   - 보증채무/자기자본 비율 (15% 이상시 위험)")
            context_parts.append("")
            context_parts.append("2. 관계회사 거래 투명성:")
            context_parts.append("   - 관계회사 매출/총매출 비율 (내부거래 의존도)")
            context_parts.append("   - 관계회사 매입/총매입 비율")
            context_parts.append("   - 관계회사 대여금, 차입금 규모")
            context_parts.append("   - 거래조건의 제3자 거래 대비 공정성")
            context_parts.append("")
            context_parts.append("3. 금융상품 및 파생상품 위험 평가:")
            context_parts.append("   - 파생상품 공정가치 변동손익 3년 추이")
            context_parts.append("   - 헤지회계 효과성 (80-125% 기준 준수 여부)")
            context_parts.append("   - 외환위험: 외화자산/부채 규모와 헤지비율")
            context_parts.append("   - 금리위험: 변동금리 부채 비중과 민감도")
            context_parts.append("")
            context_parts.append("4. 리스 및 약정사항 영향도:")
            context_parts.append("   - 운용리스 미래 최소 지급액의 현재가치")
            context_parts.append("   - 리스부채/총부채 비율 (K-IFRS 1116 적용)")
            context_parts.append("   - 약정 미실행 한도 (신용한도, 투자약정 등)")
            context_parts.append("   - Sale & Leaseback 거래의 손익 영향")
            context_parts.append("")
            context_parts.append("5. 회계정책 변경 및 추정변경 영향:")
            context_parts.append("   - 회계정책 변경으로 인한 손익 조정액")
            context_parts.append("   - 회계추정 변경 (내용연수, 잔존가치 등)")
            context_parts.append("   - 손상차손 인식과 환입 이력")
            context_parts.append("   - 충당부채 설정과 사용 내역")
            context_parts.append("")
            context_parts.append("6. 연결범위 변동 및 지배력 분석:")
            context_parts.append("   - 신규 연결 자회사 편입으로 인한 재무 영향")
            context_parts.append("   - 지배력 상실로 인한 연결 제외 영향")
            context_parts.append("   - 지분법 적용 투자주식의 손익 기여도")
            context_parts.append("   - 소수주주 지분 변동과 자본 거래")
            context_parts.append("")
            context_parts.append("⚠️ 주석 분석 주의사항:")
            context_parts.append("- 숨겨진 부채나 위험요소 발굴이 핵심")
            context_parts.append("- 정량적 임계치 초과시 반드시 리스크 등급 상향")
            context_parts.append("- 3년 추이 분석으로 패턴과 변화 방향 파악")
            context_parts.append("- 감사인 의견과 핵심감사사항(KAM) 교차 검증")

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

        full_context = "\n".join(safe_context_parts)

        # 토큰 수 계산 및 로깅
        estimated_tokens = self._estimate_tokens(full_context)
        logger.info(
            f"🎯 {expert.name} 통합 컨텍스트: {estimated_tokens:,} 토큰 (PDF 딕셔너리 완전 활용)"
        )

        return full_context

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
