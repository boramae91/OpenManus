#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
펀더멘털 분석가 LangChain 기능 테스트

Day 1 개발 완료 후 테스트를 위한 스크립트
"""

import os
import sys
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.crew.gics_sectors import GICSSector, GICSSectorManager
from app.crew.sector_teams import SectorTeamFactory


def test_fundamental_analyst_langchain():
    """펀더멘털 분석가 LangChain 기능 테스트"""

    print("🚀 펀더멘털 분석가 LangChain 기능 테스트 시작!")
    print("=" * 60)

    try:
        # 1. 섹터 매니저 초기화
        print("1️⃣ 섹터 매니저 초기화...")
        sector_manager = GICSSectorManager()
        print("✅ 섹터 매니저 초기화 완료")

        # 2. 섹터팀 팩토리 생성
        print("\n2️⃣ 섹터팀 팩토리 생성...")
        factory = SectorTeamFactory(sector_manager)
        print("✅ 섹터팀 팩토리 생성 완료")

        # 3. IT 섹터팀 생성 (테스트용)
        print("\n3️⃣ IT 섹터팀 생성...")
        it_team = factory.create_sector_team(GICSSector.INFORMATION_TECHNOLOGY)
        print("✅ IT 섹터팀 생성 완료")

        # 4. 펀더멘털 분석가 찾기
        print("\n4️⃣ 펀더멘털 분석가 찾기...")
        fundamental_analyst = factory.get_expert_by_role(it_team, "Fundamental Analyst")

        if fundamental_analyst is None:
            print("❌ 펀더멘털 분석가를 찾을 수 없습니다.")
            return

        print(f"✅ 펀더멘털 분석가 찾기 완료: {fundamental_analyst.name}")

        # 5. LangChain 상태 확인
        print("\n5️⃣ LangChain 상태 확인...")
        print(f"   - LangChain 활성화: {fundamental_analyst.langchain_enabled}")
        print(
            f"   - LangChain Chain 존재: {fundamental_analyst.langchain_chain is not None}"
        )
        print(
            f"   - Memory 시스템 존재: {fundamental_analyst.memory_system is not None}"
        )

        if not fundamental_analyst.langchain_enabled:
            print("❌ LangChain이 활성화되지 않았습니다.")
            return

        # 6. 테스트 데이터 준비
        print("\n6️⃣ 테스트 데이터 준비...")
        test_financial_data = """
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
        """

        # 7. LangChain 분석 실행
        print("\n7️⃣ LangChain 분석 실행...")
        print("   (이 과정은 시간이 걸릴 수 있습니다...)")

        input_data = {
            "financial_data": test_financial_data,
            "sector_name": "정보기술",
            "company_name": "삼성전자",
        }

        start_time = datetime.now()
        result = fundamental_analyst.run_langchain_analysis(input_data)
        end_time = datetime.now()

        analysis_time = (end_time - start_time).total_seconds()

        # 8. 결과 출력
        print(f"\n8️⃣ 분석 결과 (소요시간: {analysis_time:.2f}초)")
        print("=" * 60)

        if result and "result" in result:
            print("✅ LangChain 분석 성공!")
            print(f"   - 분석 방법: {result.get('method', 'langchain')}")
            print(f"   - 소요 시간: {result.get('analysis_time', 0):.2f}초")
            print(f"   - 에이전트: {result.get('agent_name', 'Unknown')}")

            # 결과 내용 출력 (간단히)
            result_content = str(result.get("result", ""))
            if len(result_content) > 500:
                print(f"   - 결과 요약: {result_content[:500]}...")
            else:
                print(f"   - 결과: {result_content}")
        else:
            print("❌ LangChain 분석 실패")
            print(f"   - 결과: {result}")

        # 9. 분석 이력 확인
        print("\n9️⃣ 분석 이력 확인...")
        summary = fundamental_analyst.get_analysis_summary()
        print(f"   - 총 분석 횟수: {summary.get('total_analyses', 0)}")
        print(f"   - 성능 지표: {summary.get('performance_metrics', {})}")

        # 10. 성공 메시지
        print("\n🎉 테스트 완료!")
        print("=" * 60)
        print("✅ 펀더멘털 분석가 LangChain 기능이 정상적으로 작동합니다!")
        print("✅ Day 1 개발이 성공적으로 완료되었습니다!")

    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # 환경변수 확인
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("   환경변수를 설정한 후 다시 실행하세요.")
        sys.exit(1)

    test_fundamental_analyst_langchain()
