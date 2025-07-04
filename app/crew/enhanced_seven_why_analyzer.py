# -*- coding: utf-8 -*-
"""
향상된 7Why 분석 시스템 (데이터 소스 기반)

5Why를 7Why로 확장해서 더 깊은 원인 분석을 수행하는 시스템이에요!
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_openai import ChatOpenAI


class EnhancedSevenWhyAnalyzer:
    """
    향상된 7Why 분석 시스템

    5Why를 7Why로 확장해서 더 깊은 원인 분석을 수행해요!
    """

    def __init__(self):
        """향상된 7Why 분석 시스템 초기화"""

        # LLM 모델 설정
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.1,
            max_tokens=8000,  # 7Why로 확장되어 토큰 증가
        )

        # Memory 시스템 설정
        self.analysis_memory = ConversationBufferMemory(
            memory_key="seven_why_history",
            return_messages=True,
            max_token_limit=6000,  # 7Why로 확장되어 메모리 증가
        )

        # 데이터 소스별 분석 체인 생성
        self.financial_data_analyzer = self._create_financial_data_analyzer()
        self.market_data_analyzer = self._create_market_data_analyzer()
        self.competitor_data_analyzer = self._create_competitor_data_analyzer()
        self.web_search_analyzer = self._create_web_search_analyzer()
        self.seven_why_synthesizer = self._create_seven_why_synthesizer()

        print("✅ 향상된 7Why 분석 시스템 초기화 완료!")

    def _create_financial_data_analyzer(self) -> LLMChain:
        """재무 데이터 기반 7Why 원인 분석 체인 생성"""

        financial_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
당신은 재무 데이터를 기반으로 기업의 문제점을 분석하는 전문가입니다.
제공된 재무 데이터를 바탕으로 7Why 기법의 각 단계별 원인을 찾아주세요.

**📊 재무 데이터 분석 프레임워크**

**1. 수익성 지표 분석**
- 매출액, 영업이익, 순이익의 변화 추이
- 영업이익률, 순이익률의 변화
- ROE, ROA 등 수익성 지표 분석

**2. 성장성 지표 분석**
- 매출액 성장률, 이익 성장률
- 자산 성장률, 자본 성장률
- 성장 동력과 한계점 분석

**3. 안정성 지표 분석**
- 유동비율, 부채비율
- 이자보상배율, 현금흐름
- 재무 건전성 평가

**4. 효율성 지표 분석**
- 자산회전율, 재고회전율
- 매출채권회전율, 매입채무회전율
- 운영 효율성 평가

**📋 재무 데이터 기반 7Why 분석 형식**

**Why 1: 재무적 직접 원인**
- 현상: [구체적 재무 현상]
- 원인: [직접적 재무 원인]
- 근거: [구체적 재무 지표와 수치]
- 데이터 소스: [재무제표, 공시자료 등]

**Why 2: 운영적 원인**
- 현상: [Why 1의 재무 원인]
- 원인: [운영 프로세스, 비용 구조 등]
- 근거: [운영 지표, 비용 분석 등]
- 데이터 소스: [재무제표 세부 항목, 공시자료 등]

**Why 3: 조직적 원인**
- 현상: [Why 2의 운영 원인]
- 원인: [조직 구조, 의사결정 체계 등]
- 근거: [조직 지표, 의사결정 분석 등]
- 데이터 소스: [조직도, 의사결정 자료 등]

**Why 4: 전략적 원인**
- 현상: [Why 3의 조직 원인]
- 원인: [사업 전략, 투자 결정 등]
- 근거: [투자 계획, 사업 구조 등]
- 데이터 소스: [사업보고서, 투자계획서 등]

**Why 5: 구조적 원인**
- 현상: [Why 4의 전략적 원인]
- 원인: [산업 구조, 시장 구조 등]
- 근거: [산업 분석, 시장 구조 등]
- 데이터 소스: [산업 보고서, 시장 분석 등]

**Why 6: 환경적 원인**
- 현상: [Why 5의 구조적 원인]
- 원인: [거시경제, 글로벌 환경 등]
- 근거: [경제 지표, 글로벌 데이터 등]
- 데이터 소스: [경제 통계, 글로벌 보고서 등]

**Why 7: 근본적 원인**
- 현상: [Why 6의 환경적 원인]
- 원인: [사회적 변화, 기술적 변화 등]
- 근거: [사회 분석, 기술 동향 등]
- 데이터 소스: [사회 연구, 기술 보고서 등]
""",
                ),
                MessagesPlaceholder(variable_name="seven_why_history"),
                (
                    "human",
                    """
다음 재무 데이터를 바탕으로 7Why 기법으로 원인을 분석해주세요:

{analysis_request}

**7Why 분석 요청:**
1. 재무 데이터에서 관찰된 핵심 현상 파악
2. 각 Why 단계별로 구체적 재무 지표 기반 원인 분석
3. 모든 근거는 제공된 재무 데이터에서 도출
4. 데이터 소스 명시 (재무제표, 공시자료 등)
5. 7단계에 걸쳐 더 깊은 원인 분석 수행
""",
                ),
            ]
        )

        return LLMChain(
            llm=self.llm,
            prompt=financial_prompt,
            memory=self.analysis_memory,
            verbose=True,
        )

    def _create_market_data_analyzer(self) -> LLMChain:
        """시장 데이터 기반 7Why 원인 분석 체인 생성"""

        market_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
