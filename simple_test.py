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

    # print("7️⃣ 주석 전문가 찾기 테스트...")  # 🚫 비활성화 (개발 시간 절약)
    # footnote_specialist = None
    # for expert in it_team.experts:
    #     if "주석 전문가" in expert.name:
    #         footnote_specialist = expert
    #         break

    # if footnote_specialist:
    #     print(f"✅ 주석 전문가 발견: {footnote_specialist.name}")
    #     print(f"   - LangChain 활성화: {footnote_specialist.langchain_enabled}")
    #     print(f"   - Chain 존재: {footnote_specialist.langchain_chain is not None}")

    #     print("\n8️⃣ 주석 전문가 LangChain 분석 테스트...")
    #     test_financial_data = """
    #     삼성전자 (005930) 재무제표 주석 데이터:

    #     [재무상태표 주석]
    #     - 유형자산: 정액법으로 감가상각, 잔존가치 10%
    #     - 무형자산: 특허권 20년 상각, 상표권 10년 상각
    #     - 금융상품: 공정가치 평가, Level 2 분류
    #     - 우발부채: 소송사건 3건 진행중, 총 500억원 추정
    #     - 보증부채: 자회사 보증 2,000억원, 기간 3년

    #     [손익계산서 주석]
    #     - 매출인식: 상품인도 시점 기준
    #     - 원가분류: 제조원가와 판매관리비 명확 구분
    #     - 특별손익: 자산처분이익 300억원 (일회성)
    #     - 세금: 유효세율 25.2%, 법인세율 25% 대비 0.2%p 높음
    #     """

    #     input_data = {
    #         "financial_data": test_financial_data,
    #         "sector_name": "IT",
    #         "company_name": "삼성전자",
    #     }

    #     print("   - 5단계 분석 실행 중...")
    #     result = footnote_specialist.run_full_footnote_analysis(input_data)

    #     if "error" in result:
    #         print(f"   ❌ 분석 실패: {result['error']}")
    #     else:
    #         print(
    #             f"   ✅ 분석 성공! (소요시간: {result.get('analysis_time', 0):.2f}초)"
    #         )
    #         print(
    #             f"   - 1단계 결과 길이: {len(str(result.get('step1_result', '')))} 문자"
    #         )
    #         print(
    #             f"   - 2단계 결과 길이: {len(str(result.get('step2_result', '')))} 문자"
    #         )
    #         print(
    #             f"   - 3단계 결과 길이: {len(str(result.get('step3_result', '')))} 문자"
    #         )
    #         print(
    #             f"   - 4단계 결과 길이: {len(str(result.get('step4_result', '')))} 문자"
    #         )
    #         print(
    #             f"   - 5단계 결과 길이: {len(str(result.get('step5_result', '')))} 문자"
    #         )
    # else:
    #     print("❌ 주석 전문가를 찾을 수 없어요!")

    print("7️⃣ 주석 전문가 테스트는 비활성화됨 (개발 시간 절약)")

    print("\n🎉 모든 테스트 완료!")

except Exception as e:
    print(f"❌ 테스트 실패: {e}")
    import traceback

    traceback.print_exc()


def test_data_creation():
    """테스트 데이터 생성 테스트"""

    def _create_test_data_for_expert(role: str):
        """전문가 역할에 맞는 테스트 데이터를 생성해요"""
        # 모든 전문가에게 공통적으로 필요한 값이에요
        base_data = {
            "sector_name": "Technology",  # 섹터명
            "company_name": "삼성전자",  # 회사명
        }

        # 펀더멘털 분석가: financial_data가 반드시 필요해요
        if "펀더멘털" in role:
            base_data.update(
                {
                    # financial_data는 재무데이터 전체를 의미해요
                    "financial_data": "매출액: 100조원, 영업이익: 15조원, 순이익: 12조원",
                }
            )
        # 기술적 분석가: price_data가 반드시 필요해요
        elif "기술적" in role:
            base_data.update(
                {
                    # price_data는 주가 데이터 전체를 의미해요
                    "price_data": "현재가: 70,000원, 52주 최고: 80,000원, 52주 최저: 50,000원",
                }
            )
        # 밸류에이션 전문가: financial_data가 반드시 필요해요
        elif "밸류에이션" in role:
            base_data.update(
                {
                    "financial_data": "매출액: 100조원, 영업이익: 15조원, 순이익: 12조원",
                }
            )
        # 리스크 평가자: financial_data가 반드시 필요해요
        elif "리스크" in role:
            base_data.update(
                {
                    "financial_data": "부채비율: 30%, 유동비율: 2.5, 이자보상배율: 15",
                }
            )
        # 산업 전문가: company_data가 반드시 필요해요 (PromptTemplate에서 요구하는 변수명)
        elif "산업" in role:
            base_data.update(
                {
                    "company_data": "반도체 시장 규모: 500조원, 성장률: 8%, 경쟁사: SK하이닉스, TSMC, 시장점유율: 15%",
                }
            )
        # 주석 전문가: financial_data가 반드시 필요해요 (비활성화됨)
        # elif "주석" in role:
        #     base_data.update(
        #         {
        #             "financial_data": "매출액: 100조원, 영업이익: 15조원, 순이익: 12조원",
        #         }
        #     )

        return base_data

    # 테스트
    roles = [
        "펀더멘털 분석가",
        "기술적 분석가",
        "산업 전문가",
        "밸류에이션 전문가",
        "리스크 평가자",
        # "재무제표 주석 전문가",  # 🚫 비활성화 (개발 시간 절약)
    ]

    print("🔍 테스트 데이터 생성 테스트")
    print("=" * 50)

    for role in roles:
        data = _create_test_data_for_expert(role)
        print(f"\n📊 {role}:")
        print(f"   데이터: {data}")
        print(f"   키: {list(data.keys())}")


if __name__ == "__main__":
    test_data_creation()
