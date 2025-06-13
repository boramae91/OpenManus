#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 enhanced_main.py 실제 실행 테스트

실제로 enhanced_main.py를 실행했을 때 meta 데이터가 어떻게 전달되는지 확인하는 스크립트입니다.
"""

import asyncio
import os
import sys

# 프로젝트 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_main import EnhancedStockAnalysisSystem


async def test_enhanced_main():
    """enhanced_main.py 실제 실행 테스트"""
    print("🧪 enhanced_main.py 실제 실행 테스트")
    print("=" * 60)

    try:
        # 시스템 초기화
        system = EnhancedStockAnalysisSystem()

        # 실제 사용자 프롬프트 테스트
        user_prompt = "삼성전자 주식 분석해줘"

        print(f"📝 사용자 프롬프트: {user_prompt}")
        print("-" * 40)

        # Step 1: 종목 감지 테스트
        print("📊 Step 1: 종목 감지...")
        stock_info = await system.extract_stock_info(user_prompt)
        print(f"종목 감지 결과: {stock_info}")

        # enhanced_main.py의 save_enhanced_results에서 하는 것과 같은 처리
        print("\n🏢 ticker_bbg 매핑 처리...")
        original_stock_code = stock_info.get("stock_code")
        original_stock_name = stock_info.get("stock_name")

        ticker_bbg = system.get_ticker_bbg_from_name(
            stock_name=original_stock_name, stock_code=original_stock_code
        )

        # stock_info 업데이트
        updated_stock_info = stock_info.copy()
        updated_stock_info["ticker_bbg"] = ticker_bbg
        updated_stock_info["original_stock_code"] = original_stock_code
        updated_stock_info["original_stock_name"] = original_stock_name

        if ticker_bbg != (original_stock_code or original_stock_name):
            print(
                f"📊 파일명 종목코드 변환: {original_stock_code or original_stock_name} -> {ticker_bbg}"
            )
            updated_stock_info["stock_code"] = ticker_bbg  # 파일명 생성용으로 교체

        print(f"업데이트된 stock_info: {updated_stock_info}")

        # meta_data 구성
        print("\n📋 meta_data 구성...")
        meta_data = {
            "analysis_flow": "enhanced",
            "success": True,
            "timestamp": "20250613_110000",
            "stock_info": updated_stock_info,  # 🏢 ticker_bbg가 포함된 업데이트된 정보 사용
            "enhanced_features": {
                "ticker_bbg_mapping_used": True,
            },
        }

        print(f"meta_data['stock_info']: {meta_data['stock_info']}")

        # io_logger.py에서 확인하는 조건들 테스트
        print("\n🔍 io_logger.py 조건 확인...")

        # 조건 1: meta and "stock_info" in meta
        has_meta = bool(meta_data)
        has_stock_info = "stock_info" in meta_data
        print(f"meta 존재: {has_meta}")
        print(f"stock_info 키 존재: {has_stock_info}")

        if has_meta and has_stock_info:
            stock_info_meta = meta_data["stock_info"]
            print(f"stock_info_meta: {stock_info_meta}")

            # 조건 2: stock_info_meta and stock_info_meta.get("found")
            has_stock_info_meta = bool(stock_info_meta)
            has_found = stock_info_meta.get("found") if stock_info_meta else False
            print(f"stock_info_meta 존재: {has_stock_info_meta}")
            print(f"found 값: {has_found}")

            if has_stock_info_meta and has_found:
                # 조건 3: ticker_bbg 추출
                ticker_bbg_from_meta = stock_info_meta.get("ticker_bbg")
                stock_code_from_meta = stock_info_meta.get(
                    "stock_code"
                ) or stock_info_meta.get("ticker")

                print(f"ticker_bbg: {ticker_bbg_from_meta}")
                print(f"stock_code: {stock_code_from_meta}")

                if ticker_bbg_from_meta:
                    stock_identifier = ticker_bbg_from_meta.replace(" ", "").replace(
                        "/", ""
                    )
                    print(f"🎯 최종 파일명 식별자: {stock_identifier}")
                elif stock_code_from_meta:
                    stock_identifier = stock_code_from_meta
                    print(f"🎯 최종 파일명 식별자 (fallback): {stock_identifier}")
                else:
                    stock_identifier = stock_info_meta.get("stock_name")
                    print(f"🎯 최종 파일명 식별자 (name fallback): {stock_identifier}")
            else:
                print("❌ found 조건 실패!")
        else:
            print("❌ meta 조건 실패!")

        print("\n" + "=" * 60)
        print("🧪 테스트 완료!")

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_enhanced_main())
