#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 대용량 PDF 분석 시스템 v2.0

100만 글자까지의 대용량 PDF 파일을 AI로 완전 분석하는 전문 시스템입니다.

주요 기능:
1. 🔍 PDF 목차 기반 지능형 청킹 (최적화된 섹션 분할)
2. 🤖 GPT-4o 기반 섹션별 정밀 분석
3. 🎯 CrewAI용 PDF 딕셔너리 생성 (100만자 지원)
4. 💾 JSON 직렬화 지원 (메모리 효율성)

특징:
- 지능형: 목차와 제목 구조를 인식한 논리적 분할
- 확장성: 다양한 PDF 형식 지원
- 대용량: 100만+ 글자 처리 가능
- 효율성: 메모리 최적화 및 병렬 처리
- 안정성: 에러 처리 및 복구 기능

사용법:
```python
from app.utils.large_pdf_analyzer import LargePDFAnalyzer
from app.llm import LLM

llm = LLM()
analyzer = LargePDFAnalyzer(llm=llm)

# PDF 파일을 딕셔너리로 변환
result = await analyzer.analyze_pdf_to_dictionary(
    pdf_path="report.pdf",
    company_name="삼성전자",
    max_section_size=1000000  # 100만자 지원
)

if result["success"]:
    pdf_dict = result["pdf_dictionary"]
    print(f"분석 완료: {len(pdf_dict)}개 섹션")
```

버전 히스토리:
- v1.0: 기본 PDF 분석 기능
- v1.5: 목차 기반 청킹 추가
- v2.0: 100만+ 글자 지원
"""

import asyncio
import io
import json
import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# PyMuPDF 안전 가져오기 - 라이브러리가 없어도 프로그램이 멈추지 않아요!
try:
    import fitz  # PyMuPDF - PDF 문서를 읽고 분석하는 강력한 도구예요

    PYMUPDF_AVAILABLE = True
    print("✅ PyMuPDF(fitz) 라이브러리를 성공적으로 불러왔습니다!")
except ImportError as e:
    print(f"⚠️ PyMuPDF(fitz) 라이브러리를 찾을 수 없습니다: {e}")
    print("💡 해결방법: 터미널에서 'pip install pymupdf' 명령어를 실행하세요")
    PYMUPDF_AVAILABLE = False

    # 가짜 fitz 모듈을 만들어서 나머지 코드가 동작하도록 해요
    class MockFitz:
        def open(self, *args, **kwargs):
            raise RuntimeError("PyMuPDF가 설치되지 않아서 PDF 처리가 불가능합니다")

    fitz = MockFitz()

# 다른 PDF 처리 라이브러리들도 안전하게 가져와요
try:
    import pdfplumber

    PDFPLUMBER_AVAILABLE = True
except ImportError:
    print("⚠️ pdfplumber 라이브러리를 찾을 수 없습니다")
    PDFPLUMBER_AVAILABLE = False

try:
    import PyPDF2

    PYPDF2_AVAILABLE = True
except ImportError:
    print("⚠️ PyPDF2 라이브러리를 찾을 수 없습니다")
    PYPDF2_AVAILABLE = False

from loguru import logger

from app.llm import LLM

# 🔖 목차 기반 청킹을 위한 PyMuPDF 가용성 확인
# 이 부분은 이미 위에서 처리했으니 주석처리해요
# try:
#     PYMUPDF_AVAILABLE = True
# except ImportError:
#     PYMUPDF_AVAILABLE = False
#     logger.warning("⚠️ PyMuPDF를 찾을 수 없습니다. 목차 기반 청킹이 비활성화됩니다.")


class IndependentChunkProcessor:
    """
    🚀 PDFReader와 완전히 독립된 청크 처리기

    대용량 PDF를 위한 전용 청크 프로세서예요:
    - PDFReader 의존성 완전 제거
    - 100만+ 글자 지원
    - 🔖 목차 기반 청킹 지원
    - 스마트 섹션 보존
    """

    def __init__(self, chunk_size: int = 25000, overlap_size: int = 2000):
        """
        독립 청크 프로세서 초기화

        Args:
            chunk_size: 각 청크의 최대 크기 (문자 수)
            overlap_size: 청크 간 겹치는 부분 크기 (문맥 유지용)
        """
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        logger.info(
            f"🔧 독립 청크 프로세서 초기화 (청크: {chunk_size:,}자, 겹침: {overlap_size:,}자)"
        )

        # 🔖 목차 기반 청킹 지원 여부
        self.toc_chunking_available = PYMUPDF_AVAILABLE
        if self.toc_chunking_available:
            logger.info("🔖 PDF 목차 기반 청킹 지원 활성화됨")

    async def _download_pdf_from_url(self, url: str) -> Optional[io.BytesIO]:
        """
        URL에서 PDF 파일을 다운로드하여 메모리 스트림으로 반환

        Args:
            url: PDF 파일 URL

        Returns:
            Optional[io.BytesIO]: 다운로드된 PDF 데이터 스트림 또는 None (실패시)
        """
        try:
            logger.info(f"🌐 PDF URL 다운로드 시작: {url}")

            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        pdf_data = await response.read()
                        pdf_stream = io.BytesIO(pdf_data)
                        logger.info(f"✅ PDF 다운로드 완료: {len(pdf_data):,} bytes")
                        return pdf_stream
                    else:
                        logger.error(f"❌ PDF 다운로드 실패: HTTP {response.status}")
                        return None

        except Exception as e:
            logger.error(f"❌ PDF URL 다운로드 오류: {e}")
            return None

    def smart_chunk_text(
        self, text: str, preserve_sections: bool = True
    ) -> List[Dict[str, Any]]:
        """
        텍스트를 논리적 섹션으로 분할합니다 (목차가 없는 경우)

        🚀 200만자 지원으로 대용량 섹션도 완벽 처리!
        """
        sections = {}

        # 간단한 섹션 분할 패턴들
        section_patterns = [
            r"\n\s*\d+\.\s+[가-힣\w\s]+\n",  # 1. 섹션명
            r"\n\s*[가-힣]+\s*\n",  # 단독 한글 제목
            r"\n\s*[A-Z][A-Z\s]+\n",  # 영문 대문자 제목
        ]

        # 패턴으로 분할점 찾기
        split_points = [0]
        for pattern in section_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                split_points.append(match.start())

        split_points.append(len(text))
        split_points = sorted(list(set(split_points)))

        # 섹션 생성
        for i in range(len(split_points) - 1):
            start = split_points[i]
            end = split_points[i + 1]

            section_text = text[start:end].strip()

            # 🚀 최소 길이 100자로 유지하되, 최대 크기는 200만자로 확장
            if len(section_text) >= 100:  # 최소 길이
                # 섹션 제목 추출
                title_match = re.match(r"(.*?)\n", section_text)
                if title_match:
                    section_title = title_match.group(1).strip()[:50]
                else:
                    section_title = f"섹션_{i+1}"

                # 🚀 200만자 제한 적용 (기존보다 2배 확장!)
                if len(section_text) > 2000000:
                    section_text = (
                        section_text[:2000000] + "...[200만자 제한으로 내용 일부 생략]"
                    )

                sections[section_title] = section_text

        logger.info(f"🤖 논리적 섹션 분할 완료 - {len(sections)}개 섹션 (200만자 지원)")
        return sections

    async def extract_pdf_table_of_contents(
        self, pdf_path: str
    ) -> List[Dict[str, Any]]:
        """
        🔖 PDF에서 목차(Table of Contents) 추출

        PyMuPDF를 사용하여 PDF의 북마크/아웃라인을 추출하고
        계층 구조로 정리합니다.

        URL과 로컬 파일 모두 지원해요!

        Args:
            pdf_path: PDF 파일 경로 또는 URL

        Returns:
            List[Dict]: 목차 구조 리스트
        """
        if not self.toc_chunking_available:
            logger.warning("⚠️ PyMuPDF가 없어서 목차 추출이 불가능합니다")
            return []

        try:
            # URL인지 로컬 파일인지 확인하고 적절히 처리
            if pdf_path.startswith(("http://", "https://")):
                # 🌐 URL PDF - 메모리에서 처리
                logger.info(f"🌐 URL PDF 목차 추출 시도: {pdf_path}")
                pdf_data = await self._download_pdf_from_url(pdf_path)
                if not pdf_data:
                    logger.error(f"❌ URL PDF 다운로드 실패: {pdf_path}")
                    return []

                # 메모리 스트림으로 PDF 문서 열기
                doc = fitz.open(stream=pdf_data.getvalue(), filetype="pdf")
            else:
                # 📁 로컬 파일 처리
                logger.info(f"📁 로컬 PDF 목차 추출 시도: {pdf_path}")
                doc = fitz.open(pdf_path)

            # 목차 추출 (toc = table of contents)
            toc = doc.get_toc(simple=False)  # detailed=True
            doc.close()

            if not toc:
                logger.info("📄 PDF에 목차가 없습니다")
                return []

            # 목차 구조 정리
            structured_toc = []
            for item in toc:
                level = item[0]  # 계층 레벨 (1=최상위, 2=하위 등)
                title = item[1]  # 목차 제목
                page_num = item[2]  # 페이지 번호

                # 추가 정보가 있으면 추출
                if len(item) > 3:
                    dest = item[3]  # 목적지 정보
                else:
                    dest = None

                structured_toc.append(
                    {
                        "level": level,
                        "title": title.strip(),
                        "page": page_num,
                        "destination": dest,
                        "section_id": len(structured_toc) + 1,
                    }
                )

            logger.info(f"🔖 PDF 목차 추출 완료: {len(structured_toc)}개 항목")

            # 목차 구조를 계층별로 로그 출력
            for item in structured_toc[:10]:  # 처음 10개만 출력
                indent = "  " * (item["level"] - 1)
                logger.info(f"  {indent}📑 {item['title']} (페이지 {item['page']})")

            if len(structured_toc) > 10:
                logger.info(f"  ... 외 {len(structured_toc) - 10}개 목차 항목")

            return structured_toc

        except Exception as e:
            logger.error(f"❌ PDF 목차 추출 실패: {e}")
            return []

    def chunk_by_table_of_contents(
        self, text: str, table_of_contents: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        🔖 목차를 기반으로 텍스트를 청킹합니다

        목차 구조에 따라 텍스트를 논리적 섹션으로 나누어서
        각 섹션별로 청크를 생성해요!

        Args:
            text: 전체 PDF 텍스트
            table_of_contents: 목차 구조 리스트

        Returns:
            List[Dict]: 목차 기반 청크 리스트
        """
        if not table_of_contents:
            logger.warning("⚠️ 목차가 없어서 기본 청킹으로 대체합니다")
            return self.smart_chunk_text(text, preserve_sections=True)

        chunks = []

        try:
            logger.info(f"🔖 목차 기반 청킹 시작: {len(table_of_contents)}개 목차 항목")

            for i, toc_item in enumerate(table_of_contents):
                section_title = toc_item.get("title", f"섹션_{i+1}")

                # 텍스트에서 해당 섹션 찾기
                title_pos = text.find(section_title)

                if title_pos == -1:
                    # 제목 변형으로 다시 시도
                    title_variations = [
                        section_title.replace(" ", ""),
                        section_title.replace(".", ""),
                        section_title.upper(),
                        section_title.lower(),
                    ]

                    for variation in title_variations:
                        title_pos = text.find(variation)
                        if title_pos != -1:
                            break

                if title_pos == -1:
                    logger.warning(
                        f"⚠️ 섹션 '{section_title}'을 텍스트에서 찾을 수 없습니다"
                    )
                    continue

                # 다음 섹션까지의 텍스트 추출
                next_pos = len(text)
                for j in range(i + 1, len(table_of_contents)):
                    next_title = table_of_contents[j].get("title", "")
                    next_title_pos = text.find(next_title, title_pos + 1)
                    if next_title_pos != -1:
                        next_pos = next_title_pos
                        break

                section_text = text[title_pos:next_pos].strip()

                # 섹션이 너무 크면 서브청킹
                if len(section_text) > self.chunk_size:
                    # 큰 섹션을 여러 청크로 분할
                    sub_chunks = self._split_large_section(section_text, section_title)
                    chunks.extend(sub_chunks)
                else:
                    # 작은 섹션은 하나의 청크로
                    if len(section_text) >= 100:  # 최소 길이 필터
                        chunks.append(
                            {
                                "chunk_id": len(chunks) + 1,
                                "section_title": section_title,
                                "section_type": "toc_based",
                                "chunk_type": "toc_based",
                                "analysis_priority": "high",
                                "content": section_text,
                                "content_length": len(section_text),
                                "metadata": {
                                    "toc_level": toc_item.get("level", 1),
                                    "page": toc_item.get("page", "unknown"),
                                    "source": "table_of_contents",
                                },
                            }
                        )

            logger.info(f"✅ 목차 기반 청킹 완료: {len(chunks)}개 청크 생성")

        except Exception as e:
            logger.error(f"❌ 목차 기반 청킹 실패: {e}")
            # 실패시 기본 청킹으로 폴백
            return self.smart_chunk_text(text, preserve_sections=True)

        return chunks

    def _split_large_section(
        self, section_text: str, section_title: str
    ) -> List[Dict[str, Any]]:
        """
        큰 섹션을 여러 청크로 분할

        Args:
            section_text: 섹션 텍스트
            section_title: 섹션 제목

        Returns:
            List[Dict]: 분할된 청크 리스트
        """
        chunks = []
        current_pos = 0
        chunk_num = 1

        while current_pos < len(section_text):
            # 청크 크기만큼 자르기
            end_pos = min(current_pos + self.chunk_size, len(section_text))

            # 단어 경계에서 자르기 (더 자연스러운 분할)
            if end_pos < len(section_text):
                # 마지막 공백이나 줄바꿈 찾기
                last_space = section_text.rfind(" ", current_pos, end_pos)
                last_newline = section_text.rfind("\n", current_pos, end_pos)

                # 더 나은 분할점 선택
                better_end = max(last_space, last_newline)
                if better_end > current_pos + (
                    self.chunk_size * 0.7
                ):  # 70% 이상이면 사용
                    end_pos = better_end

            chunk_text = section_text[current_pos:end_pos].strip()

            if len(chunk_text) >= 100:  # 최소 길이 필터
                chunks.append(
                    {
                        "chunk_id": len(chunks) + 1,
                        "section_title": f"{section_title}_Part{chunk_num}",
                        "section_type": "toc_based_split",
                        "chunk_type": "toc_based",
                        "analysis_priority": "high",
                        "content": chunk_text,
                        "content_length": len(chunk_text),
                        "metadata": {
                            "original_section": section_title,
                            "part_number": chunk_num,
                            "is_split_chunk": True,
                            "source": "large_section_split",
                        },
                    }
                )
                chunk_num += 1

            # 다음 청크로 이동 (겹침 고려)
            current_pos = max(end_pos - self.overlap_size, end_pos)
            if current_pos >= end_pos:  # 무한루프 방지
                break

        return chunks


