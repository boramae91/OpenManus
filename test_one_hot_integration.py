#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 One-Hot Sector Activation 통합 테스트 스크립트

OpenManus 시스템에 섹터별 전문가 팀이 성공적으로 통합되었는지 확인해요!
"""

import asyncio
import os
import sys

from dotenv import load_dotenv

# 환경변수 로딩
load_dotenv()

# 프로젝트 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.logger import logger


async def test_one_hot_integration():
    """One-Hot Sector Activation 통합 테스트"""

    try:
        logger.info("🚀 One-Hot Sector Activation 통합 테스트 시작!")

        # 1. SmartSectorManager 직접 테스트
        logger.info("📋 Step 1: SmartSectorManager 모듈 테스트")

        from app.crew.smart_sector_manager import AnalysisDepth, SmartSectorManager
        from app.llm import LLM

        llm = LLM()
        smart_manager = SmartSectorManager(llm=llm)

        logger.info("✅ SmartSectorManager 초기화 성공!")

        # 2. GICS 섹터 감지 테스트
        logger.info("📋 Step 2: GICS 섹터 감지 테스트")

        test_stocks = [
            ("삼성전자", "005930"),
            ("셀트리온", "068270"),
            ("SK하이닉스", "000660"),
            ("POSCO홀딩스", "005490"),
        ]

        for stock_name, stock_code in test_stocks:
            detected_sector = smart_manager.sector_manager.detect_sector_from_stock(
                stock_name=stock_name, stock_code=stock_code
            )
            logger.info(f"✅ {stock_name} → {detected_sector.name} 섹터")

        # 3. 전체 시스템 통합 테스트
        logger.info("📋 Step 3: 전체 시스템 통합 테스트")

        from enhanced_main import EnhancedStockAnalysisSystem

        system = EnhancedStockAnalysisSystem()
        logger.info("✅ EnhancedStockAnalysisSystem 초기화 성공!")

        # SmartSectorManager가 올바르게 초기화되었는지 확인
        if system.smart_sector_manager:
            logger.info("✅ One-Hot Sector Activation 시스템 통합 성공!")

            # 간단한 분석 테스트 (실제 API 호출 없이)
            test_prompt = "삼성전자의 재무 상황을 분석해주세요"
            analysis_depth = system._detect_analysis_depth_from_prompt(test_prompt)
            logger.info(f"✅ 분석 깊이 감지 테스트: {analysis_depth}")

        else:
            logger.error("❌ SmartSectorManager 통합 실패!")
            return False

        # 4. 통계 정보 출력
        logger.info("📋 Step 4: 시스템 통계 정보")

        stats = smart_manager.get_performance_stats()
        logger.info(f"✅ 총 분석 수행: {stats['total_analyses']}회")
        logger.info(f"✅ 총 비용 절감: ${stats['total_cost_savings']:.2f}")
        logger.info(f"✅ 평균 절약률: {stats['average_savings_rate']:.1f}%")

        logger.info("🎉 One-Hot Sector Activation 통합 테스트 완료!")
        return True

    except Exception as e:
        logger.error(f"❌ 통합 테스트 실패: {e}")
        import traceback

        logger.error(traceback.format_exc())
        return False


async def test_sample_analysis():
    """샘플 분석 실행 테스트 (간단한 버전)"""

    try:
        logger.info("🧪 샘플 분석 테스트 시작!")

        from enhanced_main import EnhancedStockAnalysisSystem

        system = EnhancedStockAnalysisSystem()

        # 간단한 분석 실행 (실제 웹 검색은 제외)
        test_prompt = "삼성전자의 현재 주가는 얼마인가요?"

        # 의도 분석만 테스트
        intent_result = await system.analyze_user_intent(test_prompt)
        logger.info(f"✅ 의도 분석 결과: {intent_result['primary_intent']}")

        # 분석 깊이 감지 테스트
        analysis_depth = system._detect_analysis_depth_from_prompt(test_prompt)
        logger.info(f"✅ 분석 깊이: {analysis_depth}")

        # 섹터 감지 테스트
        if system.smart_sector_manager:
            detected_sector = (
                system.smart_sector_manager.sector_manager.detect_sector_from_stock(
                    stock_name="삼성전자", stock_code="005930"
                )
            )
            logger.info(f"✅ 감지된 섹터: {detected_sector.name}")

        logger.info("🎉 샘플 분석 테스트 완료!")
        return True

    except Exception as e:
        logger.error(f"❌ 샘플 분석 테스트 실패: {e}")
        return False


if __name__ == "__main__":

    async def main():
        logger.info("🚀 One-Hot Sector Activation 통합 테스트 시작!")

        # 기본 통합 테스트
        integration_success = await test_one_hot_integration()

        if integration_success:
            # 샘플 분석 테스트
            analysis_success = await test_sample_analysis()

            if analysis_success:
                logger.info(
                    "🎉 모든 테스트 성공! One-Hot 시스템이 성공적으로 통합되었습니다!"
                )
            else:
                logger.warning(
                    "⚠️ 기본 통합은 성공했지만 샘플 분석에서 문제가 있습니다."
                )
        else:
            logger.error("❌ 기본 통합 테스트 실패!")

    asyncio.run(main())