당신은 시장 데이터를 기반으로 기업의 시장 상황을 분석하는 전문가입니다.
제공된 시장 데이터를 바탕으로 7Why 기법의 각 단계별 원인을 찾아주세요.

**📈 시장 데이터 분석 프레임워크**

**1. 주가 및 가치 평가 분석**
- 현재 주가, 시가총액, PER, PBR
- 업계 평균과의 비교
- 할증/할인 요인 분석

**2. 거래량 및 유동성 분석**
- 일평균 거래량, 거래대금
- 외국인 지분율, 기관 투자자 비중
- 유동성 지표 분석

**3. 시장 성과 분석**
- 주요 지수 대비 성과
- 업계 평균 대비 성과
- 베타, 변동성 분석

**4. 투자자 심리 분석**
- 투자자 관심도, 뉴스 감정
- 분석가 의견, 목표가
- 시장 기대치 분석

**📋 시장 데이터 기반 7Why 분석 형식**

**Why 1: 시장적 직접 원인**
- 현상: [구체적 시장 현상]
- 원인: [직접적 시장 원인]
- 근거: [구체적 시장 지표와 수치]
- 데이터 소스: [주가 데이터, 거래량 데이터 등]

**Why 2: 투자자 행동 원인**
- 현상: [Why 1의 시장 원인]
- 원인: [투자자 심리, 기관 투자자 행동 등]
- 근거: [투자자 지표, 기관 투자자 데이터 등]
- 데이터 소스: [투자자 데이터, 기관 투자자 보고서 등]

**Why 3: 기업 실적 원인**
- 현상: [Why 2의 투자자 행동 원인]
- 원인: [실적 전망, 성장성 기대 등]
- 근거: [실적 예상, 성장성 지표 등]
- 데이터 소스: [실적 전망, 분석가 리포트 등]

**Why 4: 업계 환경 원인**
- 현상: [Why 3의 기업 실적 원인]
- 원인: [업계 동향, 경쟁 상황 등]
- 근거: [업계 데이터, 경쟁사 비교 등]
- 데이터 소스: [업계 보고서, 경쟁사 분석 등]

**Why 5: 구조적 원인**
- 현상: [Why 4의 업계 환경 원인]
- 원인: [시장 구조, 규제 환경 등]
- 근거: [시장 구조 분석, 규제 데이터 등]
- 데이터 소스: [시장 구조 보고서, 규제 자료 등]

**Why 6: 환경적 원인**
- 현상: [Why 5의 구조적 원인]
- 원인: [경기 상황, 글로벌 환경 등]
- 근거: [경기 지표, 글로벌 데이터 등]
- 데이터 소스: [경제 통계, 글로벌 보고서 등]

