#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
산업 전문가 LangChain 5단계 분석 테스트 코드
Day 2 4단계: 산업 전문가 LangChain 적용 테스트

이 코드는 산업 전문가가 LangChain을 사용해서 5단계 분석을 수행하는지 테스트해요.
각 단계별로 산업 분석을 수행하고 결과를 확인해요.
"""

import os
import sys
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.crew.gics_sectors import GICSSector, GICSSectorManager
from app.crew.sector_teams import SectorTeamFactory


def test_industry_expert_langchain():
    """
    산업 전문가의 LangChain 5단계 분석을 테스트해요
    """
    print("🚀 산업 전문가 LangChain 5단계 분석 테스트 시작!")
    print("=" * 60)

    try:
        # 1. GICS 섹터 매니저 초기화
        print("📋 1단계: GICS 섹터 매니저 초기화...")
        sector_manager = GICSSectorManager()

        # 2. 섹터팀 팩토리 생성
        print("🏭 2단계: 섹터팀 팩토리 생성...")
        factory = SectorTeamFactory(sector_manager)

        # 3. IT 섹터팀 생성 (산업 전문가 포함)
        print("💻 3단계: IT 섹터팀 생성 (산업 전문가 포함)...")
        it_team = factory.create_sector_team(GICSSector.INFORMATION_TECHNOLOGY)

        # 4. 산업 전문가 찾기
        print("🔍 4단계: 산업 전문가 찾기...")
        industry_expert = None
        for expert in it_team.experts:
            if "산업" in expert.name:
                industry_expert = expert
                break

        if not industry_expert:
            print("❌ 산업 전문가를 찾을 수 없어요!")
            return

        print(f"✅ 산업 전문가 발견: {industry_expert.name}")
        print(f"   - LangChain 활성화: {industry_expert.langchain_enabled}")
        print(f"   - Chain 존재: {industry_expert.langchain_chain is not None}")

        # 5. 테스트용 기업 데이터 준비
        print("📊 5단계: 테스트용 기업 데이터 준비...")
        test_company_data = """
        삼성전자 (005930) 기업 데이터:

        [기업 개요]
        - 설립: 1969년
        - 업종: 반도체, 디스플레이, 모바일, 가전
        - 매출: 258조원 (2023년)
        - 영업이익: 6.5조원 (2023년)
        - 시가총액: 450조원

        [사업 구조]
        - 반도체 사업: 메모리, 시스템LSI, 파운드리
        - 디스플레이 사업: OLED, LCD, 마이크로LED
        - 모바일 사업: 갤럭시 스마트폰, 태블릿
        - 가전 사업: TV, 냉장고, 세탁기

        [시장 점유율]
        - 메모리 반도체: 글로벌 1위 (약 40%)
        - OLED 디스플레이: 글로벌 1위 (약 70%)
        - 스마트폰: 글로벌 1위 (약 20%)
        - TV: 글로벌 1위 (약 30%)

        [R&D 투자]
        - R&D 비용: 22조원 (2023년)
        - R&D 비율: 매출 대비 8.5%
        - 특허 보유: 20만건 이상

        [글로벌 진출]
        - 해외 매출 비중: 80% 이상
        - 주요 시장: 미국, 중국, 유럽
        - 생산 기지: 한국, 중국, 베트남, 인도

        [경쟁사]
        - 반도체: SK하이닉스, 마이크론, 인텔, TSMC
        - 디스플레이: LG디스플레이, BOE, CSOT
        - 모바일: 애플, 샤오미, OPPO, vivo
        - 가전: LG전자, 하이얼, TCL
        """

        # 6. 산업 전문가 5단계 전체 분석 실행
        print("🎯 6단계: 산업 전문가 5단계 전체 분석 실행...")
        input_data = {
            "company_data": test_company_data,
            "sector_name": "정보기술(IT)",
            "company_name": "삼성전자",
        }

        # 5단계 전체 분석 실행
        result = industry_expert.run_full_valuation_analysis(input_data)

        # 7. 결과 출력
        print("\n📈 산업 전문가 5단계 분석 결과:")
        print("=" * 60)

        if "error" in result:
            print(f"❌ 분석 실패: {result['error']}")
            return

        # 각 단계별 결과 출력
        steps = [
            ("1단계: 산업 구조 분석 (Porter 5 Forces)", "step1_result"),
            ("2단계: 시장 동향 및 성장성 분석", "step2_result"),
            ("3단계: 경쟁사 분석", "step3_result"),
            ("4단계: 규제 환경 및 정책 분석", "step4_result"),
            ("5단계: 산업 리스크 및 기회요소 분석", "step5_result"),
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
        print(f"\n📊 산업 전문가 성능 지표:")
        print(f"   - 총 분석 횟수: {len(industry_expert.analysis_history)}")
        print(f"   - LangChain 활성화: {industry_expert.langchain_enabled}")
        print(f"   - 최근 분석 시간: {analysis_time:.2f}초")

        print("\n✅ 산업 전문가 LangChain 5단계 분석 테스트 완료!")

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback

        traceback.print_exc()


def test_industry_expert_individual_steps():
    """
    산업 전문가의 개별 단계별 분석을 테스트해요
    """
    print("\n🔬 산업 전문가 개별 단계별 분석 테스트...")
    print("=" * 60)

    try:
        # 섹터팀 생성
        sector_manager = GICSSectorManager()
        factory = SectorTeamFactory(sector_manager)
        it_team = factory.create_sector_team(GICSSector.INFORMATION_TECHNOLOGY)

        # 산업 전문가 찾기
        industry_expert = None
        for expert in it_team.experts:
            if "산업" in expert.name:
                industry_expert = expert
                break

        if not industry_expert or not industry_expert.langchain_chain:
            print("❌ 산업 전문가 또는 Chain을 찾을 수 없어요!")
            return

        # 테스트 데이터
        test_data = {
            "company_data": "삼성전자 기업 데이터: 반도체, 디스플레이, 모바일, 가전 사업, 글로벌 1위 기업",
            "sector_name": "정보기술(IT)",
            "company_name": "삼성전자",
        }

        # 개별 단계별 테스트
        print("🎯 개별 단계별 분석 테스트...")
        result = industry_expert.langchain_chain(test_data)

        for i, (step_name, step_key) in enumerate(
            [
                ("산업 구조 분석", "step1_result"),
                ("시장 동향 분석", "step2_result"),
                ("경쟁사 분석", "step3_result"),
                ("규제 환경 분석", "step4_result"),
                ("리스크 및 기회 분석", "step5_result"),
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
    print("🎯 산업 전문가 LangChain 테스트 시작!")
    print("=" * 60)

    # 전체 5단계 분석 테스트
    test_industry_expert_langchain()

    # 개별 단계별 분석 테스트
    test_industry_expert_individual_steps()

    print("\n🎉 모든 산업 전문가 테스트 완료!")
