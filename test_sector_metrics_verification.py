#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
섹터별 핵심 지표 동적 수집 검증 테스트
GICS 섹터 전문가로부터 핵심 지표들이 실제로 가져와지는지 확인해요!
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.crew.gics_sectors import GICSSector, GICSSectorManager
from app.tool.fundamental_analysis_tools import FundamentalAnalysisTools


def test_sector_metrics_collection():
    """섹터별 핵심 지표 수집 테스트"""
    print("🔍 섹터별 핵심 지표 동적 수집 검증 테스트")
    print("=" * 60)

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
        print(f"\n📊 {sector_manager.get_sector_korean_name(sector)} 섹터 검증")
        print("-" * 40)

        # 1. 섹터별 핵심 지표 직접 확인
        print("1️⃣ 섹터별 핵심 지표 (직접 조회):")
        key_metrics = sector_manager.get_sector_key_metrics(sector)
        for i, metric in enumerate(key_metrics, 1):
            print(f"   {i}. {metric}")

        # 2. 펀더멘털 도구를 통한 지침 수신
        print("\n2️⃣ 펀더멘털 도구를 통한 지침 수신:")
        guidance = fundamental_tools._get_sector_analysis_guidance(sector)

        print(f"   📋 섹터명: {guidance['sector_korean_name']}")
        print(f"   📊 핵심 지표: {len(guidance['key_metrics'])}개")
        print(f"   🔍 분석 포인트: {guidance['analysis_points'][:50]}...")
        print(f"   ⚠️  위험 요소: {guidance['risk_factors'][:50]}...")

        # 3. 지표 일치성 확인
        print("\n3️⃣ 지표 일치성 확인:")
        direct_metrics = set(sector_manager.get_sector_key_metrics(sector))
        guidance_metrics = set(guidance["key_metrics"])

        if direct_metrics == guidance_metrics:
            print("   ✅ 직접 조회와 지침 수신 지표가 일치합니다!")
        else:
            print("   ❌ 지표가 일치하지 않습니다!")
            print(f"   직접 조회: {direct_metrics}")
            print(f"   지침 수신: {guidance_metrics}")

        # 4. 실제 분석에서 사용되는지 확인
        print("\n4️⃣ 실제 분석에서 사용 확인:")
        sample_data = {
            "revenue": 1000000000000,  # 1조원
            "operating_income": 150000000000,  # 1500억원
            "net_income": 100000000000,  # 1000억원
            "total_assets": 2000000000000,  # 2조원
            "total_equity": 1000000000000,  # 1조원
        }

        try:
            analysis_result = (
                fundamental_tools.analyze_fundamental_with_sector_guidance(
                    sample_data, "테스트기업"
                )
            )
            print("   ✅ 섹터 연동 분석이 정상 실행됩니다!")
            print(f"   📈 분석 결과 키: {list(analysis_result.keys())}")
        except Exception as e:
            print(f"   ❌ 섹터 연동 분석 실패: {e}")


def test_specific_company_analysis():
    """특정 기업 분석 테스트"""
    print("\n\n🏢 특정 기업 분석 테스트")
    print("=" * 60)

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

    print("📱 삼성전자 섹터 연동 분석:")
    try:
        result = fundamental_tools.analyze_fundamental_with_sector_guidance(
            samsung_data, "삼성전자", "005930"
        )

        print("✅ 분석 완료!")
        print(f"📊 섹터: {result.get('sector_info', {}).get('sector_name', 'N/A')}")
        print(f"🔍 분석 결과: {len(result.get('analysis_result', {}))}개 항목")

        # 섹터별 지침이 실제로 사용되었는지 확인
        if "sector_guidance" in result:
            guidance = result["sector_guidance"]
            print(f"📋 섹터 지침 수신: {len(guidance.get('key_metrics', []))}개 지표")
            print(f"   핵심 지표: {', '.join(guidance.get('key_metrics', [])[:3])}...")

    except Exception as e:
        print(f"❌ 분석 실패: {e}")


if __name__ == "__main__":
    test_sector_metrics_collection()
    test_specific_company_analysis()
    print("\n🎉 섹터별 핵심 지표 동적 수집 검증 완료!")
