#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📄 PDF 파일 읽기 유틸리티

이 파일은 AI Agent가 PDF 파일을 읽고 텍스트를 추출할 수 있게 도와주는 도구입니다.
마치 사람이 PDF 문서를 읽고 내용을 이해하는 것처럼, AI도 PDF를 읽을 수 있게 해줍니다.

주요 기능:
1. PDF 파일에서 텍스트 추출하기
2. PDF 파일의 페이지별로 내용 분리하기
3. PDF 파일에서 표(테이블) 데이터 추출하기
4. 여러 PDF 처리 라이브러리를 자동으로 시도하여 최적의 결과 제공
"""

import io
import logging
import math
import re
import tempfile
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse

import requests
from loguru import logger


class PDFReader:
    """PDF 파일을 다양한 라이브러리로 읽는 유니버설 PDF 리더 (청크 처리 지원)"""

    def __init__(self, max_chars: int = 100000):  # 전문 분석을 위해 100KB로 증량
        """
        PDFReader 초기화

        Args:
            max_chars: 한 번에 읽을 최대 문자 수 (전문 분석: 100KB)
        """
        self.max_chars = max_chars
        # 청크 프로세서는 나중에 초기화
        self.chunk_processor = None

        # 지원하는 PDF 라이브러리들 (우선순위 순서)
        self.pdf_libraries = [
            ("pdfplumber", self._read_with_pdfplumber),
            ("pymupdf", self._read_with_pymupdf),
            ("pypdf", self._read_with_pypdf),
            ("PyPDF2", self._read_with_pypdf2),
            ("pdfminer", self._read_with_pdfminer),
        ]

        logger.info(
            f"📚 PDFReader 초기화 완료 (최대 크기: {max_chars:,}자, 청크 처리: 활성화)"
        )

    async def read_pdf_chunked(
        self,
        pdf_path: str,
        analysis_function: Callable = None,
        progress_callback: Optional[Callable] = None,
        chunk_size: int = 15000,
        preserve_sections: bool = True,
    ) -> Dict[str, any]:
        """
         📄 PDF를 청크 단위로 읽고 분석하는 전문 분석 메서드

        이 메서드는 대용량 PDF도 안전하게 처리할 수 있어요:
         1. PDF 전체 텍스트 추출
         2. 스마트 청킹으로 의미 단위 분할
         3. 각 청크를 순차적으로 분석
         4. 결과를 통합하여 종합 리포트 생성

         Args:
             pdf_path: PDF 파일 경로
             analysis_function: 각 청크를 분석할 함수 (없으면 기본 요약 수행)
             progress_callback: 진행 상황 콜백 함수
             chunk_size: 청크 크기 (기본: 15KB)
             preserve_sections: 섹션 구조 보존 여부

         Returns:
             Dict: 청크별 분석 결과와 통합 결과
        """
        try:
            logger.info(f"📖 청크 단위 PDF 분석 시작: {pdf_path}")

            # 1단계: PDF 전체 텍스트 추출
            logger.info("🔍 1단계: PDF 전체 텍스트 추출 중...")
            full_text = await self.read_pdf(
                pdf_path, max_chars=None
            )  # 전체 텍스트 추출

            if not full_text or len(full_text.strip()) == 0:
                return {
                    "success": False,
                    "error": "PDF에서 텍스트를 추출할 수 없습니다",
                    "pdf_path": pdf_path,
                }

            logger.info(f"✅ PDF 텍스트 추출 완료: {len(full_text):,}자")

            # 2단계: 스마트 청킹
            logger.info("🧩 2단계: 스마트 청킹 수행 중...")
            if self.chunk_processor is None:
                self.chunk_processor = ChunkProcessor()
            self.chunk_processor.chunk_size = chunk_size
            chunks = self.chunk_processor.smart_chunk_text(full_text, preserve_sections)

            if not chunks:
                return {
                    "success": False,
                    "error": "텍스트를 청크로 나눌 수 없습니다",
                    "pdf_path": pdf_path,
                    "text_length": len(full_text),
                }

            logger.info(f"✅ 청킹 완료: {len(chunks)}개 청크 생성")

            # 3단계: 기본 분석 함수 설정 (사용자가 제공하지 않은 경우)
            if analysis_function is None:
                analysis_function = self._default_chunk_analysis

            # 4단계: 청크별 분석 수행
            logger.info("🔬 3단계: 청크별 분석 수행 중...")
            analysis_result = await self.chunk_processor.process_chunks_with_callback(
                chunks=chunks,
                analysis_function=analysis_function,
                progress_callback=progress_callback,
            )

            # 5단계: 메타데이터 추가
            analysis_result.update(
                {
                    "pdf_path": pdf_path,
                    "total_text_length": len(full_text),
                    "chunk_configuration": {
                        "chunk_size": chunk_size,
                        "preserve_sections": preserve_sections,
                        "overlap_size": self.chunk_processor.overlap_size,
                    },
                    "extraction_method": self._get_successful_library_name(),
                    "timestamp": self._get_current_timestamp(),
                }
            )

            logger.info(f"🎉 청크 단위 PDF 분석 완료!")
            return analysis_result

        except Exception as e:
            logger.error(f"❌ 청크 단위 PDF 분석 실패: {e}")
            return {
                "success": False,
                "error": f"청크 단위 분석 중 오류 발생: {str(e)}",
                "pdf_path": pdf_path,
            }

    async def _default_chunk_analysis(self, chunk: Dict[str, any]) -> Dict[str, any]:
        """
        기본 청크 분석 함수

        사용자가 별도의 분석 함수를 제공하지 않은 경우 사용되는 기본 분석기예요.
        주요 키워드, 중요 문장, 섹션 요약 등을 추출합니다.

        Args:
            chunk: 분석할 청크 정보

        Returns:
            Dict: 기본 분석 결과
        """
        content = chunk["content"]

        # 기본 분석 수행
        analysis = {
            "summary": self._extract_key_sentences(content, max_sentences=3),
            "keywords": self._extract_keywords(content, max_keywords=10),
            "section_type": chunk["metadata"].get("type", "unknown"),
            "content_length": len(content),
            "key_numbers": self._extract_numbers(content),
            "structure_info": {
                "has_sections": "제" in content or "장" in content or "절" in content,
                "has_tables": "│" in content or "┌" in content or "├" in content,
                "has_lists": "•" in content or "-" in content or "1." in content,
                "paragraph_count": content.count("\n\n") + 1,
            },
        }

        # 섹션 제목이 있으면 추가
        if "section_title" in chunk["metadata"]:
            analysis["section_title"] = chunk["metadata"]["section_title"]

        return analysis

    def _extract_key_sentences(self, text: str, max_sentences: int = 3) -> List[str]:
        """텍스트에서 핵심 문장들을 추출"""

        # 문장 분리
        sentences = re.split(r"[.!?]\s+", text)
        sentences = [
            s.strip() for s in sentences if len(s.strip()) > 20
        ]  # 너무 짧은 문장 제외

        if len(sentences) <= max_sentences:
            return sentences

        # 키워드 점수 기반으로 핵심 문장 선별
        keyword_patterns = [
            r"중요한?",
            r"핵심",
            r"주요",
            r"결론",
            r"요약",
            r"특징",
            r"\d+%",
            r"\d+억",
            r"\d+만",
            r"증가",
            r"감소",
            r"상승",
            r"하락",
        ]

        scored_sentences = []
        for sentence in sentences:
            score = 0
            for pattern in keyword_patterns:
                score += len(re.findall(pattern, sentence, re.IGNORECASE))

            scored_sentences.append((sentence, score))

        # 점수순으로 정렬하여 상위 문장들 반환
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        return [sent[0] for sent in scored_sentences[:max_sentences]]

    def _extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """텍스트에서 키워드들을 추출"""

        # 한국어 명사 패턴 (간단한 버전)
        noun_pattern = r"[가-힣]{2,}"

        # 숫자 + 단위 패턴
        number_pattern = r"\d+(?:억|만|천|백|%|원|달러|유로|엔)"

        # 영어 단어 패턴
        english_pattern = r"[A-Za-z]{3,}"

        keywords = []

        # 명사 추출
        nouns = re.findall(noun_pattern, text)
        keywords.extend(nouns)

        # 숫자 + 단위 추출
        numbers = re.findall(number_pattern, text)
        keywords.extend(numbers)

        # 영어 단어 추출
        english_words = re.findall(english_pattern, text)
        keywords.extend(english_words)

        # 빈도 계산 및 상위 키워드 반환
        from collections import Counter

        keyword_counts = Counter(keywords)

        # 너무 짧거나 일반적인 단어 제외
        exclude_words = {
            "있는",
            "있다",
            "이다",
            "것은",
            "것이",
            "에서",
            "으로",
            "에게",
            "하는",
            "한다",
            "되는",
            "된다",
        }
        filtered_keywords = [
            word
            for word, count in keyword_counts.most_common()
            if len(word) > 1 and word not in exclude_words
        ]

        return filtered_keywords[:max_keywords]

    def _extract_numbers(self, text: str) -> List[str]:
        """텍스트에서 중요한 숫자들을 추출"""

        # 다양한 숫자 패턴들
        patterns = [
            r"\d{1,3}(?:,\d{3})*(?:\.\d+)?%",  # 퍼센트
            r"\d{1,3}(?:,\d{3})*(?:\.\d+)?억",  # 억 단위
            r"\d{1,3}(?:,\d{3})*(?:\.\d+)?만",  # 만 단위
            r"\d{1,3}(?:,\d{3})*(?:\.\d+)?원",  # 원 단위
            r"\$\d{1,3}(?:,\d{3})*(?:\.\d+)?",  # 달러
            r"\d{4}년",  # 연도
            r"\d{1,2}월",  # 월
            r"\d{1,2}일",  # 일
        ]

        numbers = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            numbers.extend(matches)

        return list(set(numbers))  # 중복 제거

    def _get_successful_library_name(self) -> str:
        """성공적으로 사용된 PDF 라이브러리 이름 반환"""
        # 실제 구현에서는 성공한 라이브러리를 추적해야 합니다
        return "auto-detected"

    def _get_current_timestamp(self) -> str:
        """현재 타임스탬프 반환"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _read_with_pdfplumber(
        self, pdf_data: io.BytesIO
    ) -> Dict[str, Union[str, List[str], bool]]:
        """
        pdfplumber 라이브러리를 사용하여 텍스트를 추출합니다.
        이 라이브러리는 표(table)와 복잡한 레이아웃을 잘 처리합니다.
        """
        import pdfplumber

        pages_text = []
        full_text = ""

        with pdfplumber.open(pdf_data) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text() or ""
                pages_text.append(page_text)
                full_text += f"\n--- 페이지 {page_num} ---\n{page_text}\n"

        return {
            "success": True,
            "text": full_text.strip(),
            "pages": pages_text,
            "method": "pdfplumber",
        }

    def _read_with_pymupdf(
        self, pdf_data: io.BytesIO
    ) -> Dict[str, Union[str, List[str], bool]]:
        """
        pymupdf(fitz) 라이브러리를 사용하여 텍스트를 추출합니다.
        이 라이브러리는 처리 속도가 빠르고 안정적입니다.
        """
        import fitz  # pymupdf

        pages_text = []
        full_text = ""

        pdf_document = fitz.open(stream=pdf_data.read(), filetype="pdf")

        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            page_text = page.get_text()
            pages_text.append(page_text)
            full_text += f"\n--- 페이지 {page_num + 1} ---\n{page_text}\n"

        pdf_document.close()

        return {
            "success": True,
            "text": full_text.strip(),
            "pages": pages_text,
            "method": "pymupdf",
        }

    def _read_with_pypdf(
        self, pdf_data: io.BytesIO
    ) -> Dict[str, Union[str, List[str], bool]]:
        """
        pypdf 라이브러리를 사용하여 텍스트를 추출합니다.
        이 라이브러리는 최신 버전의 PDF 처리 라이브러리입니다.
        """
        import pypdf

        pages_text = []
        full_text = ""

        reader = pypdf.PdfReader(pdf_data)

        for page_num, page in enumerate(reader.pages, 1):
            page_text = page.extract_text()
            pages_text.append(page_text)
            full_text += f"\n--- 페이지 {page_num} ---\n{page_text}\n"

        return {
            "success": True,
            "text": full_text.strip(),
            "pages": pages_text,
            "method": "pypdf",
        }

    def _read_with_pypdf2(
        self, pdf_data: io.BytesIO
    ) -> Dict[str, Union[str, List[str], bool]]:
        """
        PyPDF2 라이브러리를 사용하여 텍스트를 추출합니다.
        이 라이브러리는 가장 기본적인 PDF 처리 라이브러리입니다.
        """
        import PyPDF2

        pages_text = []
        full_text = ""

        reader = PyPDF2.PdfReader(pdf_data)

        for page_num, page in enumerate(reader.pages, 1):
            page_text = page.extract_text()
            pages_text.append(page_text)
            full_text += f"\n--- 페이지 {page_num} ---\n{page_text}\n"

        return {
            "success": True,
            "text": full_text.strip(),
            "pages": pages_text,
            "method": "PyPDF2",
        }

    def _read_with_pdfminer(
        self, pdf_data: io.BytesIO
    ) -> Dict[str, Union[str, List[str], bool]]:
        """
        pdfminer 라이브러리를 사용하여 텍스트를 추출합니다.
        이 라이브러리는 복잡한 레이아웃의 PDF도 잘 처리합니다.
        """
        from pdfminer.high_level import extract_text

        # pdfminer는 페이지별 분리를 직접 지원하지 않으므로 전체 텍스트만 추출
        full_text = extract_text(pdf_data)

        # 간단하게 페이지 구분을 위해 전체 텍스트를 하나의 페이지로 처리
        pages_text = [full_text] if full_text.strip() else []

        return {
            "success": True,
            "text": full_text.strip(),
            "pages": pages_text,
            "method": "pdfminer",
        }


