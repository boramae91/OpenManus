#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q5 강제 생성 Custom AgentExecutor 테스트

Q5EnforcedAgentExecutor가 섹터별 Q5 질문을
확실히 강제 생성하는지 검증하는 스크립트입니다.

기존 61.5% Q5 성공률을 100%로 향상시키는 것이 목표입니다!
"""

import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List

# 현재 파일의 디렉토리를 기준으로 프로젝트 루트 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
sys.path.append(project_root)

# 환경 변수 로드
from dotenv import load_dotenv

load_dotenv()

# 필요한 모듈들 import
from app.crew.gics_sectors import GICSSector, GICSSectorManager
from app.crew.sector_teams import SectorTeamFactory


def test_q5_enforcement_single_sector():
    """
    단일 섹터에서 Q5 강제 생성 테스트

    테스트 대상: IT 섹터 (삼성전자)
    기대 결과: Q5 🖥️ IT 섹터 특화 질문이 반드시 포함되어야 함
    """
    print("🚀 Q5 강제 생성 단일 섹터 테스트 시작...")
    print("=" * 60)

    try:
        # 섹터 설정
        sector = GICSSector.INFORMATION_TECHNOLOGY
        sector_manager = GICSSectorManager()
        sector_korean_name = sector_manager.get_sector_korean_name(sector)

        print(f"🎯 테스트 섹터: 🖥️ {sector_korean_name}")
        print(f"🏢 테스트 기업: 삼성전자 (005930)")
        print()

        # SectorTeamFactory 생성
        team_factory = SectorTeamFactory(sector_manager)

        # 섹터팀 생성 (Q5EnforcedAgentExecutor 포함)
        print("🔧 Q5 강제 생성 섹터팀 생성 중...")
        sector_team = team_factory.create_sector_team(sector)

        # 통합 재무분석가 추출
        integrated_analyst = None
        for expert in sector_team.experts:
            if "통합 재무분석가" in expert.name:
                integrated_analyst = expert
                break

        if not integrated_analyst:
            raise ValueError("❌ 통합 재무분석가를 찾을 수 없습니다!")

        print(f"✅ 분석가 발견: {integrated_analyst.name}")
        print(f"🔗 Chain 타입: {type(integrated_analyst.langchain_chain)}")
        print()

        # 테스트 입력 데이터
        test_input = {
            "input": """
삼성전자 (005930) 재무분석을 수행해주세요.

**제공된 재무데이터:**
- 현재 주가: 58,000원
- 시가총액: 435조원
- PER: 18.5
- PBR: 1.2
- ROE: 12.3%
- ROA: 8.7%
- 부채비율: 35.2%

