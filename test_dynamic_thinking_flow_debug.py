#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dynamic Enhanced Thinking Flow 디버깅 테스트

수정 후 섹터별 동적 질문 생성이 제대로 작동하는지 검증합니다.
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


def test_dynamic_question_generation():
    """
    Dynamic Enhanced Thinking Flow 테스트
    """
    print("🧪 Dynamic Enhanced Thinking Flow 디버깅 테스트")
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

        # 간단한 테스트 입력 (회사명 명시)
        test_input = {
            "input": """
삼성전자의 IT 섹터 특화 분석을 수행해주세요.

Enhanced Thinking Flow 1단계만 실행하여
동적으로 생성된 섹터별 Q5 질문이 포함되는지 확인해주세요.

제공된 기본 정보:
- 현재 주가: 58,000원
- 시가총액: 435조원
- PER: 18.5
""",
            "chat_history": [],
        }

        print("🚀 Dynamic Enhanced Thinking Flow 실행...")
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

        # Dynamic Q5 검증
        print("🔍 **Dynamic Q5 검증 결과**")
        print("-" * 30)

        it_q5_keywords = [
            "기술 경쟁력",
            "플랫폼 점유율",
            "R&D 투자",
            "클라우드/AI 전환",
            "반도체 사이클",
            "고객 락인 효과",
        ]

        found_keywords = []
        for keyword in it_q5_keywords:
            if keyword in output:
                found_keywords.append(keyword)

        if found_keywords:
            print(f"✅ IT 섹터 특화 Q5 키워드 발견: {found_keywords}")
            print(
                f"🎯 동적 질문 생성 성공률: {len(found_keywords)}/{len(it_q5_keywords)} ({len(found_keywords)/len(it_q5_keywords)*100:.1f}%)"
            )
        else:
            print("❌ IT 섹터 특화 Q5 키워드 없음")

        # Q5 구조 검증
        q5_structure_found = any(
            [
                "Q5:" in output,
                "Q5-1:" in output,
                "Q5-2:" in output,
                "IT 섹터 특화" in output,
                "🖥️" in output,
            ]
        )

        print(f"📋 Q5 구조 발견: {'✅ 발견' if q5_structure_found else '❌ 누락'}")

        # 전체 성공 판정
        dynamic_success = len(found_keywords) >= 3 and q5_structure_found
        print(
            f"🏆 Dynamic Enhanced Thinking Flow: {'🎉 성공' if dynamic_success else '❌ 실패'}"
        )

        # 출력 미리보기
        print("\n📄 **출력 미리보기 (처음 500자)**")
        print("-" * 30)
        preview = output[:500] + "..." if len(output) > 500 else output
        print(preview)

        return dynamic_success

    except Exception as e:
        print(f"❌ 테스트 실행 오류: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """
    Dynamic Enhanced Thinking Flow 디버깅 메인
    """
    print("🧪 Dynamic Enhanced Thinking Flow 디버깅 프로그램")
    print("목표: 수정 후 섹터별 동적 질문 생성 검증")
    print("=" * 60)

    success = test_dynamic_question_generation()

    print("\n" + "=" * 60)
    if success:
        print("🎉 **성공!** Dynamic Enhanced Thinking Flow 정상 작동")
        print("✅ 기존 문제: 일반 Q1-Q4만 생성")
        print("✅ 수정 결과: IT 섹터 특화 Q5 동적 생성")
    else:
        print("❌ **실패!** 추가 디버깅 필요")
        print("⚠️ 원인 분석 및 추가 수정 검토")


if __name__ == "__main__":
    main()
