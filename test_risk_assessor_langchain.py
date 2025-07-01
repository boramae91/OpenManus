#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
리스크 평가자 LangChain 5단계 분석 테스트 코드
Day 2 3단계: 리스크 평가자 LangChain 적용 테스트

이 코드는 리스크 평가자가 LangChain을 사용해서 5단계 분석을 수행하는지 테스트해요.
각 단계별로 리스크 분석을 수행하고 결과를 확인해요.
"""

import os
import sys
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.crew.gics_sectors import GICSSector, GICSSectorManager
from app.crew.sector_teams import SectorTeamFactory


def test_risk_assessor_langchain():
    """
    리스크 평가자의 LangChain 5단계 분석을 테스트해요
    """
    print("🚀 리스크 평가자 LangChain 5단계 분석 테스트 시작!")
    print("=" * 60)

    try:
        # 1. GICS 섹터 매니저 초기화
        print("📋 1단계: GICS 섹터 매니저 초기화...")
        sector_manager = GICSSectorManager()

        # 2. 섹터팀 팩토리 생성
        print("🏭 2단계: 섹터팀 팩토리 생성...")
        factory = SectorTeamFactory(sector_manager)

        # 3. IT 섹터팀 생성 (리스크 평가자 포함)
        print("💻 3단계: IT 섹터팀 생성 (리스크 평가자 포함)...")
        it_team = factory.create_sector_team(GICSSector.INFORMATION_TECHNOLOGY)

        # 4. 리스크 평가자 찾기
        print("🔍 4단계: 리스크 평가자 찾기...")
        risk_assessor = None
        for expert in it_team.experts:
            if "리스크" in expert.name:
                risk_assessor = expert
                break

        if not risk_assessor:
            print("❌ 리스크 평가자를 찾을 수 없어요!")
            return

        print(f"✅ 리스크 평가자 발견: {risk_assessor.name}")
        print(f"   - LangChain 활성화: {risk_assessor.langchain_enabled}")
        print(f"   - Chain 존재: {risk_assessor.langchain_chain is not None}")

        # 5. 테스트용 재무데이터 준비
        print("📊 5단계: 테스트용 재무데이터 준비...")
        test_financial_data = """
        삼성전자 (005930) 재무데이터:

        [재무상태표]
        총자산: 426조원 (2023년)
        총부채: 89조원 (2023년)
        자기자본: 337조원 (2023년)

        [손익계산서]
        매출액: 258조원 (2023년)
        영업이익: 6.5조원 (2023년)
        당기순이익: 15.2조원 (2023년)

        [현금흐름표]
        영업활동현금흐름: 45조원 (2023년)
        투자활동현금흐름: -35조원 (2023년)
        재무활동현금흐름: -8조원 (2023년)

        [주가 정보]
        현재주가: 75,000원
        시가총액: 450조원
        PER: 29.6배
        PBR: 1.3배
        ROE: 4.4%

        [부채 정보]
        유이자부채: 45조원
        이자비용: 1.2조원
        법인세비용: 3.8조원
        세전이익: 19조원

        [베타 정보]
        베타: 1.15 (KOSPI 대비)
        무위험수익률: 3.5%
        시장위험프리미엄: 6.0%

        [배당 정보]
        배당금: 2.8조원
        배당수익률: 2.1%
        배당성향: 18.4%
        """

        # 6. 리스크 평가자 5단계 전체 분석 실행
        print("🎯 6단계: 리스크 평가자 5단계 전체 분석 실행...")
        input_data = {
            "financial_data": test_financial_data,
            "sector_name": "정보기술(IT)",
            "company_name": "삼성전자",
        }

        # 5단계 전체 분석 실행
        result = risk_assessor.run_full_valuation_analysis(input_data)

        # 7. 결과 출력
        print("\n📈 리스크 평가자 5단계 분석 결과:")
        print("=" * 60)

        if "error" in result:
            print(f"❌ 분석 실패: {result['error']}")
            return

        # 각 단계별 결과 출력
        steps = [
            ("1단계: 시계열 멀티플 분석", "step1_result"),
            ("2단계: 경쟁사 멀티플 비교", "step2_result"),
            ("3단계: WACC 계산 및 DCF 모델링", "step3_result"),
            ("4단계: 종합 목표가 산출", "step4_result"),
            ("5단계: 시나리오별 민감도 분석", "step5_result"),
        ]

        for step_name, step_key in steps:
            print(f"\n🔹 {step_name}:")
            print("-" * 40)
            step_result = result.get(step_key, "결과 없음")
            if hasattr(step_result, "content"):
                print(step_result.content)
            else:
                print(
                    str(step_result)[:500] + "..."
                    if len(str(step_result)) > 500
                    else str(step_result)
                )

        # 분석 시간 출력
        analysis_time = result.get("analysis_time", 0)
        print(f"\n⏱️ 전체 분석 소요시간: {analysis_time:.2f}초")

        # 8. 성능 지표 확인
        print(f"\n📊 리스크 평가자 성능 지표:")
        print(f"   - 총 분석 횟수: {len(risk_assessor.analysis_history)}")
        print(f"   - LangChain 활성화: {risk_assessor.langchain_enabled}")
        print(f"   - 최근 분석 시간: {analysis_time:.2f}초")

        print("\n✅ 리스크 평가자 LangChain 5단계 분석 테스트 완료!")

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback

        traceback.print_exc()


def test_risk_assessor_individual_steps():
    """
    리스크 평가자의 개별 단계별 분석을 테스트해요
    """
    print("\n🔬 리스크 평가자 개별 단계별 분석 테스트...")
    print("=" * 60)

    try:
        # 섹터팀 생성
        sector_manager = GICSSectorManager()
        factory = SectorTeamFactory(sector_manager)
        it_team = factory.create_sector_team(GICSSector.INFORMATION_TECHNOLOGY)

        # 리스크 평가자 찾기
        risk_assessor = None
        for expert in it_team.experts:
            if "리스크" in expert.name:
                risk_assessor = expert
                break

        if not risk_assessor or not risk_assessor.langchain_chain:
            print("❌ 리스크 평가자 또는 Chain을 찾을 수 없어요!")
            return

        # 테스트 데이터
        test_data = {
            "financial_data": "삼성전자 재무데이터: 매출 258조원, 영업이익 6.5조원, 당기순이익 15.2조원",
            "sector_name": "정보기술(IT)",
            "company_name": "삼성전자",
        }

        # 개별 단계별 테스트
        print("🎯 개별 단계별 분석 테스트...")
        result = risk_assessor.langchain_chain(test_data)

        for i, (step_name, step_key) in enumerate(
            [
                ("시계열 멀티플 분석", "step1_result"),
                ("경쟁사 멀티플 비교", "step2_result"),
                ("WACC 계산 및 DCF 모델링", "step3_result"),
                ("종합 목표가 산출", "step4_result"),
                ("시나리오별 민감도 분석", "step5_result"),
            ],
            1,
        ):
            print(f"\n📋 {i}. {step_name}:")
            step_result = result.get(step_key, "결과 없음")
            if hasattr(step_result, "content"):
                content = step_result.content
            else:
                content = str(step_result)

            # 결과 요약 출력 (첫 200자)
            print(f"   결과: {content[:200]}...")

        print("\n✅ 개별 단계별 분석 테스트 완료!")

    except Exception as e:
        print(f"❌ 개별 단계별 테스트 실패: {e}")


if __name__ == "__main__":
    print("🎯 리스크 평가자 LangChain 테스트 시작!")
    print("=" * 60)

    # 전체 5단계 분석 테스트
    test_risk_assessor_langchain()

    # 개별 단계별 분석 테스트
    test_risk_assessor_individual_steps()

    print("\n🎉 모든 리스크 평가자 테스트 완료!")
