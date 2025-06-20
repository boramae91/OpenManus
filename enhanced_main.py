#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
개선된 주식 분석 시스템 (Enhanced Main Flow)

새로운 플로우:
1. 프롬프트 입력
2. 종목+종목코드 감지
3. 📊 DART API + yfinance 재무정보 수집
4. 🏷️ Classifier (재무데이터 기반 분류)
5. 📈 분석 에이전트 (재무데이터 기반 상세분석)
6. 💾 JSON 파일 생성 (모든 데이터 포함)
"""

import asyncio
import glob
import json
import os
import re
import time
from typing import Any, Dict, List, Optional

# 환경변수 로딩 (가장 먼저 실행)
from dotenv import load_dotenv

load_dotenv()  # .env 파일에서 환경변수 로딩

# 프로젝트 경로 설정
import sys
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 모듈 import
from app.agent.manus import Manus

# 종목 분류 기능 제거 - from app.agent.stock_classifier import StockClassifier
from app.agent.stock_name_extractor import StockNameExtractor

# 🚀 One-Hot Sector Activation 시스템 import
from app.crew.smart_sector_manager import AnalysisDepth, SmartSectorManager
from app.data_collector import FinancialDataCollector
from app.data_collector.enhanced_financial_data_collector import (
    EnhancedDartDataCollector,
)
from app.llm import LLM
from app.logger import logger

# 🚀 io_logger 모듈을 import해서 일관된 로그 저장을 위해 사용해요
from io_logger import save_interaction_log

# 동적 종목 정보 추출을 위한 AI 에이전트 import
try:
    from app.agent.dynamic_stock_extractor import DynamicStockExtractor

    DYNAMIC_EXTRACTOR_AVAILABLE = True
    logger.info("🚀 동적 종목 추출 에이전트 로드 성공!")
except ImportError as e:
    logger.warning(f"동적 종목 추출 에이전트 로드 실패: {e}")
    DYNAMIC_EXTRACTOR_AVAILABLE = False

from app.utils.large_pdf_analyzer import LargePDFAnalyzer

# 기존 PDFReader는 제거하고 LargePDFAnalyzer로 완전 대체
# 대용량 PDF 원문 추출을 위한 전용 시스템 사용


class EnhancedStockAnalysisSystem:
    """
    개선된 주식 분석 시스템 클래스
    실제 재무데이터를 기반으로 정확한 분석을 수행해요!
    + 🚀 One-Hot Sector Activation으로 90% 비용 절감!
    """

    def __init__(self):
        """시스템 초기화"""
        logger.info("🚀 개선된 주식 분석 시스템 초기화...")

        # 에이전트들 초기화
        self.llm = LLM()
        # 종목 분류 기능 제거 - self.stock_classifier = StockClassifier(llm=self.llm)
        self.manus_agent = Manus(llm=self.llm)

        # 🤖 종목 감지용 AI 에이전트들 초기화
        self.stock_name_extractor = StockNameExtractor()
        if DYNAMIC_EXTRACTOR_AVAILABLE:
            self.dynamic_stock_extractor = DynamicStockExtractor()
            logger.info("🎯 동적 종목 추출 에이전트 초기화 완료")
        else:
            self.dynamic_stock_extractor = None
            logger.warning("⚠️ 동적 종목 추출 에이전트 사용 불가")

        # 재무데이터 수집기 초기화 (DART API 키는 선택사항)
        dart_api_key = os.getenv("DART_API_KEY")  # 환경변수에서 가져오기
        self.financial_collector = FinancialDataCollector(dart_api_key=dart_api_key)

        # 🚀 Enhanced DART API 수집기 초기화 (새로운 기능들)
        self.enhanced_dart_collector = EnhancedDartDataCollector(
            dart_api_key=dart_api_key
        )

        # 🏢 Dataset 매핑 테이블 로드 (ticker_bbg 변환용)
        self.stock_mapping_table = self._load_stock_mapping_tables()

        # 📄 대용량 PDF 분석기 초기화 (새로 추가!)
        self.large_pdf_analyzer = LargePDFAnalyzer(llm=self.llm)

        # 🚀 One-Hot Sector Activation 시스템 초기화 (핵심 혁신!)
        try:
            self.smart_sector_manager = SmartSectorManager(llm=self.llm)
            logger.info("🎯 One-Hot 섹터 전문가 시스템 초기화 완료!")
            logger.info("💰 비용 절감: 기존 55개 → 5개 에이전트 (90% 절약)")
        except Exception as e:
            logger.error(f"One-Hot 섹터 시스템 초기화 실패: {e}")
            self.smart_sector_manager = None

        # 결과 저장용
        self.analysis_results = {}

        logger.info("✅ 모든 컴포넌트 초기화 완료!")

        # DART API 상태 로그
        if dart_api_key:
            logger.info("🔑 DART API 키가 설정되었습니다 - Enhanced 기능 사용 가능!")
        else:
            logger.warning("⚠️ DART API 키가 없습니다 - yfinance 데이터만 사용됩니다")

    async def run_enhanced_analysis(self, user_prompt: str) -> Dict[str, Any]:
        """
        🚀 개선된 종합 주식 분석 시스템 (수정된 워크플로우)

        수정된 워크플로우:
        0. 🎯 사용자 의도 분석
        1. 📋 종목 감지 (AI 웹검색 우선)
        1.5. 🏷️ ticker_bbg + GICS 섹터 매핑
        2. 📊 재무데이터 수집 (기본 + Enhanced DART)
        3. 📈 의도 맞춤형 정보 수집 (Manus Agent 먼저 실행)
        4. 🎯 CrewAI 종합 분석 (모든 데이터 통합 분석)
        5. 📋 종합 결과 정리
        6. 💾 JSON 저장

        Args:
            user_prompt: 사용자 입력 프롬프트

        Returns:
            Dict: 전체 분석 결과
        """
        logger.info(f"🔍 개선된 분석 시작 (수정된 워크플로우): {user_prompt}")

        results = {
            "user_prompt": user_prompt,
            "timestamp": datetime.now().isoformat(),
            "analysis_flow": "enhanced_manus_first_crewai_synthesis",
            "success": False,
            "steps": {},
        }

        try:
            # 🚀 Step 0: 질문 의도 분석
            logger.info("🎯 Step 0: 사용자 질문 의도 분석")
            intent_analysis = await self.analyze_user_intent(user_prompt)
            results["steps"]["step0_intent_analysis"] = intent_analysis
            logger.info(
                f"✅ 의도 분석 완료: {intent_analysis['primary_intent']} (신뢰도: {intent_analysis['confidence']})"
            )

            # Step 1: 종목 및 종목코드 감지
            logger.info("📋 Step 1: 종목 및 종목코드 감지")
            stock_info = await self.extract_stock_info(user_prompt)
            results["steps"]["step1_stock_detection"] = stock_info

            if not stock_info["detected"]:
                results["error"] = "종목이나 종목코드를 감지할 수 없습니다"
                logger.warning("⚠️ 종목 감지 실패")
                return results

            logger.info(
                f"✅ 감지된 종목: {stock_info['stock_name']} ({stock_info['stock_code']})"
            )

            # 🏢 Step 1.5: ticker_bbg + GICS 섹터 매핑 시도
            logger.info("🏷️ Step 1.5: ticker_bbg + GICS 섹터 매핑 시도")
            mapping_result = self.get_ticker_bbg_from_name(
                stock_name=stock_info.get("stock_name"),
                stock_code=stock_info.get("stock_code"),
            )

            # stock_info에 매핑 결과 추가 (🎯 GICS 섹터 포함!)
            stock_info["ticker_bbg"] = mapping_result["ticker_bbg"]
            stock_info["gics_sector"] = mapping_result["gics_sector"]
            stock_info["mapped_company_name"] = mapping_result["company_name"]
            stock_info["market_index"] = mapping_result.get("market_index", "Unknown")
            stock_info["original_stock_code"] = stock_info.get("stock_code")
            stock_info["original_stock_name"] = stock_info.get("stock_name")

            if mapping_result["ticker_bbg"] != (
                stock_info.get("stock_code") or stock_info.get("stock_name")
            ):
                logger.info(f"🎯 ticker_bbg 매핑 성공: {mapping_result['ticker_bbg']}")
                logger.info(f"🏢 GICS 섹터 감지: {mapping_result['gics_sector']}")
            else:
                logger.info("ℹ️ ticker_bbg 매핑: 원본 코드 유지")
                if mapping_result["gics_sector"] != "Unknown":
                    logger.info(f"🏢 GICS 섹터 감지: {mapping_result['gics_sector']}")

            # 분석 결과에 매핑 정보 업데이트
            results["steps"]["step1_stock_detection"] = stock_info

            # Step 2: 재무데이터 수집 (기본 + Enhanced DART)
            logger.info("📊 Step 2: 실제 재무데이터 수집")

            # 2-1: 기본 재무데이터 수집 (yfinance + 기본 DART)
            financial_data = self.financial_collector.collect_stock_data(
                stock_code=stock_info["stock_code"], stock_name=stock_info["stock_name"]
            )
            results["steps"]["step2_financial_data"] = financial_data

            if not financial_data["success"]:
                logger.warning("⚠️ 기본 재무데이터 수집 실패 - 기존 방식으로 진행")
            else:
                logger.info(
                    f"✅ 기본 재무데이터 수집 완료 (출처: {', '.join(financial_data['data_sources'])})"
                )

            # 2-2: 🚀 Enhanced DART API 데이터 수집 (새로운 기능들)
            enhanced_dart_data = None
            if self.enhanced_dart_collector.is_available() and self._is_korean_stock(
                stock_info["stock_code"]
            ):
                logger.info("🔍 Enhanced DART 데이터 수집 시작...")
                enhanced_dart_data = (
                    self.enhanced_dart_collector.get_comprehensive_company_analysis(
                        stock_code=stock_info["stock_code"],
                        company_name=stock_info.get("stock_name"),
                    )
                )

                if enhanced_dart_data["success"]:
                    results["steps"]["step2_enhanced_dart_data"] = enhanced_dart_data
                    logger.info("✅ Enhanced DART 데이터 수집 완료!")
                else:
                    logger.warning(
                        f"⚠️ Enhanced DART 데이터 수집 실패: {enhanced_dart_data.get('error')}"
                    )
            else:
                logger.info(
                    "ℹ️ Enhanced DART 데이터 수집 생략 (API 키 없음 또는 해외 종목)"
                )

            # 🚀 Step 3: 의도 맞춤형 정보 수집 (Manus Agent 먼저 실행!)
            logger.info("📈 Step 3: 의도 맞춤형 정보 수집 (Manus Agent 웹검색 우선)")
            classification_result = {"performed": False, "reason": "분류 기능 제거됨"}

            manus_collection_result = await self.perform_information_collection_first(
                user_prompt,
                stock_info,
                financial_data,
                classification_result,
                enhanced_dart_data,
                intent_analysis,
            )
            results["steps"]["step3_information_collection"] = manus_collection_result

            # 🚀 PDF 분석 결과가 있다면 별도 스텝으로 추가 (chunking 정보 포함)
            if manus_collection_result.get("pdf_analysis", {}).get("pdf_detected"):
                logger.info(
                    "📄 PDF 분석 결과 감지됨 - 별도 단계로 기록 (chunking 포함)"
                )
                pdf_analysis_data = manus_collection_result["pdf_analysis"]

                # Chunking 정보 로그
                pdf_content = pdf_analysis_data.get("pdf_content", {})
                if pdf_content.get("chunking_applied"):
                    total_chunks = pdf_content.get("total_chunks", 0)
                    chunk_types = pdf_content.get("chunk_types", [])
                    logger.info(
                        f"📄 PDF Chunking 적용됨: {total_chunks}개 청크, 타입: {', '.join(chunk_types)}"
                    )

                results["steps"]["pdf_large_analysis"] = pdf_analysis_data

            # 🎯 Step 4: CrewAI 종합 분석 (모든 데이터 통합!)
            sector_analysis_result = None
            if self.smart_sector_manager:
                logger.info(
                    "🎯 Step 4: CrewAI 종합 분석 (재무데이터 + Manus 수집 정보 통합)"
                )
                try:
                    # 분석 깊이 자동 감지
                    analysis_depth = self._detect_analysis_depth_from_prompt(
                        user_prompt
                    )

                    # 🚀 통합 데이터로 CrewAI 섹터별 전문가 분석 수행 (🎯 GICS 섹터 사전 감지됨!)
                    sector_analysis_result = await self.smart_sector_manager.analyze_with_comprehensive_data(
                        user_prompt=user_prompt,
                        stock_name=stock_info.get("stock_name"),
                        stock_code=stock_info.get("stock_code"),
                        financial_data=financial_data,
                        enhanced_dart_data=enhanced_dart_data,
                        manus_collected_data=manus_collection_result,  # 🚀 Manus 수집 데이터 추가
                        analysis_depth=analysis_depth,
                        pre_detected_gics_sector=stock_info.get(
                            "gics_sector"
                        ),  # 🎯 사전 감지된 GICS 섹터 전달
                    )

                    results["steps"][
                        "step4_crewai_comprehensive_analysis"
                    ] = sector_analysis_result
                    logger.info(
                        f"✅ CrewAI 종합 분석 완료 - 섹터: {sector_analysis_result.get('detected_sector', '알 수 없음')}"
                    )

                except Exception as e:
                    logger.error(f"CrewAI 종합 분석 실패: {e}")
                    results["steps"]["step4_crewai_comprehensive_analysis"] = {
                        "error": str(e)
                    }

            # Step 5: 종합 결과 정리
            logger.info("📋 Step 5: 종합 결과 정리")
            final_summary = self.create_comprehensive_summary_v2(results)
            results["final_summary"] = final_summary

            # Step 6: JSON 파일 저장
            logger.info("💾 Step 6: 결과 저장")
            saved_file = self.save_enhanced_results(results, stock_info)
            results["saved_file"] = saved_file

            results["success"] = True
            logger.info("🎉 개선된 분석 완료 (수정된 워크플로우)!")

        except Exception as e:
            logger.error(f"❌ 분석 중 오류 발생: {e}")
            results["error"] = str(e)

        return results

    async def perform_information_collection_first(
        self,
        user_prompt: str,
        stock_info: Dict,
        financial_data: Dict,
        classification_result: Dict,
        enhanced_dart_data: Dict = None,
        intent_analysis: Dict = None,
    ) -> Dict[str, Any]:
        """
        📈 정보 수집 우선 실행 (CrewAI 피딩용 데이터 준비)

        Manus Agent가 먼저 웹 검색으로 정보를 수집하고,
        이 결과를 나중에 CrewAI에게 피딩할 수 있도록 준비해요.

        Args:
            user_prompt: 사용자 질문
            stock_info: 감지된 종목 정보
            financial_data: 수집된 재무데이터
            classification_result: 분류 결과
            enhanced_dart_data: Enhanced DART 데이터
            intent_analysis: 의도 분석 결과

        Returns:
            Dict: Manus Agent 수집 결과 (CrewAI 피딩용)
        """
        try:
            logger.info("📈 Manus Agent 정보 수집 시작 (CrewAI 피딩 준비)...")

            # 의도 분석 결과 추출
            primary_intent = intent_analysis.get("primary_intent", "일반문의")
            analysis_focus = intent_analysis.get("analysis_focus", "종합분석")
            data_priority = intent_analysis.get("data_priority", "기본")
            confidence = intent_analysis.get("confidence", 0.0)

            logger.info(
                f"🎯 정보 수집 - 의도: {primary_intent}, 포커스: {analysis_focus}, 신뢰도: {confidence:.2f}"
            )

            # 🎯 정보 수집용 프롬프트 구성 (CrewAI 피딩을 위한 포괄적 수집)
            collection_prompt = f"""
