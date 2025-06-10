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
import json
import os
import re

# 프로젝트 경로 설정
import sys
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 모듈 import
from app.agent.manus import Manus
from app.agent.stock_classifier import StockClassifier
from app.data_collector import FinancialDataCollector
from app.llm import LLM
from app.logger import logger


class EnhancedStockAnalysisSystem:
    """
    개선된 주식 분석 시스템 클래스
    실제 재무데이터를 기반으로 정확한 분석을 수행해요!
    """

    def __init__(self):
        """시스템 초기화"""
        logger.info("🚀 개선된 주식 분석 시스템 초기화...")

        # 에이전트들 초기화
        self.llm = LLM()
        self.stock_classifier = StockClassifier(llm=self.llm)
        self.manus_agent = Manus(llm=self.llm)

        # 재무데이터 수집기 초기화 (DART API 키는 선택사항)
        dart_api_key = os.getenv("DART_API_KEY")  # 환경변수에서 가져오기
        self.financial_collector = FinancialDataCollector(dart_api_key=dart_api_key)

        # 결과 저장용
        self.analysis_results = {}

        logger.info("✅ 모든 컴포넌트 초기화 완료!")

    async def run_enhanced_analysis(self, user_prompt: str) -> Dict[str, Any]:
        """
        개선된 분석 플로우의 메인 실행 함수

        Args:
            user_prompt: 사용자 입력 프롬프트

        Returns:
            Dict: 전체 분석 결과
        """
        logger.info(f"🔍 개선된 분석 시작: {user_prompt}")

        results = {
            "user_prompt": user_prompt,
            "timestamp": datetime.now().isoformat(),
            "analysis_flow": "enhanced",
            "success": False,
            "steps": {},
        }

        try:
            # Step 1: 종목 및 종목코드 감지
            logger.info("📋 Step 1: 종목 및 종목코드 감지")
            stock_info = self.extract_stock_info(user_prompt)
            results["steps"]["step1_stock_detection"] = stock_info

            if not stock_info["detected"]:
                results["error"] = "종목이나 종목코드를 감지할 수 없습니다"
                logger.warning("⚠️ 종목 감지 실패")
                return results

            logger.info(
                f"✅ 감지된 종목: {stock_info['stock_name']} ({stock_info['stock_code']})"
            )

            # Step 2: 재무데이터 수집
            logger.info("📊 Step 2: 실제 재무데이터 수집")
            financial_data = self.financial_collector.collect_stock_data(
                stock_code=stock_info["stock_code"], stock_name=stock_info["stock_name"]
            )
            results["steps"]["step2_financial_data"] = financial_data

            if not financial_data["success"]:
                logger.warning("⚠️ 재무데이터 수집 실패 - 기존 방식으로 진행")
                # 재무데이터 없이도 분석 계속 진행
            else:
                logger.info(
                    f"✅ 재무데이터 수집 완료 (출처: {', '.join(financial_data['data_sources'])})"
                )

            # Step 3: 재무데이터 기반 종목 분류
            logger.info("🏷️ Step 3: 재무데이터 기반 종목 분류")
            classification_result = await self.perform_enhanced_classification(
                user_prompt, stock_info, financial_data
            )
            results["steps"]["step3_classification"] = classification_result

            # Step 4: 재무데이터 기반 상세 분석
            logger.info("📈 Step 4: 재무데이터 기반 상세 분석")
            analysis_result = await self.perform_enhanced_analysis(
                user_prompt, stock_info, financial_data, classification_result
            )
            results["steps"]["step4_detailed_analysis"] = analysis_result

            # Step 5: 종합 결과 정리
            logger.info("📋 Step 5: 종합 결과 정리")
            final_summary = self.create_comprehensive_summary(results)
            results["final_summary"] = final_summary

            # Step 6: JSON 파일 저장
            logger.info("💾 Step 6: 결과 저장")
            saved_file = self.save_enhanced_results(results, stock_info)
            results["saved_file"] = saved_file

            results["success"] = True
            logger.info("🎉 개선된 분석 완료!")

        except Exception as e:
            logger.error(f"❌ 분석 중 오류 발생: {e}")
            results["error"] = str(e)

        return results

    def extract_stock_info(self, prompt: str) -> Dict[str, Any]:
        """
        사용자 프롬프트에서 종목 정보를 추출해요

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

        # 1. 6자리 종목코드 패턴 검색 (한국 주식)
        korean_code_pattern = r"\b(\d{6})\b"
        korean_codes = re.findall(korean_code_pattern, prompt)

        if korean_codes:
            result["detected"] = True
            result["stock_code"] = korean_codes[0]
            result["detection_method"] = "korean_stock_code"
            logger.info(f"📈 한국 종목코드 감지: {result['stock_code']}")

        # 2. 해외 티커 패턴 검색 (2-5자리 대문자)
        if not result["detected"]:
            ticker_pattern = r"\b([A-Z]{2,5})\b"
            tickers = re.findall(ticker_pattern, prompt.upper())

            if tickers:
                # 일반적인 단어 제외 (예: "THE", "AND" 등)
                excluded_words = {
                    "THE",
                    "AND",
                    "FOR",
                    "YOU",
                    "ARE",
                    "NOT",
                    "BUT",
                    "CAN",
                }
                valid_tickers = [t for t in tickers if t not in excluded_words]

                if valid_tickers:
                    result["detected"] = True
                    result["stock_code"] = valid_tickers[0]
                    result["detection_method"] = "ticker_symbol"
                    logger.info(f"🌐 해외 티커 감지: {result['stock_code']}")

        # 3. 한국 회사명 패턴 검색
        if not result["detected"]:
            korean_companies = [
                "삼성전자",
                "SK하이닉스",
                "LG전자",
                "현대자동차",
                "카카오",
                "네이버",
                "셀트리온",
                "LG화학",
                "포스코",
                "삼성바이오로직스",
                "삼성SDI",
                "기아",
            ]

            for company in korean_companies:
                if company in prompt:
                    result["detected"] = True
                    result["stock_name"] = company
                    result["detection_method"] = "company_name"
                    logger.info(f"🏢 회사명 감지: {result['stock_name']}")
                    break

        return result

    async def perform_enhanced_classification(
        self, user_prompt: str, stock_info: Dict, financial_data: Dict
    ) -> Dict[str, Any]:
        """
        재무데이터를 활용한 개선된 종목 분류

        Args:
            user_prompt: 사용자 질문
            stock_info: 감지된 종목 정보
            financial_data: 수집된 재무데이터

        Returns:
            Dict: 분류 결과
        """
        try:
            # 분류 키워드 감지
            classification_keywords = [
                "분류",
                "classify",
                "유형",
                "type",
                "저성장주",
                "우량주",
                "고성장주",
                "자산주",
                "턴어라운드주",
                "시이클주",
                "기타주",
                "어떤 종류",
                "어떤 유형",
                "분석",
                "analyze",
                "어떤 주식",
                "어떤 종목",
                "성격",
                "특성",
            ]

            should_classify = any(
                keyword in user_prompt.lower() for keyword in classification_keywords
            )

            if not should_classify:
                # 종목이 감지되면 자동으로 분류 실행
                should_classify = stock_info["detected"]

            if should_classify:
                logger.info("🏷️ 종목 분류 실행...")

                # 재무데이터가 있으면 포함해서 분류
                if financial_data.get("success"):
                    financial_summary = self.financial_collector.get_analysis_summary(
                        financial_data
                    )
                    enhanced_prompt = f"""
