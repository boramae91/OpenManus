# 개선된 종목 분류 에이전트 (재무데이터 기반)
# 실제 재무정보를 바탕으로 더 정확하게 종목을 분류하는 고도화된 에이전트예요!

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import Field

from ..llm import LLM
from ..logger import logger
from ..schema import AgentState
from .base import BaseAgent


class EnhancedStockClassifier(BaseAgent):
    """
    실제 재무데이터를 기반으로 종목을 분류하는 고도화된 에이전트예요
    - DART API와 yfinance에서 수집한 실제 재무정보 활용
    - 정량적 지표와 정성적 분석을 결합한 정확한 분류
    """

    name: str = "EnhancedStockClassifier"
    description: str = "실제 재무데이터 기반 고정밀 종목 분류 에이전트"

    # 재무데이터 기반 고도화된 시스템 프롬프트
    system_prompt: str = """
당신은 실제 재무데이터를 바탕으로 종목을 정밀 분류하는 최고 수준의 금융 분석 전문가입니다.

제공된 실제 재무데이터를 기반으로 다음 7가지 분류 중 하나로 정확하게 분류해주세요:

📊 **분류 체계 및 정량적 기준:**

1. **저성장주 (Low Growth Stock)**
   - 매출 성장률: 연평균 0-5%
   - PER: 8-15배 범위의 안정적 밸류에이션
   - 배당수익률: 3% 이상의 꾸준한 배당
   - 부채비율: 50% 이하의 안정적 재무구조
   - 특징: 성숙 산업, 안정적 현금흐름

2. **우량주 (Blue Chip Stock)**
   - 시가총액: 10조원 이상 (대형주)
   - ROE: 10% 이상의 우수한 자본효율성
   - 매출액: 10조원 이상의 안정적 사업규모
   - 배당: 연속 3년 이상 배당 지급
   - 특징: 업계 1-2위, 시장 지배력

3. **고성장주 (High Growth Stock)**
   - 매출 성장률: 연평균 15% 이상
   - 영업이익 성장률: 20% 이상
   - PER: 높은 밸류에이션 (30배 이상 허용)
   - R&D 투자비율: 매출 대비 5% 이상
   - 특징: 혁신 기술, 신시장 개척

4. **자산주 (Asset Stock)**
   - PBR: 1.0 미만의 저평가
   - 순자산 대비 현금비중: 높음
   - 부동산 등 유형자산 비중: 총자산 50% 이상
   - 특징: 자산가치 > 시장가치

5. **턴어라운드주 (Turnaround Stock)**
   - 최근 3년간 적자 또는 부진
   - 최근 1년 실적 개선 징후
   - 부채비율 개선 추세
   - 구조조정 진행 또는 완료
   - 특징: V자 회복 기대

6. **시이클주 (Cyclical Stock)**
   - 매출/이익 변동계수: 높음 (업종별 경기 민감도)
   - 원자재/에너지 연관 업종
   - PER 밴드폭: 5배-50배 넓은 범위
   - 특징: 경기 사이클과 강한 상관관계

7. **기타주 (Other Stock)**
   - 위 분류 기준에 명확히 부합하지 않음
   - 특수한 사업모델 (REITs, 지주회사 등)
   - 신규 상장 기업 (데이터 부족)

📈 **분석 프로세스:**
1. 정량적 지표 우선 분석 (성장률, 밸류에이션, 재무안정성)
2. 업종 특성 및 사업모델 고려
3. 경기 민감도 및 시장 포지션 평가
4. 최근 3년 트렌드 분석
5. 종합 판단 및 신뢰도 평가

반드시 제공된 실제 재무데이터를 근거로 분석하고, 추측이나 일반론을 배제해주세요.
"""

    max_steps: int = 2
    classification_result: Optional[Dict] = Field(default=None)

    async def classify_with_financial_data(
        self, financial_data: Dict[str, Any], stock_query: str = ""
    ) -> Dict[str, Any]:
        """
        실제 재무데이터를 바탕으로 종목을 분류하는 메인 함수예요

        Args:
            financial_data: FinancialDataCollector에서 수집한 재무데이터
            stock_query: 사용자의 원래 질문 (선택사항)

        Returns:
            Dict: 분류 결과 및 상세 분석
        """
        logger.info(f"📊 재무데이터 기반 종목 분류 시작...")

        if not financial_data.get("success"):
            return {
                "success": False,
                "error": "재무데이터가 제공되지 않았거나 수집에 실패했습니다",
                "classification": None,
                "analysis": "재무데이터 부족으로 분류할 수 없습니다",
            }

        try:
            # 1단계: 재무데이터 요약 및 분석 준비
            financial_summary = self._prepare_financial_summary(financial_data)

            # 2단계: AI 분류 실행
            classification_result = await self._perform_classification(
                financial_summary, stock_query
            )

            # 3단계: 정량적 검증 및 신뢰도 평가
            validated_result = self._validate_classification(
                classification_result, financial_data
            )

            logger.info(
                f"✅ 재무데이터 기반 분류 완료: {validated_result.get('classification', {}).get('classification')}"
            )

            return {
                "success": True,
                "classification": validated_result,
                "financial_data_used": financial_data.get("data_sources", []),
                "data_quality": financial_data.get("data_quality", "보통"),
                "full_analysis": classification_result,
            }

        except Exception as e:
            logger.error(f"❌ 재무데이터 기반 분류 중 오류: {e}")
            return {
                "success": False,
                "error": f"분류 중 오류 발생: {str(e)}",
                "classification": None,
            }

    def _prepare_financial_summary(self, financial_data: Dict[str, Any]) -> str:
        """
        재무데이터를 AI 분석용 텍스트로 정리하는 함수예요

        Args:
            financial_data: 수집된 재무데이터

        Returns:
            str: AI 분석용 재무데이터 요약
        """
        stock_info = financial_data.get("stock_info", {})
        basic_info = financial_data.get("basic_info", {})
        current_price_info = financial_data.get("current_price_info", {})
        financial_ratios = financial_data.get("financial_ratios", {})
        growth_metrics = financial_data.get("growth_metrics", {})
        price_history = financial_data.get("price_history", {})

        # 정량적 지표 중심으로 구조화된 요약 생성
        summary = f"""
=== 실제 재무데이터 기반 종목 분석 ===

🏢 **기업 기본정보:**
- 기업명: {basic_info.get('company_name', stock_info.get('stock_name', '정보없음'))}
- 종목코드: {stock_info.get('stock_code', '정보없음')}
- 섹터: {basic_info.get('sector', '정보없음')}
- 산업: {basic_info.get('industry', '정보없음')}
- 거래소: {basic_info.get('exchange', '정보없음')}

💰 **시장 데이터:**
- 현재 주가: {current_price_info.get('current_price', 'N/A'):,} {basic_info.get('currency', 'KRW')}
- 시가총액: {self._format_large_number(current_price_info.get('market_cap', 0))}
- 발행주식수: {self._format_large_number(current_price_info.get('shares_outstanding', 0))}
- 거래량: {current_price_info.get('volume', 'N/A'):,}

📊 **핵심 재무지표:**
- PER (주가수익비율): {financial_ratios.get('pe_ratio', 'N/A')}
- PBR (주가순자산비율): {financial_ratios.get('pb_ratio', 'N/A')}
- PSR (주가매출비율): {financial_ratios.get('ps_ratio', 'N/A')}
- ROE (자기자본이익률): {self._format_percentage(financial_ratios.get('return_on_equity'))}
- ROA (총자산이익률): {self._format_percentage(financial_ratios.get('return_on_assets'))}
- 부채비율: {financial_ratios.get('debt_to_equity', 'N/A')}
- 유동비율: {financial_ratios.get('current_ratio', 'N/A')}

📈 **성장성 지표:**
- 매출 성장률 (연간): {self._format_percentage(growth_metrics.get('revenue_growth'))}
- 이익 성장률 (연간): {self._format_percentage(growth_metrics.get('earnings_growth'))}
- 매출 성장률 (분기): {self._format_percentage(growth_metrics.get('revenue_quarterly_growth'))}
- 이익 성장률 (분기): {self._format_percentage(growth_metrics.get('earnings_quarterly_growth'))}

💎 **수익성 지표:**
- 순이익률: {self._format_percentage(financial_ratios.get('profit_margin'))}
- 영업이익률: {self._format_percentage(financial_ratios.get('operating_margin'))}
- 배당수익률: {self._format_percentage(financial_ratios.get('dividend_yield'))}

📉 **주가 성과:**
- 52주 최고가: {price_history.get('52_week_high', 'N/A')}
- 52주 최저가: {price_history.get('52_week_low', 'N/A')}
- 1년 수익률: {self._format_percentage(price_history.get('price_change_1y', 0)/100) if price_history.get('price_change_1y') else 'N/A'}
- 평균 거래량 (3개월): {self._format_large_number(price_history.get('avg_volume_3m', 0))}

🔍 **데이터 품질:** {financial_data.get('data_quality', '보통')}
📅 **데이터 수집 시점:** {stock_info.get('collection_timestamp', 'N/A')}
🗂️ **데이터 출처:** {', '.join(financial_data.get('data_sources', []))}

위 실제 재무데이터를 바탕으로 정확한 종목 분류를 수행해주세요.
"""

        return summary.strip()

    async def _perform_classification(
        self, financial_summary: str, user_query: str = ""
    ) -> str:
        """
        준비된 재무데이터 요약을 바탕으로 AI 분류를 실행해요

        Args:
            financial_summary: 정리된 재무데이터 요약
            user_query: 사용자 원래 질문

        Returns:
            str: AI 분류 결과
        """
        classification_prompt = f"""
실제 재무데이터를 바탕으로 정밀한 종목 분류를 수행해주세요.

📊 **제공된 실제 재무데이터:**
{financial_summary}

{"🙋 **사용자 질문:** " + user_query if user_query else ""}

📋 **분류 요청사항:**
1. 위 실제 재무데이터만을 근거로 분석해주세요 (추측 금지)
2. 정량적 지표를 우선적으로 고려해주세요
3. 각 분류 기준별 부합도를 점수화해주세요 (1-5점)
4. 최종 분류와 명확한 근거를 제시해주세요
5. 신뢰도를 평가해주세요 (높음/보통/낮음)

**결과 형식:**
**분류 결과: [7가지 분류 중 1개]**
**신뢰도: [높음/보통/낮음]**
**주요 근거:**
- 정량적 근거 1 (구체적 수치 포함)
- 정량적 근거 2 (구체적 수치 포함)
- 정량적 근거 3 (구체적 수치 포함)
**추가 분석:**
[상세 분석 내용]
"""

        # 메모리 초기화 및 프롬프트 설정
        self.memory.clear()
        self.update_memory("user", classification_prompt)

        # AI 분류 실행
        system_messages = [{"role": "system", "content": self.system_prompt}]
        response = await self.llm.ask(
            messages=self.memory.to_dict_list(), system_msgs=system_messages
        )

        self.update_memory("assistant", response)
        return response

    def _validate_classification(
        self, ai_result: str, financial_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        AI 분류 결과를 정량적 지표로 검증하고 신뢰도를 평가해요

        Args:
            ai_result: AI가 분석한 분류 결과
            financial_data: 원본 재무데이터

        Returns:
            Dict: 검증된 최종 분류 결과
        """
        try:
            # AI 결과에서 분류 정보 파싱
            parsed_result = self._parse_ai_classification(ai_result)

            # 정량적 지표 기반 검증
            quantitative_validation = self._quantitative_validation(financial_data)

            # 최종 신뢰도 계산
            final_confidence = self._calculate_final_confidence(
                parsed_result.get("confidence", "보통"),
                quantitative_validation,
                financial_data.get("data_quality", "보통"),
            )

            return {
                "classification": parsed_result.get("classification", "기타주"),
                "confidence": final_confidence,
                "reasoning": parsed_result.get("reasoning", []),
                "quantitative_scores": quantitative_validation,
                "data_validation": {
                    "data_quality": financial_data.get("data_quality", "보통"),
                    "data_sources": financial_data.get("data_sources", []),
                    "key_metrics_available": self._check_key_metrics(financial_data),
                },
                "raw_ai_analysis": ai_result,
            }

        except Exception as e:
            logger.error(f"분류 결과 검증 중 오류: {e}")
            return {
                "classification": "기타주",
                "confidence": "낮음",
                "reasoning": ["검증 과정에서 오류 발생"],
                "error": str(e),
            }

    def _parse_ai_classification(self, ai_result: str) -> Dict[str, Any]:
        """AI 분석 결과에서 구조화된 정보를 추출해요"""
        import re

        # 분류 결과 추출
        classification_match = re.search(r"분류 결과:\s*([^\n]+)", ai_result)
        classification = (
            classification_match.group(1).strip() if classification_match else "기타주"
        )

        # 신뢰도 추출
        confidence_match = re.search(r"신뢰도:\s*([^\n]+)", ai_result)
        confidence = confidence_match.group(1).strip() if confidence_match else "보통"

        # 근거 추출
        reasoning_section = re.search(
            r"주요 근거:\s*(.*?)(?=\*\*|$)", ai_result, re.DOTALL
        )
        reasoning = []
        if reasoning_section:
            reasoning_text = reasoning_section.group(1)
            reasoning = [
                line.strip("- ").strip()
                for line in reasoning_text.split("\n")
                if line.strip() and line.strip().startswith("-")
            ]

        return {
            "classification": classification,
            "confidence": confidence,
            "reasoning": reasoning[:5],  # 최대 5개까지
        }

    def _quantitative_validation(
        self, financial_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """정량적 지표 기반으로 각 분류별 점수를 계산해요"""
        financial_ratios = financial_data.get("financial_ratios", {})
        growth_metrics = financial_data.get("growth_metrics", {})
        current_price_info = financial_data.get("current_price_info", {})

        scores = {
            "저성장주": 0.0,
            "우량주": 0.0,
            "고성장주": 0.0,
            "자산주": 0.0,
            "턴어라운드주": 0.0,
            "시이클주": 0.0,
            "기타주": 0.0,
        }

        # 성장률 기반 점수 계산
        revenue_growth = growth_metrics.get("revenue_growth", 0) or 0
        if revenue_growth < 0.05:  # 5% 미만
            scores["저성장주"] += 2.0
        elif revenue_growth > 0.15:  # 15% 이상
            scores["고성장주"] += 2.0

        # 시가총액 기반 점수 (우량주 판단)
        market_cap = current_price_info.get("market_cap", 0) or 0
        if market_cap > 10_000_000_000_000:  # 10조원 이상
            scores["우량주"] += 1.5

        # PBR 기반 점수 (자산주 판단)
        pbr = financial_ratios.get("pb_ratio", 999) or 999
        if pbr < 1.0:
            scores["자산주"] += 2.0

        # ROE 기반 점수 (우량주 판단)
        roe = financial_ratios.get("return_on_equity", 0) or 0
        if roe > 0.10:  # 10% 이상
            scores["우량주"] += 1.0

        return scores

    def _calculate_final_confidence(
        self,
        ai_confidence: str,
        quantitative_scores: Dict[str, float],
        data_quality: str,
    ) -> str:
        """최종 신뢰도를 계산해요"""
        confidence_score = 0

        # AI 신뢰도 점수
        if ai_confidence == "높음":
            confidence_score += 3
        elif ai_confidence == "보통":
            confidence_score += 2
        else:
            confidence_score += 1

        # 정량적 검증 점수 추가
        max_quantitative_score = (
            max(quantitative_scores.values()) if quantitative_scores else 0
        )
        if max_quantitative_score >= 2.0:
            confidence_score += 2
        elif max_quantitative_score >= 1.0:
            confidence_score += 1

        # 데이터 품질 점수 추가
        if data_quality == "높음":
            confidence_score += 2
        elif data_quality == "보통":
            confidence_score += 1

        # 최종 신뢰도 결정
        if confidence_score >= 6:
            return "높음"
        elif confidence_score >= 4:
            return "보통"
        else:
            return "낮음"

    def _check_key_metrics(self, financial_data: Dict[str, Any]) -> Dict[str, bool]:
        """핵심 지표들이 사용 가능한지 확인해요"""
        financial_ratios = financial_data.get("financial_ratios", {})
        growth_metrics = financial_data.get("growth_metrics", {})
        current_price_info = financial_data.get("current_price_info", {})

        return {
            "current_price": current_price_info.get("current_price") is not None,
            "market_cap": current_price_info.get("market_cap") is not None,
            "pe_ratio": financial_ratios.get("pe_ratio") is not None,
            "pb_ratio": financial_ratios.get("pb_ratio") is not None,
            "revenue_growth": growth_metrics.get("revenue_growth") is not None,
            "roe": financial_ratios.get("return_on_equity") is not None,
        }

    def _format_large_number(self, number) -> str:
        """큰 숫자를 읽기 쉽게 포맷팅해요"""
        if not number or number == 0:
            return "N/A"

        if number >= 1_000_000_000_000:  # 1조 이상
            return f"{number/1_000_000_000_000:.1f}조"
        elif number >= 100_000_000:  # 1억 이상
            return f"{number/100_000_000:.1f}억"
        else:
            return f"{number:,}"

    def _format_percentage(self, ratio) -> str:
        """비율을 퍼센트로 포맷팅해요"""
        if ratio is None:
            return "N/A"
        return f"{ratio*100:.2f}%"

    async def step(self) -> str:
        """기본 step 함수 (호환성 유지용)"""
        return "Enhanced Stock Classifier는 classify_with_financial_data() 메서드를 사용해주세요."
