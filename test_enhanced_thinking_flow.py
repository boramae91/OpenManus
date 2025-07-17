#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enhanced Thinking Flow 테스트 스크립트

이 스크립트는 개선된 애널리스트 사고 흐름 (Self-Ask with ToT → ReAct → CoT + Self-Critique)을
테스트하기 위한 것으로, 통합 재무분석전문가의 새로운 프롬프트 기법을 검증합니다.

사고 흐름:
1. Self-Ask with ToT - 질문 구성 단계에 ToT 적용
2. ReAct (Reason + Action) - 검색 및 정보 수집 수행
3. CoT Reasoning + Self-Critique - 최종 분석
"""

import asyncio
import os
import sys
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.crew.gics_sectors import GICSSector, GICSSectorManager
from app.crew.sector_teams import SectorTeamFactory
from app.data_collector.financial_data_collector import FinancialDataCollector


async def test_enhanced_thinking_flow():
    """
    동적 섹터별 맞춤형 향상된 애널리스트 사고 흐름을 테스트하는 함수

    삼성전자(IT 섹터)를 대상으로 새로운 동적 질문 생성 기능과
    섹터별 맞춤형 사고 흐름이 올바르게 작동하는지 확인합니다.
    """
    print("🧠 Dynamic Enhanced Analyst Thinking Flow 테스트 시작...")
    print("🚀 섹터별 맞춤형 질문 생성 기능 + 데이터 우선순위 기반 분석")
    print("=" * 80)

    try:
        # 1. 기본 설정
        print("\n📋 1단계: 시스템 초기화...")

        # 재무데이터 수집기 초기화
        financial_collector = FinancialDataCollector()

        # GICS 섹터 매니저 초기화
        sector_manager = GICSSectorManager()

        # 섹터 기반 분석팀 팩토리 초기화
        try:
            team_factory = SectorTeamFactory(sector_manager)
        except Exception as e:
            print(f"❌ SectorTeamFactory 초기화 실패: {e}")
            return

        print("✅ 시스템 초기화 완료")

        # 2. 테스트 대상 설정
        print("\n🎯 2단계: 테스트 대상 설정...")

        test_stock = {
            "stock_name": "삼성전자",
            "stock_code": "005930",
            "sector": GICSSector.INFORMATION_TECHNOLOGY,
        }

        test_prompt = """
        삼성전자에 대한 종합적인 투자 분석을 부탁드립니다.

        특히 다음 사항들을 중점적으로 분석해 주세요:
        1. 현재 재무 건전성과 수익성은 어떤 수준인가요?
        2. 반도체 업계에서의 경쟁력과 시장 지위는?
        3. DCF와 멀티플 방식으로 적정 가치는 얼마인가요?
        4. 주요 투자 리스크와 기회 요소는 무엇인가요?

        Enhanced Thinking Flow 방식으로 체계적으로 분석해 주세요.
        """

        print(
            f"✅ 테스트 대상: {test_stock['stock_name']} ({test_stock['stock_code']})"
        )
        print(f"✅ 섹터: {test_stock['sector'].name} ({test_stock['sector'].value})")

        # 3. 재무데이터 수집
        print("\n💰 3단계: 재무데이터 수집...")

        try:
            financial_data = financial_collector.collect_stock_data(
                test_stock["stock_code"], test_stock["stock_name"]
            )
        except Exception as e:
            print(f"⚠️ 재무데이터 수집 중 오류: {e}")
            financial_data = {"success": False, "data": {}}

        if financial_data.get("success"):
            print("✅ 재무데이터 수집 성공")
            print(f"   - 수집된 데이터 항목: {len(financial_data.get('data', {}))}")
        else:
            print("⚠️ 재무데이터 수집 실패, 테스트용 더미 데이터 사용")
            financial_data = {"success": False, "data": {}}

            # 4. 섹터별 전문가 팀 생성
        print("\n👥 4단계: IT 섹터 전문가 팀 생성...")

        try:
            it_sector_team = team_factory.create_sector_team(
                GICSSector.INFORMATION_TECHNOLOGY
            )

            if it_sector_team and it_sector_team.experts:
                it_experts = it_sector_team.experts
                print(f"✅ IT 섹터 전문가 {len(it_experts)}명 생성 완료")
            else:
                print("❌ 섹터 팀이 생성되지 않았거나 전문가가 없습니다")
                return
        except Exception as e:
            print(f"❌ 섹터 팀 생성 실패: {e}")
            import traceback

            traceback.print_exc()
            return

        # 통합 재무분석가 확인
        integrated_analyst = None
        print(f"🔍 생성된 전문가 목록:")
        for i, expert in enumerate(it_experts):
            print(f"   {i+1}. {expert.name}")
            if (
                "통합 재무분석가" in expert.name
                and "Enhanced Thinking Flow" in expert.name
            ):
                integrated_analyst = expert

        if integrated_analyst:
            print(f"\n✅ Enhanced Thinking Flow 전문가 확인: {integrated_analyst.name}")
            print(f"   - 역할: {integrated_analyst.role}")
            print(f"   - 전문성: {integrated_analyst.expertise}")
            print(f"   - 핵심 방법론:")
            for method in integrated_analyst.key_methods:
                print(f"     • {method}")
        else:
            print("❌ Enhanced Thinking Flow 통합 재무분석가를 찾을 수 없습니다")
            print(
                "   생성된 전문가 중에서 Enhanced Thinking Flow가 포함된 전문가가 없습니다"
            )
            return

        # 5. Enhanced Thinking Flow 분석 실행
        print("\n🧠 5단계: Enhanced Thinking Flow 분석 실행...")
        print("-" * 60)

        start_time = datetime.now()

        # 통합 재무분석가로 분석 수행
        if integrated_analyst.langchain_chain:
            print("🚀 LangChain 기반 Enhanced Thinking Flow 분석 시작...")

            # 컨텍스트 구성 (데이터 활용 우선순위 강조)
            context = f"""
