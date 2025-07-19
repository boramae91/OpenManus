#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
전체 3단계 Dynamic Enhanced Thinking Flow 테스트

강화된 강제 지시사항이 LLM으로 하여금
완전한 3단계 구조를 수행하도록 하는지 검증합니다.
"""

import os
import sys
from datetime import datetime

# 프로젝트 루트 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 환경 변수 로드
from dotenv import load_dotenv

load_dotenv()

# 필요한 모듈들 import
from app.crew.gics_sectors import GICSSector, GICSSectorManager
from app.crew.sector_teams import SectorTeamFactory


def test_full_3stage_thinking_flow():
    """
    전체 3단계 Dynamic Enhanced Thinking Flow 테스트
    """
    print("🧪 전체 3단계 Dynamic Enhanced Thinking Flow 테스트")
    print("=" * 60)

    try:
        # 섹터 설정
        sector = GICSSector.INFORMATION_TECHNOLOGY
        sector_manager = GICSSectorManager()
        sector_korean_name = sector_manager.get_sector_korean_name(sector)

        print(f"🎯 테스트 섹터: 🖥️ {sector_korean_name}")
        print(f"🏢 테스트 기업: 삼성전자")
        print()

        # 섹터팀 생성
        team_factory = SectorTeamFactory(sector_manager)
        sector_team = team_factory.create_sector_team(sector)

        # 통합 재무분석가 찾기
        integrated_analyst = None
        for expert in sector_team.experts:
            if "통합 재무분석가" in expert.name:
                integrated_analyst = expert
                break

        if not integrated_analyst:
            raise ValueError("❌ 통합 재무분석가를 찾을 수 없습니다!")

        print(f"✅ 분석가: {integrated_analyst.name}")
        print(f"🔗 Chain 타입: {type(integrated_analyst.langchain_chain)}")
        print()

        # 전체 3단계 테스트 입력
        test_input = {
            "input": """
삼성전자(005930) 종합 재무분석을 수행해주세요.

**제공된 재무데이터:**
- 현재 주가: 58,000원
- 시가총액: 435조원
- PER: 18.5
- PBR: 1.2
- ROE: 12.3%
- ROA: 8.7%
- 부채비율: 35.2%
- 영업이익률: 10.9%

**요청사항:**
Enhanced Thinking Flow 전체 3단계를 모두 완료하여 종합적인 투자 의견을 제시해주세요:
1. Self-Ask with ToT (질문 구성)
2. ReAct (정보 수집 및 분석)
3. CoT + Self-Critique (추론 및 검증)

