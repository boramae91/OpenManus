#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 분석 테스트 스크립트

대시보드 없이 직접 분석을 실행해서 실제로 잘 작동하는지 확인해요.
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# OpenManus 시스템 import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.tool.expert_analysis_integration import ExpertAnalysisIntegration
from enhanced_main import EnhancedStockAnalysisSystem


async def simple_test():
    """
    간단한 분석 테스트
    """
    print("🚀 간단한 분석 테스트 시작!")
    print("=" * 50)

    try:
        # 1. 기본 분석 시스템 초기화
        print("📊 1단계: 분석 시스템 초기화...")
        analysis_system = EnhancedStockAnalysisSystem()
        print("✅ 분석 시스템 초기화 완료!")

        # 2. 기본 분석 실행
        print("\n🔍 2단계: 삼성전자 기본 분석 실행...")
        user_input = "삼성전자의 재무 상황과 투자 가치를 분석해주세요"

        result = await analysis_system.run_enhanced_analysis(user_input)

        if result and result.get("success"):
            print("✅ 기본 분석 성공!")
            print(f"   분석 시간: {result.get('total_analysis_time', 'N/A')}")
            print(
                f"   데이터 품질: {result.get('data_integration_quality', {}).get('quality_grade', 'N/A')}"
            )

            # 비용 절감 효과
            cost_savings = result.get("cost_savings", {})
            if cost_savings:
                print(f"   비용 절감: {cost_savings.get('savings_percentage', 0):.1f}%")
                print(f"   절약 금액: ${cost_savings.get('savings_amount', 0):.2f}")
        else:
            print("❌ 기본 분석 실패!")
            return

        # 3. 전문가 통합 분석 실행
        print("\n🎯 3단계: 전문가 통합 분석 실행...")
        expert_integration = ExpertAnalysisIntegration()

        # 분석 데이터 준비
        analysis_data = {
            "financial_data": result.get("financial_data", {}),
            "market_data": result.get("market_data", {}),
            "company_data": result.get("company_data", {}),
            "industry_data": result.get("industry_data", {}),
            "operation_data": result.get("operation_data", {}),
            "footnotes": result.get("footnotes", []),
            "timestamp": datetime.now().isoformat(),
        }

        expert_result = await expert_integration.perform_comprehensive_analysis(
            analysis_data
        )

        if expert_result and expert_result.get("success"):
            print("✅ 전문가 통합 분석 성공!")
            print(
                f"   활성화된 전문가: {len(expert_result.get('expert_analyses', {}))}명"
            )

            # 위험 신호 확인
            risk_signals = []
            for expert_type, analysis in expert_result.get(
                "expert_analyses", {}
            ).items():
                if "risk" in expert_type.lower():
                    risks = (
                        analysis.get("extra_risks")
                        or analysis.get("risks")
                        or analysis.get("risk_signals")
                    )
                    if risks:
                        risk_signals.extend(risks)

            if risk_signals:
                print(f"   ⚠️ 감지된 위험 신호: {len(risk_signals)}개")
                for signal in risk_signals[:3]:  # 상위 3개만 표시
                    print(f"      - {signal}")

            # 종합 추천
            recommendations = expert_result.get("integrated_recommendations", [])
            if recommendations:
                print(f"   💡 종합 추천: {len(recommendations)}개")
                for rec in recommendations[:2]:  # 상위 2개만 표시
                    print(f"      - {rec}")
        else:
            print("❌ 전문가 통합 분석 실패!")
            return

        # 4. 결과 저장
        print("\n💾 4단계: 결과 저장...")
        output_file = (
            f"simple_test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        final_result = {
            "success": True,
            "basic_analysis": result,
            "expert_analysis": expert_result,
            "timestamp": datetime.now().isoformat(),
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(final_result, f, ensure_ascii=False, indent=2, default=str)

        print(f"✅ 결과 저장 완료: {output_file}")

        # 5. 요약 출력
        print("\n🎉 테스트 완료!")
        print("=" * 50)
        print("📊 분석 결과 요약:")
        print(f"   기업명: 삼성전자 (005930)")
        print(f"   기본 분석: 성공")
        print(f"   전문가 분석: 성공")
        print(f"   위험 신호: {len(risk_signals)}개")
        print(f"   종합 추천: {len(recommendations)}개")
        print(f"   결과 파일: {output_file}")

        return final_result

    except Exception as e:
        print(f"❌ 테스트 실패: {str(e)}")
        import traceback

        print(traceback.format_exc())
        return None


def main():
    """
    메인 실행 함수
    """
    print("🎯 OpenManus 간단한 분석 테스트")
    print("대시보드 없이 직접 분석을 실행해서 실제로 잘 작동하는지 확인해볼게요!")

    # 비동기 실행
    result = asyncio.run(simple_test())

    if result:
        print("\n✅ 모든 테스트가 성공적으로 완료되었습니다!")
    else:
        print("\n❌ 테스트 중 오류가 발생했습니다.")


if __name__ == "__main__":
    main()
