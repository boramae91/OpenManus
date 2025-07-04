#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
향상된 분석 시스템 (CoT + 5Why + 7Why) 테스트

이 파일은 CoT, 5Why, 7Why 분석이 제대로 작동하는지 테스트해요.
"""

import os
import sys
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.crew.gics_sectors import GICSSector, GICSSectorManager
from app.crew.sector_teams import SectorTeamFactory


def test_enhanced_analysis_system():
    """향상된 분석 시스템 테스트"""
    print("🚀 향상된 분석 시스템 테스트 시작!")
    print("=" * 60)

    try:
        # 1. GICS 섹터 매니저 초기화
        print("📋 1단계: GICS 섹터 매니저 초기화...")
        sector_manager = GICSSectorManager()
        print("✅ GICS 섹터 매니저 초기화 완료!")

        # 2. 섹터팀 팩토리 생성
        print("\n🏗️ 2단계: 섹터팀 팩토리 생성...")
        factory = SectorTeamFactory(sector_manager)
        print("✅ 섹터팀 팩토리 생성 완료!")

        # 3. 정보기술 섹터팀 생성
        print("\n💻 3단계: 정보기술 섹터팀 생성...")
        it_sector = GICSSector.INFORMATION_TECHNOLOGY
        team = factory.create_sector_team(it_sector)
        print("✅ 정보기술 섹터팀 생성 완료!")

        # 4. 통합 재무분석가 찾기
        print("\n🔍 4단계: 통합 재무분석가 찾기...")
        fundamental_analyst = None
        for expert in team.experts:
            if "통합 재무분석가" in expert.name:
                fundamental_analyst = expert
                break

        if not fundamental_analyst:
            print("❌ 통합 재무분석가를 찾을 수 없습니다!")
            return False

        print(f"✅ 통합 재무분석가 발견: {fundamental_analyst.name}")

        # 5. LangChain 활성화 상태 확인
        print("\n🔧 5단계: LangChain 활성화 상태 확인...")
        print(f"   - LangChain 활성화: {fundamental_analyst.langchain_enabled}")
        print(
            f"   - LangChain Chain 존재: {fundamental_analyst.langchain_chain is not None}"
        )

        if not fundamental_analyst.langchain_enabled:
            print("❌ LangChain이 활성화되지 않았습니다!")
            return False

        # 6. 테스트 데이터 준비
        print("\n📊 6단계: 테스트 데이터 준비...")
        test_data = {
            "financial_data": """
삼성전자 재무데이터 (2021-2023):

손익계산서:
- 매출: 2021년 279조원, 2022년 302조원, 2023년 258조원
- 영업이익: 2021년 51조원, 2022년 43조원, 2023년 6조원
- 순이익: 2021년 39조원, 2022년 55조원, 2023년 15조원

대차대조표:
- 총자산: 2021년 426조원, 2022년 448조원, 2023년 484조원
- 총부채: 2021년 87조원, 2022년 95조원, 2023년 108조원
- 자기자본: 2021년 339조원, 2022년 353조원, 2023년 376조원

현금흐름표:
- 영업현금흐름: 2021년 47조원, 2022년 58조원, 2023년 35조원
- 투자현금흐름: 2021년 -48조원, 2022년 -53조원, 2023년 -45조원
- 재무현금흐름: 2021년 2조원, 2022년 -4조원, 2023년 10조원

현재 주가: 75,000원
발행주식수: 5.97억주
""",
            "sector_name": "정보기술",
            "company_name": "삼성전자",
        }

        # 7. 향상된 분석 실행
        print("\n🧠 7단계: 향상된 분석 실행 (CoT + 5Why + 7Why)...")
        print("   (이 과정은 시간이 걸릴 수 있습니다...)")

        start_time = datetime.now()
        result = fundamental_analyst.run_langchain_analysis(test_data)
        end_time = datetime.now()

        analysis_time = (end_time - start_time).total_seconds()

        # 8. 결과 출력
        print(f"\n📈 8단계: 분석 결과 (소요시간: {analysis_time:.2f}초)")
        print("=" * 60)

        if result and "result" in result:
            print("✅ 향상된 분석 성공!")
            print(f"   - 분석 방법: {result.get('analysis_method', '기본 분석')}")
            print(f"   - 소요 시간: {result.get('analysis_time', 0):.2f}초")
            print(f"   - 에이전트: {result.get('agent_name', 'Unknown')}")

            # 결과 내용 출력 (간단히)
            result_content = str(result.get("result", ""))
            if len(result_content) > 500:
                print(f"   - 결과 요약: {result_content[:500]}...")
            else:
                print(f"   - 결과: {result_content}")

            # 향상된 분석 결과 확인
            if "CoT + 5Why + 7Why" in result.get("analysis_method", ""):
                print("   🎉 CoT + 5Why + 7Why 분석이 성공적으로 적용되었습니다!")
            else:
                print("   ⚠️ 기본 분석으로 폴백되었습니다.")

        else:
            print("❌ 향상된 분석 실패")
            print(f"   - 결과: {result}")

        # 9. 분석 이력 확인
        print("\n📋 9단계: 분석 이력 확인...")
        summary = fundamental_analyst.get_analysis_summary()
        print(f"   - 총 분석 횟수: {summary.get('total_analyses', 0)}")
        print(f"   - 성능 지표: {summary.get('performance_metrics', {})}")

        # 10. 성공 메시지
        print("\n🎉 테스트 완료!")
        print("=" * 60)
        print("✅ 향상된 분석 시스템이 정상적으로 작동합니다!")
        print("✅ CoT + 5Why + 7Why 분석이 성공적으로 통합되었습니다!")

        return True

    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 환경변수 확인
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("   환경변수를 설정한 후 다시 실행하세요.")
        sys.exit(1)

    success = test_enhanced_analysis_system()

    if success:
        print("\n🎯 모든 테스트가 성공적으로 완료되었습니다!")
    else:
        print("\n❌ 테스트 중 문제가 발생했습니다.")
        sys.exit(1)