사용자의 핵심 질문: {user_prompt}

분석 대상: {stock_info.get('stock_name', '정보없음')} ({stock_info.get('stock_code', '정보없음')})
감지된 의도: {primary_intent}
분석 포커스: {analysis_focus}

🎯 **정보 수집 미션**:
다음 정보들을 웹에서 포괄적으로 수집해주세요. 이 정보는 나중에 전문가 팀(CrewAI)이 종합 분석할 때 사용됩니다:

1. **최신 뉴스 및 이슈**: 최근 1개월 내 주요 뉴스, 공시, 이슈들
2. **시장 동향**: 해당 종목 관련 시장 트렌드, 업계 동향
3. **애널리스트 의견**: 증권사 리포트, 목표가, 투자 의견
4. **경쟁사 정보**: 주요 경쟁업체 현황과 비교 정보
5. **기술적 분석**: 차트 패턴, 기술적 지표 현황
6. **특별 정보**: PDF 보고서, 특별 자료 등 (발견시 자동 분석)

**중요**: 단순 요약이 아닌, 나중에 전문가들이 분석할 수 있도록 상세한 정보를 수집해주세요.
"""

            # 재무데이터 포함 (참고자료로)
            basic_financial_included = False
            if financial_data.get("success"):
                financial_summary = self.financial_collector.get_analysis_summary(
                    financial_data
                )
                collection_prompt += f"""

📊 **참고 재무데이터**:
{financial_summary}
"""
                basic_financial_included = True

            # Enhanced DART 데이터 포함
            enhanced_dart_included = False
            if enhanced_dart_data and enhanced_dart_data.get("success"):
                enhanced_summary = self._create_comprehensive_dart_analysis(
                    enhanced_dart_data
                )
                if enhanced_summary:
                    collection_prompt += f"""

🚀 **Enhanced DART 상세정보**:
{enhanced_summary}
"""
                    enhanced_dart_included = True

            collection_prompt += f"""

