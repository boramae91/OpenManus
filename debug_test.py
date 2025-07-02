#!/usr/bin/env python3
"""
디버깅을 위한 간단한 테스트 파일
"""

import os
import sys

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from integration_test_system import IntegrationTestSystem


def test_data_generation():
    """테스트 데이터 생성 함수를 테스트해요"""
    test_system = IntegrationTestSystem()

    # 각 전문가 역할별로 테스트 데이터 생성
    roles = [
        "펀더멘털 분석가",
        "기술적 분석가",
        "산업 전문가",
        "밸류에이션 전문가",
        "리스크 평가자",
        "재무제표 주석 전문가",
    ]

    print("🔍 테스트 데이터 생성 테스트")
    print("=" * 50)

    for role in roles:
        test_data = test_system._create_test_data_for_expert(role)
        print(f"\n📊 {role}:")
        print(f"   생성된 데이터: {test_data}")
        print(f"   키 목록: {list(test_data.keys())}")


if __name__ == "__main__":
    test_data_generation()
