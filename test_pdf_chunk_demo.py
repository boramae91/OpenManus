#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 PDF 청크 단위 전문 분석 테스트 데모

OpenManus의 새로운 PDF 청크 처리 기능을 시연합니다.
"""

import asyncio

from enhanced_main import check_and_process_pdf_url


async def demo_pdf_chunk_analysis():
    """PDF 청크 분석 데모"""
    print("🧪 PDF 청크 단위 분석 데모")
    print("=" * 50)

    # 테스트용 샘플 입력들
    test_queries = [
        "삼성전자 주식 분석해줘",  # PDF 없음
        "이 PDF를 분석해줘: https://example.com/report.pdf",  # PDF URL 있음
        "분석 요청: https://test.com/financial-report.pdf 내용 정리",  # PDF URL 있음
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 테스트 {i}: {query}")
        print("-" * 40)

        result = await check_and_process_pdf_url(query)

        if result:
            print(f"✅ PDF URL 감지됨!")
            print(f"   URL: {result['pdf_url']}")
            print(f"   청크 수: {result['total_chunks']}")
            print(
                f"   성공률: {result['analysis_result']['processing_summary']['success_rate']}%"
            )
        else:
            print("ℹ️ PDF URL이 감지되지 않았습니다.")

    print("\n🎉 데모 완료!")


if __name__ == "__main__":
    asyncio.run(demo_pdf_chunk_analysis())
