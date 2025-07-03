#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실제 주식 분석 테스트 스크립트

지금까지 개발한 시스템들이 실제로 잘 작동하는지 확인하기 위한 실사용 테스트예요.
삼성전자와 SK하이닉스 두 기업을 분석해서 결과를 보여줄게요!
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# OpenManus 시스템 import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.tool.expert_analysis_integration import ExpertAnalysisIntegration
from app.utils.performance_monitor import get_performance_monitor
from enhanced_main import EnhancedStockAnalysisSystem


async def test_real_analysis():
    """
    실제 주식 분석을 실행하는 함수예요
    """
    print("🚀 실제 주식 분석 테스트 시작!")
    print("=" * 60)

    # 성능 모니터 초기화
    performance_monitor = get_performance_monitor()

    # 분석할 주식 목록
    test_stocks = [
        {"name": "삼성전자", "code": "005930", "description": "반도체 및 전자제품"},
        {"name": "SK하이닉스", "code": "000660", "description": "메모리 반도체"},
    ]

    for i, stock in enumerate(test_stocks, 1):
        print(f"\n📊 {i}번째 분석: {stock['name']} ({stock['code']})")
        print("-" * 40)

        # 성능 모니터링 시작
        analysis_id = (
            f"real_test_{stock['code']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        performance_monitor.start_monitoring(analysis_id)

        try:
            # 1. 기본 분석 시스템 테스트
            print("🔍 1단계: 기본 분석 시스템 실행...")
            analysis_system = EnhancedStockAnalysisSystem()

            # 사용자 입력 시뮬레이션
            user_input = f"{stock['name']}의 재무 상황과 투자 가치를 분석해주세요"

            # 분석 실행
            result = await analysis_system.analyze_stock(
                user_input=user_input,
                stock_name=stock["name"],
                stock_code=stock["code"],
            )

            print(
                f"✅ 기본 분석 완료! 소요시간: {result.get('total_analysis_time', 'N/A')}"
            )

            # 2. 전문가 통합 분석 테스트
            print("🎯 2단계: 전문가 통합 분석 실행...")
            expert_integration = ExpertAnalysisIntegration()

            # 전문가 분석 실행
            expert_result = await expert_integration.perform_comprehensive_analysis(
                result
            )

            print("✅ 전문가 통합 분석 완료!")

            # 3. 결과 요약 출력
            print("\n📋 분석 결과 요약:")
            print(f"   기업명: {stock['name']} ({stock['code']})")
            print(f"   분석 시간: {result.get('total_analysis_time', 'N/A')}")
            print(
                f"   데이터 품질: {result.get('data_integration_quality', {}).get('quality_grade', 'N/A')}"
            )

            # 비용 절감 효과
            cost_savings = result.get("cost_savings", {})
            if cost_savings:
                print(f"   비용 절감: {cost_savings.get('savings_percentage', 0):.1f}%")
                print(f"   절약 금액: ${cost_savings.get('savings_amount', 0):.2f}")

            # 전문가 분석 결과
            if expert_result.get("success"):
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

            # 4. 성능 모니터링 결과
            performance_metrics = performance_monitor.stop_monitoring()
            if performance_metrics:
                print(f"\n📊 성능 지표:")
                print(f"   총 소요시간: {performance_metrics.total_duration:.2f}초")
                print(f"   최대 메모리: {performance_metrics.peak_memory_mb:.1f}MB")
                print(f"   API 호출: {performance_metrics.api_calls}회")
                print(f"   성능 점수: {performance_metrics.performance_score:.1f}/100")

            # 5. 결과 저장
            output_file = f"real_test_result_{stock['code']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "stock_info": stock,
                        "basic_analysis": result,
                        "expert_analysis": expert_result,
                        "performance_metrics": (
                            performance_metrics.__dict__
                            if performance_metrics
                            else None
                        ),
                        "timestamp": datetime.now().isoformat(),
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                    default=str,
                )

            print(f"💾 결과 저장: {output_file}")

        except Exception as e:
            print(f"❌ 분석 실패: {str(e)}")
            import traceback

            print(traceback.format_exc())

            # 성능 모니터링 중지
            performance_monitor.stop_monitoring()

    print("\n🎉 실제 분석 테스트 완료!")
    print("=" * 60)

    # 전체 성능 리포트 생성
    print("\n📊 전체 성능 리포트:")
    performance_report = performance_monitor.get_performance_report()
    print(f"   총 분석 수: {performance_report.get('total_analyses', 0)}")
    print(f"   평균 소요시간: {performance_report.get('average_duration', 0):.2f}초")
    print(f"   평균 메모리: {performance_report.get('average_memory', 0):.1f}MB")
    print(f"   총 API 호출: {performance_report.get('total_api_calls', 0)}회")
    print(f"   총 비용: ${performance_report.get('total_cost', 0):.2f}")


def main():
    """
    메인 실행 함수
    """
    print("🎯 OpenManus 실제 분석 테스트")
    print("지금까지 개발한 시스템들이 실제로 잘 작동하는지 확인해볼게요!")

    # 비동기 실행
    asyncio.run(test_real_analysis())


if __name__ == "__main__":
    main()
