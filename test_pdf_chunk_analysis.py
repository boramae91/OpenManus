#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 PDF 청크 단위 전문 분석 테스트 스크립트

이 스크립트는 OpenManus의 새로운 PDF 청크 처리 기능을 테스트하고 시연합니다.
대용량 PDF 파일도 메모리 효율적으로 처리하면서 전문 분석을 수행할 수 있습니다.

주요 기능:
- 📄 PDF URL 자동 감지
- 🧩 스마트 청킹 (섹션, 문단, 고정 크기)
- 🔬 각 청크별 AI 분석
- 📊 진행 상황 실시간 추적
- 📋 결과 통합 및 요약

사용법:
    python test_pdf_chunk_analysis.py
"""

import asyncio
import time
from datetime import datetime
from pathlib import Path

from app.logger import logger

# OpenManus 라이브러리 임포트
from app.utils.pdf_reader import ChunkProcessor, PDFReader


class PDFChunkAnalysisDemo:
    """📄 PDF 청크 분석 시연 클래스"""

    def __init__(self):
        """데모 시스템 초기화"""
        self.pdf_reader = PDFReader(max_chars=100000)  # 100KB 전문 분석 모드
        self.chunk_processor = ChunkProcessor()
        self.demo_stats = {
            "start_time": None,
            "end_time": None,
            "processed_chunks": 0,
            "total_characters": 0,
            "success_rate": 0.0,
        }

        logger.info("🚀 PDF 청크 분석 데모 시스템 초기화 완료")

    async def run_demo_analysis(self, pdf_source: str) -> dict:
        """
        📊 PDF 청크 분석 데모 실행

        Args:
            pdf_source: PDF URL 또는 파일 경로

        Returns:
            dict: 분석 결과 및 통계
        """
        print("=" * 60)
        print("🧪 PDF 청크 단위 전문 분석 데모")
        print("=" * 60)
        print(f"📄 분석 대상: {pdf_source}")
        print(f"🕒 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)

        self.demo_stats["start_time"] = time.time()

        try:
            # 진행 상황 추적 콜백
            async def demo_progress_callback(
                current: int, total: int, chunk_info: dict
            ):
                progress = round(current / total * 100, 1)
                chunk_size = chunk_info.get("chunk_size", 0)
                chunk_type = chunk_info.get("metadata", {}).get("type", "알 수 없음")

                print(
                    f"📖 청크 {current:2d}/{total:2d} 분석 중... "
                    f"({progress:5.1f}%) "
                    f"| 크기: {chunk_size:,}자 "
                    f"| 타입: {chunk_type}"
                )

            # 청크별 분석 함수
            async def demo_chunk_analysis(chunk: dict) -> dict:
                """시연용 청크 분석 함수"""
                content = chunk["content"]

                # 간단한 텍스트 분석 수행
                analysis = {
                    "chunk_summary": self._create_chunk_summary(content),
                    "key_insights": self._extract_key_insights(content),
                    "structure_analysis": self._analyze_structure(content),
                    "keyword_density": self._calculate_keyword_density(content),
                    "readability_score": self._estimate_readability(content),
                    "processing_time": time.time(),
                }

                # 처리 시간 시뮬레이션 (실제 AI 분석 시간)
                await asyncio.sleep(0.5)  # 500ms 시뮬레이션

                return analysis

            # PDF 청크 분석 실행
            print("🔍 PDF 텍스트 추출 및 청킹 시작...")

            result = await self.pdf_reader.read_pdf_chunked(
                pdf_path=pdf_source,
                analysis_function=demo_chunk_analysis,
                progress_callback=demo_progress_callback,
                chunk_size=12000,  # 12KB 청크 (데모용)
                preserve_sections=True,
            )

            self.demo_stats["end_time"] = time.time()

            if result.get("success"):
                # 통계 업데이트
                self.demo_stats.update(
                    {
                        "processed_chunks": result.get("successful_chunks", 0),
                        "total_characters": result.get("total_text_length", 0),
                        "success_rate": result["processing_summary"]["success_rate"],
                    }
                )

                # 결과 출력
                self._print_analysis_results(result)

                return {
                    "success": True,
                    "analysis_result": result,
                    "demo_stats": self.demo_stats,
                }
            else:
                print(f"❌ 분석 실패: {result.get('error', '알 수 없는 오류')}")
                return {"success": False, "error": result.get("error")}

        except Exception as e:
            print(f"❌ 데모 실행 중 오류: {e}")
            return {"success": False, "error": str(e)}

    def _create_chunk_summary(self, content: str) -> str:
        """청크 내용 간단 요약"""
        sentences = content.split(".")[:3]  # 첫 3문장
        summary = ". ".join(s.strip() for s in sentences if s.strip())
        return summary[:200] + "..." if len(summary) > 200 else summary

    def _extract_key_insights(self, content: str) -> list:
        """핵심 인사이트 추출"""
        insights = []

        # 중요한 키워드들
        important_keywords = [
            "수익률",
            "투자",
            "성장",
            "위험",
            "전략",
            "분석",
            "시장",
            "경제",
            "재무",
            "실적",
            "예측",
            "전망",
        ]

        for keyword in important_keywords:
            if keyword in content:
                # 키워드 주변 문맥 추출
                import re

                pattern = rf".{{0,30}}{keyword}.{{0,30}}"
                matches = re.findall(pattern, content)
                if matches:
                    insights.append(f"{keyword}: {matches[0][:60]}...")

        return insights[:5]

    def _analyze_structure(self, content: str) -> dict:
        """텍스트 구조 분석"""
        return {
            "총_글자수": len(content),
            "문단_수": content.count("\n\n") + 1,
            "문장_수": content.count(".") + content.count("!") + content.count("?"),
            "has_numbers": bool(re.search(r"\d+", content)),
            "has_tables": "│" in content or "┌" in content,
            "has_lists": "•" in content or "-" in content,
        }

    def _calculate_keyword_density(self, content: str) -> dict:
        """키워드 밀도 계산"""
        import re
        from collections import Counter

        words = re.findall(r"[가-힣]{2,}", content)
        word_counts = Counter(words)
        total_words = len(words)

        if total_words == 0:
            return {"총_단어수": 0, "상위_키워드": []}

        top_words = word_counts.most_common(5)
        keyword_density = {
            "총_단어수": total_words,
            "상위_키워드": [
                {
                    "단어": word,
                    "빈도": count,
                    "밀도": round(count / total_words * 100, 2),
                }
                for word, count in top_words
            ],
        }

        return keyword_density

    def _estimate_readability(self, content: str) -> dict:
        """가독성 점수 추정 (간단한 버전)"""
        sentences = content.count(".") + content.count("!") + content.count("?")
        words = len(content.split())

        if sentences == 0:
            return {"평균_문장길이": 0, "가독성_등급": "측정불가"}

        avg_sentence_length = words / sentences

        # 간단한 가독성 평가
        if avg_sentence_length < 15:
            readability = "쉬움"
        elif avg_sentence_length < 25:
            readability = "보통"
        else:
            readability = "어려움"

        return {
            "평균_문장길이": round(avg_sentence_length, 1),
            "가독성_등급": readability,
            "총_문장수": sentences,
            "총_단어수": words,
        }

    def _print_analysis_results(self, result: dict):
        """분석 결과 출력"""
        print("\n" + "=" * 60)
        print("📊 PDF 청크 분석 결과")
        print("=" * 60)

        # 기본 통계
        total_chunks = result.get("total_chunks", 0)
        successful_chunks = result.get("successful_chunks", 0)
        success_rate = result["processing_summary"]["success_rate"]
        total_chars = result.get("total_text_length", 0)

        print(f"📄 처리 결과:")
        print(f"   • 총 청크 수: {total_chunks}개")
        print(f"   • 성공 분석: {successful_chunks}개")
        print(f"   • 성공률: {success_rate}%")
        print(f"   • 총 문자 수: {total_chars:,}자")

        # 처리 시간
        processing_time = self.demo_stats["end_time"] - self.demo_stats["start_time"]
        print(f"   • 처리 시간: {processing_time:.1f}초")

        print(f"\n📈 성능 지표:")
        if processing_time > 0:
            chars_per_sec = total_chars / processing_time
            chunks_per_sec = total_chunks / processing_time
            print(f"   • 처리 속도: {chars_per_sec:,.0f}자/초")
            print(f"   • 청크 처리율: {chunks_per_sec:.1f}청크/초")

        # 청크별 분석 샘플 출력
        chunk_results = result.get("chunk_results", [])
        if chunk_results:
            print(f"\n🔍 청크 분석 샘플 (첫 번째 청크):")
            first_chunk = chunk_results[0]["result"]

            if "structure_analysis" in first_chunk:
                structure = first_chunk["structure_analysis"]
                print(
                    f"   • 구조: {structure.get('문단_수', 0)}문단, {structure.get('문장_수', 0)}문장"
                )

            if "key_insights" in first_chunk and first_chunk["key_insights"]:
                print(f"   • 핵심 인사이트: {len(first_chunk['key_insights'])}개 발견")

            if "readability_score" in first_chunk:
                readability = first_chunk["readability_score"]
                print(f"   • 가독성: {readability.get('가독성_등급', '측정불가')}")

        print("\n🎉 PDF 청크 분석 완료!")


async def main():
    """데모 실행 메인 함수"""
    print("🧪 PDF 청크 단위 전문 분석 데모")
    print("이 데모는 대용량 PDF를 안전하게 처리하는 방법을 보여줍니다.\n")

    demo = PDFChunkAnalysisDemo()

    # 테스트 옵션 제공
    print("테스트 옵션을 선택하세요:")
    print("1. PDF URL 입력")
    print("2. 로컬 PDF 파일")
    print("3. 샘플 텍스트로 테스트")

    choice = input("\n선택 (1-3): ").strip()

    if choice == "1":
        pdf_url = input("PDF URL을 입력하세요: ").strip()
        if pdf_url:
            result = await demo.run_demo_analysis(pdf_url)
        else:
            print("❌ 유효한 URL을 입력해주세요.")
            return

    elif choice == "2":
        pdf_path = input("PDF 파일 경로를 입력하세요: ").strip()
        if pdf_path and Path(pdf_path).exists():
            result = await demo.run_demo_analysis(pdf_path)
        else:
            print("❌ 파일을 찾을 수 없습니다.")
            return

    elif choice == "3":
        # 샘플 텍스트 생성
        print("📝 샘플 텍스트로 청킹 테스트를 진행합니다...")

        sample_text = (
            """
        제1장 투자 개요

        본 보고서는 주식 투자에 대한 종합적인 분석을 제공합니다.
        투자 수익률은 지난 5년간 평균 12.5%를 기록했으며,
        이는 시장 평균인 8.9%를 크게 상회하는 수치입니다.

        제2장 재무 분석

        재무 건전성 측면에서 볼 때, 부채비율은 35%로
        업계 평균인 45%보다 낮은 수준을 유지하고 있습니다.
        ROE는 15.2%, ROA는 8.7%로 양호한 수준입니다.

        제3장 시장 전망

        향후 시장 전망은 긍정적으로 평가됩니다.
        신규 사업 진출과 기술 혁신을 통해
        지속적인 성장이 기대됩니다.
        """
            * 10
        )  # 텍스트 반복으로 크기 증가

        # 임시 텍스트 파일 생성
        temp_file = "temp_sample.txt"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(sample_text)

        try:
            # 청킹 테스트 (PDF 대신 텍스트 직접 처리)
            chunk_processor = ChunkProcessor(chunk_size=500, overlap_size=50)
            chunks = chunk_processor.smart_chunk_text(sample_text)

            print(f"✅ 청킹 완료: {len(chunks)}개 청크 생성")
            for i, chunk in enumerate(chunks[:3], 1):  # 첫 3개 청크만 표시
                print(f"\n📄 청크 {i}:")
                print(f"   크기: {chunk['chunk_size']}자")
                print(f"   타입: {chunk['metadata'].get('type', '알 수 없음')}")
                print(f"   내용: {chunk['content'][:100]}...")

        finally:
            # 임시 파일 삭제
            if Path(temp_file).exists():
                Path(temp_file).unlink()

        return

    else:
        print("❌ 잘못된 선택입니다.")
        return

    # 결과 요약
    if result and result.get("success"):
        print(f"\n🎯 데모 완료 요약:")
        stats = result.get("demo_stats", {})
        print(f"   • 처리된 청크: {stats.get('processed_chunks', 0)}개")
        print(f"   • 총 처리 문자: {stats.get('total_characters', 0):,}자")
        print(f"   • 성공률: {stats.get('success_rate', 0)}%")
        print(f"\n💡 이제 실제 PDF URL과 함께 enhanced_main.py를 실행해보세요!")
    else:
        print("❌ 데모 실행에 실패했습니다.")


if __name__ == "__main__":
    # 필요한 모듈 임포트
    import re

    # 데모 실행
    asyncio.run(main())
