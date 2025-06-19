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
        🚀 종합 데이터 기반 CrewAI 분석 (수정된 워크플로우용)

        재무데이터 + Enhanced DART + Manus Agent 수집 정보를 모두 통합해서
        CrewAI 전문가들이 종합적인 분석을 수행합니다.

        Args:
            user_prompt: 사용자 질문
            stock_name: 종목명
            stock_code: 종목코드
            financial_data: 재무 데이터
            enhanced_dart_data: Enhanced DART 데이터
            manus_collected_data: Manus Agent가 수집한 정보
            analysis_depth: 분석 깊이

        Returns:
            Dict: 종합 분석 결과
        """
        try:
            logger.info(f"🎯 CrewAI 종합 분석 시작: {stock_name} (수정된 워크플로우)")

            # 1. 종합 캐시 키 생성 (Manus 데이터 포함)
            comprehensive_cache_key = self._generate_comprehensive_cache_key(
                user_prompt,
                stock_name,
                stock_code,
                analysis_depth,
                manus_collected_data,
            )
            cached_result = self.cache_manager.get_cache(comprehensive_cache_key)
            if cached_result:
                logger.info("⚡ 종합 분석 캐시된 결과 반환 - 추가 비용 없음!")
                return cached_result

            # 2. 섹터 감지
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

            # 5. 🚀 종합 데이터로 전문가별 분석 수행
            expert_insights = await self._perform_comprehensive_expert_analysis(
                selected_experts,
                user_prompt,
                stock_name,
                stock_code,
                financial_data,
                enhanced_dart_data,
                manus_collected_data,
            )

            # 6. 비용 절감 계산
            cost_savings = self._calculate_cost_savings(
                len(selected_experts), analysis_depth
            )

            # 7. 🚀 종합 분석 결과 구성
            result = {
                "success": True,
                "analysis_type": "comprehensive_manus_crewai_synthesis",
                "detected_sector": detected_sector.name,
                "sector_korean_name": detected_sector.korean_name,
                "activated_experts": [expert.name for expert in selected_experts],
                "selected_experts_count": len(selected_experts),
                "expert_insights": expert_insights,
                "cost_savings": cost_savings,
                "analysis_depth": analysis_depth.value,
                "cache_key": comprehensive_cache_key,
                "data_integration_quality": self._assess_data_integration_quality(
                    financial_data, enhanced_dart_data, manus_collected_data
                ),
                "synthesis_completeness": "완전통합",  # 모든 데이터 소스 활용
            }

            # 8. 캐시 저장
            ttl_hours = self._get_cache_ttl(analysis_depth)
            self.cache_manager.set_cache(comprehensive_cache_key, result, ttl_hours)

            # 9. 통계 업데이트
            self._update_stats(detected_sector, cost_savings)

            logger.info(
                f"✅ CrewAI 종합 분석 완료 - 절약률: {cost_savings['savings_percentage']:.1f}%"
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
                expert_prompt = f"""
당신은 {expert.name}입니다.
전문 분야: {expert.expertise}
분석 초점: {expert.analysis_focus}

다음 종목을 분석해주세요:
- 종목명: {stock_name}
- 종목코드: {stock_code}
- 사용자 질문: {prompt}

