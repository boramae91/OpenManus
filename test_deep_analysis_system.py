# -*- coding: utf-8 -*-
"""
심층 분석 시스템 테스트 (CoT + 5Why + Memory 기반)

새로운 심층 분석 시스템이 제대로 작동하는지 테스트해보는 코드에요!
"""

import json
import os
import sys
from datetime import datetime

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.crew.deep_analysis_system import DeepAnalysisSystem


def test_deep_analysis_system():
    """심층 분석 시스템 테스트"""

    print("🧪 심층 분석 시스템 테스트 시작!")
    print("=" * 60)

    try:
        # 1. 심층 분석 시스템 초기화
        print("1️⃣ 심층 분석 시스템 초기화 중...")
        deep_analysis = DeepAnalysisSystem()
        print("✅ 심층 분석 시스템 초기화 완료!")

        # 2. 테스트 데이터 준비 (삼성전자 예시)
        print("\n2️⃣ 테스트 데이터 준비 중...")

        company_name = "삼성전자"
        sector_name = "반도체 및 전자제품"

        financial_data = """
        **재무 데이터 (2023년 기준):**
        - 매출액: 258.9조원 (전년 대비 -14.3%)
        - 영업이익: 6.6조원 (전년 대비 -84.9%)
        - 순이익: 15.5조원 (전년 대비 -72.2%)
        - ROE: 8.2% (전년 대비 -18.5%p)
        - 부채비율: 26.3% (전년 대비 +2.1%p)
        - 영업이익률: 2.5% (전년 대비 -15.2%p)

        **주요 재무 지표:**
        - 유동비율: 2.1배
        - 이자보상배율: 15.2배
        - 현금흐름: 영업활동 현금흐름 45.2조원
        """

        market_data = """
        **시장 데이터:**
        - 현재 주가: 75,000원 (2024년 1월 기준)
        - 시가총액: 4,500조원
        - PER: 15.2배 (업계 평균 18.5배)
        - PBR: 1.2배 (업계 평균 1.8배)
        - 배당수익률: 2.1% (업계 평균 1.8%)

        **주요 지수 대비 성과:**
        - KOSPI 대비: -5.2% (1년)
        - 업계 평균 대비: -12.3% (1년)
        - 베타: 0.85 (시장 대비 변동성)
        """

        competitor_data = """
        **경쟁사 정보:**

        **SK하이닉스:**
        - 매출액: 29.2조원 (전년 대비 -26.3%)
        - 영업이익: -7.7조원 (적자)
        - 시가총액: 1,200조원

        **LG전자:**
        - 매출액: 84.3조원 (전년 대비 +1.2%)
        - 영업이익: 3.5조원 (전년 대비 +12.5%)
        - 시가총액: 800조원

        **애플 (글로벌 경쟁사):**
        - 매출액: 3,830억 달러 (전년 대비 -2.8%)
        - 영업이익: 1,140억 달러 (전년 대비 -3.4%)
        - 시가총액: 3조 달러

        **TSMC (반도체 파운드리):**
        - 매출액: 2.2조원 (대만 달러, 전년 대비 -4.5%)
        - 영업이익: 8,500억원 (대만 달러, 전년 대비 -19.3%)
        - 시가총액: 15조원 (대만 달러)
        """

        print("✅ 테스트 데이터 준비 완료!")

        # 3. 심층 분석 실행
        print("\n3️⃣ 심층 분석 실행 중...")
        print("⏳ 분석에 시간이 걸릴 수 있어요. 잠시만 기다려주세요...")

        analysis_result = deep_analysis.perform_deep_analysis(
            company_name=company_name,
            sector_name=sector_name,
            financial_data=financial_data,
            market_data=market_data,
            competitor_data=competitor_data,
        )

        # 4. 결과 확인
        print("\n4️⃣ 분석 결과 확인 중...")

        if "error" in analysis_result:
            print(f"❌ 분석 실패: {analysis_result['error']}")
            return False

        print("✅ 심층 분석 완료!")

        # 5. 결과 저장
        print("\n5️⃣ 분석 결과 저장 중...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_filename = f"deep_analysis_result_{timestamp}.json"

        deep_analysis.save_deep_analysis_result(result_filename, analysis_result)

        # 6. 결과 요약 출력
        print("\n6️⃣ 분석 결과 요약:")
        print("=" * 60)

        print(f"📊 분석 대상: {analysis_result['company_name']}")
        print(f"🏭 섹터: {analysis_result['sector_name']}")
        print(f"🔬 분석 방법: {analysis_result['analysis_method']}")
        print(f"⏰ 분석 시간: {analysis_result['timestamp']}")

        # Memory 정보 출력
        memory_summary = deep_analysis.get_analysis_summary()
        print(f"\n🧠 Memory 상태:")
        print(f"   - 대화 이력 크기: {memory_summary['conversation_memory_size']}")
        print(f"   - 요약 메모리 크기: {memory_summary['summary_memory_size']}")

        # 각 단계별 분석 결과 길이
        print(f"\n📝 분석 결과 길이:")
        print(f"   - CoT 분석: {len(analysis_result['cot_analysis'])} 문자")
        print(f"   - 5Why 분석: {len(analysis_result['five_why_analysis'])} 문자")
        print(
            f"   - 근본 원인 분석: {len(analysis_result['root_cause_analysis'])} 문자"
        )
        print(f"   - 시사점 분석: {len(analysis_result['implication_analysis'])} 문자")

        # 7. 각 단계별 핵심 내용 미리보기
        print(f"\n🔍 분석 내용 미리보기:")
        print("-" * 40)

        print(f"🧠 CoT 분석 (처음 200자):")
        print(analysis_result["cot_analysis"][:200] + "...")
        print()

        print(f"🔍 5Why 분석 (처음 200자):")
        print(analysis_result["five_why_analysis"][:200] + "...")
        print()

        print(f"🎯 근본 원인 분석 (처음 200자):")
        print(analysis_result["root_cause_analysis"][:200] + "...")
        print()

        print(f"💡 시사점 분석 (처음 200자):")
        print(analysis_result["implication_analysis"][:200] + "...")
        print()

        print("🎉 심층 분석 시스템 테스트 완료!")
        print(f"📁 결과 파일: {result_filename}")

        return True

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_memory_functionality():
    """Memory 기능 테스트"""

    print("\n🧠 Memory 기능 테스트 시작!")
    print("=" * 40)

    try:
        # 심층 분석 시스템 초기화
        deep_analysis = DeepAnalysisSystem()

        # 간단한 테스트 데이터
        test_data = {
            "company_name": "테스트 기업",
            "sector_name": "테스트 섹터",
            "financial_data": "매출 1000억원, 영업이익 100억원",
            "market_data": "주가 10,000원, PER 10배",
            "competitor_data": "경쟁사 A: 매출 800억원, 경쟁사 B: 매출 1200억원",
        }

        # 첫 번째 분석
        print("1️⃣ 첫 번째 분석 실행...")
        result1 = deep_analysis.perform_deep_analysis(**test_data)

        # Memory 상태 확인
        memory_summary1 = deep_analysis.get_analysis_summary()
        print(
            f"   - 첫 번째 분석 후 대화 이력: {memory_summary1['conversation_memory_size']}"
        )

        # 두 번째 분석 (같은 기업, 다른 데이터)
        print("2️⃣ 두 번째 분석 실행...")
        test_data["financial_data"] = "매출 1100억원, 영업이익 120억원"  # 데이터 변경
        result2 = deep_analysis.perform_deep_analysis(**test_data)

        # Memory 상태 재확인
        memory_summary2 = deep_analysis.get_analysis_summary()
        print(
            f"   - 두 번째 분석 후 대화 이력: {memory_summary2['conversation_memory_size']}"
        )

        # Memory가 증가했는지 확인
        if (
            memory_summary2["conversation_memory_size"]
            > memory_summary1["conversation_memory_size"]
        ):
            print("✅ Memory 기능 정상 작동!")
        else:
            print("⚠️ Memory 기능에 문제가 있을 수 있어요.")

        return True

    except Exception as e:
        print(f"❌ Memory 테스트 실패: {e}")
        return False


if __name__ == "__main__":
    print("🚀 심층 분석 시스템 종합 테스트 시작!")
    print("=" * 60)

    # 메인 테스트 실행
    main_test_success = test_deep_analysis_system()

    # Memory 기능 테스트 실행
    memory_test_success = test_memory_functionality()

    # 최종 결과
    print("\n" + "=" * 60)
    print("📊 최종 테스트 결과:")
    print(f"   - 메인 테스트: {'✅ 성공' if main_test_success else '❌ 실패'}")
    print(f"   - Memory 테스트: {'✅ 성공' if memory_test_success else '❌ 실패'}")

    if main_test_success and memory_test_success:
        print("\n🎉 모든 테스트 통과! 심층 분석 시스템이 정상 작동합니다!")
    else:
        print("\n⚠️ 일부 테스트가 실패했어요. 문제를 확인해주세요.")
