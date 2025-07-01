#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
밸류에이션 전문가 LangChain Chain 테스트

이 파일은 밸류에이션 전문가의 LangChain Chain이 정상적으로 작동하는지 테스트해요.
5단계 밸류에이션 분석 과정을 단계별로 검증하고 성능을 측정해요!
"""

import json
import os
import sys
from datetime import datetime
from typing import Any, Dict

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import Config
from app.crew.gics_sectors import GICSSector, GICSSectorManager
from app.crew.sector_teams import SectorTeamFactory


def test_valuation_langchain():
    """밸류에이션 전문가 LangChain Chain 테스트"""

    print("🚀 밸류에이션 전문가 LangChain Chain 테스트 시작!")
    print("=" * 60)

    try:
        # 1. 설정 로드
        print("📋 1단계: 설정 로드 중...")
        config = Config()
        print("✅ 설정 로드 완료!")

        # 2. GICS 섹터 매니저 초기화
        print("\n🏭 2단계: GICS 섹터 매니저 초기화 중...")
        sector_manager = GICSSectorManager()
        print("✅ GICS 섹터 매니저 초기화 완료!")

        # 3. 섹터팀 팩토리 생성
        print("\n🏗️ 3단계: 섹터팀 팩토리 생성 중...")
        factory = SectorTeamFactory(sector_manager)
        print("✅ 섹터팀 팩토리 생성 완료!")

        # 4. 테스트용 섹터 선택 (IT 섹터)
        print("\n💻 4단계: 테스트 섹터 선택 (IT 섹터)...")
        test_sector = GICSSector.INFORMATION_TECHNOLOGY
        print(f"✅ 테스트 섹터 선택 완료: {test_sector.value}")

        # 5. 섹터팀 생성
        print("\n👥 5단계: 섹터팀 생성 중...")
        sector_team = factory.create_sector_team(test_sector)
        print("✅ 섹터팀 생성 완료!")

        # 6. 밸류에이션 전문가 찾기
        print("\n🔍 6단계: 밸류에이션 전문가 찾는 중...")
        valuation_expert = None
        for expert in sector_team.experts:
            if "밸류에이션" in expert.name:
                valuation_expert = expert
                break

        if not valuation_expert:
            print("❌ 밸류에이션 전문가를 찾을 수 없습니다!")
            return False

        print(f"✅ 밸류에이션 전문가 발견: {valuation_expert.name}")

        # 7. LangChain 활성화 상태 확인
        print("\n🔧 7단계: LangChain 활성화 상태 확인...")
        print(f"   - LangChain 활성화: {valuation_expert.langchain_enabled}")
        print(
            f"   - LangChain Chain 존재: {valuation_expert.langchain_chain is not None}"
        )
        print(f"   - Memory 시스템 존재: {valuation_expert.memory_system is not None}")

        if not valuation_expert.langchain_enabled:
            print("❌ LangChain이 활성화되지 않았습니다!")
            return False

        print("✅ LangChain 활성화 상태 확인 완료!")

        # 8. 테스트 데이터 준비
        print("\n📊 8단계: 테스트 데이터 준비 중...")
        test_financial_data = {
            "company_name": "삼성전자",
            "ticker": "005930.KS",
            "current_price": 75000,
            "financial_metrics": {
                "revenue_2023": 2589400,  # 258조 9400억원
                "net_income_2023": 150000,  # 15조원
                "total_assets_2023": 4268000,  # 426조 8000억원
                "total_equity_2023": 3200000,  # 320조원
                "total_debt_2023": 1068000,  # 106조 8000억원
                "fcf_2023": 180000,  # 18조원
                "ebitda_2023": 250000,  # 25조원
                "shares_outstanding": 5969783,  # 발행주식수 (백만주)
                "interest_expense_2023": 15000,  # 1조 5000억원
                "tax_expense_2023": 45000,  # 4조 5000억원
                "pretax_income_2023": 195000,  # 19조 5000억원
            },
            "historical_data": {
                "per_2021": 12.5,
                "per_2022": 10.8,
                "per_2023": 11.2,
                "pbr_2021": 1.8,
                "pbr_2022": 1.5,
                "pbr_2023": 1.6,
                "ev_ebitda_2021": 8.2,
                "ev_ebitda_2022": 7.5,
                "ev_ebitda_2023": 7.8,
            },
            "market_data": {
                "risk_free_rate": 0.035,  # 3.5%
                "market_risk_premium": 0.06,  # 6%
                "beta": 1.2,
                "bond_yield": 0.04,  # 4%
            },
        }

        print("✅ 테스트 데이터 준비 완료!")

        # 9. LangChain 분석 실행 (5단계 전체)
        print("\n🧠 9단계: LangChain 5단계 전체 분석 실행 중...")
        start_time = datetime.now()

        # 분석 입력 데이터 준비
        analysis_input = {
            "financial_data": json.dumps(
                test_financial_data, ensure_ascii=False, indent=2
            ),
            "sector_name": "IT",
            "company_name": "삼성전자",
        }

        # 5단계 전체 분석 실행
        full_result = valuation_expert.run_full_valuation_analysis(analysis_input)

        end_time = datetime.now()
        analysis_duration = (end_time - start_time).total_seconds()

        print(f"✅ 5단계 전체 분석 완료! (소요시간: {analysis_duration:.2f}초)")

        # 10. 결과 검증
        print("\n📋 10단계: 결과 검증 중...")

        # 단계별 결과 구조 확인
        required_keys = [
            "step1_result",
            "step2_result",
            "step3_result",
            "step4_result",
            "step5_result",
        ]
        for key in required_keys:
            if key not in full_result:
                print(f"❌ 필수 단계 결과 누락: {key}")
                return False
        print("✅ 단계별 결과 구조 검증 완료!")

        # 11. 각 단계별 결과 출력
        print("\n📄 11단계: 5단계 분석 결과 출력...")
        print("=" * 60)
        for i in range(1, 6):
            step_key = f"step{i}_result"
            print(f"\n--- [Step {i} 결과] ---")
            result = full_result.get(step_key)
            if hasattr(result, "content"):
                print(result.content)
            elif isinstance(result, str):
                print(result)
            else:
                print(json.dumps(result, ensure_ascii=False, indent=2))
        print("\n" + "=" * 60)
        print("🎉 5단계 밸류에이션 분석 전체 성공!")
        print("=" * 60)
        print(f"✅ 테스트 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"✅ 총 소요 시간: {analysis_duration:.2f}초")
        print(f"✅ 분석가: {valuation_expert.name}")
        print(f"✅ 섹터: {test_sector.value}")
        return True

    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """메인 실행 함수"""
    print("🚀 밸류에이션 전문가 LangChain Chain 테스트 시작!")
    print("=" * 60)

    success = test_valuation_langchain()

    if success:
        print("\n🎯 Day 2 1단계 완료: 밸류에이션 전문가 LangChain 적용 성공!")
        print("다음 단계로 진행할 준비가 되었습니다.")
    else:
        print("\n❌ Day 2 1단계 실패: 밸류에이션 전문가 LangChain 적용 실패!")
        print("문제를 해결한 후 다시 시도해주세요.")


if __name__ == "__main__":
    main()