# 사용하기 쉽도록 전역 인스턴스 생성
pdf_reader = PDFReader()


def extract_pdf_text(
    source: Union[str, Path, io.BytesIO],
) -> Dict[str, Union[str, List[str], bool]]:
    """
    PDF에서 텍스트를 추출하는 간편한 함수입니다.

    이 함수는 AI Agent가 쉽게 사용할 수 있도록 만든 단순한 인터페이스입니다.
    URL, 파일 경로, 또는 바이너리 데이터 중 어떤 것이든 자동으로 감지해서 처리합니다.

    매개변수:
        source: PDF의 출처
            - str: URL (http://...) 또는 파일 경로 (C:/...)
            - Path: 파일 경로 객체
            - io.BytesIO: PDF 바이너리 데이터

    반환값:
        Dict: 추출 결과 (PDFReader.extract_text_from_* 메서드들과 동일한 형식)

    사용 예시:
        # URL에서 PDF 읽기
        result = extract_pdf_text("https://example.com/report.pdf")

        # 로컬 파일에서 PDF 읽기
        result = extract_pdf_text("C:/Documents/report.pdf")

        # 결과 확인
        if result['success']:
            print("PDF 텍스트:", result['text'])
        else:
            print("오류:", result['error'])
    """
    try:
        # PDFReader 인스턴스 생성
        pdf_reader = PDFReader(max_chars=100000)

        if isinstance(source, str):
            # URL인지 파일 경로인지 판단
            parsed = urlparse(source)
            if parsed.scheme in ("http", "https"):
                # URL인 경우 - 직접 처리
                return _extract_text_from_url(source, pdf_reader)
            else:
                # 파일 경로인 경우 - 직접 처리
                return _extract_text_from_file(source, pdf_reader)

        elif isinstance(source, Path):
            # Path 객체인 경우 - 직접 처리
            return _extract_text_from_file(str(source), pdf_reader)

        elif isinstance(source, io.BytesIO):
            # 바이너리 데이터인 경우 - 직접 처리
            return _extract_text_from_bytes(source, pdf_reader)

        else:
            # 지원하지 않는 타입
            error_msg = f"지원하지 않는 소스 타입: {type(source)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "text": "",
                "pages": [],
                "method": "none",
                "error": error_msg,
            }

    except Exception as e:
        error_msg = f"PDF 텍스트 추출 중 오류: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "text": "",
            "pages": [],
            "method": "none",
            "error": error_msg,
        }