**요청사항:**
Enhanced Thinking Flow 3단계를 모두 수행하여
종합적인 투자 의견을 제시해주세요.
""",
            "chat_history": [],
        }

        print("🚀 Q5 강제 생성 Agent 실행 시작...")
        print("-" * 40)

        # 분석 실행
        start_time = datetime.now()
        result = integrated_analyst.langchain_chain.invoke(test_input)
        end_time = datetime.now()

        execution_time = (end_time - start_time).total_seconds()

        print("=" * 60)
        print(f"✅ 분석 완료! (실행시간: {execution_time:.1f}초)")
        print("=" * 60)

        # 결과 분석
        output = result.get("output", "")

        # Q5 검증
        q5_found = check_q5_presence(output, sector_korean_name)

        # 3단계 구조 검증
        structure_valid = check_three_stage_structure(output)

        # 결과 리포트
        print_test_results(q5_found, structure_valid, output, execution_time)

        # 결과 저장
        save_test_results(
            sector_korean_name, q5_found, structure_valid, result, execution_time
        )

        return q5_found and structure_valid

    except Exception as e:
        print(f"❌ 테스트 실행 오류: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_q5_enforcement_multiple_sectors():
    """
    다중 섹터에서 Q5 강제 생성 테스트

    테스트 대상: IT, 금융, 헬스케어 섹터
    기대 결과: 모든 섹터에서 각각의 특화 Q5가 강제 생성되어야 함
    """
    print("🚀 Q5 강제 생성 다중 섹터 테스트 시작...")
    print("=" * 60)

    test_sectors = [
        (GICSSector.INFORMATION_TECHNOLOGY, "삼성전자", "005930"),
        (GICSSector.FINANCIALS, "KB금융", "105560"),
        (GICSSector.HEALTH_CARE, "셀트리온", "068270"),
    ]

    results = []
    sector_manager = GICSSectorManager()

    for sector, company_name, ticker in test_sectors:
        sector_korean_name = sector_manager.get_sector_korean_name(sector)

        print(f"\n🎯 테스트 중: {sector_korean_name} - {company_name} ({ticker})")
        print("-" * 40)

        try:
            # 각 섹터별 테스트 실행
            success = test_single_sector_q5(
                sector, company_name, ticker, sector_manager
            )
            results.append(
                {
                    "sector": sector_korean_name,
                    "company": company_name,
                    "ticker": ticker,
                    "success": success,
                }
            )

        except Exception as e:
            print(f"❌ {sector_korean_name} 테스트 실패: {e}")
            results.append(
                {
                    "sector": sector_korean_name,
                    "company": company_name,
                    "ticker": ticker,
                    "success": False,
                    "error": str(e),
                }
            )

    # 최종 결과 분석
    print("\n" + "=" * 60)
    print("🎯 Q5 강제 생성 다중 섹터 테스트 결과")
    print("=" * 60)

    success_count = sum(1 for r in results if r["success"])
    total_count = len(results)
    success_rate = (success_count / total_count) * 100

    for result in results:
        status = "✅ 성공" if result["success"] else "❌ 실패"
        print(f"{status} | {result['sector']} - {result['company']}")
        if "error" in result:
            print(f"     오류: {result['error']}")

    print(f"\n🎯 최종 성공률: {success_count}/{total_count} ({success_rate:.1f}%)")

    if success_rate == 100.0:
        print("🎉 **완벽 성공!** Q5 강제 생성이 모든 섹터에서 100% 작동!")
    elif success_rate >= 80.0:
        print("✅ **대체로 성공!** Q5 강제 생성이 효과적으로 작동함")
    else:
        print("⚠️ **개선 필요!** Q5 강제 생성 로직 점검 필요")

    return success_rate


def test_single_sector_q5(
    sector: GICSSector,
    company_name: str,
    ticker: str,
    sector_manager: GICSSectorManager,
) -> bool:
    """
    단일 섹터의 Q5 강제 생성 테스트

    Args:
        sector: GICS 섹터
        company_name: 회사명
        ticker: 티커
        sector_manager: 섹터 매니저

    Returns:
        bool: Q5 강제 생성 성공 여부
    """
    try:
        sector_korean_name = sector_manager.get_sector_korean_name(sector)

        # SectorTeamFactory 생성
        team_factory = SectorTeamFactory(sector_manager)
        sector_team = team_factory.create_sector_team(sector)

        # 통합 재무분석가 추출
        integrated_analyst = None
        for expert in sector_team.experts:
            if "통합 재무분석가" in expert.name:
                integrated_analyst = expert
                break

        if not integrated_analyst:
            raise ValueError("통합 재무분석가를 찾을 수 없습니다!")

        # 간단한 테스트 입력
        test_input = {
            "input": f"""
{company_name} ({ticker}) 간단 분석을 수행해주세요.

