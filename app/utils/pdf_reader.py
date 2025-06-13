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
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse

import requests
from loguru import logger


class PDFReader:
    """
    PDF 파일을 읽고 텍스트를 추출하는 클래스입니다.

    이 클래스는 마치 여러 종류의 번역기를 가진 것과 같습니다.
    하나의 번역기가 안 되면, 다른 번역기를 자동으로 시도해서
    최대한 정확하게 PDF 내용을 텍스트로 변환해줍니다.
    """

    def __init__(self):
        """
        PDF 리더를 초기화합니다.
        여러 PDF 처리 라이브러리들이 설치되어 있는지 확인하고,
        사용 가능한 라이브러리들의 목록을 만듭니다.
        """
        self.available_libraries = self._check_available_libraries()
        logger.info(
            f"📚 사용 가능한 PDF 처리 라이브러리: {list(self.available_libraries.keys())}"
        )

    def _check_available_libraries(self) -> Dict[str, bool]:
        """
        설치된 PDF 처리 라이브러리들을 확인하는 함수입니다.

        반환값:
            Dict[str, bool]: 각 라이브러리의 사용 가능 여부
        """
        libraries = {}

        # PyPDF2 라이브러리 확인 (기본적인 PDF 텍스트 추출)
        try:
            import PyPDF2

            libraries["PyPDF2"] = True
            logger.debug("✅ PyPDF2 라이브러리 사용 가능")
        except ImportError:
            libraries["PyPDF2"] = False
            logger.debug("❌ PyPDF2 라이브러리 없음")

        # pdfplumber 라이브러리 확인 (표와 복잡한 레이아웃 처리 가능)
        try:
            import pdfplumber

            libraries["pdfplumber"] = True
            logger.debug("✅ pdfplumber 라이브러리 사용 가능")
        except ImportError:
            libraries["pdfplumber"] = False
            logger.debug("❌ pdfplumber 라이브러리 없음")

        # pymupdf(fitz) 라이브러리 확인 (고성능 PDF 처리)
        try:
            import fitz  # pymupdf의 실제 모듈명

            libraries["pymupdf"] = True
            logger.debug("✅ pymupdf 라이브러리 사용 가능")
        except ImportError:
            libraries["pymupdf"] = False
            logger.debug("❌ pymupdf 라이브러리 없음")

        # pdfminer 라이브러리 확인 (복잡한 레이아웃 분석)
        try:
            from pdfminer.high_level import extract_text

            libraries["pdfminer"] = True
            logger.debug("✅ pdfminer 라이브러리 사용 가능")
        except ImportError:
            libraries["pdfminer"] = False
            logger.debug("❌ pdfminer 라이브러리 없음")

        # pypdf 라이브러리 확인 (최신 PDF 처리)
        try:
            import pypdf

            libraries["pypdf"] = True
            logger.debug("✅ pypdf 라이브러리 사용 가능")
        except ImportError:
            libraries["pypdf"] = False
            logger.debug("❌ pypdf 라이브러리 없음")

        return libraries

    def extract_text_from_url(
        self, pdf_url: str
    ) -> Dict[str, Union[str, List[str], bool]]:
        """
        인터넷에 있는 PDF 파일의 URL을 받아서 텍스트를 추출합니다.

        매개변수:
            pdf_url (str): PDF 파일의 인터넷 주소 (예: "https://example.com/report.pdf")

        반환값:
            Dict: 추출 결과가 담긴 사전
                - success (bool): 추출 성공 여부
                - text (str): 추출된 전체 텍스트
                - pages (List[str]): 페이지별 텍스트 목록
                - method (str): 사용된 처리 방법
                - error (str): 오류가 있을 경우 오류 메시지
        """
        logger.info(f"🌐 PDF URL에서 텍스트 추출 시작: {pdf_url}")

        try:
            # 1단계: PDF 파일을 인터넷에서 다운로드
            logger.debug("📥 PDF 파일 다운로드 중...")
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()

            # 2단계: 다운로드한 PDF 데이터를 메모리에서 처리
            pdf_data = io.BytesIO(response.content)
            logger.debug(
                f"✅ PDF 파일 다운로드 완료 (크기: {len(response.content)} bytes)"
            )

            # 3단계: PDF 데이터에서 텍스트 추출
            return self.extract_text_from_bytes(pdf_data)

        except requests.RequestException as e:
            error_msg = f"PDF 다운로드 실패: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "text": "",
                "pages": [],
                "method": "none",
                "error": error_msg,
            }
        except Exception as e:
            error_msg = f"PDF URL 처리 중 예상치 못한 오류: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "text": "",
                "pages": [],
                "method": "none",
                "error": error_msg,
            }

    def extract_text_from_file(
        self, file_path: Union[str, Path]
    ) -> Dict[str, Union[str, List[str], bool]]:
        """
        컴퓨터에 저장된 PDF 파일에서 텍스트를 추출합니다.

        매개변수:
            file_path (Union[str, Path]): PDF 파일 경로 (예: "C:/Documents/report.pdf")

        반환값:
            Dict: 추출 결과가 담긴 사전 (extract_text_from_url과 동일한 형식)
        """
        file_path = Path(file_path)
        logger.info(f"📁 로컬 PDF 파일에서 텍스트 추출 시작: {file_path}")

        if not file_path.exists():
            error_msg = f"파일을 찾을 수 없습니다: {file_path}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "text": "",
                "pages": [],
                "method": "none",
                "error": error_msg,
            }

        try:
            # PDF 파일을 바이너리 모드로 읽어서 메모리에 로드
            with open(file_path, "rb") as file:
                pdf_data = io.BytesIO(file.read())

            return self.extract_text_from_bytes(pdf_data)

        except Exception as e:
            error_msg = f"PDF 파일 읽기 실패: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "text": "",
                "pages": [],
                "method": "none",
                "error": error_msg,
            }

    def extract_text_from_bytes(
        self, pdf_data: io.BytesIO
    ) -> Dict[str, Union[str, List[str], bool]]:
        """
        메모리에 있는 PDF 데이터에서 텍스트를 추출합니다.
        여러 라이브러리를 순서대로 시도해서 가장 좋은 결과를 반환합니다.

        매개변수:
            pdf_data (io.BytesIO): PDF 파일의 바이너리 데이터

        반환값:
            Dict: 추출 결과가 담긴 사전
        """
        logger.debug("🔄 PDF 바이너리 데이터에서 텍스트 추출 시작")

        # 여러 라이브러리를 우선순위 순으로 시도
        extraction_methods = [
            ("pdfplumber", self._extract_with_pdfplumber),
            ("pymupdf", self._extract_with_pymupdf),
            ("pypdf", self._extract_with_pypdf),
            ("PyPDF2", self._extract_with_pypdf2),
            ("pdfminer", self._extract_with_pdfminer),
        ]

        for method_name, method_func in extraction_methods:
            if not self.available_libraries.get(method_name, False):
                logger.debug(f"⏭️ {method_name} 라이브러리 사용 불가, 다음 방법 시도")
                continue

            try:
                logger.debug(f"🔧 {method_name} 라이브러리로 텍스트 추출 시도")

                # PDF 데이터 포인터를 처음으로 리셋 (이전 시도에서 위치가 변경되었을 수 있음)
                pdf_data.seek(0)

                result = method_func(pdf_data)

                # 추출이 성공하고 의미있는 텍스트가 있는지 확인
                if result["success"] and result["text"].strip():
                    logger.info(
                        f"✅ {method_name}로 텍스트 추출 성공 (텍스트 길이: {len(result['text'])} 문자)"
                    )
                    result["method"] = method_name
                    return result
                else:
                    logger.debug(f"⚠️ {method_name}로 추출했지만 텍스트가 비어있음")

            except Exception as e:
                logger.debug(f"❌ {method_name} 라이브러리 오류: {str(e)}")
                continue

        # 모든 방법이 실패한 경우
        error_msg = "모든 PDF 처리 방법이 실패했습니다"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "text": "",
            "pages": [],
            "method": "none",
            "error": error_msg,
        }

    def _extract_with_pdfplumber(
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

    def _extract_with_pymupdf(
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

    def _extract_with_pypdf(
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

    def _extract_with_pypdf2(
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

    def _extract_with_pdfminer(
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
    if isinstance(source, str):
        # URL인지 파일 경로인지 판단
        parsed = urlparse(source)
        if parsed.scheme in ("http", "https"):
            # URL인 경우
            return pdf_reader.extract_text_from_url(source)
        else:
            # 파일 경로인 경우
            return pdf_reader.extract_text_from_file(source)

    elif isinstance(source, Path):
        # Path 객체인 경우
        return pdf_reader.extract_text_from_file(source)

    elif isinstance(source, io.BytesIO):
        # 바이너리 데이터인 경우
        return pdf_reader.extract_text_from_bytes(source)

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
