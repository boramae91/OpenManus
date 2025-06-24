#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
수정된 DART API ZIP 파일 처리 테스트
ZIP 압축 파일을 올바르게 처리하는지 확인합니다
"""

import asyncio
import json
import os
from datetime import datetime

from app.data_collector.enhanced_financial_data_collector import (
    EnhancedDartDataCollector,
)


async def test_dart_zip_processing():
    """수정된 ZIP 파일 처리 테스트"""
    print("🚀 DART API ZIP 파일 처리 테스트")
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

        # 삼성전자 사업보고서/분기보고서 딕셔너리 생성 테스트
        print("\n📊 삼성전자 사업보고서/분기보고서 딕셔너리 생성 테스트...")

        result = await collector.get_business_reports_with_dictionary(
            corp_code="00126380", company_name="삼성전자", bsns_year="2024"  # 삼성전자
        )

        print(f"\n🎯 딕셔너리 생성 결과:")
        print(f"   - 성공 여부: {result.get('success')}")

        if result.get("success"):
            # 사업보고서 딕셔너리 확인
            business_dict = result.get("business_report_dictionary", {})
            quarterly_dict = result.get("quarterly_report_dictionary", {})

            print(f"   - 사업보고서 섹션: {len(business_dict)}개")
            print(f"   - 분기보고서 섹션: {len(quarterly_dict)}개")

            # 첫 번째 섹션 미리보기
            if business_dict:
                print(f"\n📄 사업보고서 첫 번째 섹션:")
                first_key = list(business_dict.keys())[0]
                first_content = business_dict[first_key]
                print(f"   - 섹션명: {first_key}")
                print(f"   - 내용 길이: {len(first_content):,}자")
                print(f"   - 내용 미리보기: {first_content[:300]}...")

            if quarterly_dict:
                print(f"\n📈 분기보고서 첫 번째 섹션:")
                first_key = list(quarterly_dict.keys())[0]
                first_content = quarterly_dict[first_key]
                print(f"   - 섹션명: {first_key}")
                print(f"   - 내용 길이: {len(first_content):,}자")
                print(f"   - 내용 미리보기: {first_content[:300]}...")

            # PDF 딕셔너리 인터페이스 확인
            pdf_interface = result.get("pdf_dictionary_interface")
            if pdf_interface:
                print(f"\n🔗 PDF 딕셔너리 인터페이스:")
                print(f"   - 전체 섹션: {len(pdf_interface.get_all_sections())}개")

                # 전문가별 섹션 확인
                financial_sections = pdf_interface.get_sections_by_expert_type(
                    "financial"
                )
                print(f"   - 재무 전문가용 섹션: {len(financial_sections)}개")

            # 메타데이터 확인
            metadata = result.get("metadata", {})
            if metadata:
                print(f"\n📊 처리 메타데이터:")
                print(f"   - 회사명: {metadata.get('company_name')}")
                print(f"   - 사업연도: {metadata.get('bsns_year')}")
                print(f"   - 수집시간: {metadata.get('collected_at')}")

            return True
        else:
            print(f"   - 오류: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ 테스트 중 예외 발생: {e}")
        return False


async def test_document_download_directly():
    """문서 다운로드만 따로 테스트"""
    print("\n🔍 직접 문서 다운로드 테스트")
    print("-" * 40)

    dart_key = os.getenv("DART_API_KEY")
    if not dart_key:
        print("❌ DART API 키가 없습니다")
        return False

    collector = EnhancedDartDataCollector(dart_key)

    # 삼성전자 2024년 사업보고서 접수번호로 직접 다운로드 테스트
    test_rcept_no = "20250311001085"  # 로그에서 확인된 삼성전자 2024년 사업보고서

    print(f"📥 보고서 다운로드 테스트: {test_rcept_no}")

    try:
        content = await collector._download_document_content(test_rcept_no)

        if content:
            print(f"✅ 문서 다운로드 성공!")
            print(f"   - 내용 길이: {len(content):,}자")
            print(f"   - 내용 미리보기: {content[:200]}...")

            # 텍스트 기반 딕셔너리 생성 테스트
            print(f"\n🧩 텍스트 기반 딕셔너리 생성 테스트...")
            dict_result = await collector._create_text_based_dictionary(
                text_content=content, company_name="삼성전자", max_section_size=1000000
            )

            if dict_result.get("success"):
                sections = dict_result.get("pdf_dictionary", {})
                print(f"✅ 딕셔너리 생성 성공: {len(sections)}개 섹션")

                # 섹션 목록 출력
                for i, (key, value) in enumerate(sections.items()):
                    if i < 5:  # 처음 5개만
                        print(f"   {i+1}. {key}: {len(value):,}자")
                if len(sections) > 5:
                    print(f"   ... 외 {len(sections) - 5}개 섹션")

                return True
            else:
                print(f"❌ 딕셔너리 생성 실패: {dict_result.get('error')}")
                return False
        else:
            print("❌ 문서 다운로드 실패")
            return False

    except Exception as e:
        print(f"❌ 다운로드 테스트 중 오류: {e}")
        return False


async def main():
    """메인 테스트 함수"""
    print("🎯 DART API ZIP 파일 처리 종합 테스트")
    print("=" * 60)

    # 1단계: 직접 문서 다운로드 테스트
    success1 = await test_document_download_directly()

    # 2단계: 전체 딕셔너리 생성 테스트
    success2 = await test_dart_zip_processing()

    # 결과 요약
    print("\n" + "=" * 60)
    print("🎯 테스트 결과 요약")
    print("=" * 60)
    print(f"문서 다운로드: {'✅ 성공' if success1 else '❌ 실패'}")
    print(f"딕셔너리 생성: {'✅ 성공' if success2 else '❌ 실패'}")

    if success1 and success2:
        print("\n🎉 모든 테스트가 성공했습니다!")
        print("💡 DART API ZIP 파일 처리가 정상적으로 작동합니다.")
    else:
        print("\n🚨 일부 테스트가 실패했습니다.")
        if not success1:
            print("   - 문서 다운로드 및 ZIP 처리 확인 필요")
        if not success2:
            print("   - 전체 딕셔너리 생성 프로세스 확인 필요")


if __name__ == "__main__":
    asyncio.run(main())