📋 **수집 지침**:
- 위의 재무데이터는 참고용이며, 추가 정보 수집에 집중해주세요
- 모든 정보는 나중에 전문가 팀이 종합 분석할 예정입니다
- 특히 {primary_intent} 관련 정보를 중점적으로 수집해주세요
- PDF나 특별 자료 발견시 즉시 분석해주세요
"""

            logger.info(f"🎯 정보 수집 프롬프트 생성 완료 - 의도: {primary_intent}")

            # Manus 에이전트 실행
            self.manus_agent.memory.clear()
            self.manus_agent.update_memory("user", collection_prompt)

            collection_response = ""
            run_result = await self.manus_agent.run()

            if hasattr(run_result, "__aiter__"):
                async for response in run_result:
                    collection_response += response + "\n"
            else:
                collection_response = str(run_result)

            # 📄 PDF 감지 및 자동 분석
            pdf_analysis_result = await self._detect_and_analyze_pdf_from_response(
                collection_response, stock_info
            )

            return {
                "performed": True,
                "method": f"information_collection_for_crewai_{primary_intent}",
                "collected_information": collection_response.strip(),
                "primary_intent": primary_intent,
                "analysis_focus": analysis_focus,
                "data_priority": data_priority,
                "confidence": confidence,
                "basic_financial_data_used": basic_financial_included,
                "enhanced_dart_data_used": enhanced_dart_included,
                "collection_purpose": "crewai_feeding",
                "ready_for_crewai": True,
                # 📄 PDF 분석 결과 추가
                "pdf_analysis": pdf_analysis_result,
                "data_richness_score": self._calculate_data_richness(
                    collection_response, pdf_analysis_result
                ),
            }

        except Exception as e:
            logger.error(f"정보 수집 중 오류: {e}")
            return {
                "performed": False,
                "error": str(e),
                "primary_intent": intent_analysis.get("primary_intent", "오류"),
                "ready_for_crewai": False,
            }

    def _calculate_data_richness(
        self, collection_response: str, pdf_analysis: Dict
    ) -> float:
        """수집된 데이터의 풍부함 점수 계산 (CrewAI 피딩 품질 평가용)"""
        try:
            richness_score = 0.0

            # 텍스트 길이 기반 점수 (최대 30점)
            text_length = len(collection_response)
            if text_length > 5000:
                richness_score += 30
            elif text_length > 3000:
                richness_score += 20
            elif text_length > 1000:
                richness_score += 10
            else:
                richness_score += 5

            # 키워드 다양성 점수 (최대 25점)
            key_terms = [
                "뉴스",
                "공시",
                "애널리스트",
                "목표가",
                "리포트",
                "전망",
                "경쟁사",
                "시장",
                "업계",
                "트렌드",
            ]
            found_terms = sum(1 for term in key_terms if term in collection_response)
            richness_score += (found_terms / len(key_terms)) * 25

            # PDF 분석 보너스 (최대 25점)
            if pdf_analysis.get("pdf_detected") and pdf_analysis.get(
                "analysis_completed"
            ):
                pdf_text_length = pdf_analysis.get("pdf_content", {}).get(
                    "text_length", 0
                )
                if pdf_text_length > 10000:
                    richness_score += 25
                elif pdf_text_length > 5000:
                    richness_score += 15
                elif pdf_text_length > 1000:
                    richness_score += 10
                else:
                    richness_score += 5

            # 구조화된 정보 보너스 (최대 20점)
            structured_indicators = ["1.", "2.", "3.", "•", "-", "**", "###"]
            structure_count = sum(
                1
                for indicator in structured_indicators
                if indicator in collection_response
            )
            richness_score += min(structure_count * 2, 20)

            # 최대 100점으로 정규화
            richness_score = min(richness_score, 100.0)

            logger.info(f"📊 데이터 풍부함 점수: {richness_score:.1f}/100")
            return richness_score

        except Exception as e:
            logger.error(f"데이터 풍부함 점수 계산 오류: {e}")
            return 50.0  # 기본값

    def create_comprehensive_summary_v2(
        self, results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """수정된 워크플로우용 종합 요약 생성"""
        stock_info = results["steps"].get("step1_stock_detection", {})
        financial_data = results["steps"].get("step2_financial_data", {})
        manus_collection = results["steps"].get("step3_information_collection", {})
        crewai_analysis = results["steps"].get(
            "step4_crewai_comprehensive_analysis", {}
        )

        return {
            "analyzed_stock": {
                "name": stock_info.get("stock_name"),
                "code": stock_info.get("stock_code"),
                "ticker_bbg": stock_info.get("ticker_bbg"),
                "gics_sector": stock_info.get(
                    "gics_sector", "Unknown"
                ),  # 🎯 GICS 섹터 추가
                "market_index": stock_info.get(
                    "market_index", "Unknown"
                ),  # 🎯 시장 지수 추가
                "detection_method": stock_info.get("detection_method"),
            },
            "data_sources": {
                "financial_data_collected": financial_data.get("success", False),
                "data_sources": financial_data.get("data_sources", []),
                "data_quality": financial_data.get("data_quality", "없음"),
                "manus_information_collected": manus_collection.get("performed", False),
                "data_richness_score": manus_collection.get("data_richness_score", 0.0),
            },
            "analysis_quality": {
                "information_collection_performed": manus_collection.get(
                    "performed", False
                ),
                "crewai_comprehensive_analysis_performed": bool(
                    crewai_analysis and not crewai_analysis.get("error")
                ),
                "financial_data_enhanced": financial_data.get("success", False),
                "workflow_type": "manus_first_crewai_synthesis",
            },
            "key_insights": self.extract_key_insights_v2(
                manus_collection, crewai_analysis
            ),
        }

    def extract_key_insights_v2(
        self, manus_collection: Dict, crewai_analysis: Dict
    ) -> Dict[str, Any]:
        """수정된 워크플로우용 핵심 인사이트 추출"""
        insights = {
            "information_collection_quality": "알 수 없음",
            "crewai_analysis_quality": "알 수 없음",
            "overall_analysis_depth": "알 수 없음",
            "data_integration_success": False,
        }

        # Manus 정보 수집 품질 평가
        if manus_collection.get("performed"):
            richness_score = manus_collection.get("data_richness_score", 0)
            if richness_score >= 80:
                insights["information_collection_quality"] = "매우 높음"
            elif richness_score >= 60:
                insights["information_collection_quality"] = "높음"
            elif richness_score >= 40:
                insights["information_collection_quality"] = "보통"
            else:
                insights["information_collection_quality"] = "낮음"

        # CrewAI 분석 품질 평가
        if crewai_analysis and not crewai_analysis.get("error"):
            insights["crewai_analysis_quality"] = "성공"
            insights["data_integration_success"] = True
        elif crewai_analysis.get("error"):
            insights["crewai_analysis_quality"] = "실패"

        # 전체 분석 깊이 평가
        if (
            insights["information_collection_quality"] in ["높음", "매우 높음"]
            and insights["crewai_analysis_quality"] == "성공"
        ):
            insights["overall_analysis_depth"] = "매우 높음"
        elif (
            insights["information_collection_quality"] != "알 수 없음"
            and insights["crewai_analysis_quality"] == "성공"
        ):
            insights["overall_analysis_depth"] = "높음"
        elif (
            insights["information_collection_quality"] != "알 수 없음"
            or insights["crewai_analysis_quality"] == "성공"
        ):
            insights["overall_analysis_depth"] = "보통"
        else:
            insights["overall_analysis_depth"] = "낮음"

        return insights

    async def extract_stock_info(self, prompt: str) -> Dict[str, Any]:
        """
        🚀 AI 기반 동적 웹검색 우선 종목 정보 추출

        순서:
        1. AI 웹검색 (최우선) - 실시간 웹 검색으로 정확한 종목코드 찾기
        2. 정규식 매핑 (백업) - 빠른 로컬 매칭
        3. 패턴 매칭 (최후 수단) - 기본 패턴 인식

        Args:
            prompt: 사용자 입력

        Returns:
            Dict: 추출된 종목 정보
        """
        result = {
            "detected": False,
            "stock_name": None,
            "stock_code": None,
            "detection_method": None,
        }

        logger.info("🚀 AI 기반 동적 웹검색 우선 종목 감지 시작...")

        try:
            # 🚀 1단계: Manus 에이전트로 AI 기반 동적 웹검색 시도 (최우선!)
            logger.info("🎯 AI 기반 동적 웹검색 시도... (최우선 방법)")

            # 종목 검색을 위한 특별한 프롬프트 구성
            search_prompt = f"""
다음 질문에서 종목명과 종목코드를 찾아주세요:
"{prompt}"

웹에서 검색해서 정확한 종목명과 6자리 종목코드를 찾아주세요.
한국 주식이면 6자리 숫자 종목코드를, 해외 주식이면 티커를 찾아주세요.

결과는 다음 형식으로 출력해주세요:
종목명: [회사명]
종목코드: [6자리 숫자 또는 티커]

예시:
종목명: 삼성전자
종목코드: 005930

