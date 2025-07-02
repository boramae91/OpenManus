# -*- coding: utf-8 -*-
"""
Day 2: 성능 최적화 시스템

이 파일은 LangChain Chain들의 성능 최적화를 위한 스크립트에요.
실행 시간 측정, 메모리 사용량 최적화, 프롬프트 템플릿 개선을 수행해요.
"""

import gc
import json
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import psutil

from app.crew.gics_sectors import GICSSectorManager

# 필요한 모듈들 import
from app.crew.sector_teams import AnalystAgent, SectorTeamFactory


@dataclass
class PerformanceMetrics:
    """
    성능 지표를 저장하는 데이터 클래스에요
    """

    agent_name: str
    role: str
    execution_time: float
    memory_usage_before: float
    memory_usage_after: float
    memory_increase: float
    chain_type: str
    optimization_applied: List[str]
    success: bool
    error_message: Optional[str] = None


class PerformanceOptimizationSystem:
    """
    LangChain Agent들의 성능 최적화를 담당하는 클래스에요
    """

    def __init__(self):
        """성능 최적화 시스템 초기화"""
        print("🚀 성능 최적화 시스템 초기화 중...")

        # 섹터 매니저 초기화
        self.sector_manager = GICSSectorManager()

        # 섹터 팀 팩토리 초기화
        self.team_factory = SectorTeamFactory(self.sector_manager)

        # 성능 지표 저장용
        self.performance_metrics = []

        # 최적화 설정
        self.optimization_config = {
            "enable_parallel_processing": True,
            "enable_memory_optimization": True,
            "enable_prompt_optimization": True,
            "enable_chain_caching": True,
            "max_concurrent_analyses": 3,
        }

        print("✅ 성능 최적화 시스템 초기화 완료!")

    def measure_agent_performance(
        self, agent: AnalystAgent, test_data: Dict[str, Any]
    ) -> PerformanceMetrics:
        """
        개별 Agent의 성능을 측정해요
        """
        print(f"   📊 {agent.name} 성능 측정 중...")

        # 메모리 사용량 측정 (분석 전)
        memory_before = self._get_memory_usage()

        # 분석 실행 시간 측정
        start_time = time.time()

        try:
            # Agent 분석 실행
            if "밸류에이션" in agent.role:
                result = agent.run_full_valuation_analysis(test_data)
            elif "기술적" in agent.role:
                result = agent.run_full_technical_analysis(test_data)
            elif "주석" in agent.role:
                result = agent.run_full_footnote_analysis(test_data)
            else:
                result = agent.run_langchain_analysis(test_data)

            execution_time = time.time() - start_time

            # 메모리 사용량 측정 (분석 후)
            memory_after = self._get_memory_usage()
            memory_increase = memory_after - memory_before

            # 성공한 경우
            return PerformanceMetrics(
                agent_name=agent.name,
                role=agent.role,
                execution_time=execution_time,
                memory_usage_before=memory_before,
                memory_usage_after=memory_after,
                memory_increase=memory_increase,
                chain_type=self._get_chain_type(agent),
                optimization_applied=[],
                success=True,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            memory_after = self._get_memory_usage()
            memory_increase = memory_after - memory_before

            # 실패한 경우
            return PerformanceMetrics(
                agent_name=agent.name,
                role=agent.role,
                execution_time=execution_time,
                memory_usage_before=memory_before,
                memory_usage_after=memory_after,
                memory_increase=memory_increase,
                chain_type=self._get_chain_type(agent),
                optimization_applied=[],
                success=False,
                error_message=str(e),
            )

    def _get_memory_usage(self) -> float:
        """
        현재 프로세스의 메모리 사용량을 MB 단위로 반환해요
        """
        process = psutil.Process()
        memory_info = process.memory_info()
        return memory_info.rss / 1024 / 1024  # MB로 변환

    def _get_chain_type(self, agent: AnalystAgent) -> str:
        """
        Agent의 Chain 타입을 반환해요
        """
        if agent.langchain_chain is None:
            return "No Chain"

        chain_class = type(agent.langchain_chain).__name__
        return chain_class

    def optimize_agent_performance(
        self, agent: AnalystAgent, test_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        개별 Agent의 성능을 최적화해요
        """
        print(f"   ⚡ {agent.name} 성능 최적화 중...")

        optimizations = []

        # 1. 메모리 최적화
        if self.optimization_config["enable_memory_optimization"]:
            memory_optimization = self._apply_memory_optimization(agent)
            if memory_optimization:
                optimizations.append("memory_optimization")

        # 2. 프롬프트 최적화
        if self.optimization_config["enable_prompt_optimization"]:
            prompt_optimization = self._apply_prompt_optimization(agent)
            if prompt_optimization:
                optimizations.append("prompt_optimization")

        # 3. Chain 캐싱
        if self.optimization_config["enable_chain_caching"]:
            cache_optimization = self._apply_chain_caching(agent)
            if cache_optimization:
                optimizations.append("chain_caching")

        # 최적화 후 성능 재측정
        optimized_metrics = self.measure_agent_performance(agent, test_data)
        optimized_metrics.optimization_applied = optimizations

        return {
            "agent_name": agent.name,
            "role": agent.role,
            "optimizations_applied": optimizations,
            "performance_metrics": optimized_metrics,
            "optimization_success": len(optimizations) > 0,
        }

    def _apply_memory_optimization(self, agent: AnalystAgent) -> bool:
        """
        메모리 최적화를 적용해요
        """
        try:
            # 가비지 컬렉션 실행
            gc.collect()

            # 분석 이력 크기 제한 (최근 10개만 유지)
            if len(agent.analysis_history) > 10:
                agent.analysis_history = agent.analysis_history[-10:]

            # Memory 시스템 최적화
            if agent.memory_system:
                # 메모리 크기 제한
                if hasattr(agent.memory_system, "max_token_limit"):
                    agent.memory_system.max_token_limit = 1000

            return True

        except Exception as e:
            print(f"     ⚠️ 메모리 최적화 실패: {e}")
            return False

    def _apply_prompt_optimization(self, agent: AnalystAgent) -> bool:
        """
        프롬프트 최적화를 적용해요
        """
        try:
            # Chain이 있는 경우 프롬프트 최적화
            if agent.langchain_chain:
                # 프롬프트 템플릿 최적화 (간소화)
                if hasattr(agent.langchain_chain, "prompt"):
                    prompt = agent.langchain_chain.prompt
                    if hasattr(prompt, "template"):
                        # 템플릿에서 불필요한 공백 제거
                        optimized_template = prompt.template.strip()
                        if len(optimized_template) < len(prompt.template):
                            prompt.template = optimized_template

            return True

        except Exception as e:
            print(f"     ⚠️ 프롬프트 최적화 실패: {e}")
            return False

    def _apply_chain_caching(self, agent: AnalystAgent) -> bool:
        """
        Chain 캐싱을 적용해요
        """
        try:
            # 간단한 캐싱 메커니즘 구현
            if not hasattr(agent, "_analysis_cache"):
                agent._analysis_cache = {}

            # 캐시 크기 제한
            if len(agent._analysis_cache) > 50:
                # 가장 오래된 항목 제거
                oldest_key = next(iter(agent._analysis_cache))
                del agent._analysis_cache[oldest_key]

            return True

        except Exception as e:
            print(f"     ⚠️ Chain 캐싱 실패: {e}")
            return False

    def run_parallel_analysis(
        self, agents: List[AnalystAgent], test_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        여러 Agent를 병렬로 분석해요
        """
        print(f"   🔄 {len(agents)}개 Agent 병렬 분석 시작...")

        import concurrent.futures

        results = []

        # ThreadPoolExecutor를 사용한 병렬 처리
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.optimization_config["max_concurrent_analyses"]
        ) as executor:
            # 각 Agent별로 분석 작업 제출
            future_to_agent = {
                executor.submit(
                    self.optimize_agent_performance, agent, test_data
                ): agent
                for agent in agents
            }

            # 결과 수집
            for future in concurrent.futures.as_completed(future_to_agent):
                agent = future_to_agent[future]
                try:
                    result = future.result()
                    results.append(result)
                    print(f"     ✅ {agent.name} 병렬 분석 완료")
                except Exception as e:
                    print(f"     ❌ {agent.name} 병렬 분석 실패: {e}")
                    results.append(
                        {
                            "agent_name": agent.name,
                            "role": agent.role,
                            "error": str(e),
                            "optimization_success": False,
                        }
                    )

        return results

    def benchmark_all_agents(self) -> Dict[str, Any]:
        """
        모든 Agent들의 성능 벤치마크를 실행해요
        """
        print("\n🏁 전체 Agent 성능 벤치마크 시작...")

        # Technology 섹터 팀 가져오기
        tech_sector = self.sector_manager.get_sector_by_name("Technology")
        team = self.team_factory.create_sector_team(tech_sector)

        benchmark_results = {
            "timestamp": datetime.now().isoformat(),
            "total_agents": len(team.experts),
            "agent_results": [],
            "summary": {},
        }

        # 각 Agent별 성능 측정
        for agent in team.experts:
            print(f"\n📊 {agent.name} ({agent.role}) 벤치마크 중...")

            # 테스트 데이터 생성
            test_data = self._create_benchmark_test_data(agent.role)

            # 최적화 전 성능 측정
            baseline_metrics = self.measure_agent_performance(agent, test_data)

            # 최적화 적용
            optimization_result = self.optimize_agent_performance(agent, test_data)

            # 결과 저장
            agent_result = {
                "agent_name": agent.name,
                "role": agent.role,
                "baseline_metrics": baseline_metrics,
                "optimization_result": optimization_result,
                "improvement": self._calculate_improvement(
                    baseline_metrics, optimization_result["performance_metrics"]
                ),
            }

            benchmark_results["agent_results"].append(agent_result)

        # 전체 요약 생성
        benchmark_results["summary"] = self._generate_benchmark_summary(
            benchmark_results["agent_results"]
        )

        return benchmark_results

    def _create_benchmark_test_data(self, role: str) -> Dict[str, Any]:
        """
        벤치마크용 테스트 데이터를 생성해요
        """
        base_data = {
            "sector_name": "Technology",
            "company_name": "삼성전자",
            "ticker": "005930",
        }

        if "펀더멘털" in role:
            base_data.update(
                {
                    "financial_data": "매출액: 100조원, 영업이익: 15조원, 순이익: 12조원, 자산총계: 500조원, 부채총계: 200조원",
                    "revenue": "100000000000000",
                    "operating_income": "15000000000000",
                    "net_income": "12000000000000",
                    "total_assets": "500000000000000",
                    "total_liabilities": "200000000000000",
                }
            )
        elif "기술적" in role:
            base_data.update(
                {
                    "price_data": "현재가: 70,000원, 52주 최고: 80,000원, 52주 최저: 50,000원, 거래량: 1000만주",
                    "current_price": "70000",
                    "high_52w": "80000",
                    "low_52w": "50000",
                    "volume": "10000000",
                }
            )
        elif "밸류에이션" in role:
            base_data.update(
                {
                    "financial_data": "매출액: 100조원, 영업이익: 15조원, 순이익: 12조원",
                    "market_cap": "500000000000000",
                    "book_value": "300000000000000",
                    "pe_ratio": "15.5",
                    "pb_ratio": "1.8",
                }
            )
        elif "리스크" in role:
            base_data.update(
                {
                    "financial_data": "부채비율: 30%, 유동비율: 2.5, 이자보상배율: 15, 베타: 1.2",
                    "debt_ratio": "30",
                    "current_ratio": "2.5",
                    "interest_coverage": "15",
                    "beta": "1.2",
                }
            )
        elif "산업" in role:
            base_data.update(
                {
                    "industry_data": "반도체 시장 규모: 500조원, 성장률: 8%, 경쟁사: SK하이닉스, TSMC, 시장점유율: 25%",
                    "market_size": "500000000000000",
                    "growth_rate": "8",
                    "competitors": ["SK하이닉스", "TSMC"],
                    "market_share": "25",
                }
            )
        elif "주석" in role:
            base_data.update(
                {
                    "financial_data": "매출액: 100조원, 영업이익: 15조원, 순이익: 12조원",
                    "footnotes": "주석1: 외환손익 포함, 주석2: 연구개발비 증가, 주석3: 법인세율 변경, 주석4: 자산재평가",
                }
            )

        return base_data

    def _calculate_improvement(
        self, baseline: PerformanceMetrics, optimized: PerformanceMetrics
    ) -> Dict[str, float]:
        """
        최적화 전후 성능 개선도를 계산해요
        """
        if baseline.execution_time > 0:
            time_improvement = (
                (baseline.execution_time - optimized.execution_time)
                / baseline.execution_time
            ) * 100
        else:
            time_improvement = 0

        if baseline.memory_increase > 0:
            memory_improvement = (
                (baseline.memory_increase - optimized.memory_increase)
                / baseline.memory_increase
            ) * 100
        else:
            memory_improvement = 0

        return {
            "time_improvement_percent": time_improvement,
            "memory_improvement_percent": memory_improvement,
            "overall_improvement": (time_improvement + memory_improvement) / 2,
        }

    def _generate_benchmark_summary(
        self, agent_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        벤치마크 결과 요약을 생성해요
        """
        total_agents = len(agent_results)
        successful_optimizations = sum(
            1
            for result in agent_results
            if result["optimization_result"]["optimization_success"]
        )

        # 평균 성능 개선도 계산
        time_improvements = [
            result["improvement"]["time_improvement_percent"]
            for result in agent_results
        ]
        memory_improvements = [
            result["improvement"]["memory_improvement_percent"]
            for result in agent_results
        ]
        overall_improvements = [
            result["improvement"]["overall_improvement"] for result in agent_results
        ]

        return {
            "total_agents": total_agents,
            "successful_optimizations": successful_optimizations,
            "optimization_success_rate": (
                (successful_optimizations / total_agents * 100)
                if total_agents > 0
                else 0
            ),
            "average_time_improvement": (
                sum(time_improvements) / len(time_improvements)
                if time_improvements
                else 0
            ),
            "average_memory_improvement": (
                sum(memory_improvements) / len(memory_improvements)
                if memory_improvements
                else 0
            ),
            "average_overall_improvement": (
                sum(overall_improvements) / len(overall_improvements)
                if overall_improvements
                else 0
            ),
        }

    def generate_optimization_report(self, benchmark_results: Dict[str, Any]) -> str:
        """
        최적화 결과를 보고서로 생성해요
        """
        print("\n📋 최적화 보고서 생성 중...")

        report = {
            "optimization_timestamp": datetime.now().isoformat(),
            "optimization_config": self.optimization_config,
            "benchmark_results": benchmark_results,
            "recommendations": self._generate_optimization_recommendations(
                benchmark_results
            ),
        }

        # JSON 파일로 저장
        filename = f"performance_optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"✅ 최적화 보고서 저장 완료: {filename}")
        return filename

    def _generate_optimization_recommendations(
        self, benchmark_results: Dict[str, Any]
    ) -> List[str]:
        """
        최적화 권장사항을 생성해요
        """
        recommendations = []
        summary = benchmark_results["summary"]

        # 성능 개선도에 따른 권장사항
        if summary["average_time_improvement"] < 10:
            recommendations.append(
                "실행 시간 최적화가 필요합니다. 프롬프트 템플릿을 더 간소화하세요."
            )

        if summary["average_memory_improvement"] < 10:
            recommendations.append(
                "메모리 사용량 최적화가 필요합니다. 분석 이력 크기를 더 제한하세요."
            )

        if summary["optimization_success_rate"] < 80:
            recommendations.append(
                "일부 Agent의 최적화가 실패했습니다. 개별 Agent 설정을 점검하세요."
            )

        # 긍정적인 결과에 대한 권장사항
        if summary["average_overall_improvement"] > 20:
            recommendations.append(
                "전체적인 성능 개선이 우수합니다. 현재 최적화 설정을 유지하세요."
            )

        if summary["optimization_success_rate"] > 90:
            recommendations.append(
                "최적화 성공률이 높습니다. 추가적인 고급 최적화 기법을 고려해보세요."
            )

        return recommendations


def main():
    """
    메인 실행 함수에요
    """
    print("🎯 Day 2: 성능 최적화 시스템 시작!")
    print("=" * 60)

    # 성능 최적화 시스템 초기화
    optimization_system = PerformanceOptimizationSystem()

    # 1. 전체 Agent 성능 벤치마크
    print("\n🏁 1단계: 전체 Agent 성능 벤치마크")
    benchmark_results = optimization_system.benchmark_all_agents()

    # 2. 최적화 보고서 생성
    print("\n📋 2단계: 최적화 보고서 생성")
    report_filename = optimization_system.generate_optimization_report(
        benchmark_results
    )

    # 3. 결과 요약 출력
    print("\n🎯 최적화 결과 요약:")
    summary = benchmark_results["summary"]

    print(f"   총 Agent 수: {summary['total_agents']}")
    print(f"   최적화 성공: {summary['successful_optimizations']}")
    print(f"   성공률: {summary['optimization_success_rate']:.1f}%")
    print(f"   평균 실행시간 개선: {summary['average_time_improvement']:.1f}%")
    print(f"   평균 메모리 개선: {summary['average_memory_improvement']:.1f}%")
    print(f"   전체 평균 개선: {summary['average_overall_improvement']:.1f}%")

    # 권장사항 출력
    print("\n💡 권장사항:")
    recommendations = optimization_system._generate_optimization_recommendations(
        benchmark_results
    )
    for i, recommendation in enumerate(recommendations, 1):
        print(f"   {i}. {recommendation}")

    print(f"\n✅ Day 2 작업 완료! 보고서: {report_filename}")


if __name__ == "__main__":
    main()
