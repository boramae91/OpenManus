#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 대용량 PDF 보고서 분석 메인 스크립트

이 스크립트는 60만 글자 정도의 대용량 사업보고서나 분기보고서를
AI로 완전히 분석해서 JSON 파일로 저장하는 전문 시스템입니다.

사용법:
1. 터미널에서 실행: python large_pdf_main.py
2. PDF 파일 경로 입력
3. 회사명과 보고서 종류 입력
4. AI가 자동으로 분석해서 JSON 결과 생성

🎯 처리 과정:
1. PDF 텍스트 추출 (무제한 크기)
2. 보고서 구조 AI 분석
3. 섹션별 전문 분석 (GPT-4o 사용)
4. 통합 리포트 생성
5. 핵심 인사이트 추출
6. JSON 파일 저장
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# 환경변수 로딩 (가장 먼저 실행)
from dotenv import load_dotenv

load_dotenv()

# 프로젝트 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from loguru import logger

from app.llm import LLM
from app.utils.large_pdf_analyzer import LargePDFAnalyzer


async def main():
    """
    대용량 PDF 보고서 분석 메인 함수

    이 함수는 사용자와 상호작용하면서 PDF 보고서를 분석해요:
    1. 사용자로부터 PDF 파일 경로 입력받기
    2. 회사명과 보고서 종류 입력받기
    3. AI 분석 시스템 실행
    4. 결과를 JSON으로 저장
    """

    print("🚀 대용량 PDF 보고서 분석 시스템")
    print("=" * 50)
    print("이 시스템은 60만 글자까지의 대용량 보고서를 AI로 분석해서")
    print("체계적인 JSON 파일을 생성합니다. (GPT-4o 사용)")
    print()

    try:
        # 🔍 1단계: 사용자 입력 받기
        print("📁 분석할 PDF 파일 정보를 입력해 주세요:")
        print()

        # PDF 파일 경로 입력
        while True:
            pdf_path = input("PDF 파일 경로: ").strip()
            if pdf_path.startswith('"') and pdf_path.endswith('"'):
                pdf_path = pdf_path[1:-1]  # 따옴표 제거

            if not pdf_path:
                print("❌ PDF 파일 경로를 입력해 주세요.")
                continue

            if not os.path.exists(pdf_path):
                print(f"❌ 파일을 찾을 수 없습니다: {pdf_path}")
                print("올바른 경로를 입력해 주세요.")
                continue

            if not pdf_path.lower().endswith(".pdf"):
                print("❌ PDF 파일이 아닙니다. .pdf 파일을 선택해 주세요.")
                continue

            break

        # 회사명 입력
        company_name = input("회사명 (선택사항): ").strip()
        if not company_name:
            company_name = "분석대상회사"

        # 보고서 종류 입력
        print("\n📊 보고서 종류를 선택해 주세요:")
        print("1. 사업보고서")
        print("2. 분기보고서")
        print("3. 반기보고서")
        print("4. 기타")

        report_choice = input("선택 (1-4): ").strip()
        report_types = {
            "1": "사업보고서",
            "2": "분기보고서",
            "3": "반기보고서",
            "4": "기타보고서",
        }
        report_type = report_types.get(report_choice, "사업보고서")

        if report_choice == "4":
            custom_type = input("보고서 종류를 직접 입력: ").strip()
            if custom_type:
                report_type = custom_type

        print()
        print("=" * 50)
        print(f"📋 분석 설정 확인:")
        print(f"   파일: {pdf_path}")
        print(f"   회사: {company_name}")
        print(f"   종류: {report_type}")
        print("=" * 50)
        print()

        # 시작 확인
        start_confirm = input("분석을 시작하시겠습니까? (y/n): ").strip().lower()
        if start_confirm not in ["y", "yes", "네", "ㅇ"]:
            print("❌ 분석이 취소되었습니다.")
            return

        # 🚀 2단계: AI 분석 시스템 초기화
        print("\n🔧 AI 분석 시스템 초기화 중...")

        # LLM 초기화 (GPT-4o 사용)
        llm = LLM()
        analyzer = LargePDFAnalyzer(llm=llm)

        print("✅ 시스템 초기화 완료!")
        print(f"🤖 사용 모델: GPT-4o")
        print(f"📊 처리 용량: 무제한 (60만+ 글자 지원)")
        print()

        # 🔬 3단계: 대용량 PDF 분석 실행
        print("🔍 대용량 PDF 분석 시작...")
        print("⏱️ 대용량 파일의 경우 몇 분이 소요될 수 있습니다...")
        print()

        start_time = datetime.now()

        # 분석 실행
        result = await analyzer.analyze_large_report(
            pdf_path=pdf_path,
            report_type=report_type,
            company_name=company_name,
            save_directory="results",
        )

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()

        # 📊 4단계: 결과 출력
        print("\n" + "=" * 50)
        print("🎉 분석 완료!")
        print("=" * 50)

        if result["metadata"]["success"]:
            print(f"✅ 분석 성공!")
            print(f"📄 처리된 텍스트: {result['metadata']['total_text_length']:,}자")
            print(f"🧩 분석 섹션 수: {result['metadata']['total_chunks']}개")
            print(f"⏱️ 총 처리 시간: {total_time:.1f}초")
            print(f"💾 저장 경로: {result['metadata']['save_path']}")

            # 핵심 인사이트 미리보기
            if result.get("key_insights", {}).get("success", False):
                print(f"\n💎 핵심 인사이트 미리보기:")
                insights_preview = result["key_insights"]["key_insights"][:300]
                print(f"{insights_preview}...")

            print(f"\n📁 상세 분석 결과는 JSON 파일에서 확인하세요:")
            print(f"   {result['metadata']['save_path']}")

        else:
            print(f"❌ 분석 실패!")
            print(f"🚨 오류: {result['metadata'].get('error', '알 수 없는 오류')}")

        print()
        print("=" * 50)

    except KeyboardInterrupt:
        print("\n❌ 사용자에 의해 중단되었습니다.")

    except Exception as e:
        logger.error(f"❌ 시스템 오류: {str(e)}")
        print(f"\n❌ 시스템 오류가 발생했습니다: {str(e)}")
        print("설정을 확인하고 다시 시도해 주세요.")