전문 분야에 맞는 핵심 인사이트를 제공해주세요.
"""

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
                comprehensive_prompt = self._build_comprehensive_analysis_prompt(
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

    def _build_comprehensive_analysis_prompt(
        self,
        expert,
        user_prompt: str,
        stock_name: str,
        stock_code: str,
        financial_data: Dict,
        enhanced_dart_data: Dict = None,
        manus_collected_data: Dict = None,
    ) -> str:
        """종합 데이터 기반 전문가 분석 프롬프트 구성"""

        prompt_parts = [
            f"🎯 **전문가 종합 분석 요청**",
            f"전문가: {expert.name} ({expert.expertise})",
            f"사용자 질문: {user_prompt}",
            f"분석 대상: {stock_name} ({stock_code})",
            "",
            f"🎯 **당신의 전문성**: {expert.expertise}",
            f"🎯 **분석 접근법**: {expert.approach}",
            "",
        ]

        # 1. 재무데이터 섹션
        if financial_data and financial_data.get("success"):
            prompt_parts.extend(
                [
                    "📊 **재무데이터 (yfinance + 기본 DART)**:",
                    self._summarize_financial_data(financial_data),
                    "",
                ]
            )

        # 2. Enhanced DART 데이터 섹션
        if enhanced_dart_data and enhanced_dart_data.get("success"):
            prompt_parts.extend(
                [
                    "🚀 **Enhanced DART 상세 데이터**:",
                    self._summarize_enhanced_dart_data(enhanced_dart_data),
                    "",
                ]
            )

        # 3. Manus Agent 수집 정보 섹션 (새로 추가!)
        if manus_collected_data and manus_collected_data.get("performed"):
            collected_info = manus_collected_data.get("collected_information", "")
            data_richness = manus_collected_data.get("data_richness_score", 0)

            prompt_parts.extend(
                [
                    "🤖 **Manus Agent 수집 정보** (실시간 웹 검색 결과):",
                    f"📊 정보 풍부함 점수: {data_richness:.1f}/100",
                    f"🔍 수집된 정보:",
                    (
                        collected_info[:2000] + "..."
                        if len(collected_info) > 2000
                        else collected_info
                    ),
                    "",
                ]
            )

            # PDF 분석 결과 추가
            pdf_analysis = manus_collected_data.get("pdf_analysis", {})
            if pdf_analysis.get("pdf_detected") and pdf_analysis.get(
                "analysis_completed"
            ):
                pdf_content = pdf_analysis.get("pdf_content", {})
                pdf_text = pdf_content.get("raw_text", "")

                prompt_parts.extend(
                    [
                        "📄 **PDF 문서 분석 결과**:",
                        f"📊 PDF 텍스트 길이: {pdf_content.get('text_length', 0)}자",
                        f"🔍 PDF 내용 요약:",
                        pdf_text[:1500] + "..." if len(pdf_text) > 1500 else pdf_text,
                        "",
                    ]
                )

        # 4. 전문가별 분석 지시사항
        prompt_parts.extend(
            [
                f"🎯 **{expert.name} 전문가 종합 분석 지시사항**:",
                f"위의 모든 데이터(재무데이터 + Enhanced DART + Manus 수집 정보)를 통합하여",
                f"당신의 전문 분야인 '{expert.expertise}' 관점에서 종합 분석해주세요.",
                "",
                "📋 **분석 요구사항**:",
                "1. 모든 데이터 소스를 종합적으로 활용",
                "2. 당신의 전문성을 바탕으로 한 독특한 인사이트 제공",
                "3. 실시간 웹 정보와 재무데이터의 연관성 분석",
                "4. PDF 문서 내용과 다른 데이터의 일치성/차이점 분석",
                "5. 구체적이고 실행 가능한 투자 조언",
                "",
                "**중요**: 단순 요약이 아닌, 전문가로서의 깊이 있는 분석과 해석을 제공해주세요.",
            ]
        )

        return "\n".join(prompt_parts)

    def _summarize_financial_data(self, financial_data: Dict) -> str:
        """재무데이터 요약"""
        if not financial_data.get("success"):
            return "재무데이터 수집 실패"

        summary_parts = []

        # 기본 정보
        basic_info = financial_data.get("basic_info", {})
        if basic_info:
            summary_parts.append(
                f"• 시가총액: {basic_info.get('market_cap', '정보없음')}"
            )
            summary_parts.append(
                f"• 현재 주가: {basic_info.get('current_price', '정보없음')}"
            )

        # 재무비율
        ratios = financial_data.get("financial_ratios", {})
        if ratios:
            summary_parts.append(f"• PER: {ratios.get('pe_ratio', '정보없음')}")
            summary_parts.append(f"• PBR: {ratios.get('pb_ratio', '정보없음')}")
            summary_parts.append(f"• ROE: {ratios.get('roe', '정보없음')}")

        return "\n".join(summary_parts) if summary_parts else "재무데이터 정보 없음"

    def _summarize_enhanced_dart_data(self, enhanced_dart_data: Dict) -> str:
        """Enhanced DART 데이터 요약"""
        if not enhanced_dart_data.get("success"):
            return "Enhanced DART 데이터 수집 실패"

        summary_parts = []

        # 재무분석 정보
        if "financial_analysis" in enhanced_dart_data:
            summary_parts.append("• 상세 재무제표 포함")

        # 지배구조 정보
        if "governance_analysis" in enhanced_dart_data:
            governance = enhanced_dart_data["governance_analysis"]
            if governance.get("success"):
                summary_parts.append("• 기업지배구조 정보 포함")
                shareholders = governance.get("major_shareholders", [])
                if shareholders:
                    top_shareholder = shareholders[0]
                    summary_parts.append(
                        f"• 최대주주: {top_shareholder.get('shareholder_name', '정보없음')}"
                    )

        # 투자정보
        if "investment_analysis" in enhanced_dart_data:
            investment = enhanced_dart_data["investment_analysis"]
            if investment.get("success"):
                summary_parts.append("• 투자정보(배당, 증자감자 등) 포함")

        return "\n".join(summary_parts) if summary_parts else "Enhanced DART 정보 없음"

    async def _synthesize_expert_insights(
        self, expert_results: List[Dict], user_prompt: str
    ) -> str:
        """전문가 분석 결과를 종합하여 최종 인사이트 생성"""
        try:
            logger.info("🎯 전문가 분석 결과 종합 시작...")

            successful_analyses = [r for r in expert_results if not r.get("error")]

            if not successful_analyses:
                return "전문가 분석 실패로 종합 결과를 생성할 수 없습니다."

            synthesis_prompt = f"""
🎯 **전문가 팀 분석 결과 종합**

사용자 질문: {user_prompt}

다음은 {len(successful_analyses)}명의 전문가가 각자의 전문성을 바탕으로 분석한 결과입니다:

"""

            for i, analysis in enumerate(successful_analyses, 1):
                synthesis_prompt += f"""
