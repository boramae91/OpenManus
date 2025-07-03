#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GICS 섹터 연동 펀더멘털 분석 테스트 스크립트

기존 GICS 섹터 전문가들과 연동하여 동적으로 분석 지침을 받아오는
펀더멘털 분석의 품질을 테스트해요!
"""

import asyncio
import os
import sys

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.logger import logger
from app.tool.fundamental_analysis_tools import FundamentalAnalysisTools


async def test_sector_guided_fundamental_analysis():
    """GICS 섹터 연동 펀더멘털 분석 테스트"""
    logger.info("🧪 GICS 섹터 연동 펀더멘털 분석 테스트 시작...")

    # 펀더멘털 분석 도구 초기화
    fundamental_tools = FundamentalAnalysisTools()

    # 테스트용 재무 데이터 (삼성전자 예시)
    test_financial_data = {
        "revenue": 300000000000000,  # 300조원
        "operating_income": 30000000000000,  # 30조원
        "net_income": 25000000000000,  # 25조원
        "total_assets": 400000000000000,  # 400조원
        "total_equity": 300000000000000,  # 300조원
        "total_liabilities": 100000000000000,  # 100조원
        "current_price": 65000,  # 6.5만원
        "rnd_expense": 20000000000000,  # 20조원 (R&D)
        "capex": 25000000000000,  # 25조원 (자본투자)
    }

    try:
        # 1. GICS 섹터 연동 펀더멘털 분석 테스트
        logger.info("📊 GICS 섹터 연동 펀더멘털 분석 테스트...")

        sector_guided_result = (
            fundamental_tools.analyze_fundamental_with_sector_guidance(
                financial_data=test_financial_data,
                company_name="삼성전자",
                company_code="005930",
            )
        )

        if sector_guided_result.get("success"):
            detected_sector = sector_guided_result.get("detected_sector")
            sector_guidance = sector_guided_result.get("sector_guidance", {})
            analysis_result = sector_guided_result.get("analysis_result", {})

            logger.info(f"✅ 섹터 연동 분석 성공!")
            logger.info(f"🏢 감지된 섹터: {detected_sector}")
            logger.info(f"📋 섹터 지침: {len(sector_guidance)}개 항목")

            # 섹터 지침 상세 출력
            if sector_guidance:
                logger.info(
                    f"📊 핵심 분석 지표: {sector_guidance.get('key_metrics', [])}"
                )
                logger.info(
                    f"🎯 중점 분석 포인트: {sector_guidance.get('analysis_points', 'N/A')}"
                )
                logger.info(
                    f"⚠️ 주요 위험 요소: {sector_guidance.get('risk_factors', 'N/A')}"
                )

            # 분석 결과 출력
            if analysis_result:
                calculated_metrics = analysis_result.get("calculated_metrics", {})
                llm_analysis = analysis_result.get("analysis_result", {})

                logger.info(f"📈 계산된 지표: {len(calculated_metrics)}개")
                for key, value in calculated_metrics.items():
                    if isinstance(value, (int, float)):
                        logger.info(f"  - {key}: {value:.2f}%")
                    else:
                        logger.info(f"  - {key}: {value}")

                if llm_analysis:
                    logger.info(f"🤖 LLM 분석 결과:")
                    logger.info(
                        f"  - 분석 요약: {llm_analysis.get('analysis_summary', 'N/A')}"
                    )
                    logger.info(
                        f"  - 투자 추천: {llm_analysis.get('recommendation', 'N/A')}"
                    )
                    logger.info(
                        f"  - 핵심 인사이트: {llm_analysis.get('key_insights', [])}"
                    )
                    logger.info(
                        f"  - 위험 요소: {llm_analysis.get('risk_factors', [])}"
                    )
        else:
            logger.error(f"❌ 섹터 연동 분석 실패: {sector_guided_result.get('error')}")

        # 2. 기존 방식과 비교 테스트
        logger.info("📊 기존 방식 펀더멘털 분석 테스트...")

        traditional_result = fundamental_tools.calculate_roic_trend(test_financial_data)

        if traditional_result.get("success"):
            logger.info(f"✅ 기존 방식 분석 성공!")
            logger.info(f"📈 ROIC: {traditional_result.get('roic', 0):.2f}%")
        else:
            logger.error(f"❌ 기존 방식 분석 실패: {traditional_result.get('error')}")

        # 3. 분석 방식 비교
        logger.info("🔍 분석 방식 비교...")

        if sector_guided_result.get("success") and traditional_result.get("success"):
            sector_roic = (
                sector_guided_result.get("analysis_result", {})
                .get("calculated_metrics", {})
                .get("roic", 0)
            )
            traditional_roic = traditional_result.get("roic", 0)

            logger.info(f"📊 ROIC 비교:")
            logger.info(f"  - 섹터 연동 방식: {sector_roic:.2f}%")
            logger.info(f"  - 기존 방식: {traditional_roic:.2f}%")

            if abs(sector_roic - traditional_roic) < 0.1:
                logger.info("✅ 두 방식의 ROIC 계산이 일치합니다!")
            else:
                logger.warning("⚠️ 두 방식의 ROIC 계산에 차이가 있습니다.")

        logger.info("🎉 GICS 섹터 연동 펀더멘털 분석 테스트 완료!")

    except Exception as e:
        logger.error(f"❌ 테스트 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_sector_guided_fundamental_analysis())
