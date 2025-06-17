# 긴 텍스트를 여러 부분으로 나누어 처리하는 유틸리티 모듈이에요
# 마치 긴 책을 여러 챕터로 나누어 읽는 것처럼 텍스트를 효율적으로 관리해요!

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from loguru import logger


@dataclass
class TextChunk:
    """텍스트 조각을 나타내는 클래스예요"""

    content: str  # 실제 텍스트 내용 (상자 안에 담긴 글자들)
    chunk_number: int  # 조각 번호 (몇 번째 조각인지)
    total_chunks: int  # 전체 조각 개수 (전체가 몇 개로 나뉘었는지)
    start_position: int  # 시작 위치 (원본에서 어디서 시작하는지)
    end_position: int  # 끝 위치 (원본에서 어디서 끝나는지)
    metadata: Dict[str, Any]  # 추가 정보들 (메모나 설명들)


class SmartTextSplitter:
    """
    똑똑한 텍스트 분할기 클래스예요
    긴 텍스트를 의미 있는 단위로 나누어서 모든 내용을 볼 수 있게 해줘요
    """

    def __init__(
        self,
        max_chunk_size: int = 2000,
        overlap_size: int = 100,
        preserve_structure: bool = True,
    ):
        """
        텍스트 분할기를 초기화하는 함수예요

        매개변수:
            max_chunk_size: 한 조각의 최대 크기 (글자 수)
            overlap_size: 조각들 사이의 겹치는 부분 크기 (연결성을 위해)
            preserve_structure: 문장이나 단락 구조를 보존할지 여부
        """
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
        self.preserve_structure = preserve_structure

        # 문장 구분을 위한 패턴들 (마침표, 느낌표, 물음표 등)
        self.sentence_patterns = [
            r"[.!?]\s+",  # 영어 문장 끝
            r"[.!?。！？]\s*",  # 한국어/일본어 문장 끝
            r"\n\s*\n",  # 빈 줄 (단락 구분)
            r":\s*\n",  # 콜론 후 줄바꿈
        ]

        # 단락 구분을 위한 패턴들
        self.paragraph_patterns = [
            r"\n\s*\n",  # 빈 줄
            r"\n[-•*]\s+",  # 목록 항목
            r"\n\d+\.\s+",  # 번호 목록
            r"\n#{1,6}\s+",  # 마크다운 헤더
        ]

    def split_text(
        self, text: str, source_info: Dict[str, Any] = None
    ) -> List[TextChunk]:
        """
        텍스트를 여러 조각으로 나누는 주요 함수예요

        입력:
            text: 나눌 텍스트 (긴 문서나 웹페이지 내용)
            source_info: 원본 정보 (URL, 제목 등)

        출력:
            TextChunk 객체들의 리스트 (나뉘어진 텍스트 조각들)
        """
        if not text or len(text) <= self.max_chunk_size:
            # 텍스트가 없거나 충분히 짧으면 그대로 반환
            return [
                TextChunk(
                    content=text,
                    chunk_number=1,
                    total_chunks=1,
                    start_position=0,
                    end_position=len(text) if text else 0,
                    metadata=source_info or {},
                )
            ]

        logger.info(
            f"📖 긴 텍스트 분할 시작: {len(text):,}자 → 예상 {(len(text) // self.max_chunk_size) + 1}개 조각"
        )

        if self.preserve_structure:
            # 구조를 보존하면서 분할 (더 똑똑한 방법)
            chunks = self._split_with_structure_preservation(text)
        else:
            # 단순 분할 (빠르지만 문장이 잘릴 수 있음)
            chunks = self._split_simple(text)

        # 조각들에 메타데이터 추가
        for i, chunk in enumerate(chunks):
            chunk.chunk_number = i + 1
            chunk.total_chunks = len(chunks)
            chunk.metadata.update(source_info or {})
            chunk.metadata.update(
                {
                    "original_length": len(text),
                    "chunk_length": len(chunk.content),
                    "split_method": (
                        "structure_preserved" if self.preserve_structure else "simple"
                    ),
                }
            )

        logger.info(f"✅ 텍스트 분할 완료: {len(chunks)}개 조각 생성")
        return chunks

    def _split_with_structure_preservation(self, text: str) -> List[TextChunk]:
        """
        문장과 단락 구조를 보존하면서 텍스트를 분할하는 함수예요
        마치 책을 챕터별로 나누되, 문장 중간에서 자르지 않는 것처럼요
        """
        chunks = []
        current_pos = 0

        while current_pos < len(text):
            # 현재 위치에서 최대 크기만큼의 텍스트 추출
            end_pos = min(current_pos + self.max_chunk_size, len(text))
            candidate_text = text[current_pos:end_pos]

            # 마지막 조각이 아니라면 적절한 분할점 찾기
            if end_pos < len(text):
                best_split_pos = self._find_best_split_position(candidate_text)
                actual_end_pos = current_pos + best_split_pos
            else:
                actual_end_pos = end_pos

            # 조각 생성
            chunk_content = text[current_pos:actual_end_pos].strip()
            if chunk_content:  # 빈 조각은 제외
                chunk = TextChunk(
                    content=chunk_content,
                    chunk_number=0,  # 나중에 설정
                    total_chunks=0,  # 나중에 설정
                    start_position=current_pos,
                    end_position=actual_end_pos,
                    metadata={},
                )
                chunks.append(chunk)

            # 다음 위치로 이동 (겹치는 부분 고려)
            current_pos = max(actual_end_pos - self.overlap_size, actual_end_pos)

        return chunks

    def _find_best_split_position(self, text: str) -> int:
        """
        텍스트에서 가장 적절한 분할 위치를 찾는 함수예요
        문장 끝이나 단락 구분점을 우선적으로 찾아요
        """
        # 1차: 단락 구분점 찾기 (가장 좋은 분할점)
        for pattern in self.paragraph_patterns:
            matches = list(re.finditer(pattern, text))
            if matches:
                # 텍스트 뒤쪽 70% 지점 이후의 단락 구분점 선택
                target_pos = len(text) * 0.7
                best_match = None
                for match in matches:
                    if match.start() >= target_pos:
                        best_match = match
                        break
                if best_match:
                    return best_match.end()

        # 2차: 문장 끝 찾기
        for pattern in self.sentence_patterns:
            matches = list(re.finditer(pattern, text))
            if matches:
                # 텍스트 뒤쪽 80% 지점 이후의 문장 끝 선택
                target_pos = len(text) * 0.8
                best_match = None
                for match in matches:
                    if match.start() >= target_pos:
                        best_match = match
                        break
                if best_match:
                    return best_match.end()

        # 3차: 단어 경계 찾기 (공백 위치)
        words = text.split()
        if len(words) > 1:
            # 뒤쪽 80% 지점 이후의 공백 찾기
            target_pos = len(text) * 0.8
            current_pos = 0
            for word in words[:-1]:  # 마지막 단어는 제외
                current_pos += len(word) + 1  # +1은 공백
                if current_pos >= target_pos:
                    return current_pos

        # 4차: 그냥 최대 길이로 자르기 (최후 수단)
        return len(text)

    def _split_simple(self, text: str) -> List[TextChunk]:
        """
        단순하게 길이만 고려해서 텍스트를 분할하는 함수예요
        빠르지만 문장 중간에서 잘릴 수 있어요
        """
        chunks = []
        for i in range(0, len(text), self.max_chunk_size - self.overlap_size):
            start_pos = i
            end_pos = min(i + self.max_chunk_size, len(text))

            chunk_content = text[start_pos:end_pos].strip()
            if chunk_content:
                chunk = TextChunk(
                    content=chunk_content,
                    chunk_number=0,  # 나중에 설정
                    total_chunks=0,  # 나중에 설정
                    start_position=start_pos,
                    end_position=end_pos,
                    metadata={},
                )
                chunks.append(chunk)

        return chunks

    def merge_chunks(self, chunks: List[TextChunk]) -> str:
        """
        분할된 조각들을 다시 하나로 합치는 함수예요
        겹치는 부분은 제거해서 원본과 최대한 동일하게 복원해요
        """
        if not chunks:
            return ""

        if len(chunks) == 1:
            return chunks[0].content

        # 첫 번째 조각부터 시작
        merged_text = chunks[0].content

        for i in range(1, len(chunks)):
            current_chunk = chunks[i].content

            # 이전 조각과의 겹치는 부분 찾기
            overlap = self._find_overlap(merged_text, current_chunk)

            # 겹치는 부분 제거하고 추가
            if overlap > 0:
                merged_text += current_chunk[overlap:]
            else:
                merged_text += " " + current_chunk  # 연결 단어 추가

        return merged_text

    def _find_overlap(self, text1: str, text2: str) -> int:
        """
        두 텍스트 사이의 겹치는 부분의 길이를 찾는 함수예요
        """
        max_overlap = min(len(text1), len(text2), self.overlap_size)

        for i in range(max_overlap, 0, -1):
            if text1[-i:] == text2[:i]:
                return i

        return 0

    def get_chunk_summary(self, chunks: List[TextChunk]) -> Dict[str, Any]:
        """
        분할된 조각들의 요약 정보를 제공하는 함수예요
        """
        if not chunks:
            return {}

        total_length = sum(len(chunk.content) for chunk in chunks)

        return {
            "total_chunks": len(chunks),
            "total_length": total_length,
            "average_chunk_length": total_length // len(chunks),
            "max_chunk_length": max(len(chunk.content) for chunk in chunks),
            "min_chunk_length": min(len(chunk.content) for chunk in chunks),
            "original_length": chunks[0].metadata.get("original_length", 0),
            "split_method": chunks[0].metadata.get("split_method", "unknown"),
            "coverage_percentage": (
                total_length / chunks[0].metadata.get("original_length", 1)
            )
            * 100,
        }