반드시 === 1단계 ===, === 2단계 ===, === 3단계 === 형식을 사용하세요.
""",
            "chat_history": [],
        }

        print("🚀 전체 3단계 Dynamic Enhanced Thinking Flow 실행...")
        print("-" * 40)

        # 실행
        start_time = datetime.now()
        result = integrated_analyst.langchain_chain.invoke(test_input)
        end_time = datetime.now()

        execution_time = (end_time - start_time).total_seconds()

        print("=" * 60)
        print(f"✅ 실행 완료! (시간: {execution_time:.1f}초)")
        print("=" * 60)

        # 결과 분석
        output = result.get("output", "")

        # 3단계 구조 검증
        print("🔍 **3단계 구조 검증**")
        print("-" * 30)

        stage_patterns = {
            "1단계": ["=== 1단계:", "Self-Ask with ToT"],
            "2단계": ["=== 2단계:", "ReAct"],
            "3단계": ["=== 3단계:", "CoT", "Self-Critique"],
        }

        found_stages = {}
        for stage_name, patterns in stage_patterns.items():
            found = any(pattern in output for pattern in patterns)
            found_stages[stage_name] = found
            status = "✅ 발견" if found else "❌ 누락"
            print(f"{status} {stage_name}: {patterns}")

        # Dynamic Q5 검증
        print("\n🔍 **Dynamic Q5 검증**")
        print("-" * 30)

        q5_patterns = ["Q5:", "IT 섹터 특화", "기술 경쟁력", "R&D 투자", "클라우드/AI"]

        found_q5 = []
        for pattern in q5_patterns:
            if pattern in output:
                found_q5.append(pattern)

        q5_success = len(found_q5) >= 3
        print(f"✅ Q5 키워드: {found_q5}")
        print(f"📊 Q5 성공: {'✅ 성공' if q5_success else '❌ 실패'}")

        # 강제 형식 검증
        print("\n🔍 **강제 형식 검증**")
        print("-" * 30)

        forbidden_patterns = [
            "### 1.",
            "### 2.",
            "### 3.",
            "수익성 분석",
            "안정성 분석",
        ]
        uses_forbidden = any(pattern in output for pattern in forbidden_patterns)

        if uses_forbidden:
            print("❌ 금지된 기존 형식 사용됨")
            forbidden_found = [p for p in forbidden_patterns if p in output]
            print(f"   발견된 금지 패턴: {forbidden_found}")
        else:
            print("✅ 강제 형식 준수")

        # 최종 평가
        print("\n🏆 **최종 평가**")
        print("-" * 30)

        stages_complete = sum(found_stages.values())
        total_stages = len(found_stages)

        overall_success = (
            stages_complete == total_stages  # 모든 단계 완료
            and q5_success  # Q5 성공
            and not uses_forbidden  # 금지 형식 미사용
        )

        print(f"📊 단계 완성도: {stages_complete}/{total_stages}")
        print(f"📊 Q5 성공: {'✅' if q5_success else '❌'}")
        print(f"📊 형식 준수: {'✅' if not uses_forbidden else '❌'}")
        print(
            f"🏆 전체 성공: {'🎉 완전 성공' if overall_success else '⚠️ 부분 성공' if stages_complete > 0 else '❌ 실패'}"
        )

        # 출력 미리보기
        print(f"\n📄 **출력 길이**: {len(output):,}자")
        print("📄 **출력 미리보기 (처음 800자)**")
        print("-" * 30)
        preview = output[:800] + "..." if len(output) > 800 else output
        print(preview)

        # 결과 저장
        save_full_test_results(
            overall_success,
            found_stages,
            q5_success,
            uses_forbidden,
            output,
            execution_time,
        )

        return overall_success

    except Exception as e:
        print(f"❌ 테스트 실행 오류: {e}")
        import traceback

        traceback.print_exc()
        return False


def save_full_test_results(
    success, stages, q5_success, uses_forbidden, output, execution_time
):
    """
    전체 3단계 테스트 결과를 저장합니다.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"full_3stage_test_result_{timestamp}.json"

    import json

    test_result = {
        "timestamp": timestamp,
        "test_type": "Full_3Stage_Dynamic_Enhanced_Thinking_Flow_Test",
        "overall_success": success,
        "stages_found": stages,
        "q5_success": q5_success,
        "forbidden_format_used": uses_forbidden,
        "execution_time_seconds": execution_time,
        "output_length": len(output),
        "full_output": output,
    }

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(test_result, f, ensure_ascii=False, indent=2)
        print(f"💾 테스트 결과 저장: {filename}")
    except Exception as e:
        print(f"⚠️ 결과 저장 실패: {e}")


def main():
    """
    전체 3단계 테스트 메인 함수
    """
    print("🧪 전체 3단계 Dynamic Enhanced Thinking Flow 테스트 프로그램")
    print("목표: 강화된 강제 지시사항으로 완전한 3단계 구조 달성")
    print("=" * 60)

    success = test_full_3stage_thinking_flow()

    print("\n" + "=" * 60)
    if success:
        print("🎉 **완전 성공!** Dynamic Enhanced Thinking Flow 완벽 구현")
        print("✅ 기존 문제 해결: LLM이 3단계 구조를 정확히 따름")
        print("✅ Q5 강제 생성: 100% 성공")
        print("✅ 강제 형식: 기존 패턴 완전 차단")
    else:
        print("⚠️ **개선 필요** 추가 강화 조치 검토")


if __name__ == "__main__":
    main()