def _extract_text_from_url(
    url: str, pdf_reader: PDFReader
) -> Dict[str, Union[str, List[str], bool]]:
    """URL에서 PDF 다운로드 후 텍스트 추출"""
    try:
        import requests

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        pdf_data = io.BytesIO(response.content)
        return _extract_text_from_bytes(pdf_data, pdf_reader)

    except Exception as e:
        return {
            "success": False,
            "text": "",
            "pages": [],
            "method": "url_download_failed",
            "error": f"URL에서 PDF 다운로드 실패: {str(e)}",
        }


def _extract_text_from_file(
    file_path: str, pdf_reader: PDFReader
) -> Dict[str, Union[str, List[str], bool]]:
    """로컬 파일에서 PDF 텍스트 추출"""
    try:
        with open(file_path, "rb") as file:
            pdf_data = io.BytesIO(file.read())
            return _extract_text_from_bytes(pdf_data, pdf_reader)

    except Exception as e:
        return {
            "success": False,
            "text": "",
            "pages": [],
            "method": "file_read_failed",
            "error": f"파일 읽기 실패: {str(e)}",
        }


def _extract_text_from_bytes(
    pdf_data: io.BytesIO, pdf_reader: PDFReader
) -> Dict[str, Union[str, List[str], bool]]:
    """PDF 바이너리 데이터에서 텍스트 추출"""
    try:
        # PDFReader의 라이브러리들을 차례로 시도
        for lib_name, extract_method in pdf_reader.pdf_libraries:
            try:
                pdf_data.seek(0)  # 스트림 포지션 초기화
                result = extract_method(pdf_data)

                if result.get("success", False) and result.get("text", "").strip():
                    logger.info(f"✅ PDF 텍스트 추출 성공 (라이브러리: {lib_name})")
                    return result

            except Exception as e:
                logger.warning(f"⚠️ {lib_name} 라이브러리 실패: {e}")
                continue

        # 모든 라이브러리 실패
        return {
            "success": False,
            "text": "",
            "pages": [],
            "method": "all_libraries_failed",
            "error": "모든 PDF 처리 라이브러리에서 텍스트 추출 실패",
        }

    except Exception as e:
        return {
            "success": False,
            "text": "",
            "pages": [],
            "method": "extraction_error",
            "error": f"PDF 처리 중 오류: {str(e)}",
        }