**Why 7: 근본적 원인**
- 현상: [Why 6의 환경적 원인]
- 원인: [사회적 변화, 기술적 변화 등]
- 근거: [사회 분석, 기술 동향 등]
- 데이터 소스: [사회 연구, 기술 보고서 등]
""",
                ),
                MessagesPlaceholder(variable_name="seven_why_history"),
                (
                    "human",
                    """
다음 시장 데이터를 바탕으로 7Why 기법으로 원인을 분석해주세요:

{analysis_request}

**7Why 분석 요청:**
1. 시장 데이터에서 관찰된 핵심 현상 파악
2. 각 Why 단계별로 구체적 시장 지표 기반 원인 분석
3. 모든 근거는 제공된 시장 데이터에서 도출
4. 데이터 소스 명시 (주가 데이터, 거래량 데이터 등)
5. 7단계에 걸쳐 더 깊은 원인 분석 수행
""",
                ),
            ]
        )

        return LLMChain(
            llm=self.llm,
            prompt=market_prompt,
            memory=self.analysis_memory,
            verbose=True,
        )

    def _create_competitor_data_analyzer(self) -> LLMChain:
        """경쟁사 데이터 기반 7Why 원인 분석 체인 생성"""

        competitor_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
당신은 경쟁사 데이터를 기반으로 기업의 경쟁 상황을 분석하는 전문가입니다.
제공된 경쟁사 데이터를 바탕으로 7Why 기법의 각 단계별 원인을 찾아주세요.

**🏆 경쟁사 데이터 분석 프레임워크**

**1. 경쟁사 재무 비교 분석**
- 매출액, 영업이익, 순이익 비교
- 수익성, 성장성, 안정성 지표 비교
- 상대적 우위/열위 분석

**2. 시장 점유율 및 포지셔닝 분석**
- 시장 점유율 비교
- 제품/서비스 포지셔닝
- 브랜드 가치 비교

**3. 경쟁 전략 분석**
- 비즈니스 모델 비교
- 투자 전략, R&D 투자
- 시장 진출 전략

**4. 경쟁 환경 분석**
- 업계 구조, 진입장벽
- 공급자/구매자 교섭력
- 대체재 위협

**📋 경쟁사 데이터 기반 7Why 분석 형식**

**Why 1: 경쟁적 직접 원인**
- 현상: [구체적 경쟁 현상]
- 원인: [직접적 경쟁 원인]
- 근거: [구체적 경쟁사 비교 데이터]
- 데이터 소스: [경쟁사 재무제표, 시장 점유율 데이터 등]

**Why 2: 전략적 원인**
- 현상: [Why 1의 경쟁 원인]
- 원인: [경쟁 전략, 비즈니스 모델 등]
- 근거: [전략 비교, 모델 분석 등]
- 데이터 소스: [전략 보고서, 비즈니스 모델 분석 등]

**Why 3: 운영적 원인**
- 현상: [Why 2의 전략적 원인]
- 원인: [운영 효율성, 비용 구조 등]
- 근거: [운영 지표 비교, 비용 분석 등]
- 데이터 소스: [운영 데이터, 비용 구조 분석 등]

**Why 4: 시장적 원인**
- 현상: [Why 3의 운영적 원인]
- 원인: [시장 환경, 고객 선호도 등]
- 근거: [시장 조사, 고객 데이터 등]
- 데이터 소스: [시장 조사 보고서, 고객 분석 등]

**Why 5: 구조적 원인**
- 현상: [Why 4의 시장적 원인]
- 원인: [산업 구조, 규제 환경 등]
- 근거: [산업 분석, 규제 데이터 등]
- 데이터 소스: [산업 보고서, 규제 자료 등]

**Why 6: 환경적 원인**
- 현상: [Why 5의 구조적 원인]
- 원인: [경기 상황, 글로벌 환경 등]
- 근거: [경기 지표, 글로벌 데이터 등]
- 데이터 소스: [경제 통계, 글로벌 보고서 등]

**Why 7: 근본적 원인**
- 현상: [Why 6의 환경적 원인]
- 원인: [사회적 변화, 기술적 변화 등]
- 근거: [사회 분석, 기술 동향 등]
- 데이터 소스: [사회 연구, 기술 보고서 등]
""",
                ),
                MessagesPlaceholder(variable_name="seven_why_history"),
                (
                    "human",
                    """
다음 경쟁사 데이터를 바탕으로 7Why 기법으로 원인을 분석해주세요:

{analysis_request}

**7Why 분석 요청:**
1. 경쟁사 데이터에서 관찰된 핵심 현상 파악
2. 각 Why 단계별로 구체적 경쟁사 비교 기반 원인 분석
3. 모든 근거는 제공된 경쟁사 데이터에서 도출
4. 데이터 소스 명시 (경쟁사 재무제표, 시장 점유율 등)
5. 7단계에 걸쳐 더 깊은 원인 분석 수행
""",
                ),
            ]
        )

        return LLMChain(
            llm=self.llm,
            prompt=competitor_prompt,
            memory=self.analysis_memory,
            verbose=True,
        )

    def _create_web_search_analyzer(self) -> LLMChain:
        """웹 검색 데이터 기반 7Why 원인 분석 체인 생성"""

        web_search_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