**{i}. {analysis['expert_name']} ({analysis['expertise_area']})**:
{analysis['analysis_result'][:1000]}...

"""

            synthesis_prompt += f"""

🎯 **종합 분석 요청**:
위의 {len(successful_analyses)}명 전문가 분석을 종합하여 다음을 제공해주세요:

1. **핵심 공통 인사이트**: 전문가들이 공통적으로 지적한 핵심 포인트
2. **분야별 특화 인사이트**: 각 전문가만이 제공할 수 있는 독특한 관점
3. **종합 투자 의견**: 모든 분석을 고려한 최종 투자 추천
4. **리스크와 기회**: 주요 위험 요소와 기회 요소
5. **실행 가능한 액션 플랜**: 구체적인 투자 전략

**중요**: 각 전문가의 의견을 균형있게 반영하되, 일관된 결론을 도출해주세요.
"""

            synthesis_result = await self._call_llm_for_analysis(synthesis_prompt)
            logger.info("✅ 전문가 분석 결과 종합 완료")

            return synthesis_result

        except Exception as e:
            logger.error(f"❌ 전문가 분석 결과 종합 실패: {e}")
            return f"종합 분석 중 오류 발생: {str(e)}"

    def _generate_comprehensive_cache_key(
        self,
        prompt: str,
        stock_name: str,
        stock_code: str,
        depth: AnalysisDepth,
        manus_data: Dict = None,
    ) -> str:
        """종합 분석용 캐시 키 생성 (Manus 데이터 포함)"""

        # Manus 데이터의 핵심 정보만 해시에 포함 (너무 길어지지 않도록)
        manus_signature = ""
        if manus_data and manus_data.get("performed"):
            collected_info = manus_data.get("collected_information", "")
            richness_score = manus_data.get("data_richness_score", 0)
            # 수집된 정보의 길이와 풍부함 점수로 간단한 시그니처 생성
            manus_signature = f"_manus_{len(collected_info)}_{richness_score:.0f}"

            # PDF 포함 여부도 시그니처에 추가
            pdf_analysis = manus_data.get("pdf_analysis", {})
            if pdf_analysis.get("pdf_detected"):
                manus_signature += "_pdf"

        # 종합 캐시 키 생성
        comprehensive_key = (
            f"{prompt}_{stock_name}_{stock_code}_{depth.value}{manus_signature}"
        )
        return hashlib.md5(comprehensive_key.encode()).hexdigest()[:16]

    def _assess_data_integration_quality(
        self,
        financial_data: Dict,
        enhanced_dart_data: Dict = None,
        manus_collected_data: Dict = None,
    ) -> Dict[str, Any]:
        """데이터 통합 품질 평가"""

        quality_assessment = {
            "overall_score": 0,
            "data_sources_count": 0,
            "completeness": "낮음",
            "richness_level": "기본",
        }

        score = 0
        sources = 0

        # 재무데이터 평가
        if financial_data and financial_data.get("success"):
            score += 30
            sources += 1

        # Enhanced DART 데이터 평가
        if enhanced_dart_data and enhanced_dart_data.get("success"):
            score += 25
            sources += 1

        # Manus 수집 데이터 평가
        if manus_collected_data and manus_collected_data.get("performed"):
            score += 20
            sources += 1

            # 데이터 풍부함 보너스
            richness_score = manus_collected_data.get("data_richness_score", 0)
            score += min(richness_score * 0.25, 25)  # 최대 25점 추가

            # PDF 분석 보너스
            pdf_analysis = manus_collected_data.get("pdf_analysis", {})
            if pdf_analysis.get("pdf_detected") and pdf_analysis.get(
                "analysis_completed"
            ):
                score += 15

        # 최종 평가
        quality_assessment["overall_score"] = min(score, 100)
        quality_assessment["data_sources_count"] = sources

        if score >= 80:
            quality_assessment["completeness"] = "매우 높음"
            quality_assessment["richness_level"] = "최고급"
        elif score >= 60:
            quality_assessment["completeness"] = "높음"
            quality_assessment["richness_level"] = "고급"
        elif score >= 40:
            quality_assessment["completeness"] = "보통"
            quality_assessment["richness_level"] = "표준"
        else:
            quality_assessment["completeness"] = "낮음"
            quality_assessment["richness_level"] = "기본"

        return quality_assessment

    def _identify_used_data_sources(
        self,
        financial_data: Dict,
        enhanced_dart_data: Dict = None,
        manus_collected_data: Dict = None,
    ) -> List[str]:
        """사용된 데이터 소스 목록 생성"""

        sources = []

        if financial_data and financial_data.get("success"):
            sources.extend(financial_data.get("data_sources", ["yfinance"]))

        if enhanced_dart_data and enhanced_dart_data.get("success"):
            sources.append("Enhanced DART API")

        if manus_collected_data and manus_collected_data.get("performed"):
            sources.append("Manus Agent 웹검색")

            # PDF 분석이 포함된 경우
            pdf_analysis = manus_collected_data.get("pdf_analysis", {})
            if pdf_analysis.get("pdf_detected"):
                sources.append("PDF 문서 분석")

        return list(set(sources))  # 중복 제거

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