다음 종목에 대한 분류를 수행해주세요:

사용자 질문: {user_prompt}

실제 재무데이터:
{financial_summary}

위 실제 재무정보를 바탕으로 정확한 분류를 수행해주세요.
"""
                else:
                    enhanced_prompt = (
                        f"다음 종목에 대한 분류를 수행해주세요: {user_prompt}"
                    )

                # Stock Classifier 실행
                self.stock_classifier.reset()
                self.stock_classifier.update_memory("user", enhanced_prompt)

                classification_response = ""
                async for response in self.stock_classifier.run():
                    classification_response += response + "\n"

                return {
                    "performed": True,
                    "method": (
                        "enhanced_with_financial_data"
                        if financial_data.get("success")
                        else "standard"
                    ),
                    "response": classification_response.strip(),
                    "financial_data_used": financial_data.get("success", False),
                }
            else:
                return {
                    "performed": False,
                    "reason": "분류 키워드나 종목이 감지되지 않음",
                }

        except Exception as e:
            logger.error(f"분류 중 오류: {e}")
            return {"performed": False, "error": str(e)}

    async def perform_enhanced_analysis(
        self,
        user_prompt: str,
        stock_info: Dict,
        financial_data: Dict,
        classification_result: Dict,
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
            logger.info("📊 상세 분석 실행...")

            # 분석용 프롬프트 구성
            analysis_prompt = f"사용자 질문: {user_prompt}\n\n"

            # 재무데이터 포함
            if financial_data.get("success"):
                financial_summary = self.financial_collector.get_analysis_summary(
                    financial_data
                )
                analysis_prompt += f"""
