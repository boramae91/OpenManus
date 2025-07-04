# -*- coding: utf-8 -*-
"""
향상된 분석 시스템 테스트 (CoT + 5Why + Memory + 품질 향상 통합)

새로운 향상된 분석 시스템이 제대로 작동하는지 테스트해보는 코드에요!
"""

import json
import os
import sys
from datetime import datetime

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.crew.enhanced_analysis_system import EnhancedAnalysisSystem


def test_enhanced_analysis_system():
    """향상된 분석 시스템 테스트"""

    print("🧪 향상된 분석 시스템 테스트 시작!")
    print("=" * 60)

    try:
        # 1. 향상된 분석 시스템 초기화
        print("1️⃣ 향상된 분석 시스템 초기화 중...")
        enhanced_analysis = EnhancedAnalysisSystem()
        print("✅ 향상된 분석 시스템 초기화 완료!")

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

        **3년간 재무 트렌드:**
        - 2021년: 매출 279.6조원, 영업이익 51.6조원
        - 2022년: 매출 302.2조원, 영업이익 43.4조원
        - 2023년: 매출 258.9조원, 영업이익 6.6조원
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

        **거래량 및 유동성:**
        - 일평균 거래량: 1,200만주
        - 거래대금: 9조원
        - 외국인 지분율: 52.3%
        """

        competitor_data = """
        **경쟁사 정보:**

        **SK하이닉스 (반도체):**
        - 매출액: 29.2조원 (전년 대비 -26.3%)
        - 영업이익: -7.7조원 (적자)
        - 시가총액: 1,200조원
        - PER: N/A (적자)
        - 시장 점유율: DRAM 28%, NAND 18%

        **LG전자 (가전/디스플레이):**
        - 매출액: 84.3조원 (전년 대비 +1.2%)
        - 영업이익: 3.5조원 (전년 대비 +12.5%)
        - 시가총액: 800조원
        - PER: 22.8배
        - 시장 점유율: OLED TV 60%, 가전 15%

        **애플 (글로벌 경쟁사):**
        - 매출액: 3,830억 달러 (전년 대비 -2.8%)
        - 영업이익: 1,140억 달러 (전년 대비 -3.4%)
        - 시가총액: 3조 달러
        - PER: 28.5배
        - 시장 점유율: 스마트폰 18%, 태블릿 35%

        **TSMC (반도체 파운드리):**
        - 매출액: 2.2조원 (대만 달러, 전년 대비 -4.5%)
        - 영업이익: 8,500억원 (대만 달러, 전년 대비 -19.3%)
        - 시가총액: 15조원 (대만 달러)
        - PER: 18.2배
        - 시장 점유율: 파운드리 58%

        **업계 평균 지표:**
        - PER: 18.5배
        - PBR: 1.8배
        - ROE: 12.3%
        - 영업이익률: 8.7%
        """

        print("✅ 테스트 데이터 준비 완료!")

        # 3. 향상된 분석 실행
        print("\n3️⃣ 향상된 분석 실행 중...")
        print("⏳ 분석에 시간이 걸릴 수 있어요. 잠시만 기다려주세요...")

        analysis_result = enhanced_analysis.perform_enhanced_analysis(
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

        print("✅ 향상된 분석 완료!")

        # 5. 결과 저장
        print("\n5️⃣ 분석 결과 저장 중...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_filename = f"enhanced_analysis_result_{timestamp}.json"

        enhanced_analysis.save_enhanced_analysis_result(
            result_filename, analysis_result
        )

        # 6. 결과 요약 출력
        print("\n6️⃣ 분석 결과 요약:")
        print("=" * 60)

        print(f"📊 분석 대상: {analysis_result['company_name']}")
        print(f"🏭 섹터: {analysis_result['sector_name']}")
        print(f"🔬 분석 방법: {analysis_result['analysis_method']}")
        print(f"⏰ 분석 시간: {analysis_result['timestamp']}")

        # Memory 정보 출력
        memory_summary = enhanced_analysis.get_enhanced_analysis_summary()
        print(f"\n🧠 통합 Memory 상태:")
        print(f"   - 통합 대화 이력 크기: {memory_summary['integrated_memory_size']}")
        print(
            f"   - 통합 요약 메모리 크기: {memory_summary['integrated_summary_size']}"
        )

        # LangChain 메시지 객체를 문자열로 변환하는 함수
        def convert_to_serializable(obj):
            """LangChain 메시지 객체를 JSON 직렬화 가능한 형태로 변환"""
            if hasattr(obj, "content"):
                return str(obj.content)
            elif isinstance(obj, dict):
                return {k: convert_to_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_serializable(item) for item in obj]
            else:
                return str(obj)

        # 각 단계별 분석 결과 길이
        print(f"\n📝 분석 결과 길이:")
        print(
            f"   - 심층 분석: {len(json.dumps(convert_to_serializable(analysis_result['deep_analysis']), ensure_ascii=False))} 문자"
        )
        print(
            f"   - 품질 향상: {len(json.dumps(convert_to_serializable(analysis_result['quality_enhancement']), ensure_ascii=False))} 문자"
        )
        print(f"   - 통합 분석: {len(analysis_result['integration_analysis'])} 문자")
        print(f"   - 최종 보고서: {len(analysis_result['final_report'])} 문자")

        # 7. 각 단계별 핵심 내용 미리보기
        print(f"\n🔍 분석 내용 미리보기:")
        print("-" * 40)

        print(f"🧠 심층 분석 (CoT + 5Why):")
        deep_analysis = analysis_result["deep_analysis"]
        print(f"   - CoT 분석: {deep_analysis['cot_analysis'][:150]}...")
        print(f"   - 5Why 분석: {deep_analysis['five_why_analysis'][:150]}...")
        print()

        print(f"🔧 품질 향상:")
        quality_enhancement = analysis_result["quality_enhancement"]
        if "enhanced_analysis" in quality_enhancement:
            print(
                f"   - 보완된 분석: {quality_enhancement['enhanced_analysis'][:150]}..."
            )
        print()

        print(f"🔗 통합 분석:")
        print(f"   {analysis_result['integration_analysis'][:200]}...")
        print()

        print(f"📊 최종 보고서:")
        print(f"   {analysis_result['final_report'][:200]}...")
        print()

        print("🎉 향상된 분석 시스템 테스트 완료!")
        print(f"📁 결과 파일: {result_filename}")

        return True

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_analysis_comparison():
    """분석 방법 비교 테스트"""

    print("\n🔍 분석 방법 비교 테스트 시작!")
    print("=" * 40)

    try:
        # 향상된 분석 시스템 초기화
        enhanced_analysis = EnhancedAnalysisSystem()

        # 간단한 테스트 데이터
        test_data = {
            "company_name": "테스트 기업",
            "sector_name": "테스트 섹터",
            "financial_data": "매출 1000억원, 영업이익 100억원, ROE 15%",
            "market_data": "주가 10,000원, PER 10배, 시가총액 5000억원",
            "competitor_data": "경쟁사 A: 매출 800억원, 경쟁사 B: 매출 1200억원, 업계 평균 PER 12배",
        }

        # 분석 방법 비교 실행
        print("🔍 분석 방법 비교 실행 중...")
        comparison_result = enhanced_analysis.compare_analysis_methods(**test_data)

        if "error" in comparison_result:
            print(f"❌ 비교 분석 실패: {comparison_result['error']}")
            return False

        # 비교 결과 출력
        print("📊 분석 방법 비교 결과:")
        print("-" * 30)

        metrics = comparison_result["comparison_metrics"]
        print(f"📏 분석 길이 비교:")
        print(
            f"   - 심층 분석만: {metrics['total_analysis_length']['deep_only']:,} 문자"
        )
        print(
            f"   - 향상된 분석: {metrics['total_analysis_length']['enhanced']:,} 문자"
        )
        print(
            f"   - 향상도: {metrics['total_analysis_length']['enhanced'] / metrics['total_analysis_length']['deep_only']:.1f}배"
        )

        quality = comparison_result["analysis_quality_comparison"]
        print(f"\n🎯 품질 비교:")
        print(f"   - 심층 분석만: {quality['deep_only']['depth']}")
        print(f"   - 향상된 분석: {quality['enhanced']['depth']}")

        print(f"\n💡 권장사항: {comparison_result['recommendation']}")

        return True

    except Exception as e:
        print(f"❌ 비교 테스트 실패: {e}")
        return False


def test_memory_integration():
    """Memory 통합 기능 테스트"""

    print("\n🧠 Memory 통합 기능 테스트 시작!")
    print("=" * 40)

    try:
        # 향상된 분석 시스템 초기화
        enhanced_analysis = EnhancedAnalysisSystem()

        # 첫 번째 분석
        print("1️⃣ 첫 번째 분석 실행...")
        test_data1 = {
            "company_name": "테스트 기업 A",
            "sector_name": "테스트 섹터",
            "financial_data": "매출 1000억원, 영업이익 100억원",
            "market_data": "주가 10,000원, PER 10배",
            "competitor_data": "경쟁사 A: 매출 800억원",
        }

        result1 = enhanced_analysis.perform_enhanced_analysis(**test_data1)

        # Memory 상태 확인
        memory_summary1 = enhanced_analysis.get_enhanced_analysis_summary()
        print(
            f"   - 첫 번째 분석 후 통합 이력: {memory_summary1['integrated_memory_size']}"
        )

        # 두 번째 분석
        print("2️⃣ 두 번째 분석 실행...")
        test_data2 = {
            "company_name": "테스트 기업 B",
            "sector_name": "테스트 섹터",
            "financial_data": "매출 1200억원, 영업이익 150억원",
            "market_data": "주가 12,000원, PER 12배",
            "competitor_data": "경쟁사 B: 매출 1000억원",
        }

        result2 = enhanced_analysis.perform_enhanced_analysis(**test_data2)

        # Memory 상태 재확인
        memory_summary2 = enhanced_analysis.get_enhanced_analysis_summary()
        print(
            f"   - 두 번째 분석 후 통합 이력: {memory_summary2['integrated_memory_size']}"
        )

        # Memory가 증가했는지 확인
        if (
            memory_summary2["integrated_memory_size"]
            > memory_summary1["integrated_memory_size"]
        ):
            print("✅ Memory 통합 기능 정상 작동!")
        else:
            print("⚠️ Memory 통합 기능에 문제가 있을 수 있어요.")

        return True

    except Exception as e:
        print(f"❌ Memory 통합 테스트 실패: {e}")
        return False


if __name__ == "__main__":
    print("🚀 향상된 분석 시스템 종합 테스트 시작!")
    print("=" * 60)

    # 메인 테스트 실행
    main_test_success = test_enhanced_analysis_system()

    # 분석 방법 비교 테스트 실행
    comparison_test_success = test_analysis_comparison()

    # Memory 통합 테스트 실행
    memory_test_success = test_memory_integration()

    # 최종 결과
    print("\n" + "=" * 60)
    print("📊 최종 테스트 결과:")
    print(f"   - 메인 테스트: {'✅ 성공' if main_test_success else '❌ 실패'}")
    print(f"   - 비교 테스트: {'✅ 성공' if comparison_test_success else '❌ 실패'}")
    print(f"   - Memory 테스트: {'✅ 성공' if memory_test_success else '❌ 실패'}")

    if main_test_success and comparison_test_success and memory_test_success:
        print("\n🎉 모든 테스트 통과! 향상된 분석 시스템이 정상 작동합니다!")
        print("\n🌟 주요 특징:")
        print("   - CoT + 5Why 기법으로 심층 분석")
        print("   - LangChain Memory로 연속성 확보")
        print("   - 품질 향상 시스템으로 완성도 극대화")
        print("   - 통합 분석으로 일관성 확보")
    else:
        print("\n⚠️ 일부 테스트가 실패했어요. 문제를 확인해주세요.")
