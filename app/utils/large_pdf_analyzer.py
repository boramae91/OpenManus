#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 대용량 PDF 보고서 분석 시스템

이 시스템은 60만 글자 정도의 대용량 사업보고서나 분기보고서를 처리하는 전문 도구입니다.
마치 숙련된 재무분석가가 두꺼운 보고서를 체계적으로 분석하는 것처럼,
AI가 단계별로 꼼꼼히 분석해서 JSON 파일로 정리해 줍니다.

🔍 주요 기능:
1. 대용량 PDF 텍스트 추출 (무제한 크기)
2. 스마트 섹션 분할 (재무제표, 주석, 경영진단 등)
3. 섹션별 AI 전문 분석
4. 통합 리포트 생성
5. 구조화된 JSON 결과 저장
"""

import asyncio
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from loguru import logger

from app.agent.manus import Manus

# OpenManus 모듈들 import
from app.llm import LLM
from app.utils.pdf_reader import ChunkProcessor, PDFReader


class LargePDFAnalyzer:
    """
    대용량 PDF 보고서 전문 분석 시스템

    이 클래스는 대용량 PDF를 처리하는 전문가입니다:
    - 60만 글자도 안전하게 처리할 수 있어요
    - 보고서 구조를 자동으로 파악해요
    - 각 섹션을 전문적으로 분석해요
    - 결과를 체계적으로 정리해서 JSON으로 저장해요
    """

    def __init__(self, llm: LLM = None):
        """
        시스템 초기화

        Args:
            llm: OpenAI GPT-4o를 사용하는 언어모델 (없으면 자동 생성)
        """
        logger.info("🚀 대용량 PDF 분석 시스템 초기화 중...")

        # AI 에이전트들 초기화
        self.llm = llm if llm else LLM()
        self.manus_agent = Manus(llm=self.llm)

        # PDF 처리기 초기화 (무제한 크기로 설정)
        self.pdf_reader = PDFReader(max_chars=1000000)  # 100만자로 설정 (None 대신)
        self.chunk_processor = ChunkProcessor(
            chunk_size=25000,  # 25KB 청크 (더 큰 청크로 효율성 향상)
            overlap_size=2000,  # 2KB 겹침 (맥락 보존)
        )

        # 분석 결과 저장용
        self.analysis_results = {}

        logger.info("✅ 대용량 PDF 분석 시스템 초기화 완료!")
        logger.info(
            f"📊 설정값: 청크크기={self.chunk_processor.chunk_size:,}자, 겹침={self.chunk_processor.overlap_size:,}자"
        )

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

        60만 글자도 안전하게 처리할 수 있도록 최적화되어 있어요.
        여러 PDF 라이브러리를 시도해서 가장 좋은 결과를 얻습니다.

        Args:
            pdf_path: PDF 파일 경로

        Returns:
            Dict: 추출 결과와 메타데이터
        """
        try:
            # PDF 파일 존재 확인
            if not os.path.exists(pdf_path):
                return {
                    "success": False,
                    "error": f"PDF 파일을 찾을 수 없습니다: {pdf_path}",
                }

            # 무제한 크기로 PDF 텍스트 추출
            from app.utils.pdf_reader import extract_pdf_text

            logger.info(f"📄 PDF 텍스트 추출 시도: {pdf_path}")
            pdf_result = extract_pdf_text(pdf_path)

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
                "extraction_method": pdf_result.get("extraction_method", "unknown"),
                "pages_processed": pdf_result.get("pages", []),
                "total_pages": len(pdf_result.get("pages", [])),
            }

        except Exception as e:
            logger.error(f"❌ PDF 텍스트 추출 중 오류: {str(e)}")
            return {"success": False, "error": f"PDF 텍스트 추출 오류: {str(e)}"}

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


# 사용 예시 함수
async def analyze_large_pdf_report(
    pdf_path: str, company_name: str = "", report_type: str = "사업보고서"
) -> Dict[str, Any]:
    """
    대용량 PDF 보고서 분석 간편 함수

    사용법:
    result = await analyze_large_pdf_report(
        pdf_path="reports/삼성전자_2024_사업보고서.pdf",
        company_name="삼성전자",
        report_type="사업보고서"
    )
    """
    analyzer = LargePDFAnalyzer()
    return await analyzer.analyze_large_report(
        pdf_path=pdf_path, company_name=company_name, report_type=report_type
    )


if __name__ == "__main__":
    # 테스트 실행 예시
    async def main():
        result = await analyze_large_pdf_report(
            pdf_path="test_report.pdf",
            company_name="테스트회사",
            report_type="분기보고서",
        )
        print(f"분석 완료: {result['metadata']['success']}")
        if result["metadata"]["success"]:
            print(f"저장 경로: {result['metadata']['save_path']}")

    # asyncio.run(main())
