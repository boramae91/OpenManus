#!/usr/bin/env python3
"""
웹검색 기능 테스트 스크립트
Chat GPT 피드백의 핵심인 웹검색 기능이 작동하는지 확인
"""

import asyncio
import os
import sys

# OpenManus 프로젝트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.tool.web_search import WebSearch


async def test_web_search():
    """웹검색 기능 테스트"""

    print("🌐 웹검색 기능 테스트 시작")
    print("=" * 50)

    try:
        web_search_tool = WebSearch()

        # 테스트 쿼리들 (Chat GPT 피드백에서 필요한 정보들)
        test_queries = [
            "삼성전자 ROE 3년 추이",
            "삼성전자 경쟁사 TSMC SK하이닉스 비교",
            "반도체 업계 평균 PER 2024",
            "삼성전자 목표주가 컨센서스",
            "한국 국고채 3년 수익률 2024",
        ]

        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 테스트 {i}: {query}")
            print("-" * 30)

            try:
                result = await web_search_tool.execute(
                    query=query, num_results=3, lang="ko", country="kr"
                )

                if result and result.output:
                    print(f"✅ 검색 성공!")
                    print(f"📄 결과 길이: {len(result.output):,}자")
                    print(f"📖 결과 미리보기: {result.output[:200]}...")
                else:
                    print("❌ 검색 결과 없음")

            except Exception as e:
                print(f"❌ 검색 실패: {e}")

        print(f"\n🎉 웹검색 기능 테스트 완료!")
        return True

    except Exception as e:
        print(f"❌ 웹검색 도구 초기화 실패: {e}")
        return False


if __name__ == "__main__":
    try:
        result = asyncio.run(test_web_search())
        if result:
            print("\n✅ 웹검색 기능이 정상 작동합니다!")
            print("💡 이제 펀더멘탈 분석에서 웹검색을 활용할 수 있습니다.")
        else:
            print("\n❌ 웹검색 기능에 문제가 있습니다.")
            print("🔧 웹검색 도구 설정을 확인해주세요.")
    except Exception as e:
        print(f"\n❌ 테스트 실행 오류: {e}")
