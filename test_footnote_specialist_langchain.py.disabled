#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주석 전문가 LangChain 테스트 코드
주석 전문가의 5단계 LangChain 분석을 테스트해요

실행 방법:
python test_footnote_specialist_langchain.py
"""

import os
import sys
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.crew.gics_sectors import GICSSectorManager
from app.crew.sector_teams import SectorTeamFactory


def test_footnote_specialist_langchain():
    """
    주석 전문가의 LangChain 5단계 분석을 테스트하는 함수에요
    """
    print("🚀 주석 전문가 LangChain 테스트 시작!")
    print("=" * 60)

    try:
        # 1. 섹터 매니저 초기화
        print("1️⃣ 섹터 매니저 초기화 중...")
        sector_manager = GICSSectorManager()

        # 2. 섹터 팀 팩토리 생성
        print("2️⃣ 섹터 팀 팩토리 생성 중...")
        factory = SectorTeamFactory(sector_manager)

        # 3. IT 섹터 팀 생성 (주석 분석에 적합한 섹터)
        print("3️⃣ IT 섹터 팀 생성 중...")
        it_sector = sector_manager.get_sector_by_name("Information Technology")
        it_team = factory.create_sector_team(it_sector)

        # 4. 주석 전문가 찾기
        print("4️⃣ 주석 전문가 찾는 중...")
        footnote_specialist = None
        for expert in it_team.experts:
            if "주석 전문가" in expert.name:
                footnote_specialist = expert
                break

        if not footnote_specialist:
            print("❌ 주석 전문가를 찾을 수 없어요!")
            return

        print(f"✅ 주석 전문가 발견: {footnote_specialist.name}")
        print(f"   - LangChain 활성화: {footnote_specialist.langchain_enabled}")
        print(f"   - Chain 존재: {footnote_specialist.langchain_chain is not None}")

        # 5. 테스트용 재무제표 주석 데이터 준비
        print("5️⃣ 테스트용 재무제표 주석 데이터 준비 중...")
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

        [현금흐름표 주석]
        - 영업현금흐름: 순이익 대비 120% (운전자본 개선)
        - 투자현금흐름: 설비투자 5,000억원, R&D 투자 3,000억원
        - 재무현금흐름: 배당지급 2,000억원, 부채상환 1,500억원
        - 현금성자산: 제한된 현금 500억원 (보증금)

        [연결범위 주석]
        - 연결대상: 지분 50% 초과 보유 회사
        - 연결범위 변동: 신규 자회사 2개사 추가
        - 지배력 판단: 의결권 50% 초과 기준

        [회계정책 주석]
        - 회계정책 변경: 없음
        - 추정변경: 없음
        - 오류수정: 없음
        """

        # 6. LangChain 5단계 분석 실행
        print("6️⃣ LangChain 5단계 분석 실행 중...")
        print("-" * 40)

        input_data = {
            "financial_data": test_financial_data,
            "sector_name": "IT",
            "company_name": "삼성전자",
        }

        # 5단계 전체 분석 실행
        result = footnote_specialist.run_full_footnote_analysis(input_data)

        if "error" in result:
            print(f"❌ 분석 실패: {result['error']}")
            return

        # 7. 결과 출력
        print("7️⃣ 분석 결과 출력:")
        print("=" * 60)

        print(f"📊 분석 소요시간: {result.get('analysis_time', 0):.2f}초")
        print(f"👨‍💼 분석가: {result.get('agent_name', 'Unknown')}")
        print(f"🎯 역할: {result.get('role', 'Unknown')}")
        print()

        # 단계별 결과 출력
        print("🔍 1단계: 재무상태표 주석 분석")
        print("-" * 30)
        print(result.get("step1_result", "결과 없음"))
        print()

        print("📈 2단계: 손익계산서 주석 분석")
        print("-" * 30)
        print(result.get("step2_result", "결과 없음"))
        print()

        print("📊 3단계: 현금흐름표 주석 분석")
        print("-" * 30)
        print(result.get("step3_result", "결과 없음"))
        print()

        print("🏭 4단계: 우발부채 및 보증부채 분석")
        print("-" * 30)
        print(result.get("step4_result", "결과 없음"))
        print()

        print("🎯 5단계: 회계정책 및 위험요소 종합 분석")
        print("-" * 30)
        print(result.get("step5_result", "결과 없음"))
        print()

        # 8. 성능 지표 확인
        print("8️⃣ 성능 지표 확인:")
        print("-" * 30)
        summary = footnote_specialist.get_analysis_summary()
        print(f"총 분석 횟수: {summary['total_analyses']}")
        print(f"성능 지표: {summary['performance_metrics']}")
        print(f"LangChain 활성화: {summary['langchain_enabled']}")

        print("\n✅ 주석 전문가 LangChain 테스트 완료!")

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback

        traceback.print_exc()


def test_footnote_specialist_individual_steps():
    """
    주석 전문가의 개별 단계별 분석을 테스트하는 함수에요
    """
    print("\n🔬 개별 단계별 분석 테스트")
    print("=" * 60)

    try:
        # 섹터 팀 생성
        sector_manager = GICSSectorManager()
        factory = SectorTeamFactory(sector_manager)
        it_sector = sector_manager.get_sector_by_name("Information Technology")
        it_team = factory.create_sector_team(it_sector)

        # 주석 전문가 찾기
        footnote_specialist = None
        for expert in it_team.experts:
            if "주석 전문가" in expert.name:
                footnote_specialist = expert
                break

        if not footnote_specialist or not footnote_specialist.langchain_chain:
            print("❌ 주석 전문가 또는 Chain을 찾을 수 없어요!")
            return

        # 테스트 데이터
        test_data = {
            "financial_data": "삼성전자 재무상태표 주석: 유형자산 정액법 감가상각, 우발부채 500억원",
            "sector_name": "IT",
            "company_name": "삼성전자",
        }

        # 개별 Chain 실행 테스트
        print("🔍 개별 Chain 실행 테스트...")
        result = footnote_specialist.langchain_chain(test_data)

        print("✅ 개별 Chain 실행 성공!")
        print(f"결과 키: {list(result.keys())}")

        for step, content in result.items():
            print(f"\n{step}:")
            print(f"내용 길이: {len(str(content))} 문자")
            print(f"내용 미리보기: {str(content)[:100]}...")

    except Exception as e:
        print(f"❌ 개별 단계 테스트 실패: {e}")


if __name__ == "__main__":
    print("🚀 주석 전문가 LangChain 테스트 시작!")
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # 메인 테스트 실행
    test_footnote_specialist_langchain()

    # 개별 단계 테스트 실행
    test_footnote_specialist_individual_steps()

    print("\n" + "=" * 80)
    print(f"테스트 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎉 모든 테스트가 완료되었어요!")