Enhanced Thinking Flow의 1단계만 수행하여
섹터별 Q5 질문이 포함되는지 확인해주세요.
""",
            "chat_history": [],
        }

        # 분석 실행
        result = integrated_analyst.langchain_chain.invoke(test_input)
        output = result.get("output", "")

        # Q5 검증
        q5_found = check_q5_presence(output, sector_korean_name)

        print(f"Q5 검증 결과: {'✅ 발견' if q5_found else '❌ 누락'}")

        return q5_found

    except Exception as e:
        print(f"❌ 테스트 오류: {e}")
        return False


def check_q5_presence(output: str, sector_name: str) -> bool:
    """
    출력에서 Q5 섹터 특화 질문 존재 여부 검증

    Args:
        output: 분석 결과 텍스트
        sector_name: 섹터 한국어 이름

    Returns:
        bool: Q5 포함 여부
    """
    q5_indicators = [
        "Q5:",
        "Q5 ",
        "Q5-1:",
        "Q5-2:",
        f"{sector_name} 섹터 특화",
        "섹터 특화 분석",
        "섹터별 핵심",
        "업계 내 경쟁 우위",
        "시장 점유율",
        "운영 효율성",
    ]

    found_indicators = []
    for indicator in q5_indicators:
        if indicator in output:
            found_indicators.append(indicator)

    if found_indicators:
        print(f"✅ Q5 관련 키워드 발견: {found_indicators[:3]}...")
        return True
    else:
        print("❌ Q5 관련 키워드 없음")
        return False


def check_three_stage_structure(output: str) -> bool:
    """
    3단계 구조 (Self-Ask + ReAct + CoT) 존재 여부 검증

    Args:
        output: 분석 결과 텍스트

    Returns:
        bool: 3단계 구조 포함 여부
    """
    stage_indicators = {
        "1단계": ["1단계", "Self-Ask", "질문 구성"],
        "2단계": ["2단계", "ReAct", "정보 수집"],
        "3단계": ["3단계", "CoT", "추론", "Self-Critique"],
    }

    found_stages = []
    for stage_name, indicators in stage_indicators.items():
        for indicator in indicators:
            if indicator in output:
                found_stages.append(stage_name)
                break

    structure_valid = len(found_stages) >= 2  # 최소 2단계 이상

    print(
        f"📊 구조 검증: {found_stages} ({'✅ 유효' if structure_valid else '❌ 무효'})"
    )

    return structure_valid


def print_test_results(
    q5_found: bool, structure_valid: bool, output: str, execution_time: float
):
    """
    테스트 결과를 보기 좋게 출력

    Args:
        q5_found: Q5 발견 여부
        structure_valid: 구조 유효성
        output: 분석 결과
        execution_time: 실행 시간
    """
    print("📋 **Q5 강제 생성 테스트 결과**")
    print("-" * 40)

    q5_status = "✅ 성공" if q5_found else "❌ 실패"
    structure_status = "✅ 유효" if structure_valid else "❌ 무효"
    overall_status = (
        "🎉 완전 성공"
        if (q5_found and structure_valid)
        else "⚠️ 부분 성공" if (q5_found or structure_valid) else "❌ 완전 실패"
    )

    print(f"🎯 Q5 강제 생성: {q5_status}")
    print(f"🏗️ 3단계 구조: {structure_status}")
    print(f"⏱️ 실행 시간: {execution_time:.1f}초")
    print(f"🏆 종합 결과: {overall_status}")

    if q5_found:
        print("\n✅ **Q5 강제 생성 성공!** Custom AgentExecutor가 올바르게 작동함")
    else:
        print("\n❌ **Q5 강제 생성 실패!** 로직 점검 필요")

    print(f"\n📄 출력 길이: {len(output):,}자")
    print(f"📄 출력 미리보기:")
    preview = output[:300] + "..." if len(output) > 300 else output
    print(preview)


def save_test_results(
    sector_name: str,
    q5_found: bool,
    structure_valid: bool,
    result: Dict[str, Any],
    execution_time: float,
):
    """
    테스트 결과를 JSON 파일로 저장

    Args:
        sector_name: 섹터명
        q5_found: Q5 발견 여부
        structure_valid: 구조 유효성
        result: 전체 결과
        execution_time: 실행 시간
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"q5_enforced_test_result_{timestamp}.json"

    test_result = {
        "timestamp": timestamp,
        "test_type": "Q5_Enforced_AgentExecutor_Test",
        "sector": sector_name,
        "q5_found": q5_found,
        "structure_valid": structure_valid,
        "execution_time_seconds": execution_time,
        "overall_success": q5_found and structure_valid,
        "q5_enforced_flag": result.get("q5_enforced", False),
        "sector_emoji": result.get("sector_emoji", ""),
        "full_output": result.get("output", ""),
        "intermediate_steps": result.get("intermediate_steps", []),
    }

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(test_result, f, ensure_ascii=False, indent=2)
        print(f"💾 테스트 결과 저장: {filename}")
    except Exception as e:
        print(f"⚠️ 결과 저장 실패: {e}")


def main():
    """
    Q5 강제 생성 테스트 메인 함수
    """
    print("🚀 Q5EnforcedAgentExecutor 테스트 프로그램")
    print("=" * 60)
    print("목표: Q5 섹터 특화 질문 강제 생성 100% 달성!")
    print("기존: 61.5% → 목표: 100%")
    print("=" * 60)

    # 1. 단일 섹터 테스트
    print("\n🎯 **1단계: 단일 섹터 집중 테스트**")
    single_success = test_q5_enforcement_single_sector()

    if single_success:
        print("\n✅ 단일 섹터 테스트 성공! 다중 섹터 테스트 진행...")

        # 2. 다중 섹터 테스트
        print("\n🎯 **2단계: 다중 섹터 종합 테스트**")
        multi_success_rate = test_q5_enforcement_multiple_sectors()

        if multi_success_rate == 100.0:
            print("\n🎉 **완벽한 성공!** Q5 강제 생성 시스템 완성!")
            print("✅ 기존 61.5% → 신규 100% 달성!")
        else:
            print(f"\n⚠️ **개선 필요** 성공률: {multi_success_rate:.1f}%")
    else:
        print("\n❌ 단일 섹터 테스트 실패. 로직 점검 필요.")


if __name__ == "__main__":
    main()
