#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기술적 분석 전문가 수정사항 테스트
프롬프트 템플릿 변수 불일치 문제 해결 확인
"""

import asyncio
import os
import sys
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.crew.gics_sectors import GICSSector, GICSSectorManager
from app.crew.sector_teams import SectorTeamFactory


async def test_technical_analysis_fix():
    """기술적 분석 전문가 수정사항 테스트"""
    print("🔧 기술적 분석 전문가 수정사항 테스트 시작")
    print("=" * 60)

    try:
        # 1. 섹터 매니저 초기화
        print("\n📊 1단계: 섹터 매니저 초기화...")
        sector_manager = GICSSectorManager()
        print("✅ 섹터 매니저 초기화 완료")

        # 2. 섹터팀 팩토리 초기화
        print("\n🏭 2단계: 섹터팀 팩토리 초기화...")
        team_factory = SectorTeamFactory(sector_manager)
        print("✅ 섹터팀 팩토리 초기화 완료")

        # 3. 정보기술 섹터팀 생성
        print("\n💻 3단계: 정보기술 섹터팀 생성...")
        it_team = team_factory.create_sector_team(GICSSector.INFORMATION_TECHNOLOGY)
        print(f"✅ 정보기술 섹터팀 생성 완료: {len(it_team.experts)}명 전문가")

        # 4. 기술적 분석가 찾기
        print("\n🎯 4단계: 기술적 분석가 찾기...")
        technical_analyst = None
        for expert in it_team.experts:
            if "기술적 분석가" in expert.name:
                technical_analyst = expert
                break

        if not technical_analyst:
            print("❌ 기술적 분석가를 찾을 수 없습니다!")
            return

        print(f"✅ 기술적 분석가 발견: {technical_analyst.name}")
        print(f"   - LangChain 활성화: {technical_analyst.langchain_enabled}")
        print(f"   - Chain 객체: {type(technical_analyst.langchain_chain)}")

        # 5. 기술적 분석 테스트
        print("\n📈 5단계: 기술적 분석 테스트...")

        # 테스트용 입력 데이터 (실제 데이터 구조와 유사하게)
        test_input_data = {
            "company_name": "삼성전자",
            "sector_name": "정보기술",
            "price_data": {
                "current_snapshot": {"price": 67800.0},
                "support_resistance": {
                    "nearest_support": 60200.0,
                    "nearest_resistance": None,
                },
            },
            "market_data": {"kospi": 2500},
            "technical_indicators": {
                "rsi": {"current_value": 76.0, "interpretation": "과매수"},
                "macd": {
                    "MACD_line": 2021.9,
                    "signal_interpretation": "상승 추세 지속",
                },
                "moving_averages": {
                    "MA_5": 66000.0,
                    "MA_20": 62515.0,
                    "MA_60": 58651.7,
                },
                "bollinger_bands": {
                    "position_analysis": "상단 밴드 근처",
                    "signal": "매도 고려",
                },
                "volume_indicators": {"volume_ratio": 0.86},
            },
            "trading_signals": {
                "overall_signal": "중립",
                "recommendation": "관망 또는 기존 포지션 유지",
            },
        }

        print("🔍 기술적 분석 실행 중...")
        result = technical_analyst.run_full_technical_analysis(test_input_data)

        # 6. 결과 확인
        print("\n📋 6단계: 결과 확인...")
        if "error" in result:
            print(f"❌ 기술적 분석 실패: {result['error']}")
        else:
            print("✅ 기술적 분석 성공!")
            print(f"   - 분석 시간: {result.get('analysis_time', 0):.2f}초")
            print(f"   - 분석 방법: {result.get('analysis_method', 'N/A')}")
            print(f"   - 분석 초점: {result.get('analysis_focus', 'N/A')}")
            print(f"   - 제한사항: {result.get('restrictions', [])}")

            # 분석 결과 일부 출력
            technical_analysis = result.get("technical_analysis", "")
            if technical_analysis:
                print(f"\n📊 분석 결과 (처음 500자):")
                print(
                    technical_analysis[:500] + "..."
                    if len(technical_analysis) > 500
                    else technical_analysis
                )

        print("\n🎉 기술적 분석 전문가 수정사항 테스트 완료!")

    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # 환경변수 설정 (필요한 경우)
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("   테스트를 위해 환경변수를 설정하거나 config.example.env를 참고하세요.")

    # 테스트 실행
    asyncio.run(test_technical_analysis_fix())