실제 재무데이터:
{financial_summary}

"""

            # 분류 결과 포함
            if classification_result.get("performed"):
                analysis_prompt += f"""
종목 분류 결과:
{classification_result.get('response', '')}

"""

            analysis_prompt += """
위 정보들을 종합하여 상세한 투자 분석을 수행해주세요.
특히 실제 재무데이터가 있다면 이를 중심으로 분석해주세요.
"""

            # Manus 에이전트 실행
            self.manus_agent.reset()
            self.manus_agent.update_memory("user", analysis_prompt)

            analysis_response = ""
            async for response in self.manus_agent.run():
                analysis_response += response + "\n"

            return {
                "performed": True,
                "method": (
                    "enhanced_with_financial_data"
                    if financial_data.get("success")
                    else "standard"
                ),
                "response": analysis_response.strip(),
                "financial_data_used": financial_data.get("success", False),
                "classification_included": classification_result.get(
                    "performed", False
                ),
            }

        except Exception as e:
            logger.error(f"상세 분석 중 오류: {e}")
            return {"performed": False, "error": str(e)}

    def create_comprehensive_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """전체 분석 결과의 종합 요약을 생성해요"""
        stock_info = results["steps"].get("step1_stock_detection", {})
        financial_data = results["steps"].get("step2_financial_data", {})
        classification = results["steps"].get("step3_classification", {})
        analysis = results["steps"].get("step4_detailed_analysis", {})

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
                "classification_performed": classification.get("performed", False),
                "detailed_analysis_performed": analysis.get("performed", False),
                "financial_data_enhanced": financial_data.get("success", False),
            },
            "key_insights": self.extract_key_insights(classification, analysis),
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

        # 분류 결과에서 핵심 정보 추출
        if classification.get("performed"):
            class_response = classification.get("response", "")
            # 간단한 키워드 기반 추출 (실제로는 더 정교한 NLP 처리 필요)
            if "우량주" in class_response:
                insights["classification"] = "우량주"
            elif "고성장주" in class_response:
                insights["classification"] = "고성장주"
            elif "자산주" in class_response:
                insights["classification"] = "자산주"

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
        """개선된 분석 결과를 JSON 파일로 저장해요"""
        try:
            # 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stock_identifier = (
                stock_info.get("stock_code")
                or stock_info.get("stock_name")
                or "unknown"
            )
            filename = f"enhanced_analysis_{stock_identifier}_{timestamp}.json"

            # results 디렉토리 생성
            os.makedirs("results", exist_ok=True)
            filepath = f"results/{filename}"

            # JSON 저장
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

            logger.info(f"💾 분석 결과 저장: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"결과 저장 중 오류: {e}")
            return None


async def main():
    """메인 실행 함수"""
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
        while True:
            print("\n" + "=" * 50)
            user_input = input(
                "📝 질문을 입력하세요 (종료: 'quit' 또는 'exit'): "
            ).strip()

            if user_input.lower() in ["quit", "exit", "종료"]:
                print("👋 시스템을 종료합니다. 감사합니다!")
                break

            if not user_input:
                print("❌ 빈 입력입니다. 다시 입력해주세요.")
                continue

            print(f"\n🔍 분석 시작: {user_input}")
            print("-" * 50)

            # 개선된 분석 실행
            results = await system.run_enhanced_analysis(user_input)

            # 결과 출력
            if results["success"]:
                print("\n✅ 분석 완료!")

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

                print("\n상세 결과는 저장된 JSON 파일을 확인해주세요! 📁")

            else:
                print(f"❌ 분석 실패: {results.get('error', '알 수 없는 오류')}")

    except KeyboardInterrupt:
        print("\n👋 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"❌ 시스템 오류: {e}")


if __name__ == "__main__":
    asyncio.run(main())
