# 긴 텍스트를 여러 부분으로 나누어 처리하는 향상된 콘텐츠 프로세서예요
# 마치 긴 책을 여러 챕터로 나누어 읽는 것처럼 텍스트를 효율적으로 관리해요!

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ContentChunk:
    """콘텐츠 조각을 나타내는 클래스예요"""

    content: str  # 실제 텍스트 내용
    chunk_number: int  # 조각 번호
    total_chunks: int  # 전체 조각 개수
    start_position: int  # 시작 위치
    end_position: int  # 끝 위치
    metadata: Dict[str, Any]  # 추가 정보들


class EnhancedContentProcessor:
    """
    향상된 콘텐츠 프로세서 클래스예요
    긴 텍스트를 의미 있는 단위로 나누어서 모든 내용을 볼 수 있게 해줘요
    """

    def __init__(self, max_chunk_size: int = 5000, overlap_size: int = 200):
        """
        콘텐츠 프로세서를 초기화하는 함수예요

        매개변수:
            max_chunk_size: 한 조각의 최대 크기 (글자 수) - 기본값을 5000으로 늘림
            overlap_size: 조각들 사이의 겹치는 부분 크기 (연결성을 위해)
        """
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size

        # 문장 구분을 위한 패턴들
        self.sentence_patterns = [
            r"[.!?]\s+",  # 영어 문장 끝
            r"[.!?。！？]\s*",  # 한국어/일본어 문장 끝
            r"\n\s*\n",  # 빈 줄 (단락 구분)
            r":\s*\n",  # 콜론 후 줄바꿈
        ]

    def process_long_content(
        self, content: str, source_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        긴 콘텐츠를 처리해서 모든 내용을 볼 수 있게 하는 주요 함수예요

        입력:
            content: 처리할 긴 텍스트
            source_info: 원본 정보 (URL, 제목 등)

        출력:
            처리된 결과 딕셔너리 (조각들과 요약 정보 포함)
        """
        if not content:
            return {
                "success": False,
                "error": "처리할 콘텐츠가 없습니다.",
                "chunks": [],
                "summary": {},
            }

        print(f"🔍 긴 콘텐츠 처리 시작: {len(content):,}자")

        # 콘텐츠가 짧으면 그대로 반환
        if len(content) <= self.max_chunk_size:
            return {
                "success": True,
                "total_length": len(content),
                "chunks": [
                    {
                        "chunk_number": 1,
                        "total_chunks": 1,
                        "content": content,
                        "length": len(content),
                        "preview": (
                            content[:200] + "..." if len(content) > 200 else content
                        ),
                    }
                ],
                "summary": {
                    "total_chunks": 1,
                    "total_length": len(content),
                    "needs_splitting": False,
                },
                "full_content": content,
            }

        # 긴 콘텐츠를 조각으로 나누기
        chunks = self._split_content(content, source_info)

        # 결과 구성
        result = {
            "success": True,
            "total_length": len(content),
            "chunks": [],
            "summary": {
                "total_chunks": len(chunks),
                "total_length": len(content),
                "average_chunk_length": len(content) // len(chunks) if chunks else 0,
                "needs_splitting": True,
                "split_reason": f"원본이 {len(content):,}자로 제한({self.max_chunk_size:,}자)을 초과함",
            },
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
                    chunk.content[:200] + "..."
                    if len(chunk.content) > 200
                    else chunk.content
                ),
            }
            result["chunks"].append(chunk_data)

        print(f"✅ 콘텐츠 처리 완료: {len(chunks)}개 조각, {len(content):,}자")

        return result

    def _split_content(
        self, content: str, source_info: Dict[str, Any] = None
    ) -> List[ContentChunk]:
        """
        콘텐츠를 여러 조각으로 나누는 내부 함수예요
        """
        chunks = []
        current_pos = 0

        while current_pos < len(content):
            # 현재 위치에서 최대 크기만큼의 텍스트 추출
            end_pos = min(current_pos + self.max_chunk_size, len(content))
            candidate_text = content[current_pos:end_pos]

            # 마지막 조각이 아니라면 적절한 분할점 찾기
            if end_pos < len(content):
                best_split_pos = self._find_best_split_position(candidate_text)
                actual_end_pos = current_pos + best_split_pos
            else:
                actual_end_pos = end_pos

            # 조각 생성
            chunk_content = content[current_pos:actual_end_pos].strip()
            if chunk_content:  # 빈 조각은 제외
                chunk = ContentChunk(
                    content=chunk_content,
                    chunk_number=len(chunks) + 1,
                    total_chunks=0,  # 나중에 설정
                    start_position=current_pos,
                    end_position=actual_end_pos,
                    metadata=source_info or {},
                )
                chunks.append(chunk)

            # 다음 위치로 이동 (겹치는 부분 고려)
            current_pos = max(actual_end_pos - self.overlap_size, actual_end_pos)

        # 전체 조각 수 설정
        for chunk in chunks:
            chunk.total_chunks = len(chunks)

        return chunks

    def _find_best_split_position(self, text: str) -> int:
        """
        텍스트에서 가장 적절한 분할 위치를 찾는 함수예요
        문장 끝이나 단락 구분점을 우선적으로 찾아요
        """
        # 1차: 단락 구분점 찾기 (빈 줄)
        paragraph_matches = list(re.finditer(r"\n\s*\n", text))
        if paragraph_matches:
            # 텍스트 뒤쪽 70% 지점 이후의 단락 구분점 선택
            target_pos = len(text) * 0.7
            for match in paragraph_matches:
                if match.start() >= target_pos:
                    return match.end()

        # 2차: 문장 끝 찾기
        for pattern in self.sentence_patterns:
            matches = list(re.finditer(pattern, text))
            if matches:
                # 텍스트 뒤쪽 80% 지점 이후의 문장 끝 선택
                target_pos = len(text) * 0.8
                for match in matches:
                    if match.start() >= target_pos:
                        return match.end()

        # 3차: 단어 경계 찾기 (공백 위치)
        words = text.split()
        if len(words) > 1:
            # 뒤쪽 90% 지점 이후의 공백 찾기
            target_pos = len(text) * 0.9
            current_pos = 0
            for word in words[:-1]:  # 마지막 단어는 제외
                current_pos += len(word) + 1  # +1은 공백
                if current_pos >= target_pos:
                    return current_pos

        # 4차: 그냥 최대 길이로 자르기 (최후 수단)
        return len(text)

    def get_all_chunks_formatted(self, processed_result: Dict[str, Any]) -> str:
        """
        모든 조각을 보기 좋게 포맷팅해서 반환하는 함수예요
        """
        if not processed_result.get("chunks"):
            return "📭 처리된 조각이 없습니다."

        summary = processed_result["summary"]
        chunks = processed_result["chunks"]

        output_lines = [
            "🔍 **전체 콘텐츠 처리 결과**",
            "=" * 50,
            f"📊 **통계 정보:**",
            f"   • 전체 길이: {summary['total_length']:,}자",
            f"   • 조각 개수: {summary['total_chunks']}개",
            f"   • 평균 조각 크기: {summary['average_chunk_length']:,}자",
            "",
        ]

        if summary.get("needs_splitting"):
            output_lines.append(f"⚠️ **분할 이유:** {summary['split_reason']}")
            output_lines.append("")

        output_lines.append(f"📝 **조각별 내용:**")

        for chunk in chunks:
            output_lines.extend(
                [
                    "",
                    f"**🔸 조각 {chunk['chunk_number']}/{chunk['total_chunks']} ({chunk['length']:,}자)**",
                    f"위치: {chunk['position']['start']:,} ~ {chunk['position']['end']:,}",
                    "```",
                    chunk["content"],
                    "```",
                ]
            )

        output_lines.extend(["", "✅ **모든 내용이 여기에 표시되었습니다!**", "=" * 50])

        return "\n".join(output_lines)


# 편의 함수들
def display_all_content(text: str, max_chunk_size: int = 5000) -> str:
    """
    긴 텍스트를 모두 표시하는 편의 함수예요
    """
    processor = EnhancedContentProcessor(max_chunk_size=max_chunk_size)
    result = processor.process_long_content(text)
    return processor.get_all_chunks_formatted(result)
