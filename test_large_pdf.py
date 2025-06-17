#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 대용량 PDF 분석 시스템 테스트 스크립트

이 스크립트는 대용량 PDF 분석 시스템이 올바르게 작동하는지 테스트하는 도구입니다.
실제 PDF 파일이 없어도 시스템의 각 단계를 확인할 수 있어요.

사용법:
python test_large_pdf.py
"""

import asyncio
import os
import sys
from datetime import datetime

# 환경변수 로딩
from dotenv import load_dotenv

load_dotenv()

# 프로젝트 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from loguru import logger

from app.llm import LLM
from app.utils.large_pdf_analyzer import LargePDFAnalyzer


async def test_system_initialization():
    """
    시스템 초기화 테스트

    LLM과 PDF 분석기가 올바르게 초기화되는지 확인해요.
    """
    print("🔧 1단계: 시스템 초기화 테스트")

    try:
        # LLM 초기화 테스트
        llm = LLM()
        print("  ✅ LLM 초기화 성공")

        # PDF 분석기 초기화 테스트
        analyzer = LargePDFAnalyzer(llm=llm)
        print("  ✅ 대용량 PDF 분석기 초기화 성공")

        print(f"  📊 청크 크기: {analyzer.chunk_processor.chunk_size:,}자")
        print(f"  🔄 겹침 크기: {analyzer.chunk_processor.overlap_size:,}자")

        return True, analyzer

    except Exception as e:
        print(f"  ❌ 초기화 실패: {str(e)}")
        return False, None


async def test_text_chunking():
    """
    텍스트 청킹 기능 테스트

    대용량 텍스트를 적절한 청크로 나누는 기능을 테스트해요.
    """
    print("\n🧩 2단계: 텍스트 청킹 기능 테스트")

    try:
        # 테스트용 긴 텍스트 생성 (약 50KB)
        test_text = (
            """
        삼성전자 2024년 3분기 실적 분석

        1. 개요
        삼성전자는 2024년 3분기에 매출 79조원을 기록하며 전년 동기 대비 15% 증가했습니다.
        이는 메모리 반도체 시장의 회복과 AI 칩 수요 증가에 기인합니다.

        2. 사업부문별 성과
        2.1 반도체 사업부
        - 매출: 35조원 (전년 동기 대비 25% 증가)
        - 영업이익: 12조원 (전년 동기 대비 80% 증가)
        - 주요 성장 동력: AI 서버용 고대역폭 메모리(HBM) 수요 급증

        2.2 디스플레이 사업부
        - 매출: 18조원 (전년 동기 대비 5% 감소)
        - 영업이익: 2.5조원 (전년 동기 대비 10% 감소)
        - 주요 이슈: 스마트폰 시장 둔화 영향

        3. 재무 현황
        3.1 수익성 지표
        - 총 영업이익률: 20.5% (전년 동기 15.2%)
        - 순이익률: 18.3% (전년 동기 13.1%)
        - ROE: 22.1% (전년 동기 16.8%)

        3.2 안정성 지표
        - 부채비율: 28.5% (전년 동기 31.2%)
        - 유동비율: 180.3% (전년 동기 175.1%)
        - 자기자본비율: 77.8% (전년 동기 76.2%)
        """
            * 200
        )  # 200번 반복해서 긴 텍스트 만들기

        analyzer = LargePDFAnalyzer()

        # 텍스트 청킹 테스트
        chunks = analyzer.chunk_processor.smart_chunk_text(
            test_text, preserve_sections=True
        )

        print(f"  📊 테스트 텍스트 길이: {len(test_text):,}자")
        print(f"  🧩 생성된 청크 수: {len(chunks)}개")

        if chunks:
            print(f"  📏 첫 번째 청크 길이: {len(chunks[0]['content']):,}자")
            print(f"  📏 마지막 청크 길이: {len(chunks[-1]['content']):,}자")
            print("  ✅ 텍스트 청킹 성공")
            return True
        else:
            print("  ❌ 청킹 실패: 청크가 생성되지 않음")
            return False

    except Exception as e:
        print(f"  ❌ 청킹 테스트 실패: {str(e)}")
        return False


async def test_ai_analysis():
    """
    AI 분석 기능 테스트

    실제 GPT-4o를 사용해서 텍스트 분석이 작동하는지 테스트해요.
    """
    print("\n🤖 3단계: AI 분석 기능 테스트")

    try:
        llm = LLM()
        analyzer = LargePDFAnalyzer(llm=llm)

        # 테스트용 간단한 재무 텍스트
        test_content = """
        삼성전자 2024년 3분기 실적 요약

        - 매출: 79조원 (전년 동기 대비 15% 증가)
        - 영업이익: 16.2조원 (전년 동기 대비 35% 증가)
        - 순이익: 14.5조원 (전년 동기 대비 28% 증가)

        주요 성장 동력:
        1. AI 반도체 수요 급증으로 HBM 매출 300% 증가
        2. 서버용 SSD 매출 40% 증가
        3. 모바일 프로세서 시장점유율 확대

        주요 우려사항:
        1. 중국 시장 스마트폰 수요 둔화
        2. 디스플레이 패널 가격 하락 압박
        3. 환율 변동 리스크
        """

        # AI 분석 프롬프트 생성
        prompt = analyzer._create_professional_analysis_prompt(
            content=test_content,
            report_type="분기보고서",
            company_name="삼성전자",
            section_num=1,
            total_sections=1,
        )

        print("  🔍 AI 분석 요청 중...")

        # AI 분석 실행
        analysis_result = await analyzer.llm.ask([{"role": "user", "content": prompt}])

        if analysis_result and len(analysis_result) > 100:
            print("  ✅ AI 분석 성공")
            print(f"  📊 분석 결과 길이: {len(analysis_result)}자")
            print(f"  📝 분석 미리보기: {analysis_result[:200]}...")
            return True
        else:
            print("  ❌ AI 분석 실패: 결과가 너무 짧거나 비어있음")
            return False

    except Exception as e:
        print(f"  ❌ AI 분석 테스트 실패: {str(e)}")
        return False


async def test_json_saving():
    """
    JSON 파일 저장 기능 테스트

    분석 결과를 JSON 파일로 저장하는 기능을 테스트해요.
    """
    print("\n💾 4단계: JSON 저장 기능 테스트")

    try:
        analyzer = LargePDFAnalyzer()

        # 테스트용 분석 결과 생성
        test_result = {
            "metadata": {
                "pdf_path": "test_report.pdf",
                "report_type": "테스트보고서",
                "company_name": "테스트회사",
                "analysis_start_time": datetime.now().isoformat(),
                "success": True,
                "total_text_length": 50000,
                "total_chunks": 3,
                "analyzer_version": "LargePDFAnalyzer_v1.0_TEST",
            },
            "key_insights": {
                "success": True,
                "key_insights": "테스트 인사이트: 이 회사는 테스트용으로 좋은 성과를 보이고 있습니다.",
                "extraction_timestamp": datetime.now().isoformat(),
            },
        }

        # JSON 파일 저장 테스트
        save_path = await analyzer._save_analysis_results(
            analysis_results=test_result,
            save_directory="test_results",
            company_name="테스트회사",
            report_type="테스트보고서",
        )

        if os.path.exists(save_path):
            print(f"  ✅ JSON 저장 성공")
            print(f"  📁 저장 경로: {save_path}")

            # 파일 크기 확인
            file_size = os.path.getsize(save_path)
            print(f"  📊 파일 크기: {file_size:,} 바이트")

            # 테스트 파일 정리
            os.remove(save_path)
            os.rmdir("test_results")
            print("  🧹 테스트 파일 정리 완료")

            return True
        else:
            print(f"  ❌ JSON 저장 실패: 파일이 생성되지 않음")
            return False

    except Exception as e:
        print(f"  ❌ JSON 저장 테스트 실패: {str(e)}")
        return False


async def run_full_test():
    """
    전체 시스템 테스트 실행

    모든 테스트를 순차적으로 실행해서 시스템 상태를 점검해요.
    """
    print("🧪 대용량 PDF 분석 시스템 전체 테스트")
    print("=" * 50)
    print("시스템의 각 기능이 올바르게 작동하는지 확인합니다.")
    print()

    test_results = []

    # 1단계: 시스템 초기화 테스트
    init_success, analyzer = await test_system_initialization()
    test_results.append(("시스템 초기화", init_success))

    if not init_success:
        print("\n❌ 시스템 초기화 실패로 테스트 중단")
        return False

    # 2단계: 텍스트 청킹 테스트
    chunk_success = await test_text_chunking()
    test_results.append(("텍스트 청킹", chunk_success))

    # 3단계: AI 분석 테스트 (OpenAI API 키가 있을 때만)
    if os.getenv("OPENAI_API_KEY"):
        ai_success = await test_ai_analysis()
        test_results.append(("AI 분석", ai_success))
    else:
        print("\n⚠️ OPENAI_API_KEY가 없어서 AI 분석 테스트를 건너뜁니다.")
        test_results.append(("AI 분석", "건너뜀"))

    # 4단계: JSON 저장 테스트
    json_success = await test_json_saving()
    test_results.append(("JSON 저장", json_success))

    # 테스트 결과 요약
    print("\n" + "=" * 50)
    print("🧪 테스트 결과 요약")
    print("=" * 50)

    for test_name, result in test_results:
        if result == True:
            print(f"✅ {test_name}: 성공")
        elif result == "건너뜀":
            print(f"⚠️ {test_name}: 건너뜀")
        else:
            print(f"❌ {test_name}: 실패")

    # 전체 성공률 계산
    success_count = sum(1 for _, result in test_results if result == True)
    total_tests = len([r for _, r in test_results if r != "건너뜀"])
    success_rate = (success_count / total_tests * 100) if total_tests > 0 else 0

    print(f"\n📊 전체 성공률: {success_rate:.1f}% ({success_count}/{total_tests})")

    if success_rate >= 75:
        print("🎉 시스템이 정상적으로 작동하고 있습니다!")
        return True
    else:
        print("⚠️ 일부 기능에 문제가 있습니다. 설정을 확인해 주세요.")
        return False


async def main():
    """메인 테스트 함수"""
    try:
        success = await run_full_test()

        print("\n" + "=" * 50)
        if success:
            print("✅ 테스트 완료: 시스템이 정상적으로 작동합니다!")
            print("\n💡 이제 large_pdf_main.py를 실행해서 실제 PDF를 분석해 보세요:")
            print("   python large_pdf_main.py")
        else:
            print("❌ 테스트 완료: 일부 기능에 문제가 있습니다.")
            print("\n🔧 해결 방법:")
            print("1. .env 파일에 OPENAI_API_KEY가 올바르게 설정되어 있는지 확인")
            print("2. 필요한 패키지들이 모두 설치되어 있는지 확인")
            print("3. 네트워크 연결 상태 확인")

    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류: {str(e)}")


if __name__ == "__main__":
    print("🧪 OpenManus 대용량 PDF 분석 시스템 테스트")
    print("버전: v1.0 | 시스템 점검 도구")
    print()

    asyncio.run(main())