예시:
종목명: Apple
종목코드: AAPL
"""

            # 메모리 초기화
            self.manus_agent.memory.clear()
            self.manus_agent.update_memory("user", search_prompt)

            # AI 에이전트 실행
            search_result = await self.manus_agent.run()

            # 결과 처리
            if hasattr(search_result, "__aiter__"):
                ai_response = ""
                async for response in search_result:
                    ai_response += response + "\n"
            else:
                ai_response = str(search_result)

            # AI 응답에서 종목 정보 추출
            extracted_info = self._parse_ai_stock_response(
                ai_response, "ai_web_search_priority"
            )
            if extracted_info["detected"]:
                result.update(extracted_info)
                logger.info(
                    f"🎉 AI 웹검색 성공 (최우선): {result['stock_name']} ({result['stock_code']})"
                )
                return result
            else:
                logger.info("⚠️ AI 웹검색에서 종목 감지 실패, 백업 방법 시도...")

            # 2단계: StockNameExtractor로 빠른 매핑 시도 (백업)
            logger.info("📝 StockNameExtractor 백업 시도...")
            extracted_name, extracted_code = (
                self.stock_name_extractor.extract_from_prompt(prompt)
            )

            if extracted_name and extracted_code:
                result["detected"] = True
                result["stock_name"] = extracted_name
                result["stock_code"] = extracted_code
                result["detection_method"] = "stock_name_extractor_backup"
                logger.info(
                    f"✅ StockNameExtractor 백업 성공: {result['stock_name']} ({result['stock_code']})"
                )
                return result
            else:
                logger.info("⚠️ StockNameExtractor 백업에서도 종목 감지 실패")

            # 3단계: 마지막 수단으로 정규식 패턴 매칭
            logger.info("🔍 정규식 패턴 매칭 시도...")
            fallback_result = self._fallback_pattern_matching(prompt)
            if fallback_result["detected"]:
                result.update(fallback_result)
                logger.info(
                    f"✅ 패턴 매칭 성공: {result['stock_name']} ({result['stock_code']})"
                )
                return result

            logger.warning("❌ 모든 방법으로 종목 감지 실패")
            return result

        except Exception as e:
            logger.error(f"❌ 종목 감지 중 오류 발생: {e}")

            # 오류 발생시 폴백으로 정규식 시도
            logger.info("🔄 오류 발생으로 폴백 패턴 매칭 시도...")
            fallback_result = self._fallback_pattern_matching(prompt)
            if fallback_result["detected"]:
                result.update(fallback_result)
                logger.info(
                    f"✅ 폴백 매칭 성공: {result['stock_name']} ({result['stock_code']})"
                )

            return result

    def _parse_ai_stock_response(self, ai_response: str, method: str) -> Dict[str, Any]:
        """AI 에이전트 응답에서 종목 정보 파싱 (한국 + 해외 종목 지원)"""
        result = {
            "detected": False,
            "stock_name": None,
            "stock_code": None,
            "detection_method": f"ai_{method}",
        }

        if not ai_response:
            return result

        logger.info(f"🔍 AI 응답 파싱 시작: {ai_response[:200]}...")

        # 1. 구조화된 패턴 우선 검색 (AI가 명시적으로 출력한 형태)
        structured_patterns = [
            # "종목명: XXX" 형태
            r"종목명\s*[:：]\s*([가-힣A-Za-z0-9\s&\-\.]+?)(?=\s*\n|$)",
            # "종목코드: XXX" 형태 (한국 6자리 + 해외 티커)
            r"종목코드\s*[:：]\s*([A-Z0-9]{2,6})(?=\s*\n|$)",
        ]

        name_matches = []
        code_matches = []

        for i, pattern in enumerate(structured_patterns):
            matches = re.findall(pattern, ai_response, re.IGNORECASE | re.MULTILINE)
            if i == 0:  # 종목명 패턴
                name_matches.extend([m.strip() for m in matches])
            else:  # 종목코드 패턴
                code_matches.extend([m.strip() for m in matches])

        # 구조화된 패턴에서 매칭 성공
        if name_matches and code_matches:
            result["detected"] = True
            result["stock_name"] = name_matches[0]
            result["stock_code"] = code_matches[0]
            logger.info(
                f"✅ 구조화된 패턴 매칭 성공: {result['stock_name']} ({result['stock_code']})"
            )
            return result

        # 2. 괄호 패턴 검색 (한국 + 해외)
        bracket_patterns = [
            # 한국 종목: "삼성전자(005930)" 또는 "한화오션(A042660)"
            r"([가-힣A-Za-z0-9\s&\-\.]+)\s*\(\s*A?([0-9]{6})\s*\)",
            # 해외 종목: "Lockheed Martin Corporation (LMT)" 또는 "Apple (AAPL)"
            r"([A-Za-z\s&\-\.]+?)\s*\(\s*([A-Z]{2,5})\s*\)",
            # 혼합 패턴: "Company Name (TICKER)" 형태
            r"([가-힣A-Za-z0-9\s&\-\.]+?)\s*\(\s*([A-Z0-9]{2,6})\s*\)",
        ]

        found_codes = []
        found_names = []

        for pattern in bracket_patterns:
            matches = re.findall(pattern, ai_response, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple) and len(match) == 2:
                    name, code = match
                    name = name.strip()
                    code = code.strip()

                    # 유효성 검증
                    if self._is_valid_stock_info(name, code):
                        found_names.append(name)
                        found_codes.append(code)
                        logger.info(f"🎯 괄호 패턴에서 발견: {name} ({code})")

        # 괄호 패턴에서 매칭 성공
        if found_codes and found_names:
            from collections import Counter

            most_common_code = Counter(found_codes).most_common(1)[0][0]
            most_common_name = Counter(found_names).most_common(1)[0][0]

            result["detected"] = True
            result["stock_code"] = most_common_code
            result["stock_name"] = most_common_name
            logger.info(
                f"✅ 괄호 패턴 매칭 성공: {result['stock_name']} ({result['stock_code']})"
            )
            return result

        # 3. 브라우저 검색 결과 패턴 (기존 로직 유지)
        browser_patterns = [
            # Company Guide 패턴: "한화오션(A042660) | 업종분석"
            r"([가-힣A-Za-z0-9\s&\-\.]+)\(A([0-9]{6})\)\s*\|\s*업종분석",
            # URL 패턴: "gicode=A042660"
            r"gicode=A([0-9]{6})",
            # 브라우저 출력 패턴: "한화오션 042660"
            r"([가-힣A-Za-z0-9\s&\-\.]+)\s+([0-9]{6})",
            # 직접 언급 패턴: "종목코드: 042660"
            r"종목코드:\s*([0-9]{6})",
        ]

        for pattern in browser_patterns:
            matches = re.findall(pattern, ai_response, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) == 2:
                        name, code = match
                        found_names.append(name.strip())
                        found_codes.append(code)
                    else:
                        # 마지막 요소가 종목코드
                        code = match[-1]
                        found_codes.append(code)
                else:
                    found_codes.append(match)

        # 브라우저 패턴에서 한국 종목코드 발견
        if found_codes:
            from collections import Counter

            most_common_code = Counter(found_codes).most_common(1)[0][0]

            # 한국 종목코드 유효성 검사
            if len(most_common_code) == 6 and most_common_code.isdigit():
                if most_common_code.startswith(("0", "1", "2", "3")):
                    result["detected"] = True
                    result["stock_code"] = most_common_code

                    # 매칭되는 회사명이 있으면 사용
                    if found_names:
                        most_common_name = Counter(found_names).most_common(1)[0][0]
                        result["stock_name"] = most_common_name.strip()

                    logger.info(
                        f"✅ 브라우저 패턴 매칭 성공: {result['stock_name']} ({result['stock_code']})"
                    )
                    return result

        logger.warning("❌ AI 응답에서 종목 정보를 찾지 못했습니다.")
        return result

    def _is_valid_stock_info(self, name: str, code: str) -> bool:
        """종목명과 코드의 유효성을 검증합니다"""
        if not name or not code:
            return False

        name = name.strip()
        code = code.strip()

        # 이름 길이 체크
        if len(name) < 2 or len(name) > 50:
            return False

        # 제외할 일반적인 단어들
        exclude_words = {
            "Company",
            "Inc",
            "Corp",
            "Ltd",
            "분석",
            "정보",
            "결과",
            "PDF",
            "URL",
            "Description",
            "Metadata",
            "Search",
            "results",
            "http",
            "www",
            "com",
            "html",
            "Step",
            "Observed",
            "output",
        }

        if name in exclude_words:
            return False

        # 코드 유효성 검사
        # 한국 종목코드 (6자리 숫자)
        if re.match(r"^\d{6}$", code):
            return True

        # 해외 티커 (2-5글자 알파벳)
        if re.match(r"^[A-Z]{2,5}$", code):
            return True

        return False

    def _fallback_pattern_matching(self, prompt: str) -> Dict[str, Any]:
        """폴백용 정규식 패턴 매칭"""
        result = {
            "detected": False,
            "stock_name": None,
            "stock_code": None,
            "detection_method": "pattern_fallback",
        }

        # 1. 6자리 종목코드 패턴 검색 (한국 주식)
        korean_code_pattern = r"\b(\d{6})\b"
        korean_codes = re.findall(korean_code_pattern, prompt)

        if korean_codes:
            result["detected"] = True
            result["stock_code"] = korean_codes[0]
            result["detection_method"] = "korean_stock_code_fallback"
            return result

        # 2. 해외 티커 패턴 검색 (2-5자리 대문자)
        ticker_pattern = r"\b([A-Z]{2,5})\b"
        tickers = re.findall(ticker_pattern, prompt.upper())

        if tickers:
            # 일반적인 단어 제외
            excluded_words = {"THE", "AND", "FOR", "YOU", "ARE", "NOT", "BUT", "CAN"}
            valid_tickers = [t for t in tickers if t not in excluded_words]

            if valid_tickers:
                result["detected"] = True
                result["stock_code"] = valid_tickers[0]
                result["detection_method"] = "ticker_symbol_fallback"
                return result

                # 3. 주요 한국 회사명 패턴 검색 (폴백용 간소화된 목록)
        korean_companies = {
            "삼성전자": "005930",
            "삼성증권": "016360",
            "SK하이닉스": "000660",
            "LG전자": "066570",
            "현대자동차": "005380",
            "카카오": "035720",
            "네이버": "035420",
            "한화에어로스페이스": "012450",
            "한화오션": "042660",
        }

        for company, code in korean_companies.items():
            if company in prompt:
                result["detected"] = True
                result["stock_name"] = company
                result["stock_code"] = code
                result["detection_method"] = "company_name_fallback"
                return result

        return result

    async def analyze_user_intent(self, user_prompt: str) -> Dict[str, Any]:
        """
        🎯 사용자 질문의 의도를 분석하는 새로운 단계

        질문 유형을 분석해서 맞춤형 분석을 위한 정보를 제공해요:
        - 주가 문의: 현재 주가나 주가 동향에 대한 질문
        - 재무분석: 재무제표나 재무비율 분석 요청
        - 투자조언: 매수/매도 의견이나 투자 전략 문의
        - 종목분류: 어떤 유형의 주식인지 분류 요청
        - 기업정보: 회사 소개나 사업 내용 문의
        - 단순조회: 간단한 정보 확인

        Args:
            user_prompt: 사용자 입력 프롬프트

        Returns:
            Dict: 의도 분석 결과
        """
        logger.info("🎯 사용자 질문 의도 분석 시작...")

        intent_result = {
            "primary_intent": "일반문의",
            "secondary_intents": [],
            "confidence": 0.0,
            # 분류 기능 제거됨 - "needs_classification": False,
            "analysis_focus": "종합분석",
            "data_priority": "기본",
            "keywords": [],
        }

        try:
            # 🔍 의도 분석을 위한 키워드 패턴들
            intent_patterns = {
                "주가문의": {
                    "keywords": [
                        "주가",
                        "가격",
                        "시세",
                        "얼마",
                        "price",
                        "현재가",
                        "종가",
                        "오늘",
                        "어제",
                        "최근",
                    ],
                    "patterns": [
                        r"주가.*얼마",
                        r"가격.*어떻게",
                        r"얼마.*거래",
                        r"현재.*주가",
                    ],
                    "focus": "주가동향",
                    "data_priority": "실시간",
                },
                "재무분석": {
                    "keywords": [
                        "재무",
                        "재무제표",
                        "손익계산서",
                        "대차대조표",
                        "현금흐름표",
                        "매출",
                        "순이익",
                        "부채비율",
                        "ROE",
                        "ROA",
                        "PER",
                        "PBR",
                    ],
                    "patterns": [
                        r"재무.*분석",
                        r"재무.*어떤",
                        r"매출.*얼마",
                        r"이익.*어느",
                    ],
                    "focus": "재무건전성",
                    "data_priority": "재무데이터",
                },
                "투자조언": {
                    "keywords": [
                        "투자",
                        "매수",
                        "매도",
                        "사야",
                        "팔아야",
                        "추천",
                        "의견",
                        "전망",
                        "미래",
                        "목표가",
                    ],
                    "patterns": [
                        r"투자.*어떻게",
                        r"사야.*할까",
                        r"매수.*의견",
                        r"전망.*어떻게",
                    ],
                    "focus": "투자의견",
                    "data_priority": "종합",
                },
                "종목분류": {
                    "keywords": [
                        "분류",
                        "유형",
                        "어떤 주식",
                        "어떤 종목",
                        "성장주",
                        "가치주",
                        "우량주",
                        "성격",
                        "특성",
                        "타입",
                    ],
                    "patterns": [
                        r"어떤.*주식",
                        r"어떤.*종목",
                        r".*분류",
                        r"유형.*무엇",
                    ],
                    "focus": "종목분류",
                    "data_priority": "종합",
                    # 분류 기능 제거됨 - "needs_classification": True,
                },
                "기업정보": {
                    "keywords": [
                        "회사",
                        "기업",
                        "사업",
                        "업종",
                        "무엇",
                        "하는",
                        "소개",
                        "설명",
                    ],
                    "patterns": [
                        r"회사.*무엇",
                        r"기업.*설명",
                        r"사업.*내용",
                        r"무엇.*하는",
                    ],
                    "focus": "기업개요",
                    "data_priority": "기본",
                },
                "배당정보": {
                    "keywords": ["배당", "배당금", "배당률", "배당수익률", "dividend"],
                    "patterns": [r"배당.*얼마", r"배당.*언제", r"배당.*정보"],
                    "focus": "배당분석",
                    "data_priority": "투자정보",
                },
            }

            # 키워드 매칭으로 의도 점수 계산
            intent_scores = {}
            found_keywords = []

            user_prompt_lower = user_prompt.lower()

            for intent_name, intent_data in intent_patterns.items():
                score = 0

                # 키워드 매칭 점수
                for keyword in intent_data["keywords"]:
                    if keyword in user_prompt_lower:
                        score += 2
                        found_keywords.append(keyword)

                # 패턴 매칭 점수 (더 높은 가중치)
                for pattern in intent_data["patterns"]:
                    if re.search(pattern, user_prompt_lower):
                        score += 5

                if score > 0:
                    intent_scores[intent_name] = score

            # 가장 높은 점수의 의도를 주 의도로 설정
            if intent_scores:
                primary_intent = max(intent_scores, key=intent_scores.get)
                max_score = intent_scores[primary_intent]

                # 신뢰도 계산 (최대 점수 기준으로 정규화)
                confidence = min(max_score / 10.0, 1.0)

                intent_result.update(
                    {
                        "primary_intent": primary_intent,
                        "confidence": confidence,
                        "analysis_focus": intent_patterns[primary_intent]["focus"],
                        "data_priority": intent_patterns[primary_intent][
                            "data_priority"
                        ],
                        # 분류 기능 제거됨 - "needs_classification": intent_patterns[primary_intent].get("needs_classification", False),
                        "keywords": found_keywords,
                    }
                )

                # 2차 의도들 (점수가 절반 이상인 것들)
                threshold = max_score * 0.5
                secondary_intents = [
                    intent
                    for intent, score in intent_scores.items()
                    if intent != primary_intent and score >= threshold
                ]
                intent_result["secondary_intents"] = secondary_intents

                logger.info(
                    f"🎯 의도 분석 완료: {primary_intent} (점수: {max_score}, 신뢰도: {confidence:.2f})"
                )
                if secondary_intents:
                    logger.info(f"🔍 2차 의도: {', '.join(secondary_intents)}")
            else:
                logger.info("🤔 명확한 의도를 감지하지 못했습니다 - 일반 분석 진행")
                intent_result["confidence"] = 0.3  # 기본 신뢰도

        except Exception as e:
            logger.error(f"❌ 의도 분석 중 오류: {e}")
            intent_result["error"] = str(e)
            intent_result["confidence"] = 0.1

        return intent_result

    def _is_korean_stock(self, stock_code: str) -> bool:
        """한국 주식인지 확인해요 (6자리 숫자면 한국 주식)"""
        if not stock_code:
            return False
        return len(stock_code) == 6 and stock_code.isdigit()

    def _detect_analysis_depth_from_prompt(self, user_prompt: str) -> AnalysisDepth:
        """
        🎯 사용자 프롬프트에서 분석 깊이 자동 감지

        키워드 기반으로 사용자가 원하는 분석 수준을 파악해요:
        - QUICK: 간단한 질문, 빠른 답변 필요
        - STANDARD: 일반적인 분석 요청
        - DEEP: 상세한 분석, 투자 결정 관련

        Args:
            user_prompt: 사용자 입력 프롬프트

        Returns:
            AnalysisDepth: 감지된 분석 깊이
        """
        prompt_lower = user_prompt.lower()

        # DEEP 분석 키워드 (상세 분석 필요)
        deep_keywords = [
            "상세",
            "자세히",
            "깊이",
            "투자",
            "매수",
            "매도",
            "투자결정",
            "포트폴리오",
            "리스크",
            "위험",
            "전망",
            "목표가",
            "적정가",
            "밸류에이션",
            "dcf",
            "재무제표",
            "손익계산서",
            "현금흐름",
            "부채비율",
            "수익성",
        ]

        # QUICK 분석 키워드 (빠른 답변)
        quick_keywords = [
            "간단히",
            "빠르게",
            "요약",
            "개요",
            "현재",
            "지금",
            "오늘",
            "주가",
            "시가총액",
            "거래량",
            "52주",
            "배당",
        ]

        # 키워드 카운트
        deep_count = sum(1 for keyword in deep_keywords if keyword in prompt_lower)
        quick_count = sum(1 for keyword in quick_keywords if keyword in prompt_lower)

        # 프롬프트 길이도 고려 (긴 질문 = 상세한 답변 원함)
        prompt_length = len(user_prompt)

        if deep_count >= 2 or prompt_length > 200:
            logger.info("🔍 DEEP 분석 모드 감지 - 상세한 전문가 분석 수행")
            return AnalysisDepth.DEEP
        elif quick_count >= 2 or prompt_length < 50:
            logger.info("⚡ QUICK 분석 모드 감지 - 빠른 핵심 분석 수행")
            return AnalysisDepth.QUICK
        else:
            logger.info("📊 STANDARD 분석 모드 감지 - 균형잡힌 분석 수행")
            return AnalysisDepth.STANDARD

    def _load_stock_mapping_tables(self) -> Dict[str, pd.DataFrame]:
        """
        Dataset CSV 파일들을 로드해서 종목명과 ticker_bbg를 매핑하는 테이블을 생성합니다.
        """
        logger.info("📊 종목 매핑 테이블 로드 시작...")

        mapping_tables = {}

        try:
            # dataset-bbg-*.csv 파일들 찾기
            current_dir = os.path.dirname(os.path.abspath(__file__))
            dataset_files = glob.glob(os.path.join(current_dir, "dataset-bbg-*.csv"))

            for file_path in dataset_files:
                logger.info(f"📁 데이터셋 로드: {os.path.basename(file_path)}")

                try:
                    # CSV 파일 읽기
                    df = pd.read_csv(file_path)

                    # 파일명에서 지수명 추출 (예: KOSPI Index, KOSDAQ Index)
                    filename = os.path.basename(file_path)
                    market_index = filename.split("-")[2].replace(
                        " ", "_"
                    )  # KOSPI Index -> KOSPI_Index

                    # 필요한 컬럼이 있는지 확인
                    required_cols = ["ticker_bbg"]
                    if not all(col in df.columns for col in required_cols):
                        logger.warning(f"⚠️ 필수 컬럼 누락: {file_path}")
                        continue

                    # 매핑 테이블에 저장
                    mapping_tables[market_index] = df
                    logger.info(f"✅ {market_index}: {len(df)} 종목 로드 완료")

                except Exception as e:
                    logger.error(f"❌ 파일 로드 실패 {file_path}: {e}")
                    continue

            # 전체 매핑 테이블도 생성 (모든 지수 통합)
            if mapping_tables:
                all_stocks = pd.concat(mapping_tables.values(), ignore_index=True)
                mapping_tables["ALL"] = all_stocks
                logger.info(f"✅ 전체 통합 테이블: {len(all_stocks)} 종목")

            logger.info(f"🎯 총 {len(mapping_tables)} 개 매핑 테이블 로드 완료")

        except Exception as e:
            logger.error(f"❌ 매핑 테이블 로드 실패: {e}")
            mapping_tables = {}

        return mapping_tables

    def get_ticker_bbg_from_name(
        self, stock_name: str, stock_code: str = None
    ) -> Dict[str, str]:
        """
        종목명 또는 종목코드로부터 ticker_bbg와 GICS 섹터 정보를 찾아서 반환합니다.

        Args:
            stock_name: 종목명 (한글 또는 영문)
            stock_code: 종목코드 (선택사항)

        Returns:
            Dict: {"ticker_bbg": str, "gics_sector": str, "company_name": str} 또는 원본 정보
        """
        if not self.stock_mapping_table:
            logger.warning("⚠️ 매핑 테이블이 없어서 원본 정보를 반환합니다")
            return {
                "ticker_bbg": stock_code or stock_name,
                "gics_sector": "Unknown",
                "company_name": stock_name or stock_code or "Unknown",
            }

        try:
            # 전체 통합 테이블 사용
            df = self.stock_mapping_table.get("ALL")
            if df is None or df.empty:
                logger.warning("⚠️ 통합 매핑 테이블이 비어있습니다")
                return {
                    "ticker_bbg": stock_code or stock_name,
                    "gics_sector": "Unknown",
                    "company_name": stock_name or stock_code or "Unknown",
                }

            matched_row = None

            # 1. 종목코드로 먼저 찾기 (가장 정확함)
            if stock_code:
                # 한국 종목코드는 6자리 숫자
                if re.match(r"^\d{6}$", stock_code):
                    # ticker_bbg에서 종목코드 부분 추출해서 매칭
                    matched = df[
                        df["ticker_bbg"].str.contains(f"{stock_code} KS", na=False)
                    ]
                    if not matched.empty:
                        matched_row = matched.iloc[0]
                        logger.info(
                            f"✅ 종목코드 매칭 성공: {stock_code} -> {matched_row['ticker_bbg']}"
                        )

                if matched_row is None:
                    # 해외 종목코드 직접 매칭
                    matched = df[df["ticker_bbg"].str.contains(stock_code, na=False)]
                    if not matched.empty:
                        matched_row = matched.iloc[0]
                        logger.info(
                            f"✅ 종목코드 매칭 성공: {stock_code} -> {matched_row['ticker_bbg']}"
                        )

            # 2. 종목명으로 찾기 (한글 우선)
            if matched_row is None and stock_name:
                # 한글명 매칭 (NAME_KOREAN 컬럼)
                if "NAME_KOREAN" in df.columns:
                    matched = df[df["NAME_KOREAN"].str.contains(stock_name, na=False)]
                    if not matched.empty:
                        matched_row = matched.iloc[0]
                        logger.info(
                            f"✅ 한글명 매칭 성공: {stock_name} -> {matched_row['ticker_bbg']}"
                        )

                if matched_row is None:
                    # 영문명 매칭 (NAME 컬럼)
                    if "NAME" in df.columns:
                        matched = df[
                            df["NAME"].str.contains(
                                stock_name.upper(), na=False, case=False
                            )
                        ]
                        if not matched.empty:
                            matched_row = matched.iloc[0]
                            logger.info(
                                f"✅ 영문명 매칭 성공: {stock_name} -> {matched_row['ticker_bbg']}"
                            )

                if matched_row is None:
                    # 부분 매칭 시도 (더 관대한 매칭)
                    if "NAME_KOREAN" in df.columns:
                        for _, row in df.iterrows():
                            if (
                                pd.notna(row["NAME_KOREAN"])
                                and stock_name in row["NAME_KOREAN"]
                            ):
                                matched_row = row
                                logger.info(
                                    f"✅ 부분 매칭 성공: {stock_name} -> {matched_row['ticker_bbg']}"
                                )
                                break

            # 3. 매칭 성공 시 전체 정보 반환 (🎯 GICS 섹터 포함!)
            if matched_row is not None:
                result = {
                    "ticker_bbg": matched_row.get(
                        "ticker_bbg", stock_code or stock_name
                    ),
                    "gics_sector": matched_row.get("GICS_SECTOR_NAME", "Unknown"),
                    "company_name": matched_row.get("NAME", stock_name or "Unknown"),
                    "market_index": matched_row.get("market_index", "Unknown"),
                }

                logger.info(f"🎯 GICS 섹터 감지 성공: {result['gics_sector']}")
                return result

            # 4. 매칭 실패
            logger.warning(f"⚠️ 매핑 실패: {stock_name} ({stock_code}) - 원본 반환")
            return {
                "ticker_bbg": stock_code or stock_name,
                "gics_sector": "Unknown",
                "company_name": stock_name or stock_code or "Unknown",
            }

        except Exception as e:
            logger.error(f"❌ ticker_bbg 매핑 중 오류: {e}")
            return {
                "ticker_bbg": stock_code or stock_name,
                "gics_sector": "Unknown",
                "company_name": stock_name or stock_code or "Unknown",
            }

    # 종목 분류 기능 제거됨 - perform_selective_classification 메서드 삭제

    # 종목 분류 기능 제거됨 - perform_enhanced_classification 메서드 삭제

    async def perform_intent_based_analysis(
        self,
        user_prompt: str,
        stock_info: Dict,
        financial_data: Dict,
        classification_result: Dict,
        enhanced_dart_data: Dict = None,
        intent_analysis: Dict = None,
        sector_analysis: Dict = None,  # 🚀 새로운 섹터 분석 결과 추가
    ) -> Dict[str, Any]:
        """
        📈 의도 맞춤형 상세 분석 (개선된 핵심 기능!)

        사용자의 질문 의도에 따라 완전히 다른 분석을 수행하는 혁신적인 시스템이에요!
        기존처럼 획일적인 5단계 분석이 아니라, 사용자가 진짜 원하는 정보에 집중해요.

        Args:
            user_prompt: 사용자 질문
            stock_info: 감지된 종목 정보
            financial_data: 수집된 재무데이터
            classification_result: 분류 결과
            enhanced_dart_data: Enhanced DART 데이터
            intent_analysis: 의도 분석 결과

        Returns:
            Dict: 맞춤형 분석 결과
        """
        try:
            logger.info("📈 의도 맞춤형 분석 시작...")

            # 의도 분석 결과 추출
            primary_intent = intent_analysis.get("primary_intent", "일반문의")
            analysis_focus = intent_analysis.get("analysis_focus", "종합분석")
            data_priority = intent_analysis.get("data_priority", "기본")
            confidence = intent_analysis.get("confidence", 0.0)

            logger.info(
                f"🎯 맞춤형 분석 - 의도: {primary_intent}, 포커스: {analysis_focus}, 신뢰도: {confidence:.2f}"
            )

            # 🎯 의도별 맞춤형 분석 프롬프트 구성
            analysis_prompt = f"""