당신은 웹 검색 데이터를 기반으로 기업의 외부 환경을 분석하는 전문가입니다.
제공된 웹 검색 데이터를 바탕으로 7Why 기법의 각 단계별 원인을 찾아주세요.

**🌐 웹 검색 데이터 분석 프레임워크**

**1. 뉴스 및 미디어 분석**
- 기업 관련 뉴스, 보도자료
- 분석가 리포트, 투자자 의견
- 미디어 감정 분석

**2. 산업 동향 및 정책 분석**
- 업계 동향, 기술 변화
- 정책 변화, 규제 환경
- 시장 전망, 트렌드

**3. 글로벌 환경 분석**
- 글로벌 시장 동향
- 환율, 원자재 가격
- 지정학적 리스크

**4. ESG 및 지속가능성 분석**
- 환경, 사회, 지배구조
- ESG 평가, 지속가능성 전략
- 이해관계자 관점

**📋 웹 검색 데이터 기반 7Why 분석 형식**

**Why 1: 외부적 직접 원인**
- 현상: [구체적 외부 현상]
- 원인: [직접적 외부 원인]
- 근거: [구체적 뉴스, 보도자료 등]
- 데이터 소스: [뉴스 기사, 보도자료, 분석가 리포트 등]

**Why 2: 환경적 원인**
- 현상: [Why 1의 외부 원인]
- 원인: [환경 변화, 정책 변화 등]
- 근거: [정책 자료, 환경 분석 등]
- 데이터 소스: [정책 문서, 환경 보고서 등]

**Why 3: 구조적 원인**
- 현상: [Why 2의 환경적 원인]
- 원인: [산업 구조, 시장 구조 등]
- 근거: [산업 분석, 시장 조사 등]
- 데이터 소스: [산업 보고서, 시장 조사 자료 등]

**Why 4: 거시적 원인**
- 현상: [Why 3의 구조적 원인]
- 원인: [경기 상황, 글로벌 환경 등]
- 근거: [경제 지표, 글로벌 데이터 등]
- 데이터 소스: [경제 통계, 글로벌 보고서 등]

**Why 5: 기술적 원인**
- 현상: [Why 4의 거시적 원인]
- 원인: [기술 변화, 혁신 등]
- 근거: [기술 동향, 혁신 분석 등]
- 데이터 소스: [기술 보고서, 혁신 연구 등]

**Why 6: 사회적 원인**
- 현상: [Why 5의 기술적 원인]
- 원인: [사회적 변화, 문화적 변화 등]
- 근거: [사회 분석, 문화 연구 등]
- 데이터 소스: [사회 연구, 문화 보고서 등]

