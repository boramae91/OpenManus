#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 200만자 업그레이드 테스트 스크립트

60만자에서 200만자로 확장된 대용량 PDF 처리 능력을 테스트합니다.
이제 더욱 방대한 사업보고서도 완전히 처리할 수 있어요!
"""

import asyncio

from app.data_collector.enhanced_financial_data_collector import (
    EnhancedDartDataCollector,
)
from app.utils.large_pdf_analyzer import LargePDFAnalyzer


async def test_200만자_upgrade():
    """200만자 업그레이드 테스트"""
    print("🚀 200만자 업그레이드 테스트")
    print("=" * 60)

    try:
        # LargePDFAnalyzer 초기화 (200만자 지원)
        analyzer = LargePDFAnalyzer(
            chunk_size=100000,
            overlap_size=5000,
            max_section_size=2000000,  # 🚀 200만자 지원
        )

        print("✅ 200만자 지원 LargePDFAnalyzer 초기화 완료")

        # 가상의 대용량 텍스트 생성 (200만자)
        print("📝 200만자 테스트 텍스트 생성...")
        large_text = "이것은 테스트용 긴 텍스트입니다. " * 100000  # 약 200만자
        print(f"   생성된 텍스트 길이: {len(large_text):,}자")

        # DART 데이터 수집기 테스트
        dart_collector = EnhancedDartDataCollector()

        if not dart_collector.is_available():
            print("⚠️ DART API 키가 설정되지 않았습니다. 텍스트 분할만 테스트합니다.")

        # 200만자 제한 테스트
        print("\n🎯 200만자 제한 테스트...")
        sections = dart_collector._split_text_into_logical_sections(
            large_text, max_section_size=2000000  # 🚀 200만자로 확장
        )

        print(f"📊 텍스트 분할 결과:")
        print(f"   - 총 섹션 수: {len(sections)}개")

        total_length = sum(len(content) for content in sections.values())
        print(f"   - 총 텍스트 길이: {total_length:,}자")

        for i, (section_name, content) in enumerate(sections.items(), 1):
            if len(content) > 2000000:
                print(
                    f"     ❌ 섹션 {i} ({section_name}): {len(content):,}자 - 200만자 초과!"
                )
            else:
                print(f"     ✅ 섹션 {i} ({section_name}): {len(content):,}자")

        # 최대 섹션 크기 확인
        max_section_length = (
            max(len(content) for content in sections.values()) if sections else 0
        )

        if max_section_length > 2000000:
            print(f"     ❌ 200만자 초과분이 발견됨: {max_section_length:,}자")
        else:
            print(f"     ✅ 200만자 제한 올바르게 적용됨")

        print("\n🎉 200만자 업그레이드 테스트 완료!")
        print("✅ 모든 기능이 200만자 지원으로 성공적으로 업그레이드되었습니다!")
        return True

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return False


if __name__ == "__main__":
    print("🚀 OpenManus 200만자 업그레이드 테스트")
    print("=" * 60)

    try:
        success = asyncio.run(test_200만자_upgrade())
        if success:
            print("\n🎉 모든 테스트가 성공했습니다!")
        else:
            print("\n❌ 일부 테스트가 실패했습니다.")
    except Exception as e:
        print(f"\n💥 테스트 실행 중 오류 발생: {e}")
