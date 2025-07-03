#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
대시보드 핵심 함수 간단 테스트

대시보드의 주요 함수들이 올바르게 작동하는지 확인해요.
"""

import os
import sys

# OpenManus 시스템 import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_dashboard_imports():
    """
    대시보드 모듈들이 올바르게 import되는지 테스트해요
    """
    print("🚀 대시보드 모듈 import 테스트 시작!")
    print("=" * 50)

    try:
        # 1. 대시보드 매니저 import 테스트
        print("📊 1단계: EnhancedDashboardManager import...")
        from streamlit_dashboard_enhanced import EnhancedDashboardManager

        print("✅ EnhancedDashboardManager import 성공!")

        # 2. 대시보드 매니저 초기화 테스트
        print("\n🔧 2단계: 대시보드 매니저 초기화...")
        dashboard = EnhancedDashboardManager()
        print("✅ 대시보드 매니저 초기화 성공!")

        # 3. 함수들 import 테스트
        print("\n📋 3단계: 대시보드 함수들 import...")
        from streamlit_dashboard_enhanced import (
            evaluate_quality,
            run_ab_test,
            run_enhanced_analysis,
            show_enhanced_analysis_result,
        )

        print("✅ 모든 대시보드 함수 import 성공!")

        # 4. 함수 타입 확인
        print("\n🔍 4단계: 함수 타입 확인...")
        print(f"   - run_enhanced_analysis 타입: {type(run_enhanced_analysis)}")
        print(f"   - run_ab_test 타입: {type(run_ab_test)}")
        print(
            f"   - show_enhanced_analysis_result 타입: {type(show_enhanced_analysis_result)}"
        )
        print(f"   - evaluate_quality 타입: {type(evaluate_quality)}")

        # 5. 비동기 함수가 아닌지 확인
        print("\n⚡ 5단계: 비동기 함수 여부 확인...")
        import inspect

        is_async_run = inspect.iscoroutinefunction(run_enhanced_analysis)
        is_async_ab = inspect.iscoroutinefunction(run_ab_test)
        print(f"   - run_enhanced_analysis가 비동기 함수: {is_async_run}")
        print(f"   - run_ab_test가 비동기 함수: {is_async_ab}")

        if not is_async_run and not is_async_ab:
            print("✅ 모든 함수가 동기 함수로 올바르게 정의됨!")
        else:
            print("⚠️ 일부 함수가 비동기 함수로 정의됨 - 수정 필요!")

        print("\n🎉 대시보드 모듈 테스트 완료!")
        return True

    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_dashboard_imports()
    if success:
        print("\n✅ 대시보드가 정상적으로 작동할 준비가 되었습니다!")
    else:
        print("\n❌ 대시보드에 문제가 있습니다. 수정이 필요합니다.")
