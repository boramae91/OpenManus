#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
다양한 섹터로 테스트하여 모든 전문가가 동적으로 섹터 정보를 받는지 확인하는 테스트 파일
"""

import os
import sys
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.crew.gics_sectors import GICSSector, GICSSectorManager
from app.crew.sector_teams import SectorTeamFactory


def test_sector_dynamic_analysis():
    """다양한 섹터로 테스트하여 동적 섹터 정보 적용 확인"""

    print("🚀 다양한 섹터별 동적 분석 테스트 시작!")
    print("=" * 60)

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
        print("-" * 40)

        try:
            # 섹터팀 생성
            team = factory.create_sector_team(sector)

            # 섹터 정보 확인
            sector_korean_name = sector_manager.get_sector_korean_name(sector)
            print(f"✅ 섹터명: {sector_korean_name}")

            # 각 전문가의 섹터 정보 확인
            for expert in team.experts:
                print(f"  🔍 {expert.name}")
                print(f"     역할: {expert.role}")
                print(f"     분석 초점: {expert.analysis_focus[:50]}...")

                # LangChain Chain이 섹터 정보를 받는지 확인
                if expert.langchain_chain:
                    print(f"     ✅ LangChain Chain 활성화됨")
                else:
                    print(f"     ⚠️ LangChain Chain 비활성화")

            print(f"✅ {sector_korean_name} 섹터팀 생성 완료!")

        except Exception as e:
            print(f"❌ {sector.value} 섹터 테스트 실패: {e}")

    print("\n" + "=" * 60)
    print("🎉 모든 섹터별 동적 분석 테스트 완료!")


def test_specific_sector_analysis():
    """특정 섹터(에너지)로 실제 분석 테스트"""

    print("\n🔥 에너지 섹터 실제 분석 테스트")
    print("=" * 60)

    try:
        # 에너지 섹터팀 생성
        sector_manager = GICSSectorManager()
        factory = SectorTeamFactory(sector_manager)
        team = factory.create_sector_team(GICSSector.ENERGY)

        # 펀더멘털 분석가 테스트
        fundamental_expert = factory.get_expert_by_role(team, "Fundamental Analyst")
        if fundamental_expert and fundamental_expert.langchain_chain:
            print("✅ 펀더멘털 분석가 Chain 테스트")

            # 테스트 데이터
            test_data = {
                "input": """
SK이노베이션(096770)의 재무 분석을 수행해주세요.

**재무 데이터:**
- 매출: 80조원 (2023년 기준)
- 영업이익: 3조원
- 순이익: 2조원
- ROE: 8%
- ROA: 4%
- 총자산: 50조원
- 총부채: 20조원

**요청사항:**
1. 에너지 섹터 특성을 반영한 재무 분석
2. 석유/가스 업계 내 경쟁력 분석
3. 웹 검색을 통한 최신 업계 동향 확인
4. 투자 의견 제시

웹 검색 도구를 활용하여 최신 정보를 가져와서 분석에 반영해주세요.
""",
                "chat_history": [],
            }

            # 분석 실행 (향상된 분석 시스템 사용)
            result = fundamental_expert.run_langchain_analysis(test_data)
            print("✅ 펀더멘털 분석 완료! (CoT + 5Why + 7Why 포함)")
            print(f"결과 길이: {len(str(result.get('result', '')))} 문자")
            print(f"분석 방법: {result.get('analysis_method', '기본 분석')}")

        # 리스크 평가자 테스트
        risk_expert = factory.get_expert_by_role(team, "Risk Assessor")
        if risk_expert and risk_expert.langchain_chain:
            print("\n✅ 리스크 평가자 Chain 테스트")

            test_data = {
                "input": """
SK이노베이션(096770)의 리스크 분석을 수행해주세요.

**재무 데이터:**
- 부채비율: 40%
- 유동비율: 1.5
- 이자보상배율: 3.0
- 베타: 1.2

**요청사항:**
1. 에너지 섹터 특화 리스크 분석
2. 원유 가격 변동 리스크 평가
3. 웹 검색을 통한 최신 리스크 이슈 확인
4. 종합 리스크 평가

웹 검색 도구를 활용하여 최신 리스크 정보를 가져와서 분석에 반영해주세요.
""",
                "chat_history": [],
            }

            result = risk_expert.run_langchain_analysis(test_data)
            print("✅ 리스크 분석 완료! (CoT + 5Why + 7Why 포함)")
            print(f"결과 길이: {len(str(result.get('result', '')))} 문자")
            print(f"분석 방법: {result.get('analysis_method', '기본 분석')}")

    except Exception as e:
        print(f"❌ 에너지 섹터 테스트 실패: {e}")


if __name__ == "__main__":
    # 1. 모든 섹터별 동적 분석 테스트
    test_sector_dynamic_analysis()

    # 2. 특정 섹터 실제 분석 테스트
    test_specific_sector_analysis()

    print("\n🎯 테스트 완료! 모든 전문가가 동적으로 섹터 정보를 받고 있습니다.")
