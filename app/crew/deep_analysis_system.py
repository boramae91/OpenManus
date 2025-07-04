# -*- coding: utf-8 -*-
"""
심층 분석 시스템 (CoT + 5Why + Memory 기반)

Chain of Thought와 맥킨지 5Why 기법을 결합해서
시니어 애널리스트 수준의 심층 분석을 수행하는 시스템이에요!
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from langchain.chains import LLMChain, SequentialChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_openai import ChatOpenAI


class DeepAnalysisSystem:
    """
    심층 분석 시스템

    CoT(Chain of Thought) + 5Why 기법 + Memory 기능을 결합해서
    시니어 애널리스트 수준의 심층 분석을 수행해요!
    """

    def __init__(self):
        """심층 분석 시스템 초기화"""

        # LLM 모델 설정
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.1,  # 일관된 분석을 위해 낮은 값
            max_tokens=8000,  # 심층 분석을 위해 충분한 토큰
        )

        # Memory 시스템 설정
        self.conversation_memory = ConversationBufferMemory(
            memory_key="analysis_history",
            return_messages=True,
            max_token_limit=6000,  # 대화 이력 저장
        )

        self.summary_memory = ConversationBufferMemory(
            memory_key="analysis_summary",
            return_messages=True,
            max_token_limit=4000,  # 분석 요약 저장
        )

        # 분석 체인들 생성
        self.cot_analyzer = self._create_cot_analyzer()
        self.five_why_analyzer = self._create_five_why_analyzer()
        self.root_cause_analyzer = self._create_root_cause_analyzer()
        self.implication_analyzer = self._create_implication_analyzer()

        print("✅ 심층 분석 시스템 초기화 완료!")

    def _create_cot_analyzer(self) -> LLMChain:
        """CoT 기반 1차 분석 체인 생성"""

        cot_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
당신은 시니어 애널리스트입니다. Chain of Thought(CoT) 기법을 사용해서 기업 분석을 수행해주세요.

**🧠 Chain of Thought 분석 프레임워크**

**1단계: 데이터 수집 및 정리**
- 재무 데이터, 시장 데이터, 경쟁사 데이터를 체계적으로 정리
- 각 데이터의 출처와 신뢰성 평가
- 데이터 간의 상관관계 파악

**2단계: 패턴 인식 및 트렌드 분석**
- 3-5년간의 데이터 트렌드 분석
- 계절성, 순환성, 구조적 변화 구분
- 업계 평균과의 비교 분석

**3단계: 원인 분석 및 가설 설정**
- 관찰된 패턴의 근본 원인 추정
- 내부 요인(경영, 전략, 구조) vs 외부 요인(시장, 경쟁, 규제) 구분
- 다중 가설 설정 및 우선순위 부여

**4단계: 검증 및 분석**
- 각 가설에 대한 증거 수집
- 통계적 검증 및 논리적 일관성 확인
- 대안 시나리오 고려

**5단계: 결론 도출**
- 가장 설득력 있는 가설 선택
- 불확실성과 리스크 요인 명시
- 투자 시사점 도출

**📋 CoT 분석 형식**

**관찰된 현상:**
- 구체적 수치와 데이터 제시

**1차 추론 (패턴 인식):**
- 이 데이터가 무엇을 의미하는가?
- 어떤 패턴이나 트렌드가 보이는가?

**2차 추론 (원인 분석):**
- 이 패턴의 근본 원인은 무엇인가?
- 내부/외부 요인 중 어떤 것이 주도적인가?

**3차 추론 (가설 검증):**
- 이 원인이 맞다면 어떤 증거가 있어야 하는가?
- 실제로 그런 증거가 있는가?

**4차 추론 (시사점):**
- 이 분석이 투자 판단에 어떤 의미가 있는가?
- 어떤 리스크와 기회가 있는가?

**최종 결론:**
- 종합적 분석 결과
- 투자 의견의 근거
""",
                ),
                MessagesPlaceholder(variable_name="analysis_history"),
                (
                    "human",
                    """
다음 기업에 대해 Chain of Thought 기법으로 심층 분석을 수행해주세요:

{integrated_data}

**CoT 분석 요청:**
1. 관찰된 현상부터 시작해서 단계별 추론
2. 각 단계에서 구체적 근거 제시
3. 최종 결론과 투자 시사점 도출
""",
                ),
            ]
        )

        return LLMChain(
            llm=self.llm,
            prompt=cot_prompt,
            memory=self.conversation_memory,
            verbose=True,
        )

    def _create_five_why_analyzer(self) -> LLMChain:
        """5Why 기법 기반 심층 분석 체인 생성"""

        five_why_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