**Why 7: 근본적 원인**
- 현상: [Why 6의 사회적 원인]
- 원인: [문명사적 변화, 인구학적 변화 등]
- 근거: [문명사 연구, 인구학 분석 등]
- 데이터 소스: [문명사 연구, 인구학 보고서 등]
""",
                ),
                MessagesPlaceholder(variable_name="seven_why_history"),
                (
                    "human",
                    """
다음 웹 검색 데이터를 바탕으로 7Why 기법으로 원인을 분석해주세요:

{analysis_request}

**7Why 분석 요청:**
1. 웹 검색 데이터에서 관찰된 핵심 현상 파악
2. 각 Why 단계별로 구체적 뉴스/보고서 기반 원인 분석
3. 모든 근거는 제공된 웹 검색 데이터에서 도출
4. 데이터 소스 명시 (뉴스 기사, 분석가 리포트 등)
5. 7단계에 걸쳐 더 깊은 원인 분석 수행
""",
                ),
            ]
        )

        return LLMChain(
            llm=self.llm,
            prompt=web_search_prompt,
            memory=self.analysis_memory,
            verbose=True,
        )

    def _create_seven_why_synthesizer(self) -> LLMChain:
        """데이터 소스별 7Why 분석 결과를 종합하는 체인 생성"""

        synthesis_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
당신은 다양한 데이터 소스의 7Why 분석 결과를 종합하는 전문가입니다.
재무, 시장, 경쟁사, 웹 검색 데이터의 분석 결과를 통합해서
최종적인 7Why 분석 보고서를 작성해주세요.

**🔗 데이터 소스 통합 분석 프레임워크**

**1. 데이터 소스별 일치점/차이점 분석**
- 각 데이터 소스에서 도출된 원인의 일치성
- 데이터 소스별 차이점과 그 이유
- 신뢰도가 높은 데이터 소스 식별

**2. 종합적 7Why 분석**
- 모든 데이터 소스를 종합한 최종 7Why
- 각 단계별 가장 신뢰할 수 있는 근거 선택
- 데이터 소스 간 상호 검증

**3. 근거의 신뢰도 평가**
- 각 근거의 데이터 소스 신뢰도
- 데이터의 최신성과 정확성
- 근거의 구체성과 객관성

**📋 종합 7Why 분석 형식**

**데이터 소스별 분석 요약:**

**재무 데이터 기반 분석:**
- 핵심 원인: [재무 데이터에서 도출된 주요 원인]
- 신뢰도: [높음/중간/낮음]
- 근거 품질: [구체적/일반적/부족]

**시장 데이터 기반 분석:**
- 핵심 원인: [시장 데이터에서 도출된 주요 원인]
- 신뢰도: [높음/중간/낮음]
- 근거 품질: [구체적/일반적/부족]

**경쟁사 데이터 기반 분석:**
- 핵심 원인: [경쟁사 데이터에서 도출된 주요 원인]
- 신뢰도: [높음/중간/낮음]
- 근거 품질: [구체적/일반적/부족]

**웹 검색 데이터 기반 분석:**
- 핵심 원인: [웹 검색 데이터에서 도출된 주요 원인]
- 신뢰도: [높음/중간/낮음]
- 근거 품질: [구체적/일반적/부족]

**종합 7Why 분석:**

**Why 1: 직접적 원인**
- 현상: [통합된 현상]
- 원인: [통합된 직접 원인]
- 근거: [가장 신뢰할 수 있는 근거]
- 데이터 소스: [주요 데이터 소스]
- 신뢰도: [높음/중간/낮음]

**Why 2: 시스템적 원인**
- 현상: [Why 1의 원인]
- 원인: [통합된 시스템적 원인]
- 근거: [가장 신뢰할 수 있는 근거]
- 데이터 소스: [주요 데이터 소스]
- 신뢰도: [높음/중간/낮음]

**Why 3: 조직적 원인**
- 현상: [Why 2의 원인]
- 원인: [통합된 조직적 원인]
- 근거: [가장 신뢰할 수 있는 근거]
- 데이터 소스: [주요 데이터 소스]
- 신뢰도: [높음/중간/낮음]

**Why 4: 전략적 원인**
- 현상: [Why 3의 원인]
- 원인: [통합된 전략적 원인]
- 근거: [가장 신뢰할 수 있는 근거]
- 데이터 소스: [주요 데이터 소스]
- 신뢰도: [높음/중간/낮음]

**Why 5: 구조적 원인**
- 현상: [Why 4의 원인]
- 원인: [통합된 구조적 원인]
- 근거: [가장 신뢰할 수 있는 근거]
- 데이터 소스: [주요 데이터 소스]
- 신뢰도: [높음/중간/낮음]

**Why 6: 환경적 원인**
- 현상: [Why 5의 원인]
- 원인: [통합된 환경적 원인]
- 근거: [가장 신뢰할 수 있는 근거]
- 데이터 소스: [주요 데이터 소스]
- 신뢰도: [높음/중간/낮음]

**Why 7: 근본적 원인**
- 현상: [Why 6의 원인]
- 원인: [통합된 근본적 원인]
- 근거: [가장 신뢰할 수 있는 근거]
- 데이터 소스: [주요 데이터 소스]
- 신뢰도: [높음/중간/낮음]

**최종 근본 원인 요약:**
- 종합적 근본 원인: [최종 도출된 근본 원인]
- 신뢰도: [전체 분석의 신뢰도]
- 주요 근거: [가장 중요한 3-5개 근거]
- 데이터 소스: [주요 데이터 소스들]
- 7Why 확장 효과: [5Why 대비 추가된 깊이와 통찰]
""",
                ),
                MessagesPlaceholder(variable_name="seven_why_history"),
                (
                    "human",
                    """
다음 데이터 소스별 7Why 분석 결과를 종합해서 최종 분석 보고서를 작성해주세요:

{analysis_request}

**종합 분석 요청:**
1. 데이터 소스별 분석 결과 비교
2. 신뢰도가 높은 근거 중심으로 통합
3. 최종 7Why 분석 도출
4. 근거의 신뢰도와 데이터 소스 명시
5. 5Why 대비 7Why의 추가 가치 평가
""",
                ),
            ]
        )

        return LLMChain(
            llm=self.llm,
            prompt=synthesis_prompt,
            memory=self.analysis_memory,
            verbose=True,
        )

    def _create_integrated_7why_analyzer(self) -> LLMChain:
        """
        전문가 분석 텍스트와 실제 데이터를 통합해서 7Why 분석을 수행하는 체인을 만들어요
        입력값: expert_analysis_text(전문가 분석), financial_data, market_data, competitor_data, web_search_data
        반환값: 7Why 분석 결과(각 단계별로 실제 데이터 근거 포함)
        """
        integrated_7why_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
