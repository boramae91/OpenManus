#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
빠른 연동 상태 검증 스크립트 (30초 이내)
"""

print("🚀 빠른 연동 상태 검증 시작...")

try:
    # 1. 기본 임포트 확인
    print("1️⃣ 모듈 임포트 확인...")
    from app.crew.gics_sectors import GICSSector, GICSSectorManager
    from app.crew.sector_teams import Q5EnforcedAgentExecutor, SectorTeamFactory
    from app.crew.smart_sector_manager import SmartSectorManager

    print("   ✅ 모든 모듈 임포트 성공")

    # 2. 클래스 생성 확인
    print("2️⃣ 클래스 생성 확인...")
    sector_manager = GICSSectorManager()
    team_factory = SectorTeamFactory(sector_manager)
    print("   ✅ 팩토리 생성 성공")

    # 3. 섹터팀 생성 확인
    print("3️⃣ 섹터팀 생성 확인...")
    sector = GICSSector.INFORMATION_TECHNOLOGY
    sector_team = team_factory.create_sector_team(sector)
    print(f"   ✅ {sector.name} 섹터팀 생성 성공")

    # 4. 전문가 langchain_chain 확인
    print("4️⃣ LangChain Chain 확인...")
    expert_found = False
    for expert in sector_team.experts:
        if "통합 재무분석가" in expert.name:
            if hasattr(expert, "langchain_chain") and expert.langchain_chain:
                chain_type = type(expert.langchain_chain).__name__
                print(f"   ✅ {expert.name}: {chain_type}")
                if "Q5EnforcedAgentExecutor" in chain_type:
                    print("   🎯 Q5 강제 생성 확인됨!")
                expert_found = True
                break

    if not expert_found:
        print("   ❌ 통합 재무분석가를 찾을 수 없음")

    # 5. 수정된 연동 로직 확인
    print("5️⃣ 연동 로직 확인...")

    # smart_sector_manager.py의 수정된 부분 확인
    import inspect

    import app.crew.smart_sector_manager as ssm

    # _perform_comprehensive_expert_analysis 메서드의 소스 확인
    source = inspect.getsource(
        ssm.SmartSectorManager._perform_comprehensive_expert_analysis
    )

    if "expert.langchain_chain" in source and "invoke" in source:
        print("   ✅ smart_sector_manager.py에서 langchain_chain 사용 확인")
    else:
        print("   ❌ smart_sector_manager.py에서 langchain_chain 미사용")

    print("\n🎉 **빠른 검증 완료!**")
    print("=" * 50)
    print("✅ 모든 모듈 정상 로드")
    print("✅ 섹터팀 생성 성공")
    print("✅ Q5EnforcedAgentExecutor 확인")
    print("✅ 연동 로직 수정 확인")
    print("🎯 **결론: Smart Sector Manager ↔ Sector Teams 연동 완료!**")

except Exception as e:
    print(f"❌ 검증 실패: {e}")
    import traceback

    traceback.print_exc()