당신은 맥킨지 5Why 기법을 활용한 심층 분석 전문가입니다.
CoT 분석 결과를 바탕으로 5Why 기법으로 근본 원인을 찾아주세요.

**🔍 5Why 기법 분석 프레임워크**

**Why 1: 직접적 원인**
- 관찰된 현상의 직접적 원인은 무엇인가?
- 즉시 확인 가능한 요인들

**Why 2: 시스템적 원인**
- Why 1의 원인은 무엇 때문인가?
- 프로세스, 시스템, 구조적 요인

**Why 3: 조직적 원인**
- Why 2의 원인은 무엇 때문인가?
- 경영진, 조직문화, 의사결정 구조

**Why 4: 전략적 원인**
- Why 3의 원인은 무엇 때문인가?
- 비즈니스 모델, 전략적 선택, 시장 포지셔닝

**Why 5: 근본적 원인**
- Why 4의 원인은 무엇 때문인가?
- 산업 구조, 시장 환경, 규제, 기술 변화 등

**📋 5Why 분석 형식**

**관찰된 현상:**
- CoT 분석에서 도출된 핵심 현상

**Why 1: 직접적 원인**
- 현상: [구체적 현상]
- 원인: [직접적 원인]
- 근거: [증거와 데이터]

**Why 2: 시스템적 원인**
- 현상: [Why 1의 원인]
- 원인: [시스템적 원인]
- 근거: [증거와 데이터]

**Why 3: 조직적 원인**
- 현상: [Why 2의 원인]
- 원인: [조직적 원인]
- 근거: [증거와 데이터]

**Why 4: 전략적 원인**
- 현상: [Why 3의 원인]
- 원인: [전략적 원인]
- 근거: [증거와 데이터]

**Why 5: 근본적 원인**
- 현상: [Why 4의 원인]
- 원인: [근본적 원인]
- 근거: [증거와 데이터]

**근본 원인 요약:**
- 5단계 분석을 통해 도출된 최종 근본 원인
""",
                ),
                MessagesPlaceholder(variable_name="analysis_history"),
                (
                    "human",
                    """
다음 CoT 분석 결과를 바탕으로 5Why 기법으로 근본 원인을 분석해주세요:

**CoT 분석 결과:**
{cot_analysis_result}

**5Why 분석 요청:**
1. CoT에서 도출된 핵심 현상부터 시작
2. 5단계에 걸쳐 단계별 원인 분석
3. 각 단계에서 구체적 근거 제시
4. 최종 근본 원인 도출
""",
                ),
            ]
        )

        return LLMChain(
            llm=self.llm,
            prompt=five_why_prompt,
            memory=self.conversation_memory,
            verbose=True,
        )

    def _create_root_cause_analyzer(self) -> LLMChain:
        """근본 원인 종합 분석 체인 생성"""

        root_cause_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
당신은 근본 원인 분석 전문가입니다.
CoT와 5Why 분석 결과를 종합해서 근본 원인을 체계적으로 정리해주세요.

**🎯 근본 원인 분석 프레임워크**

**1. 다층적 원인 구조**
- 직접 원인 (Immediate Cause)
- 근본 원인 (Root Cause)
- 구조적 원인 (Structural Cause)
- 환경적 원인 (Environmental Cause)

**2. 원인 간 상호작용**
- 각 원인 간의 인과관계
- 순환적 피드백 루프
- 승수 효과 (Multiplier Effect)

**3. 원인의 지속성과 변화 가능성**
- 일시적 vs 구조적 원인
- 내부 통제 가능 vs 외부 의존적
- 변화의 난이도와 시간

**📋 근본 원인 분석 형식**

**다층적 원인 구조:**

**직접 원인:**
- 즉시 관찰 가능한 원인
- 영향도: [높음/중간/낮음]
- 통제 가능성: [내부/외부]

**근본 원인:**
- 5Why 분석을 통해 도출된 핵심 원인
- 영향도: [높음/중간/낮음]
- 통제 가능성: [내부/외부]

**구조적 원인:**
- 조직, 시스템, 프로세스 수준의 원인
- 영향도: [높음/중간/낮음]
- 통제 가능성: [내부/외부]

**환경적 원인:**
- 시장, 규제, 기술, 경쟁 환경의 원인
- 영향도: [높음/중간/낮음]
- 통제 가능성: [내부/외부]

**원인 간 상호작용:**
- 각 원인 간의 관계와 영향
- 순환적 패턴이나 승수 효과

**변화 가능성 평가:**
- 각 원인의 변화 난이도
- 예상 변화 시간
- 변화를 위한 필요 조건
""",
                ),
                MessagesPlaceholder(variable_name="analysis_history"),
                (
                    "human",
                    """
다음 CoT와 5Why 분석 결과를 종합해서 근본 원인을 체계적으로 분석해주세요:

{integrated_analysis}

**근본 원인 분석 요청:**
1. 다층적 원인 구조로 정리
2. 원인 간 상호작용 분석
3. 변화 가능성 평가
4. 종합적 근본 원인 도출
""",
                ),
            ]
        )

        return LLMChain(
            llm=self.llm,
            prompt=root_cause_prompt,
            memory=self.conversation_memory,
            verbose=True,
        )

    def _create_implication_analyzer(self) -> LLMChain:
        """시사점 및 투자 의견 도출 체인 생성"""

        implication_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
