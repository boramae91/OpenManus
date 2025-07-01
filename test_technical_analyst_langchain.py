#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기술적 분석가 LangChain 테스트 코드
기술적 분석가의 5단계 LangChain 분석을 테스트해요

실행 방법:
python test_technical_analyst_langchain.py
"""

print("테스트 시작 - 기술적 분석가 LangChain")

import os
import sys
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.crew.gics_sectors import GICSSectorManager
from app.crew.sector_teams import SectorTeamFactory


def test_technical_analyst_langchain():
    """
    기술적 분석가의 LangChain 5단계 분석을 테스트하는 함수에요
    """
    print("🚀 기술적 분석가 LangChain 테스트 시작!")
    print("=" * 60)

    try:
        # 1. 섹터 매니저 초기화
        print("1️⃣ 섹터 매니저 초기화 중...")
        sector_manager = GICSSectorManager()

        # 2. 섹터 팀 팩토리 생성
        print("2️⃣ 섹터 팀 팩토리 생성 중...")
        factory = SectorTeamFactory(sector_manager)

        # 3. IT 섹터 팀 생성 (기술적 분석에 적합한 섹터)
        print("3️⃣ IT 섹터 팀 생성 중...")
        it_sector = sector_manager.get_sector_by_name("Information Technology")
        it_team = factory.create_sector_team(it_sector)

        # 4. 기술적 분석가 찾기
        print("4️⃣ 기술적 분석가 찾는 중...")
        technical_analyst = None
        for expert in it_team.experts:
            if "기술적 분석가" in expert.name:
                technical_analyst = expert
                break

        if not technical_analyst:
            print("❌ 기술적 분석가를 찾을 수 없어요!")
            return

        print(f"✅ 기술적 분석가 발견: {technical_analyst.name}")
        print(f"   - LangChain 활성화: {technical_analyst.langchain_enabled}")
        print(f"   - Chain 존재: {technical_analyst.langchain_chain is not None}")

        # 5. 테스트용 가격 데이터 준비
        print("5️⃣ 테스트용 가격 데이터 준비 중...")
        test_price_data = """
        삼성전자 (005930) 기술적 분석 데이터:

        [가격 데이터]
        - 현재가: 75,000원
        - 5일 이동평균: 74,200원 (상승)
        - 20일 이동평균: 72,800원 (상승)
        - 60일 이동평균: 70,500원 (상승)
        - 120일 이동평균: 68,200원 (상승)

        [기술적 지표]
        - MACD: 2.5 (양수, 상승)
        - MACD Signal: 1.8 (상승)
        - MACD Histogram: 0.7 (확대)
        - RSI(14): 65 (중립)

        [볼린저 밴드]
        - 상단: 78,500원
        - 중간: 74,200원
        - 하단: 69,900원
        - 밴드폭: 8,600원 (확장)

        [거래량]
        - 일평균 거래량: 15,000,000주
        - OBV: 상승 추세
        - 거래량 가중 평균가: 74,800원

        [지지/저항 레벨]
        - 주요 지지: 72,000원, 70,000원
        - 주요 저항: 76,000원, 78,000원
        - Fibonacci 61.8%: 73,500원

        [섹터 상대강도]
        - KOSPI 대비: +5.2% (아웃퍼폼)
        - IT 섹터 대비: +2.1% (상위권)
        - 베타: 1.15 (시장 대비 높은 변동성)
        """

        # 6. LangChain 5단계 분석 실행
        print("6️⃣ LangChain 5단계 분석 실행 중...")
        print("-" * 40)

        input_data = {
            "price_data": test_price_data,
            "sector_name": "IT",
            "company_name": "삼성전자",
        }

        # 5단계 전체 분석 실행
        print("[DEBUG] technical_analyst.run_full_technical_analysis 호출")
        result = technical_analyst.run_full_technical_analysis(input_data)
        print("[DEBUG] 분석 결과 반환됨")

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
        print("🔍 1단계: 차트 패턴 분석")
        print("-" * 30)
        print(result.get("step1_result", "결과 없음"))
        print()

        print("📈 2단계: 지지/저항선 분석")
        print("-" * 30)
        print(result.get("step2_result", "결과 없음"))
        print()

        print("📊 3단계: 거래량 분석")
        print("-" * 30)
        print(result.get("step3_result", "결과 없음"))
        print()

        print("🏭 4단계: 섹터 상대강도 분석")
        print("-" * 30)
        print(result.get("step4_result", "결과 없음"))
        print()

        print("🎯 5단계: 기술적 전망 및 매매 신호")
        print("-" * 30)
        print(result.get("step5_result", "결과 없음"))
        print()

        # 8. 성능 지표 확인
        print("8️⃣ 성능 지표 확인:")
        print("-" * 30)
        summary = technical_analyst.get_analysis_summary()
        print(f"총 분석 횟수: {summary['total_analyses']}")
        print(f"성능 지표: {summary['performance_metrics']}")
        print(f"LangChain 활성화: {summary['langchain_enabled']}")

        print("\n✅ 기술적 분석가 LangChain 테스트 완료!")

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback

        traceback.print_exc()


def test_technical_analyst_individual_steps():
    """
    기술적 분석가의 개별 단계별 분석을 테스트하는 함수에요
    """
    print("\n🔬 개별 단계별 분석 테스트")
    print("=" * 60)

    try:
        # 섹터 팀 생성
        sector_manager = GICSSectorManager()
        factory = SectorTeamFactory(sector_manager)
        it_sector = sector_manager.get_sector_by_name("Information Technology")
        it_team = factory.create_sector_team(it_sector)

        # 기술적 분석가 찾기
        technical_analyst = None
        for expert in it_team.experts:
            if "기술적 분석가" in expert.name:
                technical_analyst = expert
                break

        if not technical_analyst or not technical_analyst.langchain_chain:
            print("❌ 기술적 분석가 또는 Chain을 찾을 수 없어요!")
            return

        # 테스트 데이터
        test_data = {
            "price_data": "삼성전자 현재가 75,000원, 20일 이동평균 72,800원, RSI 65",
            "sector_name": "IT",
            "company_name": "삼성전자",
        }

        # 개별 Chain 실행 테스트
        print("🔍 개별 Chain 실행 테스트...")
        result = technical_analyst.langchain_chain(test_data)

        print("✅ 개별 Chain 실행 성공!")
        print(f"결과 키: {list(result.keys())}")

        for step, content in result.items():
            print(f"\n{step}:")
            print(f"내용 길이: {len(str(content))} 문자")
            print(f"내용 미리보기: {str(content)[:100]}...")

    except Exception as e:
        print(f"❌ 개별 단계 테스트 실패: {e}")


if __name__ == "__main__":
    print("🚀 기술적 분석가 LangChain 테스트 시작!")
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # 메인 테스트 실행
    test_technical_analyst_langchain()

    # 개별 단계 테스트 실행
    test_technical_analyst_individual_steps()

    print("\n" + "=" * 80)
    print(f"테스트 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎉 모든 테스트가 완료되었어요!")
