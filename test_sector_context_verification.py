#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
섹터별 전문 컨텍스트 동적 수집 검증 테스트
GICS 섹터 전문가로부터 모든 분석 관련 정보가 실제로 가져와지는지 확인해요!
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.crew.gics_sectors import GICSSector, GICSSectorManager
from app.tool.fundamental_analysis_tools import FundamentalAnalysisTools


def test_sector_context_collection():
    """섹터별 전문 컨텍스트 수집 테스트"""
    print("🔍 섹터별 전문 컨텍스트 동적 수집 검증 테스트")
    print("=" * 70)

    # 섹터 매니저 초기화
    sector_manager = GICSSectorManager()
    fundamental_tools = FundamentalAnalysisTools()

    # 테스트할 섹터들
    test_sectors = [
        GICSSector.INFORMATION_TECHNOLOGY,  # 삼성전자
        GICSSector.FINANCIALS,  # KB금융
        GICSSector.HEALTH_CARE,  # 셀트리온
        GICSSector.ENERGY,  # SK에너지
    ]

    for sector in test_sectors:
        print(
            f"\n📊 {sector_manager.get_sector_korean_name(sector)} 섹터 전문 컨텍스트 검증"
        )
        print("-" * 50)

        # 1. 섹터별 전문 컨텍스트 직접 확인
        print("1️⃣ 섹터별 전문 컨텍스트 (직접 조회):")
        sector_context = sector_manager.get_sector_context(sector)
        print(f"   📋 업계 포커스: {sector_context['industry_focus']}")
        print(
            f"   🔍 중점 분석 포인트: {sector_context['key_analysis_points'][:80]}..."
        )
        print(f"   ⚠️  주요 위험 요소: {sector_context['key_risks'][:80]}...")
        print(f"   💰 밸류에이션 접근법: {sector_context['valuation_approach']}")
        print(f"   📈 경기순환성: {sector_context['cyclical_nature']}")
        print(f"   📊 핵심 지표: {sector_context['critical_metrics'][:80]}...")

        # 2. 펀더멘털 도구를 통한 지침 수신
        print("\n2️⃣ 펀더멘털 도구를 통한 지침 수신:")
        guidance = fundamental_tools._get_sector_analysis_guidance(sector)

        print(f"   📋 섹터명: {guidance['sector_korean_name']}")
        print(f"   📊 핵심 지표: {len(guidance['key_metrics'])}개")
        print(f"   🔍 분석 포인트: {guidance['analysis_points'][:80]}...")
        print(f"   ⚠️  위험 요소: {guidance['risk_factors'][:80]}...")
        print(f"   📈 핵심 지표: {guidance['critical_metrics'][:80]}...")

        # 3. 섹터 컨텍스트 포함 확인
        print("\n3️⃣ 섹터 컨텍스트 포함 확인:")
        if "sector_context" in guidance:
            context = guidance["sector_context"]
            print("   ✅ 섹터 컨텍스트가 지침에 포함되어 있습니다!")
            print(f"   📋 업계 포커스: {context['industry_focus']}")
            print(f"   💰 밸류에이션 접근법: {context['valuation_approach']}")
            print(f"   📈 경기순환성: {context['cyclical_nature']}")
        else:
            print("   ❌ 섹터 컨텍스트가 지침에 포함되지 않았습니다!")

        # 4. 컨텍스트 일치성 확인
        print("\n4️⃣ 컨텍스트 일치성 확인:")
        direct_context = sector_manager.get_sector_context(sector)
        guidance_context = guidance.get("sector_context", {})

        if direct_context == guidance_context:
            print("   ✅ 직접 조회와 지침 수신 컨텍스트가 일치합니다!")
        else:
            print("   ❌ 컨텍스트가 일치하지 않습니다!")
            print(f"   직접 조회 키: {list(direct_context.keys())}")
            print(f"   지침 수신 키: {list(guidance_context.keys())}")


