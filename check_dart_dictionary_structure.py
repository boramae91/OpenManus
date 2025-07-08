#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DART API 딕셔너리 구조 확인 스크립트
실제 딕셔너리의 Key와 Value 구조를 정확히 확인합니다.
"""

import asyncio
import json
import os
from datetime import datetime

from app.data_collector.enhanced_financial_data_collector import (
    EnhancedDartDataCollector,
)


async def check_dart_dictionary_structure():
    """DART 딕셔너리 구조 확인"""
    print("🔍 DART API 딕셔너리 구조 확인")
    print("=" * 60)

    # DART API 키 확인
    dart_key = os.getenv("DART_API_KEY")
    if not dart_key:
        print("❌ DART_API_KEY 환경변수가 설정되지 않았습니다!")
        return False

    print(f"✅ DART API 키 설정됨: {dart_key[:10]}...")

    try:
        # Enhanced DART 데이터 수집기 초기화
        collector = EnhancedDartDataCollector(dart_key)
        print("✅ Enhanced DART 데이터 수집기 초기화 완료")

        # 삼성전자 사업보고서/분기보고서 딕셔너리 생성
        print("\n📊 삼성전자 사업보고서/분기보고서 딕셔너리 생성...")

        result = await collector.get_business_reports_with_dictionary(
            corp_code="00126380", company_name="삼성전자", bsns_year="2024"
        )

        print(f"\n🎯 딕셔너리 생성 결과:")
        print(f"   - 성공 여부: {result.get('success')}")

        if result.get("success"):
            # 1. 최상위 딕셔너리 구조 확인
            print(f"\n📋 1. 최상위 딕셔너리 구조:")
            print(f"   - 전체 키 개수: {len(result)}개")
            print(f"   - 키 목록: {list(result.keys())}")

            # 2. 사업보고서 딕셔너리 구조 확인
            business_dict = result.get("business_report_dictionary", {})
            print(f"\n📄 2. 사업보고서 딕셔너리 구조:")
            print(f"   - 섹션 개수: {len(business_dict)}개")
            print(f"   - 섹션 키 목록: {list(business_dict.keys())}")

            # 3. 첫 번째 섹션의 Value 타입 확인
            if business_dict:
                first_key = list(business_dict.keys())[0]
                first_value = business_dict[first_key]
                print(f"\n🔍 3. 첫 번째 섹션 상세 분석:")
                print(f"   - 섹션명: {first_key}")
                print(f"   - Value 타입: {type(first_value)}")
                print(f"   - Value 길이: {len(str(first_value))}자")

                if isinstance(first_value, dict):
                    print(f"   - Value는 딕셔너리입니다!")
                    print(f"   - 딕셔너리 키: {list(first_value.keys())}")
                    print(
                        f"   - 딕셔너리 내용: {json.dumps(first_value, indent=4, ensure_ascii=False)[:500]}..."
                    )
                else:
                    print(f"   - Value는 문자열입니다!")
                    print(f"   - 내용 미리보기: {str(first_value)[:300]}...")

            # 4. 분기보고서 딕셔너리 구조 확인
            quarterly_dict = result.get("quarterly_report_dictionary", {})
            print(f"\n📈 4. 분기보고서 딕셔너리 구조:")
            print(f"   - 섹션 개수: {len(quarterly_dict)}개")
            print(f"   - 섹션 키 목록: {list(quarterly_dict.keys())}")

            # 5. 첫 번째 분기보고서 섹션의 Value 타입 확인
            if quarterly_dict:
                first_key = list(quarterly_dict.keys())[0]
                first_value = quarterly_dict[first_key]
                print(f"\n🔍 5. 첫 번째 분기보고서 섹션 상세 분석:")
                print(f"   - 섹션명: {first_key}")
                print(f"   - Value 타입: {type(first_value)}")
                print(f"   - Value 길이: {len(str(first_value))}자")

                if isinstance(first_value, dict):
                    print(f"   - Value는 딕셔너리입니다!")
                    print(f"   - 딕셔너리 키: {list(first_value.keys())}")
                    print(
                        f"   - 딕셔너리 내용: {json.dumps(first_value, indent=4, ensure_ascii=False)[:500]}..."
                    )
                else:
                    print(f"   - Value는 문자열입니다!")
                    print(f"   - 내용 미리보기: {str(first_value)[:300]}...")

            # 6. 전체 구조 요약
            print(f"\n📊 6. 전체 구조 요약:")
            print(f"   - 사업보고서 Value 타입: {type(business_dict)}")
            print(f"   - 분기보고서 Value 타입: {type(quarterly_dict)}")

            # 7. 실제 파일로 저장하여 확인
            output_file = f"dart_dictionary_structure_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                # 딕셔너리 구조만 저장 (전체 내용은 너무 큼)
                structure_info = {
                    "success": result.get("success"),
                    "business_report_sections": (
                        list(business_dict.keys()) if business_dict else []
                    ),
                    "quarterly_report_sections": (
                        list(quarterly_dict.keys()) if quarterly_dict else []
                    ),
                    "business_report_sample": {
                        k: (
                            f"[{len(v)}자 텍스트]"
                            if isinstance(v, str)
                            else f"[{type(v).__name__}]"
                        )
                        for k, v in list(business_dict.items())[:3]  # 처음 3개만
                    },
                    "quarterly_report_sample": {
                        k: (
                            f"[{len(v)}자 텍스트]"
                            if isinstance(v, str)
                            else f"[{type(v).__name__}]"
                        )
                        for k, v in list(quarterly_dict.items())[:3]  # 처음 3개만
                    },
                }
                json.dump(structure_info, f, indent=2, ensure_ascii=False)

            print(f"   - 구조 정보 저장됨: {output_file}")

            return True
        else:
            print(f"❌ 딕셔너리 생성 실패: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False


async def main():
    """메인 함수"""
    success = await check_dart_dictionary_structure()

    if success:
        print("\n🎉 딕셔너리 구조 확인 완료!")
    else:
        print("\n❌ 딕셔너리 구조 확인 실패!")


if __name__ == "__main__":
    asyncio.run(main())
