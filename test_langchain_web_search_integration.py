# -*- coding: utf-8 -*-
"""
LangChain 웹 검색 통합 테스트

개선된 시스템이 제대로 작동하는지 확인하는 테스트 파일이에요!
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.crew.gics_sectors import GICSSector, GICSSectorManager
from app.crew.sector_teams import SectorTeamFactory
from app.tool.langchain_web_search import LangChainWebSearchTool


async def test_web_search_tool():
    """웹 검색 도구 테스트"""
    print("🔍 웹 검색 도구 테스트 시작...")

    async with LangChainWebSearchTool() as search_tool:
        # 기본 검색 테스트
        print("\n1. 기본 검색 테스트")
        result = await search_tool.search("삼성전자 재무비율 2024")
        print(f"검색 결과: {json.dumps(result, ensure_ascii=False, indent=2)}")

        # 재무 데이터 검색 테스트
        print("\n2. 재무 데이터 검색 테스트")
        financial_result = await search_tool.search_financial_data(
            "삼성전자", "financial_ratios"
        )
        print(
            f"재무 데이터 검색 결과: {json.dumps(financial_result, ensure_ascii=False, indent=2)}"
        )

        # 경쟁사 검색 테스트
        print("\n3. 경쟁사 검색 테스트")
        competitor_result = await search_tool.search_financial_data(
            "삼성전자", "competitors"
        )
        print(
            f"경쟁사 검색 결과: {json.dumps(competitor_result, ensure_ascii=False, indent=2)}"
        )


async def test_sector_team_with_web_search():
    """웹 검색이 포함된 섹터팀 테스트"""
    print("\n🏢 웹 검색이 포함된 섹터팀 테스트 시작...")

    # GICS 섹터 매니저 초기화
    sector_manager = GICSSectorManager()

    # 섹터팀 팩토리 초기화
    factory = SectorTeamFactory(sector_manager)

    # 정보기술 섹터팀 생성
    it_sector = GICSSector.INFORMATION_TECHNOLOGY
    team = factory.create_sector_team(it_sector)

    print(f"✅ {team.team_name} 생성 완료")
    print(f"전문가 수: {len(team.experts)}명")

    # 각 전문가의 LangChain Chain 상태 확인
    for i, expert in enumerate(team.experts, 1):
        print(f"\n{i}. {expert.name}")
        print(f"   LangChain 활성화: {expert.langchain_enabled}")
        print(f"   LangChain Chain 존재: {expert.langchain_chain is not None}")
        print(f"   역할: {expert.role}")

        if expert.langchain_chain:
            print(f"   Chain 타입: {type(expert.langchain_chain).__name__}")

            # 웹 검색 도구가 포함되어 있는지 확인
            if hasattr(expert.langchain_chain, "tools"):
                tools = expert.langchain_chain.tools
                web_search_tools = [tool for tool in tools if tool.name == "web_search"]
                print(f"   웹 검색 도구 포함: {len(web_search_tools) > 0}")
            else:
                print(f"   웹 검색 도구 포함: 확인 불가")


async def test_langchain_chain_execution():
    """LangChain Chain 실행 테스트"""
    print("\n🚀 LangChain Chain 실행 테스트 시작...")

    # GICS 섹터 매니저 초기화
    sector_manager = GICSSectorManager()

    # 섹터팀 팩토리 초기화
    factory = SectorTeamFactory(sector_manager)

    # 정보기술 섹터팀 생성
    it_sector = GICSSector.INFORMATION_TECHNOLOGY
    team = factory.create_sector_team(it_sector)

    # 펀더멘털 분석가 선택
    fundamental_analyst = None
    for expert in team.experts:
        if "펀더멘털" in expert.name:
            fundamental_analyst = expert
            break

    if fundamental_analyst and fundamental_analyst.langchain_chain:
        print(f"✅ {fundamental_analyst.name} LangChain Chain 테스트")

        # 테스트용 입력 데이터 (더 구체적인 정보 포함)
        test_input = {
            "input": """
삼성전자(005930)의 종합 재무 분석을 수행해주세요.

**재무 데이터:**
- 매출: 300조원 (2023년 기준)
- 영업이익: 30조원
- 순이익: 25조원
- ROE: 15%
- ROA: 8%
- 총자산: 400조원
- 총부채: 100조원
- 유동자산: 200조원
- 유동부채: 80조원

**요청사항:**
1. 위 재무 데이터를 바탕으로 핵심 재무비율 분석
2. 웹 검색을 통해 삼성전자의 최신 경쟁사 정보와 업계 동향 확인
3. 반도체 업계 내 삼성전자의 경쟁력 분석
4. 투자 의견 제시

웹 검색 도구를 활용하여 최신 정보를 가져와서 분석에 반영해주세요.
""",
            "chat_history": [],
        }

        try:
            # LangChain Chain 실행
            print("🔗 LangChain Chain 실행 중...")
            result = fundamental_analyst.langchain_chain.invoke(test_input)

            print("✅ LangChain Chain 실행 성공!")
            print(f"결과 타입: {type(result)}")

            if isinstance(result, dict):
                if "output" in result:
                    print(f"출력 결과: {result['output'][:500]}...")
                else:
                    print(f"결과 키: {list(result.keys())}")
            else:
                print(f"결과: {str(result)[:500]}...")

        except Exception as e:
            print(f"❌ LangChain Chain 실행 실패: {e}")
            import traceback

            traceback.print_exc()
    else:
        print("❌ 펀더멘털 분석가의 LangChain Chain을 찾을 수 없습니다.")


async def test_web_search_integration():
    """웹 검색 통합 테스트"""
    print("\n🔍 웹 검색 통합 테스트 시작...")

    # 웹 검색 도구 테스트
    async with LangChainWebSearchTool() as search_tool:
        # 다양한 검색 쿼리 테스트
        test_queries = [
            "삼성전자 시장점유율 2024",
            "삼성전자 경쟁사 재무비율",
            "반도체 업계 동향 2024",
            "삼성전자 애널리스트 목표가",
        ]

        for query in test_queries:
            print(f"\n검색 쿼리: {query}")
            result = await search_tool.search(query, max_results=3)

            if result.get("success"):
                results = result.get("results", [])
                print(f"검색 결과 수: {len(results)}")

                for i, item in enumerate(results, 1):
                    print(f"  {i}. {item['title']}")
                    print(f"     URL: {item['url']}")
                    print(f"     내용: {item['snippet'][:100]}...")
            else:
                print(f"검색 실패: {result.get('error')}")


async def main():
    """메인 테스트 함수"""
    print("🧪 LangChain 웹 검색 통합 테스트 시작")
    print("=" * 60)

    try:
        # 1. 웹 검색 도구 테스트
        await test_web_search_tool()

        # 2. 섹터팀 웹 검색 통합 테스트
        await test_sector_team_with_web_search()

        # 3. LangChain Chain 실행 테스트
        await test_langchain_chain_execution()

        # 4. 웹 검색 통합 테스트
        await test_web_search_integration()

        print("\n🎉 모든 테스트 완료!")

    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # 환경변수 설정 (필요한 경우)
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("테스트를 계속 진행하지만 일부 기능이 제한될 수 있습니다.")

    # 테스트 실행
    asyncio.run(main())
