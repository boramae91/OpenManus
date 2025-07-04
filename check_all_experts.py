#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모든 전문가들의 LangChain 상태 확인 테스트
Day 2에서 누락된 테스트가 있는지 확인해요
"""

import os
import sys
from datetime import datetime

print("🔍 모든 전문가 LangChain 상태 확인 시작!")
print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

try:
    from app.crew.gics_sectors import GICSSector, GICSSectorManager
    from app.crew.sector_teams import SectorTeamFactory

    print("✅ 모듈 import 성공")

    # IT 섹터 팀 생성
    sector_manager = GICSSectorManager()
    factory = SectorTeamFactory(sector_manager)
    it_sector = GICSSector.INFORMATION_TECHNOLOGY
    it_team = factory.create_sector_team(it_sector)

    print(f"\n📋 IT 섹터 팀 전문가 현황 (총 {len(it_team.experts)}명):")
    print("=" * 80)

    expert_status = {}

    for i, expert in enumerate(it_team.experts, 1):
        print(f"\n{i}️⃣ {expert.name}")
        print(f"   - 역할: {expert.role}")
        print(f"   - LangChain 활성화: {expert.langchain_enabled}")
        print(f"   - Chain 존재: {expert.langchain_chain is not None}")

        # 테스트 상태 기록
        expert_status[expert.role] = {
            "name": expert.name,
            "langchain_enabled": expert.langchain_enabled,
            "chain_exists": expert.langchain_chain is not None,
            "test_file_exists": False,
        }

    print(f"\n📊 전문가별 테스트 파일 존재 여부:")
    print("=" * 50)

    test_files = [
        # "test_fundamental_analyst_langchain.py",  # 🚫 비활성화 (통합 재무분석가로 대체)
        # "test_valuation_specialist_langchain.py",  # 🚫 비활성화 (통합 재무분석가로 대체)
        # "test_risk_assessor_langchain.py",  # 🚫 비활성화 (개발 시간 절약)
        # "test_industry_expert_langchain.py",  # 🚫 비활성화 (개발 시간 절약)
        "test_technical_analyst_langchain.py",
        # "test_footnote_specialist_langchain.py",  # 🚫 비활성화 (개발 시간 절약)
    ]

    for test_file in test_files:
        exists = os.path.exists(test_file)
        print(f"   {test_file}: {'✅ 존재' if exists else '❌ 없음'}")

        # 해당하는 전문가 찾기
        for role, status in expert_status.items():
            if any(keyword in test_file.lower() for keyword in role.lower().split()):
                status["test_file_exists"] = exists

    print(f"\n🎯 테스트 누락 현황:")
    print("=" * 50)

    missing_tests = []
    for role, status in expert_status.items():
        if not status["test_file_exists"]:
            missing_tests.append(role)
            print(f"   ❌ {role}: 테스트 파일 없음")
        else:
            print(f"   ✅ {role}: 테스트 파일 존재")

    if missing_tests:
        print(f"\n⚠️ 테스트가 누락된 전문가들:")
        for role in missing_tests:
            print(f"   - {role}")
    else:
        print(f"\n🎉 모든 전문가의 테스트 파일이 존재합니다!")

    print(f"\n📈 LangChain 활성화 현황:")
    print("=" * 50)

    enabled_count = sum(
        1 for status in expert_status.values() if status["langchain_enabled"]
    )
    chain_count = sum(1 for status in expert_status.values() if status["chain_exists"])

    print(f"   - LangChain 활성화: {enabled_count}/{len(expert_status)}")
    print(f"   - Chain 생성: {chain_count}/{len(expert_status)}")

    if enabled_count == len(expert_status) and chain_count == len(expert_status):
        print("   🎉 모든 전문가가 LangChain으로 완전히 설정되었습니다!")
    else:
        print("   ⚠️ 일부 전문가의 LangChain 설정이 누락되었습니다.")

    print(f"\n✅ 상태 확인 완료!")

except Exception as e:
    print(f"❌ 확인 실패: {e}")
    import traceback

    traceback.print_exc()