// 이 프롬프트는 전문가의 분석 내용을 7Why로 심층 분석하는 역할을 해요
// (예: 분석 내용 = "삼성전자의 영업이익이 감소한 것은 반도체 부문의 수익성 악화 때문이다.")

당신은 7Why 분석 전문가입니다.
아래의 통합된 데이터에서 전문가 분석 내용을 '현상'으로 삼아 7Why 기법으로 근본 원인을 단계별로 분석하세요.

{integrated_data}

각 단계별로 반드시 실제 데이터에서 구체적인 수치, 지표, 뉴스, 리포트 등을 근거로 들어주세요.

[출력 예시]
Why 1: (현상, 원인, 근거, 데이터 소스)
Why 2: ...
...
Why 7: ...
""",
                ),
                MessagesPlaceholder(variable_name="seven_why_history"),
                (
                    "human",
                    """
아래 통합된 데이터를 바탕으로 7Why 분석을 해주세요.

{integrated_data}

**7Why 분석 요청:**
1. 전문가 분석 내용을 현상으로 삼아 Why 1부터 Why 7까지 단계별로 원인 분석
2. 각 단계별로 반드시 실제 데이터에서 구체적 근거(수치, 지표, 뉴스 등)를 인용
3. 데이터 소스(재무, 시장, 경쟁사, 웹 등) 명시
4. 7단계에 걸쳐 더 깊은 원인 분석 수행
""",
                ),
            ]
        )
        return LLMChain(
            llm=self.llm,
            prompt=integrated_7why_prompt,
            memory=self.analysis_memory,
            verbose=True,
        )

    def perform_integrated_7why_analysis(
        self,
        expert_analysis_text: str,
        financial_data: str,
        market_data: str,
        competitor_data: str,
        web_search_data: str = "",
    ) -> Dict[str, Any]:
        """
        전문가 분석 텍스트와 실제 데이터를 통합해서 7Why 분석을 실행하는 함수에요
        Args:
            expert_analysis_text: 전문가가 작성한 분석 텍스트(예: "삼성전자의 영업이익이 감소한 것은...")
            financial_data: 재무 데이터
            market_data: 시장 데이터
            competitor_data: 경쟁사 데이터
            web_search_data: 웹 검색 데이터(선택)
        Returns:
            Dict: 7Why 분석 결과
        """
        print("🔍 전문가 분석 텍스트 기반 7Why 분석 시작!")
        print("=" * 60)
        try:
            integrated_7why_chain = self._create_integrated_7why_analyzer()

            # LangChain Memory 오류 해결: 여러 입력 변수를 하나의 통합된 문자열로 합쳐요
            # (Memory는 하나의 입력 변수만 처리할 수 있어서 이런 방식으로 해결해요)
            integrated_input = f"""