당신은 투자 시사점 분석 전문가입니다.
근본 원인 분석 결과를 바탕으로 구체적인 투자 시사점과 전략적 제언을 도출해주세요.

**💡 시사점 분석 프레임워크**

**1. 투자 가치 평가**
- 현재 가치 vs 내재 가치
- 리스크 대비 수익률
- 투자 기간별 전망

**2. 시나리오별 분석**
- 낙관 시나리오 (근본 원인 개선)
- 기본 시나리오 (현재 추세 유지)
- 비관 시나리오 (근본 원인 악화)

**3. 전략적 제언**
- 단기 전략 (1년 이내)
- 중기 전략 (1-3년)
- 장기 전략 (3년 이상)

**4. 리스크 관리**
- 주요 리스크 요인
- 리스크 완화 방안
- 모니터링 지표

**📋 시사점 분석 형식**

**투자 가치 평가:**

**현재 가치 vs 내재 가치:**
- 현재 주가: [구체적 수치]
- 내재 가치: [구체적 수치]
- 할증/할인율: [구체적 수치]
- 근거: [가치 평가 방법론]

**리스크 대비 수익률:**
- 예상 수익률: [구체적 수치]
- 주요 리스크: [구체적 리스크]
- 리스크 대비 수익률: [높음/중간/낮음]

**시나리오별 분석:**

**낙관 시나리오 (확률: XX%):**
- 전제조건: [근본 원인 개선 조건]
- 예상 결과: [구체적 수치]
- 투자 의견: [매수/중립/매도]

**기본 시나리오 (확률: XX%):**
- 전제조건: [현재 추세 유지]
- 예상 결과: [구체적 수치]
- 투자 의견: [매수/중립/매도]

**비관 시나리오 (확률: XX%):**
- 전제조건: [근본 원인 악화 조건]
- 예상 결과: [구체적 수치]
- 투자 의견: [매수/중립/매도]

**전략적 제언:**

**단기 전략 (1년 이내):**
- 핵심 액션: [구체적 행동]
- 기대 효과: [구체적 결과]
- 실행 조건: [필요 조건]

**중기 전략 (1-3년):**
- 핵심 액션: [구체적 행동]
- 기대 효과: [구체적 결과]
- 실행 조건: [필요 조건]

**장기 전략 (3년 이상):**
- 핵심 액션: [구체적 행동]
- 기대 효과: [구체적 결과]
- 실행 조건: [필요 조건]

**리스크 관리:**

**주요 리스크 요인:**
- [리스크 1]: [발생 확률, 영향도]
- [리스크 2]: [발생 확률, 영향도]
- [리스크 3]: [발생 확률, 영향도]

**리스크 완화 방안:**
- [리스크 1] 완화: [구체적 방안]
- [리스크 2] 완화: [구체적 방안]
- [리스크 3] 완화: [구체적 방안]

**모니터링 지표:**
- [지표 1]: [기준값, 모니터링 주기]
- [지표 2]: [기준값, 모니터링 주기]
- [지표 3]: [기준값, 모니터링 주기]

**최종 투자 의견:**
- 종합 의견: [매수/중립/매도]
- 목표가: [구체적 수치]
- 투자 기간: [구체적 기간]
- 근거: [핵심 근거 요약]
""",
                ),
                MessagesPlaceholder(variable_name="analysis_history"),
                (
                    "human",
                    """
다음 근본 원인 분석 결과를 바탕으로 투자 시사점과 전략적 제언을 도출해주세요:

**근본 원인 분석 결과:**
{root_cause_analysis_result}