class LargePDFAnalyzer:
    """
    🚀 대용량 PDF 분석 전문 클래스

    주요 기능:
    1. 📄 대용량 PDF 직접 처리 (메모리 최적화)
    2. 🧩 청킹 및 토큰 최적화
    3. 🎯 CrewAI용 PDF 딕셔너리 생성 (200만자 지원)
    4. 💡 AI 기반 목차 구조 분석
    5. ⚡ 병렬 처리로 속도 최적화

    특징:
    - 메모리 효율적 스트리밍 처리
    - 200만자 대용량 섹션 지원
    - CrewAI 전문가별 최적화된 섹션 제공
    """

    def __init__(
        self,
        llm=None,  # LLM 인스턴스 (선택사항)
        chunk_size: int = 100000,  # 10만자 청크
        overlap_size: int = 5000,  # 5천자 겹침
        max_section_size=2000000,  # 🚀 200만자 지원으로 확장
    ):
        """
        🚀 200만자 지원 대용량 PDF 분석기 초기화

        Args:
            chunk_size: 청크 크기 (기본 10만자)
            overlap_size: 청크 간 겹침 크기 (기본 5천자)
            max_section_size: 최대 섹션 크기 (기본 200만자)
        """
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.max_section_size = max_section_size

        # 청킹 프로세서 초기화
        self.chunk_processor = IndependentChunkProcessor(
            chunk_size=chunk_size, overlap_size=overlap_size
        )

        logger.info(f"🚀 LargePDFAnalyzer 초기화 완료 (200만자 지원)")
        logger.info(f"   청크 크기: {chunk_size:,}자")
        logger.info(f"   겹침 크기: {overlap_size:,}자")
        logger.info(f"   최대 섹션: {max_section_size:,}자")

        # AI 에이전트들 초기화
        self.llm = llm

        # Manus agent import 처리
        try:
            from app.agent.manus import Manus

            self.manus_agent = Manus(llm=self.llm)
        except ImportError:
            logger.warning(
                "⚠️ Manus agent를 찾을 수 없습니다. 일부 기능이 제한될 수 있습니다."
            )
            self.manus_agent = None

        # 분석 결과 저장용
        self.analysis_results = {}

        logger.info("✅ 대용량 PDF 분석 시스템 초기화 완료!")
        logger.info(f"📊 설정값: 청크크기={chunk_size:,}자, 겹침={overlap_size:,}자")

    async def extract_raw_text_only(
        self,
        pdf_path: str,
        company_name: str = "분석대상회사",
        save_to_json: bool = True,
    ) -> Dict[str, Any]:
        """
        🚀 대용량 PDF 원문 추출 (AI 분석 없이 텍스트만)

        개선된 버전으로 대용량 PDF를 효율적으로 처리하고,
        목차 기반 청킹을 통해 구조화된 데이터를 제공합니다.

        Args:
            pdf_path: PDF 파일 경로 또는 URL
            company_name: 회사명
            save_to_json: JSON 파일로 저장 여부

        Returns:
            Dict: 추출 결과와 구조화된 청크 데이터
        """
        start_time = time.time()
        logger.info(f"📄 대용량 PDF 원문 추출 시작: {pdf_path}")

        # 🎯 결과 구조 표준화
        result = {
            "success": False,  # 🔧 성공/실패 명확히 표시
            "pdf_path": pdf_path,
            "company_name": company_name,
            "extraction_timestamp": datetime.now().isoformat(),
            "error": None,  # 🔧 오류 정보 필드 추가
            "metadata": {},
            "raw_content": None,  # 🔧 raw_content 구조 명확히 정의
            "content_preview": "",
            "saved_file": None,
        }

        try:
            logger.info("📖 대용량 PDF 텍스트 추출 중...")

            # 1️⃣ PDF 전체 텍스트 추출
            full_text = ""
            extraction_method = "unknown"

            try:
                # 🔧 URL과 로컬 파일 구분하여 처리 - _direct_pdf_extraction 직접 호출
                pdf_result = await self._direct_pdf_extraction(pdf_path)

                if pdf_result.get("success"):
                    full_text = pdf_result.get("full_text", "")
                    extraction_method = pdf_result.get("extraction_method", "unknown")
                    logger.info(f"✅ PDF 추출 성공 (방법: {extraction_method})")
                else:
                    error_msg = pdf_result.get("error", "PDF 추출 실패")
                    logger.error(f"❌ PDF 추출 실패: {error_msg}")
                    result["error"] = error_msg
                    return result

            except Exception as e:
                error_msg = f"PDF 처리 중 오류: {str(e)}"
                logger.error(f"❌ {error_msg}")
                result["error"] = error_msg
                return result

            # 텍스트가 비어있는지 확인
            if not full_text or len(full_text.strip()) < 100:
                error_msg = f"추출된 텍스트가 너무 짧습니다: {len(full_text)}자"
                logger.warning(f"⚠️ {error_msg}")
                result["error"] = error_msg
                return result

            # 2️⃣ 목차 기반 청킹 시도
            contextual_chunks = []
            chunking_method = "none"

            try:
                logger.info("🔖 PDF 목차 기반 청킹 시도...")

                # 목차 추출 시도
                table_of_contents = (
                    await self.chunk_processor.extract_pdf_table_of_contents(pdf_path)
                )

                if table_of_contents:
                    # 목차가 있는 경우
                    contextual_chunks = self.chunk_processor.chunk_by_table_of_contents(
                        full_text, table_of_contents
                    )
                    chunking_method = "table_of_contents"
                    logger.info(
                        f"📑 목차 기반 청킹 완료: {len(contextual_chunks)}개 청크"
                    )
                else:
                    # 목차가 없는 경우 스마트 청킹
                    contextual_chunks = self.chunk_processor.smart_chunk_text(
                        full_text, preserve_sections=True
                    )
                    chunking_method = "smart_chunk"
                    logger.info(f"🤖 스마트 청킹 완료: {len(contextual_chunks)}개 청크")

                if contextual_chunks:
                    logger.info(f"✅ 청킹 성공: {len(contextual_chunks)}개 청크 생성")

                    # 목차 구조 로그 출력
                    toc_chunks = [
                        c
                        for c in contextual_chunks
                        if c.get("chunk_type") == "toc_based"
                    ]
                    if toc_chunks:
                        logger.info("📑 목차 구조:")
                        for chunk in toc_chunks[:5]:  # 처음 5개만 출력
                            level = chunk.get("metadata", {}).get("toc_level", 1)
                            title = chunk.get("section_title", "제목없음")
                            length = chunk.get("content_length", 0)
                            indent = "  " * (level - 1)
                            logger.info(f"  {indent}📄 {title} ({length:,}자)")
                        if len(toc_chunks) > 5:
                            logger.info(f"  ... 외 {len(toc_chunks) - 5}개 목차 청크")
                else:
                    logger.info("📄 목차가 없거나 목차 기반 청킹 실패")
                    chunking_method = "no_toc_available"

            except Exception as e:
                logger.warning(f"⚠️ 목차 기반 청킹 중 오류: {e}")
                chunking_method = "error_fallback"

            # 3️⃣ 결과 구조 생성
            # 🔧 raw_content 구조 명확히 정의
            result["raw_content"] = {
                "full_text": full_text,
                "text_length": len(full_text),
                "note": "원문 그대로 추출됨 (AI 분석/요약 없음)",
                # 🔖 목차 기반 청킹 정보 추가
                "contextual_chunks": contextual_chunks,
                "chunking_applied": len(contextual_chunks) > 0,
                "chunking_method": chunking_method,
                "total_chunks": len(contextual_chunks),
                "chunk_types": (
                    list(
                        set(
                            chunk.get("chunk_type", "unknown")
                            for chunk in contextual_chunks
                        )
                    )
                    if contextual_chunks
                    else []
                ),
                "toc_available": any(
                    chunk.get("chunk_type") == "toc_based"
                    for chunk in contextual_chunks
                ),
                "chunk_summary": {
                    "toc_based_chunks": len(
                        [
                            c
                            for c in contextual_chunks
                            if c.get("chunk_type") == "toc_based"
                        ]
                    ),
                    "fallback_chunks": len(
                        [
                            c
                            for c in contextual_chunks
                            if c.get("chunk_type") in ["toc_fallback", "toc_split"]
                        ]
                    ),
                    "average_chunk_size": (
                        sum(c.get("content_length", 0) for c in contextual_chunks)
                        // len(contextual_chunks)
                        if contextual_chunks
                        else 0
                    ),
                },
            }

            # 메타데이터 생성
            result["metadata"] = {
                "original_file": pdf_path,
                "company_name": company_name,
                "total_text_length": len(full_text),
                "extraction_method": extraction_method,
                "chunking_method": chunking_method,
                "chunk_count": len(contextual_chunks),
                "processing_time_seconds": time.time() - start_time,
                "creation_timestamp": datetime.now().isoformat(),
                "has_table_of_contents": any(
                    chunk.get("chunk_type") == "toc_based"
                    for chunk in contextual_chunks
                ),
            }

            # 내용 미리보기 생성 (처음 500자)
            result["content_preview"] = (
                full_text[:500] + "..." if len(full_text) > 500 else full_text
            )

            # 4️⃣ JSON 파일 저장 (옵션)
            if save_to_json:
                try:
                    # 저장용 데이터 준비
                    save_data = {
                        "extraction_info": {
                            "pdf_path": pdf_path,
                            "company_name": company_name,
                            "extraction_timestamp": result["extraction_timestamp"],
                            "processing_time": result["metadata"][
                                "processing_time_seconds"
                            ],
                        },
                        "metadata": result["metadata"],
                        "raw_text": full_text,
                        "contextual_chunks": contextual_chunks,
                        "content_preview": result["content_preview"],
                    }

                    # 파일명 생성
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    safe_company_name = "".join(
                        c for c in company_name if c.isalnum() or c in (" ", "-", "_")
                    ).rstrip()
                    filename = f"pdf_raw_extract_{safe_company_name}_{timestamp}.json"

                    results_dir = "results"
                    if not os.path.exists(results_dir):
                        os.makedirs(results_dir)

                    filepath = os.path.join(results_dir, filename)

                    # UTF-8 인코딩으로 저장
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(save_data, f, ensure_ascii=False, indent=2)

                    result["saved_file"] = filepath
                    logger.info(f"💾 추출 결과 저장: {filepath}")

                except Exception as e:
                    logger.warning(f"⚠️ JSON 저장 실패: {e}")

            # 🔧 성공 상태로 설정
            result["success"] = True
            logger.info(
                f"✅ 원문 추출 완료: {len(full_text):,}자 (처리시간: {time.time() - start_time:.1f}초)"
            )

            return result

        except Exception as e:
            error_msg = f"PDF 원문 추출 실패: {str(e)}"
            logger.error(f"❌ {error_msg}")
            result["error"] = error_msg
            result["success"] = False
            return result

    async def analyze_large_report(
        self,
        pdf_path: str,
        report_type: str = "사업보고서",
        company_name: str = "",
        save_directory: str = "results",
    ) -> Dict[str, Any]:
        """
        대용량 보고서 전체 분석 메인 함수

        이 함수는 대용량 PDF 보고서를 처음부터 끝까지 완전히 분석해요:
        1. PDF에서 전체 텍스트 추출
        2. 보고서 구조 자동 파악
        3. 섹션별 스마트 분할
        4. 각 섹션 AI 전문 분석
        5. 통합 결과 생성
        6. JSON 파일로 저장

        Args:
            pdf_path: 분석할 PDF 파일 경로
            report_type: 보고서 종류 ("사업보고서", "분기보고서", "반기보고서" 등)
            company_name: 회사명 (자동 추출도 가능)
            save_directory: 결과 저장 폴더

        Returns:
            Dict: 전체 분석 결과와 저장 경로 정보
        """
        start_time = datetime.now()
        logger.info(f"📈 대용량 {report_type} 분석 시작: {pdf_path}")

        # 결과 저장용 구조 초기화
        analysis_results = {
            "metadata": {
                "pdf_path": pdf_path,
                "report_type": report_type,
                "company_name": company_name,
                "analysis_start_time": start_time.isoformat(),
                "success": False,
                "total_processing_time": None,
                "total_text_length": 0,
                "total_chunks": 0,
                "analyzer_version": "LargePDFAnalyzer_v1.0",
            },
            "extraction_info": {},
            "structure_analysis": {},
            "section_analyses": {},
            "integrated_summary": {},
            "key_insights": {},
            "raw_content": {},
        }

        try:
            # 🔍 1단계: PDF 전체 텍스트 추출
            logger.info("📖 1단계: 대용량 PDF 텍스트 추출 중...")
            extraction_result = await self._extract_full_text(pdf_path)

            if not extraction_result["success"]:
                analysis_results["metadata"]["error"] = extraction_result["error"]
                return analysis_results

            full_text = extraction_result["full_text"]
            analysis_results["extraction_info"] = extraction_result
            analysis_results["metadata"]["total_text_length"] = len(full_text)

            logger.info(
                f"✅ 텍스트 추출 완료: {len(full_text):,}자 (약 {len(full_text)/10000:.1f}만 글자)"
            )

            # 🧩 2단계: 보고서 구조 분석 및 섹션 분할
            logger.info("🔍 2단계: 보고서 구조 분석 및 스마트 분할 중...")
            structure_result = await self._analyze_report_structure(
                full_text, report_type
            )
            analysis_results["structure_analysis"] = structure_result

            # 📊 3단계: 섹션별 전문 분석
            logger.info("🔬 3단계: 섹션별 AI 전문 분석 수행 중...")
            section_results = await self._analyze_sections_professionally(
                structure_result["sections"], report_type, company_name
            )
            analysis_results["section_analyses"] = section_results
            analysis_results["metadata"]["total_chunks"] = len(
                structure_result["sections"]
            )

            # 🎯 4단계: 통합 분석 및 인사이트 추출
            logger.info("🎯 4단계: 통합 분석 및 핵심 인사이트 추출 중...")
            integrated_result = await self._create_integrated_analysis(
                section_results, report_type, company_name
            )
            analysis_results["integrated_summary"] = integrated_result

            # 💎 5단계: 핵심 인사이트 추출
            logger.info("💎 5단계: 핵심 투자 인사이트 추출 중...")
            key_insights = await self._extract_key_insights(
                analysis_results, report_type, company_name
            )
            analysis_results["key_insights"] = key_insights

            # 📁 6단계: 원본 텍스트 저장 (선택사항)
            analysis_results["raw_content"] = {
                "full_text_preview": (
                    full_text[:5000] + "..." if len(full_text) > 5000 else full_text
                ),
                "full_text_length": len(full_text),
                "note": "전체 원본 텍스트는 크기상 생략됨 (요청시 별도 제공 가능)",
            }

            # ⏱️ 처리 시간 계산
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            analysis_results["metadata"]["analysis_end_time"] = end_time.isoformat()
            analysis_results["metadata"][
                "total_processing_time"
            ] = f"{processing_time:.2f}초"
            analysis_results["metadata"]["success"] = True

            logger.info(f"🎉 대용량 PDF 분석 완료! (처리시간: {processing_time:.1f}초)")

            # 💾 7단계: JSON 파일로 저장
            save_path = await self._save_analysis_results(
                analysis_results, save_directory, company_name, report_type
            )
            analysis_results["metadata"]["save_path"] = save_path

            return analysis_results

        except Exception as e:
            logger.error(f"❌ 대용량 PDF 분석 중 오류 발생: {str(e)}")
            analysis_results["metadata"]["error"] = f"분석 중 오류: {str(e)}"
            analysis_results["metadata"]["success"] = False
            return analysis_results

    async def _extract_full_text(self, pdf_path: str) -> Dict[str, Any]:
        """
        PDF에서 전체 텍스트를 추출하는 함수

        100만 글자도 안전하게 처리할 수 있도록 최적화되어 있어요.
        여러 PDF 라이브러리를 시도해서 가장 좋은 결과를 얻습니다.
        URL PDF도 자동으로 다운로드해서 처리합니다.

        Args:
            pdf_path: PDF 파일 경로 또는 URL

        Returns:
            Dict: 추출 결과와 메타데이터
        """
        try:
            # 🌐 URL PDF인지 확인하고 다운로드
            actual_pdf_path = await self._handle_pdf_source(pdf_path)
            if not actual_pdf_path:
                return {
                    "success": False,
                    "error": f"PDF 소스를 처리할 수 없습니다: {pdf_path}",
                }

            # 🚀 직접 PDF 텍스트 추출 (PDFReader 의존성 제거)
            logger.info(f"📄 대용량 PDF 직접 추출 시도: {actual_pdf_path}")
            pdf_result = await self._direct_pdf_extraction(actual_pdf_path)

            if not pdf_result.get("success", False):
                return {
                    "success": False,
                    "error": f"PDF 텍스트 추출 실패: {pdf_result.get('error', '알 수 없는 오류')}",
                }

            full_text = pdf_result.get("full_text", "")
            if not full_text or len(full_text.strip()) < 1000:
                return {
                    "success": False,
                    "error": "추출된 텍스트가 너무 짧거나 비어있습니다",
                }

            return {
                "success": True,
                "full_text": full_text,
                "text_length": len(full_text),
                "extraction_method": pdf_result.get(
                    "extraction_method", "direct_large_pdf"
                ),
                "pages_processed": pdf_result.get("pages", []),
                "total_pages": len(pdf_result.get("pages", [])),
                "original_source": pdf_path,
                "processed_file": actual_pdf_path,
            }

        except Exception as e:
            logger.error(f"❌ PDF 텍스트 추출 중 오류: {str(e)}")
            return {"success": False, "error": f"PDF 텍스트 추출 오류: {str(e)}"}

    async def _handle_pdf_source(self, pdf_path: str) -> Optional[str]:
        """
        🌐 PDF 소스 처리 (로컬 파일 또는 URL 직접 처리)

        URL인 경우 메모리에서 직접 처리하고, 로컬 파일인 경우 그대로 반환합니다.
        다운로드 없이 스트림으로 처리해서 더 빠르고 효율적입니다.

        Args:
            pdf_path: PDF 파일 경로 또는 URL

        Returns:
            str: 처리 가능한 경로 또는 URL (실패시 None)
        """
        try:
            # URL인지 확인
            if pdf_path.startswith(("http://", "https://")):
                logger.info(f"🌐 URL PDF 감지, 메모리에서 직접 처리: {pdf_path}")
                # URL 그대로 반환 - _direct_pdf_extraction에서 직접 처리
                return pdf_path

            # 로컬 파일인지 확인
            elif os.path.exists(pdf_path):
                logger.info(f"📁 로컬 PDF 파일 확인: {pdf_path}")
                return pdf_path

            # 파일을 찾을 수 없음
            else:
                logger.error(f"❌ PDF 파일을 찾을 수 없습니다: {pdf_path}")
                return None

        except Exception as e:
            logger.error(f"❌ PDF 소스 처리 중 오류: {str(e)}")
            return None

    async def _download_pdf_from_url(self, url: str) -> Optional[io.BytesIO]:
        """
        URL에서 PDF 파일을 다운로드하여 메모리 스트림으로 반환

        Args:
            url: PDF 파일 URL

        Returns:
            Optional[io.BytesIO]: 다운로드된 PDF 데이터 스트림 또는 None (실패시)
        """
        try:
            logger.info(f"🌐 PDF URL 다운로드 시작: {url}")

            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        pdf_data = await response.read()
                        pdf_stream = io.BytesIO(pdf_data)
                        logger.info(f"✅ PDF 다운로드 완료: {len(pdf_data):,} bytes")
                        return pdf_stream
                    else:
                        logger.error(f"❌ PDF 다운로드 실패: HTTP {response.status}")
                        return None

        except Exception as e:
            logger.error(f"❌ PDF URL 다운로드 오류: {e}")
            return None

    async def _direct_pdf_extraction(self, pdf_path: str) -> Dict[str, Any]:
        """
        🚀 PDFReader 없이 직접 PDF 텍스트 추출 (대용량 특화)
        로컬 파일과 URL PDF 모두 지원 (다운로드 없이 메모리 처리)

        🔧 ZIP 파일 감지 및 처리 로직 추가됨
        (DART API에서 ZIP 압축 파일로 문서를 제공하는 경우를 대응해요)

        Args:
            pdf_path: PDF 파일 경로 또는 URL

        Returns:
            Dict: 추출 결과
        """
        import io

        # PDF 데이터 준비 (로컬 파일 또는 URL)
        try:
            if pdf_path.startswith(("http://", "https://")):
                # 🌐 URL PDF - 메모리에서 직접 처리
                pdf_data = await self._download_pdf_from_url(pdf_path)
                if not pdf_data:
                    return {"success": False, "error": f"URL PDF 로드 실패: {pdf_path}"}
            else:
                # 📁 로컬 파일 - 파일에서 읽기
                with open(pdf_path, "rb") as file:
                    pdf_data = io.BytesIO(file.read())

            # 🔧 ZIP 파일 감지 (DART API 대응)
            pdf_data.seek(0)
            file_header = pdf_data.read(4)
            pdf_data.seek(0)

            # ZIP 파일 매직 넘버 확인 (b'PK\x03\x04' 또는 다른 ZIP 변형들)
            if file_header.startswith(b"PK"):
                logger.warning("🚨 ZIP 압축 파일 감지 - PDF 추출 불가")
                return {
                    "success": False,
                    "error": "ZIP 압축 파일입니다. DART API 문서는 압축 해제 후 처리되어야 합니다.",
                    "file_type": "ZIP",
                    "suggestion": "EnhancedDartDataCollector의 ZIP 처리 로직을 사용하세요",
                }

            # PDF 파일 매직 넘버 확인
            if not file_header.startswith(b"%PDF"):
                logger.warning(f"⚠️ PDF 형식이 아닌 파일 감지: {file_header}")
                return {
                    "success": False,
                    "error": f"PDF 형식이 아닙니다. 파일 헤더: {file_header}",
                    "file_type": "Unknown",
                }

        except Exception as e:
            return {"success": False, "error": f"PDF 데이터 준비 실패: {str(e)}"}

        # 지원하는 PDF 라이브러리들 (우선순위 순서)
        extraction_methods = [
            ("pdfplumber", self._extract_with_pdfplumber),
            ("pymupdf", self._extract_with_pymupdf),
            ("pypdf", self._extract_with_pypdf),
        ]

        # 각 라이브러리를 순차 시도
        for method_name, method_func in extraction_methods:
            try:
                pdf_data.seek(0)  # 스트림 포지션 초기화
                result = await method_func(pdf_data)

                if result.get("success", False) and result.get("full_text", "").strip():
                    logger.info(f"✅ 대용량 PDF 추출 성공 (방법: {method_name})")
                    result["extraction_method"] = f"direct_{method_name}"
                    result["source_type"] = (
                        "URL"
                        if pdf_path.startswith(("http://", "https://"))
                        else "로컬파일"
                    )
                    return result

            except Exception as e:
                logger.warning(f"⚠️ {method_name} 추출 실패: {e}")
                continue

        # 모든 방법 실패
        return {
            "success": False,
            "error": "모든 PDF 추출 방법 실패 - 파일이 손상되었거나 지원되지 않는 형식",
            "full_text": "",
        }

    async def _extract_with_pdfplumber(self, pdf_data: io.BytesIO) -> Dict[str, Any]:
        """pdfplumber로 PDF 텍스트 추출"""
        try:
            import pdfplumber

            full_text = ""
            pages = []

            with pdfplumber.open(pdf_data) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        page_text = page.extract_text() or ""
                        full_text += page_text + "\n"
                        pages.append(f"페이지 {page_num}: {len(page_text)}자")
                    except Exception as e:
                        logger.warning(f"⚠️ 페이지 {page_num} 추출 실패: {e}")
                        continue

            return {
                "success": True,
                "full_text": full_text.strip(),
                "pages": pages,
                "total_pages": len(pages),
            }

        except ImportError:
            return {"success": False, "error": "pdfplumber 라이브러리가 설치되지 않음"}
        except Exception as e:
            return {"success": False, "error": f"pdfplumber 추출 오류: {str(e)}"}

    async def _extract_with_pymupdf(self, pdf_data: io.BytesIO) -> Dict[str, Any]:
        """PyMuPDF(fitz)로 PDF 텍스트 추출"""
        try:
            import fitz  # PyMuPDF

            full_text = ""
            pages = []

            doc = fitz.open(stream=pdf_data.read(), filetype="pdf")

            for page_num in range(doc.page_count):
                try:
                    page = doc[page_num]
                    page_text = page.get_text() or ""
                    full_text += page_text + "\n"
                    pages.append(f"페이지 {page_num + 1}: {len(page_text)}자")
                except Exception as e:
                    logger.warning(f"⚠️ 페이지 {page_num + 1} 추출 실패: {e}")
                    continue

            doc.close()

            return {
                "success": True,
                "full_text": full_text.strip(),
                "pages": pages,
                "total_pages": len(pages),
            }

        except ImportError:
            return {"success": False, "error": "PyMuPDF 라이브러리가 설치되지 않음"}
        except Exception as e:
            return {"success": False, "error": f"PyMuPDF 추출 오류: {str(e)}"}

    async def _extract_with_pypdf(self, pdf_data: io.BytesIO) -> Dict[str, Any]:
        """PyPDF로 PDF 텍스트 추출"""
        try:
            from pypdf import PdfReader

            full_text = ""
            pages = []

            reader = PdfReader(pdf_data)

            for page_num, page in enumerate(reader.pages, 1):
                try:
                    page_text = page.extract_text() or ""
                    full_text += page_text + "\n"
                    pages.append(f"페이지 {page_num}: {len(page_text)}자")
                except Exception as e:
                    logger.warning(f"⚠️ 페이지 {page_num} 추출 실패: {e}")
                    continue

            return {
                "success": True,
                "full_text": full_text.strip(),
                "pages": pages,
                "total_pages": len(pages),
            }

        except ImportError:
            return {"success": False, "error": "PyPDF 라이브러리가 설치되지 않음"}
        except Exception as e:
            return {"success": False, "error": f"PyPDF 추출 오류: {str(e)}"}

    async def _analyze_report_structure(
        self, full_text: str, report_type: str
    ) -> Dict[str, Any]:
        """
        보고서 구조를 AI로 분석하고 의미있는 섹션으로 분할

        이 함수는 보고서의 구조를 파악해서 각 섹션을 식별해요:
        - 재무제표, 주석, 경영진 분석, 위험요인 등
        - 각 섹션의 중요도와 분석 우선순위 결정
        - 청크 단위로 효율적 분할

        Args:
            full_text: 전체 텍스트
            report_type: 보고서 종류

        Returns:
            Dict: 구조 분석 결과와 섹션 목록
        """
        logger.info("🏗️ 보고서 구조 분석 시작...")

        # 먼저 텍스트를 청크로 분할
        chunks = self.chunk_processor.smart_chunk_text(
            full_text, preserve_sections=True
        )
        logger.info(f"📊 총 {len(chunks)}개 청크 생성 완료")

        # AI로 전체 구조 분석
        structure_prompt = f"""
다음은 {report_type}의 전체 텍스트입니다. 이 보고서의 구조를 분석해서 주요 섹션들을 식별해 주세요.

텍스트 미리보기 (처음 3000자):
{full_text[:3000]}...

전체 텍스트 길이: {len(full_text):,}자

분석 요청:
1. 이 보고서에 포함된 주요 섹션들 식별
2. 각 섹션의 중요도 평가 (1-5점)
3. 섹션별 키워드와 특징
4. 재무분석 관점에서의 우선순위

아래 형태로 답변해 주세요:
- 섹션명: [섹션 이름]
- 중요도: [1-5점]
- 키워드: [주요 키워드들]
- 특징: [해당 섹션의 특징과 내용]
"""

        try:
            structure_analysis = await self.llm.ask(
                [{"role": "user", "content": structure_prompt}]
            )

            # 청크에 구조 정보 추가
            enhanced_chunks = []
            for i, chunk in enumerate(chunks):
                chunk["chunk_id"] = i + 1
                chunk["analysis_priority"] = "medium"  # 기본값
                chunk["section_type"] = "unknown"
                enhanced_chunks.append(chunk)

            return {
                "success": True,
                "total_chunks": len(enhanced_chunks),
                "sections": enhanced_chunks,
                "structure_analysis": structure_analysis,
                "processing_info": {
                    "chunk_size": self.chunk_processor.chunk_size,
                    "overlap_size": self.chunk_processor.overlap_size,
                    "total_text_length": len(full_text),
                },
            }

        except Exception as e:
            logger.error(f"❌ 보고서 구조 분석 실패: {str(e)}")
            # 실패해도 기본 청크로 진행
            basic_chunks = []
            for i, chunk in enumerate(chunks):
                chunk["chunk_id"] = i + 1
                chunk["analysis_priority"] = "medium"
                chunk["section_type"] = "basic_chunk"
                basic_chunks.append(chunk)

            return {
                "success": False,
                "error": str(e),
                "total_chunks": len(basic_chunks),
                "sections": basic_chunks,
                "structure_analysis": "구조 분석 실패 - 기본 청크 처리로 진행",
            }

    async def _analyze_sections_professionally(
        self, sections: List[Dict], report_type: str, company_name: str
    ) -> Dict[str, Any]:
        """
        각 섹션을 전문적으로 AI 분석

        각 청크를 재무 전문가 관점에서 깊이 있게 분석해요:
        - 핵심 수치와 비율 추출
        - 트렌드와 변화 분석
        - 위험요인과 기회요인 식별
        - 투자 관점에서의 시사점

        Args:
            sections: 분할된 섹션 목록
            report_type: 보고서 종류
            company_name: 회사명

        Returns:
            Dict: 섹션별 분석 결과
        """
        logger.info(f"🔬 {len(sections)}개 섹션 전문 분석 시작...")

        section_results = {}
        failed_sections = []

        # 각 섹션을 순차적으로 분석 (병렬 처리는 리소스 부족시 문제가 될 수 있음)
        for i, section in enumerate(sections, 1):
            try:
                logger.info(
                    f"📊 섹션 {i}/{len(sections)} 분석 중... (길이: {len(section['content']):,}자)"
                )

                # 전문 분석 프롬프트 생성
                analysis_prompt = self._create_professional_analysis_prompt(
                    section["content"], report_type, company_name, i, len(sections)
                )

                # AI 분석 수행
                analysis_result = await self.llm.ask(
                    [{"role": "user", "content": analysis_prompt}]
                )

                # 결과 저장
                section_results[f"section_{i}"] = {
                    "chunk_id": section.get("chunk_id", i),
                    "content_length": len(section["content"]),
                    "content_preview": (
                        section["content"][:500] + "..."
                        if len(section["content"]) > 500
                        else section["content"]
                    ),
                    "analysis": analysis_result,
                    "metadata": section.get("metadata", {}),
                    "analysis_timestamp": datetime.now().isoformat(),
                }

                logger.info(f"✅ 섹션 {i} 분석 완료")

                # 메모리 사용량 관리를 위한 잠깐 대기
                if i % 5 == 0:
                    await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"❌ 섹션 {i} 분석 실패: {str(e)}")
                failed_sections.append(
                    {
                        "section_id": i,
                        "error": str(e),
                        "content_length": len(section.get("content", "")),
                    }
                )

        return {
            "success": True,
            "total_sections_analyzed": len(section_results),
            "failed_sections": failed_sections,
            "section_analyses": section_results,
            "analysis_summary": {
                "total_sections": len(sections),
                "successful_analyses": len(section_results),
                "failed_analyses": len(failed_sections),
                "success_rate": f"{len(section_results)/len(sections)*100:.1f}%",
            },
        }

    def _create_professional_analysis_prompt(
        self,
        content: str,
        report_type: str,
        company_name: str,
        section_num: int,
        total_sections: int,
    ) -> str:
        """
        전문적인 분석을 위한 프롬프트 생성

        이 함수는 각 섹션을 재무 전문가 수준으로 분석하기 위한
        상세하고 전문적인 프롬프트를 만들어요.
        """
        return f"""
당신은 경험이 풍부한 재무분석 전문가입니다. 다음 {report_type}의 섹션을 전문적으로 분석해 주세요.

회사명: {company_name}
보고서 종류: {report_type}
분석 대상: 섹션 {section_num}/{total_sections}

분석할 텍스트:
{content}

전문 분석 요청사항:

1. 📊 핵심 수치 분석:
   - 중요한 재무 수치나 비율 추출
   - 전년 대비 변화율이나 트렌드
   - 특이사항이나 주목할 만한 수치

2. 💼 비즈니스 인사이트:
   - 이 섹션에서 드러나는 사업 현황
   - 경영진의 판단이나 전략
   - 시장 환경이나 경쟁 상황

3. ⚠️ 위험요인 및 기회요인:
   - 잠재적 리스크나 우려사항
   - 성장 기회나 긍정적 요소
   - 투자자가 주목해야 할 포인트

4. 🎯 핵심 요약:
   - 이 섹션의 가장 중요한 3가지 포인트
   - 투자 의사결정에 미치는 영향
   - 다른 섹션과의 연관성

분석 결과를 구조적이고 전문적으로 정리해서 제시해 주세요.
"""

    async def _create_integrated_analysis(
        self, section_results: Dict[str, Any], report_type: str, company_name: str
    ) -> Dict[str, Any]:
        """
        섹션별 분석 결과를 통합해서 종합적인 분석 리포트 생성

        이 함수는 개별 섹션 분석들을 연결해서 전체적인 그림을 그려요:
        - 섹션 간 상호 연관성 분석
        - 전체적인 투자 테마 도출
        - 종합적인 투자 의견 제시
        """
        logger.info("🎯 통합 분석 및 종합 리포트 생성 중...")

        try:
            # 모든 섹션 분석 결과 요약
            section_summaries = []
            for section_key, section_data in section_results.get(
                "section_analyses", {}
            ).items():
                summary = f"섹션 {section_data['chunk_id']}: {section_data['analysis'][:300]}..."
                section_summaries.append(summary)

            integrated_prompt = f"""
당신은 최고 수준의 투자분석가입니다. 다음 {report_type}의 모든 섹션 분석 결과를 종합해서
완전한 투자 리포트를 작성해 주세요.

회사명: {company_name}
보고서 종류: {report_type}
분석된 총 섹션 수: {len(section_summaries)}

각 섹션 분석 요약:
{chr(10).join(section_summaries)}

종합 분석 요청:

1. 🏢 기업 전체 현황:
   - 전반적인 재무 건전성 평가
   - 주요 사업부문별 성과
   - 경영진의 전략 방향성

2. 📈 투자 포인트:
   - 핵심 투자 매력 요소
   - 성장 동력과 수익성 전망
   - 동종업계 대비 경쟁력

3. ⚠️ 리스크 요인:
   - 주요 위험 요소들
   - 불확실성과 도전 과제
   - 리스크 관리 방안

4. 💡 투자 의견:
   - 종합적인 투자 추천 의견
   - 목표 주가나 밸류에이션
   - 향후 모니터링 포인트

5. 📊 핵심 지표 요약:
   - 가장 중요한 재무 지표들
   - 핵심 성과 지표 (KPI)
   - 주요 변화 트렌드

전문적이고 실용적인 투자 리포트로 작성해 주세요.
"""

            integrated_analysis = await self.llm.ask(
                [{"role": "user", "content": integrated_prompt}]
            )

            return {
                "success": True,
                "integrated_report": integrated_analysis,
                "sections_integrated": len(section_summaries),
                "integration_timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ 통합 분석 실패: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "fallback_summary": "통합 분석 실패 - 개별 섹션 분석 결과를 참조하세요",
            }

    async def _extract_key_insights(
        self, analysis_results: Dict[str, Any], report_type: str, company_name: str
    ) -> Dict[str, Any]:
        """
        전체 분석에서 핵심 투자 인사이트를 추출

        마지막 단계에서 가장 중요한 인사이트들만 골라내요:
        - 투자자가 꼭 알아야 할 핵심 팩트
        - 주가에 영향을 줄 수 있는 요소들
        - 간단명료한 투자 포인트 정리
        """
        logger.info("💎 핵심 투자 인사이트 추출 중...")

        try:
            insights_prompt = f"""
당신은 투자 전문가입니다. 다음 {company_name}의 {report_type} 분석 결과에서
투자자가 반드시 알아야 할 핵심 인사이트만 간단명료하게 추출해 주세요.

분석 결과 요약:
- 총 텍스트 길이: {analysis_results['metadata']['total_text_length']:,}자
- 분석된 섹션 수: {analysis_results['metadata']['total_chunks']}개
- 통합 분석: {analysis_results.get('integrated_summary', {}).get('integrated_report', '없음')[:500]}...

핵심 인사이트 추출 요청:

1. 🎯 투자 핵심 포인트 (3가지):
   - 가장 중요한 투자 매력 요소들
   - 간단명료하게 한 문장씩

2. ⚠️ 주요 리스크 (3가지):
   - 가장 우려되는 위험 요소들
   - 투자 전 반드시 고려해야 할 사항들

3. 📊 핵심 수치:
   - 가장 중요한 재무 지표 3-5개
   - 투자 판단의 근거가 되는 수치들

4. 💡 한 줄 투자 의견:
   - 이 분석을 한 문장으로 요약
   - 투자자에게 주는 명확한 메시지

간결하고 임팩트 있게 정리해 주세요.
"""

            key_insights = await self.llm.ask(
                [{"role": "user", "content": insights_prompt}]
            )

            return {
                "success": True,
                "key_insights": key_insights,
                "extraction_timestamp": datetime.now().isoformat(),
                "source_sections": analysis_results["metadata"]["total_chunks"],
            }

        except Exception as e:
            logger.error(f"❌ 핵심 인사이트 추출 실패: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "fallback_insights": "핵심 인사이트 추출 실패 - 통합 분석 결과를 참조하세요",
            }

    async def _save_analysis_results(
        self,
        analysis_results: Dict[str, Any],
        save_directory: str,
        company_name: str,
        report_type: str,
    ) -> str:
        """
        분석 결과를 구조화된 JSON 파일로 저장

        분석 결과를 체계적으로 정리해서 JSON 파일로 저장해요:
        - 읽기 쉬운 구조로 정리
        - 타임스탬프와 메타데이터 포함
        - 파일명에 회사명과 날짜 포함
        """
        try:
            # 저장 디렉토리 생성
            os.makedirs(save_directory, exist_ok=True)

            # 파일명 생성 (회사명-보고서종류-날짜-시간)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            company_safe = (
                re.sub(r"[^\w\-_.]", "_", company_name) if company_name else "UNKNOWN"
            )
            report_safe = re.sub(r"[^\w\-_.]", "_", report_type)

            filename = (
                f"large_pdf_analysis-{company_safe}-{report_safe}-{timestamp}.json"
            )
            file_path = os.path.join(save_directory, filename)

            # JSON 파일로 저장 (한국어 지원, 보기 좋게 정렬)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(
                    analysis_results,
                    f,
                    ensure_ascii=False,
                    indent=2,
                    default=str,  # datetime 객체 등을 문자열로 변환
                )

            logger.info(f"💾 분석 결과 저장 완료: {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"❌ 분석 결과 저장 실패: {str(e)}")
            return f"저장 실패: {str(e)}"

    async def _save_raw_text_results(
        self, result: Dict[str, Any], company_name: str
    ) -> str:
        """
        원문 추출 결과를 JSON 파일로 저장하는 함수

        Args:
            result: 추출 결과 딕셔너리
            company_name: 회사명

        Returns:
            str: 저장된 파일 경로
        """
        try:
            # 저장 디렉토리 생성
            save_directory = "results"
            os.makedirs(save_directory, exist_ok=True)

            # 파일명 생성 (원문추출 전용)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_company_name = "".join(
                c for c in company_name if c.isalnum() or c in " -_"
            ).strip()[:50]

            filename = f"PDF-RAW-{safe_company_name}-{timestamp}.json"
            save_path = os.path.join(save_directory, filename)

            # JSON 파일로 저장
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            logger.info(f"💾 원문 JSON 파일 저장 완료: {save_path}")
            return save_path

        except Exception as e:
            logger.error(f"❌ 원문 결과 저장 중 오류: {e}")
            return ""

    async def extract_pdf_table_of_contents(
        self,
        pdf_path: str,
        company_name: str = "분석대상회사",
        save_to_json: bool = True,
    ) -> Dict[str, Any]:
        """
        PDF에서 목차(Table of Contents)를 추출합니다.

        Args:
            pdf_path: PDF 파일 경로 또는 URL
            company_name: 회사명
            save_to_json: JSON 파일로 저장 여부

        Returns:
            Dict: 추출된 목차 정보
        """
        logger.info(f"📋 PDF 목차 추출 시작: {pdf_path}")

        result = {
            "success": False,
            "table_of_contents": [],
            "metadata": {
                "pdf_path": pdf_path,
                "company_name": company_name,
                "extraction_timestamp": datetime.now().isoformat(),
            },
        }

        try:
            # IndependentChunkProcessor를 사용해서 목차 추출
            toc_list = await self.chunk_processor.extract_pdf_table_of_contents(
                pdf_path
            )

            if toc_list:
                result["success"] = True
                result["table_of_contents"] = toc_list
                result["metadata"]["total_toc_items"] = len(toc_list)
                logger.info(f"✅ 목차 추출 성공: {len(toc_list)}개 항목")
            else:
                result["error"] = "목차를 찾을 수 없습니다"
                logger.warning("⚠️ PDF에서 목차를 찾을 수 없습니다")

        except Exception as e:
            error_msg = f"목차 추출 실패: {str(e)}"
            result["error"] = error_msg
            logger.error(f"❌ {error_msg}")

        return result

    async def _map_text_to_toc_sections(
        self,
        full_text: str,
        table_of_contents: List[Dict],
        max_section_size: int,
    ) -> Dict[str, str]:
        """
        전체 텍스트를 목차 구조에 따라 섹션별로 매핑합니다.

        Args:
            full_text: PDF 전체 텍스트
            table_of_contents: 목차 구조
            max_section_size: 각 섹션의 최대 크기

        Returns:
            Dict: {목차_제목: 섹션_내용} 딕셔너리
        """
        logger.info(f"📝 목차-텍스트 매핑 시작: {len(table_of_contents)}개 목차 항목")

        sections = {}

        try:
            for i, toc_item in enumerate(table_of_contents):
                section_title = toc_item.get("title", f"섹션_{i+1}")

                # 텍스트에서 해당 섹션 찾기
                title_pos = full_text.find(section_title)
                if title_pos == -1:
                    # 제목 변형으로 다시 시도
                    title_variations = [
                        section_title.replace(" ", ""),
                        section_title.replace(".", ""),
                        section_title.upper(),
                        section_title.lower(),
                    ]

                    for variation in title_variations:
                        title_pos = full_text.find(variation)
                        if title_pos != -1:
                            break

                if title_pos == -1:
                    logger.warning(
                        f"⚠️ 섹션 '{section_title}'을 텍스트에서 찾을 수 없습니다"
                    )
                    continue

                # 다음 섹션까지의 텍스트 추출
                next_pos = len(full_text)
                for j in range(i + 1, len(table_of_contents)):
                    next_title = table_of_contents[j].get("title", "")
                    next_title_pos = full_text.find(next_title, title_pos + 1)
                    if next_title_pos != -1:
                        next_pos = next_title_pos
                        break

                section_text = full_text[title_pos:next_pos].strip()

                # 섹션 크기 제한 적용
                if len(section_text) > max_section_size:
                    section_text = (
                        section_text[:max_section_size] + "...[내용 일부 생략]"
                    )

                if len(section_text) >= 100:  # 최소 길이 필터
                    sections[section_title] = section_text

            logger.info(f"✅ 목차-텍스트 매핑 완료: {len(sections)}개 섹션")

        except Exception as e:
            logger.error(f"❌ 목차-텍스트 매핑 실패: {e}")

        return sections

    async def create_pdf_dictionary_for_crewai(
        self,
        pdf_path: str,
        company_name: str = "분석대상회사",
        max_section_size: int = 1000000,  # 🚀 100만자로 확장!
    ) -> Dict[str, Any]:
        """
        🚀 CrewAI 전문가용 PDF 딕셔너리 생성기

        대용량 PDF를 목차별/섹션별 딕셔너리로 구조화해서
        CrewAI 전문가들이 필요한 부분만 선택적으로 가져와서 분석할 수 있게 해요!

        이게 바로 토큰 절약과 정확성 향상의 핵심이에요! 🎯

        Args:
            pdf_path: PDF 파일 경로 또는 URL
            company_name: 회사명
            max_section_size: 각 섹션의 최대 크기 (토큰 제한 고려) - 기본 100만자

        Returns:
            Dict: {
                "success": bool,
                "pdf_dictionary": Dict[str, str],  # {목차항목: 내용}
                "interface": PDFDictionaryInterface,  # CrewAI용 인터페이스
                "metadata": Dict,
                "error": str (실패 시)
            }
        """
        start_time = time.time()
        logger.info(f"🚀 {company_name} PDF 딕셔너리 생성 시작...")
        logger.info(f"   최대 섹션 크기: {max_section_size:,}자 (100만자 지원)")

        try:
            # 1️⃣ PDF 목차 추출
            logger.info("📋 1단계: PDF 목차 추출...")
            toc_result = await self.extract_pdf_table_of_contents(
                pdf_path=pdf_path, company_name=company_name, save_to_json=False
            )

            if not toc_result.get("success"):
                logger.warning("⚠️ 목차 추출 실패, 텍스트 기반 섹션 분할로 대체...")
                # 목차가 없는 경우 전체 텍스트를 기반으로 섹션 분할
                return await self._create_dictionary_without_toc(
                    pdf_path, company_name, max_section_size
                )

            # 2️⃣ 목차 기반으로 PDF를 섹션별로 분할
            logger.info("✂️ 2단계: 목차 기반 섹션 분할...")

            # PDF 전체 텍스트 추출
            full_text_result = await self.extract_raw_text_only(
                pdf_path=pdf_path, company_name=company_name, save_to_json=False
            )

            if not full_text_result.get("success"):
                raise Exception(
                    f"PDF 텍스트 추출 실패: {full_text_result.get('error')}"
                )

            full_text = full_text_result.get("raw_text", "")
            table_of_contents = toc_result.get("table_of_contents", [])

            # 3️⃣ 목차별로 텍스트를 매핑하여 딕셔너리 생성
            logger.info("📝 3단계: 목차-텍스트 매핑...")
            pdf_dictionary = await self._map_text_to_toc_sections(
                full_text=full_text,
                table_of_contents=table_of_contents,
                max_section_size=max_section_size,
            )

            # 4️⃣ 주석 섹션 별도 추출 및 추가
            logger.info("📝 4단계: 주석 섹션 추출...")
            footnote_sections = self._extract_footnote_sections(
                full_text, max_section_size
            )

            # 주석 섹션을 딕셔너리에 추가
            for footnote_title, footnote_content in footnote_sections.items():
                pdf_dictionary[f"[주석] {footnote_title}"] = footnote_content

            # 5️⃣ 메타데이터 생성
            metadata = {
                "company_name": company_name,
                "pdf_source": pdf_path,
                "creation_timestamp": datetime.now().isoformat(),
                "total_sections": len(pdf_dictionary),
                "toc_based_sections": len(pdf_dictionary) - len(footnote_sections),
                "footnote_sections": len(footnote_sections),
                "total_text_length": sum(
                    len(content) for content in pdf_dictionary.values()
                ),
                "avg_section_length": (
                    sum(len(content) for content in pdf_dictionary.values())
                    // len(pdf_dictionary)
                    if pdf_dictionary
                    else 0
                ),
                "max_section_size_limit": max_section_size,
                "processing_time": time.time() - start_time,
            }

            # 6️⃣ PDFDictionaryInterface 생성
            logger.info("🎯 5단계: PDF 딕셔너리 인터페이스 생성...")
            pdf_interface = PDFDictionaryInterface(
                pdf_dictionary=pdf_dictionary, metadata=metadata
            )

            # 7️⃣ 완성 로그
            logger.info(f"✅ PDF 딕셔너리 생성 완료!")
            logger.info(f"   📊 총 섹션: {len(pdf_dictionary)}개")
            logger.info(f"   📝 주석 섹션: {len(footnote_sections)}개")
            logger.info(f"   📄 총 텍스트: {metadata['total_text_length']:,}자")
            logger.info(f"   ⏱️ 처리시간: {metadata['processing_time']:.1f}초")

            return {
                "success": True,
                "pdf_dictionary": pdf_dictionary,
                "interface": pdf_interface,
                "metadata": metadata,
            }

        except Exception as e:
            error_msg = f"PDF 딕셔너리 생성 실패: {str(e)}"
            logger.error(f"❌ {error_msg}")

            return {
                "success": False,
                "pdf_dictionary": {},
                "interface": None,
                "metadata": {"error": error_msg},
                "error": error_msg,
            }

    def _extract_footnote_sections(
        self, full_text: str, max_section_size: int
    ) -> Dict[str, str]:
        """
        📝 PDF에서 주석/각주 섹션들을 별도로 추출해요!

        사업보고서나 분기보고서에서 중요한 주석 정보를 찾아내는 핵심 기능입니다.

        🚀 100만자 지원으로 대용량 주석도 완전 분석!
        """
        footnote_sections = {}

        try:
            # 주석 섹션을 찾는 패턴들
            footnote_patterns = [
                r"주\s*석\s*\d+[\.:\s].*?(?=주\s*석\s*\d+|\n\n\n|\Z)",  # 주석 1. ... 주석 2. ...
                r"각\s*주\s*\d+[\.:\s].*?(?=각\s*주\s*\d+|\n\n\n|\Z)",  # 각주 1. ... 각주 2. ...
                r"\d+\)\s+.*?(?=\d+\)|\n\n\n|\Z)",  # 1) ... 2) ... 형태
                r"note\s+\d+[\.:\s].*?(?=note\s+\d+|\n\n\n|\Z)",  # Note 1. ... Note 2. ... (영문)
            ]

            section_counter = 1

            for pattern in footnote_patterns:
                matches = re.finditer(pattern, full_text, re.IGNORECASE | re.DOTALL)

                for match in matches:
                    footnote_text = match.group().strip()

                    # 🚀 100만자 제한으로 확장 (기존 100~50,000자에서 100~1,000,000자로)
                    if 100 <= len(footnote_text) <= max_section_size:
                        # 주석 제목 추출 (첫 줄 또는 처음 50자)
                        first_line = footnote_text.split("\n")[0][:50]
                        footnote_title = f"주석_{section_counter}_{first_line}"

                        footnote_sections[footnote_title] = footnote_text
                        section_counter += 1

            # 추가로 "우발채무", "보증채무", "파생상품" 등 중요 주석 키워드 검색
            important_keywords = [
                "우발채무",
                "보증채무",
                "파생상품",
                "관계회사거래",
                "contingent",
                "derivative",
                "related party",
            ]

            for keyword in important_keywords:
                # 🚀 키워드 주변 텍스트 추출 범위 확장 (앞뒤 2000자 → 10000자)
                pattern = f".{{0,10000}}{re.escape(keyword)}.{{0,10000}}"
                matches = re.finditer(pattern, full_text, re.IGNORECASE | re.DOTALL)

                for match in matches:
                    context_text = match.group().strip()
                    # 🚀 최소 200자에서 최대 100만자까지 지원
                    if 200 <= len(context_text) <= max_section_size:
                        footnote_title = f"키워드_{keyword}_주변내용"
                        if footnote_title not in footnote_sections:  # 중복 방지
                            footnote_sections[footnote_title] = context_text

            logger.info(
                f"📝 주석 섹션 {len(footnote_sections)}개 추출 완료 (100만자 지원)"
            )

        except Exception as e:
            logger.warning(f"⚠️ 주석 섹션 추출 중 오류: {e}")

        return footnote_sections

    async def _create_dictionary_without_toc(
        self,
        pdf_path: str,
        company_name: str,
        max_section_size: int = 2000000,  # 🚀 200만자로 확장!
    ) -> Dict[str, Any]:
        """
        목차가 없는 PDF를 텍스트 기반으로 딕셔너리 생성 (고급)

        Args:
            pdf_path: PDF 파일 경로 또는 URL
            company_name: 회사명
            max_section_size: 각 섹션의 최대 크기 (토큰 제한 고려) - 기본 200만자

        Returns:
            Dict: 생성된 딕셔너리와 메타데이터
        """
        try:
            logger.info(f"📄 {company_name} PDF 딕셔너리 생성 시작 (목차 없음)")
            logger.info(f"   PDF 경로: {pdf_path}")
            logger.info(f"   최대 섹션 크기: {max_section_size:,}자 (200만자 지원)")

            # 전체 텍스트 추출
            full_text_result = await self.extract_raw_text_only(
                pdf_path=pdf_path, company_name=company_name, save_to_json=False
            )

            # 🔍 디버깅: 결과 구조 로그
            logger.info(f"🔍 extract_raw_text_only 결과 타입: {type(full_text_result)}")
            if full_text_result:
                logger.info(f"🔍 결과 키들: {list(full_text_result.keys())}")
                logger.info(f"🔍 success 필드: {full_text_result.get('success')}")
                logger.info(f"🔍 error 필드: {full_text_result.get('error')}")

            # 결과 검증 - success 필드 확인
            if not full_text_result or not full_text_result.get("success"):
                error_msg = (
                    full_text_result.get("error") if full_text_result else "결과 없음"
                )
                raise Exception(f"PDF 텍스트 추출 실패: {error_msg}")

            # extract_raw_text_only 결과 구조에 맞춰 수정
            raw_content = full_text_result.get("raw_content", {})
            full_text = raw_content.get("full_text", "")

            # 🔍 디버깅: raw_content 구조 로그
            logger.info(
                f"🔍 raw_content 키들: {list(raw_content.keys()) if raw_content else 'None'}"
            )
            logger.info(
                f"🔍 추출된 텍스트 길이: {len(full_text) if full_text else 0}자"
            )

            # 텍스트가 비어있는지 확인
            if not full_text or len(full_text.strip()) < 100:
                raise Exception(f"추출된 텍스트가 너무 짧습니다: {len(full_text)}자")

            # 논리적 섹션으로 분할
            pdf_dictionary = self._split_text_into_logical_sections(
                full_text, max_section_size
            )

            # 주석 섹션 별도 추가
            footnote_sections = self._extract_footnote_sections(
                full_text, max_section_size
            )

            for footnote_title, footnote_content in footnote_sections.items():
                pdf_dictionary[f"[주석] {footnote_title}"] = footnote_content

            # 메타데이터 생성
            metadata = {
                "company_name": company_name,
                "pdf_source": pdf_path,
                "creation_timestamp": datetime.now().isoformat(),
                "total_sections": len(pdf_dictionary),
                "toc_based_sections": 0,  # 목차 기반 아님
                "footnote_sections": len(footnote_sections),
                "text_based_sections": len(pdf_dictionary) - len(footnote_sections),
                "total_text_length": sum(
                    len(content) for content in pdf_dictionary.values()
                ),
                "avg_section_length": (
                    sum(len(content) for content in pdf_dictionary.values())
                    // len(pdf_dictionary)
                    if pdf_dictionary
                    else 0
                ),
                "max_section_size_limit": max_section_size,
                "creation_method": "text_pattern_based",
            }

            # PDFDictionaryInterface 생성
            pdf_interface = PDFDictionaryInterface(
                pdf_dictionary=pdf_dictionary, metadata=metadata
            )

            logger.info(
                f"✅ 텍스트 기반 PDF 딕셔너리 생성 완료 - {len(pdf_dictionary)}개 섹션"
            )

            return {
                "success": True,
                "pdf_dictionary": pdf_dictionary,
                "interface": pdf_interface,
                "metadata": metadata,
            }

        except Exception as e:
            error_msg = f"텍스트 기반 PDF 딕셔너리 생성 실패: {str(e)}"
            logger.error(f"❌ {error_msg}")

            return {
                "success": False,
                "pdf_dictionary": {},
                "interface": None,
                "metadata": {"error": error_msg},
                "error": error_msg,
            }

    def _split_text_into_logical_sections(
        self, text: str, max_section_size: int
    ) -> Dict[str, str]:
        """
        텍스트를 논리적 섹션으로 분할합니다 (목차가 없는 경우)

        🚀 200만자 지원으로 대용량 섹션도 완벽 처리!
        """
        sections = {}

        # 간단한 섹션 분할 패턴들
        section_patterns = [
            r"\n\s*\d+\.\s+[가-힣\w\s]+\n",  # 1. 섹션명
            r"\n\s*[가-힣]+\s*\n",  # 단독 한글 제목
            r"\n\s*[A-Z][A-Z\s]+\n",  # 영문 대문자 제목
        ]

        # 패턴으로 분할점 찾기
        split_points = [0]
        for pattern in section_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                split_points.append(match.start())

        split_points.append(len(text))
        split_points = sorted(list(set(split_points)))

        # 섹션 생성
        for i in range(len(split_points) - 1):
            start = split_points[i]
            end = split_points[i + 1]

            section_text = text[start:end].strip()

            # 🚀 최소 길이 100자로 유지하되, 최대 크기는 200만자로 확장
            if len(section_text) >= 100:  # 최소 길이
                # 섹션 제목 추출
                title_match = re.match(r"(.*?)\n", section_text)
                if title_match:
                    section_title = title_match.group(1).strip()[:50]
                else:
                    section_title = f"섹션_{i+1}"

                # 🚀 200만자 제한 적용
                if len(section_text) > max_section_size:
                    section_text = (
                        section_text[:max_section_size]
                        + "...[200만자 제한으로 내용 일부 생략]"
                    )

                sections[section_title] = section_text

        # 텍스트가 너무 짧거나 섹션 분할이 제대로 안된 경우 전체를 하나의 섹션으로
        if not sections and len(text) >= 100:
            sections["전체_문서"] = text[:max_section_size]

        logger.info(f"🤖 논리적 섹션 분할 완료 - {len(sections)}개 섹션 (200만자 지원)")
        return sections

    async def create_pdf_footnotes_analysis(
        self, pdf_path: str, company_name: str
    ) -> Dict[str, Any]:
        """
        🚀 PDF 주석/각주 전문 분석 함수

        🚀 200만자 지원으로 대용량 주석도 완전 분석!

        Args:
            pdf_path: PDF 파일 경로
            company_name: 회사명

        Returns:
            Dict: 주석 분석 결과
        """
        # This function is not implemented in the provided file, so it's left unchanged.
        pass


