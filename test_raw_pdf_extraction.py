#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 대용량 PDF 원문 추출 테스트 스크립트

기존 PDF 처리를 대체하는 새로운 시스템을 테스트해요:
- 100만+ 글자 지원
- 원문 그대로 추출 (AI 분석 없음)
- 빠른 처리 속도
- JSON 자동 저장
"""

import asyncio
import os
import sys
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.logger import logger
from app.utils.large_pdf_analyzer import LargePDFAnalyzer


class RawPDFExtractionTester:
    """대용량 PDF 원문 추출 테스터"""

    def __init__(self):
        """테스터 초기화"""
        self.analyzer = LargePDFAnalyzer()
        logger.info("🔧 원문 추출 테스터 초기화 완료")

    async def test_raw_extraction(
        self, pdf_path: str, company_name: str = "테스트회사"
    ) -> bool:
        """
        원문 추출 기능을 테스트하는 함수

        Args:
            pdf_path: 테스트할 PDF 파일 경로
            company_name: 회사명

        Returns:
            bool: 테스트 성공 여부
        """
        logger.info(f"🧪 원문 추출 테스트 시작: {pdf_path}")

        try:
            # PDF 파일 존재 확인
            if not os.path.exists(pdf_path):
                logger.error(f"❌ PDF 파일을 찾을 수 없습니다: {pdf_path}")
                return False

            # 원문 추출 실행
            result = await self.analyzer.extract_raw_text_only(
                pdf_path=pdf_path, company_name=company_name, save_to_json=True
            )

            # 결과 검증
            if result.get("metadata", {}).get("success"):
                text_length = result.get("metadata", {}).get("total_text_length", 0)
                saved_file = result.get("saved_file", "")
                processing_time = result.get("metadata", {}).get(
                    "total_processing_time", "알 수 없음"
                )

                logger.info("✅ 원문 추출 테스트 성공!")
                logger.info(f"📊 추출된 텍스트 길이: {text_length:,}자")
                logger.info(f"⏱️ 처리 시간: {processing_time}")
                logger.info(f"💾 저장된 파일: {saved_file}")

                # 미리보기 출력
                preview = result.get("content_preview", "")
                if preview:
                    logger.info("📄 원문 미리보기 (처음 500자):")
                    print("-" * 50)
                    print(preview[:500])
                    print("-" * 50)

                return True
            else:
                error_msg = result.get("metadata", {}).get("error", "알 수 없는 오류")
                logger.error(f"❌ 원문 추출 실패: {error_msg}")
                return False

        except Exception as e:
            logger.error(f"❌ 테스트 중 예외 발생: {str(e)}")
            return False


async def main():
    """메인 실행 함수"""
    print("🚀 대용량 PDF 원문 추출 테스트 시작!")
    print("=" * 60)

    # 테스터 초기화
    tester = RawPDFExtractionTester()

    # 사용자로부터 PDF 파일 경로 입력받기
    pdf_path = input("📝 테스트할 PDF 파일 경로를 입력하세요: ").strip()

    if not pdf_path:
        print("❌ PDF 파일 경로가 입력되지 않았습니다.")
        return

    # 회사명 입력받기 (선택사항)
    company_name = input("🏢 회사명을 입력하세요 (선택사항, 엔터로 건너뛰기): ").strip()
    if not company_name:
        company_name = "테스트회사"

    print(f"\n🔍 테스트 시작: {pdf_path}")
    print(f"🏢 회사명: {company_name}")
    print("-" * 50)

    # 원문 추출 테스트 실행
    success = await tester.test_raw_extraction(pdf_path, company_name)

    print("\n" + "=" * 60)
    if success:
        print("🎉 테스트 완료! 원문 추출이 성공적으로 완료되었습니다.")
        print("📁 results 폴더에서 저장된 JSON 파일을 확인해보세요!")
    else:
        print("❌ 테스트 실패! 오류를 확인해주세요.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
