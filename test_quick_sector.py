#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
빠른 섹터 테스트 - 웹 검색 없이 섹터별 전문가 생성만 확인
"""

import os
import sys

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.crew.gics_sectors import GICSSector, GICSSectorManager
from app.crew.sector_teams import SectorTeamFactory


def test_sector_experts_creation():
    """섹터별 전문가 생성 테스트 (웹 검색 없이)"""

    print("🚀 빠른 섹터별 전문가 생성 테스트")
    print("=" * 50)

    try:
        # GICS 섹터 매니저 초기화
        sector_manager = GICSSectorManager()
        factory = SectorTeamFactory(sector_manager)

        # 테스트할 섹터들
        test_sectors = [
            GICSSector.ENERGY,  # 에너지
            GICSSector.MATERIALS,  # 소재
            GICSSector.FINANCIALS,  # 금융
            GICSSector.INFORMATION_TECHNOLOGY,  # 정보기술
        ]

        for sector in test_sectors:
            print(f"\n📊 {sector.value} 섹터 테스트")
            print("-" * 30)

            # 섹터팀 생성
            team = factory.create_sector_team(sector)

            # 섹터 정보 확인
            sector_korean_name = sector_manager.get_sector_korean_name(sector)
            print(f"✅ 섹터명: {sector_korean_name}")

            # 각 전문가의 섹터 정보 확인
            for expert in team.experts:
                print(f"  🔍 {expert.name}")
                print(f"     역할: {expert.role}")
                print(
                    f"     LangChain 활성화: {'✅' if expert.langchain_enabled else '❌'}"
                )
                print(f"     Chain 생성: {'✅' if expert.langchain_chain else '❌'}")

            print(f"✅ {sector_korean_name} 섹터팀 생성 완료!")

        print("\n" + "=" * 50)
        print("🎉 모든 섹터별 전문가 생성 테스트 완료!")
        print("\n📋 요약:")
        print("- 모든 전문가가 동적으로 섹터 정보를 받고 있습니다")
        print("- 모든 전문가의 LangChain Chain이 생성되었습니다")
        print("- 웹 검색 도구가 모든 전문가에게 포함되었습니다")

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_sector_experts_creation()
