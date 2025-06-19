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

            # 🚀 의도별 맞춤형 분석 지시사항 (핵심 개선 포인트!)
            custom_instructions = self._generate_custom_analysis_instructions(
                primary_intent, analysis_focus, data_priority, user_prompt
            )

            analysis_prompt += f"""

{custom_instructions}
"""

            logger.info(f"🎯 맞춤형 지시사항 생성 완료 - 의도: {primary_intent}")

            # Manus 에이전트 실행
            self.manus_agent.memory.clear()
            self.manus_agent.update_memory("user", analysis_prompt)

            analysis_response = ""
            run_result = await self.manus_agent.run()

            if hasattr(run_result, "__aiter__"):
                async for response in run_result:
                    analysis_response += response + "\n"
            else:
                analysis_response = str(run_result)

            # 📄 새로 추가: AI 응답에서 PDF 감지 및 자동 분석
            pdf_analysis_result = await self._detect_and_analyze_pdf_from_response(
                analysis_response, stock_info
            )

            return {
                "performed": True,
                "method": f"intent_based_analysis_{primary_intent}",
                "response": analysis_response.strip(),
                "primary_intent": primary_intent,
                "analysis_focus": analysis_focus,
                "data_priority": data_priority,
                "confidence": confidence,
                "basic_financial_data_used": basic_financial_included,
                "enhanced_dart_data_used": enhanced_dart_included,
                # 분류 기능 제거됨 - "classification_included": classification_result.get("performed", False),
                "customization_level": (
                    "높음"
                    if confidence > 0.7
                    else "보통" if confidence > 0.4 else "낮음"
                ),
                # 📄 PDF 분석 결과 추가
                "pdf_analysis": pdf_analysis_result,
            }

        except Exception as e:
            logger.error(f"의도 맞춤형 분석 중 오류: {e}")
            return {
                "performed": False,
                "error": str(e),
                "primary_intent": intent_analysis.get("primary_intent", "오류"),
            }

    async def _detect_and_analyze_pdf_from_response(
        self, ai_response: str, stock_info: Dict
    ) -> Dict[str, Any]:
        """
        🔍 AI 응답에서 PDF 파일 감지 및 자동 분석

        AI 에이전트가 웹 검색 중에 PDF 파일을 발견하면 자동으로
        LargePDFAnalyzer를 사용해서 상세 분석을 수행합니다.

        Args:
            ai_response: Manus 에이전트의 응답 텍스트
            stock_info: 종목 정보

        Returns:
            Dict: PDF 분석 결과
        """
        try:
            logger.info("🔍 AI 응답에서 PDF 파일 감지 시도...")

            # PDF 파일 패턴 감지 (다양한 형태)
            pdf_patterns = [
                r'https?://[^\s<>"]+\.pdf',  # HTTP/HTTPS PDF URL
                r'file:///[^\s<>"]+\.pdf',  # 로컬 파일 PDF
                r'PDF.*파일.*경로[:\s]*([^\s<>"]+\.pdf)',  # "PDF 파일 경로: ..." 형태
                r'다운로드.*PDF[:\s]*([^\s<>"]+\.pdf)',  # "다운로드된 PDF: ..." 형태
                r'보고서.*PDF[:\s]*([^\s<>"]+\.pdf)',  # "보고서 PDF: ..." 형태
            ]

            detected_pdfs = []
            for pattern in pdf_patterns:
                matches = re.findall(pattern, ai_response, re.IGNORECASE)
                detected_pdfs.extend(matches)

            if not detected_pdfs:
                return {
                    "pdf_detected": False,
                    "reason": "AI 응답에서 PDF 파일 감지되지 않음",
                }

            # 첫 번째 PDF만 분석 (여러 개 발견시)
            pdf_path = detected_pdfs[0]
            logger.info(f"📄 PDF 파일 감지됨: {pdf_path}")

            # PDF 파일 존재 여부 확인 (로컬 파일인 경우)
            if pdf_path.startswith("file://") or not pdf_path.startswith("http"):
                # 로컬 파일 경로 정리
                clean_path = pdf_path.replace("file:///", "").replace("file://", "")
                if not os.path.exists(clean_path):
                    logger.warning(f"⚠️ PDF 파일을 찾을 수 없음: {clean_path}")
                    return {
                        "pdf_detected": True,
                        "pdf_path": pdf_path,
                        "analysis_completed": False,
                        "error": f"PDF 파일을 찾을 수 없음: {clean_path}",
                    }
                pdf_path = clean_path

            # 🚀 LargePDFAnalyzer로 자동 분석 수행
            logger.info("🚀 대용량 PDF 분석기로 자동 분석 시작...")

            company_name = stock_info.get("stock_name", "분석대상회사")

            # 📄 사용자 선택: 원문 추출 vs AI 분석
            # 현재: 원문 추출 모드 (빠름, 요약 없음)
            company_name = stock_info.get("stock_name", "분석대상회사")

            # PDF 분석 수행 (원문 추출 모드, 별도 파일 저장하지 않음)
            pdf_result = await self.large_pdf_analyzer.extract_raw_text_only(
                pdf_path=pdf_path,
                company_name=company_name,
                save_to_json=False,  # 🔧 별도 저장 비활성화
            )

            if pdf_result.get("metadata", {}).get("success", False):
                logger.info("✅ PDF 분석 완료!")

                # 📄 PDF 분석 결과를 분석 응답에 포함 (chunking 정보 추가)
                raw_text = pdf_result.get("raw_content", {}).get("full_text", "")

                # 🔖 PDF를 목차 기반으로 chunking (목차 우선, 키워드 폴백)
                contextual_chunks = []
                if raw_text and len(raw_text) > 1000:
                    try:
                        # 목차 기반 청킹 우선 시도 (PDF 경로 전달)
                        contextual_chunks = await self._create_pdf_chunks_for_crewai(
                            raw_text, pdf_path
                        )
                        logger.info(
                            f"📄 PDF Chunking 완료: {len(contextual_chunks)}개 청크 생성"
                        )

                        # 목차 기반 청킹 성공 여부 로그
                        toc_chunks = [
                            c
                            for c in contextual_chunks
                            if c.get("source") == "table_of_contents"
                        ]
                        if toc_chunks:
                            logger.info(f"🔖 목차 기반 청크: {len(toc_chunks)}개")
                        else:
                            logger.info("📝 키워드 기반 청킹 사용됨 (목차 없음)")

                    except Exception as e:
                        logger.warning(f"⚠️ PDF Chunking 실패: {e} - 원본 텍스트 유지")

                return {
                    "pdf_detected": True,
                    "pdf_path": pdf_path,
                    "analysis_completed": True,
                    "pdf_content": {  # 🚀 PDF 내용을 직접 포함 (chunking 정보 추가)
                        "raw_text": raw_text,
                        "contextual_chunks": contextual_chunks,  # 🚀 Context별 청크 정보 추가
                        "chunking_applied": len(contextual_chunks) > 0,
                        "total_chunks": len(contextual_chunks),
                        "chunk_types": (
                            list(
                                set(
                                    chunk["context_type"] for chunk in contextual_chunks
                                )
                            )
                            if contextual_chunks
                            else []
                        ),
                        "text_length": pdf_result.get("metadata", {}).get(
                            "total_text_length", 0
                        ),
                        "pages_info": pdf_result.get("metadata", {}).get(
                            "pages_processed", []
                        ),
                        "processing_time": pdf_result.get("metadata", {}).get(
                            "total_processing_time", "정보없음"
                        ),
                        "extraction_method": pdf_result.get("metadata", {}).get(
                            "extraction_method_detail", ""
                        ),
                        "pdf_url": pdf_path,
                    },
                    "analysis_result": {
                        "company_name": company_name,
                        "text_length": pdf_result.get("metadata", {}).get(
                            "total_text_length", 0
                        ),
                        "processing_time": pdf_result.get("metadata", {}).get(
                            "total_processing_time", "정보없음"
                        ),
                        "content_preview": pdf_result.get("content_preview", ""),
                        "chunking_info": {
                            "total_chunks": len(contextual_chunks),
                            "chunk_types": (
                                list(
                                    set(
                                        chunk["context_type"]
                                        for chunk in contextual_chunks
                                    )
                                )
                                if contextual_chunks
                                else []
                            ),
                            "chunking_success": len(contextual_chunks) > 0,
                        },
                    },
                }

            else:
                error_msg = pdf_result.get("metadata", {}).get(
                    "error", "알 수 없는 오류"
                )
                logger.error(f"❌ PDF 분석 실패: {error_msg}")
                return {
                    "pdf_detected": True,
                    "pdf_path": pdf_path,
                    "analysis_completed": False,
                    "error": error_msg,
                }

        except Exception as e:
            logger.error(f"❌ PDF 감지 및 분석 중 오류: {e}")
            return {"pdf_detected": False, "error": f"PDF 처리 중 오류: {str(e)}"}

    def _generate_custom_analysis_instructions(
        self,
        primary_intent: str,
        analysis_focus: str,
        data_priority: str,
        user_prompt: str,
    ) -> str:
        """
        🎯 의도별 맞춤형 분석 지시사항 생성 (핵심 차별화 기능!)

        사용자의 질문 의도에 따라 완전히 다른 분석 지시사항을 만들어요.
        이제 획일적인 5단계 분석이 아니라 진짜 원하는 답변을 받을 수 있어요!
        """

        # 🎯 의도별 맞춤형 지시사항
        custom_instructions = {
            "주가문의": f"""
🎯 **주가 문의 전용 분석**:
사용자가 "{user_prompt}"라고 질문했습니다. 주가와 가격 동향에 집중해서 답변해주세요.

**분석 포커스**:
1. **현재 주가 수준 평가** - 고평가/적정/저평가 판단
2. **최근 주가 동향 분석** - 상승/하락 요인과 흐름
3. **주가 전망** - 단기/중기 목표가와 방향성
4. **매수/매도 타이밍** - 현재 시점의 투자 의견

**재무데이터 활용법**: 주가 정당성 평가를 위한 밸류에이션 중심
**답변 스타일**: 구체적 수치와 명확한 투자 의견 제시
""",
            "재무분석": f"""
🎯 **재무분석 전용 분석**:
사용자가 "{user_prompt}"라고 질문했습니다. 재무제표와 재무지표 분석에 집중해주세요.

**분석 포커스**:
1. **수익성 분석** - 매출, 영업이익, 순이익 증감과 마진율
2. **안정성 분석** - 부채비율, 유동비율, 이자보상배수
3. **성장성 분석** - 매출/이익 성장률, 확장 계획
4. **효율성 분석** - ROE, ROA, 총자산회전율

**재무데이터 활용법**: 모든 재무지표를 상세히 분석하고 동종업계 비교
**답변 스타일**: 구체적 재무비율과 수치 기반 전문적 분석
""",
            "투자조언": f"""
🎯 **투자조언 전용 분석**:
사용자가 "{user_prompt}"라고 질문했습니다. 명확한 투자 의견과 전략을 제시해주세요.

**분석 포커스**:
1. **투자 추천 등급** - 매수/보유/매도 명확한 의견
2. **목표가 제시** - 구체적 목표 주가와 달성 기간
3. **투자 리스크** - 주요 위험 요인과 대응 방안
4. **포트폴리오 비중** - 적정 투자 비중과 분산 전략

**재무데이터 활용법**: 투자 의사결정을 위한 핵심 지표 중심
**답변 스타일**: 실행 가능한 구체적 투자 가이드라인 제공
""",
            "종목분류": f"""
🎯 **종목분류 전용 분석**:
사용자가 "{user_prompt}"라고 질문했습니다. 정확한 종목 분류와 특성 분석에 집중해주세요.

**분석 포커스**:
1. **주요 분류** - 우량주/성장주/가치주/배당주 등 명확한 분류
2. **분류 근거** - 재무지표 기반 객관적 분류 기준
3. **투자 특성** - 해당 분류의 투자 특징과 장단점
4. **비교 분석** - 동일 분류 내 다른 종목과의 비교

**재무데이터 활용법**: 분류 기준에 맞는 핵심 지표 집중 분석
**답변 스타일**: 명확한 분류 결과와 근거 중심
""",
            "기업정보": f"""
🎯 **기업정보 전용 분석**:
사용자가 "{user_prompt}"라고 질문했습니다. 회사 소개와 사업 내용에 집중해주세요.

**분석 포커스**:
1. **사업 개요** - 주력 사업과 수익 구조
2. **시장 지위** - 업계 내 위치와 경쟁력
3. **성장 동력** - 미래 성장 사업과 전략
4. **기업 특징** - 독특한 강점과 차별화 요소

**재무데이터 활용법**: 사업 성과를 보여주는 참고 자료로 활용
**답변 스타일**: 이해하기 쉬운 회사 소개와 사업 설명
""",
            "배당정보": f"""
🎯 **배당정보 전용 분석**:
사용자가 "{user_prompt}"라고 질문했습니다. 배당 관련 모든 정보에 집중해주세요.

**분석 포커스**:
1. **배당 현황** - 현재 배당금, 배당률, 배당수익률
2. **배당 이력** - 과거 배당 패턴과 증감 추이
3. **배당 정책** - 회사의 배당 철학과 향후 계획
4. **배당 매력도** - 배당 투자 관점에서의 평가

**재무데이터 활용법**: 배당 지급 능력과 지속가능성 평가
**답변 스타일**: 배당 투자자를 위한 실용적 정보 제공
""",
        }

        # 해당 의도의 맞춤형 지시사항 반환 (없으면 일반 분석)
        if primary_intent in custom_instructions:
            return custom_instructions[primary_intent]
        else:
            # 일반 문의의 경우 기본적이지만 사용자 질문에 집중하는 지시사항
            return f"""
🎯 **맞춤형 일반 분석**:
사용자가 "{user_prompt}"라고 질문했습니다. 이 질문에 정확히 답변하는 것에 집중해주세요.

**분석 포커스**: 사용자 질문의 핵심 의도 파악하여 맞춤형 답변
**재무데이터 활용법**: 질문 답변에 필요한 정보만 선별적으로 활용
**답변 스타일**: 질문에 직접적이고 구체적으로 답변

❗ 중요: 획일적인 분석보다는 사용자의 구체적 질문에 정확히 답변해주세요.
"""

    def _create_dart_summary(self, enhanced_dart_data: Dict) -> str:
        """Enhanced DART 데이터 요약 생성"""
        if not enhanced_dart_data or not enhanced_dart_data.get("success"):
            return ""

        summary_parts = ["📊 추가 DART 상세 정보:"]

        # 재무분석 정보
        if "financial_analysis" in enhanced_dart_data:
            financial = enhanced_dart_data["financial_analysis"]
            if financial.get("success"):
                summary_parts.append("• 상세 재무제표 데이터 포함")

        # 지배구조 정보
        if "governance_analysis" in enhanced_dart_data:
            governance = enhanced_dart_data["governance_analysis"]
            if governance.get("success") and "major_shareholders" in governance:
                shareholders = governance["major_shareholders"][:3]  # 상위 3명만
                summary_parts.append("• 주요 주주 정보:")
                for shareholder in shareholders:
                    name = shareholder.get("shareholder_name", "")
                    ratio = shareholder.get("ownership_ratio", 0)
                    if name and ratio:
                        summary_parts.append(f"  - {name}: {ratio}%")

        # 투자정보
        if "investment_analysis" in enhanced_dart_data:
            investment = enhanced_dart_data["investment_analysis"]
            if investment.get("success") and "dividend_info" in investment:
                summary_parts.append("• 배당 정보 포함")

        # 공시정보
        if "disclosure_monitoring" in enhanced_dart_data:
            disclosure = enhanced_dart_data["disclosure_monitoring"]
            if disclosure.get("success") and "recent_disclosures" in disclosure:
                recent_count = len(disclosure["recent_disclosures"])
                summary_parts.append(f"• 최근 공시: {recent_count}건")

        return "\n".join(summary_parts) if len(summary_parts) > 1 else ""

    def _create_comprehensive_dart_analysis(self, enhanced_dart_data: Dict) -> str:
        """Enhanced DART 데이터의 포괄적 분석 생성"""
        if not enhanced_dart_data or not enhanced_dart_data.get("success"):
            return ""

        analysis_parts = ["📊 **Enhanced DART 종합 분석**:"]

        # 1. 재무분석 상세 정보
        if "financial_analysis" in enhanced_dart_data:
            financial = enhanced_dart_data["financial_analysis"]
            if financial.get("success"):
                analysis_parts.append("\n🏦 **상세 재무분석**:")

                # 개별재무제표 정보
                if "individual_statements" in financial:
                    individual = financial["individual_statements"]
                    if individual.get("assets"):
                        total_assets = individual["assets"].get("total_assets", 0)
                        analysis_parts.append(f"• 개별 총자산: {total_assets:,}원")
                    if individual.get("liabilities"):
                        total_debt = individual["liabilities"].get(
                            "total_liabilities", 0
                        )
                        analysis_parts.append(f"• 개별 총부채: {total_debt:,}원")
                    if individual.get("equity"):
                        total_equity = individual["equity"].get("total_equity", 0)
                        analysis_parts.append(f"• 개별 총자본: {total_equity:,}원")

                # 연결재무제표 정보
                if "consolidated_statements" in financial:
                    consolidated = financial["consolidated_statements"]
                    if consolidated.get("assets"):
                        total_assets = consolidated["assets"].get("total_assets", 0)
                        analysis_parts.append(f"• 연결 총자산: {total_assets:,}원")
                    if consolidated.get("equity"):
                        total_equity = consolidated["equity"].get("total_equity", 0)
                        analysis_parts.append(f"• 연결 총자본: {total_equity:,}원")

                # 분기별 실적
                if "quarterly_performance" in financial:
                    quarterly = financial["quarterly_performance"]
                    if quarterly:
                        analysis_parts.append(
                            f"• 분기별 실적 데이터: {len(quarterly)}분기"
                        )

        # 2. 지배구조 상세 정보
        if "governance_analysis" in enhanced_dart_data:
            governance = enhanced_dart_data["governance_analysis"]
            if governance.get("success"):
                analysis_parts.append("\n🏢 **기업지배구조 분석**:")

                # 주요 주주 정보
                if "major_shareholders" in governance:
                    shareholders = governance["major_shareholders"][:3]  # 상위 3명
                    analysis_parts.append("• 주요 주주:")
                    for i, shareholder in enumerate(shareholders, 1):
                        name = shareholder.get("shareholder_name", "")
                        ratio = shareholder.get("ownership_ratio", 0)
                        if name and ratio:
                            analysis_parts.append(f"  {i}. {name}: {ratio}%")

                # 임원 정보
                if "executives" in governance:
                    executives = governance["executives"]
                    if executives:
                        analysis_parts.append(f"• 등록임원 수: {len(executives)}명")

                # 이사 보수
                if "director_compensation" in governance:
                    compensation = governance["director_compensation"]
                    if compensation:
                        total_compensation = sum(
                            comp.get("total_compensation", 0) for comp in compensation
                        )
                        analysis_parts.append(
                            f"• 이사 총 보수: {total_compensation:,}원"
                        )

                # 사외이사
                if "outside_directors" in governance:
                    outside = governance["outside_directors"]
                    if outside:
                        analysis_parts.append(f"• 사외이사 수: {len(outside)}명")

        # 3. 투자정보 상세 분석
        if "investment_analysis" in enhanced_dart_data:
            investment = enhanced_dart_data["investment_analysis"]
            if investment.get("success"):
                analysis_parts.append("\n💰 **투자정보 분석**:")

                # 배당 정보
                if "dividend_info" in investment:
                    dividend = investment["dividend_info"]
                    if dividend:
                        latest_dividend = dividend[0] if dividend else {}
                        dividend_rate = latest_dividend.get("dividend_rate", 0)
                        dividend_amount = latest_dividend.get("dividend_amount", 0)
                        if dividend_rate or dividend_amount:
                            analysis_parts.append(f"• 최근 배당률: {dividend_rate}%")
                            analysis_parts.append(f"• 최근 배당금: {dividend_amount}원")

                # 증자감자 정보
                if "capital_changes" in investment:
                    capital = investment["capital_changes"]
                    if capital:
                        analysis_parts.append(f"• 자본변동 이력: {len(capital)}건")

                # 자기주식 정보
                if "treasury_stock" in investment:
                    treasury = investment["treasury_stock"]
                    if treasury:
                        latest_treasury = treasury[0] if treasury else {}
                        stock_count = latest_treasury.get("stock_count", 0)
                        if stock_count:
                            analysis_parts.append(f"• 자기주식 보유: {stock_count:,}주")

                # 타법인 출자
                if "investments" in investment:
                    investments = investment["investments"]
                    if investments:
                        analysis_parts.append(f"• 타법인 출자: {len(investments)}건")

        # 4. 공시 모니터링 정보
        if "disclosure_monitoring" in enhanced_dart_data:
            disclosure = enhanced_dart_data["disclosure_monitoring"]
            if disclosure.get("success"):
                analysis_parts.append("\n📢 **실시간 공시 모니터링**:")

                # 최근 공시
                if "recent_disclosures" in disclosure:
                    recent = disclosure["recent_disclosures"]
                    if recent:
                        analysis_parts.append(f"• 최근 30일 공시: {len(recent)}건")

                        # 최신 3개 공시 표시
                        for i, disc in enumerate(recent[:3], 1):
                            report_name = disc.get("report_name", "")
                            receipt_date = disc.get("receipt_date", "")
                            if report_name:
                                analysis_parts.append(
                                    f"  {i}. {report_name} ({receipt_date})"
                                )

                # 중요 공시
                if "important_notices" in disclosure:
                    important = disclosure["important_notices"]
                    if important:
                        analysis_parts.append(f"• 중요 공시: {len(important)}건")

                # 정정 공시
                if "corrections" in disclosure:
                    corrections = disclosure["corrections"]
                    if corrections:
                        analysis_parts.append(f"• 정정 공시: {len(corrections)}건")

        analysis_parts.append("\n💡 **Enhanced DART 특별 인사이트**:")
        analysis_parts.append(
            "• 위 정보는 일반 재무데이터에서는 얻을 수 없는 DART 전용 상세 정보입니다"
        )
        analysis_parts.append(
            "• 특히 지배구조, 배당정책, 실시간 공시는 투자 의사결정에 중요한 차별화 정보입니다"
        )

        return "\n".join(analysis_parts)

    async def perform_enhanced_analysis(
        self,
        user_prompt: str,
        stock_info: Dict,
        financial_data: Dict,
        classification_result: Dict,
        enhanced_dart_data: Dict = None,
    ) -> Dict[str, Any]:
        """
        재무데이터를 활용한 개선된 상세 분석

        Args:
            user_prompt: 사용자 질문
            stock_info: 감지된 종목 정보
            financial_data: 수집된 재무데이터
            classification_result: 분류 결과

        Returns:
            Dict: 상세 분석 결과
        """
        try:
            logger.info("📊 통합 재무데이터 기반 상세 분석 실행...")

            # 🚀 통합 분석용 프롬프트 구성
            analysis_prompt = f"사용자 질문: {user_prompt}\n\n"

            # 📊 Step 2-1: 기본 재무데이터 (yfinance + 기본 DART)
            basic_financial_included = False
            if financial_data.get("success"):
                financial_summary = self.financial_collector.get_analysis_summary(
                    financial_data
                )
                analysis_prompt += f"""
📊 **기본 재무데이터 (yfinance + 기본 DART)**:
{financial_summary}

"""
                basic_financial_included = True
                logger.info("✅ 기본 재무데이터를 분석에 포함했습니다")

            # 🚀 Step 2-2: Enhanced DART 상세 데이터 (한국 주식 전용)
            enhanced_dart_included = False
            if enhanced_dart_data and enhanced_dart_data.get("success"):
                enhanced_summary = self._create_comprehensive_dart_analysis(
                    enhanced_dart_data
                )
                if enhanced_summary:
                    analysis_prompt += f"""
🚀 **Enhanced DART 상세 분석**:
{enhanced_summary}

"""
                    enhanced_dart_included = True
                    logger.info("✅ Enhanced DART 데이터를 분석에 포함했습니다")

            # 분류 기능 제거됨 - 분류 결과 포함 로직 삭제

            # 🎯 통합 분석 지시사항
            analysis_method = "통합분석"
            if basic_financial_included and enhanced_dart_included:
                analysis_method = "완전통합분석"
                analysis_prompt += """
🎯 **통합 분석 지시사항**:
위의 기본 재무데이터와 Enhanced DART 상세 정보를 모두 종합하여 다음 관점에서 상세 분석해주세요:

1. **재무건전성 분석**:
   - 기본 재무비율과 상세 재무제표 비교 분석
   - 개별 vs 연결재무제표 차이점 분석
   - 분기별 실적 트렌드 분석

2. **기업지배구조 평가**:
   - 주요 주주 구조와 지분 안정성
   - 경영진 역량과 보상체계 적정성
   - 사외이사 독립성과 전문성

3. **투자자 친화 정책**:
   - 배당 정책과 주주환원 의지
   - 자기주식 운용과 자본 효율성
   - 증자감자 등 자본 정책 변화

4. **실시간 리스크 평가**:
   - 최근 공시사항과 주가 영향 요인
   - 중요 공시와 투자 의사결정 포인트
   - 정정공시 등 주의사항

5. **종합 투자 의견**:
   - 모든 데이터를 종합한 투자 추천 등급
   - 목표 주가와 투자 기간 제시
   - 핵심 리스크와 기회 요소 정리

특히 기본 재무데이터로는 알 수 없는 Enhanced DART만의 독특한 인사이트를 강조해주세요.
"""
            elif basic_financial_included:
                analysis_method = "기본재무분석"
                analysis_prompt += """
📊 **기본 재무분석 지시사항**:
기본 재무데이터를 중심으로 상세한 투자 분석을 수행해주세요.
특히 실제 재무데이터가 있다면 이를 중심으로 분석해주세요.
"""
            else:
                analysis_method = "일반분석"
                analysis_prompt += """
📝 **일반 분석 지시사항**:
사용 가능한 정보를 바탕으로 투자 분석을 수행해주세요.
"""

            logger.info(f"🎯 분석 방법: {analysis_method}")
            logger.info(f"📊 기본 재무데이터 포함: {basic_financial_included}")
            logger.info(f"🚀 Enhanced DART 포함: {enhanced_dart_included}")

            # Manus 에이전트 실행
            # reset() 대신 memory.clear() 사용
            self.manus_agent.memory.clear()
            self.manus_agent.update_memory("user", analysis_prompt)

            analysis_response = ""
            # run()을 await으로 호출하고 결과를 직접 사용
            run_result = await self.manus_agent.run()
            # run_result가 제너레이터라면 반복하여 수집
            if hasattr(run_result, "__aiter__"):
                async for response in run_result:
                    analysis_response += response + "\n"
            else:
                # 단일 결과라면 바로 사용
                analysis_response = str(run_result)

            return {
                "performed": True,
                "method": analysis_method,
                "response": analysis_response.strip(),
                "basic_financial_data_used": basic_financial_included,
                "enhanced_dart_data_used": enhanced_dart_included,
                # 분류 기능 제거됨 - "classification_included": classification_result.get("performed", False),
                "analysis_completeness": (
                    "완전통합"
                    if (basic_financial_included and enhanced_dart_included)
                    else (
                        "부분통합"
                        if (basic_financial_included or enhanced_dart_included)
                        else "기본"
                    )
                ),
            }

        except Exception as e:
            logger.error(f"상세 분석 중 오류: {e}")
            return {"performed": False, "error": str(e)}

    def create_comprehensive_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """전체 분석 결과의 종합 요약을 생성해요"""
        stock_info = results["steps"].get("step1_stock_detection", {})
        financial_data = results["steps"].get("step2_financial_data", {})
        # 분류 기능 제거됨 - classification = results["steps"].get("step3_classification", {})
        analysis = results["steps"].get("step3_detailed_analysis", {})

        return {
            "analyzed_stock": {
                "name": stock_info.get("stock_name"),
                "code": stock_info.get("stock_code"),
                "detection_method": stock_info.get("detection_method"),
            },
            "data_sources": {
                "financial_data_collected": financial_data.get("success", False),
                "data_sources": financial_data.get("data_sources", []),
                "data_quality": financial_data.get("data_quality", "없음"),
            },
            "analysis_quality": {
                # 분류 기능 제거됨 - "classification_performed": classification.get("performed", False),
                "detailed_analysis_performed": analysis.get("performed", False),
                "financial_data_enhanced": financial_data.get("success", False),
            },
            "key_insights": self.extract_key_insights({}, analysis),
        }

    def extract_key_insights(
        self, classification: Dict, analysis: Dict
    ) -> Dict[str, Any]:
        """분석 결과에서 핵심 인사이트를 추출해요"""
        insights = {
            "classification": None,
            "investment_outlook": None,
            "risk_factors": None,
            "recommendation": None,
        }

        # 분류 기능 제거됨 - 분류 결과에서 핵심 정보 추출 로직 삭제

        # 분석 결과에서 투자 전망 추출
        if analysis.get("performed"):
            analysis_response = analysis.get("response", "")
            if "긍정적" in analysis_response or "매수" in analysis_response:
                insights["investment_outlook"] = "긍정적"
            elif "부정적" in analysis_response or "매도" in analysis_response:
                insights["investment_outlook"] = "부정적"
            else:
                insights["investment_outlook"] = "중립적"

        return insights

    def save_enhanced_results(
        self, results: Dict[str, Any], stock_info: Dict[str, Any]
    ) -> str:
        """🚀 io_logger를 사용해서 개선된 분석 결과를 일관된 형식으로 저장해요 (원본 데이터 포함)"""
        try:
            # 🏢 이미 Step 1.5에서 매핑된 정보 사용 (GICS 섹터 포함)
            original_stock_code = stock_info.get(
                "original_stock_code"
            ) or stock_info.get("stock_code")
            original_stock_name = stock_info.get(
                "original_stock_name"
            ) or stock_info.get("stock_name")
            ticker_bbg = stock_info.get("ticker_bbg")
            gics_sector = stock_info.get("gics_sector", "Unknown")

            # stock_info 업데이트 (이미 매핑된 정보 활용)
            updated_stock_info = stock_info.copy()

            # 파일명에 사용할 종목 코드를 ticker_bbg로 교체
            if ticker_bbg != (original_stock_code or original_stock_name):
                logger.info(
                    f"📊 파일명 종목코드 변환: {original_stock_code or original_stock_name} -> {ticker_bbg}"
                )
                logger.info(f"🏢 GICS 섹터 정보: {gics_sector}")
                updated_stock_info["stock_code"] = ticker_bbg  # 파일명 생성용으로 교체

            # 사용자 프롬프트와 최종 응답 추출
            user_prompt = results.get("user_prompt", "")

            # 최종 응답 구성 (단계별 결과를 종합)
            final_response = []

            # 종목 감지 결과
            if "step1_stock_detection" in results.get("steps", {}):
                stock_detection = results["steps"]["step1_stock_detection"]
                if stock_detection.get("detected"):
                    final_response.append(
                        f"📊 감지된 종목: {stock_detection.get('stock_name')} ({stock_detection.get('stock_code')})"
                    )
                    final_response.append(f"🏷️ ticker_bbg: {ticker_bbg}")
                    if gics_sector != "Unknown":
                        final_response.append(
                            f"🏢 GICS 섹터: {gics_sector}"
                        )  # 🎯 GICS 섹터 정보 추가

            # 분류 결과
            # 분류 기능 제거됨 - step3_classification 관련 로직 삭제

            # 상세 분석 결과
            if "step3_detailed_analysis" in results.get("steps", {}):
                analysis = results["steps"]["step3_detailed_analysis"]
                if analysis.get("performed"):
                    final_response.append("📈 상세 분석:")
                    final_response.append(analysis.get("response", ""))

            # 종합 요약
            if "final_summary" in results:
                final_response.append("📋 종합 요약:")
                final_response.append(str(results["final_summary"]))

            response_text = "\n\n".join(final_response)

            # 🚀 첨부된 JSON 파일과 동일한 형식의 단계별 정보 구성
            steps_text = []
            steps_text.append("")  # 첫 번째는 빈 문자열

            # 각 단계별 결과를 문자열로 변환 (수정된 워크플로우)
            for step_key, step_data in results.get("steps", {}).items():
                if step_key == "step1_stock_detection" and step_data.get("detected"):
                    steps_text.append(
                        f"📊 감지된 종목: {step_data.get('stock_name')} ({step_data.get('stock_code')})"
                    )
                    if (
                        step_data.get("gics_sector")
                        and step_data.get("gics_sector") != "Unknown"
                    ):
                        steps_text.append(
                            f"🏢 GICS 섹터: {step_data.get('gics_sector')}"
                        )  # 🎯 GICS 섹터 정보 추가
                elif step_key == "step2_financial_data" and step_data.get("success"):
                    steps_text.append(
                        f"📈 재무데이터 수집 성공: {', '.join(step_data.get('data_sources', []))}"
                    )
                elif step_key == "step2_enhanced_dart_data" and step_data.get(
                    "success"
                ):
                    steps_text.append("🚀 Enhanced DART 데이터 수집 성공")
                elif step_key == "step3_information_collection" and step_data.get(
                    "performed"
                ):
                    richness_score = step_data.get("data_richness_score", 0)
                    steps_text.append(
                        f"🤖 Manus Agent 정보 수집 완료 (풍부함: {richness_score:.1f}/100)"
                    )
                elif (
                    step_key == "step4_crewai_comprehensive_analysis"
                    and step_data.get("success")
                ):
                    sector = step_data.get("detected_sector", "알 수 없음")
                    steps_text.append(f"🎯 CrewAI 종합 분석 완료 (섹터: {sector})")

            # 전체 응답 내용을 steps에 중복 추가하지 않음 (response 필드에 이미 있음)
            steps_text.append("")  # 마지막은 빈 문자열

            # 📊 원본 데이터 추가 준비
            raw_data_section = self._prepare_raw_data_for_json(results)

            # 메타데이터 구성 (원본 데이터 포함)
            meta_data = {
                "analysis_flow": results.get("analysis_flow", "enhanced"),
                "success": results.get("success", False),
                "timestamp": results.get("timestamp"),
                "stock_info": updated_stock_info,  # 🏢 ticker_bbg가 포함된 업데이트된 정보 사용
                "data_quality": results.get("steps", {})
                .get("step2_financial_data", {})
                .get("data_quality", "없음"),
                "enhanced_features": {
                    "financial_data_used": results.get("steps", {})
                    .get("step2_financial_data", {})
                    .get("success", False),
                    "enhanced_dart_used": "step2_enhanced_dart_data"
                    in results.get("steps", {}),
                    # 분류 기능 제거됨 - "classification_performed": results.get("steps", {}).get("step3_classification", {}).get("performed", False),
                    "detailed_analysis_performed": results.get("steps", {})
                    .get("step3_detailed_analysis", {})
                    .get("performed", False),
                    "ticker_bbg_mapping_used": True,  # 🏢 ticker_bbg 매핑 사용 표시
                    "gics_sector_detected": gics_sector
                    != "Unknown",  # 🎯 GICS 섹터 감지 성공 여부
                    "dataset_sector_mapping_used": True,  # 🎯 Dataset 기반 섹터 매핑 사용
                },
                # 🚀 원본 데이터 섹션 추가
                "raw_data": raw_data_section,
            }

            # 🚀 io_logger를 사용해서 첨부된 JSON 파일과 동일한 형식으로 저장
            filepath = save_interaction_log(
                prompt=user_prompt,
                response=response_text,
                steps=steps_text,
                meta=meta_data,
            )

            logger.info(f"💾 Enhanced 분석 결과 저장 (원본 데이터 포함): {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"결과 저장 중 오류: {e}")
            return None

    def _prepare_raw_data_for_json(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        JSON 저장을 위한 원본 데이터 준비
        yfinance, DART, PDF, CrewAI에서 가져온 모든 원본 데이터를 정리해요
        """
        raw_data = {
            "data_sources_summary": {
                "yfinance_data_available": False,
                "dart_basic_data_available": False,
                "enhanced_dart_data_available": False,
                "pdf_data_available": False,
                "manus_collection_available": False,  # 🤖 Manus Agent 수집 데이터 추가
                "crewai_comprehensive_analysis_available": False,  # 🚀 CrewAI 종합 분석 수정
            },
            "yfinance_raw_data": {},
            "dart_basic_raw_data": {},
            "enhanced_dart_raw_data": {},
            "pdf_raw_data": {},
            "manus_collection_raw_data": {},  # 🤖 Manus Agent 원본 데이터 섹션 추가
            "crewai_comprehensive_analysis_raw_data": {},  # 🚀 CrewAI 종합 분석 원본 데이터 섹션
        }

        try:
            # 1. 🔍 yfinance 원본 데이터 추출
            financial_data = results.get("steps", {}).get("step2_financial_data", {})
            if financial_data.get("success"):
                raw_data["data_sources_summary"]["yfinance_data_available"] = True

                # yfinance에서 수집한 모든 데이터를 포함
                yfinance_data = {
                    "basic_info": financial_data.get("basic_info", {}),
                    "current_price_info": financial_data.get("current_price_info", {}),
                    "financial_ratios": financial_data.get("financial_ratios", {}),
                    "growth_metrics": financial_data.get("growth_metrics", {}),
                    "price_history": financial_data.get("price_history", {}),
                    "data_quality": financial_data.get("data_quality", "정보없음"),
                    "data_sources": financial_data.get("data_sources", []),
                    "collection_info": {
                        "success": financial_data.get("success", False),
                        "errors": financial_data.get("errors", []),
                        "stock_info": financial_data.get("stock_info", {}),
                    },
                }

                # DART 기본 정보가 포함되어 있다면 분리
                if "dart_info" in financial_data:
                    raw_data["data_sources_summary"]["dart_basic_data_available"] = True
                    raw_data["dart_basic_raw_data"] = financial_data["dart_info"]

                raw_data["yfinance_raw_data"] = yfinance_data
                logger.info("✅ yfinance 원본 데이터 JSON 준비 완료")

            # 2. 🚀 Enhanced DART 원본 데이터 추출
            enhanced_dart_data = results.get("steps", {}).get(
                "step2_enhanced_dart_data", {}
            )
            if enhanced_dart_data.get("success"):
                raw_data["data_sources_summary"]["enhanced_dart_data_available"] = True

                # Enhanced DART에서 수집한 모든 데이터를 포함
                enhanced_dart_raw = {
                    "collection_info": {
                        "success": enhanced_dart_data.get("success", False),
                        "stock_code": enhanced_dart_data.get("stock_code", ""),
                        "collected_at": enhanced_dart_data.get("collected_at", ""),
                        "error": enhanced_dart_data.get("error", ""),
                    },
                    "financial_analysis": enhanced_dart_data.get(
                        "financial_analysis", {}
                    ),
                    "governance_analysis": enhanced_dart_data.get(
                        "governance_analysis", {}
                    ),
                    "investment_analysis": enhanced_dart_data.get(
                        "investment_analysis", {}
                    ),
                    "disclosure_monitoring": enhanced_dart_data.get(
                        "disclosure_monitoring", {}
                    ),
                }

                raw_data["enhanced_dart_raw_data"] = enhanced_dart_raw
                logger.info("✅ Enhanced DART 원본 데이터 JSON 준비 완료")

            # 3. 📄 PDF 원본 데이터 추출
            pdf_analysis = results.get("steps", {}).get("pdf_large_analysis", {})
            if pdf_analysis.get("pdf_detected") and pdf_analysis.get("pdf_content"):
                raw_data["data_sources_summary"]["pdf_data_available"] = True

                # PDF 원본 데이터를 포함
                pdf_raw = {
                    "pdf_metadata": {
                        "pdf_url": pdf_analysis.get("pdf_path", ""),
                        "analysis_completed": pdf_analysis.get(
                            "analysis_completed", False
                        ),
                        "text_length": pdf_analysis.get("pdf_content", {}).get(
                            "text_length", 0
                        ),
                        "processing_time": pdf_analysis.get("pdf_content", {}).get(
                            "processing_time", ""
                        ),
                        "extraction_method": pdf_analysis.get("pdf_content", {}).get(
                            "extraction_method", ""
                        ),
                        "total_pages": len(
                            pdf_analysis.get("pdf_content", {}).get("pages_info", [])
                        ),
                    },
                    "pdf_full_text": pdf_analysis.get("pdf_content", {}).get(
                        "raw_text", ""
                    ),
                    "pages_breakdown": pdf_analysis.get("pdf_content", {}).get(
                        "pages_info", []
                    ),
                    "extraction_info": {
                        "source_type": "company_report",
                        "language": "auto_detected",
                        "note": "PDF 내용이 기존 JSON 파일에 통합되어 별도 파일 저장하지 않음",
                    },
                }

                raw_data["pdf_raw_data"] = pdf_raw
                logger.info(
                    "✅ PDF 원본 데이터 JSON 준비 완료 - 별도 파일 저장 없이 통합"
                )

            # 4. 🤖 Manus Agent 정보 수집 원본 데이터 추출 (새로 추가!)
            manus_collection = results.get("steps", {}).get(
                "step3_information_collection", {}
            )
            if manus_collection and manus_collection.get("performed"):
                raw_data["data_sources_summary"]["manus_collection_available"] = True

                # Manus Agent 수집 데이터를 포함
                manus_raw = {
                    "collection_info": {
                        "performed": manus_collection.get("performed", False),
                        "method": manus_collection.get("method", ""),
                        "collection_purpose": manus_collection.get(
                            "collection_purpose", ""
                        ),
                        "ready_for_crewai": manus_collection.get(
                            "ready_for_crewai", False
                        ),
                        "data_richness_score": manus_collection.get(
                            "data_richness_score", 0
                        ),
                        "primary_intent": manus_collection.get("primary_intent", ""),
                        "analysis_focus": manus_collection.get("analysis_focus", ""),
                        "confidence": manus_collection.get("confidence", 0.0),
                    },
                    "collected_information_full": manus_collection.get(
                        "collected_information", ""
                    ),
                    "data_sources_used": {
                        "basic_financial_data_used": manus_collection.get(
                            "basic_financial_data_used", False
                        ),
                        "enhanced_dart_data_used": manus_collection.get(
                            "enhanced_dart_data_used", False
                        ),
                    },
                    "pdf_analysis_included": manus_collection.get("pdf_analysis", {}),
                }

                raw_data["manus_collection_raw_data"] = manus_raw
                logger.info("✅ Manus Agent 수집 원본 데이터 JSON 준비 완료")

            # 5. 🎯 CrewAI 종합 분석 원본 데이터 추출 (수정됨!)
            crewai_analysis = results.get("steps", {}).get(
                "step4_crewai_comprehensive_analysis", {}
            )
            if crewai_analysis and not crewai_analysis.get("error"):
                raw_data["data_sources_summary"][
                    "crewai_comprehensive_analysis_available"
                ] = True

                # CrewAI 종합 분석의 모든 과정과 결과를 포함 (수정된 워크플로우)
                crewai_raw = {
                    "analysis_type": crewai_analysis.get("analysis_type", ""),
                    "sector_detection_process": {
                        "detected_sector": crewai_analysis.get("detected_sector", ""),
                        "sector_korean_name": crewai_analysis.get(
                            "sector_korean_name", ""
                        ),
                        "activated_experts": crewai_analysis.get(
                            "activated_experts", []
                        ),
                        "selected_experts_count": crewai_analysis.get(
                            "selected_experts_count", 0
                        ),
                        "analysis_depth": crewai_analysis.get("analysis_depth", ""),
                    },
                    "data_integration_info": {
                        "data_integration_quality": crewai_analysis.get(
                            "data_integration_quality", {}
                        ),
                        "synthesis_completeness": crewai_analysis.get(
                            "synthesis_completeness", ""
                        ),
                    },
                    "expert_analysis_results": crewai_analysis.get(
                        "expert_insights", {}
                    ),
                    "cost_savings_metrics": crewai_analysis.get("cost_savings", {}),
                    "cache_and_performance": {
                        "cache_key": crewai_analysis.get("cache_key", ""),
                        "cache_used": False,  # 새로운 분석이므로 캐시 사용 안됨
                    },
                    "workflow_integration": {
                        "manus_data_integrated": True,  # Manus 데이터가 통합됨
                        "financial_data_integrated": True,  # 재무데이터 통합됨
                        "enhanced_dart_integrated": bool(
                            enhanced_dart_data
                        ),  # Enhanced DART 통합 여부
                        "comprehensive_analysis": True,  # 종합 분석 수행됨
                    },
                }

                raw_data["crewai_comprehensive_analysis_raw_data"] = crewai_raw
                logger.info(
                    "✅ CrewAI 종합 분석 원본 데이터 JSON 준비 완료 - Manus+재무+DART 통합 분석"
                )

            # 5. 📊 데이터 소스별 통계 정보 추가
            raw_data["data_statistics"] = self._calculate_data_statistics(raw_data)

            logger.info("📊 원본 데이터 JSON 준비 완료 (PDF + CrewAI 포함)")

        except Exception as e:
            logger.error(f"❌ 원본 데이터 준비 중 오류: {e}")
            raw_data["preparation_error"] = str(e)

        return raw_data

    def _calculate_data_statistics(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """원본 데이터의 통계 정보를 계산해요 (PDF + CrewAI 포함)"""
        stats = {
            "total_data_points": 0,
            "yfinance_data_points": 0,
            "enhanced_dart_data_points": 0,
            "pdf_data_points": 0,
            "manus_collection_data_points": 0,  # 🤖 Manus Agent 데이터 포인트 추가
            "crewai_data_points": 0,  # 🚀 CrewAI 데이터 포인트 수정
            "data_completeness": "정보없음",
        }

        try:
            # yfinance 데이터 포인트 계산
            yfinance_data = raw_data.get("yfinance_raw_data", {})
            if yfinance_data:
                yfinance_count = 0
                for section_name, section_data in yfinance_data.items():
                    if isinstance(section_data, dict):
                        # None이 아닌 값들만 카운트
                        yfinance_count += sum(
                            1 for v in section_data.values() if v is not None
                        )
                stats["yfinance_data_points"] = yfinance_count

            # Enhanced DART 데이터 포인트 계산
            enhanced_dart_data = raw_data.get("enhanced_dart_raw_data", {})
            if enhanced_dart_data:
                dart_count = 0
                for section_name, section_data in enhanced_dart_data.items():
                    if isinstance(section_data, dict):
                        dart_count += self._count_nested_dict_values(section_data)
                stats["enhanced_dart_data_points"] = dart_count

            # 🚀 PDF 데이터 포인트 계산
            pdf_data = raw_data.get("pdf_raw_data", {})
            if pdf_data:
                pdf_count = 0
                # PDF 텍스트 길이를 데이터 포인트로 환산 (1000자 = 1포인트)
                pdf_text = pdf_data.get("pdf_full_text", "")
                if pdf_text:
                    pdf_count += max(1, len(pdf_text) // 1000)  # 최소 1포인트

                # 메타데이터도 포인트로 계산
                pdf_metadata = pdf_data.get("pdf_metadata", {})
                if pdf_metadata:
                    pdf_count += sum(1 for v in pdf_metadata.values() if v)

                # 페이지 정보도 포인트로 계산
                pages_info = pdf_data.get("pages_breakdown", [])
                if pages_info:
                    pdf_count += len(pages_info)

                stats["pdf_data_points"] = pdf_count

            # 🤖 Manus Agent 수집 데이터 포인트 계산 (새로 추가!)
            manus_data = raw_data.get("manus_collection_raw_data", {})
            if manus_data:
                manus_count = 0

                # 수집된 정보 길이를 데이터 포인트로 환산 (500자 = 1포인트)
                collected_info = manus_data.get("collected_information_full", "")
                if collected_info:
                    manus_count += max(1, len(collected_info) // 500)  # 최소 1포인트

                # 데이터 풍부함 점수도 포인트로 환산
                collection_info = manus_data.get("collection_info", {})
                richness_score = collection_info.get("data_richness_score", 0)
                manus_count += int(richness_score // 10)  # 10점당 1포인트

                # PDF 분석 포함시 보너스
                pdf_analysis = manus_data.get("pdf_analysis_included", {})
                if pdf_analysis.get("pdf_detected"):
                    manus_count += 20  # PDF 분석 보너스

                stats["manus_collection_data_points"] = manus_count

            # 🚀 CrewAI 종합 분석 데이터 포인트 계산 (수정됨!)
            crewai_data = raw_data.get("crewai_comprehensive_analysis_raw_data", {})
            if crewai_data:
                crewai_count = 0

                # 섹터 감지 프로세스 포인트
                sector_detection = crewai_data.get("sector_detection_process", {})
                if sector_detection:
                    crewai_count += sum(1 for v in sector_detection.values() if v)

                # 활성화된 팀 정보 포인트
                team_info = crewai_data.get("activated_team_info", {})
                if team_info:
                    crewai_count += sum(1 for v in team_info.values() if v)
                    # 전문가 상세 정보는 개수로 계산
                    experts = team_info.get("experts_details", [])
                    crewai_count += len(experts) * 5  # 전문가당 5포인트

                # 분석 깊이 정보 포인트
                depth_info = crewai_data.get("analysis_depth_info", {})
                if depth_info:
                    crewai_count += sum(1 for v in depth_info.values() if v)

                # 전문가 분석 결과 포인트
                analysis_results = crewai_data.get("expert_analysis_results", {})
                if analysis_results:
                    individual_analyses = analysis_results.get(
                        "individual_analyses", []
                    )
                    crewai_count += (
                        len(individual_analyses) * 10
                    )  # 개별 분석당 10포인트

                    # 종합 결과도 길이에 따라 포인트 계산
                    synthesis = analysis_results.get("synthesis_result", "")
                    if synthesis:
                        crewai_count += max(1, len(synthesis) // 500)  # 500자당 1포인트

                # One-Hot 활성화 메트릭 포인트
                activation_metrics = crewai_data.get("one_hot_activation_metrics", {})
                if activation_metrics:
                    crewai_count += sum(1 for v in activation_metrics.values() if v)

                # 섹터별 인사이트 포인트
                sector_insights = crewai_data.get("sector_specific_insights", {})
                if sector_insights:
                    crewai_count += sum(1 for v in sector_insights.values() if v)
                    # 핵심 지표는 개수로 계산
                    key_metrics = sector_insights.get("key_metrics", [])
                    crewai_count += len(key_metrics)

                stats["crewai_data_points"] = crewai_count

            # 총 데이터 포인트 (수정된 워크플로우)
            stats["total_data_points"] = (
                stats["yfinance_data_points"]
                + stats["enhanced_dart_data_points"]
                + stats["pdf_data_points"]
                + stats.get("manus_collection_data_points", 0)  # 🤖 Manus Agent 포함
                + stats["crewai_data_points"]  # 🚀 CrewAI 포함
            )

            # 데이터 완성도 평가 (Manus Agent + CrewAI 포함하여 기준 재조정)
            if (
                stats["total_data_points"] > 400
            ):  # Manus Agent + CrewAI 포함하여 기준 다시 상향
                stats["data_completeness"] = "매우높음"
            elif stats["total_data_points"] > 200:
                stats["data_completeness"] = "높음"
            elif stats["total_data_points"] > 100:
                stats["data_completeness"] = "보통"
            else:
                stats["data_completeness"] = "낮음"

        except Exception as e:
            logger.error(f"데이터 통계 계산 오류: {e}")
            stats["calculation_error"] = str(e)

        return stats

    def _count_nested_dict_values(
        self, data: Dict, max_depth: int = 3, current_depth: int = 0
    ) -> int:
        """중첩된 딕셔너리의 값 개수를 재귀적으로 계산해요"""
        if current_depth > max_depth:
            return 0

        count = 0
        for value in data.values():
            if isinstance(value, dict):
                count += self._count_nested_dict_values(
                    value, max_depth, current_depth + 1
                )
            elif isinstance(value, list):
                count += len(value)
            elif value is not None:
                count += 1
        return count

    async def _create_pdf_chunks_for_crewai(
        self, pdf_text: str, pdf_path: str = None
    ) -> List[Dict[str, Any]]:
        """
        🤖 AI 기반 지능적 PDF 청킹 시스템 (60만자 지원)

        하드코딩된 목차 추출 대신 Manus Agent가 PDF 내용을 분석해서
        자동으로 최적의 청킹을 수행합니다. 청킹 단위도 60만자까지 확장했습니다.

        Args:
            pdf_text: 분할할 PDF 텍스트
            pdf_path: PDF 파일 경로 (참고용)

        Returns:
            List[Dict]: AI 기반 context별 청크 목록
        """
        if not pdf_text or len(pdf_text) < 1000:
            return []

        logger.info(f"🤖 AI 기반 지능적 PDF 청킹 시작 (총 {len(pdf_text):,}자)")

        # 🚀 1. Manus Agent를 통한 AI 기반 구조 분석 (우선 방법)
        try:
            logger.info("🧠 Manus Agent로 PDF 구조 분석 시작...")
            intelligent_chunks = await self._ai_based_pdf_chunking(pdf_text, pdf_path)

            if intelligent_chunks and len(intelligent_chunks) > 0:
                logger.info(f"✅ AI 기반 청킹 성공: {len(intelligent_chunks)}개 청크")
                return intelligent_chunks
            else:
                logger.warning("⚠️ AI 기반 청킹에서 결과 없음 - 폴백 방법 시도")

        except Exception as e:
            logger.warning(f"⚠️ AI 기반 청킹 실패: {e} - 폴백 방법 시도")

        # 📝 2. 고급 키워드 기반 청킹 (폴백, 60만자 지원)
        logger.info("📝 고급 키워드 기반 청킹 수행 (60만자 지원)...")
        return self._advanced_keyword_chunking(pdf_text)

    async def _ai_based_pdf_chunking(
        self, pdf_text: str, pdf_path: str = None
    ) -> List[Dict[str, Any]]:
        """
        🧠 Manus Agent를 활용한 AI 기반 PDF 청킹

        PDF 내용을 AI가 분석해서 논리적인 구조를 파악하고
        의미있는 단위로 자동 분할합니다.
        """
        try:
            # PDF 텍스트가 너무 길면 요약본으로 구조 분석
            analysis_text = pdf_text
            if len(pdf_text) > 100000:  # 10만자 이상이면 앞부분만 분석
                analysis_text = pdf_text[:50000] + "\n...\n" + pdf_text[-10000:]
                logger.info("📊 대용량 PDF - 요약본으로 구조 분석 수행")

            # AI 기반 구조 분석 프롬프트
            structure_analysis_prompt = f"""
다음 PDF 문서의 구조를 분석해서 논리적인 섹션으로 나누어주세요.

📄 **PDF 내용 (총 {len(pdf_text):,}자)**:
{analysis_text}

🎯 **분석 요청**:
1. 이 문서의 주요 섹션들을 식별해주세요
2. 각 섹션의 시작을 나타내는 제목이나 키워드를 찾아주세요
3. 섹션별로 어떤 내용 유형인지 분류해주세요 (재무/사업/리스크/투자/기술/일반)

🔍 **출력 형식** (정확히 이 형식으로):
```
SECTION_1: [섹션제목] | [내용유형] | [시작키워드]
SECTION_2: [섹션제목] | [내용유형] | [시작키워드]
SECTION_3: [섹션제목] | [내용유형] | [시작키워드]
...
```

**예시**:
```
SECTION_1: 경영진단서 | business | 경영진단서
SECTION_2: 재무제표 | financial | 재무제표
SECTION_3: 위험요인 | risk | 위험요인
```

📋 **중요 지침**:
- 각 섹션은 최소 10,000자, 최대 600,000자로 구성
- 논리적으로 연관된 내용끼리 묶어주세요
- 너무 세분화하지 말고 의미있는 큰 단위로 나누어주세요
- 제목이 명확하지 않으면 내용의 핵심 키워드를 사용하세요
"""

            # Manus Agent로 구조 분석 실행
            self.manus_agent.memory.clear()
            self.manus_agent.update_memory("user", structure_analysis_prompt)

            structure_response = ""
            run_result = await self.manus_agent.run()

            if hasattr(run_result, "__aiter__"):
                async for response in run_result:
                    structure_response += response + "\n"
            else:
                structure_response = str(run_result)

            # AI 응답에서 섹션 정보 파싱
            sections = self._parse_ai_section_analysis(structure_response)

            if not sections:
                logger.warning("⚠️ AI 구조 분석에서 섹션을 찾지 못함")
                return []

            # 섹션 정보를 바탕으로 실제 텍스트 분할
            chunks = self._split_text_by_ai_sections(pdf_text, sections)

            logger.info(f"🧠 AI 기반 청킹 완료: {len(chunks)}개 청크 생성")
            return chunks

        except Exception as e:
            logger.error(f"❌ AI 기반 청킹 중 오류: {e}")
            return []

    def _parse_ai_section_analysis(self, ai_response: str) -> List[Dict[str, str]]:
        """
        AI의 섹션 분석 응답에서 구조화된 정보 추출
        """
        sections = []

        try:
            # SECTION_X 패턴으로 섹션 정보 추출
            import re

            # 패턴: SECTION_숫자: 제목 | 유형 | 키워드
            section_pattern = r"SECTION_(\d+):\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*(.+)"

            matches = re.findall(
                section_pattern, ai_response, re.MULTILINE | re.IGNORECASE
            )

            for match in matches:
                section_num, title, content_type, keyword = match
                sections.append(
                    {
                        "section_number": int(section_num),
                        "title": title.strip(),
                        "content_type": content_type.strip(),
                        "start_keyword": keyword.strip(),
                    }
                )

            # 패턴 매칭 실패시 간단한 파싱 시도
            if not sections:
                lines = ai_response.split("\n")
                section_count = 1

                for line in lines:
                    line = line.strip()
                    if line and ("섹션" in line or "section" in line.lower()):
                        # 간단한 섹션 정보 추출
                        if ":" in line:
                            parts = line.split(":")
                            if len(parts) >= 2:
                                title = parts[1].strip()
                                if title:
                                    sections.append(
                                        {
                                            "section_number": section_count,
                                            "title": title,
                                            "content_type": "general",
                                            "start_keyword": title[
                                                :20
                                            ],  # 앞 20자를 키워드로
                                        }
                                    )
                                    section_count += 1

            logger.info(f"🔍 AI 분석에서 {len(sections)}개 섹션 파싱됨")

            # 최소 2개 이상의 섹션이 필요
            if len(sections) >= 2:
                return sections
            else:
                logger.warning("⚠️ 충분한 섹션이 파싱되지 않음")
                return []

        except Exception as e:
            logger.error(f"❌ 섹션 분석 파싱 오류: {e}")
            return []

    def _split_text_by_ai_sections(
        self, pdf_text: str, sections: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        AI가 분석한 섹션 정보를 바탕으로 실제 텍스트를 분할
        """
        chunks = []

        try:
            # 섹션별 시작 위치 찾기
            section_positions = []

            for section in sections:
                start_keyword = section["start_keyword"]

                # 키워드 변형들로 검색
                keyword_variations = [
                    start_keyword,
                    start_keyword.replace(" ", ""),
                    start_keyword.upper(),
                    start_keyword.lower(),
                    # 숫자나 특수문자 제거한 버전
                    re.sub(r"[0-9\.\-\(\)]", "", start_keyword).strip(),
                ]

                best_position = -1
                found_keyword = start_keyword

                for variant in keyword_variations:
                    if variant and len(variant) > 2:
                        pos = pdf_text.find(variant)
                        if pos != -1:
                            best_position = pos
                            found_keyword = variant
                            break

                section_positions.append(
                    {
                        "section": section,
                        "start_pos": best_position,
                        "found_keyword": found_keyword,
                    }
                )

            # 위치 기준으로 정렬
            section_positions.sort(
                key=lambda x: x["start_pos"] if x["start_pos"] != -1 else float("inf")
            )

            # 실제로 찾은 섹션들만 사용
            valid_sections = [sp for sp in section_positions if sp["start_pos"] != -1]

            if not valid_sections:
                logger.warning("⚠️ AI 분석 섹션의 키워드들을 텍스트에서 찾지 못함")
                return []

            # 섹션별로 텍스트 분할 (60만자 제한 적용)
            for i, section_pos in enumerate(valid_sections):
                section = section_pos["section"]
                start_pos = section_pos["start_pos"]

                # 다음 섹션의 시작까지 또는 텍스트 끝까지
                if i + 1 < len(valid_sections):
                    end_pos = valid_sections[i + 1]["start_pos"]
                else:
                    end_pos = len(pdf_text)

                section_text = pdf_text[start_pos:end_pos].strip()

                # 최소 크기 검증 (너무 작은 섹션 제외)
                if len(section_text) > 3000:  # 최소 3000자
                    # 60만자 제한 적용
                    max_size_applied = False
                    if len(section_text) > 600000:
                        section_text = (
                            section_text[:600000]
                            + "\n...[AI 분석 60만자 제한으로 일부 생략]"
                        )
                        max_size_applied = True
                        logger.info(f"📏 AI 섹션 '{section['title']}' 60만자로 제한")

                    # 내용 유형을 표준 컨텍스트로 매핑
                    context_type = self._map_content_type_to_context(
                        section["content_type"]
                    )

                    chunks.append(
                        {
                            "chunk_id": i + 1,
                            "section_title": section["title"],
                            "context_type": context_type,
                            "content": section_text,
                            "content_length": len(section_text),
                            "start_position": start_pos,
                            "start_keyword": section["start_keyword"],
                            "found_keyword": section_pos["found_keyword"],
                            "ai_section_info": section,
                            "chunk_type": "ai_analyzed",
                            "source": "manus_agent_analysis",
                            "max_size_applied": max_size_applied,
                            "analysis_method": "ai_structure_analysis",
                            "keywords_found": self._extract_pdf_chunk_keywords(
                                section_text
                            ),
                        }
                    )

            logger.info(f"✂️ AI 기반 텍스트 분할 완료: {len(chunks)}개 청크")
            return chunks

        except Exception as e:
            logger.error(f"❌ AI 기반 텍스트 분할 중 오류: {e}")
            return []

    def _map_content_type_to_context(self, content_type: str) -> str:
        """
        AI가 분석한 content_type을 표준 context로 매핑
        """
        content_type_lower = content_type.lower()

        mapping = {
            "financial": "financial",
            "재무": "financial",
            "business": "business",
            "사업": "business",
            "risk": "risk",
            "리스크": "risk",
            "위험": "risk",
            "investment": "investment",
            "투자": "investment",
            "governance": "governance",
            "지배구조": "governance",
            "technical": "technical",
            "기술": "technical",
            "technology": "technical",
        }

        for key, value in mapping.items():
            if key in content_type_lower:
                return value

        return "general"

    def _advanced_keyword_chunking(self, pdf_text: str) -> List[Dict[str, Any]]:
        """
        고급 키워드 기반 청킹 (60만자 지원, AI 폴백용)

        기존 키워드 기반 청킹을 개선하여 더 큰 청크와 더 정확한 분할을 지원합니다.
        """
        chunks = []
        lines = pdf_text.split("\n")

        # 개선된 Context 타입별 키워드 정의 (더 포괄적)
        context_keywords = {
            "financial": [
                "재무",
                "financial",
                "매출",
                "revenue",
                "이익",
                "profit",
                "손익",
                "income",
                "자산",
                "assets",
                "부채",
                "liabilities",
                "현금",
                "cash",
                "배당",
                "dividend",
                "ROE",
                "ROA",
                "PER",
                "PBR",
                "부채비율",
                "유동비율",
                "재무제표",
                "대차대조표",
                "손익계산서",
                "현금흐름표",
                "자본금",
                "영업이익",
                "순이익",
                "매출총이익",
                "EBITDA",
                "순자산",
                "유동자산",
                "고정자산",
                "유동부채",
                "장기부채",
                "자기자본",
                "자본총계",
                "투자자산",
                "재무비율",
                "수익성",
                "안정성",
                "성장성",
            ],
            "business": [
                "사업",
                "business",
                "영업",
                "operation",
                "시장",
                "market",
                "경쟁",
                "competition",
                "고객",
                "customer",
                "제품",
                "product",
                "서비스",
                "service",
                "전략",
                "strategy",
                "성장",
                "growth",
                "점유율",
                "market share",
                "업계",
                "산업",
                "industry",
                "브랜드",
                "brand",
                "마케팅",
                "marketing",
                "판매",
                "sales",
                "유통",
                "distribution",
                "파트너십",
                "partnership",
                "경쟁사",
                "competitor",
                "차별화",
                "differentiation",
            ],
            "risk": [
                "리스크",
                "risk",
                "위험",
                "danger",
                "문제",
                "problem",
                "우려",
                "concern",
                "하락",
                "decline",
                "부정적",
                "negative",
                "위기",
                "crisis",
                "불확실",
                "uncertainty",
                "변동",
                "volatility",
                "손실",
                "loss",
                "취약",
                "vulnerable",
                "제약",
                "constraint",
                "규제",
                "regulation",
                "환경변화",
                "변동성",
                "신용위험",
                "시장위험",
                "운영위험",
            ],
            "investment": [
                "투자",
                "investment",
                "주가",
                "stock price",
                "목표가",
                "target price",
                "전망",
                "outlook",
                "추천",
                "recommendation",
                "매수",
                "buy",
                "매도",
                "sell",
                "밸류에이션",
                "valuation",
                "적정가",
                "fair value",
                "투자자",
                "investor",
                "포트폴리오",
                "portfolio",
                "수익률",
                "return",
                "배당수익률",
                "dividend yield",
            ],
            "governance": [
                "지배구조",
                "governance",
                "주주",
                "shareholder",
                "이사회",
                "board",
                "경영진",
                "management",
                "임원",
                "executive",
                "보상",
                "compensation",
                "의결권",
                "voting",
                "투명성",
                "transparency",
                "기업지배구조",
                "ESG",
                "사외이사",
                "independent director",
                "감사",
                "audit",
                "내부통제",
            ],
            "technical": [
                "기술",
                "technology",
                "혁신",
                "innovation",
                "개발",
                "development",
                "R&D",
                "연구",
                "특허",
                "patent",
                "플랫폼",
                "platform",
                "시스템",
                "system",
                "솔루션",
                "solution",
                "디지털",
                "digital",
                "AI",
                "인공지능",
                "자동화",
                "데이터",
                "data",
                "클라우드",
                "cloud",
                "소프트웨어",
                "software",
            ],
        }

        # 대용량 청킹을 위한 개선된 알고리즘
        current_chunk = {
            "lines": [],
            "context_type": "general",
            "score": 0,
            "context_scores": {},
        }
        chunks_buffer = []

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # 각 라인의 context 점수 계산 (개선된 알고리즘)
            line_scores = {}
            line_lower = line.lower()

            for context_type, keywords in context_keywords.items():
                score = 0
                for keyword in keywords:
                    if keyword in line_lower:
                        # 키워드 길이에 따른 가중치 적용
                        score += len(keyword) * 0.5 + 1

                if score > 0:
                    line_scores[context_type] = score

            # 현재 청크에 라인 추가
            current_chunk["lines"].append(line)

            # 청크의 누적 점수 업데이트
            for context_type, score in line_scores.items():
                if context_type not in current_chunk["context_scores"]:
                    current_chunk["context_scores"][context_type] = 0
                current_chunk["context_scores"][context_type] += score

            # 청크 크기가 적당하면 (50-300줄) context 결정
            chunk_size = len(current_chunk["lines"])

            if chunk_size >= 50:  # 최소 50줄
                # 청크의 주요 context 결정
                if current_chunk["context_scores"]:
                    best_context = max(
                        current_chunk["context_scores"].items(), key=lambda x: x[1]
                    )
                    current_chunk["context_type"] = best_context[0]
                    current_chunk["score"] = best_context[1]

                # 청크가 충분히 크면 (300줄 이상 또는 50만자 이상) 분할
                chunk_text = "\n".join(current_chunk["lines"])
                if chunk_size >= 300 or len(chunk_text) >= 500000:  # 50만자 기준
                    chunks_buffer.append(current_chunk)
                    current_chunk = {
                        "lines": [],
                        "context_type": "general",
                        "score": 0,
                        "context_scores": {},
                    }

        # 마지막 청크 처리
        if current_chunk["lines"]:
            chunk_text = "\n".join(current_chunk["lines"])
            if current_chunk["context_scores"]:
                best_context = max(
                    current_chunk["context_scores"].items(), key=lambda x: x[1]
                )
                current_chunk["context_type"] = best_context[0]
                current_chunk["score"] = best_context[1]
            chunks_buffer.append(current_chunk)

        # 청크를 최종 형태로 변환 (60만자 제한 적용)
        for i, chunk_data in enumerate(chunks_buffer):
            chunk_text = "\n".join(chunk_data["lines"])

            if len(chunk_text) > 2000:  # 최소 크기 필터 (2000자)
                # 60만자 제한 적용
                if len(chunk_text) > 600000:
                    chunk_text = (
                        chunk_text[:600000] + "\n...[텍스트 길이 제한으로 일부 생략]"
                    )
                    logger.info(f"📏 청크 {i+1} 60만자로 제한됨")

                chunks.append(
                    {
                        "chunk_id": i + 1,
                        "context_type": chunk_data["context_type"],
                        "content": chunk_text,
                        "content_length": len(chunk_text),
                        "line_count": len(chunk_data["lines"]),
                        "relevance_score": chunk_data["score"],
                        "context_distribution": chunk_data["context_scores"],
                        "keywords_found": self._extract_pdf_chunk_keywords(chunk_text),
                        "source": "advanced_keyword_based",
                        "chunk_type": "advanced_keyword",
                        "max_size_applied": len(chunk_text) >= 600000,
                    }
                )

        logger.info(
            f"📝 고급 키워드 기반 청킹 완료: {len(chunks)}개 청크 (최대 60만자 지원)"
        )
        return chunks

    def _extract_pdf_chunk_keywords(self, text: str) -> List[str]:
        """PDF 청크에서 핵심 키워드 추출"""
        import re

        # 숫자가 포함된 중요한 패턴들
        patterns = [
            r"\d+[%％]",  # 퍼센트
            r"\d+[조억만천]원?",  # 한국 단위
            r"\d+\.?\d*[MB]?억?원?",  # 금액
            r"ROE|ROA|PER|PBR|EPS",  # 재무비율
            r"[가-힣]{2,}주식회사?|[A-Z]{2,}",  # 회사명/브랜드
        ]

        keywords = []
        text_lower = text.lower()

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            keywords.extend(matches[:3])  # 각 패턴에서 최대 3개

        return keywords[:10]  # 최대 10개 키워드


async def main():
    """메인 실행 함수 - 한 번 실행하고 자동 종료"""
    print("🚀 개선된 주식 분석 시스템에 오신 것을 환영합니다!")
    print("=" * 60)
    print("📊 새로운 기능:")
    print("  ✅ 실제 재무데이터 기반 분석 (yfinance + DART API)")
    print("  ✅ 정량적 지표 기반 정밀 분류")
    print("  ✅ 데이터 품질 평가 및 신뢰도 측정")
    print("  ✅ 종합적인 결과 저장")
    print("=" * 60)

    # 시스템 초기화
    system = EnhancedStockAnalysisSystem()

    try:
        # 사용자 입력 받기 (한 번만)
        print("\n" + "=" * 50)
        user_input = input("📝 질문을 입력하세요: ").strip()

        if not user_input:
            print("❌ 빈 입력입니다. 프로그램을 종료합니다.")
            return

        print(f"\n🔍 분석 시작: {user_input}")
        print("-" * 50)

        # PDF 처리는 이제 웹 검색 중에 자동으로 수행됩니다
        # (별도의 전처리 필요 없음)

        # 개선된 분석 실행
        results = await system.run_enhanced_analysis(user_input)

        # 결과 출력
        if results["success"]:
            print("\n✅ 분석 완료!")

            # PDF 분석 결과 출력
            pdf_analysis = results.get("steps", {}).get("pdf_large_analysis", {})
            if pdf_analysis.get("pdf_detected"):
                print(f"📄 PDF 분석: {pdf_analysis['pdf_path']}")
                if pdf_analysis.get("analysis_completed"):
                    pdf_result = pdf_analysis.get("analysis_result", {})
                    print(
                        f"📄 PDF 분석 완료: {pdf_result.get('saved_file', '파일 저장됨')}"
                    )
                    print(
                        f"📄 분석 대상: {pdf_result.get('company_name', '알 수 없음')}"
                    )
                else:
                    print(
                        f"❌ PDF 분석 실패: {pdf_analysis.get('error', '알 수 없는 오류')}"
                    )

            # 종합 요약 출력
            summary = results.get("final_summary", {})
            analyzed_stock = summary.get("analyzed_stock", {})
            data_sources = summary.get("data_sources", {})

            print(
                f"📊 분석 대상: {analyzed_stock.get('name', '정보없음')} ({analyzed_stock.get('code', '정보없음')})"
            )
            print(
                f"📈 데이터 수집: {'성공' if data_sources.get('financial_data_collected') else '실패'}"
            )
            if data_sources.get("data_sources"):
                print(f"🗂️ 데이터 출처: {', '.join(data_sources['data_sources'])}")
            print(f"🔍 데이터 품질: {data_sources.get('data_quality', '정보없음')}")

            # 저장된 파일 정보
            if results.get("saved_file"):
                print(f"💾 결과 저장: {results['saved_file']}")

            print("\n📁 상세 결과는 저장된 JSON 파일을 확인해주세요!")
            print("🎉 분석이 완료되었습니다. 프로그램을 종료합니다.")

        else:
            print(f"❌ 분석 실패: {results.get('error', '알 수 없는 오류')}")
            print("⚠️ 프로그램을 종료합니다.")

    except KeyboardInterrupt:
        print("\n👋 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"❌ 시스템 오류: {e}")
        print("⚠️ 프로그램을 종료합니다.")


if __name__ == "__main__":
    asyncio.run(main())
