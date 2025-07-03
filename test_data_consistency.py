#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
데이터 일관성 테스트 스크립트
ROIC/WACC 값이 전문가마다 일관되게 나오는지 확인해요
"""

import asyncio
import os
import sys

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.logger import logger
from app.tool.expert_analysis_integration import ExpertAnalysisIntegration


async def test_data_consistency():
    """데이터 일관성 테스트"""
    logger.info("🧪 데이터 일관성 테스트 시작...")

    # 테스트용 재무 데이터 (삼성전자 예시)
    test_financial_data = {
        "revenue": 300000000000000,  # 300조원
        "operating_income": 30000000000000,  # 30조원
        "net_income": 25000000000000,  # 25조원
        "total_assets": 400000000000000,  # 400조원
        "total_equity": 300000000000000,  # 300조원
        "total_liabilities": 100000000000000,  # 100조원
        "current_price": 65000,  # 6.5만원
        # 실제 계산된 값들 (일관성 보장용)
        "calculated_roic": 12.5,  # 실제 계산된 ROIC
        "calculated_roe": 8.3,  # 실제 계산된 ROE
        "calculated_wacc": 8.0,  # 실제 계산된 WACC
    }

    test_market_data = {
        "current_price": 65000,
        "price_history": [60000, 61000, 62000, 63000, 64000, 65000],  # 상승 추세
        "volume": 1000000,
    }

    # 전문가 통합 분석 도구 초기화
    expert_integration = ExpertAnalysisIntegration()

    try:
        # 1. 펀더멘털 전문가 분석
        logger.info("📊 펀더멘털 전문가 분석 테스트...")
        fundamental_result = expert_integration.analyze_fundamental(test_financial_data)

        if fundamental_result.get("success"):
            roic_value = fundamental_result.get("calculated_metrics", {}).get("roic")
            roe_value = fundamental_result.get("calculated_metrics", {}).get("roe")
            logger.info(
                f"✅ 펀더멘털 분석 성공 - ROIC: {roic_value}%, ROE: {roe_value}%"
            )
        else:
            logger.error(f"❌ 펀더멘털 분석 실패: {fundamental_result.get('error')}")

        # 2. 밸류에이션 전문가 분석
        logger.info("💰 밸류에이션 전문가 분석 테스트...")
        valuation_result = expert_integration.analyze_valuation(
            test_financial_data, test_market_data
        )

        if valuation_result.get("success"):
            roic_wacc = valuation_result.get("roic_wacc_analysis", {})
            roic_value = roic_wacc.get("roic")
            wacc_value = roic_wacc.get("wacc")
            spread = roic_wacc.get("spread")
            logger.info(
                f"✅ 밸류에이션 분석 성공 - ROIC: {roic_value}%, WACC: {wacc_value}%, 스프레드: {spread}%"
            )
            logger.info(f"📊 가치창출 가능성: {roic_wacc.get('value_creation')}")
        else:
            logger.error(f"❌ 밸류에이션 분석 실패: {valuation_result.get('error')}")

        # 3. 데이터 일관성 검증
        logger.info("🔍 데이터 일관성 검증...")

        fundamental_roic = fundamental_result.get("calculated_metrics", {}).get("roic")
        valuation_roic = valuation_result.get("roic_wacc_analysis", {}).get("roic")

        if fundamental_roic == valuation_roic:
            logger.info(f"✅ ROIC 일관성 확인: {fundamental_roic}%")
        else:
            logger.error(
                f"❌ ROIC 불일치: 펀더멘털 {fundamental_roic}% vs 밸류에이션 {valuation_roic}%"
            )

        # 4. 종합 분석 테스트
        logger.info("🎯 종합 분석 테스트...")
        all_data = {
            "financial_data": test_financial_data,
            "market_data": test_market_data,
            "company_data": test_financial_data,
            "industry_data": {},
            "operation_data": {},
        }

        comprehensive_result = await expert_integration.perform_comprehensive_analysis(
            all_data
        )

        if comprehensive_result.get("success"):
            expert_analyses = comprehensive_result.get("expert_analyses", {})
            logger.info(
                f"✅ 종합 분석 성공 - {len(expert_analyses)}명 전문가 분석 완료"
            )

            # 각 전문가의 ROIC 값 확인
            for expert_name, analysis in expert_analyses.items():
                if analysis.get("success"):
                    calculated_metrics = analysis.get("calculated_metrics", {})
                    roic = calculated_metrics.get("roic")
                    if roic is not None:
                        logger.info(f"📊 {expert_name}: ROIC {roic}%")
        else:
            logger.error(f"❌ 종합 분석 실패: {comprehensive_result.get('error')}")

        logger.info("🎉 데이터 일관성 테스트 완료!")

    except Exception as e:
        logger.error(f"❌ 테스트 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_data_consistency())