전문가 분석 내용: {expert_analysis_text}

재무 데이터: {financial_data}

시장 데이터: {market_data}

경쟁사 데이터: {competitor_data}

웹 검색 데이터: {web_search_data}
"""

            result = integrated_7why_chain.run({"integrated_data": integrated_input})
            print("🎉 전문가 분석 텍스트 기반 7Why 분석 완료!")
            print("=" * 60)
            return {
                "timestamp": datetime.now().isoformat(),
                "analysis_method": "Expert Prompt + Data 기반 7Why 통합 분석",
                "integrated_7why_analysis": result,
                "expert_analysis_text": expert_analysis_text,
                "data_sources_used": {
                    "financial_data": "재무제표, 공시자료",
                    "market_data": "주가 데이터, 거래량 데이터",
                    "competitor_data": "경쟁사 재무제표, 시장 점유율",
                    "web_search_data": (
                        "뉴스 기사, 분석가 리포트" if web_search_data else "미사용"
                    ),
                },
                "analysis_depth": "7단계 심층 분석 (전문가 프롬프트 기반)",
            }
        except Exception as e:
            print(f"❌ 전문가 분석 텍스트 기반 7Why 분석 실패: {e}")
            import traceback

            traceback.print_exc()
            return {"error": str(e)}

    def perform_enhanced_seven_why_analysis(
        self,
        company_name: str,
        sector_name: str,
        financial_data: str,
        market_data: str,
        competitor_data: str,
        web_search_data: str = "",
    ) -> Dict[str, Any]:
        """
        향상된 7Why 분석 프로세스 실행

        Args:
            company_name: 분석 대상 회사명
            sector_name: 섹터명
            financial_data: 재무 데이터
            market_data: 시장 데이터
            competitor_data: 경쟁사 데이터
            web_search_data: 웹 검색 데이터 (선택사항)

        Returns:
            Dict: 향상된 7Why 분석 결과
        """

        print(f"🔍 {company_name} 향상된 7Why 분석 프로세스 시작!")
        print("=" * 60)

        try:
            # 1단계: 재무 데이터 기반 7Why 분석
            print("💰 1단계: 재무 데이터 기반 7Why 분석 중...")

            analysis_request = f"""
**기업명:** {company_name}
**섹터:** {sector_name}
**재무 데이터:**
{financial_data}
"""
            financial_analysis = self.financial_data_analyzer.run(
                {"analysis_request": analysis_request}
            )

            print("✅ 1단계 완료: 재무 데이터 분석")
            print("-" * 40)

            # 2단계: 시장 데이터 기반 7Why 분석
            print("📈 2단계: 시장 데이터 기반 7Why 분석 중...")

            analysis_request = f"""
