# -*- coding: utf-8 -*-
"""
Enhanced DART API 재무데이터 수집기
실제 DART API를 활용한 한국 기업 상세 정보 수집 도구

주요 기능:
1. 상세한 재무정보 (단일회사 주요계정, 연결재무제표 등)
2. 기업 지배구조 정보 (임원, 주주, 보수 등)
3. 투자정보 (배당, 증자감자, 자기주식 등)
4. 실시간 공시 모니터링 (최신 공시, 중요 공시 등)
5. 🚀 사업보고서/분기보고서 원문 다운로드 및 목차별 딕셔너리 생성 (NEW!)
"""

import io
import json
import time
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from app.logger import logger


class EnhancedDartDataCollector:
    """
    DART API를 활용한 확장 재무데이터 수집기
    실제 DART 엔드포인트들을 호출해서 상세한 기업 정보를 수집해요!
    + 🚀 사업보고서/분기보고서 원문 다운로드 및 목차별 딕셔너리 생성 기능 추가!
    """

    def __init__(self, dart_api_key: Optional[str] = None):
        """
        Enhanced DART API 수집기 초기화

        Args:
            dart_api_key: DART API 키
        """
        self.dart_api_key = dart_api_key
        self.base_url = "https://opendart.fss.or.kr/api"
        self.api_delay = 0.1  # API 호출 간격 (초)

        # DART API 엔드포인트 정의
        self.endpoints = {
            # 재무정보
            "single_account": "/fnlttSinglAcnt.json",  # 단일회사 주요계정
            "multi_account": "/fnlttMultiAcnt.json",  # 다중회사 주요계정
            "company_info": "/company.json",  # 기업개황
            # 지배구조 정보
            "executives": "/exctvSttus.json",  # 임원현황
            "major_shareholders": "/hyslrSttus.json",  # 최대주주현황
            "director_compensation": "/rmunSttus.json",  # 이사보수현황
            "outside_directors": "/otcpSttus.json",  # 사외이사현황
            # 투자정보
            "dividends": "/alotMatter.json",  # 배당정보
            "capital_changes": "/irdsSttus.json",  # 증자감자현황
            "treasury_stock": "/tsstk.json",  # 자기주식현황
            "investments": "/otrCprInvstmntSttus.json",  # 타법인출자현황
            # 공시정보
            "disclosures": "/list.json",  # 공시검색
            "corp_code": "/corpCode.xml",  # 고유번호
            # 🚀 보고서 원문 관련 (FIXED!)
            "document": "/document.xml",  # 보고서 원문 (XML 형식)
        }

        # 🚀 대용량 PDF 분석기 지연 로딩을 위한 참조
        self._large_pdf_analyzer = None

        logger.info("📊 Enhanced DART API 수집기가 초기화되었습니다")

    def is_available(self) -> bool:
        """DART API 사용 가능 여부 확인"""
        return self.dart_api_key is not None

    @property
    def large_pdf_analyzer(self):
        """🚀 LargePDFAnalyzer 지연 로딩 - 필요할 때만 import하여 순환 참조 방지"""
        if self._large_pdf_analyzer is None:
            try:
                from app.llm import LLM
                from app.utils.large_pdf_analyzer import LargePDFAnalyzer

                llm = LLM()
                self._large_pdf_analyzer = LargePDFAnalyzer(llm=llm)
                logger.info("✅ LargePDFAnalyzer 지연 로딩 완료")
            except Exception as e:
                logger.warning(f"⚠️ LargePDFAnalyzer 로딩 실패: {e}")
                self._large_pdf_analyzer = None
        return self._large_pdf_analyzer

    # ==================== 🚀 사업보고서/분기보고서 원문 다운로드 ====================

    async def get_business_reports_with_dictionary(
        self, corp_code: str, company_name: str = "분석대상회사", bsns_year: str = None
    ) -> Dict[str, Any]:
        """
        🚀 사업보고서와 분기보고서를 다운로드해서 전문가 에이전트에게 바로 피딩 가능한 딕셔너리로 변환!

        기존의 Manus Agent가 웹에서 PDF를 찾지 못하는 문제를 해결하기 위해
        DART API에서 직접 사업보고서 원문을 가져와서 전문가별로 최적화된 딕셔너리를 생성해요!

        Args:
            corp_code: 기업 고유코드 (8자리)
            company_name: 회사명
            bsns_year: 사업연도 (기본값: 작년)

        Returns:
            Dict: {
                "success": bool,
                "business_report_dictionary": Dict[str, str],  # 사업보고서 목차별 딕셔너리
                "quarterly_report_dictionary": Dict[str, str],  # 최신 분기보고서 목차별 딕셔너리
                "expert_ready_dictionaries": Dict,  # 🚀 전문가별 바로 사용 가능한 딕셔너리
                "metadata": Dict,
                "error": str (실패 시)
            }
        """
        if not self.is_available():
            return {"success": False, "error": "DART API 키가 설정되지 않았습니다"}

        if not bsns_year:
            bsns_year = str(datetime.now().year - 1)

        logger.info(
            f"🚀 {company_name}({corp_code}) 전문가 에이전트용 DART 딕셔너리 생성 시작..."
        )

        try:
            result = {
                "success": True,
                "corp_code": corp_code,
                "company_name": company_name,
                "bsns_year": bsns_year,
                "collected_at": datetime.now().isoformat(),
                "business_report_dictionary": {},
                "quarterly_report_dictionary": {},
                "expert_ready_dictionaries": {},  # 🚀 전문가별 바로 사용 가능한 딕셔너리
                "metadata": {},
            }

            # 1️⃣ 사업보고서 다운로드 및 딕셔너리 변환
            logger.info("📋 1단계: 사업보고서 다운로드 및 딕셔너리 변환...")
            business_report_result = await self._download_and_process_report(
                corp_code=corp_code,
                company_name=company_name,
                bsns_year=bsns_year,
                report_type="business_report",  # 사업보고서
            )

            if business_report_result.get("success"):
                result["business_report_dictionary"] = business_report_result.get(
                    "pdf_dictionary", {}
                )
                logger.info(
                    f"✅ 사업보고서 딕셔너리 생성 완료: {len(result['business_report_dictionary'])}개 섹션"
                )
            else:
                logger.warning(
                    f"⚠️ 사업보고서 처리 실패: {business_report_result.get('error')}"
                )

            # 2️⃣ 최신 분기보고서 다운로드 및 딕셔너리 변환 (토큰 절약을 위해 비활성화)
            # logger.info("📋 2단계: 최신 분기보고서 다운로드 및 딕셔너리 변환...")
            # quarterly_report_result = await self._download_and_process_report(
            #     corp_code=corp_code,
            #     company_name=company_name,
            #     bsns_year=bsns_year,
            #     report_type="quarterly_report",  # 분기보고서
            # )

            # if quarterly_report_result.get("success"):
            #     result["quarterly_report_dictionary"] = quarterly_report_result.get(
            #         "pdf_dictionary", {}
            #     )
            #     logger.info(
            #         f"✅ 분기보고서 딕셔너리 생성 완료: {len(result['quarterly_report_dictionary'])}개 섹션"
            #     )
            # else:
            #     logger.warning(
            #         f"⚠️ 분기보고서 처리 실패: {quarterly_report_result.get('error')}"
            #     )

            logger.info("🚫 분기보고서 딕셔너리 생성 비활성화 (토큰 절약)")
            result["quarterly_report_dictionary"] = {}  # 빈 딕셔너리로 설정

            # 3️⃣ 전문가별 바로 사용 가능한 딕셔너리 생성 (🚀 핵심 개선!)
            logger.info("🎯 3단계: 전문가별 바로 사용 가능한 딕셔너리 생성...")

            expert_ready_dictionaries = self._create_expert_ready_dictionaries(
                business_dict=result["business_report_dictionary"],
                quarterly_dict=result["quarterly_report_dictionary"],
                company_name=company_name,
                corp_code=corp_code,
                bsns_year=bsns_year,
            )

            result["expert_ready_dictionaries"] = expert_ready_dictionaries
            logger.info(
                f"✅ 전문가별 딕셔너리 생성 완료: {len(expert_ready_dictionaries)}개 전문가 타입"
            )

            # 4️⃣ 메타데이터 생성
            logger.info("🔗 4단계: 메타데이터 생성...")

            # 🚀 분리된 딕셔너리 방식으로 개선!
            business_total_text = sum(
                len(content)
                for content in result["business_report_dictionary"].values()
            )
            quarterly_total_text = sum(
                len(content)
                for content in result["quarterly_report_dictionary"].values()
            )

            # 사업보고서 메타데이터
            business_metadata = {
                "company_name": company_name,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "report_type": "business_report",
                "creation_timestamp": datetime.now().isoformat(),
                "total_sections": len(result["business_report_dictionary"]),
                "total_text_length": business_total_text,
                "avg_section_length": (
                    business_total_text // len(result["business_report_dictionary"])
                    if result["business_report_dictionary"]
                    else 0
                ),
                "source": "dart_api_business_report",
                "processing_method": "enhanced_dart_collector_with_expert_ready_dictionaries",
            }

            # 분기보고서 메타데이터
            quarterly_metadata = {
                "company_name": company_name,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "report_type": "quarterly_report",
                "creation_timestamp": datetime.now().isoformat(),
                "total_sections": len(result["quarterly_report_dictionary"]),
                "total_text_length": quarterly_total_text,
                "avg_section_length": (
                    quarterly_total_text // len(result["quarterly_report_dictionary"])
                    if result["quarterly_report_dictionary"]
                    else 0
                ),
                "source": "dart_api_quarterly_report",
                "processing_method": "enhanced_dart_collector_with_expert_ready_dictionaries",
            }

            result["business_metadata"] = business_metadata
            result["quarterly_metadata"] = quarterly_metadata

            # 🎯 전문가별 딕셔너리 방식 요약 로그
            logger.info(f"🎯 전문가별 딕셔너리 방식 완료!")
            logger.info(
                f"   📄 사업보고서: {len(result['business_report_dictionary'])}개 섹션 ({business_total_text:,}자)"
            )
            logger.info(f"   📈 분기보고서: 비활성화됨 (토큰 절약)")
            logger.info(f"   🚀 CrewAI 전문가별 바로 사용 가능한 딕셔너리 준비 완료!")
            logger.info(f"   💡 시기별 정보를 구분하여 더 정확한 분석 가능!")

            # 📊 섹션 분할 품질 검증 추가
            self._validate_section_quality(result)

            # 5️⃣ 성공 여부 최종 판단
            if (
                result["business_report_dictionary"]
                or result["quarterly_report_dictionary"]
            ):
                logger.info(f"🎉 {company_name} 전문가용 DART 딕셔너리 생성 완료!")

                # 6️⃣ 섹션 품질 검증 수행
                business_quality = self._validate_dart_section_quality(
                    result["business_report_dictionary"], "business"
                )
                quarterly_quality = self._validate_dart_section_quality(
                    result["quarterly_report_dictionary"], "quarterly"
                )

                # 품질 검증 결과 로깅
                self._log_dart_quality_validation(
                    business_quality, quarterly_quality, company_name
                )

                # 7️⃣ 최종 상태 로깅
                logger.info(f"📊 최종 DART 딕셔너리 상태:")
                logger.info(f"   - success 필드: {result['success']}")
                logger.info(
                    f"   - business_report_dictionary: {len(result['business_report_dictionary'])}개 섹션"
                )
                logger.info(f"   - quarterly_report_dictionary: 비활성화됨 (토큰 절약)")
                logger.info(
                    f"   - expert_ready_dictionaries: {len(result['expert_ready_dictionaries'])}개 전문가 타입"
                )

                # 8️⃣ CrewAI 전달용 최종 구조 검증
                logger.info(f"🔍 CrewAI 전달용 최종 구조 검증:")
                logger.info(
                    f"   - expert_ready_dictionaries 타입: {type(result['expert_ready_dictionaries'])}"
                )
                logger.info(
                    f"   - expert_ready_dictionaries 키: {list(result['expert_ready_dictionaries'].keys())}"
                )

                for expert_type, expert_data in result[
                    "expert_ready_dictionaries"
                ].items():
                    logger.info(
                        f"   - {expert_type}: {len(expert_data.get('sections', {}))}개 섹션"
                    )
                    logger.info(
                        f"     - 샘플 키: {list(expert_data.get('sections', {}).keys())[:3]}"
                    )

                logger.info(
                    f"✅ DART 딕셔너리 전달 준비 완료: 사업보고서 {len(result['business_report_dictionary'])}개, 분기보고서 {len(result['quarterly_report_dictionary'])}개 섹션"
                )

            else:
                logger.warning(
                    f"⚠️ {company_name} DART 딕셔너리 생성 실패: 모든 보고서 처리 실패"
                )
                result["success"] = False
                result["error"] = "모든 보고서 처리 실패"

            return result

        except Exception as e:
            error_msg = f"DART 딕셔너리 생성 실패: {str(e)}"
            logger.error(f"❌ {error_msg}")
            logger.error(f"  - 오류 타입: {type(e).__name__}")
            logger.error(f"  - 오류 상세: {str(e)}")

            return {
                "success": False,
                "business_report_dictionary": {},
                "quarterly_report_dictionary": {},
                "expert_ready_dictionaries": {},
                "metadata": {"error": error_msg},
                "error": error_msg,
            }

    def _create_expert_ready_dictionaries(
        self,
        business_dict: Dict[str, str],
        quarterly_dict: Dict[str, str],
        company_name: str,
        corp_code: str,
        bsns_year: str,
    ) -> Dict[str, Any]:
        """
        🚀 전문가별 바로 사용 가능한 딕셔너리 생성

        각 전문가가 바로 사용할 수 있는 형태로 딕셔너리를 구성합니다.
        중간 변환 과정 없이 직접 CrewAI에 전달 가능한 구조입니다.

        Args:
            business_dict: 사업보고서 딕셔너리
            quarterly_dict: 분기보고서 딕셔너리
            company_name: 회사명
            corp_code: 기업코드
            bsns_year: 사업연도

        Returns:
            Dict: 전문가별 딕셔너리
        """
        logger.info(f"🎯 전문가별 딕셔너리 생성 시작: {company_name}")

        # 전문가별 키워드 매핑
        expert_keywords = {
            "integrated_financial_analyst": [
                # 재무 관련
                "재무",
                "손익",
                "매출",
                "순이익",
                "자산",
                "부채",
                "자본",
                "현금흐름",
                "수익성",
                "안정성",
                "회사개요",
                "사업내용",
                "재무제표",
                "손익계산서",
                "재무상태표",
                "현금흐름표",
                "ROE",
                "ROA",
                "ROIC",
                "유동비율",
                "부채비율",
                # 밸류에이션 관련
                "가치",
                "평가",
                "적정가",
                "목표가",
                "DCF",
                "밸류에이션",
                "투자",
                "배당",
                "내재가치",
                "멀티플",
                "PER",
                "PBR",
                "EV/EBITDA",
                # 사업 관련
                "사업",
                "매출",
                "영업",
                "이익",
                "수익",
                "비용",
                "지출",
                "투자",
                "자본",
                "재무",
                "경영",
                "전략",
                "계획",
                "전망",
                "전략",
            ],
            "technical_analyst": [
                # 기술적 분석 관련
                "차트",
                "기술적",
                "technical",
                "pattern",
                "trend",
                "모멘텀",
                "지지선",
                "저항선",
                "이동평균",
                "RSI",
                "MACD",
                "볼린저밴드",
                "거래량",
                "가격",
                "주가",
                "시장",
                "투자",
                "매매",
                "신호",
            ],
        }

        # 전문가별 딕셔너리 생성
        expert_dictionaries = {}

        for expert_type, keywords in expert_keywords.items():
            logger.info(f"🔧 {expert_type} 딕셔너리 생성 중...")

            # 해당 전문가에게 적합한 섹션들 찾기
            relevant_sections = {}

            # 사업보고서에서 관련 섹션 찾기
            for section_title, content in business_dict.items():
                title_lower = section_title.lower()
                content_lower = content.lower()

                # 키워드 매칭 확인
                if any(
                    keyword in title_lower or keyword in content_lower
                    for keyword in keywords
                ):
                    relevant_sections[f"[사업보고서] {section_title}"] = content

            # 분기보고서에서 관련 섹션 찾기
            for section_title, content in quarterly_dict.items():
                title_lower = section_title.lower()
                content_lower = content.lower()

                # 키워드 매칭 확인
                if any(
                    keyword in title_lower or keyword in content_lower
                    for keyword in keywords
                ):
                    relevant_sections[f"[분기보고서] {section_title}"] = content

            # 일반 섹션도 일부 포함 (모든 전문가가 참고할 수 있는 내용)
            general_sections = {}

            # 사업보고서 일반 섹션
            for section_title, content in business_dict.items():
                if section_title not in [
                    s.replace("[사업보고서] ", "") for s in relevant_sections.keys()
                ]:
                    general_sections[f"[사업보고서] {section_title}"] = content
                    if len(general_sections) >= 2:  # 일반 섹션 최대 2개만
                        break

            # 분기보고서 일반 섹션
            for section_title, content in quarterly_dict.items():
                if section_title not in [
                    s.replace("[분기보고서] ", "") for s in relevant_sections.keys()
                ]:
                    general_sections[f"[분기보고서] {section_title}"] = content
                    if len(general_sections) >= 2:  # 일반 섹션 최대 2개만
                        break

            # 관련 섹션과 일반 섹션 합치기
            all_sections = {**relevant_sections, **general_sections}

            # 전문가별 딕셔너리 구성
            expert_dictionaries[expert_type] = {
                "sections": all_sections,
                "metadata": {
                    "expert_type": expert_type,
                    "company_name": company_name,
                    "corp_code": corp_code,
                    "bsns_year": bsns_year,
                    "total_sections": len(all_sections),
                    "relevant_sections": len(relevant_sections),
                    "general_sections": len(general_sections),
                    "total_text_length": sum(
                        len(content) for content in all_sections.values()
                    ),
                    "creation_timestamp": datetime.now().isoformat(),
                    "source": "dart_api_expert_ready_dictionary",
                    "processing_method": "keyword_based_section_selection",
                },
                "keywords_used": keywords,
                "section_types": {
                    "relevant": list(relevant_sections.keys()),
                    "general": list(general_sections.keys()),
                },
            }

            logger.info(f"✅ {expert_type}: {len(all_sections)}개 섹션 생성 완료")
            logger.info(f"   - 관련 섹션: {len(relevant_sections)}개")
            logger.info(f"   - 일반 섹션: {len(general_sections)}개")

        return expert_dictionaries

    def _validate_section_quality(self, result: Dict[str, Any]) -> None:
        """
        📊 섹션 분할 품질을 검증하고 개선 방안을 제시합니다.

        Args:
            result: DART 딕셔너리 생성 결과
        """
        try:
            logger.info("🔍 섹션 분할 품질 검증 시작...")

            # 사업보고서 섹션 품질 검증
            if result.get("business_report_dictionary"):
                business_quality = self._analyze_section_quality(
                    result["business_report_dictionary"], "사업보고서"
                )
                logger.info(f"📄 사업보고서 섹션 품질: {business_quality['score']}/100")

                if business_quality["issues"]:
                    logger.warning(
                        f"⚠️ 사업보고서 섹션 문제점: {', '.join(business_quality['issues'])}"
                    )
                if business_quality["recommendations"]:
                    logger.info(
                        f"💡 사업보고서 개선 방안: {', '.join(business_quality['recommendations'])}"
                    )

            # 분기보고서 섹션 품질 검증
            if result.get("quarterly_report_dictionary"):
                quarterly_quality = self._analyze_section_quality(
                    result["quarterly_report_dictionary"], "분기보고서"
                )
                logger.info(
                    f"📈 분기보고서 섹션 품질: {quarterly_quality['score']}/100"
                )

                if quarterly_quality["issues"]:
                    logger.warning(
                        f"⚠️ 분기보고서 섹션 문제점: {', '.join(quarterly_quality['issues'])}"
                    )
                if quarterly_quality["recommendations"]:
                    logger.info(
                        f"💡 분기보고서 개선 방안: {', '.join(quarterly_quality['recommendations'])}"
                    )

        except Exception as e:
            logger.warning(f"⚠️ 섹션 품질 검증 실패: {e}")

    def _analyze_section_quality(
        self, sections: Dict[str, str], report_type: str
    ) -> Dict[str, Any]:
        """
        📊 개별 섹션들의 품질을 분석합니다.

        Args:
            sections: 섹션 딕셔너리
            report_type: 보고서 유형

        Returns:
            Dict: 품질 분석 결과
        """
        quality_result = {
            "score": 0,
            "issues": [],
            "recommendations": [],
            "section_count": len(sections),
            "total_length": sum(len(content) for content in sections.values()),
            "avg_length": 0,
            "min_length": 0,
            "max_length": 0,
        }

        if not sections:
            quality_result["issues"].append("섹션이 없습니다")
            return quality_result

        # 기본 통계 계산
        lengths = [len(content) for content in sections.values()]
        quality_result["avg_length"] = sum(lengths) // len(lengths)
        quality_result["min_length"] = min(lengths)
        quality_result["max_length"] = max(lengths)

        # 품질 점수 계산 (100점 만점)
        score = 0

        # 1. 섹션 개수 평가 (20점)
        if len(sections) >= 10:
            score += 20
        elif len(sections) >= 5:
            score += 15
        elif len(sections) >= 3:
            score += 10
        else:
            score += 5
            quality_result["issues"].append("섹션 개수가 적습니다")

        # 2. 평균 길이 평가 (30점)
        if quality_result["avg_length"] >= 1000:
            score += 30
        elif quality_result["avg_length"] >= 500:
            score += 25
        elif quality_result["avg_length"] >= 200:
            score += 20
        else:
            score += 10
            quality_result["issues"].append("섹션 내용이 너무 짧습니다")

        # 3. 길이 균형성 평가 (25점)
        length_variance = max(lengths) - min(lengths)
        if length_variance <= 1000:
            score += 25
        elif length_variance <= 2000:
            score += 20
        elif length_variance <= 5000:
            score += 15
        else:
            score += 10
            quality_result["issues"].append("섹션 길이가 균형적이지 않습니다")

        # 4. 제목 품질 평가 (25점)
        meaningful_titles = 0
        for title in sections.keys():
            if len(title) >= 5 and any(
                keyword in title
                for keyword in ["재무", "손익", "현금", "매출", "이익", "자산", "부채"]
            ):
                meaningful_titles += 1

        title_ratio = meaningful_titles / len(sections)
        if title_ratio >= 0.7:
            score += 25
        elif title_ratio >= 0.5:
            score += 20
        elif title_ratio >= 0.3:
            score += 15
        else:
            score += 10
            quality_result["issues"].append("의미있는 제목의 섹션이 적습니다")

        quality_result["score"] = score

        # 개선 방안 제시
        if score < 60:
            quality_result["recommendations"].append("섹션 분할 알고리즘 개선 필요")
        if quality_result["avg_length"] < 500:
            quality_result["recommendations"].append("최소 섹션 길이 증가 필요")
        if length_variance > 5000:
            quality_result["recommendations"].append("섹션 길이 균형 조정 필요")

        return quality_result

    async def _download_and_process_report(
        self,
        corp_code: str,
        company_name: str,
        bsns_year: str,
        report_type: str = "business_report",
    ) -> Dict[str, Any]:
        """
        🚀 특정 보고서를 다운로드하고 목차별 딕셔너리로 처리

        Args:
            corp_code: 기업 고유코드
            company_name: 회사명
            bsns_year: 사업연도
            report_type: "business_report" 또는 "quarterly_report"

        Returns:
            Dict: 처리 결과
        """
        try:
            # 1️⃣ 보고서 종류에 따른 설정
            if report_type == "business_report":
                report_code = "11011"  # 사업보고서
                report_name = "사업보고서"
            elif report_type == "quarterly_report":
                # 🔍 개선된 분기보고서 검색 로직 (시기와 연도 고려)
                # 사용자에게 쉽게 설명하면, 현재 시점에 맞는 분기보고서를 똑똑하게 찾는 과정이에요
                import datetime

                current_month = datetime.datetime.now().month
                current_year = datetime.datetime.now().year

                # 현재 시점에 따른 검색 우선순위 결정 (실제 공시 일정 고려)
                if current_month <= 5:  # 1~5월: 전년도 기준
                    search_years = [str(int(bsns_year) - 1), bsns_year]
                    quarterly_codes = [
                        "11014",
                        # "11012",  # 반기보고서 비활성화 (토큰 절약)
                        "11013",
                    ]  # 3분기 → 1분기 (반기보고서 제외)
                    quarterly_names = ["3분기보고서", "1분기보고서"]
                elif current_month <= 8:  # 6~8월: 1분기보고서 위주
                    search_years = [bsns_year, str(int(bsns_year) - 1)]
                    quarterly_codes = [
                        "11013",
                        "11014",
                        # "11012",  # 반기보고서 비활성화 (토큰 절약)
                    ]  # 1분기 → 3분기 (반기보고서 제외)
                    quarterly_names = ["1분기보고서", "3분기보고서"]
                elif current_month <= 11:  # 9~11월: 반기보고서 위주 (비활성화)
                    search_years = [bsns_year, str(int(bsns_year) - 1)]
                    quarterly_codes = [
                        # "11012",  # 반기보고서 비활성화 (토큰 절약)
                        "11013",
                        "11014",
                    ]  # 1분기 → 3분기 (반기보고서 제외)
                    quarterly_names = ["1분기보고서", "3분기보고서"]
                else:  # 12월: 3분기보고서 위주
                    search_years = [bsns_year, str(int(bsns_year) - 1)]
                    quarterly_codes = [
                        "11014",
                        # "11012",  # 반기보고서 비활성화 (토큰 절약)
                        "11013",
                    ]  # 3분기 → 1분기 (반기보고서 제외)
                    quarterly_names = ["3분기보고서", "1분기보고서"]

                logger.info(
                    f"🗓️ 분기보고서 검색 전략: 현재 {current_month}월 기준 (반기보고서 비활성화)"
                )
                logger.info(f"   - 검색 연도 순서: {', '.join(search_years)}")
                logger.info(
                    f"   - 검색 분기 순서: {', '.join(quarterly_names)} (반기보고서 제외)"
                )

                found_report = False
                for search_year in search_years:
                    if found_report:
                        break
                    logger.info(f"📅 {search_year}년도 분기보고서 검색 중...")

                    for report_code, quarter_name in zip(
                        quarterly_codes, quarterly_names
                    ):
                        logger.info(f"🔍 {search_year}년 {quarter_name} 검색 중...")
                        if await self._check_report_exists(
                            corp_code, search_year, report_code
                        ):
                            report_name = f"{search_year}년 {quarter_name}"
                            bsns_year = search_year  # 찾은 연도로 업데이트
                            logger.info(f"✅ {report_name} 발견!")
                            found_report = True
                            break

                    if not found_report:
                        logger.info(f"⚠️ {search_year}년도 분기보고서 없음")

                if not found_report:
                    # 📋 추가 시도: 최근 3년간 모든 분기보고서 검색
                    logger.info("🔄 최근 3년간 추가 검색 시도 중...")
                    for year_offset in range(2, 5):  # 2~4년 전까지
                        fallback_year = str(int(bsns_year) - year_offset)
                        logger.info(f"📅 {fallback_year}년도 추가 검색...")

                        for report_code, quarter_name in zip(
                            quarterly_codes, quarterly_names
                        ):
                            if await self._check_report_exists(
                                corp_code, fallback_year, report_code
                            ):
                                report_name = f"{fallback_year}년 {quarter_name}"
                                bsns_year = fallback_year
                                logger.info(f"✅ 추가 검색으로 {report_name} 발견!")
                                found_report = True
                                break

                        if found_report:
                            break

                if not found_report:
                    return {
                        "success": False,
                        "error": "분기보고서를 찾을 수 없습니다 (최근 5년간 검색 완료)",
                    }
            else:
                return {
                    "success": False,
                    "error": f"알 수 없는 보고서 타입: {report_type}",
                }

            # 2️⃣ 보고서 목록 조회 (수정된 날짜 범위 검색 방식)
            logger.info(f"📋 {report_name} 목록 조회 중...")
            time.sleep(self.api_delay)

            # 🔧 수정: 보고서 타입별 최적화된 날짜 범위 검색 (더 넓은 범위)
            if report_code == "11011":  # 사업보고서
                # 사업보고서는 다음 연도 전체(1~12월)로 넓게 검색해요
                search_year = int(bsns_year) + 1
                bgn_de = f"{search_year}0101"  # 다음 연도 1월부터
                end_de = f"{search_year}1231"  # 다음 연도 12월까지
            else:  # 분기보고서, 반기보고서
                # 분기보고서는 해당 연도 내에 제출됨
                bgn_de = f"{bsns_year}0101"  # 해당 연도 1월부터
                end_de = f"{bsns_year}1231"  # 해당 연도 12월까지

            params = {
                "crtfc_key": self.dart_api_key,
                "corp_code": corp_code,
                "bgn_de": bgn_de,
                "end_de": end_de,
                "page_count": "100",  # 충분한 개수로 검색
            }

            logger.info(
                f"🔍 검색 매개변수: corp_code={corp_code}, 연도={bsns_year}, 보고서타입={report_code}"
            )

            response = requests.get(
                self.base_url + self.endpoints["disclosures"], params=params
            )

            if response.status_code != 200:
                return {"success": False, "error": f"HTTP 오류: {response.status_code}"}

            data = response.json()

            if data.get("status") != "000":
                return {"success": False, "error": f"API 오류: {data.get('message')}"}

            # 🔧 수정: 특정 보고서 타입 필터링 후 최신 보고서 선택
            all_reports = data.get("list", [])

            # 보고서 코드에 따른 보고서명 매핑
            report_type_map = {
                "11011": "사업보고서",
                # "11012": "반기보고서",  # 반기보고서 비활성화 (토큰 절약)
                "11013": "1분기보고서",
                "11014": "3분기보고서",
            }
            target_report_name = report_type_map.get(report_code, "")

            # 해당 보고서 타입만 필터링
            if target_report_name:
                report_list = [
                    r
                    for r in all_reports
                    if target_report_name in r.get("report_nm", "")
                ]
            else:
                report_list = all_reports

            logger.info(
                f"📊 전체 공시: {len(all_reports)}개, {report_name}: {len(report_list)}개"
            )

            if not report_list:
                return {"success": False, "error": f"{report_name}을 찾을 수 없습니다"}

            # 가장 최신 보고서 선택 (날짜순 정렬)
            sorted_reports = sorted(
                report_list, key=lambda x: x.get("rcept_dt", ""), reverse=True
            )
            latest_report = sorted_reports[0]
            rcept_no = latest_report.get("rcept_no")

            if not rcept_no:
                return {
                    "success": False,
                    "error": f"{report_name} 접수번호를 찾을 수 없습니다",
                }

            logger.info(
                f"📄 {report_name} 발견: {latest_report.get('report_nm')} (접수번호: {rcept_no})"
            )

            # 3️⃣ 보고서 원문 다운로드
            logger.info(f"⬇️ {report_name} 원문 다운로드 중...")
            document_content = await self._download_document_content(rcept_no)

            if not document_content:
                return {"success": False, "error": f"{report_name} 원문 다운로드 실패"}

            # 4️⃣ 텍스트를 임시 파일로 저장하고 LargePDFAnalyzer로 처리
            logger.info(f"🧩 {report_name} 목차별 딕셔너리 변환 중...")

            # LargePDFAnalyzer가 텍스트도 처리할 수 있도록 임시 파일 생성
            import os
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False, encoding="utf-8"
            ) as temp_file:
                temp_file.write(document_content)
                temp_file_path = temp_file.name

            try:
                # LargePDFAnalyzer로 텍스트 기반 딕셔너리 생성
                if self.large_pdf_analyzer:
                    # 🔧 수정: 텍스트 파일인 경우 직접 딕셔너리 생성
                    # DART API에서 다운로드한 텍스트를 PDF처럼 처리하지 말고 텍스트로 처리해요
                    dictionary_result = await self._create_text_based_dictionary(
                        text_content=document_content,
                        company_name=company_name,
                        max_section_size=2000000,  # 🚀 200만자로 확장 (기존 100만자에서 2배 증가)
                        file_path=temp_file_path,
                    )

                    if dictionary_result.get("success"):
                        logger.info(
                            f"✅ {report_name} 딕셔너리 변환 완료: {len(dictionary_result.get('pdf_dictionary', {}))}개 섹션"
                        )
                        return {
                            "success": True,
                            "pdf_dictionary": dictionary_result.get(
                                "pdf_dictionary", {}
                            ),
                            "metadata": dictionary_result.get("metadata", {}),
                            "report_info": {
                                "report_name": report_name,
                                "rcept_no": rcept_no,
                                "corp_code": corp_code,
                                "bsns_year": bsns_year,
                            },
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"텍스트 기반 딕셔너리 생성 실패: {dictionary_result.get('error')}",
                        }
                else:
                    return {
                        "success": False,
                        "error": "LargePDFAnalyzer를 사용할 수 없습니다",
                    }

            finally:
                # 임시 파일 정리
                try:
                    os.unlink(temp_file_path)
                except:
                    pass

        except Exception as e:
            logger.error(f"❌ {report_type} 처리 중 오류: {e}")
            return {"success": False, "error": str(e)}

    async def _check_report_exists(
        self, corp_code: str, bsns_year: str, report_code: str
    ) -> bool:
        """보고서 존재 여부 확인 (Enhanced 디버깅 포함) - 날짜 범위 검색 방식 사용"""
        try:
            time.sleep(self.api_delay)

            # 🔧 수정: 보고서 타입별 최적화된 날짜 범위 검색 (더 넓은 범위)
            if report_code == "11011":  # 사업보고서
                # 사업보고서는 다음 연도 전체(1~12월)로 넓게 검색해요
                search_year = int(bsns_year) + 1
                bgn_de = f"{search_year}0101"  # 다음 연도 1월부터
                end_de = f"{search_year}1231"  # 다음 연도 12월까지
            else:  # 분기보고서, 반기보고서
                # 분기보고서는 해당 연도 내에 제출됨
                bgn_de = f"{bsns_year}0101"  # 해당 연도 1월부터
                end_de = f"{bsns_year}1231"  # 해당 연도 12월까지

            params = {
                "crtfc_key": self.dart_api_key,
                "corp_code": corp_code,
                "bgn_de": bgn_de,
                "end_de": end_de,
                "page_count": "100",  # 충분한 개수로 검색
            }

            # 디버깅을 위한 상세 로깅 (사용자를 위한 한국어 설명)
            # 이 부분은 API 호출 전에 어떤 정보로 요청하는지 확인하는 로그예요
            logger.info(f"🔍 DART API 보고서 확인 요청:")
            logger.info(f"   - 기업코드: {corp_code}")
            logger.info(f"   - 사업연도: {bsns_year}")
            logger.info(f"   - 보고서코드: {report_code}")
            logger.info(
                f"   - API키 설정여부: {'설정됨' if self.dart_api_key else '미설정'}"
            )

            # API 키가 없으면 미리 에러 반환 (사용자에게 친절한 안내)
            if not self.dart_api_key:
                logger.error(
                    "❌ DART API 키가 설정되지 않았습니다. 환경변수 DART_API_KEY를 확인해주세요."
                )
                return False

            response = requests.get(
                self.base_url + self.endpoints["disclosures"], params=params
            )

            # 응답 상태 상세 로깅 (사용자가 이해하기 쉽게)
            logger.info(f"📡 DART API 응답:")
            logger.info(f"   - HTTP 상태코드: {response.status_code}")
            logger.info(
                f"   - 요청 URL: {self.base_url + self.endpoints['disclosures']}"
            )

            if response.status_code == 200:
                data = response.json()
                api_status = data.get("status")
                api_message = data.get("message", "메시지 없음")
                report_list = data.get("list", [])

                # 🔧 수정: 특정 보고서 타입 필터링
                filtered_reports = []
                if report_code and report_list:
                    # 보고서 코드에 따른 보고서명 매핑
                    report_type_map = {
                        "11011": "사업보고서",
                        # "11012": "반기보고서",  # 반기보고서 비활성화 (토큰 절약)
                        "11013": "1분기보고서",
                        "11014": "3분기보고서",
                    }
                    target_report_name = report_type_map.get(report_code, "")

                    if target_report_name:
                        filtered_reports = [
                            r
                            for r in report_list
                            if target_report_name in r.get("report_nm", "")
                        ]
                    else:
                        filtered_reports = report_list
                else:
                    filtered_reports = report_list

                list_count = len(filtered_reports)

                # 상세한 API 응답 로깅 (문제 파악을 위한 디버깅 정보)
                logger.info(f"   - API 상태코드: {api_status}")
                logger.info(f"   - API 메시지: {api_message}")
                logger.info(f"   - 전체 검색결과: {len(report_list)}개")
                logger.info(f"   - 필터링된 결과: {list_count}개")

                # 찾은 보고서들 로깅
                if filtered_reports:
                    logger.info(f"   - 발견된 보고서들:")
                    for i, report in enumerate(filtered_reports[:3]):
                        report_nm = report.get("report_nm", "N/A")
                        rcept_dt = report.get("rcept_dt", "N/A")
                        logger.info(f"     [{i+1}] {report_nm} ({rcept_dt})")

                # 에러인 경우 추가 정보 로깅
                if api_status != "000":
                    logger.warning(f"⚠️ DART API 에러 상세:")
                    logger.warning(f"   - 에러코드: {api_status}")
                    logger.warning(f"   - 에러메시지: {api_message}")
                    logger.warning(
                        f"   - 가능한 원인: 해당 연도/보고서 타입의 보고서가 존재하지 않음"
                    )

                return api_status == "000" and list_count > 0
            else:
                logger.error(f"❌ HTTP 오류: {response.status_code}")
                logger.error(f"   - 응답 내용: {response.text[:200]}...")
                return False

        except Exception as e:
            logger.error(f"⚠️ 보고서 존재 확인 중 예외 발생: {e}")
            logger.error(f"   - 예외 타입: {type(e).__name__}")
            return False

    async def _download_document_content(self, rcept_no: str) -> Optional[str]:
        """
        🚀 DART API에서 보고서 원문 내용 다운로드

        DART API는 문서를 ZIP 압축 파일로 제공하므로 이를 올바르게 처리해요
        (사용자에게 쉽게 설명하면, DART에서 문서를 압축해서 보내주기 때문에
        압축을 풀어서 내용을 읽어야 해요)

        Args:
            rcept_no: 접수번호

        Returns:
            str: 보고서 원문 텍스트 (실패시 None)
        """
        try:
            time.sleep(self.api_delay)

            params = {
                "crtfc_key": self.dart_api_key,
                "rcept_no": rcept_no,
            }

            response = requests.get(
                self.base_url + self.endpoints["document"], params=params
            )

            if response.status_code != 200:
                logger.error(
                    f"❌ 보고서 원문 다운로드 HTTP 오류: {response.status_code}"
                )
                return None

            # 🔧 수정: DART API는 ZIP 압축 파일로 문서를 제공합니다
            try:
                # ZIP 파일 처리 (b'PK\x03\x04\x14' 헤더가 ZIP 파일의 매직 넘버예요)
                import io
                import zipfile

                # 응답 내용이 ZIP 파일인지 확인
                if response.content.startswith(b"PK\x03\x04"):
                    logger.info("📦 ZIP 압축 파일 감지 - 압축 해제 중...")

                    # ZIP 파일 압축 해제
                    zf = zipfile.ZipFile(io.BytesIO(response.content))
                    info_list = zf.infolist()

                    if not info_list:
                        logger.error("❌ ZIP 파일이 비어있습니다")
                        return None

                    # 첫 번째 파일 읽기 (보통 문서 내용이 첫 번째 파일에 있어요)
                    first_file = info_list[0]
                    document_data = zf.read(first_file.filename)

                    logger.info(f"📄 ZIP에서 파일 추출: {first_file.filename}")

                    # 인코딩 시도 (한글을 제대로 읽기 위한 방법들을 차례로 시도해요)
                    content = None
                    for encoding in ["euc-kr", "utf-8", "cp949"]:
                        try:
                            content = document_data.decode(encoding)
                            logger.info(f"✅ 인코딩 성공: {encoding}")
                            break
                        except UnicodeDecodeError:
                            continue

                    if not content:
                        logger.error("❌ 모든 인코딩 방식 실패")
                        return None

                else:
                    # ZIP이 아닌 경우 (기존 방식)
                    content = response.text

            except Exception as zip_error:
                logger.error(f"❌ ZIP 처리 실패: {zip_error}")
                # ZIP 처리 실패시 기존 방식으로 시도
                content = response.text

            # XML 오류 응답 확인
            if "<?xml" in content and ("status" in content or "error" in content):
                try:
                    # XML 파싱으로 오류 확인
                    import xml.etree.ElementTree as ET

                    root = ET.fromstring(content)

                    # 오류 메시지 추출
                    error_msg = root.find(".//message")
                    if error_msg is not None:
                        logger.error(
                            f"❌ 보고서 원문 다운로드 API 오류: {error_msg.text}"
                        )
                        return None
                except Exception:
                    # XML 파싱 실패시 계속 진행
                    pass

            # HTML 태그 제거 (BeautifulSoup 사용)
            try:
                # XML 파싱 경고를 무시하는 설정 추가 (사용자 요청에 따라 한국어 주석 포함)
                # 이 부분은 XML 문서를 안전하게 처리하기 위한 경고 필터링이에요
                import warnings

                from bs4 import XMLParsedAsHTMLWarning

                warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

                # XML 전용 파서 사용 (lxml이 있으면 사용, 없으면 기본 XML 파서 사용)
                try:
                    soup = BeautifulSoup(content, features="xml")
                except Exception:
                    # XML 파서가 없으면 html.parser 사용 (경고 필터링 적용됨)
                    soup = BeautifulSoup(content, "html.parser")

                # 스크립트와 스타일 태그 제거
                for script in soup(["script", "style"]):
                    script.decompose()

                # 텍스트만 추출
                clean_text = soup.get_text()

                # 과도한 공백 및 줄바꿈 정리
                import re

                clean_text = re.sub(r"\n\s*\n", "\n\n", clean_text)  # 연속된 빈 줄 정리
                clean_text = re.sub(r" +", " ", clean_text)  # 연속된 공백 정리
                clean_text = clean_text.strip()

                if len(clean_text) < 1000:
                    logger.warning(
                        f"⚠️ 추출된 텍스트가 너무 짧습니다: {len(clean_text)}자"
                    )
                    return None

                logger.info(f"✅ 보고서 원문 다운로드 완료: {len(clean_text):,}자")
                return clean_text

            except Exception as parsing_error:
                logger.error(f"❌ HTML 파싱 실패: {parsing_error}")

                # HTML 파싱 실패시 원본 텍스트 반환 (태그 포함)
                if len(content) > 1000:
                    logger.info("⚠️ HTML 파싱 실패, 원본 내용 반환")
                    return content
                else:
                    return None

        except Exception as e:
            logger.error(f"❌ 보고서 원문 다운로드 실패: {e}")
            return None

    # ==================== 1️⃣ 상세한 재무정보 ====================

    def get_detailed_financial_data(
        self, corp_code: str, bsns_year: str = None
    ) -> Dict[str, Any]:
        """
        상세한 재무정보를 수집해요

        Args:
            corp_code: 기업 고유코드 (8자리)
            bsns_year: 사업연도 (기본값: 작년)

        Returns:
            Dict: 상세 재무정보
        """
        if not self.is_available():
            return {"success": False, "error": "DART API 키가 설정되지 않았습니다"}

        if not bsns_year:
            bsns_year = str(datetime.now().year - 1)

        logger.info(f"📊 {corp_code} 상세 재무정보 수집 시작 ({bsns_year}년)")

        try:
            result = {
                "success": True,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "collected_at": datetime.now().isoformat(),
            }

            # 단일회사 주요계정 (개별재무제표)
            single_accounts = self._get_single_company_accounts(corp_code, bsns_year)
            if single_accounts["success"]:
                result["individual_statements"] = single_accounts["data"]

            # 다중회사 주요계정 (연결재무제표)
            multi_accounts = self._get_multi_company_accounts(corp_code, bsns_year)
            if multi_accounts["success"]:
                result["consolidated_statements"] = multi_accounts["data"]

            # 분기별 실적 (최근 4분기)
            quarterly_data = self._get_quarterly_performance(corp_code, bsns_year)
            if quarterly_data["success"]:
                result["quarterly_performance"] = quarterly_data["data"]

            logger.info(f"✅ {corp_code} 상세 재무정보 수집 완료")
            return result

        except Exception as e:
            logger.error(f"❌ 상세 재무정보 수집 실패: {e}")
            return {"success": False, "error": str(e)}

    def _get_single_company_accounts(
        self, corp_code: str, bsns_year: str
    ) -> Dict[str, Any]:
        """단일회사 주요계정 조회 (개별재무제표)"""
        try:
            time.sleep(self.api_delay)

            params = {
                "crtfc_key": self.dart_api_key,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "reprt_code": "11011",  # 사업보고서
            }

            response = requests.get(
                self.base_url + self.endpoints["single_account"], params=params
            )

            if response.status_code != 200:
                return {"success": False, "error": f"HTTP 오류: {response.status_code}"}

            data = response.json()

            if data.get("status") != "000":
                return {"success": False, "error": f"API 오류: {data.get('message')}"}

            # 주요 계정과목 추출
            accounts = data.get("list", [])
            financial_data = self._parse_financial_statements(accounts)

            return {"success": True, "data": financial_data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_multi_company_accounts(
        self, corp_code: str, bsns_year: str
    ) -> Dict[str, Any]:
        """다중회사 주요계정 조회 (연결재무제표)"""
        try:
            time.sleep(self.api_delay)

            params = {
                "crtfc_key": self.dart_api_key,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "reprt_code": "11011",  # 사업보고서
            }

            response = requests.get(
                self.base_url + self.endpoints["multi_account"], params=params
            )

            if response.status_code != 200:
                return {"success": False, "error": f"HTTP 오류: {response.status_code}"}

            data = response.json()

            if data.get("status") != "000":
                return {"success": False, "error": f"API 오류: {data.get('message')}"}

            # 연결재무제표 정보 추출
            accounts = data.get("list", [])
            consolidated_data = self._parse_financial_statements(accounts)

            return {"success": True, "data": consolidated_data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_quarterly_performance(
        self, corp_code: str, bsns_year: str
    ) -> Dict[str, Any]:
        """분기별 실적 조회"""
        try:
            quarterly_data = []

            # 최근 4분기 데이터 수집
            quarters = [
                "11013",
                "11012",
                "11014",
                "11011",
            ]  # 1분기, 반기, 3분기, 사업보고서
            quarter_names = ["1분기", "반기", "3분기", "연간"]

            for quarter_code, quarter_name in zip(quarters, quarter_names):
                time.sleep(self.api_delay)

                params = {
                    "crtfc_key": self.dart_api_key,
                    "corp_code": corp_code,
                    "bsns_year": bsns_year,
                    "reprt_code": quarter_code,
                }

                response = requests.get(
                    self.base_url + self.endpoints["single_account"], params=params
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "000":
                        accounts = data.get("list", [])
                        quarter_financials = self._parse_financial_statements(accounts)
                        quarter_financials["period"] = quarter_name
                        quarterly_data.append(quarter_financials)

            return {"success": True, "data": quarterly_data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _parse_financial_statements(self, accounts: List[Dict]) -> Dict[str, Any]:
        """재무제표 데이터 파싱"""
        parsed_data = {
            "asset_info": {},  # 자산 정보
            "liability_info": {},  # 부채 정보
            "equity_info": {},  # 자본 정보
            "income_info": {},  # 손익 정보
        }

        # 주요 계정과목 매핑
        account_mapping = {
            # 자산
            "자산총계": "total_assets",
            "유동자산": "current_assets",
            "비유동자산": "non_current_assets",
            "현금및현금성자산": "cash_and_equivalents",
            # 부채
            "부채총계": "total_liabilities",
            "유동부채": "current_liabilities",
            "비유동부채": "non_current_liabilities",
            # 자본
            "자본총계": "total_equity",
            "자본금": "capital_stock",
            "이익잉여금": "retained_earnings",
            # 손익
            "매출액": "revenue",
            "영업이익": "operating_income",
            "당기순이익": "net_income",
            "영업비용": "operating_expenses",
        }

        for account in accounts:
            account_name = account.get("account_nm", "")
            current_amount = account.get("thstrm_amount", "0")

            # 숫자로 변환 (콤마 제거)
            try:
                amount = (
                    int(current_amount.replace(",", "")) if current_amount != "-" else 0
                )
            except:
                amount = 0

            # 계정과목별 분류
            if account_name in account_mapping:
                key = account_mapping[account_name]

                if "자산" in account_name:
                    parsed_data["asset_info"][key] = amount
                elif "부채" in account_name:
                    parsed_data["liability_info"][key] = amount
                elif "자본" in account_name:
                    parsed_data["equity_info"][key] = amount
                elif account_name in ["매출액", "영업이익", "당기순이익", "영업비용"]:
                    parsed_data["income_info"][key] = amount

        return parsed_data

    # ==================== 2️⃣ 기업 지배구조 정보 ====================

    def get_governance_info(
        self, corp_code: str, bsns_year: str = None
    ) -> Dict[str, Any]:
        """
        기업 지배구조 정보를 수집해요

        Args:
            corp_code: 기업 고유코드
            bsns_year: 사업연도

        Returns:
            Dict: 지배구조 정보
        """
        if not self.is_available():
            return {"success": False, "error": "DART API 키가 설정되지 않았습니다"}

        if not bsns_year:
            bsns_year = str(datetime.now().year - 1)

        logger.info(f"👥 {corp_code} 지배구조 정보 수집 시작")

        try:
            result = {
                "success": True,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "collected_at": datetime.now().isoformat(),
            }

            # 최대주주 현황
            shareholders = self._get_major_shareholders(corp_code, bsns_year)
            if shareholders["success"]:
                result["major_shareholders"] = shareholders["data"]

            # 임원 현황
            executives = self._get_executives_info(corp_code, bsns_year)
            if executives["success"]:
                result["executives"] = executives["data"]

            # 이사 보수 현황
            compensation = self._get_director_compensation(corp_code, bsns_year)
            if compensation["success"]:
                result["director_compensation"] = compensation["data"]

            # 사외이사 현황
            outside_directors = self._get_outside_directors(corp_code, bsns_year)
            if outside_directors["success"]:
                result["outside_directors"] = outside_directors["data"]

            logger.info(f"✅ {corp_code} 지배구조 정보 수집 완료")
            return result

        except Exception as e:
            logger.error(f"❌ 지배구조 정보 수집 실패: {e}")
            return {"success": False, "error": str(e)}

    def _get_major_shareholders(self, corp_code: str, bsns_year: str) -> Dict[str, Any]:
        """최대주주 현황 조회"""
        try:
            time.sleep(self.api_delay)

            params = {
                "crtfc_key": self.dart_api_key,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "reprt_code": "11011",
            }

            response = requests.get(
                self.base_url + self.endpoints["major_shareholders"], params=params
            )

            if response.status_code != 200:
                return {"success": False, "error": f"HTTP 오류: {response.status_code}"}

            data = response.json()

            if data.get("status") != "000":
                return {"success": False, "error": f"API 오류: {data.get('message')}"}

            # 🔍 디버깅: 전체 API 응답 로깅
            logger.info(
                f"📋 DART API 전체 응답: status={data.get('status')}, message={data.get('message')}"
            )
            logger.info(f"📊 DART API 주주 데이터 개수: {len(data.get('list', []))}")

            shareholders_data = []
            for item in data.get("list", []):
                # ✅ 올바른 DART API 필드명 사용
                hold_stock_co_raw = item.get("trmend_posesn_stock_co", "0")
                hold_stock_rt_raw = item.get("trmend_posesn_stock_qota_rt", "0")

                shareholder = {
                    "shareholder_name": item.get("nm", ""),
                    "relationship": item.get("relate", ""),
                    "shares_held": self._safe_int(hold_stock_co_raw),
                    "ownership_ratio": self._safe_float(hold_stock_rt_raw),
                    "report_date": item.get("stlm_dt", ""),  # 결산일자 사용
                }
                shareholders_data.append(shareholder)

            logger.info(f"✅ 주주정보 {len(shareholders_data)}명 수집 완료")

            return {"success": True, "data": shareholders_data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_executives_info(self, corp_code: str, bsns_year: str) -> Dict[str, Any]:
        """임원 현황 조회"""
        try:
            time.sleep(self.api_delay)

            params = {
                "crtfc_key": self.dart_api_key,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "reprt_code": "11011",
            }

            response = requests.get(
                self.base_url + self.endpoints["executives"], params=params
            )

            if response.status_code != 200:
                return {"success": False, "error": f"HTTP 오류: {response.status_code}"}

            data = response.json()

            if data.get("status") != "000":
                return {"success": False, "error": f"API 오류: {data.get('message')}"}

            executives_data = []
            for item in data.get("list", []):
                executive = {
                    "name": item.get("nm", ""),
                    "position": item.get("sexdsgnm", ""),
                    "career": item.get("career", ""),
                    "main_career": item.get("main_career", ""),
                    "tenure": item.get("tenure", ""),
                }
                executives_data.append(executive)

            return {"success": True, "data": executives_data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_director_compensation(
        self, corp_code: str, bsns_year: str
    ) -> Dict[str, Any]:
        """이사 보수 현황 조회"""
        try:
            time.sleep(self.api_delay)

            params = {
                "crtfc_key": self.dart_api_key,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "reprt_code": "11011",
            }

            response = requests.get(
                self.base_url + self.endpoints["director_compensation"], params=params
            )

            if response.status_code != 200:
                return {"success": False, "error": f"HTTP 오류: {response.status_code}"}

            data = response.json()

            if data.get("status") != "000":
                return {"success": False, "error": f"API 오류: {data.get('message')}"}

            compensation_data = []
            for item in data.get("list", []):
                compensation = {
                    "classification": item.get("job", ""),
                    "number_of_people": self._safe_int(item.get("nmpr", "0")),
                    "total_compensation": self._safe_int(item.get("pymnt_totamt", "0")),
                    "average_compensation": self._safe_int(item.get("pymnt_avrg", "0")),
                }
                compensation_data.append(compensation)

            return {"success": True, "data": compensation_data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_outside_directors(self, corp_code: str, bsns_year: str) -> Dict[str, Any]:
        """사외이사 현황 조회"""
        try:
            time.sleep(self.api_delay)

            params = {
                "crtfc_key": self.dart_api_key,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "reprt_code": "11011",
            }

            response = requests.get(
                self.base_url + self.endpoints["outside_directors"], params=params
            )

            if response.status_code != 200:
                return {"success": False, "error": f"HTTP 오류: {response.status_code}"}

            data = response.json()

            if data.get("status") != "000":
                return {"success": False, "error": f"API 오류: {data.get('message')}"}

            directors_data = []
            for item in data.get("list", []):
                director = {
                    "name": item.get("nm", ""),
                    "appointment_date": item.get("apnt_dt", ""),
                    "tenure": item.get("tenure", ""),
                    "independence_criteria": item.get("indpnc_stat", ""),
                }
                directors_data.append(director)

            return {"success": True, "data": directors_data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # ==================== 3️⃣ 투자정보 ====================

    def get_investment_info(
        self, corp_code: str, bsns_year: str = None
    ) -> Dict[str, Any]:
        """
        투자 관련 정보를 수집해요

        Args:
            corp_code: 기업 고유코드
            bsns_year: 사업연도

        Returns:
            Dict: 투자정보
        """
        if not self.is_available():
            return {"success": False, "error": "DART API 키가 설정되지 않았습니다"}

        if not bsns_year:
            bsns_year = str(datetime.now().year - 1)

        logger.info(f"💰 {corp_code} 투자정보 수집 시작")

        try:
            result = {
                "success": True,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "collected_at": datetime.now().isoformat(),
            }

            # 배당 정보
            dividends = self._get_dividend_info(corp_code, bsns_year)
            if dividends["success"]:
                result["dividend_info"] = dividends["data"]

            # 증자감자 현황
            capital_changes = self._get_capital_changes(corp_code, bsns_year)
            if capital_changes["success"]:
                result["capital_changes"] = capital_changes["data"]

            # 자기주식 현황
            treasury_stock = self._get_treasury_stock(corp_code, bsns_year)
            if treasury_stock["success"]:
                result["treasury_stock"] = treasury_stock["data"]

            # 타법인 출자현황
            investments = self._get_investments(corp_code, bsns_year)
            if investments["success"]:
                result["other_investments"] = investments["data"]

            logger.info(f"✅ {corp_code} 투자정보 수집 완료")
            return result

        except Exception as e:
            logger.error(f"❌ 투자정보 수집 실패: {e}")
            return {"success": False, "error": str(e)}

    def _get_dividend_info(self, corp_code: str, bsns_year: str) -> Dict[str, Any]:
        """배당 정보 조회"""
        try:
            time.sleep(self.api_delay)

            params = {
                "crtfc_key": self.dart_api_key,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "reprt_code": "11011",
            }

            response = requests.get(
                self.base_url + self.endpoints["dividends"], params=params
            )

            if response.status_code != 200:
                return {"success": False, "error": f"HTTP 오류: {response.status_code}"}

            data = response.json()

            if data.get("status") != "000":
                return {"success": False, "error": f"API 오류: {data.get('message')}"}

            dividend_data = []
            for item in data.get("list", []):
                dividend = {
                    "dividend_classification": item.get("se", ""),
                    "current_year": self._safe_float(item.get("thstrm", "0")),  # 당기
                    "previous_year": self._safe_float(item.get("frmtrm", "0")),  # 전기
                    "two_years_ago": self._safe_float(item.get("lwfr", "0")),  # 전전기
                    "settlement_date": item.get("stlm_dt", ""),  # 결산일자
                }
                dividend_data.append(dividend)

            return {"success": True, "data": dividend_data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_capital_changes(self, corp_code: str, bsns_year: str) -> Dict[str, Any]:
        """증자감자 현황 조회"""
        try:
            time.sleep(self.api_delay)

            params = {
                "crtfc_key": self.dart_api_key,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "reprt_code": "11011",
            }

            response = requests.get(
                self.base_url + self.endpoints["capital_changes"], params=params
            )

            if response.status_code != 200:
                return {"success": False, "error": f"HTTP 오류: {response.status_code}"}

            data = response.json()

            if data.get("status") != "000":
                return {"success": False, "error": f"API 오류: {data.get('message')}"}

            capital_data = []
            for item in data.get("list", []):
                capital = {
                    "change_type": item.get(
                        "isu_dcrs_mstvdv_amount", ""
                    ),  # 증자감자구분
                    "settlement_date": item.get("stlm_dt", ""),  # 결산일자
                    "note": (
                        "증자감자 실적이 없는 경우 '-' 표시"
                        if item.get("isu_dcrs_mstvdv_amount") == "-"
                        else ""
                    ),
                }
                capital_data.append(capital)

            return {"success": True, "data": capital_data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_treasury_stock(self, corp_code: str, bsns_year: str) -> Dict[str, Any]:
        """자기주식 현황 조회"""
        try:
            time.sleep(self.api_delay)

            params = {
                "crtfc_key": self.dart_api_key,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "reprt_code": "11011",
            }

            response = requests.get(
                self.base_url + self.endpoints["treasury_stock"], params=params
            )

            if response.status_code != 200:
                return {"success": False, "error": f"HTTP 오류: {response.status_code}"}

            data = response.json()

            if data.get("status") != "000":
                return {"success": False, "error": f"API 오류: {data.get('message')}"}

            treasury_data = []
            for item in data.get("list", []):
                treasury = {
                    "acquisition_date": item.get("acqs_dt", ""),
                    "acquisition_method": item.get("acqs_mth", ""),
                    "shares_acquired": self._safe_int(item.get("acqs_stock_co", "0")),
                    "acquisition_amount": self._safe_int(item.get("acqs_amount", "0")),
                    "disposal_method": item.get("dsps_mth", ""),
                }
                treasury_data.append(treasury)

            return {"success": True, "data": treasury_data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_investments(self, corp_code: str, bsns_year: str) -> Dict[str, Any]:
        """타법인 출자현황 조회"""
        try:
            time.sleep(self.api_delay)

            params = {
                "crtfc_key": self.dart_api_key,
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "reprt_code": "11011",
            }

            response = requests.get(
                self.base_url + self.endpoints["investments"], params=params
            )

            if response.status_code != 200:
                return {"success": False, "error": f"HTTP 오류: {response.status_code}"}

            data = response.json()

            if data.get("status") != "000":
                return {"success": False, "error": f"API 오류: {data.get('message')}"}

            investment_data = []
            for item in data.get("list", []):
                investment = {
                    "company_name": item.get("inv_prm", ""),
                    "first_acquisition_date": item.get(
                        "frst_acqs_de", ""
                    ),  # 최초취득일자
                    "investment_purpose": item.get("invstmnt_purps", ""),  # 투자목적
                    "first_acquisition_amount": self._safe_int(
                        item.get("frst_acqs_amount", "0")
                    ),  # 최초취득금액
                    "ending_shares": self._safe_int(
                        item.get("trmend_blce_qy", "0")
                    ),  # 기말보유수량
                    "ownership_ratio": self._safe_float(
                        item.get("trmend_blce_qota_rt", "0")
                    ),  # 기말지분율
                    "book_value": self._safe_int(
                        item.get("trmend_blce_acntbk_amount", "0")
                    ),  # 기말장부금액
                    "settlement_date": item.get("stlm_dt", ""),  # 결산일자
                }
                investment_data.append(investment)

            return {"success": True, "data": investment_data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # ==================== 4️⃣ 실시간 공시 모니터링 ====================

    def monitor_disclosures(
        self, corp_code: str = None, days: int = 7
    ) -> Dict[str, Any]:
        """
        실시간 공시 모니터링

        Args:
            corp_code: 기업 고유코드 (None이면 전체 공시)
            days: 조회 기간 (일)

        Returns:
            Dict: 공시 모니터링 결과
        """
        if not self.is_available():
            return {"success": False, "error": "DART API 키가 설정되지 않았습니다"}

        logger.info(f"📰 공시 모니터링 시작 (최근 {days}일)")

        try:
            result = {
                "success": True,
                "monitoring_period": f"최근 {days}일",
                "collected_at": datetime.now().isoformat(),
            }

            # 최근 공시 목록
            recent_disclosures = self._get_recent_disclosures(corp_code, days)
            if recent_disclosures["success"]:
                result["recent_disclosures"] = recent_disclosures["data"]
            else:
                result["recent_disclosures"] = []
                result["recent_disclosures_error"] = recent_disclosures.get("error")

            # 중요 공시 알림
            important_notices = self._get_important_notices(corp_code, days)
            if important_notices["success"]:
                result["important_notices"] = important_notices["data"]
            else:
                result["important_notices"] = []
                result["important_notices_error"] = important_notices.get("error")

            # 정정공시 목록
            corrections = self._get_corrections(corp_code, days)
            if corrections["success"]:
                result["corrections"] = corrections["data"]
            else:
                result["corrections"] = []
                result["corrections_error"] = corrections.get("error")

            # 통합 데이터 추가
            result["data"] = {
                "recent_disclosures": result["recent_disclosures"],
                "important_notices": result["important_notices"],
                "corrections": result["corrections"],
            }

            logger.info(f"✅ 공시 모니터링 완료")
            return result

        except Exception as e:
            logger.error(f"❌ 공시 모니터링 실패: {e}")
            return {"success": False, "error": str(e)}

    def _get_recent_disclosures(self, corp_code: str, days: int) -> Dict[str, Any]:
        """최근 공시 목록 조회"""
        try:
            time.sleep(self.api_delay)

            # 날짜 범위 설정
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            params = {
                "crtfc_key": self.dart_api_key,
                "bgn_de": start_date.strftime("%Y%m%d"),
                "end_de": end_date.strftime("%Y%m%d"),
                "page_no": "1",
                "page_count": "100",
            }

            if corp_code:
                params["corp_code"] = corp_code

            response = requests.get(
                self.base_url + self.endpoints["disclosures"], params=params
            )

            if response.status_code != 200:
                return {"success": False, "error": f"HTTP 오류: {response.status_code}"}

            data = response.json()

            if data.get("status") != "000":
                return {"success": False, "error": f"API 오류: {data.get('message')}"}

            disclosure_data = []
            for item in data.get("list", []):
                # 날짜 형식 변환 (YYYYMMDD → YYYY-MM-DD)
                receipt_date = item.get("rcept_dt", "")
                formatted_date = self._format_date(receipt_date)

                # 보고서명 공백 제거
                report_name = item.get("report_nm", "").strip()

                disclosure = {
                    "corp_name": item.get("corp_name", ""),
                    "report_name": report_name,
                    "receipt_number": item.get("rcept_no", ""),
                    "receipt_date": formatted_date,
                    "receipt_date_raw": receipt_date,  # 원본 날짜도 보관
                    "submitter": item.get("flr_nm", ""),
                    "remarks": item.get("rm", ""),
                }
                disclosure_data.append(disclosure)

            return {"success": True, "data": disclosure_data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_important_notices(self, corp_code: str, days: int) -> Dict[str, Any]:
        """중요 공시 알림 (주요사항보고서, 공정공시 등)"""
        try:
            # 중요 공시 키워드 (우선순위별 분류)
            critical_keywords = {
                "최고 중요": ["합병", "분할", "영업양도", "영업양수", "해산", "청산"],
                "매우 중요": [
                    "유상증자",
                    "무상증자",
                    "감자",
                    "전환사채",
                    "신주인수권부사채",
                ],
                "중요": [
                    "주요사항보고서",
                    "공정공시",
                    "배당",
                    "자기주식",
                    "최대주주변동",
                ],
                "일반": ["기업지배구조", "감사보고서", "정기주주총회", "임시주주총회"],
            }

            recent_disclosures = self._get_recent_disclosures(corp_code, days)
            if not recent_disclosures["success"]:
                return recent_disclosures

            important_disclosures = []
            for disclosure in recent_disclosures["data"]:
                report_name = disclosure.get("report_name", "")

                # 중요도별 필터링
                importance_level = None
                matched_keyword = None

                for level, keywords in critical_keywords.items():
                    for keyword in keywords:
                        if keyword in report_name:
                            importance_level = level
                            matched_keyword = keyword
                            break
                    if importance_level:
                        break

                if importance_level:
                    disclosure_copy = disclosure.copy()
                    disclosure_copy["importance_level"] = importance_level
                    disclosure_copy["importance_reason"] = (
                        f"'{matched_keyword}' 관련 공시"
                    )
                    disclosure_copy["priority_score"] = self._calculate_priority_score(
                        importance_level, matched_keyword
                    )

                    # 🆕 공시 내용 추가 (상위 3개 중요 공시만)
                    if len(important_disclosures) < 3:
                        content_summary = self._get_disclosure_content_summary(
                            disclosure_copy.get("receipt_number", "")
                        )
                        if content_summary:
                            disclosure_copy["content_summary"] = content_summary

                    important_disclosures.append(disclosure_copy)

            # 우선순위 순으로 정렬
            important_disclosures.sort(
                key=lambda x: x.get("priority_score", 0), reverse=True
            )

            return {"success": True, "data": important_disclosures}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_corrections(self, corp_code: str, days: int) -> Dict[str, Any]:
        """정정공시 목록 조회"""
        try:
            recent_disclosures = self._get_recent_disclosures(corp_code, days)
            if not recent_disclosures["success"]:
                return recent_disclosures

            correction_keywords = ["정정", "첨부정정", "기재정정"]
            corrections = []

            for disclosure in recent_disclosures["data"]:
                report_name = disclosure.get("report_name", "")

                # 정정공시 필터링
                for keyword in correction_keywords:
                    if keyword in report_name:
                        disclosure["correction_type"] = keyword
                        corrections.append(disclosure)
                        break

            return {"success": True, "data": corrections}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # ==================== 유틸리티 함수 ====================

    def _safe_int(self, value: str) -> int:
        """안전한 정수 변환"""
        try:
            return int(value.replace(",", "")) if value and value != "-" else 0
        except:
            return 0

    def _safe_float(self, value: str) -> float:
        """안전한 실수 변환"""
        try:
            return float(value.replace(",", "")) if value and value != "-" else 0.0
        except:
            return 0.0

    def _format_date(self, date_str: str) -> str:
        """날짜 형식 변환 (YYYYMMDD → YYYY-MM-DD)"""
        try:
            if date_str and len(date_str) == 8:
                return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            return date_str
        except:
            return date_str

    def _calculate_priority_score(self, importance_level: str, keyword: str) -> int:
        """공시 우선순위 점수 계산"""
        level_scores = {"최고 중요": 100, "매우 중요": 80, "중요": 60, "일반": 40}

        # 특정 키워드에 대한 추가 점수
        keyword_bonus = {
            "합병": 20,
            "분할": 20,
            "영업양도": 15,
            "영업양수": 15,
            "유상증자": 15,
            "무상증자": 10,
            "감자": 15,
            "주요사항보고서": 10,
            "공정공시": 8,
            "배당": 5,
            "자기주식": 5,
        }

        base_score = level_scores.get(importance_level, 0)
        bonus = keyword_bonus.get(keyword, 0)

        return base_score + bonus

    def _get_disclosure_content_summary(self, receipt_no: str) -> Optional[str]:
        """공시 내용 요약 추출"""
        try:
            if not receipt_no or not self.dart_api_key:
                return None

            # DART API document.xml 호출
            url = "https://opendart.fss.or.kr/api/document.xml"
            params = {"crtfc_key": self.dart_api_key, "rcept_no": receipt_no}

            response = requests.get(url, params=params, timeout=10)

            if response.status_code != 200:
                return None

            # XML 파싱하여 ZIP 파일 추출

            try:
                # XML 파싱 경고를 무시하는 설정 추가 (사용자 요청에 따라 한국어 주석 포함)
                # 이 부분은 XML 문서를 안전하게 처리하기 위한 경고 필터링이에요
                import warnings

                from bs4 import XMLParsedAsHTMLWarning

                warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

                # 응답이 ZIP 파일인 경우
                zf = zipfile.ZipFile(io.BytesIO(response.content))
                info_list = zf.infolist()

                if not info_list:
                    return None

                # 첫 번째 파일 읽기
                first_file = info_list[0]
                xml_data = zf.read(first_file.filename)

                # 인코딩 시도 (사용자에게 쉽게 설명하면, 한글을 제대로 읽기 위한 방법들을 차례로 시도하는 거예요)
                try:
                    xml_text = xml_data.decode("euc-kr")
                except UnicodeDecodeError:
                    try:
                        xml_text = xml_data.decode("utf-8")
                    except UnicodeDecodeError:
                        xml_text = xml_data.decode("cp949", errors="ignore")

                # XML 전용 파싱 사용 (경고 해결을 위한 개선)
                # 이 부분은 XML 문서를 올바른 방법으로 분석하는 코드예요
                try:
                    # XML 파서 사용 (lxml이 있으면 사용, 없으면 기본 XML 파서 사용)
                    soup = BeautifulSoup(xml_text, features="xml")
                except Exception:
                    # XML 파서가 없으면 html.parser 사용 (경고 필터링 적용됨)
                    soup = BeautifulSoup(xml_text, "html.parser")

                # 주요 섹션 찾기 (문서에서 중요한 내용을 찾는 과정이에요)
                main_content = ""

                # 1. 주요내용 섹션 찾기
                for tag in soup.find_all(["p", "div", "span"]):
                    text = tag.get_text(strip=True)
                    if text and len(text) > 20:  # 의미있는 텍스트만
                        main_content += text + " "
                        if len(main_content) > 500:  # 적당한 길이로 제한
                            break

                # 2. 텍스트 정리 (깔끔하게 정리하는 과정이에요)
                if main_content:
                    # 불필요한 공백 제거
                    main_content = " ".join(main_content.split())

                    # 500자로 제한하고 마지막 문장 완성
                    if len(main_content) > 500:
                        main_content = main_content[:500]
                        last_period = main_content.rfind(".")
                        if last_period > 400:  # 적절한 위치에 마침표가 있으면
                            main_content = main_content[: last_period + 1]
                        else:
                            main_content = main_content + "..."

                    return main_content.strip()

            except Exception as e:
                logger.debug(f"공시 내용 파싱 오류: {e}")
                return None

        except Exception as e:
            logger.debug(f"공시 내용 조회 오류: {e}")
            return None

        return None

    def get_corp_code_from_stock_code(
        self, stock_code: str, company_name: str = None
    ) -> Optional[str]:
        """
        종목코드와 회사명으로부터 DART 기업고유코드 조회 (동적 검색 지원)

        Args:
            stock_code: 6자리 종목코드 (예: "005930")
            company_name: 회사명 (동적 검색용, 선택사항)

        Returns:
            str: 8자리 기업고유코드 또는 None
        """
        if not self.is_available():
            return None

        try:
            # 🚀 1단계: 회사명이 있으면 DART API로 동적 검색 (최우선!)
            if company_name:
                logger.info(
                    f"🔍 Enhanced DART: 회사명 '{company_name}'으로 동적 검색 시도..."
                )
                corp_code = self._search_corp_code_by_company_name(company_name)
                if corp_code:
                    logger.info(
                        f"✅ Enhanced DART 동적 검색 성공: {company_name} → {corp_code}"
                    )
                    return corp_code
                else:
                    logger.warning(
                        f"⚠️ Enhanced DART 회사명 '{company_name}' 동적 검색 실패"
                    )

            # 🗂️ 2단계: 백업용 하드코딩 매핑 테이블 (주요 종목만)
            logger.info(
                f"📋 Enhanced DART: 종목코드 {stock_code} 백업 매핑 테이블 검색..."
            )
            stock_to_corp_mapping = {
                "005930": "00126380",  # 삼성전자
                "000660": "00164779",  # SK하이닉스
                "035420": "00401731",  # NAVER
                "035720": "00258801",  # 카카오
                "207940": "00356370",  # 삼성바이오로직스
                "006400": "00102148",  # 삼성SDI
                "051910": "00135199",  # LG화학
                "028260": "00344976",  # 삼성물산
                "066570": "00186136",  # LG전자
                "096770": "00173054",  # SK이노베이션
                "032830": "00126256",  # 삼성생명 (추가)
                "272210": "00356535",  # 한화시스템 (추가)
                "012450": "00178253",  # 한화에어로스페이스 (추가)
            }

            backup_corp_code = stock_to_corp_mapping.get(stock_code)
            if backup_corp_code:
                logger.info(
                    f"✅ Enhanced DART 백업 매핑 성공: {stock_code} → {backup_corp_code}"
                )
                return backup_corp_code

            # ❌ 3단계: 모든 방법 실패
            logger.warning(
                f"❌ Enhanced DART 법인고유번호 검색 실패: 종목코드({stock_code}), 회사명({company_name})"
            )
            return None

        except Exception as e:
            logger.error(f"Enhanced DART 종목코드 변환 실패: {e}")
            return None

    def _search_corp_code_by_company_name(self, company_name: str) -> Optional[str]:
        """DART API를 사용해서 회사명으로 법인고유번호를 검색해요 (Enhanced 버전)"""
        try:
            # 🧹 회사명 정제 (접두사 및 불필요한 문자 제거)
            cleaned_name = self._clean_company_name(company_name)
            logger.info(
                f"🧹 Enhanced DART 회사명 정제: '{company_name}' → '{cleaned_name}'"
            )

            # DART API의 고유번호 검색 API 호출 (ZIP 압축 파일)
            url = "https://opendart.fss.or.kr/api/corpCode.xml"
            params = {
                "crtfc_key": self.dart_api_key,
            }

            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 200:
                # ZIP 파일 압축 해제
                import io
                import xml.etree.ElementTree as ET
                import zipfile

                # ZIP 내용을 메모리에서 압축 해제
                zip_content = io.BytesIO(response.content)
                with zipfile.ZipFile(zip_content, "r") as zip_file:
                    # CORPCODE.xml 파일 읽기
                    xml_filename = zip_file.namelist()[0]  # 첫 번째 파일
                    xml_content = zip_file.read(xml_filename).decode("utf-8")

                # XML 파싱
                root = ET.fromstring(xml_content)
                companies = []

                # 🔍 모든 회사 정보 파싱
                for company in root.findall(".//list"):
                    corp_code = company.findtext("corp_code", "")
                    corp_name = company.findtext("corp_name", "")
                    stock_code = company.findtext("stock_code", "")

                    if corp_code and corp_name:
                        companies.append(
                            {
                                "corp_code": corp_code,
                                "corp_name": corp_name.strip(),
                                "stock_code": stock_code.strip() if stock_code else "",
                            }
                        )

                logger.info(
                    f"📋 Enhanced DART에서 {len(companies)}개 기업 정보 로드 완료"
                )

                # 🎯 매칭 점수 계산하여 최적 회사 찾기
                best_match = None
                best_score = 0

                # 1차: 정제된 이름으로 직접 매칭
                for company in companies:
                    score = self._calculate_match_score(
                        cleaned_name, company["corp_name"]
                    )
                    if score > best_score:
                        best_score = score
                        best_match = company

                # 2차: 대체 표기법 시도 (점수가 낮은 경우)
                if best_score < 90:
                    alternative_names = self._try_alternative_company_names(
                        cleaned_name
                    )
                    for alt_name in alternative_names:
                        logger.info(f"🔄 Enhanced DART 대체 표기법 시도: '{alt_name}'")
                        for company in companies:
                            score = self._calculate_match_score(
                                alt_name, company["corp_name"]
                            )
                            if score > best_score:
                                best_score = score
                                best_match = company
                                logger.info(
                                    f"✅ Enhanced DART 대체 표기법 매칭 성공: {alt_name} → {company['corp_name']} (점수: {score})"
                                )

                if best_match and best_score >= 70:  # 최소 70% 매칭
                    logger.info(
                        f"🎯 Enhanced DART 최고 매칭: {best_match['corp_name']} (점수: {best_score})"
                    )
                    return best_match["corp_code"]
                else:
                    logger.warning(
                        f"⚠️ Enhanced DART 매칭 점수 부족: 최고 점수 {best_score} < 70"
                    )
                    return None

            else:
                logger.error(
                    f"Enhanced DART API 호출 실패: HTTP {response.status_code}"
                )
                return None

        except Exception as e:
            logger.error(f"Enhanced DART 회사명 검색 중 오류: {e}")
            return None

    def _clean_company_name(self, company_name: str) -> str:
        """회사명에서 불필요한 접두사와 문자를 제거해요 (Enhanced 버전)"""
        import re

        # 원본 보존
        cleaned = company_name.strip()

        # 🧹 1단계: 숫자+점+공백 접두사 제거 (예: "1. 삼성생명" → "삼성생명")
        cleaned = re.sub(r"^\d+\.\s*", "", cleaned)

        # 🧹 2단계: 괄호와 내용 제거 (예: "삼성생명(주)" → "삼성생명")
        cleaned = re.sub(r"\([^)]*\)", "", cleaned)

        # 🧹 3단계: 다양한 회사 표기 정리
        # "㈜" → "주식회사"로 정규화 (하지만 검색시에는 둘 다 시도)

        # 🧹 4단계: 여러 공백을 하나로 합치기
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        logger.debug(f"🧹 Enhanced DART 회사명 정제: '{company_name}' → '{cleaned}'")
        return cleaned

    def _try_alternative_company_names(self, company_name: str) -> List[str]:
        """다양한 대체 표기법을 생성해요 (Enhanced 버전)"""
        alternatives = []

        # 원본 추가
        alternatives.append(company_name)

        # 🔄 "주식회사" 관련 변형
        if "주식회사" in company_name:
            # "주식회사 ABC" → "ABC"
            alternatives.append(company_name.replace("주식회사", "").strip())
            # "주식회사 ABC" → "㈜ABC"
            alternatives.append(company_name.replace("주식회사", "㈜"))
        else:
            # "ABC" → "주식회사 ABC"
            alternatives.append(f"주식회사 {company_name}")
            # "ABC" → "㈜ABC"
            alternatives.append(f"㈜{company_name}")

        # 🔄 특별한 케이스들
        special_cases = {
            "삼성생명": [
                "삼성생명보험",
                "삼성생명보험주식회사",
                "주식회사 삼성생명보험",
            ],
            "삼성전자": ["삼성전자주식회사", "주식회사 삼성전자"],
            "LG전자": ["LG전자주식회사", "주식회사 LG전자"],
            "SK하이닉스": ["SK하이닉스주식회사", "에스케이하이닉스"],
            "한화에어로스페이스": [
                "한화에어로스페이스주식회사",
                "주식회사 한화에어로스페이스",
            ],
            "한화시스템": ["한화시스템주식회사", "주식회사 한화시스템"],
        }

        if company_name in special_cases:
            alternatives.extend(special_cases[company_name])

        # 중복 제거하면서 순서 보존
        seen = set()
        unique_alternatives = []
        for alt in alternatives:
            if alt not in seen:
                seen.add(alt)
                unique_alternatives.append(alt)

        logger.debug(f"🔄 Enhanced DART 대체 표기법: {unique_alternatives}")
        return unique_alternatives

    def _calculate_match_score(self, target: str, corp: str) -> int:
        """회사명 매칭 점수를 계산해요 (Enhanced 버전)"""
        score = 0

        # 🎯 1단계: 정확한 일치 (최고점)
        if target == corp:
            score += 100

        # 🎯 2단계: 완전히 포함되는 경우
        elif target in corp:
            # 정확한 부분 문자열인지 확인 (예: "한화에어로스페이스"가 "한화에어로스페이스주식회사"에 포함)
            if corp.startswith(target) or corp.endswith(target):
                score += 90
            else:
                score += 70

        elif corp in target:
            score += 60

        # 🎯 3단계: 키워드 기반 매칭
        target_keywords = target.split()
        corp_keywords = corp.split()

        # 공통 키워드 개수에 따른 점수
        common_keywords = set(target_keywords) & set(corp_keywords)
        if common_keywords:
            score += len(common_keywords) * 20

        return score

    def get_comprehensive_company_analysis(
        self, stock_code: str, company_name: str = None, bsns_year: str = None
    ) -> Dict[str, Any]:
        """
        종합 기업 분석 (토큰 최적화 버전 - 주주정보/공시정보 제외)

        Args:
            stock_code: 종목코드
            company_name: 회사명
            bsns_year: 사업연도

        Returns:
            Dict: 종합 분석 결과
        """
        if not self.is_available():
            return {"success": False, "error": "DART API 키가 설정되지 않았습니다"}

        if not bsns_year:
            bsns_year = str(datetime.now().year - 1)

        # 기업고유코드 조회
        corp_code = self.get_corp_code_from_stock_code(stock_code, company_name)
        if not corp_code:
            return {"success": False, "error": "기업고유코드를 찾을 수 없습니다"}

        logger.info(
            f"🔍 Enhanced DART: {stock_code} ({company_name}) 종합 기업 분석 시작"
        )

        result = {
            "success": True,
            "stock_code": stock_code,
            "company_name": company_name,
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "collected_at": datetime.now().isoformat(),
            "optimization_note": "토큰 최적화: 주주정보/공시정보 제외",
        }

        try:
            # 1. 상세한 재무정보 (유지)
            financial_data = self.get_detailed_financial_data(corp_code, bsns_year)
            if financial_data["success"]:
                result["financial_analysis"] = financial_data

            # 2. 기업 지배구조 정보 (제외 - 토큰 절약)
            # governance_data = self.get_governance_info(corp_code, bsns_year)
            # if governance_data["success"]:
            #     result["governance_analysis"] = governance_data
            logger.info("🚫 주주정보 수집 제외 (토큰 최적화)")

            # 3. 투자정보 (유지)
            investment_data = self.get_investment_info(corp_code, bsns_year)
            if investment_data["success"]:
                result["investment_analysis"] = investment_data

            # 4. 최근 공시 모니터링 (제외 - 토큰 절약)
            # disclosure_data = self.monitor_disclosures(corp_code, days=30)
            # if disclosure_data["success"]:
            #     result["disclosure_monitoring"] = disclosure_data
            logger.info("🚫 공시정보 수집 제외 (토큰 최적화)")

            logger.info(
                f"✅ Enhanced DART: {stock_code} ({company_name}) 종합 기업 분석 완료 (토큰 최적화)"
            )
            return result

        except Exception as e:
            logger.error(f"❌ Enhanced DART 종합 기업 분석 실패: {e}")
            result["success"] = False
            result["error"] = str(e)
            return result

    async def _create_text_based_dictionary(
        self,
        text_content: str,
        company_name: str,
        max_section_size: int,
        file_path: str = None,
    ) -> Dict[str, Any]:
        """
        DART API에서 다운로드한 텍스트를 직접 섹션별 딕셔너리로 변환

        이 함수는 ZIP 압축 해제 후 얻은 텍스트 내용을 PDF로 처리하지 않고
        텍스트 분석으로 바로 딕셔너리를 만들어줘요

        Args:
            text_content: DART API에서 다운로드한 텍스트 내용
            company_name: 회사명
            max_section_size: 섹션별 최대 크기
            file_path: 임시 파일 경로 (옵션)

        Returns:
            Dict: 딕셔너리 생성 결과
        """
        try:
            start_time = time.time()
            logger.info(f"📝 텍스트 기반 딕셔너리 생성 시작: {company_name}")

            if not text_content or len(text_content.strip()) < 1000:
                return {
                    "success": False,
                    "error": f"텍스트 내용이 너무 짧습니다: {len(text_content)}자",
                }

            # 텍스트를 논리적 섹션으로 분할
            sections_dict = self._split_text_into_logical_sections(
                text_content, max_section_size
            )

            if not sections_dict:
                return {"success": False, "error": "텍스트 섹션 분할 실패"}

            # 메타데이터 생성
            metadata = {
                "company_name": company_name,
                "total_text_length": len(text_content),
                "section_count": len(sections_dict),
                "processing_time_seconds": time.time() - start_time,
                "creation_timestamp": datetime.now().isoformat(),
                "extraction_method": "dart_api_text",
                "file_type": "DART_ZIP_TEXT",
                "average_section_size": (
                    len(text_content) // len(sections_dict) if sections_dict else 0
                ),
            }

            logger.info(
                f"✅ 텍스트 기반 딕셔너리 생성 완료: {len(sections_dict)}개 섹션"
            )

            return {
                "success": True,
                "pdf_dictionary": sections_dict,
                "metadata": metadata,
                "processing_time": time.time() - start_time,
            }

        except Exception as e:
            logger.error(f"❌ 텍스트 기반 딕셔너리 생성 실패: {e}")
            return {
                "success": False,
                "error": f"텍스트 기반 딕셔너리 생성 실패: {str(e)}",
            }

    def _split_text_into_logical_sections(
        self, text: str, max_section_size: int
    ) -> Dict[str, str]:
        """
        텍스트를 논리적 섹션으로 분할

        🚀 100만자 지원으로 대용량 사업보고서도 완벽 처리!
        사업보고서나 분기보고서의 구조를 인식해서 의미있는 섹션으로 나누어줘요
        """
        try:
            sections = {}

            # 🔧 대폭 확장된 섹션 구분 키워드들 (실제 DART 보고서 구조 반영)
            section_keywords = [
                # 【】 형태 키워드 (최우선)
                "【 주요 경영지표 】",
                "【 사업의 내용 】",
                "【 경영진의 경영진단 】",
                "【 재무제표 】",
                "【 감사보고서 】",
                "【 주주총회 】",
                "【 이사회 등 회사의 기관 】",
                "【 대주주 등과의 거래 】",
                "【 주요 계약 】",
                "【 연구개발활동 】",
                "【 기타 투자자 보호를 위한 사항 】",
                # 로마숫자 형태 (우선도 높음)
                "Ⅰ. 회사의 개요",
                "Ⅱ. 사업의 내용",
                "Ⅲ. 재무에 관한 사항",
                "Ⅳ. 감사인의 감사의견",
                "Ⅴ. 이사회 등 회사의 기관",
                "Ⅵ. 대주주 등과의 거래",
                "Ⅶ. 주요 계약",
                "Ⅷ. 연구개발활동",
                "Ⅸ. 기타 투자자 보호를 위한 사항",
                # 숫자 형태 키워드
                "1. 회사의 개요",
                "2. 사업의 내용",
                "3. 재무에 관한 사항",
                "4. 감사인의 감사의견",
                "5. 이사회 등 회사의 기관",
                "6. 대주주 등과의 거래",
                "7. 주요 계약",
                "8. 연구개발활동",
                "9. 기타 투자자 보호를 위한 사항",
                # 세부 하위 섹션들
                "1-1. 회사의 개요",
                "1-2. 회사의 역사",
                "2-1. 사업의 내용",
                "2-2. 주요 제품 및 서비스",
                "3-1. 요약재무정보",
                "3-2. 연결재무제표",
                "3-3. 재무제표",
                # 가나다 형태
                "가. 회사의 개요",
                "나. 사업의 내용",
                "다. 재무에 관한 사항",
                "라. 감사인의 감사의견",
                "마. 이사회 등 회사의 기관",
                # 괄호 번호 형태
                "(1) 회사의 개요",
                "(2) 사업의 내용",
                "(3) 재무에 관한 사항",
                "(4) 감사인의 감사의견",
                "(5) 이사회 등 회사의 기관",
                # 추가 세부 섹션들 (사업보고서에서 자주 나타나는 구조)
                "가) 영업 현황",
                "나) 매출 현황",
                "다) 수주 현황",
                "라) 생산 현황",
                "마) 판매 현황",
                "바) 수출 현황",
                # 재무 관련 세부 섹션
                "① 요약재무정보",
                "② 연결재무제표",
                "③ 재무제표",
                "④ 재무상태표",
                "⑤ 손익계산서",
                "⑥ 현금흐름표",
                "⑦ 자본변동표",
                # 기타 중요 섹션들
                "□ 주요 경영지표",
                "■ 사업부문별 현황",
                "◆ 계열회사 현황",
                "◇ 임직원 현황",
                "▲ 주주 현황",
                "▼ 배당 현황",
                # 영문 섹션들 (글로벌 기업 대응)
                "I. Company Overview",
                "II. Business Description",
                "III. Financial Information",
                "IV. Auditor's Opinion",
                "V. Board of Directors",
            ]

            logger.info(
                f"📝 텍스트 분할 시작: {len(text):,}자, 최대 섹션 크기: {max_section_size:,}자"
            )

            # 현재 섹션
            current_section = "01_회사개요_및_사업내용"
            current_content = ""
            section_count = 1

            # 🔧 더 정확한 라인 분석을 위해 전처리
            lines = text.split("\n")
            total_lines = len(lines)

            logger.info(
                f"📊 전체 라인 수: {total_lines:,}개, 키워드 수: {len(section_keywords)}개"
            )

            for line_idx, line in enumerate(lines):
                line_stripped = line.strip()

                # 섹션 구분점 찾기 (더 정확한 매칭)
                section_found = False
                for keyword in section_keywords:
                    # 🎯 정확한 매칭을 위한 조건들
                    if keyword in line_stripped and (
                        line_stripped.startswith(keyword)  # 라인 시작
                        or f" {keyword}" in line_stripped  # 공백 후
                        or f"\t{keyword}" in line_stripped  # 탭 후
                    ):
                        # 이전 섹션 저장
                        if (
                            current_content.strip()
                            and len(current_content.strip()) > 200
                        ):
                            # 🚀 100만자 제한 적용 (기존 50만자에서 2배 확장!)
                            if len(current_content) > max_section_size:
                                logger.info(
                                    f"🔄 대형 섹션 분할: {current_section} ({len(current_content):,}자)"
                                )
                                sub_sections = self._split_large_section(
                                    current_content, current_section, max_section_size
                                )
                                sections.update(sub_sections)
                            else:
                                sections[current_section] = current_content.strip()
                                logger.debug(
                                    f"✅ 섹션 저장: {current_section} ({len(current_content):,}자)"
                                )

                        # 새 섹션 시작
                        section_count += 1
                        current_section = f"{section_count:02d}_{self._extract_section_name(line_stripped)}"
                        current_content = line + "\n"
                        section_found = True
                        logger.debug(
                            f"🆕 새 섹션 시작: {current_section} (라인 {line_idx+1})"
                        )
                        break

                if not section_found:
                    current_content += line + "\n"

            # 마지막 섹션 저장
            if current_content.strip() and len(current_content.strip()) > 200:
                if len(current_content) > max_section_size:
                    logger.info(
                        f"🔄 마지막 대형 섹션 분할: {current_section} ({len(current_content):,}자)"
                    )
                    sub_sections = self._split_large_section(
                        current_content, current_section, max_section_size
                    )
                    sections.update(sub_sections)
                else:
                    sections[current_section] = current_content.strip()
                    logger.debug(
                        f"✅ 마지막 섹션 저장: {current_section} ({len(current_content):,}자)"
                    )

            # 🧹 빈 섹션이나 너무 작은 섹션 제거 (최소 500자로 상향)
            filtered_sections = {
                k: v for k, v in sections.items() if v.strip() and len(v.strip()) > 500
            }

            # 🎯 섹션이 너무 적으면 강제 분할 (사업보고서가 1개 섹션인 문제 해결)
            if len(filtered_sections) <= 2 and len(text) > 50000:
                logger.warning(
                    f"⚠️ 섹션 수가 너무 적음 ({len(filtered_sections)}개). 강제 분할 실행..."
                )
                forced_sections = self._force_split_large_text(text, max_section_size)
                filtered_sections.update(forced_sections)

            logger.info(
                f"✅ 텍스트 섹션 분할 완료: {len(filtered_sections)}개 섹션 (100만자 지원)"
            )

            # 섹션별 통계 출력
            for section_name, content in filtered_sections.items():
                logger.debug(f"   📄 {section_name}: {len(content):,}자")

            return filtered_sections

        except Exception as e:
            logger.error(f"❌ 텍스트 섹션 분할 실패: {e}")
            # 실패시 전체 텍스트를 하나의 섹션으로 반환
            if len(text.strip()) > 500:
                return {"01_전체문서": text[:max_section_size]}
            return {}

    def _extract_section_name(self, line: str) -> str:
        """라인에서 섹션 이름 추출"""
        # 특수문자 제거하고 간단한 이름 생성
        import re

        clean_name = re.sub(r"[【】\[\]()（）Ⅰ-Ⅴ1-9가-힣\.\s]+", "", line)
        clean_name = re.sub(r"[^가-힣a-zA-Z]", "_", clean_name)
        clean_name = clean_name.strip("_")

        if not clean_name:
            return "기타섹션"

        return clean_name[:20]  # 최대 20자로 제한

    def _split_large_section(
        self, content: str, section_name: str, max_size: int
    ) -> Dict[str, str]:
        """큰 섹션을 여러 개로 분할"""
        try:
            sections = {}

            # 단락별로 분할 시도
            paragraphs = content.split("\n\n")
            current_subsection = ""
            subsection_count = 1

            for paragraph in paragraphs:
                if len(current_subsection) + len(paragraph) > max_size:
                    if current_subsection.strip():
                        sections[f"{section_name}_part{subsection_count:02d}"] = (
                            current_subsection.strip()
                        )
                        subsection_count += 1
                        current_subsection = paragraph + "\n\n"
                    else:
                        # 단일 단락이 너무 큰 경우 강제 분할
                        if len(paragraph) > max_size:
                            chunks = [
                                paragraph[i : i + max_size]
                                for i in range(0, len(paragraph), max_size)
                            ]
                            for i, chunk in enumerate(chunks):
                                sections[
                                    f"{section_name}_chunk{subsection_count:02d}"
                                ] = chunk
                                subsection_count += 1
                        else:
                            sections[f"{section_name}_part{subsection_count:02d}"] = (
                                paragraph
                            )
                            subsection_count += 1
                else:
                    current_subsection += paragraph + "\n\n"

            # 마지막 서브섹션 저장
            if current_subsection.strip():
                sections[f"{section_name}_part{subsection_count:02d}"] = (
                    current_subsection.strip()
                )

            return sections

        except Exception as e:
            logger.error(f"❌ 대형 섹션 분할 실패: {e}")
            return {section_name: content}  # 실패시 원본 반환

    def _force_split_large_text(
        self, text: str, max_section_size: int
    ) -> Dict[str, str]:
        """
        🔧 대형 텍스트를 강제로 논리적 섹션으로 분할

        섹션 키워드로 분할이 안되는 경우 사용하는 백업 분할 방법이에요
        문단 구조와 문맥을 고려해서 자연스럽게 분할합니다

        Args:
            text: 분할할 텍스트
            max_section_size: 섹션별 최대 크기

        Returns:
            Dict: 강제 분할된 섹션들
        """
        try:
            logger.info(f"🔨 강제 분할 시작: {len(text):,}자")

            forced_sections = {}

            # 1단계: 큰 문단으로 분할 (빈 줄 기준)
            paragraphs = text.split("\n\n")

            current_section = ""
            section_count = 1

            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue

                # 현재 섹션에 추가했을 때 크기 확인
                if len(current_section) + len(para) > max_section_size:
                    # 현재 섹션 저장
                    if current_section.strip():
                        section_name = f"강제분할_{section_count:02d}_section"
                        forced_sections[section_name] = current_section.strip()
                        logger.debug(
                            f"💪 강제 섹션 생성: {section_name} ({len(current_section):,}자)"
                        )
                        section_count += 1

                    # 새 섹션 시작
                    current_section = para + "\n\n"
                else:
                    current_section += para + "\n\n"

            # 마지막 섹션 저장
            if current_section.strip():
                section_name = f"강제분할_{section_count:02d}_section"
                forced_sections[section_name] = current_section.strip()
                logger.debug(
                    f"💪 마지막 강제 섹션: {section_name} ({len(current_section):,}자)"
                )

            # 2단계: 여전히 섹션이 적으면 페이지나 특수 구분자로 분할
            if len(forced_sections) <= 2:
                logger.warning("🔄 2단계 강제 분할 실행 (페이지 기준)")

                # 페이지 구분자들
                page_separators = [
                    "---",
                    "━━━",
                    "페이지",
                    "Page",
                    "- ",
                    "■",
                    "□",
                    "▣",
                    "▢",
                ]

                # 페이지별로 분할 시도
                for separator in page_separators:
                    if separator in text and len(text.split(separator)) > 2:
                        parts = text.split(separator)
                        forced_sections = {}

                        for i, part in enumerate(parts):
                            part = part.strip()
                            if len(part) > 1000:  # 최소 크기 필터
                                section_name = f"페이지분할_{i+1:02d}_section"
                                # 크기 제한 적용
                                if len(part) > max_section_size:
                                    # 큰 페이지는 다시 분할
                                    sub_parts = [
                                        part[j : j + max_section_size]
                                        for j in range(0, len(part), max_section_size)
                                    ]
                                    for k, sub_part in enumerate(sub_parts):
                                        if sub_part.strip():
                                            sub_section_name = f"페이지분할_{i+1:02d}_{k+1:02d}_section"
                                            forced_sections[sub_section_name] = (
                                                sub_part.strip()
                                            )
                                else:
                                    forced_sections[section_name] = part

                        if len(forced_sections) > 2:
                            logger.info(
                                f"✅ 페이지 분할 성공: {len(forced_sections)}개 섹션"
                            )
                            break

            # 3단계: 최후 수단 - 고정 크기 분할
            if len(forced_sections) <= 1:
                logger.warning("🔄 3단계 강제 분할 실행 (고정 크기)")
                forced_sections = {}

                # 문장 경계를 고려한 고정 크기 분할
                sentences = text.split(". ")
                current_section = ""
                section_count = 1

                for sentence in sentences:
                    if len(current_section) + len(sentence) > max_section_size:
                        if current_section.strip():
                            section_name = f"고정분할_{section_count:02d}_section"
                            forced_sections[section_name] = current_section.strip()
                            section_count += 1
                        current_section = sentence + ". "
                    else:
                        current_section += sentence + ". "

                # 마지막 섹션
                if current_section.strip():
                    section_name = f"고정분할_{section_count:02d}_section"
                    forced_sections[section_name] = current_section.strip()

            logger.info(f"💪 강제 분할 완료: {len(forced_sections)}개 섹션 생성")
            return forced_sections

        except Exception as e:
            logger.error(f"❌ 강제 분할 실패: {e}")
            # 최후의 최후 수단
            section_size = min(max_section_size, len(text))
            return {"99_강제분할_전체": text[:section_size]}

    def _validate_dart_section_quality(
        self, dart_dictionary: Dict, report_type: str
    ) -> Dict[str, Any]:
        """
        DART 딕셔너리의 섹션 품질을 검증합니다.

        Args:
            dart_dictionary: DART 딕셔너리
            report_type: 보고서 타입 ("business" 또는 "quarterly")

        Returns:
            Dict: 품질 검증 결과
        """
        validation_result = {
            "total_sections": 0,
            "valid_sections": 0,
            "quality_score": 0,
            "issues": [],
            "recommendations": [],
        }

        if not dart_dictionary:
            validation_result["issues"].append("딕셔너리가 비어있습니다")
            return validation_result

        total_sections = len(dart_dictionary)
        validation_result["total_sections"] = total_sections

        if total_sections == 0:
            validation_result["issues"].append("섹션이 없습니다")
            return validation_result

        valid_sections = 0
        total_content_length = 0

        for section_name, section_content in dart_dictionary.items():
            # 섹션 내용 검증
            if not section_content:
                validation_result["issues"].append(
                    f"섹션 '{section_name}' 내용이 비어있습니다"
                )
                continue

            content_length = len(str(section_content))
            total_content_length += content_length

            # 최소 내용 길이 검증 (100자 이상)
            if content_length < 100:
                validation_result["issues"].append(
                    f"섹션 '{section_name}' 내용이 너무 짧습니다 ({content_length}자)"
                )
                continue

            # 의미있는 섹션명 검증
            meaningful_keywords = [
                "재무",
                "경영",
                "사업",
                "매출",
                "이익",
                "자산",
                "부채",
                "현금",
                "투자",
                "리스크",
            ]
            has_meaningful_content = any(
                keyword in str(section_content) for keyword in meaningful_keywords
            )

            if not has_meaningful_content:
                validation_result["issues"].append(
                    f"섹션 '{section_name}'에 의미있는 재무 정보가 부족합니다"
                )
                continue

            valid_sections += 1

        validation_result["valid_sections"] = valid_sections

        # 품질 점수 계산 (0-100)
        if total_sections > 0:
            section_ratio = valid_sections / total_sections
            avg_content_length = (
                total_content_length / total_sections if total_sections > 0 else 0
            )

            # 섹션 비율 (40%) + 평균 내용 길이 (30%) + 전체 섹션 수 (30%)
            section_score = section_ratio * 40
            length_score = (
                min(avg_content_length / 1000, 1.0) * 30
            )  # 1000자 이상이면 만점
            count_score = min(total_sections / 10, 1.0) * 30  # 10개 이상이면 만점

            validation_result["quality_score"] = int(
                section_score + length_score + count_score
            )

        # 권장사항 생성
        if validation_result["quality_score"] < 50:
            validation_result["recommendations"].append(
                "섹션 분할 품질이 낮습니다. 더 상세한 분석이 필요합니다"
            )
        elif validation_result["quality_score"] < 80:
            validation_result["recommendations"].append(
                "섹션 품질이 양호하지만 개선 여지가 있습니다"
            )
        else:
            validation_result["recommendations"].append("섹션 품질이 우수합니다")

        return validation_result

    def _log_dart_quality_validation(
        self, business_validation: Dict, quarterly_validation: Dict, company_name: str
    ):
        """
        DART 품질 검증 결과를 로깅합니다.

        Args:
            business_validation: 사업보고서 품질 검증 결과
            quarterly_validation: 분기보고서 품질 검증 결과
            company_name: 기업명
        """
        logger.info(f"🔍 {company_name} DART 딕셔너리 품질 검증 결과:")

        # 사업보고서 품질
        if business_validation["total_sections"] > 0:
            logger.info(
                f"📊 사업보고서: {business_validation['valid_sections']}/{business_validation['total_sections']}개 섹션 유효 (품질점수: {business_validation['quality_score']}/100)"
            )
            if business_validation["issues"]:
                for issue in business_validation["issues"][:3]:  # 상위 3개만
                    logger.warning(f"  ⚠️ {issue}")
        else:
            logger.warning(f"📊 사업보고서: 섹션 없음")

        # 분기보고서 품질
        if quarterly_validation["total_sections"] > 0:
            logger.info(
                f"📊 분기보고서: {quarterly_validation['valid_sections']}/{quarterly_validation['total_sections']}개 섹션 유효 (품질점수: {quarterly_validation['quality_score']}/100)"
            )
            if quarterly_validation["issues"]:
                for issue in quarterly_validation["issues"][:3]:  # 상위 3개만
                    logger.warning(f"  ⚠️ {issue}")
        else:
            logger.warning(f"📊 분기보고서: 섹션 없음")
