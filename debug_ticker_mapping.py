#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🐛 ticker_bbg 매핑 디버깅 스크립트

현재 ticker_bbg 매핑이 제대로 작동하지 않는 이유를 찾아보는 테스트 코드입니다.
"""

import os
import sys
import traceback

# 프로젝트 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_main import EnhancedStockAnalysisSystem


def debug_ticker_mapping():
    """ticker_bbg 매핑 디버깅"""
    print("🐛 ticker_bbg 매핑 디버깅 시작")
    print("=" * 60)

    try:
        # 시스템 초기화
        system = EnhancedStockAnalysisSystem()

        # 테스트 케이스들
        test_cases = [
            {"stock_name": "삼성전자", "stock_code": "005930"},
            {"stock_name": "네이버", "stock_code": "035420"},
            {"stock_name": "현대자동차", "stock_code": "005380"},
            {"stock_name": "APPLE", "stock_code": None},
            {"stock_name": "Microsoft", "stock_code": None},
            {"stock_name": "Tesla", "stock_code": None},
        ]

        print("📊 데이터셋 로딩 테스트...")
        try:
            mapping_tables = system._load_stock_mapping_tables()
            print(f"✅ 로딩된 데이터셋 개수: {len(mapping_tables)}")
            for name, df in mapping_tables.items():
                print(f"  - {name}: {len(df)} 종목")
        except Exception as e:
            print(f"❌ 데이터셋 로딩 실패: {e}")
            traceback.print_exc()
            return

        print("\n🔍 ticker_bbg 매핑 테스트...")
        for i, case in enumerate(test_cases, 1):
            stock_name = case["stock_name"]
            stock_code = case["stock_code"]

            print(f"\n[{i}] {stock_name} ({stock_code or 'No Code'})")
            print("-" * 30)

            try:
                ticker_bbg = system.get_ticker_bbg_from_name(
                    stock_name=stock_name, stock_code=stock_code
                )

                print(f"  📄 원본 종목명: {stock_name}")
                print(f"  📄 원본 종목코드: {stock_code or 'None'}")
                print(f"  🏷️ 매핑 결과: {ticker_bbg}")

                # 파일명에서 어떻게 보일지 미리보기
                file_friendly = ticker_bbg.replace(" ", "").replace("/", "")
                print(f"  📁 파일명 적용: {file_friendly}")

                # 매핑이 성공했는지 확인
                if ticker_bbg != (stock_code or stock_name):
                    print("  ✅ 매핑 성공!")
                else:
                    print("  ⚠️ 매핑 실패 (원본과 동일)")

            except Exception as e:
                print(f"  ❌ 매핑 에러: {e}")
                traceback.print_exc()

        print("\n" + "=" * 60)
        print("🐛 디버깅 완료!")

        # stock_info 업데이트 시뮬레이션
        print("\n📋 stock_info 업데이트 시뮬레이션...")
        test_stock_info = {
            "stock_name": "삼성전자",
            "stock_code": "005930",
            "detected": True,
            "found": True,
        }

        print(f"원본 stock_info: {test_stock_info}")

        # save_enhanced_results에서 하는 것과 같은 처리
        original_stock_code = test_stock_info.get("stock_code")
        original_stock_name = test_stock_info.get("stock_name")

        ticker_bbg = system.get_ticker_bbg_from_name(
            stock_name=original_stock_name, stock_code=original_stock_code
        )

        updated_stock_info = test_stock_info.copy()
        updated_stock_info["ticker_bbg"] = ticker_bbg
        updated_stock_info["original_stock_code"] = original_stock_code
        updated_stock_info["original_stock_name"] = original_stock_name

        if ticker_bbg != (original_stock_code or original_stock_name):
            print(
                f"📊 파일명 종목코드 변환: {original_stock_code or original_stock_name} -> {ticker_bbg}"
            )
            updated_stock_info["stock_code"] = ticker_bbg  # 파일명 생성용으로 교체

        print(f"업데이트된 stock_info: {updated_stock_info}")

    except Exception as e:
        print(f"❌ 전체 테스트 실패: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    debug_ticker_mapping()
