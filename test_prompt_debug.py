#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Thinking Flow 프롬프트 디버깅

실제 시스템 프롬프트에 Dynamic Enhanced Thinking Flow가
제대로 포함되는지 확인하는 디버깅 스크립트입니다.
"""

import os
import sys

# 프로젝트 루트 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 환경 변수 로드
from dotenv import load_dotenv

load_dotenv()

# 필요한 모듈들 import
from app.crew.gics_sectors import GICSSector, GICSSectorManager
from app.crew.prompt_components import PromptComponents


def debug_enhanced_thinking_flow():
    """
    Enhanced Thinking Flow 생성 내용을 디버깅합니다.
    """
    print("🧪 Enhanced Thinking Flow 프롬프트 디버깅")
    print("=" * 60)

    try:
        # 섹터 설정
        sector = GICSSector.INFORMATION_TECHNOLOGY
        sector_manager = GICSSectorManager()
        sector_korean_name = sector_manager.get_sector_korean_name(sector)

        print(f"🎯 테스트 섹터: 🖥️ {sector_korean_name}")
        print()

        # Enhanced Thinking Flow 생성
        print("🚀 Enhanced Thinking Flow 생성 중...")
        enhanced_thinking_flow = PromptComponents.get_enhanced_analyst_thinking_flow(
            sector=sector, sector_manager=sector_manager
        )

        print("=" * 60)
        print("📋 **생성된 Enhanced Thinking Flow 내용**")
        print("=" * 60)
        print(enhanced_thinking_flow)
        print("=" * 60)

        # 3단계 구조 검증
        print("\n🔍 **3단계 구조 검증**")
        print("-" * 30)

        stage_patterns = [
            "=== 1단계:",
            "=== 2단계:",
            "=== 3단계:",
            "Self-Ask with ToT",
            "ReAct",
            "CoT",
            "Self-Critique",
        ]

        found_patterns = []
        for pattern in stage_patterns:
            if pattern in enhanced_thinking_flow:
                found_patterns.append(pattern)

        print(f"✅ 발견된 패턴: {found_patterns}")
        print(
            f"📊 구조 완성도: {len(found_patterns)}/{len(stage_patterns)} ({len(found_patterns)/len(stage_patterns)*100:.1f}%)"
        )

        # Q5 섹터 특화 검증
        print("\n🔍 **Q5 섹터 특화 검증**")
        print("-" * 30)

        q5_patterns = ["Q5:", "IT 섹터 특화", "기술 경쟁력", "R&D 투자", "클라우드/AI"]

        found_q5 = []
        for pattern in q5_patterns:
            if pattern in enhanced_thinking_flow:
                found_q5.append(pattern)

        print(f"✅ Q5 관련 패턴: {found_q5}")
        print(
            f"📊 Q5 완성도: {len(found_q5)}/{len(q5_patterns)} ({len(found_q5)/len(q5_patterns)*100:.1f}%)"
        )

        # 강제 지시사항 검증
        print("\n🔍 **강제 지시사항 검증**")
        print("-" * 30)

        mandatory_patterns = ["반드시", "필수", "MUST", "순서대로", "3단계"]

        found_mandatory = []
        for pattern in mandatory_patterns:
            if pattern in enhanced_thinking_flow:
                found_mandatory.append(pattern)

        print(f"✅ 강제 지시사항: {found_mandatory}")
        print(
            f"📊 강제성: {len(found_mandatory)}/{len(mandatory_patterns)} ({len(found_mandatory)/len(mandatory_patterns)*100:.1f}%)"
        )

        # 전체 평가
        print("\n🏆 **종합 평가**")
        print("-" * 30)

        total_found = len(found_patterns) + len(found_q5) + len(found_mandatory)
        total_possible = (
            len(stage_patterns) + len(q5_patterns) + len(mandatory_patterns)
        )
        overall_score = (total_found / total_possible) * 100

        print(f"📊 전체 점수: {total_found}/{total_possible} ({overall_score:.1f}%)")

        if overall_score >= 80:
            print("🎉 **우수**: Enhanced Thinking Flow가 잘 구성됨")
        elif overall_score >= 60:
            print("✅ **양호**: 대부분의 요소가 포함됨")
        else:
            print("❌ **부족**: 중요한 요소들이 누락됨")

        return overall_score >= 70

    except Exception as e:
        print(f"❌ 디버깅 오류: {e}")
        import traceback

        traceback.print_exc()
        return False


def debug_system_prompt_construction():
    """
    시스템 프롬프트 구성 과정을 디버깅합니다.
    """
    print("\n🛠️ **시스템 프롬프트 구성 디버깅**")
    print("=" * 60)

    try:
        sector = GICSSector.INFORMATION_TECHNOLOGY
        sector_manager = GICSSectorManager()

        # 각 컴포넌트 개별 확인
        print("1️⃣ unified_framework 생성...")
        unified_framework = PromptComponents.create_unified_analysis_framework(
            analysis_type="통합 재무분석",
            sector_name="정보기술",
            specific_methods=["DCF", "PER"],
        )
        print(f"   길이: {len(unified_framework)}자")

        print("2️⃣ enhanced_thinking_flow 생성...")
        enhanced_thinking_flow = PromptComponents.get_enhanced_analyst_thinking_flow(
            sector=sector, sector_manager=sector_manager
        )
        print(f"   길이: {len(enhanced_thinking_flow)}자")

        print("3️⃣ output_format 생성...")
        output_format = PromptComponents.get_output_format_template("통합 재무분석")
        print(f"   길이: {len(output_format)}자")

        # 시스템 프롬프트 예상 길이
        estimated_length = (
            len(unified_framework)
            + len(enhanced_thinking_flow)
            + len(output_format)
            + 1000
        )  # 기타 텍스트
        print(f"\n📏 예상 시스템 프롬프트 총 길이: {estimated_length:,}자")

        if estimated_length > 15000:
            print(
                "⚠️ **경고**: 시스템 프롬프트가 너무 길어서 LLM이 일부를 무시할 수 있음"
            )
        else:
            print("✅ **적정**: 시스템 프롬프트 길이가 적절함")

        return estimated_length < 15000

    except Exception as e:
        print(f"❌ 시스템 프롬프트 디버깅 오류: {e}")
        return False


def main():
    """
    Enhanced Thinking Flow 디버깅 메인 함수
    """
    print("🧪 Enhanced Thinking Flow 프롬프트 디버깅 프로그램")
    print("목표: LLM이 3단계 구조를 무시하는 원인 분석")
    print("=" * 60)

    # 1. Enhanced Thinking Flow 내용 확인
    flow_success = debug_enhanced_thinking_flow()

    # 2. 시스템 프롬프트 구성 확인
    prompt_success = debug_system_prompt_construction()

    # 3. 결론 및 권장사항
    print("\n🎯 **진단 결과**")
    print("=" * 60)

    if flow_success and prompt_success:
        print("✅ Enhanced Thinking Flow와 프롬프트 구조 모두 정상")
        print("💡 **추정 원인**: LLM이 복잡한 지시사항을 무시하고 기존 패턴 선호")
        print("🛠️ **해결책**: 더 강력한 강제 지시사항과 예시 추가 필요")
    elif flow_success and not prompt_success:
        print("⚠️ Enhanced Thinking Flow는 정상, 시스템 프롬프트가 너무 김")
        print("🛠️ **해결책**: 시스템 프롬프트 길이 단축 필요")
    elif not flow_success and prompt_success:
        print("❌ Enhanced Thinking Flow 자체에 문제")
        print("🛠️ **해결책**: Enhanced Thinking Flow 구조 개선 필요")
    else:
        print("❌ 둘 다 문제 있음")
        print("🛠️ **해결책**: 전면적인 프롬프트 재설계 필요")


if __name__ == "__main__":
    main()