class EnhancedContentExtractor:
    """
    향상된 콘텐츠 추출기 클래스예요
    기존 도구들의 길이 제한을 우회해서 모든 내용을 추출할 수 있어요
    """

    def __init__(self, text_splitter: SmartTextSplitter = None):
        """
        콘텐츠 추출기를 초기화하는 함수예요
        """
        self.text_splitter = text_splitter or SmartTextSplitter(
            max_chunk_size=5000,  # 더 큰 조각 크기 사용
            overlap_size=200,
            preserve_structure=True,
        )

    def extract_full_content(
        self, content: str, source_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        전체 내용을 추출하고 구조화하는 함수예요
        길이 제한 없이 모든 내용을 처리할 수 있어요
        """
        logger.info(f"🔍 전체 콘텐츠 추출 시작: {len(content):,}자")

        # 텍스트를 조각으로 분할
        chunks = self.text_splitter.split_text(content, source_info)

        # 요약 정보 생성
        summary = self.text_splitter.get_chunk_summary(chunks)

        # 결과 구조화
        result = {
            "extraction_info": {
                "success": True,
                "total_length": len(content),
                "chunks_created": len(chunks),
                "extraction_method": "enhanced_full_extraction",
                "timestamp": None,  # 필요시 추가
            },
            "content_summary": summary,
            "chunks": [],
            "full_content": content,  # 전체 내용도 보관
        }

        # 각 조각을 구조화해서 추가
        for chunk in chunks:
            chunk_data = {
                "chunk_number": chunk.chunk_number,
                "total_chunks": chunk.total_chunks,
                "content": chunk.content,
                "length": len(chunk.content),
                "position": {"start": chunk.start_position, "end": chunk.end_position},
                "preview": (
                    chunk.content[:100] + "..."
                    if len(chunk.content) > 100
                    else chunk.content
                ),
                "metadata": chunk.metadata,
            }
            result["chunks"].append(chunk_data)

        logger.info(
            f"✅ 전체 콘텐츠 추출 완료: {len(chunks)}개 조각, {len(content):,}자"
        )

        return result

    def print_chunks_summary(self, extraction_result: Dict[str, Any]) -> str:
        """
        추출된 조각들의 요약을 예쁘게 출력하는 함수예요
        """
        if not extraction_result.get("chunks"):
            return "📭 추출된 내용이 없습니다."

        summary = extraction_result["content_summary"]
        chunks = extraction_result["chunks"]

        output_lines = [
            "🔍 **전체 콘텐츠 추출 결과**",
            "=" * 50,
            f"📊 **통계 정보:**",
            f"   • 전체 길이: {summary['original_length']:,}자",
            f"   • 조각 개수: {summary['total_chunks']}개",
            f"   • 평균 조각 크기: {summary['average_chunk_length']:,}자",
            f"   • 커버리지: {summary['coverage_percentage']:.1f}%",
            "",
            f"📝 **조각별 미리보기:**",
        ]

        for chunk in chunks:
            output_lines.extend(
                [
                    f"",
                    f"**🔸 조각 {chunk['chunk_number']}/{chunk['total_chunks']} ({chunk['length']:,}자)**",
                    f"```",
                    chunk["preview"],
                    f"```",
                ]
            )

        output_lines.extend(
            [
                "",
                "💡 **전체 내용 보기:** 각 조각을 개별적으로 확인하거나 전체 병합 내용을 요청하세요!",
                "=" * 50,
            ]
        )

        return "\n".join(output_lines)


# 편의 함수들
def split_long_text(text: str, max_size: int = 2000) -> List[str]:
    """
    긴 텍스트를 간단하게 나누는 편의 함수예요
    """
    splitter = SmartTextSplitter(max_chunk_size=max_size)
    chunks = splitter.split_text(text)
    return [chunk.content for chunk in chunks]


def extract_full_content_simple(content: str) -> Dict[str, Any]:
    """
    전체 내용을 간단하게 추출하는 편의 함수예요
    """
    extractor = EnhancedContentExtractor()
    return extractor.extract_full_content(content)