**분석 대상**: {test_stock['stock_name']} ({test_stock['stock_code']})
**섹터**: {test_stock['sector'].name} ({test_stock['sector'].value})

**⚠️ 중요: 먼저 아래 수집된 데이터를 우선 분석하고, 부족한 부분만 웹 검색으로 보완하세요**

**🥇 수집된 재무데이터 (yfinance)**:
- 현재가: 65,400원
- 시가총액: 424조원
- 데이터 소스: yfinance
- 수집 상태: 성공적으로 수집됨

**🥈 DART 데이터 상태**:
- DART API 키 없음으로 yfinance 데이터만 가용
- 추후 DART 데이터 보완 필요

**📋 사용자 요청**:
{test_prompt}

**📌 분석 지침**:
1. 반드시 제공된 재무데이터(yfinance)부터 분석 시작
2. 기본적인 재무비율(PER, PBR, ROE 등) 계산 및 해석
3. 부족한 정보만 웹 검색으로 보완
4. "제공된 재무데이터부터 분석하겠습니다"라고 명시하고 시작
"""

            try:
                # Enhanced Thinking Flow 실행 (chat_history 추가)
                analysis_result = await integrated_analyst.langchain_chain.ainvoke(
                    {"input": context, "chat_history": []}  # 빈 채팅 히스토리로 시작
                )

                end_time = datetime.now()
                analysis_duration = (end_time - start_time).total_seconds()

                print("✅ Enhanced Thinking Flow 분석 완료!")
                print(f"   - 소요 시간: {analysis_duration:.1f}초")

                # 6. 결과 분석 및 검증
                print("\n📊 6단계: 분석 결과 검증...")
                print("=" * 80)

                result_output = analysis_result.get("output", "결과 없음")

                # 🆕 동적 사고 흐름 단계별 포함 여부 검증
                thinking_flow_checks = {
                    "1단계 (Dynamic Self-Ask with ToT)": any(
                        [
                            "1단계" in result_output,
                            "Self-Ask" in result_output,
                            "ToT" in result_output,
                            "Tree of Thoughts" in result_output,
                            "질문 구성" in result_output,
                            "섹터별 맞춤" in result_output,
                            "IT 섹터" in result_output,
                        ]
                    ),
                    "2단계 (ReAct with Data Priority)": any(
                        [
                            "2단계" in result_output,
                            "ReAct" in result_output,
                            "Reason" in result_output,
                            "Action" in result_output,
                            "Observation" in result_output,
                            "우선순위" in result_output,
                        ]
                    ),
                    "3단계 (CoT + Self-Critique)": any(
                        [
                            "3단계" in result_output,
                            "Chain of Thought" in result_output,
                            "Self-Critique" in result_output,
                            "자기 검증" in result_output,
                            "비판적 검토" in result_output,
                        ]
                    ),
                }

                # 🚀 섹터별 맞춤형 질문 생성 검증
                sector_specific_checks = {
                    "IT 섹터 특화 질문": any(
                        [
                            "기술 경쟁력" in result_output,
                            "플랫폼 점유율" in result_output,
                            "R&D 투자" in result_output,
                            "클라우드" in result_output,
                            "AI" in result_output,
                            "반도체" in result_output,
                            "Q5" in result_output,  # IT 섹터 특화 질문
                        ]
                    ),
                    "동적 질문 생성": any(
                        [
                            "동적" in result_output,
                            "맞춤형" in result_output,
                            "섹터 특화" in result_output,
                        ]
                    ),
                }

                print("🔍 사고 흐름 단계별 포함 여부:")
                for stage, included in thinking_flow_checks.items():
                    status = "✅" if included else "❌"
                    print(f"   {status} {stage}: {'포함됨' if included else '누락됨'}")

                # 분석 품질 검증
                quality_checks = {
                    "투자 의견 (BUY/HOLD/SELL)": any(
                        [
                            "BUY" in result_output,
                            "HOLD" in result_output,
                            "SELL" in result_output,
                            "매수" in result_output,
                            "보유" in result_output,
                            "매도" in result_output,
                        ]
                    ),
                    "목표가 제시": any(
                        [
                            "목표가" in result_output,
                            "원" in result_output
                            and any(num in result_output for num in "0123456789"),
                            "target price" in result_output.lower(),
                        ]
                    ),
                    "리스크 분석": any(
                        [
                            "리스크" in result_output,
                            "위험" in result_output,
                            "risk" in result_output.lower(),
                        ]
                    ),
                    "경쟁사 비교": any(
                        [
                            "경쟁사" in result_output,
                            "경쟁" in result_output,
                            "업계" in result_output,
                        ]
                    ),
                }

                # 🆕 데이터 활용 우선순위 검증
                data_utilization_checks = {
                    "재무데이터 활용": any(
                        [
                            "yfinance" in result_output,
                            "재무데이터" in result_output,
                            "현재가" in result_output,
                            "시가총액" in result_output,
                        ]
                    ),
                    "DART 데이터 활용": any(
                        [
                            "DART" in result_output,
                            "재무제표" in result_output,
                            "사업보고서" in result_output,
                        ]
                    ),
                    "효율적 정보수집": any(
                        [
                            "1순위" in result_output,
                            "우선순위" in result_output,
                            "재무데이터를" in result_output,
                        ]
                    ),
                    "웹검색 보완적 활용": not any(
                        ["웹 검색부터" in result_output, "바로 검색" in result_output]
                    ),  # 웹검색을 첫 번째로 하지 않았는지 확인
                }

                print("\n🎯 분석 품질 검증:")
                for quality, included in quality_checks.items():
                    status = "✅" if included else "❌"
                    print(
                        f"   {status} {quality}: {'포함됨' if included else '누락됨'}"
                    )

                print("\n🥇 데이터 활용 우선순위 검증:")
                for priority, included in data_utilization_checks.items():
                    status = "✅" if included else "❌"
                    print(
                        f"   {status} {priority}: {'포함됨' if included else '누락됨'}"
                    )

                print("\n🚀 섹터별 맞춤형 질문 생성 검증:")
                for sector_feature, included in sector_specific_checks.items():
                    status = "✅" if included else "❌"
                    print(
                        f"   {status} {sector_feature}: {'포함됨' if included else '누락됨'}"
                    )

                # 7. 최종 결과 출력
                print("\n📋 7단계: 최종 분석 결과")
                print("=" * 80)
                print(result_output)
                print("=" * 80)

                # 전체 성공률 계산 (섹터별 맞춤형 질문 검증 포함)
                total_checks = (
                    len(thinking_flow_checks)
                    + len(quality_checks)
                    + len(data_utilization_checks)
                    + len(sector_specific_checks)
                )
                passed_checks = (
                    sum(thinking_flow_checks.values())
                    + sum(quality_checks.values())
                    + sum(data_utilization_checks.values())
                    + sum(sector_specific_checks.values())
                )
                success_rate = (passed_checks / total_checks) * 100

                print(f"\n🎉 테스트 완료!")
                print(f"   - 전체 검증 항목: {total_checks}개")
                print(f"   - 통과 항목: {passed_checks}개")
                print(f"   - 성공률: {success_rate:.1f}%")
                print(f"   - 분석 소요 시간: {analysis_duration:.1f}초")

                if success_rate >= 80:
                    print(
                        "✅ Dynamic Enhanced Thinking Flow가 성공적으로 구현되었습니다!"
                    )
                    print("🚀 섹터별 맞춤형 질문 생성 기능이 정상 작동합니다!")
                elif success_rate >= 60:
                    print(
                        "⚠️ Dynamic Enhanced Thinking Flow가 부분적으로 구현되었습니다. 추가 개선이 필요합니다."
                    )
                else:
                    print(
                        "❌ Dynamic Enhanced Thinking Flow 구현에 문제가 있습니다. 프롬프트 수정이 필요합니다."
                    )

            except Exception as e:
                print(f"❌ 분석 실행 중 오류 발생: {str(e)}")
                print("   프롬프트나 LangChain 설정을 점검해 주세요.")

        else:
            print("❌ LangChain Chain이 설정되지 않았습니다")

    except Exception as e:
        print(f"❌ 테스트 실행 중 오류 발생: {str(e)}")
        import traceback

        traceback.print_exc()


async def main():
    """메인 함수"""
    print("🧠 Enhanced Analyst Thinking Flow 테스트 스크립트")
    print("=" * 80)
    print("이 스크립트는 다음 사고 흐름을 테스트합니다:")
    print("1️⃣ Self-Ask with ToT: 질문 구성 단계에 ToT 적용")
    print("2️⃣ ReAct: Reason + Action 구조로 검색 및 정보 수집")
    print("3️⃣ CoT + Self-Critique: 최종 분석 및 자기 검증")
    print("=" * 80)

    await test_enhanced_thinking_flow()


if __name__ == "__main__":
    # 비동기 실행
    asyncio.run(main())
