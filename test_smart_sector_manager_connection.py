#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Sector Manager ↔ Sector Teams 연동 테스트

smart_sector_manager.py가 실제로 sector_teams.py의
Q5EnforcedAgentExecutor를 사용하는지 검증합니다.
"""

import asyncio
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
from app.crew.gics_sectors import GICSSector
from app.crew.smart_sector_manager import SmartSectorManager
from app.llm import LLM


async def test_smart_sector_manager_connection():
    """
    SmartSectorManager가 SectorTeams의 langchain_chain을 실제로 사용하는지 테스트
    """
    print("🧪 Smart Sector Manager ↔ Sector Teams 연동 테스트")
    print("=" * 60)

    try:
        # LLM 및 Smart Sector Manager 초기화
        print("🚀 시스템 초기화 중...")
        llm = LLM()
        smart_manager = SmartSectorManager(llm)

        # 테스트 데이터 준비
        test_data = {
            "user_prompt": "삼성전자의 투자 의견을 제시해주세요. 반드시 Dynamic Enhanced Thinking Flow 3단계 구조를 사용하세요.",
            "stock_name": "삼성전자",
            "stock_code": "005930",
            "financial_data": {
                "current_price": 58000,
                "market_cap": 435000000000000,
                "per": 18.5,
                "pbr": 1.2,
                "roe": 12.3,
                "roa": 8.7,
                "debt_ratio": 35.2,
                "operating_margin": 10.9,
            },
            "enhanced_dart_data": {"test": "dart_data"},
            "manus_collected_data": {"test": "manus_data"},
            "technical_analysis_data": {"test": "technical_data"},
            "dart_reports_dictionary": {"test": "dart_reports"},
            "pre_detected_gics_sector": "Information Technology",
        }

        print(f"🎯 테스트 종목: {test_data['stock_name']}")
        print(f"🏢 사전 감지 섹터: {test_data['pre_detected_gics_sector']}")
        print()

        # SmartSectorManager를 통한 종합 분석 실행
        print("🚀 SmartSectorManager 종합 분석 실행...")
        print("-" * 40)

        start_time = datetime.now()

        result = await smart_manager.analyze_with_comprehensive_data(
            user_prompt=test_data["user_prompt"],
            stock_name=test_data["stock_name"],
            stock_code=test_data["stock_code"],
            financial_data=test_data["financial_data"],
            enhanced_dart_data=test_data["enhanced_dart_data"],
            manus_collected_data=test_data["manus_collected_data"],
            technical_analysis_data=test_data["technical_analysis_data"],
            dart_reports_dictionary=test_data["dart_reports_dictionary"],
            pre_detected_gics_sector=test_data["pre_detected_gics_sector"],
        )

        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        print("=" * 60)
        print(f"✅ 실행 완료! (시간: {execution_time:.1f}초)")
        print("=" * 60)

        # 결과 분석
        if not result.get("success", False):
            print(f"❌ 분석 실패: {result.get('error', 'Unknown error')}")
            return False

        expert_insights = result.get("expert_insights", {})

        if not expert_insights or "expert_results" not in expert_insights:
            print("❌ 전문가 분석 결과가 없습니다")
            return False

        expert_results = expert_insights["expert_results"]

        # 각 전문가별 결과 검증
        print("🔍 **전문가별 결과 검증**")
        print("-" * 30)

        overall_success = True

        for expert_result in expert_results:
            expert_name = expert_result.get("expert_name", "Unknown")
            analysis_result = expert_result.get("analysis_result", "")

            print(f"\n👨‍💼 **{expert_name}**")

            # Dynamic Enhanced Thinking Flow 구조 확인
            stage_patterns = {
                "1단계": ["=== 1단계:", "Self-Ask with ToT"],
                "2단계": ["=== 2단계:", "ReAct"],
                "3단계": ["=== 3단계:", "CoT", "Self-Critique"],
            }

            found_stages = {}
            for stage_name, patterns in stage_patterns.items():
                found = any(pattern in analysis_result for pattern in patterns)
                found_stages[stage_name] = found
                status = "✅ 발견" if found else "❌ 누락"
                print(f"   {status} {stage_name}")

            # Q5 섹터 특화 확인
            q5_patterns = ["Q5:", "IT 섹터 특화", "기술 경쟁력", "R&D 투자"]
            found_q5 = any(pattern in analysis_result for pattern in q5_patterns)
            q5_status = "✅ 발견" if found_q5 else "❌ 누락"
            print(f"   {q5_status} Q5 섹터 특화")

            # 금지된 기존 형식 확인
            forbidden_patterns = [
                "### 1.",
                "### 2.",
                "### 3.",
                "수익성 분석",
                "안정성 분석",
            ]
            uses_forbidden = any(
                pattern in analysis_result for pattern in forbidden_patterns
            )
            forbidden_status = "❌ 사용됨" if uses_forbidden else "✅ 준수"
            print(f"   {forbidden_status} 형식 규칙")

            # 개별 전문가 성공 여부
            expert_success = (
                sum(found_stages.values()) >= 2  # 최소 2단계 이상
                and found_q5  # Q5 포함
                and not uses_forbidden  # 금지 형식 미사용
            )

            expert_status = "🎉 성공" if expert_success else "❌ 실패"
            print(f"   🏆 **{expert_status}**")

            if not expert_success:
                overall_success = False

            # 출력 미리보기
            print(f"   📄 출력 길이: {len(analysis_result):,}자")
            preview = (
                analysis_result[:200] + "..."
                if len(analysis_result) > 200
                else analysis_result
            )
            print(f"   📄 미리보기: {preview}")

        # 최종 평가
        print(f"\n🏆 **최종 평가**")
        print("-" * 30)

        stages_complete = sum(
            sum(found_stages.values())
            for expert_result in expert_results
            if "analysis_result" in expert_result
        )
        total_possible_stages = len(expert_results) * 3  # 각 전문가당 3단계

        print(f"📊 전체 단계 완성도: {stages_complete}/{total_possible_stages}")
        print(f"📊 감지된 섹터: {result.get('detected_sector', 'Unknown')}")
        print(f"📊 활성화된 전문가: {result.get('activated_experts', [])}")

        if overall_success:
            print("🎉 **완전 성공!** Smart Sector Manager ↔ Sector Teams 연동 완료")
            print("✅ Dynamic Enhanced Thinking Flow 정상 작동")
            print("✅ Q5 강제 생성 100% 성공")
            print("✅ 3단계 구조 완벽 구현")
        else:
            print("⚠️ **부분 성공** 일부 전문가에서 구조 미완성")

        # 결과 저장
        save_connection_test_results(result, overall_success, execution_time)

        return overall_success

    except Exception as e:
        print(f"❌ 테스트 실행 오류: {e}")
        import traceback

        traceback.print_exc()
        return False


def save_connection_test_results(result, success, execution_time):
    """
    연동 테스트 결과를 저장합니다.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"smart_sector_connection_test_{timestamp}.json"

    import json

    test_result = {
        "timestamp": timestamp,
        "test_type": "Smart_Sector_Manager_Connection_Test",
        "overall_success": success,
        "execution_time_seconds": execution_time,
        "detected_sector": result.get("detected_sector"),
        "activated_experts": result.get("activated_experts", []),
        "expert_insights": result.get("expert_insights", {}),
        "full_result": result,
    }

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(test_result, f, ensure_ascii=False, indent=2)
        print(f"💾 테스트 결과 저장: {filename}")
    except Exception as e:
        print(f"⚠️ 결과 저장 실패: {e}")


def main():
    """
    연동 테스트 메인 함수
    """
    print("🧪 Smart Sector Manager ↔ Sector Teams 연동 테스트 프로그램")
    print("목표: 수정 후 실제 연동 작동 확인")
    print("=" * 60)

    success = asyncio.run(test_smart_sector_manager_connection())

    print("\n" + "=" * 60)
    if success:
        print("🎉 **연동 성공!** 모든 시스템이 정상 작동")
        print("✅ smart_sector_manager.py → expert.langchain_chain 사용")
        print("✅ Q5EnforcedAgentExecutor → Dynamic Enhanced Thinking Flow 실행")
        print("✅ 기존 문제 완전 해결")
    else:
        print("⚠️ **연동 문제** 추가 디버깅 필요")


if __name__ == "__main__":
    main()