def test_comprehensive_sector_guide():
    """종합 섹터 가이드 테스트"""
    print("\n\n📚 종합 섹터 가이드 테스트")
    print("=" * 70)

    sector_manager = GICSSectorManager()

    # 삼성전자 섹터로 종합 가이드 확인
    sector = GICSSector.INFORMATION_TECHNOLOGY

    print(f"📱 {sector_manager.get_sector_korean_name(sector)} 섹터 종합 가이드:")

    # 종합 섹터 가이드 가져오기
    comprehensive_guide = sector_manager.get_comprehensive_sector_guide(sector)

    print(f"   📋 섹터명: {comprehensive_guide['sector_name']}")
    print(f"   🔍 분석 포인트: {comprehensive_guide['key_analysis_points'][:100]}...")
    print(f"   ⚠️  위험 요소: {comprehensive_guide['key_risks'][:100]}...")
    print(f"   📊 핵심 지표: {comprehensive_guide['critical_metrics'][:100]}...")
    print(f"   💰 밸류에이션: {comprehensive_guide['valuation_approach']}")
    print(f"   📈 경기순환성: {comprehensive_guide['cyclical_nature']}")


def test_sector_analysis_guide_print():
    """섹터 분석 가이드 출력 테스트"""
    print("\n\n🖨️ 섹터 분석 가이드 출력 테스트")
    print("=" * 70)

    sector_manager = GICSSectorManager()

    # 정보기술 섹터 분석 가이드 출력
    sector = GICSSector.INFORMATION_TECHNOLOGY

    print(f"📱 {sector_manager.get_sector_korean_name(sector)} 섹터 분석 가이드:")
    print("-" * 50)

    # 분석 가이드 출력 (실제로는 콘솔에 출력됨)
    try:
        sector_manager.print_sector_analysis_guide(sector)
        print("   ✅ 섹터 분석 가이드 출력 성공!")
    except Exception as e:
        print(f"   ❌ 섹터 분석 가이드 출력 실패: {e}")


def test_actual_analysis_with_context():
    """실제 분석에서 컨텍스트 사용 확인"""
    print("\n\n🔬 실제 분석에서 컨텍스트 사용 확인")
    print("=" * 70)

    fundamental_tools = FundamentalAnalysisTools()

    # 삼성전자 샘플 데이터
    samsung_data = {
        "revenue": 279600000000000,  # 279.6조원 (2023년)
        "operating_income": 64000000000000,  # 6.4조원
        "net_income": 15000000000000,  # 1.5조원
        "total_assets": 426800000000000,  # 426.8조원
        "total_equity": 302000000000000,  # 302조원
        "total_debt": 124800000000000,  # 124.8조원
        "cash": 50000000000000,  # 50조원
    }

    print("📱 삼성전자 섹터 컨텍스트 연동 분석:")
    try:
        result = fundamental_tools.analyze_fundamental_with_sector_guidance(
            samsung_data, "삼성전자", "005930"
        )

        print("✅ 분석 완료!")
        print(f"📊 섹터: {result.get('sector_info', {}).get('sector_name', 'N/A')}")

        # 섹터 지침에서 컨텍스트 확인
        if "sector_guidance" in result:
            guidance = result["sector_guidance"]
            print(f"📋 섹터 지침 수신: {len(guidance)}개 항목")

            if "sector_context" in guidance:
                context = guidance["sector_context"]
                print("   ✅ 섹터 컨텍스트 포함:")
                print(f"      📋 업계 포커스: {context['industry_focus']}")
                print(f"      💰 밸류에이션: {context['valuation_approach']}")
                print(f"      📈 경기순환성: {context['cyclical_nature']}")
            else:
                print("   ❌ 섹터 컨텍스트가 포함되지 않았습니다!")

        # 분석 결과에서 컨텍스트 활용 확인
        if "analysis_result" in result:
            analysis = result["analysis_result"]
            print(f"🔍 분석 결과: {len(analysis)}개 항목")
            print(f"   📝 분석 방법: {result.get('analysis_method', 'N/A')}")

    except Exception as e:
        print(f"❌ 분석 실패: {e}")


if __name__ == "__main__":
    test_sector_context_collection()
    test_comprehensive_sector_guide()
    test_sector_analysis_guide_print()
    test_actual_analysis_with_context()
    print("\n🎉 섹터별 전문 컨텍스트 동적 수집 검증 완료!")
