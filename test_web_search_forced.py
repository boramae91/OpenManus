#!/usr/bin/env python3
"""
웹검색 강제 실행 시스템 테스트
Chat GPT 피드백을 반영한 개선된 펀더멘털 분석 테스트
"""

import asyncio
import os
import sys
from datetime import datetime

# OpenManus 프로젝트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.crew.smart_sector_manager import AnalysisDepth, SmartSectorManager
from app.llm import LLM


class MockFinancialData:
    """테스트용 재무 데이터"""

    def __init__(self, stock_name: str):
        self.stock_name = stock_name
        self.stock_code = "005930"
        self.sector = "반도체"

        # 기본 재무 지표
        self.revenue = 279600000000000  # 279.6조원
        self.net_income = 26000000000000  # 26조원
        self.total_assets = 427000000000000  # 427조원
        self.total_equity = 280000000000000  # 280조원
        self.operating_cash_flow = 45000000000000  # 45조원
        self.capex = 53000000000000  # 53조원
        self.market_cap = 400000000000000  # 400조원

        # FCF 계산
        self.free_cash_flow = self.operating_cash_flow - self.capex

        # 비율 계산
        self.roe = (self.net_income / self.total_equity) * 100
        self.roa = (self.net_income / self.total_assets) * 100
        self.debt_ratio = (
            (self.total_assets - self.total_equity) / self.total_assets
        ) * 100


async def test_fundamental_web_search():
    """개선된 펀더멘털 분석 테스트"""

    print("🔍 개선된 펀더멘털 분석 테스트 시작")
    print("=" * 60)
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        # LLM 및 매니저 초기화
        llm = LLM()
        manager = SmartSectorManager(llm)

        # 테스트용 재무 데이터
        stock_name = "삼성전자"
        financial_data = MockFinancialData(stock_name)

        print(f"📊 테스트 대상: {stock_name}")
        print(f"📈 기본 정보:")
        print(f"   - 매출: {financial_data.revenue:,}원")
        print(f"   - 순이익: {financial_data.net_income:,}원")
        print(f"   - ROE: {financial_data.roe:.2f}%")
        print(f"   - FCF: {financial_data.free_cash_flow:,}원")
        print()

        # 웹검색 강제 실행 분석
        print("🚀 웹검색 강제 실행 분석 시작...")
        print("-" * 40)

        user_prompt = f"""
{stock_name}에 대한 펀더멘털 분석을 요청합니다.

특히 다음 사항들을 중점적으로 분석해주세요:
1. 경쟁사 대비 수익성 비교
2. 최근 3년간 성장성 트렌드
3. 현재 밸류에이션 수준
4. 투자 매력도 평가

Chat GPT 피드백을 반영하여 구체적이고 실용적인 분석을 제공해주세요.
"""

        # 분석 실행
        result = await manager.analyze_with_comprehensive_data(
            user_prompt=user_prompt,
            stock_name=stock_name,
            stock_code="005930",
            financial_data=financial_data.__dict__,
            analysis_depth=AnalysisDepth.STANDARD,
        )

        # 결과 분석
        print("📊 분석 결과:")
        print("=" * 60)

        if result.get("success"):
            expert_insights = result.get("expert_insights", {})
            individual_analyses = expert_insights.get("individual_expert_analyses", [])

            print(f"✅ 분석 성공!")
            print(f"🎯 활성화된 전문가: {len(individual_analyses)}명")
            print(f"📈 감지된 섹터: {result.get('detected_sector', '알 수 없음')}")
            print()

            # 펀더멘털 전문가 결과 확인
            fundamental_expert = None
            for analysis in individual_analyses:
                if "펀더멘털" in analysis.get(
                    "expert_name", ""
                ) or "펀더멘탈" in analysis.get("expert_name", ""):
                    fundamental_expert = analysis
                    break

            if fundamental_expert:
                print("🔍 펀더멘털 전문가 분석 결과:")
                print("-" * 40)
                print(f"전문가: {fundamental_expert.get('expert_name', '알 수 없음')}")
                print(f"역할: {fundamental_expert.get('expert_role', '알 수 없음')}")

                # 웹검색 실행 여부 확인
                web_search_performed = fundamental_expert.get(
                    "web_search_performed", False
                )
                web_search_count = fundamental_expert.get("web_search_count", 0)

                print(
                    f"🌐 웹검색 실행: {'✅ YES' if web_search_performed else '❌ NO'}"
                )
                print(f"🔢 웹검색 횟수: {web_search_count}회")
                print()

                # 분석 내용 미리보기
                analysis_result = fundamental_expert.get("analysis_result", "")
                if analysis_result:
                    print("📖 분석 내용 미리보기:")
                    print("-" * 30)
                    preview = (
                        analysis_result[:500] + "..."
                        if len(analysis_result) > 500
                        else analysis_result
                    )
                    print(preview)
                    print()
                    print(f"📏 전체 분석 길이: {len(analysis_result):,}자")

                    # Chat GPT 피드백 항목 체크
                    print("\n🎯 Chat GPT 피드백 항목 체크:")
                    print("-" * 30)

                    feedback_items = {
                        "경쟁사 비교": ["경쟁사", "비교", "TSMC", "SK하이닉스"],
                        "시계열 분석": ["3년", "추이", "변화", "트렌드"],
                        "밸류에이션": ["PER", "PBR", "업계 평균", "목표주가"],
                        "구체적 수치": ["ROE", "%", "조원", "배"],
                        "투자 판단": ["사야", "기다려", "피해야", "추천"],
                    }

                    for item, keywords in feedback_items.items():
                        found = any(keyword in analysis_result for keyword in keywords)
                        status = "✅" if found else "❌"
                        print(f"   {status} {item}: {'포함됨' if found else '누락됨'}")

            else:
                print("❌ 펀더멘털 전문가 결과를 찾을 수 없습니다.")

        else:
            print("❌ 분석 실패")
            error = result.get("error", "알 수 없는 오류")
            print(f"오류: {error}")

        print(f"\n⏰ 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return result

    except Exception as e:
        print(f"❌ 테스트 실행 오류: {e}")
        import traceback

        traceback.print_exc()
        return None


async def main():
    """메인 실행 함수"""
    print("🎯 웹검색 강제 실행 시스템 테스트")
    print("Chat GPT 피드백을 반영한 개선된 펀더멘털 분석")
    print("=" * 60)

    result = await test_fundamental_web_search()

    if result:
        print("\n🎉 테스트 완료!")
        print("💡 웹검색 강제 실행 시스템이 정상적으로 작동하는지 확인하세요.")
    else:
        print("\n❌ 테스트 실패!")
        print("🔧 웹검색 시스템을 다시 확인해주세요.")


if __name__ == "__main__":
    asyncio.run(main())