class ChunkProcessor:
    """
    📄 PDF 텍스트를 청크 단위로 처리하는 전문 분석 클래스

    대용량 PDF 파일을 작은 단위로 나누어서 처리함으로써:
    - 메모리 사용량 최적화
    - LLM 토큰 제한 회피
    - 전체 내용 놓치지 않고 분석
    - 진행 상황 실시간 추적
    """

    def __init__(self, chunk_size: int = 15000, overlap_size: int = 1000):
        """
        청크 프로세서 초기화

        Args:
            chunk_size: 각 청크의 최대 크기 (문자 수)
            overlap_size: 청크 간 겹치는 부분 크기 (문맥 유지용)
        """
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        logger.info(
            f"🔧 청크 프로세서 초기화 (청크 크기: {chunk_size}, 겹침: {overlap_size})"
        )

    def smart_chunk_text(
        self, text: str, preserve_sections: bool = True
    ) -> List[Dict[str, any]]:
        """
        텍스트를 스마트하게 청크로 나누는 함수

        이 함수는 단순히 글자 수로만 자르지 않고:
        1. 문단 경계를 존중
        2. 섹션 제목을 보존
        3. 표와 목록 구조 유지
        4. 문맥 연결성 확보

        Args:
            text: 나눌 텍스트
            preserve_sections: 섹션 구조 보존 여부

        Returns:
            List[Dict]: 청크 정보 리스트
                - content: 청크 텍스트
                - chunk_id: 청크 번호
                - start_char: 시작 위치
                - end_char: 끝 위치
                - metadata: 메타데이터 (제목, 페이지 등)
        """
        if not text.strip():
            return []

        logger.info(f"📝 스마트 청킹 시작 (전체 텍스트: {len(text):,}자)")

        chunks = []

        if preserve_sections:
            # 섹션 기반 청킹 시도
            chunks = self._chunk_by_sections(text)

        if not chunks:
            # 섹션 분리 실패시 문단 기반 청킹
            chunks = self._chunk_by_paragraphs(text)

        if not chunks:
            # 문단 분리도 실패시 고정 크기 청킹
            chunks = self._chunk_by_fixed_size(text)

        logger.info(f"✅ 청킹 완료: {len(chunks)}개 청크 생성")

        # 청크 정보 보강
        for i, chunk in enumerate(chunks):
            chunk.update(
                {
                    "chunk_id": i + 1,
                    "total_chunks": len(chunks),
                    "chunk_size": len(chunk["content"]),
                    "progress_percentage": round((i + 1) / len(chunks) * 100, 1),
                }
            )

        return chunks

    def _chunk_by_sections(self, text: str) -> List[Dict[str, any]]:
        """섹션 제목을 기준으로 청킹"""

        # 섹션 패턴들 (우선순위 순)
        section_patterns = [
            r"\n\s*(?:제?\s*\d+\s*[장절부편]\.?\s+.+)",  # 제1장, 제2절 등
            r"\n\s*(?:\d+\.\s*.+)",  # 1. 제목 형태
            r"\n\s*(?:[A-Z][A-Z\s]{3,})\n",  # 대문자 제목
            r"\n\s*(?:---\s*페이지\s*\d+\s*---)",  # 페이지 구분
            r"\n\s*(?:【.+】)",  # 【제목】 형태
            r"\n\s*(?:\*{2,}.+\*{2,})",  # **제목** 형태
        ]

        # 섹션 구분점 찾기
        section_breaks = []

        for pattern in section_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                section_breaks.append(
                    {
                        "position": match.start(),
                        "title": match.group().strip(),
                        "pattern": pattern,
                    }
                )

        if len(section_breaks) < 2:
            return []  # 섹션이 충분하지 않음

        # 위치순으로 정렬
        section_breaks.sort(key=lambda x: x["position"])

        chunks = []

        for i in range(len(section_breaks)):
            start_pos = section_breaks[i]["position"]
            end_pos = (
                section_breaks[i + 1]["position"]
                if i + 1 < len(section_breaks)
                else len(text)
            )

            section_text = text[start_pos:end_pos].strip()

            if len(section_text) > self.chunk_size:
                # 섹션이 너무 크면 다시 분할
                sub_chunks = self._chunk_by_paragraphs(section_text)
                chunks.extend(sub_chunks)
            else:
                chunks.append(
                    {
                        "content": section_text,
                        "start_char": start_pos,
                        "end_char": end_pos,
                        "metadata": {
                            "section_title": section_breaks[i]["title"],
                            "type": "section",
                            "pattern_used": section_breaks[i]["pattern"],
                        },
                    }
                )

        return chunks

    def _chunk_by_paragraphs(self, text: str) -> List[Dict[str, any]]:
        """문단을 기준으로 청킹"""

        # 문단 구분 패턴
        paragraph_pattern = r"\n\s*\n"
        paragraphs = re.split(paragraph_pattern, text)

        chunks = []
        current_chunk = ""
        start_pos = 0

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            # 현재 청크에 문단을 추가했을 때 크기 확인
            test_chunk = current_chunk + ("\n\n" if current_chunk else "") + paragraph

            if len(test_chunk) <= self.chunk_size or not current_chunk:
                current_chunk = test_chunk
            else:
                # 현재 청크 저장
                if current_chunk:
                    chunks.append(
                        {
                            "content": current_chunk,
                            "start_char": start_pos,
                            "end_char": start_pos + len(current_chunk),
                            "metadata": {
                                "type": "paragraph",
                                "paragraphs": current_chunk.count("\n\n") + 1,
                            },
                        }
                    )
                    start_pos += len(current_chunk)

                # 새 청크 시작 (겹침 추가)
                if chunks and self.overlap_size > 0:
                    overlap_text = current_chunk[-self.overlap_size :]
                    current_chunk = overlap_text + "\n\n" + paragraph
                else:
                    current_chunk = paragraph

        # 마지막 청크 저장
        if current_chunk:
            chunks.append(
                {
                    "content": current_chunk,
                    "start_char": start_pos,
                    "end_char": start_pos + len(current_chunk),
                    "metadata": {
                        "type": "paragraph",
                        "paragraphs": current_chunk.count("\n\n") + 1,
                    },
                }
            )

        return chunks

    def _chunk_by_fixed_size(self, text: str) -> List[Dict[str, any]]:
        """고정 크기로 청킹 (최후 수단)"""

        chunks = []

        for i in range(0, len(text), self.chunk_size - self.overlap_size):
            start_pos = max(0, i - self.overlap_size) if i > 0 else 0
            end_pos = min(len(text), i + self.chunk_size)

            chunk_text = text[start_pos:end_pos]

            chunks.append(
                {
                    "content": chunk_text,
                    "start_char": start_pos,
                    "end_char": end_pos,
                    "metadata": {"type": "fixed_size", "has_overlap": i > 0},
                }
            )

            if end_pos >= len(text):
                break

        return chunks

    async def process_chunks_with_callback(
        self,
        chunks: List[Dict[str, any]],
        analysis_function: Callable,
        progress_callback: Optional[Callable] = None,
    ) -> Dict[str, any]:
        """
        청크들을 순차적으로 처리하고 결과를 통합

        Args:
            chunks: 처리할 청크 리스트
            analysis_function: 각 청크를 분석할 함수
            progress_callback: 진행 상황 콜백 함수

        Returns:
            Dict: 통합된 분석 결과
        """
        logger.info(f"🔄 청크 처리 시작: {len(chunks)}개 청크")

        chunk_results = []
        failed_chunks = []

        for i, chunk in enumerate(chunks):
            try:
                if progress_callback:
                    await progress_callback(i + 1, len(chunks), chunk)

                logger.info(
                    f"📝 청크 {chunk['chunk_id']}/{chunk['total_chunks']} 처리 중... ({chunk['progress_percentage']}%)"
                )

                # 청크 분석 실행
                result = await analysis_function(chunk)

                chunk_results.append(
                    {
                        "chunk_id": chunk["chunk_id"],
                        "result": result,
                        "metadata": chunk["metadata"],
                        "chunk_size": chunk["chunk_size"],
                    }
                )

                logger.info(f"✅ 청크 {chunk['chunk_id']} 처리 완료")

            except Exception as e:
                logger.error(f"❌ 청크 {chunk['chunk_id']} 처리 실패: {e}")
                failed_chunks.append(
                    {
                        "chunk_id": chunk["chunk_id"],
                        "error": str(e),
                        "chunk_size": chunk["chunk_size"],
                    }
                )

        # 결과 통합
        integrated_result = self._integrate_chunk_results(chunk_results, failed_chunks)

        logger.info(
            f"🎉 청크 처리 완료: 성공 {len(chunk_results)}개, 실패 {len(failed_chunks)}개"
        )

        return integrated_result

    def _integrate_chunk_results(
        self, chunk_results: List[Dict], failed_chunks: List[Dict]
    ) -> Dict[str, any]:
        """청크 분석 결과들을 통합"""

        return {
            "success": True,
            "total_chunks": len(chunk_results) + len(failed_chunks),
            "successful_chunks": len(chunk_results),
            "failed_chunks": len(failed_chunks),
            "chunk_results": chunk_results,
            "failed_chunk_info": failed_chunks,
            "processing_summary": {
                "total_characters_processed": sum(
                    r["chunk_size"] for r in chunk_results
                ),
                "success_rate": (
                    round(
                        len(chunk_results)
                        / (len(chunk_results) + len(failed_chunks))
                        * 100,
                        1,
                    )
                    if chunk_results or failed_chunks
                    else 0
                ),
                "chunk_metadata": [r["metadata"] for r in chunk_results],
            },
        }


if __name__ == "__main__":
    # 테스트용 코드 (이 파일을 직접 실행했을 때만 동작)
    print("📄 PDF Reader 테스트")
    print("=" * 50)

    # 사용 가능한 라이브러리 확인
    reader = PDFReader()
    print(f"사용 가능한 라이브러리: {list(reader.available_libraries.keys())}")

    # 실제 PDF URL 테스트 (예시)
    # test_url = "https://example.com/sample.pdf"
    # result = extract_pdf_text(test_url)
    # print("테스트 결과:", result)