사용자의 핵심 질문: {user_prompt}

분석 대상: {stock_info.get('stock_name', '정보없음')} ({stock_info.get('stock_code', '정보없음')})
감지된 의도: {primary_intent}
분석 포커스: {analysis_focus}
"""

            # 재무데이터 포함 (항상 참고자료로 제공)
            basic_financial_included = False
            if financial_data.get("success"):
                financial_summary = self.financial_collector.get_analysis_summary(
                    financial_data
                )
                analysis_prompt += f"""

📊 **참고 재무데이터**:
{financial_summary}
"""
                basic_financial_included = True

            # Enhanced DART 데이터 포함
            enhanced_dart_included = False
            if enhanced_dart_data and enhanced_dart_data.get("success"):
                enhanced_summary = self._create_comprehensive_dart_analysis(
                    enhanced_dart_data
                )
                if enhanced_summary:
                    analysis_prompt += f"""

🚀 **Enhanced DART 상세정보**:
{enhanced_summary}
"""
                    enhanced_dart_included = True

            # 분류 기능 제거됨 - 분류 결과 포함 로직 삭제

            # TODO: 나머지 의도별 분석 로직을 완성해야 함
            return {
                "performed": True,
                "method": "intent_based_analysis",
                "primary_intent": primary_intent,
                "confidence": confidence,
                "response": "의도별 분석 완료 (구현 중)",
            }

        except Exception as e:
            logger.error(f"의도 맞춤형 분석 중 오류: {e}")
            return {
                "performed": False,
                "error": str(e),
                "primary_intent": intent_analysis.get("primary_intent", "오류"),
            }

    def _create_comprehensive_dart_analysis(self, enhanced_dart_data: Dict) -> str:
        """Enhanced DART 데이터를 종합적으로 분석하여 요약 문자열을 생성합니다."""
        if not enhanced_dart_data or not enhanced_dart_data.get("success"):
            return ""

        try:
            summary_parts = []

            # 기본 정보
            if enhanced_dart_data.get("basic_info"):
                basic_info = enhanced_dart_data["basic_info"]
                summary_parts.append(f"회사명: {basic_info.get('company_name', 'N/A')}")
                summary_parts.append(f"업종: {basic_info.get('business_type', 'N/A')}")

            # 재무 정보
            if enhanced_dart_data.get("financial_info"):
                financial_info = enhanced_dart_data["financial_info"]
                summary_parts.append("재무 데이터 수집 완료")

            # 공시 정보
            if enhanced_dart_data.get("disclosure_info"):
                disclosure_info = enhanced_dart_data["disclosure_info"]
                if disclosure_info.get("recent_disclosures"):
                    summary_parts.append(
                        f"최근 공시: {len(disclosure_info['recent_disclosures'])}건"
                    )

            return (
                "\n".join(summary_parts)
                if summary_parts
                else "Enhanced DART 데이터 요약 정보 없음"
            )

        except Exception as e:
            logger.error(f"Enhanced DART 분석 요약 생성 오류: {e}")
            return "Enhanced DART 데이터 분석 중 오류 발생"

    async def _detect_and_analyze_pdf_from_response(
        self, response: str, stock_info: Dict
    ) -> Dict[str, Any]:
        """응답에서 PDF를 감지하고 자동 분석합니다."""
        pdf_result = {
            "pdf_detected": False,
            "analysis_completed": False,
            "pdf_content": {},
            "analysis_method": "none",
            "pdf_dictionary_interface": None,  # 🚀 PDF 딕셔너리 인터페이스 추가!
        }

        try:
            # PDF URL 패턴 검색
            pdf_patterns = [
                r"https?://[^\s]+\.pdf",
                r"https?://[^\s]+/[^\s]*\.pdf[^\s]*",
                r"PDF.*?https?://[^\s]+",
            ]

            pdf_urls = []
            for pattern in pdf_patterns:
                matches = re.findall(pattern, response, re.IGNORECASE)
                pdf_urls.extend(matches)

            if pdf_urls:
                pdf_result["pdf_detected"] = True
                logger.info(f"📄 PDF URL 감지됨: {len(pdf_urls)}개")

                # 첫 번째 PDF만 분석 (리소스 절약)
                pdf_url = pdf_urls[0]
                logger.info(f"📄 PDF 분석 시작: {pdf_url}")

                # 🚀 CrewAI용 PDF 딕셔너리 생성 (핵심 기능!)
                logger.info("🚀 CrewAI용 PDF 딕셔너리 생성 시도...")
                pdf_dictionary_result = (
                    await self.large_pdf_analyzer.create_pdf_dictionary_for_crewai(
                        pdf_path=pdf_url,
                        company_name=stock_info.get("stock_name", "분석대상회사"),
                        max_section_size=600000,  # 🚀 60만자로 확장!
                    )
                )

                if pdf_dictionary_result.get("success"):
                    logger.info("✅ PDF 딕셔너리 생성 성공!")

                    # PDF 딕셔너리 인터페이스 저장 (CrewAI가 활용할 수 있도록)
                    pdf_result["pdf_dictionary_interface"] = pdf_dictionary_result[
                        "interface"
                    ]

                    # 기존 PDF 내용 구조에 딕셔너리 정보 추가
                    pdf_content = {
                        "pdf_url": pdf_url,
                        "text_length": pdf_dictionary_result["metadata"][
                            "total_text_length"
                        ],
                        "extraction_method": "large_pdf_analyzer_dictionary",
                        "analysis_timestamp": pdf_dictionary_result["metadata"][
                            "creation_timestamp"
                        ],
                        # 🚀 PDF 딕셔너리 구조 정보 (기존 구조 유지하면서 확장)
                        "chunking_applied": True,
                        "total_chunks": pdf_dictionary_result["metadata"][
                            "total_sections"
                        ],
                        "chunk_types": ["toc_based", "footnotes", "ai_generated"],
                        # 🎯 딕셔너리 구조화 정보 (새로 추가!)
                        "dictionary_structure": {
                            "total_sections": pdf_dictionary_result["metadata"][
                                "total_sections"
                            ],
                            "toc_based_sections": pdf_dictionary_result["metadata"][
                                "toc_based_sections"
                            ],
                            "footnote_sections": pdf_dictionary_result["metadata"][
                                "footnote_sections"
                            ],
                            "avg_section_length": pdf_dictionary_result["metadata"][
                                "avg_section_length"
                            ],
                            "dictionary_available": True,
                            "interface_ready": True,
                        },
                        # 기존 호환성을 위한 딕셔너리 구조 (enhanced_main.py 기존 로직과 호환)
                        "toc_based_chunks": pdf_dictionary_result.get(
                            "pdf_dictionary", {}
                        ),
                        "keyword_based_chunks": {},  # 딕셔너리 구조로 대체됨
                        "ai_detected_structure": pdf_dictionary_result["metadata"],
                        "chunking_metadata": {
                            "creation_method": "pdf_dictionary_for_crewai",
                            "selective_access_enabled": True,
                            "expert_distribution_ready": True,
                        },
                    }

                    pdf_result["pdf_content"] = pdf_content
                    pdf_result["analysis_completed"] = True
                    pdf_result["analysis_method"] = "pdf_dictionary_for_crewai"

                    # 상세 로그
                    logger.info(f"📊 PDF 딕셔너리 생성 완료:")
                    logger.info(
                        f"   📑 총 섹션: {pdf_dictionary_result['metadata']['total_sections']}개"
                    )
                    logger.info(
                        f"   📝 주석 섹션: {pdf_dictionary_result['metadata']['footnote_sections']}개"
                    )
                    logger.info(f"   🎯 CrewAI 전문가별 선택적 접근 준비 완료!")

                else:
                    logger.warning(f"⚠️ PDF 딕셔너리 생성 실패, 기존 방식으로 대체...")

                    # 기존 분석 방식으로 폴백
                    analysis_result = (
                        await self.large_pdf_analyzer.extract_raw_text_only(
                            pdf_path=pdf_url,
                            company_name=stock_info.get("stock_name", "분석대상회사"),
                            save_to_json=False,
                        )
                    )

                    if analysis_result.get("success"):
                        pdf_result["analysis_completed"] = True

                        # 기존 구조 유지
                        pdf_content = {
                            "pdf_url": pdf_url,
                            "text_length": len(analysis_result.get("raw_text", "")),
                            "raw_text": analysis_result.get("raw_text", ""),
                            "extraction_method": analysis_result.get(
                                "extraction_method", "large_pdf_analyzer"
                            ),
                            "analysis_timestamp": analysis_result.get(
                                "analysis_timestamp"
                            ),
                            "chunking_applied": analysis_result.get(
                                "chunking_applied", False
                            ),
                            "total_chunks": analysis_result.get("total_chunks", 0),
                            "chunk_types": analysis_result.get("chunk_types", []),
                            "toc_based_chunks": analysis_result.get(
                                "toc_based_chunks", {}
                            ),
                            "keyword_based_chunks": analysis_result.get(
                                "keyword_based_chunks", {}
                            ),
                            "ai_detected_structure": analysis_result.get(
                                "ai_detected_structure", {}
                            ),
                            "chunking_metadata": analysis_result.get(
                                "chunking_metadata", {}
                            ),
                        }

                        pdf_result["pdf_content"] = pdf_content
                        pdf_result["analysis_method"] = "large_pdf_analyzer_fallback"
                    else:
                        logger.warning(
                            f"⚠️ 기존 PDF 분석도 실패: {analysis_result.get('error')}"
                        )

        except Exception as e:
            logger.error(f"PDF 감지/분석 중 오류: {e}")
            pdf_result["error"] = str(e)

        return pdf_result

    def save_enhanced_results(self, results: Dict[str, Any], stock_info: Dict) -> str:
        """분석 결과를 JSON 파일로 저장합니다 - PDF 딕셔너리와 CrewAI 상세 내용 포함."""
        try:
            # 파일명 생성 - ticker_bbg 방식 사용
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # ticker_bbg를 우선적으로 사용, 없으면 stock_code 사용
            ticker_bbg = stock_info.get("ticker_bbg", "")
            stock_code = stock_info.get("stock_code", "unknown")

            # 분석 타입 결정 (기본값: enhanced)
            analysis_type = "enhanced"

            # 사용자 의도에 따라 분석 타입 결정
            user_prompt = results.get("user_prompt", "").lower()
            if "재무" in user_prompt or "financial" in user_prompt:
                analysis_type = "financial"
            elif "일반" in user_prompt or "general" in user_prompt:
                analysis_type = "general"

            # ticker_bbg가 있으면 사용, 없으면 stock_code 사용
            if ticker_bbg and ticker_bbg != "":
                # ticker_bbg에서 파일명에 사용할 수 없는 문자 제거
                safe_ticker = re.sub(r'[<>:"/\\|?*\s]', "_", ticker_bbg)
                filename = f"json-agent-{safe_ticker}-{analysis_type}-at{datetime.now().strftime('%Y%m%d')}-save{timestamp}.json"
            else:
                # 기존 방식 (fallback)
                stock_name = stock_info.get("stock_name", "unknown")
                safe_stock_name = re.sub(r'[<>:"/\\|?*]', "", stock_name)
                filename = f"json-agent-{stock_code}_{safe_stock_name}-{analysis_type}-at{datetime.now().strftime('%Y%m%d')}-save{timestamp}.json"

            # results 디렉토리 확인 및 생성
            results_dir = "results"
            if not os.path.exists(results_dir):
                os.makedirs(results_dir)

            filepath = os.path.join(results_dir, filename)

            # 🚀 PDF 딕셔너리 내용을 별도 섹션으로 추가
            enhanced_results = results.copy()

            # PDF 분석 결과에서 상세 내용 추출
            pdf_analysis = results.get("steps", {}).get("pdf_large_analysis", {})
            if pdf_analysis.get("pdf_detected") and pdf_analysis.get(
                "analysis_completed"
            ):
                pdf_content = pdf_analysis.get("pdf_content", {})

                # PDF 딕셔너리 구조 추가
                enhanced_results["pdf_detailed_content"] = {
                    "pdf_url": pdf_content.get("pdf_url"),
                    "total_text_length": pdf_content.get("text_length", 0),
                    "chunking_applied": pdf_content.get("chunking_applied", False),
                    "total_chunks": pdf_content.get("total_chunks", 0),
                    "chunk_types": pdf_content.get("chunk_types", []),
                    "toc_based_chunks": pdf_content.get(
                        "toc_based_chunks", {}
                    ),  # 🎯 목차별 딕셔너리
                    "keyword_based_chunks": pdf_content.get("keyword_based_chunks", {}),
                    "raw_text_sample": (
                        pdf_content.get("raw_text", "")[:1000] + "..."
                        if pdf_content.get("raw_text")
                        else ""
                    ),
                    "extraction_method": pdf_content.get(
                        "extraction_method", "unknown"
                    ),
                    "analysis_timestamp": pdf_content.get("analysis_timestamp"),
                }

                logger.info(
                    f"📄 PDF 상세 내용 JSON에 추가됨: {len(pdf_content.get('toc_based_chunks', {}))}개 목차 청크"
                )

            # 🎯 CrewAI 분석 결과 상세 내용 추가
            crewai_analysis = results.get("steps", {}).get(
                "step4_crewai_comprehensive_analysis", {}
            )
            if crewai_analysis.get("success"):
                expert_insights = crewai_analysis.get("expert_insights", {})

                enhanced_results["crewai_detailed_analysis"] = {
                    "detected_sector": crewai_analysis.get("detected_sector"),
                    "sector_korean_name": crewai_analysis.get("sector_korean_name"),
                    "activated_experts": crewai_analysis.get("activated_experts", []),
                    "expert_count": len(crewai_analysis.get("activated_experts", [])),
                    "individual_expert_analyses": expert_insights.get(
                        "individual_expert_analyses", []
                    ),
                    "synthesis_result": expert_insights.get("synthesis_result", {}),
                    "data_integration_quality": crewai_analysis.get(
                        "data_integration_quality"
                    ),
                    "cost_savings": crewai_analysis.get("cost_savings", {}),
                    "token_optimization": crewai_analysis.get("token_optimization", {}),
                    "analysis_depth": crewai_analysis.get("analysis_depth"),
                    "total_analysis_time": expert_insights.get("total_analysis_time"),
                    "data_sources_integrated": self._extract_integrated_data_sources(
                        results
                    ),  # 🔗 데이터 연결고리
                }

                logger.info(
                    f"🎯 CrewAI 상세 분석 JSON에 추가됨: {len(expert_insights.get('individual_expert_analyses', []))}명 전문가 의견"
                )

            # 🔗 데이터 흐름 추적 정보 추가
            enhanced_results["data_flow_tracking"] = {
                "step1_stock_detection": {
                    "method": results.get("steps", {})
                    .get("step1_stock_detection", {})
                    .get("detection_method"),
                    "confidence": (
                        "high"
                        if results.get("steps", {})
                        .get("step1_stock_detection", {})
                        .get("detected")
                        else "low"
                    ),
                },
                "step2_financial_data": {
                    "sources": results.get("steps", {})
                    .get("step2_financial_data", {})
                    .get("data_sources", []),
                    "quality": results.get("steps", {})
                    .get("step2_financial_data", {})
                    .get("data_quality"),
                },
                "step3_manus_collection": {
                    "richness_score": results.get("steps", {})
                    .get("step3_information_collection", {})
                    .get("data_richness_score", 0),
                    "pdf_detected": results.get("steps", {})
                    .get("step3_information_collection", {})
                    .get("pdf_analysis", {})
                    .get("pdf_detected", False),
                    "ready_for_crewai": results.get("steps", {})
                    .get("step3_information_collection", {})
                    .get("ready_for_crewai", False),
                },
                "step4_crewai_synthesis": {
                    "success": crewai_analysis.get("success", False),
                    "experts_activated": len(
                        crewai_analysis.get("activated_experts", [])
                    ),
                    "data_integration_success": crewai_analysis.get(
                        "expert_insights", {}
                    )
                    .get("synthesis_result", {})
                    .get("synthesis_success", False),
                },
                "overall_data_completeness": self._calculate_data_completeness(results),
            }

            # JSON 저장
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(enhanced_results, f, ensure_ascii=False, indent=2)

            logger.info(f"💾 개선된 결과 저장 완료: {filepath}")
            logger.info(
                f"📊 추가된 섹션: pdf_detailed_content, crewai_detailed_analysis, data_flow_tracking"
            )
            return filepath

        except Exception as e:
            logger.error(f"❌ 결과 저장 실패: {e}")
            return f"저장 실패: {e}"

    def _extract_integrated_data_sources(self, results: Dict) -> Dict[str, Any]:
        """통합된 데이터 소스 정보를 추출합니다."""
        integrated_sources = {
            "financial_data_sources": [],
            "manus_web_search_performed": False,
            "pdf_analysis_performed": False,
            "enhanced_dart_used": False,
            "crewai_synthesis_performed": False,
        }

        # 재무데이터 소스
        financial_data = results.get("steps", {}).get("step2_financial_data", {})
        if financial_data.get("success"):
            integrated_sources["financial_data_sources"] = financial_data.get(
                "data_sources", []
            )

        # Enhanced DART 사용 여부
        enhanced_dart = results.get("steps", {}).get("step2_enhanced_dart_data", {})
        if enhanced_dart and enhanced_dart.get("success"):
            integrated_sources["enhanced_dart_used"] = True

        # Manus 웹검색 수행 여부
        manus_collection = results.get("steps", {}).get(
            "step3_information_collection", {}
        )
        if manus_collection.get("performed"):
            integrated_sources["manus_web_search_performed"] = True

        # PDF 분석 수행 여부
        pdf_analysis = results.get("steps", {}).get("pdf_large_analysis", {})
        if pdf_analysis.get("pdf_detected") and pdf_analysis.get("analysis_completed"):
            integrated_sources["pdf_analysis_performed"] = True

        # CrewAI 종합 분석 수행 여부
        crewai_analysis = results.get("steps", {}).get(
            "step4_crewai_comprehensive_analysis", {}
        )
        if crewai_analysis.get("success"):
            integrated_sources["crewai_synthesis_performed"] = True

        return integrated_sources

    def _calculate_data_completeness(self, results: Dict) -> float:
        """전체 데이터 완성도를 계산합니다 (0-100%)."""
        completeness_score = 0.0

        # 종목 감지 (20점)
        if results.get("steps", {}).get("step1_stock_detection", {}).get("detected"):
            completeness_score += 20

        # 재무데이터 (20점)
        if results.get("steps", {}).get("step2_financial_data", {}).get("success"):
            completeness_score += 20

        # 정보 수집 (20점)
        manus_collection = results.get("steps", {}).get(
            "step3_information_collection", {}
        )
        if manus_collection.get("performed"):
            richness = manus_collection.get("data_richness_score", 0)
            completeness_score += (richness / 100) * 20

        # PDF 분석 (20점)
        pdf_analysis = results.get("steps", {}).get("pdf_large_analysis", {})
        if pdf_analysis.get("pdf_detected"):
            if pdf_analysis.get("analysis_completed"):
                completeness_score += 20
            else:
                completeness_score += 10  # 감지는 됐지만 분석 실패

        # CrewAI 종합 분석 (20점)
        crewai_analysis = results.get("steps", {}).get(
            "step4_crewai_comprehensive_analysis", {}
        )
        if crewai_analysis.get("success"):
            completeness_score += 20

        return min(completeness_score, 100.0)


async def main():
    """
    🚀 Enhanced 주식 분석 시스템 메인 함수

    사용자 입력을 받아서 종합적인 주식 분석을 수행합니다.
    """
    print("🚀 Enhanced 주식 분석 시스템 시작!")
    print("=" * 50)

    try:
        # 시스템 초기화
        system = EnhancedStockAnalysisSystem()

        # 사용자 입력 받기
        print("\n💬 분석하고 싶은 종목이나 질문을 입력해주세요:")
        print("예시: '삼성전자 투자 의견 알려줘', '005930 재무분석', 'AAPL 주가 전망'")
        print("-" * 50)

        user_input = input("질문: ").strip()

        if not user_input:
            print("❌ 질문을 입력해주세요.")
            return

        print(f"\n🔍 분석 시작: {user_input}")
        print("=" * 50)

        # 분석 실행
        results = await system.run_enhanced_analysis(user_input)

        # 결과 출력
        print("\n✅ 분석 완료!")
        print("=" * 50)

        if results.get("success"):
            # 기본 정보 출력
            stock_info = results["steps"].get("step1_stock_detection", {})
            if stock_info.get("detected"):
                print(
                    f"📊 분석 종목: {stock_info.get('stock_name')} ({stock_info.get('stock_code')})"
                )
                print(f"🏢 GICS 섹터: {stock_info.get('gics_sector', '알 수 없음')}")

            # 데이터 수집 상태
            financial_data = results["steps"].get("step2_financial_data", {})
            if financial_data.get("success"):
                print(
                    f"💹 재무데이터: ✅ 수집 완료 ({', '.join(financial_data.get('data_sources', []))})"
                )

            # 정보 수집 상태
            manus_collection = results["steps"].get("step3_information_collection", {})
            if manus_collection.get("performed"):
                richness_score = manus_collection.get("data_richness_score", 0)
                print(f"🔍 정보 수집: ✅ 완료 (풍부함: {richness_score:.1f}/100)")

            # CrewAI 분석 상태
            crewai_analysis = results["steps"].get(
                "step4_crewai_comprehensive_analysis", {}
            )
            if crewai_analysis and not crewai_analysis.get("error"):
                print("🎯 CrewAI 종합 분석: ✅ 완료")

            # 저장된 파일
            saved_file = results.get("saved_file")
            if saved_file and not saved_file.startswith("저장 실패"):
                print(f"💾 결과 파일: {saved_file}")

            print("\n📋 분석 요약:")
            final_summary = results.get("final_summary", {})
            if final_summary:
                analyzed_stock = final_summary.get("analyzed_stock", {})
                print(
                    f"  종목: {analyzed_stock.get('name')} ({analyzed_stock.get('code')})"
                )
                print(f"  섹터: {analyzed_stock.get('gics_sector', '알 수 없음')}")

                key_insights = final_summary.get("key_insights", {})
                print(
                    f"  분석 품질: {key_insights.get('overall_analysis_depth', '알 수 없음')}"
                )
        else:
            print(f"❌ 분석 실패: {results.get('error', '알 수 없는 오류')}")

    except KeyboardInterrupt:
        print("\n\n👋 분석이 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        logger.error(f"메인 함수 오류: {e}")


if __name__ == "__main__":
    """
    스크립트가 직접 실행될 때 main 함수를 실행합니다.
    """
    print("🔥 Enhanced Stock Analysis System v2.0")
    print("🚀 AI 기반 종합 주식 분석 시스템")
    print("💡 ManusAgent + CrewAI + Enhanced DART API")
    print()

    # 비동기 함수 실행
    asyncio.run(main())
