#!/usr/bin/env python3
"""
🎯 개선된 펀더멘탈 분석 시스템 테스트
Chat GPT 피드백 반영 효과 확인
"""

import asyncio
import os
import sys
from datetime import datetime

# OpenManus 프로젝트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.crew.smart_sector_manager import AnalysisDepth, SmartSectorManager
from app.llm import LLM
from app.logger import logger


async def test_improved_system():
    """개선된 시스템 테스트"""

    print("🎯 개선된 펀더멘탈 분석 시스템 테스트")
    print("=" * 60)
    print("Chat GPT 피드백 반영 사항:")
    print("✅ 웹검색 강제 실행")
    print("✅ 프롬프트 단순화 (2,000자 → 800자)")
    print("✅ 핵심 4가지 웹검색 필수화")
    print("✅ 모호한 표현 완전 금지")
    print("=" * 60)

    try:
        # LLM 및 SmartSectorManager 초기화
        llm = LLM()
        smart_sector_manager = SmartSectorManager(llm=llm)

        # 캐시 클리어 (새로운 결과 확인)
        smart_sector_manager.cache_manager.clear_all_cache()
        print("🗑️ 캐시 클리어 완료")

        # 테스트용 재무데이터
        financial_data = {
            "success": True,
            "stock_name": "삼성전자",
            "stock_code": "005930",
            "basic_info": {
                "current_price": "73,000원",
                "market_cap": "436조원",
                "per": "18.9배",
                "pbr": "1.96배",
            },
            "financial_ratios": {
                "roe": "9.228%",
                "roa": "6.2%",
                "roic": "2.69%",
                "debt_ratio": "30.2%",
            },
            "cash_flow": {
                "operating_cf": "64,645,830백만원",
                "investing_cf": "-48,370,461백만원",
                "free_cf": "16,193,722백만원",
            },
        }

        print(f"📊 테스트 종목: 삼성전자 (005930)")
        print(f"🎯 테스트 포커스: 웹검색 강제 실행 + 단순화된 프롬프트")
        print("")

        # 종합 분석 실행
        result = await smart_sector_manager.analyze_with_comprehensive_data(
            user_prompt="삼성전자의 투자 매력도를 Chat GPT 피드백을 완전히 반영하여 분석해주세요. 특히 경쟁사 비교와 시계열 트렌드 분석을 웹검색으로 확인해주세요.",
            stock_name="삼성전자",
            stock_code="005930",
            financial_data=financial_data,
            analysis_depth=AnalysisDepth.DEEP,
            pre_detected_gics_sector="Technology Hardware, Storage & Peripherals",
        )

        print("✅ 종합 분석 완료!")
        return True

    except Exception as e:
        print(f"❌ 테스트 실행 중 오류: {e}")
        return False


if __name__ == "__main__":
    try:
        asyncio.run(test_improved_system())
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류: {e}")