def show_example_usage():
    """
    사용 예시를 보여주는 함수
    """
    print("\n📖 사용 예시:")
    print("=" * 30)
    print("1. 삼성전자 사업보고서 분석:")
    print("   파일: reports/삼성전자_2024_사업보고서.pdf")
    print("   회사: 삼성전자")
    print("   종류: 사업보고서")
    print()
    print("2. LG화학 분기보고서 분석:")
    print("   파일: reports/LG화학_2024Q3_분기보고서.pdf")
    print("   회사: LG화학")
    print("   종류: 분기보고서")
    print()
    print("💡 팁:")
    print("- PDF 파일은 드래그 앤 드롭으로 경로를 쉽게 입력할 수 있어요")
    print("- 60만 글자 이상의 대용량 파일도 안전하게 처리됩니다")
    print("- 분석 결과는 results/ 폴더에 JSON 파일로 저장됩니다")


if __name__ == "__main__":
    print("🚀 OpenManus 대용량 PDF 보고서 분석 시스템")
    print("버전: v1.0 | GPT-4o 기반 | 60만+ 글자 지원")
    print()

    # 도움말 옵션 확인
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h", "help"]:
        show_example_usage()
        sys.exit(0)

    # 환경변수 확인
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 오류: OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("💡 .env 파일에 OPENAI_API_KEY를 설정해 주세요.")
        sys.exit(1)

    # 메인 분석 실행
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ 프로그램 실행 오류: {str(e)}")
        sys.exit(1)
