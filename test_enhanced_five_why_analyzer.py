# -*- coding: utf-8 -*-
"""
향상된 5Why 분석 시스템 테스트

실제 데이터 소스를 활용한 5Why 분석이 제대로 작동하는지 테스트해요!
"""

import os
import sys
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.crew.enhanced_five_why_analyzer import EnhancedFiveWhyAnalyzer


def test_enhanced_five_why_analyzer():
    """향상된 5Why 분석 시스템 테스트"""

    print("🧪 향상된 5Why 분석 시스템 테스트 시작!")
    print("=" * 60)

    try:
        # 향상된 5Why 분석 시스템 초기화
        analyzer = EnhancedFiveWhyAnalyzer()

        # 테스트용 데이터 준비
        company_name = "삼성전자"
        sector_name = "반도체"

        # 재무 데이터 (실제 DART 데이터 형태)
        financial_data = """
        **삼성전자 재무 데이터 (2023년 기준)**

        **수익성 지표:**
        - 매출액: 258.9조원 (전년 대비 -14.3%)
        - 영업이익: 6.6조원 (전년 대비 -84.9%)
        - 순이익: 15.5조원 (전년 대비 -72.2%)
        - 영업이익률: 2.5% (전년 13.8%)
        - 순이익률: 6.0% (전년 15.8%)

        **성장성 지표:**
        - 매출액 성장률: -14.3%
        - 영업이익 성장률: -84.9%
        - 자산 성장률: -2.1%
        - 자본 성장률: 3.2%

        **안정성 지표:**
        - 유동비율: 2.1배
        - 부채비율: 25.3%
        - 이자보상배율: 45.2배
        - 현금흐름: 35.2조원

        **효율성 지표:**
        - 자산회전율: 0.8배
        - 재고회전율: 4.2배
        - ROE: 8.2%
        - ROA: 6.1%
        """

        # 시장 데이터 (실제 yfinance 데이터 형태)
        market_data = """
        **삼성전자 시장 데이터 (현재 기준)**

        **주가 및 가치 평가:**
        - 현재 주가: 78,000원
        - 시가총액: 463조원
        - PER: 15.2배 (업계 평균 18.5배)
        - PBR: 1.2배 (업계 평균 2.1배)
        - EV/EBITDA: 8.5배

        **거래량 및 유동성:**
        - 일평균 거래량: 1,200만주
        - 거래대금: 9.4조원
        - 외국인 지분율: 52.3%
        - 기관 투자자 비중: 28.7%

        **시장 성과:**
        - KOSPI 대비 성과: -5.2%
        - 업계 평균 대비 성과: -12.1%
        - 베타: 1.15
        - 변동성: 28.5%

        **투자자 심리:**
        - 분석가 목표가: 95,000원
        - 투자 의견: 매수 (15명), 보유 (8명), 매도 (2명)
        - 시장 기대치: 보수적
        """

        # 경쟁사 데이터
        competitor_data = """
        **반도체 업계 경쟁사 비교 데이터**

        **주요 경쟁사 재무 비교 (2023년):**

        **삼성전자:**
        - 매출액: 258.9조원
        - 영업이익: 6.6조원
        - 영업이익률: 2.5%
        - 시장 점유율: 12.5%

        **TSMC (대만반도체):**
        - 매출액: 2.2조원 (약 300조원)
        - 영업이익: 1.1조원 (약 150조원)
        - 영업이익률: 50.0%
        - 시장 점유율: 59.0%

        **Intel:**
        - 매출액: 542억달러 (약 720조원)
        - 영업이익: 23억달러 (약 30조원)
        - 영업이익률: 4.2%
        - 시장 점유율: 7.2%

        **SK하이닉스:**
        - 매출액: 32.8조원
        - 영업이익: -7.7조원
        - 영업이익률: -23.5%
        - 시장 점유율: 6.1%

        **업계 평균:**
        - 영업이익률: 15.2%
        - 성장률: 8.5%
        - R&D 투자 비율: 12.3%
        """

        # 웹 검색 데이터 (실제 뉴스, 분석가 리포트 형태)
        web_search_data = """
        **삼성전자 관련 최신 뉴스 및 분석 (2024년)**

        **주요 뉴스:**
        1. "삼성전자, AI 반도체 시장 진출 가속화" (2024.01.15)
        2. "메모리 반도체 가격 회복세, 삼성전자 실적 개선 기대" (2024.02.20)
        3. "중국 시장 의존도 높아, 지리적 리스크 증가" (2024.03.10)

        **분석가 리포트:**
        - "AI 반도체 수요 증가로 메모리 시장 회복 전망" (KB증권)
        - "중국 경제 둔화로 스마트폰 수요 감소 우려" (NH투자증권)
        - "HBM 기술 경쟁력 강화로 고부가가치 제품 비중 확대" (미래에셋증권)

        **산업 동향:**
        - AI 반도체 시장 연평균 성장률 25% 전망
        - 메모리 반도체 공급과잉 해소 기대
        - 중국 반도체 자립화 정책으로 시장 불확실성 증가

        **정책 환경:**
        - 미국 반도체 지원법으로 투자 확대
        - EU 반도체법으로 글로벌 경쟁 심화
        - 한국 반도체 산업 육성 정책 강화
        """

        print(f"📊 테스트 데이터 준비 완료:")
        print(f"   - 기업: {company_name}")
        print(f"   - 섹터: {sector_name}")
        print(f"   - 재무 데이터: {len(financial_data)}자")
        print(f"   - 시장 데이터: {len(market_data)}자")
        print(f"   - 경쟁사 데이터: {len(competitor_data)}자")
        print(f"   - 웹 검색 데이터: {len(web_search_data)}자")
        print("-" * 40)

        # 향상된 5Why 분석 실행
        print("🚀 향상된 5Why 분석 프로세스 실행 중...")

        result = analyzer.perform_enhanced_five_why_analysis(
            company_name=company_name,
            sector_name=sector_name,
            financial_data=financial_data,
            market_data=market_data,
            competitor_data=competitor_data,
            web_search_data=web_search_data,
        )

        # 결과 확인
        if "error" in result:
            print(f"❌ 분석 실패: {result['error']}")
            return False

        print("\n" + "=" * 60)
        print("📋 향상된 5Why 분석 결과 요약")
        print("=" * 60)

        # 분석 결과 요약 출력
        print(f"✅ 분석 완료 시간: {result.get('timestamp', 'N/A')}")
        print(f"✅ 분석 방법: {result.get('analysis_method', 'N/A')}")
        print(f"✅ 사용된 데이터 소스:")

        data_sources = result.get("data_sources_used", {})
        for source, description in data_sources.items():
            print(f"   - {source}: {description}")

        print("\n" + "-" * 40)
        print("🔍 종합 5Why 분석 결과 (일부):")
        print("-" * 40)

        synthesis = result.get("synthesis_analysis", "")
        if synthesis:
            # 결과가 너무 길면 앞부분만 출력
            preview = synthesis[:1000] + "..." if len(synthesis) > 1000 else synthesis
            print(preview)

        # 결과 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"enhanced_five_why_test_result_{timestamp}.json"

        analyzer.save_enhanced_five_why_result(filename, result)

        # 분석 요약 정보 출력
        summary = analyzer.get_analysis_summary()
        print(f"\n📊 분석 요약:")
        print(f"   - 분석 히스토리 크기: {summary.get('analysis_history_size', 0)}")

        print("\n🎉 향상된 5Why 분석 시스템 테스트 완료!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 환경 변수 설정 확인
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("   config_example.env 파일을 참고하여 환경 변수를 설정해주세요.")
        sys.exit(1)

    # 테스트 실행
    success = test_enhanced_five_why_analyzer()

    if success:
        print("✅ 모든 테스트가 성공적으로 완료되었습니다!")
    else:
        print("❌ 테스트 중 오류가 발생했습니다.")
        sys.exit(1)