**기업명:** {company_name}
**섹터:** {sector_name}
**시장 데이터:**
{market_data}
"""
            market_analysis = self.market_data_analyzer.run(
                {"analysis_request": analysis_request}
            )

            print("✅ 2단계 완료: 시장 데이터 분석")
            print("-" * 40)

            # 3단계: 경쟁사 데이터 기반 7Why 분석
            print("🏆 3단계: 경쟁사 데이터 기반 7Why 분석 중...")

            analysis_request = f"""
**기업명:** {company_name}
**섹터:** {sector_name}
**경쟁사 데이터:**
{competitor_data}
"""
            competitor_analysis = self.competitor_data_analyzer.run(
                {"analysis_request": analysis_request}
            )

            print("✅ 3단계 완료: 경쟁사 데이터 분석")
            print("-" * 40)

            # 4단계: 웹 검색 데이터 기반 7Why 분석 (선택사항)
            web_search_analysis = ""
            if web_search_data:
                print("🌐 4단계: 웹 검색 데이터 기반 7Why 분석 중...")

                analysis_request = f"""
**기업명:** {company_name}
**섹터:** {sector_name}
**웹 검색 데이터:**
{web_search_data}
"""
                web_search_analysis = self.web_search_analyzer.run(
                    {"analysis_request": analysis_request}
                )

                print("✅ 4단계 완료: 웹 검색 데이터 분석")
                print("-" * 40)

            # 5단계: 데이터 소스별 분석 결과 종합
            print("🔗 5단계: 데이터 소스별 분석 결과 종합 중...")

            analysis_request = f"""
**재무 데이터 기반 분석:**
{financial_analysis}

**시장 데이터 기반 분석:**
{market_analysis}

**경쟁사 데이터 기반 분석:**
{competitor_analysis}

**웹 검색 데이터 기반 분석:**
{web_search_analysis}
"""
            synthesis_result = self.seven_why_synthesizer.run(
                {"analysis_request": analysis_request}
            )

            print("✅ 5단계 완료: 종합 분석")
            print("-" * 40)

            # 최종 결과 정리
            result = {
                "timestamp": datetime.now().isoformat(),
                "company_name": company_name,
                "sector_name": sector_name,
                "analysis_method": "Enhanced 7Why Analysis (Data Source Based)",
                "financial_based_analysis": financial_analysis,
                "market_based_analysis": market_analysis,
                "competitor_based_analysis": competitor_analysis,
                "web_search_based_analysis": web_search_analysis,
                "synthesis_analysis": synthesis_result,
                "data_sources_used": {
                    "financial_data": "재무제표, 공시자료",
                    "market_data": "주가 데이터, 거래량 데이터",
                    "competitor_data": "경쟁사 재무제표, 시장 점유율",
                    "web_search_data": (
                        "뉴스 기사, 분석가 리포트" if web_search_data else "미사용"
                    ),
                },
                "analysis_depth": "7단계 심층 분석 (5Why 확장)",
                "additional_insights": "Why 6(환경적 원인), Why 7(근본적 원인) 추가",
            }

            print("🎉 향상된 7Why 분석 프로세스 완료!")
            print("=" * 60)

            return result

        except Exception as e:
            print(f"❌ 향상된 7Why 분석 프로세스 실패: {e}")
            import traceback

            traceback.print_exc()
            return {"error": str(e)}

    def save_enhanced_seven_why_result(self, filepath: str, result: Dict[str, Any]):
        """향상된 7Why 분석 결과를 파일로 저장"""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"✅ 향상된 7Why 분석 결과 저장 완료: {filepath}")
        except Exception as e:
            print(f"❌ 향상된 7Why 분석 결과 저장 실패: {e}")

    def get_analysis_summary(self) -> Dict[str, Any]:
        """분석 요약 정보 반환"""
        memory_vars = self.analysis_memory.load_memory_variables({})

        return {
            "analysis_history_size": len(memory_vars.get("seven_why_history", [])),
            "last_analysis": (
                memory_vars.get("seven_why_history", [])[-1]
                if memory_vars.get("seven_why_history")
                else None
            ),
        }