class PDFDictionaryInterface:
    """
    🚀 PDF 딕셔너리 인터페이스 클래스

    CrewAI 전문가들이 대용량 PDF에서 필요한 부분만 선택적으로 가져와서
    분석할 수 있도록 하는 스마트 인터페이스입니다!

    이게 바로 토큰 절약과 정확성 향상의 핵심이에요! 🎯
    """

    def __init__(self, pdf_dictionary: Dict[str, str], metadata: Dict[str, Any]):
        """
        PDF 딕셔너리 인터페이스 초기화

        Args:
            pdf_dictionary: {목차_항목: 내용} 형태의 딕셔너리
            metadata: PDF 메타데이터 정보
        """
        self.pdf_dictionary = pdf_dictionary
        self.metadata = metadata
        self.section_categories = self._categorize_sections()

        logger.info(
            f"🚀 PDF 딕셔너리 인터페이스 생성됨 - 총 {len(pdf_dictionary)}개 섹션"
        )

    def _categorize_sections(self) -> Dict[str, List[str]]:
        """
        PDF 섹션들을 카테고리별로 분류해요!

        섹션 제목을 보고 어떤 전문가가 관심 있어 할지 자동으로 분류합니다.
        """
        categories = {
            "fundamental_analyst": [],  # 펀더멘털 분석가
            "technical_analyst": [],  # 기술적 분석가
            "industry_analyst": [],  # 산업 분석가
            "valuation_expert": [],  # 밸류에이션 전문가
            "risk_assessor": [],  # 리스크 평가자
            "footnote_specialist": [],  # 주석 전문가
            "general": [],  # 일반 (여러 전문가 공통)
        }

        # 🎯 섹션 제목을 보고 카테고리 자동 분류
        for section_title in self.pdf_dictionary.keys():
            title_lower = section_title.lower()

            # 주석 관련
            if any(
                keyword in title_lower
                for keyword in ["주석", "footnote", "note", "부록"]
            ):
                categories["footnote_specialist"].append(section_title)
            # 재무/펀더멘털 관련
            elif any(
                keyword in title_lower
                for keyword in [
                    "재무",
                    "손익",
                    "대차대조표",
                    "현금흐름",
                    "매출",
                    "이익",
                    "financial",
                    "revenue",
                    "profit",
                ]
            ):
                categories["fundamental_analyst"].append(section_title)
            # 리스크 관련
            elif any(
                keyword in title_lower
                for keyword in ["리스크", "위험", "risk", "위기", "불확실성"]
            ):
                categories["risk_assessor"].append(section_title)
            # 밸류에이션 관련
            elif any(
                keyword in title_lower
                for keyword in [
                    "가치",
                    "평가",
                    "valuation",
                    "dcf",
                    "per",
                    "pbr",
                    "목표가",
                ]
            ):
                categories["valuation_expert"].append(section_title)
            # 산업/시장 관련
            elif any(
                keyword in title_lower
                for keyword in [
                    "시장",
                    "산업",
                    "경쟁",
                    "업계",
                    "market",
                    "industry",
                    "competitive",
                ]
            ):
                categories["industry_analyst"].append(section_title)
            # 기술적 분석 관련
            elif any(
                keyword in title_lower
                for keyword in ["차트", "기술적", "technical", "pattern", "trend"]
            ):
                categories["technical_analyst"].append(section_title)
            else:
                # 일반 카테고리에 추가
                categories["general"].append(section_title)

        return categories

    def get_sections_by_expert_type(
        self, expert_type: str, max_sections: int = 5
    ) -> Dict[str, str]:
        """
        🎯 전문가 유형에 맞는 섹션들을 반환합니다.

        Args:
            expert_type: 전문가 유형 (fundamental_analyst, technical_analyst 등)
            max_sections: 최대 반환할 섹션 수

        Returns:
            Dict[str, str]: {섹션_제목: 섹션_내용} 형태의 딕셔너리
        """
        # 전문가 타입 매핑 (다양한 형태의 전문가명 지원)
        expert_mapping = {
            "fundamental": "fundamental_analyst",
            "fundamental_analyst": "fundamental_analyst",
            "펀더멘털": "fundamental_analyst",
            "재무": "fundamental_analyst",
            "technical": "technical_analyst",
            "technical_analyst": "technical_analyst",
            "기술적": "technical_analyst",
            "차트": "technical_analyst",
            "industry": "industry_analyst",
            "industry_analyst": "industry_analyst",
            "산업": "industry_analyst",
            "시장": "industry_analyst",
            "valuation": "valuation_expert",
            "valuation_expert": "valuation_expert",
            "밸류에이션": "valuation_expert",
            "가치평가": "valuation_expert",
            "risk": "risk_assessor",
            "risk_assessor": "risk_assessor",
            "리스크": "risk_assessor",
            "위험": "risk_assessor",
            "footnote": "footnote_specialist",
            "footnote_specialist": "footnote_specialist",
            "주석": "footnote_specialist",
            "부록": "footnote_specialist",
        }

        # 전문가 타입 정규화
        normalized_expert_type = expert_mapping.get(expert_type.lower(), "general")

        # 해당 전문가에게 적합한 섹션들 가져오기
        relevant_sections = self.section_categories.get(normalized_expert_type, [])

        # 일반 섹션도 포함 (모든 전문가가 참고할 수 있는 내용)
        if normalized_expert_type != "general":
            relevant_sections.extend(
                self.section_categories.get("general", [])[:2]
            )  # 일반 섹션 최대 2개만

        # 최대 섹션 수 제한
        selected_sections = relevant_sections[:max_sections]

        # 실제 섹션 내용 반환
        result = {}
        for section_title in selected_sections:
            if section_title in self.pdf_dictionary:
                result[section_title] = self.pdf_dictionary[section_title]

        logger.info(f"🎯 {expert_type} 전문가용 섹션 {len(result)}개 반환")
        return result

    def get_all_sections(self) -> Dict[str, str]:
        """모든 섹션을 반환합니다."""
        return self.pdf_dictionary.copy()

    def get_section_by_title(self, title: str) -> str:
        """특정 제목의 섹션을 반환합니다."""
        return self.pdf_dictionary.get(title, "")

    def search_sections(self, keyword: str, max_results: int = 3) -> Dict[str, str]:
        """키워드로 섹션을 검색합니다."""
        results = {}
        for title, content in self.pdf_dictionary.items():
            if keyword.lower() in title.lower() or keyword.lower() in content.lower():
                results[title] = content
                if len(results) >= max_results:
                    break
        return results

    def get_metadata(self) -> Dict[str, Any]:
        """메타데이터를 반환합니다."""
        return self.metadata.copy()

    def to_dict(self) -> Dict[str, Any]:
        """
        🔧 JSON 직렬화를 위한 딕셔너리 변환

        PDFDictionaryInterface 객체를 JSON으로 저장할 수 있도록
        순수 딕셔너리 형태로 변환합니다.
        """
        return {
            "pdf_dictionary": self.pdf_dictionary,
            "metadata": self.metadata,
            "section_categories": self.section_categories,
            "interface_type": "PDFDictionaryInterface",
            "total_sections": len(self.pdf_dictionary),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PDFDictionaryInterface":
        """
        🔧 딕셔너리에서 PDFDictionaryInterface 객체 복원
        """
        return cls(
            pdf_dictionary=data.get("pdf_dictionary", {}),
            metadata=data.get("metadata", {}),
        )

    def __str__(self) -> str:
        """문자열 표현"""
        return f"PDFDictionaryInterface(sections={len(self.pdf_dictionary)}, company={self.metadata.get('company_name', 'Unknown')})"

    def __repr__(self) -> str:
        """개발자용 문자열 표현"""
        return self.__str__()
