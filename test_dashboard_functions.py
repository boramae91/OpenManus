#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
대시보드 비동기 함수 호출 테스트 스크립트

대시보드의 각 함수가 올바르게 작동하는지 확인해요.
"""

import asyncio
import os
import sys
from datetime import datetime

# OpenManus 시스템 import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 대시보드 함수들 import
from streamlit_dashboard_enhanced import (
    EnhancedDashboardManager,
    evaluate_quality,
    run_ab_test,
    run_enhanced_analysis,
    show_enhanced_analysis_result,
)


def test_dashboard_functions():
    """
    대시보드 함수들을 테스트해요
    """
    print("🚀 대시보드 함수 테스트 시작!")
    print("=" * 50)

    try:
        # 1. 대시보드 매니저 초기화 테스트
        print("📊 1단계: 대시보드 매니저 초기화...")
        dashboard = EnhancedDashboardManager()
        print("✅ 대시보드 매니저 초기화 완료!")

        # 2. 시스템 로드 테스트
        print("\n🔧 2단계: 시스템 로드 테스트...")
        load_success = dashboard.load_systems()
        if load_success:
            print("✅ 시스템 로드 성공!")
        else:
            print("❌ 시스템 로드 실패!")
            return

        # 3. 간단한 분석 실행 테스트
        print("\n🔍 3단계: 간단한 분석 실행 테스트...")
        user_input = "삼성전자"
        options = {"analysis_depth": "기본", "include_pdf": False}

        print("   - 분석 실행 중...")
        result = run_enhanced_analysis(user_input, options)

        if result:
            print("✅ 분석 실행 성공!")
            print(f"   - 결과 타입: {type(result)}")
            print(f"   - 성공 여부: {result.get('success', False)}")

            # 4. 결과 구조 확인
            print("\n📋 4단계: 결과 구조 확인...")
            if isinstance(result, dict):
                print("✅ 결과가 딕셔너리 형태입니다!")
                print(
                    f"   - 기본 분석: {'있음' if 'basic_analysis' in result else '없음'}"
                )
                print(
                    f"   - 전문가 분석: {'있음' if 'expert_analysis' in result else '없음'}"
                )
                print(f"   - 타임스탬프: {'있음' if 'timestamp' in result else '없음'}")
            else:
                print(f"❌ 결과가 딕셔너리가 아닙니다: {type(result)}")

            # 5. 품질 평가 테스트
            print("\n⭐ 5단계: 품질 평가 테스트...")
            quality_score = evaluate_quality(result)
            print(f"   - 품질 점수: {quality_score}점")

        else:
            print("❌ 분석 실행 실패!")
            return

        # 6. A/B 테스트 실행 테스트 (간단 버전)
        print("\n🆚 6단계: A/B 테스트 실행 테스트...")
        try:
            ab_results = run_ab_test(user_input, options)
            if ab_results:
                print("✅ A/B 테스트 실행 성공!")
                print(f"   - A안 점수: {ab_results['A']['score']}점")
                print(f"   - B안 점수: {ab_results['B']['score']}점")
            else:
                print("❌ A/B 테스트 실행 실패!")
        except Exception as e:
            print(f"❌ A/B 테스트 실행 중 오류: {str(e)}")

        print("\n🎉 모든 테스트 완료!")

    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_dashboard_functions()