**시사점 분석 요청:**
1. 투자 가치 평가 (현재 vs 내재 가치)
2. 시나리오별 분석 (낙관/기본/비관)
3. 전략적 제언 (단기/중기/장기)
4. 리스크 관리 방안
5. 최종 투자 의견 도출
""",
                ),
            ],
        )

        return LLMChain(
            llm=self.llm,
            prompt=implication_prompt,
            memory=self.conversation_memory,
            verbose=True,
        )

    def perform_deep_analysis(
        self,
        company_name: str,
        sector_name: str,
        financial_data: str,
        market_data: str,
        competitor_data: str,
    ) -> Dict[str, Any]:
        """
        심층 분석 프로세스 실행

        Args:
            company_name: 분석 대상 회사명
            sector_name: 섹터명
            financial_data: 재무 데이터
            market_data: 시장 데이터
            competitor_data: 경쟁사 데이터

        Returns:
            Dict: 심층 분석 결과
        """

        print(f"🚀 {company_name} 심층 분석 프로세스 시작!")
        print("=" * 60)

        try:
            # 1단계: CoT 기반 1차 분석
            print("🧠 1단계: Chain of Thought 기반 1차 분석 중...")

            # LangChain Memory 오류 해결: 여러 입력 변수를 하나의 통합된 문자열로 합쳐요
            # (Memory는 하나의 입력 변수만 처리할 수 있어서 이런 방식으로 해결해요)
            integrated_input = f"""
분석 대상: {company_name}
섹터: {sector_name}
재무 데이터: {financial_data}
시장 데이터: {market_data}
경쟁사 정보: {competitor_data}
"""

            cot_result = self.cot_analyzer.run({"integrated_data": integrated_input})

            print("✅ 1단계 완료: CoT 분석")
            print("-" * 40)

            # 2단계: 5Why 기법 심층 분석
            print("🔍 2단계: 5Why 기법 심층 분석 중...")

            five_why_result = self.five_why_analyzer.run(
                {"cot_analysis_result": cot_result}
            )

            print("✅ 2단계 완료: 5Why 분석")
            print("-" * 40)

            # 3단계: 근본 원인 종합 분석
            print("🎯 3단계: 근본 원인 종합 분석 중...")

            # LangChain Memory 오류 해결: 여러 입력 변수를 하나의 통합된 문자열로 합쳐요
            integrated_analysis_input = f"""
CoT 분석 결과: {cot_result}

5Why 분석 결과: {five_why_result}
"""

            root_cause_result = self.root_cause_analyzer.run(
                {"integrated_analysis": integrated_analysis_input}
            )

            print("✅ 3단계 완료: 근본 원인 분석")
            print("-" * 40)

            # 4단계: 시사점 및 투자 의견 도출
            print("💡 4단계: 시사점 및 투자 의견 도출 중...")

            implication_result = self.implication_analyzer.run(
                {"root_cause_analysis_result": root_cause_result}
            )

            print("✅ 4단계 완료: 시사점 분석")
            print("-" * 40)

            # Memory에 분석 요약 저장
            self.summary_memory.save_context(
                {"input": f"{company_name} 심층 분석"},
                {
                    "output": f"CoT: {cot_result[:200]}... | 5Why: {five_why_result[:200]}... | 근본원인: {root_cause_result[:200]}... | 시사점: {implication_result[:200]}..."
                },
            )

            # 결과 정리
            result = {
                "timestamp": datetime.now().isoformat(),
                "company_name": company_name,
                "sector_name": sector_name,
                "analysis_method": "CoT + 5Why + Memory",
                "cot_analysis": cot_result,
                "five_why_analysis": five_why_result,
                "root_cause_analysis": root_cause_result,
                "implication_analysis": implication_result,
                "memory_context": {
                    "conversation_history": self.conversation_memory.load_memory_variables(
                        {}
                    ),
                    "analysis_summary": self.summary_memory.load_memory_variables({}),
                },
            }

            print("🎉 심층 분석 프로세스 완료!")
            print("=" * 60)

            return result

        except Exception as e:
            print(f"❌ 심층 분석 프로세스 실패: {e}")
            return {"error": str(e)}

    def save_deep_analysis_result(self, filepath: str, result: Dict[str, Any]):
        """심층 분석 결과를 파일로 저장"""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"✅ 심층 분석 결과 저장 완료: {filepath}")
        except Exception as e:
            print(f"❌ 심층 분석 결과 저장 실패: {e}")

    def get_analysis_summary(self) -> Dict[str, Any]:
        """분석 요약 정보 반환"""
        conversation_vars = self.conversation_memory.load_memory_variables({})
        summary_vars = self.summary_memory.load_memory_variables({})

        return {
            "conversation_memory_size": len(
                conversation_vars.get("analysis_history", [])
            ),
            "summary_memory_size": len(summary_vars.get("analysis_summary", [])),
            "last_analysis": (
                conversation_vars.get("analysis_history", [])[-1]
                if conversation_vars.get("analysis_history")
                else None
            ),
            "analysis_summary": (
                summary_vars.get("analysis_summary", [])[-1]
                if summary_vars.get("analysis_summary")
                else None
            ),
        }
