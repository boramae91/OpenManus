#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 테스트 파일
단계별로 문제를 찾아보기 위한 테스트
"""

import os
import sys
from datetime import datetime

print("🚀 간단한 테스트 시작!")
print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

try:
    print("1️⃣ 기본 import 테스트...")
    from app.crew.gics_sectors import GICSSectorManager

    print("✅ GICSSectorManager import 성공")

    print("2️⃣ 섹터 매니저 생성 테스트...")
    sector_manager = GICSSectorManager()
    print("✅ 섹터 매니저 생성 성공")

    print("3️⃣ IT 섹터 찾기 테스트...")
    from app.crew.gics_sectors import GICSSector

    it_sector = GICSSector.INFORMATION_TECHNOLOGY
    print(f"✅ IT 섹터 찾기 성공: {it_sector.name}")

    print("4️⃣ SectorTeamFactory import 테스트...")
    from app.crew.sector_teams import SectorTeamFactory

    print("✅ SectorTeamFactory import 성공")

    print("5️⃣ 팩토리 생성 테스트...")
    factory = SectorTeamFactory(sector_manager)
    print("✅ 팩토리 생성 성공")

    print("6️⃣ IT 섹터 팀 생성 테스트...")
    it_team = factory.create_sector_team(it_sector)
    print("✅ IT 섹터 팀 생성 성공")

    print("7️⃣ 주석 전문가 찾기 테스트...")
    footnote_specialist = None
    for expert in it_team.experts:
        if "주석 전문가" in expert.name:
            footnote_specialist = expert
            break

    if footnote_specialist:
        print(f"✅ 주석 전문가 발견: {footnote_specialist.name}")
        print(f"   - LangChain 활성화: {footnote_specialist.langchain_enabled}")
        print(f"   - Chain 존재: {footnote_specialist.langchain_chain is not None}")

        print("\n8️⃣ 주석 전문가 LangChain 분석 테스트...")
        test_financial_data = """
        삼성전자 (005930) 재무제표 주석 데이터:

        [재무상태표 주석]
        - 유형자산: 정액법으로 감가상각, 잔존가치 10%
        - 무형자산: 특허권 20년 상각, 상표권 10년 상각
        - 금융상품: 공정가치 평가, Level 2 분류
        - 우발부채: 소송사건 3건 진행중, 총 500억원 추정
        - 보증부채: 자회사 보증 2,000억원, 기간 3년

        [손익계산서 주석]
        - 매출인식: 상품인도 시점 기준
        - 원가분류: 제조원가와 판매관리비 명확 구분
        - 특별손익: 자산처분이익 300억원 (일회성)
        - 세금: 유효세율 25.2%, 법인세율 25% 대비 0.2%p 높음
        """

        input_data = {
            "financial_data": test_financial_data,
            "sector_name": "IT",
            "company_name": "삼성전자",
        }

        print("   - 5단계 분석 실행 중...")
        result = footnote_specialist.run_full_footnote_analysis(input_data)

        if "error" in result:
            print(f"   ❌ 분석 실패: {result['error']}")
        else:
            print(
                f"   ✅ 분석 성공! (소요시간: {result.get('analysis_time', 0):.2f}초)"
            )
            print(
                f"   - 1단계 결과 길이: {len(str(result.get('step1_result', '')))} 문자"
            )
            print(
                f"   - 2단계 결과 길이: {len(str(result.get('step2_result', '')))} 문자"
            )
            print(
                f"   - 3단계 결과 길이: {len(str(result.get('step3_result', '')))} 문자"
            )
            print(
                f"   - 4단계 결과 길이: {len(str(result.get('step4_result', '')))} 문자"
            )
            print(
                f"   - 5단계 결과 길이: {len(str(result.get('step5_result', '')))} 문자"
            )
    else:
        print("❌ 주석 전문가를 찾을 수 없어요!")

    print("\n🎉 모든 테스트 완료!")

except Exception as e:
    print(f"❌ 테스트 실패: {e}")
    import traceback

    traceback.print_exc()
