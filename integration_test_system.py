# -*- coding: utf-8 -*-
"""
Day 1: 시스템 통합 및 안정화 테스트

이 파일은 모든 LangChain Agent들의 통합 테스트 및 안정화를 위한 스크립트에요.
각 전문가 Agent들이 제대로 작동하는지, 서로 협력할 수 있는지 테스트해요.
"""

import json
import time
from datetime import datetime
from typing import Any, Dict, List

from app.crew.gics_sectors import GICSSectorManager

# 필요한 모듈들 import
from app.crew.sector_teams import SectorTeamFactory


class IntegrationTestSystem:
    """
    전체 시스템 통합 테스트를 담당하는 클래스에요
    모든 LangChain Agent들이 제대로 작동하는지 확인해요
    """

    def __init__(self):
        """통합 테스트 시스템 초기화"""
        print("🚀 통합 테스트 시스템 초기화 중...")

        # 섹터 매니저 초기화
        self.sector_manager = GICSSectorManager()

        # 섹터 팀 팩토리 초기화
        self.team_factory = SectorTeamFactory(self.sector_manager)

        # 테스트 결과 저장용
        self.test_results = []

        print("✅ 통합 테스트 시스템 초기화 완료!")

    def test_all_sectors(self) -> Dict[str, Any]:
        """
        모든 섹터의 팀들을 테스트해요
        각 섹터별로 6명의 전문가가 제대로 작동하는지 확인해요
        """
        print("\n🔍 모든 섹터 팀 테스트 시작...")

        all_sectors = self.sector_manager.get_all_sectors()
        sector_results = {}

        for sector in all_sectors:
            print(f"\n📊 {sector.name} 섹터 테스트 중...")
            sector_result = self._test_single_sector(sector)
            sector_results[sector.name] = sector_result

        return sector_results

    def _test_single_sector(self, sector) -> Dict[str, Any]:
        """
        단일 섹터 팀을 테스트해요
        """
        try:
            # 섹터 팀 생성
            team = self.team_factory.create_sector_team(sector)

            # 팀 정보 출력
            print(f"   팀명: {team.team_name}")
            print(f"   전문가 수: {len(team.experts)}")

            # 각 전문가별 테스트
            expert_results = {}
            for expert in team.experts:
                expert_result = self._test_single_expert(expert)
                expert_results[expert.role] = expert_result

            return {
                "team_name": team.team_name,
                "sector_name": sector.name,
                "expert_count": len(team.experts),
                "expert_results": expert_results,
                "status": "success",
            }

        except Exception as e:
            print(f"   ❌ {sector.name} 섹터 테스트 실패: {e}")
            return {
                "team_name": f"{sector.name} 팀",
                "sector_name": sector.name,
                "error": str(e),
                "status": "failed",
            }

    def _test_single_expert(self, expert) -> Dict[str, Any]:
        """
        단일 전문가를 테스트해요
        """
        try:
            print(f"     🔍 {expert.name} ({expert.role}) 테스트 중...")

            # LangChain 활성화 상태 확인
            langchain_status = {
                "enabled": expert.langchain_enabled,
                "chain_exists": expert.langchain_chain is not None,
                "memory_exists": expert.memory_system is not None,
            }

            # 기본 정보 확인
            basic_info = {
                "name": expert.name,
                "role": expert.role,
                "expertise": expert.expertise,
                "analysis_focus": expert.analysis_focus,
            }

            # 간단한 테스트 데이터로 분석 실행
            test_data = self._create_test_data_for_expert(expert.role)
            analysis_result = self._run_expert_analysis(expert, test_data)

            return {
                "basic_info": basic_info,
                "langchain_status": langchain_status,
                "analysis_result": analysis_result,
                "status": "success",
            }

        except Exception as e:
            print(f"     ❌ {expert.name} 테스트 실패: {e}")
            return {
                "name": expert.name,
                "role": expert.role,
                "error": str(e),
                "status": "failed",
            }

    def _create_test_data_for_expert(self, role: str) -> Dict[str, Any]:
        """
        전문가 역할에 맞는 테스트 데이터를 생성해요
        (모든 변수를 포함하여 PromptTemplate 에러를 방지합니다)
        """
        # 모든 전문가에게 필요한 모든 변수를 한번에 제공 (시간 절약!)
        test_data = {
            "sector_name": "Technology",  # 섹터명
            "company_name": "삼성전자",  # 회사명
            "financial_data": "매출액: 100조원, 영업이익: 15조원, 순이익: 12조원, 부채비율: 30%, 유동비율: 2.5, 이자보상배율: 15",
            "price_data": "현재가: 70,000원, 52주 최고: 80,000원, 52주 최저: 50,000원, 거래량: 100만주, 이동평균선: 65,000원",
            "company_data": "반도체 시장 규모: 500조원, 성장률: 8%, 경쟁사: SK하이닉스, TSMC, 시장점유율: 15%, 기술력: 최고수준",
        }

        return test_data

    def _run_expert_analysis(self, expert, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        전문가의 분석을 실행해요
        """
        try:
            start_time = time.time()

            # 전문가 역할에 따라 적절한 분석 메서드 호출
            if "밸류에이션" in expert.role:
                result = expert.run_full_valuation_analysis(test_data)
            elif "기술적" in expert.role:
                result = expert.run_full_technical_analysis(test_data)
            elif "주석" in expert.role:
                result = expert.run_full_footnote_analysis(test_data)
            elif "산업" in expert.role:
                # 산업 전문가는 기본 LangChain 분석 사용
                result = expert.run_langchain_analysis(test_data)
            elif "펀더멘털" in expert.role:
                # 펀더멘털 분석가는 기본 LangChain 분석 사용
                result = expert.run_langchain_analysis(test_data)
            elif "리스크" in expert.role:
                # 리스크 평가자는 기본 LangChain 분석 사용
                result = expert.run_langchain_analysis(test_data)
            else:
                # 기본 LangChain 분석
                result = expert.run_langchain_analysis(test_data)

            end_time = time.time()
            analysis_time = end_time - start_time

            return {
                "success": True,
                "analysis_time": analysis_time,
                "result_keys": list(result.keys()) if isinstance(result, dict) else [],
                "has_error": "error" in result if isinstance(result, dict) else False,
            }

        except Exception as e:
            return {"success": False, "error": str(e), "analysis_time": 0.0}

    def test_inter_agent_communication(self) -> Dict[str, Any]:
        """
        Agent 간 상호작용을 테스트해요
        """
        print("\n🤝 Agent 간 상호작용 테스트 시작...")

        try:
            # Technology 섹터 팀 가져오기
            tech_sector = self.sector_manager.get_sector_by_name("Technology")
            team = self.team_factory.create_sector_team(tech_sector)

            # 펀더멘털 분석가와 밸류에이션 전문가 간 협업 테스트
            fundamental_expert = None
            valuation_expert = None

            for expert in team.experts:
                if "펀더멘털" in expert.role:
                    fundamental_expert = expert
                elif "밸류에이션" in expert.role:
                    valuation_expert = expert

            if fundamental_expert and valuation_expert:
                # 펀더멘털 분석 실행
                fundamental_data = self._create_test_data_for_expert("펀더멘털 분석가")
                fundamental_result = fundamental_expert.run_langchain_analysis(
                    fundamental_data
                )

                # 밸류에이션 분석 실행 (펀더멘털 결과 포함)
                valuation_data = self._create_test_data_for_expert("밸류에이션 전문가")
                valuation_data["fundamental_analysis"] = fundamental_result
                valuation_result = valuation_expert.run_langchain_analysis(
                    valuation_data
                )

                return {
                    "fundamental_analysis": fundamental_result,
                    "valuation_analysis": valuation_result,
                    "collaboration_success": True,
                }
            else:
                return {
                    "error": "필요한 전문가를 찾을 수 없어요",
                    "collaboration_success": False,
                }

        except Exception as e:
            return {"error": str(e), "collaboration_success": False}

    def generate_test_report(
        self, sector_results: Dict[str, Any], communication_results: Dict[str, Any]
    ) -> str:
        """
        테스트 결과를 보고서로 생성해요
        """
        print("\n📋 테스트 보고서 생성 중...")

        report = {
            "test_timestamp": datetime.now().isoformat(),
            "total_sectors_tested": len(sector_results),
            "sector_results": sector_results,
            "communication_results": communication_results,
            "summary": self._generate_summary(sector_results, communication_results),
        }

        # JSON 파일로 저장
        filename = (
            f"integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"✅ 테스트 보고서 저장 완료: {filename}")
        return filename

    def _generate_summary(
        self, sector_results: Dict[str, Any], communication_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        테스트 결과 요약을 생성해요
        """
        total_experts = 0
        successful_experts = 0
        failed_experts = 0

        for sector_name, sector_result in sector_results.items():
            if sector_result.get("status") == "success":
                expert_results = sector_result.get("expert_results", {})
                total_experts += len(expert_results)

                for expert_role, expert_result in expert_results.items():
                    if expert_result.get("status") == "success":
                        successful_experts += 1
                    else:
                        failed_experts += 1

        return {
            "total_experts": total_experts,
            "successful_experts": successful_experts,
            "failed_experts": failed_experts,
            "success_rate": (
                (successful_experts / total_experts * 100) if total_experts > 0 else 0
            ),
            "communication_success": communication_results.get(
                "collaboration_success", False
            ),
        }


def main():
    """
    메인 실행 함수에요
    """
    print("🎯 Day 1: 시스템 통합 및 안정화 테스트 시작!")
    print("=" * 60)

    # 통합 테스트 시스템 초기화
    test_system = IntegrationTestSystem()

    # 1. 모든 섹터 테스트
    print("\n📊 1단계: 모든 섹터 팀 테스트")
    sector_results = test_system.test_all_sectors()

    # 2. Agent 간 상호작용 테스트
    print("\n🤝 2단계: Agent 간 상호작용 테스트")
    communication_results = test_system.test_inter_agent_communication()

    # 3. 테스트 보고서 생성
    print("\n📋 3단계: 테스트 보고서 생성")
    report_filename = test_system.generate_test_report(
        sector_results, communication_results
    )

    # 4. 결과 요약 출력
    print("\n🎯 테스트 결과 요약:")
    summary = test_system._generate_summary(sector_results, communication_results)

    print(f"   총 전문가 수: {summary['total_experts']}")
    print(f"   성공한 전문가: {summary['successful_experts']}")
    print(f"   실패한 전문가: {summary['failed_experts']}")
    print(f"   성공률: {summary['success_rate']:.1f}%")
    print(f"   Agent 간 협업: {'성공' if summary['communication_success'] else '실패'}")

    print(f"\n✅ Day 1 작업 완료! 보고서: {report_filename}")


if __name__ == "__main__":
    main()
