# -*- coding: utf-8 -*-
"""
분석 품질 향상 시스템 (LangChain 메모리 기반)

시니어 애널리스트의 분석 보조자료로 사용하기에 부족한 점을 피드백받아
단계적으로 분석 품질을 향상시키는 시스템이에요!
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_openai import ChatOpenAI


class AnalysisQualityEnhancer:
    """
    분석 품질 향상 시스템

    LangChain 메모리를 활용해서 분석의 부족한 점을 피드백받고
    단계적으로 분석 품질을 향상시켜요!
    """

    def __init__(self):
        """분석 품질 향상 시스템 초기화"""
        self.memory = ConversationBufferMemory(
            memory_key="analysis_history",
            return_messages=True,
            max_token_limit=4000,  # 메모리 크기 제한
        )

        # LLM 모델 설정
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.1,  # 일관된 피드백을 위해 낮은 값
            max_tokens=4000,
        )

        # 분석 품질 평가 체인
        self.quality_evaluator = self._create_quality_evaluator()

        # 분석 보완 체인
        self.analysis_enhancer = self._create_analysis_enhancer()

        # 최종 검증 체인
        self.final_validator = self._create_final_validator()

        print("✅ 분석 품질 향상 시스템 초기화 완료!")

    def _create_quality_evaluator(self) -> LLMChain:
        """분석 품질 평가 체인 생성"""

        # 시니어 애널리스트 관점에서 분석 품질을 평가하는 프롬프트
        evaluation_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
당신은 20년 경력의 시니어 애널리스트입니다.
주니어 애널리스트의 분석 보고서를 검토하고, 시니어 애널리스트의 분석 보조자료로 사용하기에 부족한 점을 구체적으로 피드백해주세요.

**🔍 평가 기준 (시니어 애널리스트 관점)**

**1. 구체성 및 정확성**
- 수치와 데이터의 출처가 명확한가?
- 추상적 표현 대신 구체적 수치가 제시되었는가?
- 계산 과정과 가정이 명시되었는가?

**2. 경쟁사 비교 분석**
- 실제 경쟁사 이름과 구체적 비교가 있는가?
- 업계 평균 수치의 출처와 계산 방법이 명시되었는가?
- 상대적 우위/열위가 구체적으로 분석되었는가?

**3. 시나리오 분석의 구체성**
- 시나리오별 구체적 가정이 명시되었는가?
- 각 시나리오의 발생 확률과 근거가 제시되었는가?
- 시나리오별 수치적 결과가 계산되었는가?

**4. 투자 판단의 근거**
- 투자 의견의 구체적 근거가 제시되었는가?
- 목표가 산출 과정과 가정이 명시되었는가?
- 리스크 요인의 구체적 영향도가 분석되었는가?

**5. 산업/시장 연관성**
- 업계 동향과의 연관성이 구체적으로 분석되었는가?
- 글로벌 시장 동향과의 연관성이 고려되었는가?
- 정책/규제 변화의 영향이 분석되었는가?

**📋 피드백 형식**

**✅ 잘된 점:**
- 구체적으로 잘 분석된 부분들

**❌ 부족한 점:**
- 각 항목별로 구체적인 부족한 점과 개선 방향

**🔧 구체적 개선 제안:**
- 추가로 필요한 데이터나 분석 방법
- 구체적 수치나 비교 대상
- 더 깊이 있는 분석 방향

**📊 종합 평가:**
- 현재 분석 수준 (1-10점)
- 시니어 애널리스트 보조자료 적합성 (적합/부적합/부분적)
- 우선 개선 필요 항목 3가지
""",
                ),
                MessagesPlaceholder(variable_name="analysis_history"),
                (
                    "human",
                    """
다음 분석 보고서를 시니어 애널리스트 관점에서 평가해주세요:

**분석 대상:** {company_name}
**섹터:** {sector_name}
**분석 전문가:** {analyst_name}

**분석 내용:**
{analysis_content}

**평가 요청:**
1. 시니어 애널리스트의 분석 보조자료로 사용하기에 부족한 점
2. 구체적인 개선 방향과 추가 필요 분석
3. 우선순위별 개선 제안
""",
                ),
            ],
            input_variables=[
                "company_name",
                "sector_name",
                "analyst_name",
                "analysis_content",
            ],
        )

        return LLMChain(
            llm=self.llm, prompt=evaluation_prompt, memory=self.memory, verbose=True
        )

    def _create_analysis_enhancer(self) -> LLMChain:
        """분석 보완 체인 생성"""

        # 피드백을 바탕으로 분석을 보완하는 프롬프트
        enhancement_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
당신은 시니어 애널리스트의 피드백을 바탕으로 분석을 보완하는 전문가입니다.
피드백에서 지적된 부족한 점들을 구체적으로 보완해서 시니어 애널리스트 수준의 분석을 만들어주세요.

**🔧 보완 원칙**

**1. 구체성 강화**
- 모든 수치에 출처와 계산 과정 명시
- 추상적 표현을 구체적 수치로 대체
- 가정과 전제조건 명확히 제시

**2. 경쟁사 비교 심화**
- 실제 경쟁사 3-5개 선정 및 구체적 비교
- 업계 평균 수치의 정확한 출처와 계산 방법
- 상대적 우위/열위의 구체적 분석

**3. 시나리오 분석 구체화**
- 각 시나리오별 구체적 가정과 근거
- 시나리오별 발생 확률과 수치적 결과
- 민감도 분석 포함

**4. 투자 판단 근거 강화**
- 목표가 산출의 구체적 과정과 가정
- 투자 의견의 구체적 근거와 리스크 분석
- 대안 시나리오별 투자 의견

**5. 산업/시장 연관성 심화**
- 업계 동향과의 구체적 연관성 분석
- 글로벌 시장 동향과의 연관성
- 정책/규제 변화의 구체적 영향 분석

**📋 보완된 분석 형식**

**1단계: 재무 건전성 분석 (보완)**
- 각 지표별 구체적 수치와 출처
- 경쟁사별 구체적 비교
- 3년간 트렌드 분석과 변화 원인

**2단계: 경쟁사 비교 분석 (보완)**
- 선정된 경쟁사 3-5개 구체적 비교
- 업계 평균 수치의 정확한 출처
- 상대적 우위/열위의 구체적 분석

**3단계: 내재가치 산출 (보완)**
- DCF 모델의 구체적 가정과 계산 과정
- 멀티플 분석의 구체적 비교 대상
- 목표가 산출의 구체적 과정

**4단계: 시나리오 분석 (보완)**
- 각 시나리오별 구체적 가정과 근거
- 시나리오별 발생 확률과 수치적 결과
- 민감도 분석 결과

**5단계: 종합 투자 의견 (보완)**
- 투자 의견의 구체적 근거와 리스크 분석
- 대안 시나리오별 투자 의견
- 투자 기간과 목표가의 구체적 근거
""",
                ),
                MessagesPlaceholder(variable_name="analysis_history"),
                (
                    "human",
                    """
다음 피드백을 바탕으로 분석을 보완해주세요:

**원본 분석:**
{original_analysis}

**시니어 애널리스트 피드백:**
{senior_feedback}

**보완 요청:**
피드백에서 지적된 부족한 점들을 구체적으로 보완해서 시니어 애널리스트 수준의 분석을 만들어주세요.
""",
                ),
            ],
            input_variables=["original_analysis", "senior_feedback"],
        )

        return LLMChain(
            llm=self.llm, prompt=enhancement_prompt, memory=self.memory, verbose=True
        )

    def _create_final_validator(self) -> LLMChain:
        """최종 검증 체인 생성"""

        # 보완된 분석의 최종 품질을 검증하는 프롬프트
        validation_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
당신은 시니어 애널리스트의 분석 보조자료 품질을 최종 검증하는 전문가입니다.
보완된 분석이 시니어 애널리스트의 분석 보조자료로 사용하기에 적합한지 검증해주세요.

**🔍 최종 검증 기준**

**1. 구체성 및 정확성 (20점)**
- 모든 수치에 출처와 계산 과정이 명시되었는가?
- 추상적 표현이 구체적 수치로 대체되었는가?
- 가정과 전제조건이 명확히 제시되었는가?

**2. 경쟁사 비교 분석 (20점)**
- 실제 경쟁사 3-5개가 선정되고 구체적으로 비교되었는가?
- 업계 평균 수치의 정확한 출처가 명시되었는가?
- 상대적 우위/열위가 구체적으로 분석되었는가?

**3. 시나리오 분석의 구체성 (20점)**
- 각 시나리오별 구체적 가정과 근거가 명시되었는가?
- 시나리오별 발생 확률과 수치적 결과가 제시되었는가?
- 민감도 분석이 포함되었는가?

**4. 투자 판단의 근거 (20점)**
- 투자 의견의 구체적 근거가 제시되었는가?
- 목표가 산출 과정과 가정이 명시되었는가?
- 리스크 요인의 구체적 영향도가 분석되었는가?

**5. 산업/시장 연관성 (20점)**
- 업계 동향과의 연관성이 구체적으로 분석되었는가?
- 글로벌 시장 동향과의 연관성이 고려되었는가?
- 정책/규제 변화의 영향이 분석되었는가?

**📋 최종 검증 결과 형식**

**✅ 검증 통과 항목:**
- 각 기준별로 잘 충족된 항목들

**⚠️ 추가 개선 필요 항목:**
- 아직 부족한 항목들과 구체적 개선 방향

**📊 종합 평가:**
- 총점: XX/100점
- 시니어 애널리스트 보조자료 적합성: 적합/부적합/부분적
- 최종 권장사항

**🎯 최종 판정:**
- 통과/재보완 필요/부분 통과
""",
                ),
                MessagesPlaceholder(variable_name="analysis_history"),
                (
                    "human",
                    """
다음 보완된 분석을 최종 검증해주세요:

**원본 분석:**
{original_analysis}

**시니어 애널리스트 피드백:**
{senior_feedback}

**보완된 분석:**
{enhanced_analysis}

**검증 요청:**
보완된 분석이 시니어 애널리스트의 분석 보조자료로 사용하기에 적합한지 최종 검증해주세요.
""",
                ),
            ],
            input_variables=[
                "original_analysis",
                "senior_feedback",
                "enhanced_analysis",
            ],
        )

        return LLMChain(
            llm=self.llm, prompt=validation_prompt, memory=self.memory, verbose=True
        )

    def enhance_analysis_quality(
        self,
        company_name: str,
        sector_name: str,
        analyst_name: str,
        analysis_content: str,
    ) -> Dict[str, Any]:
        """
        분석 품질 향상 프로세스 실행

        Args:
            company_name: 분석 대상 회사명
            sector_name: 섹터명
            analyst_name: 분석가 이름
            analysis_content: 원본 분석 내용

        Returns:
            Dict: 향상된 분석 결과
        """

        print(f"🚀 {company_name} 분석 품질 향상 프로세스 시작!")
        print("=" * 60)

        try:
            # 1단계: 분석 품질 평가 및 피드백 생성
            print("📊 1단계: 시니어 애널리스트 관점에서 분석 품질 평가 중...")

            evaluation_result = self.quality_evaluator.run(
                {
                    "company_name": company_name,
                    "sector_name": sector_name,
                    "analyst_name": analyst_name,
                    "analysis_content": analysis_content,
                }
            )

            print("✅ 1단계 완료: 분석 품질 평가 및 피드백 생성")
            print("-" * 40)

            # 2단계: 피드백 기반 분석 보완
            print("🔧 2단계: 피드백 기반 분석 보완 중...")

            enhancement_result = self.analysis_enhancer.run(
                {
                    "original_analysis": analysis_content,
                    "senior_feedback": evaluation_result,
                }
            )

            print("✅ 2단계 완료: 분석 보완")
            print("-" * 40)

            # 3단계: 최종 검증
            print("🔍 3단계: 최종 품질 검증 중...")

            validation_result = self.final_validator.run(
                {
                    "original_analysis": analysis_content,
                    "senior_feedback": evaluation_result,
                    "enhanced_analysis": enhancement_result,
                }
            )

            print("✅ 3단계 완료: 최종 검증")
            print("-" * 40)

            # 결과 정리
            result = {
                "timestamp": datetime.now().isoformat(),
                "company_name": company_name,
                "sector_name": sector_name,
                "analyst_name": analyst_name,
                "original_analysis": analysis_content,
                "senior_feedback": evaluation_result,
                "enhanced_analysis": enhancement_result,
                "final_validation": validation_result,
                "memory_context": self.memory.load_memory_variables({}),
            }

            print("🎉 분석 품질 향상 프로세스 완료!")
            print("=" * 60)

            return result

        except Exception as e:
            print(f"❌ 분석 품질 향상 프로세스 실패: {e}")
            return {"error": str(e)}

    def save_enhancement_history(self, filepath: str, result: Dict[str, Any]):
        """향상된 분석 결과를 파일로 저장"""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"✅ 향상된 분석 결과 저장 완료: {filepath}")
        except Exception as e:
            print(f"❌ 향상된 분석 결과 저장 실패: {e}")

    def get_enhancement_summary(self) -> Dict[str, Any]:
        """향상 프로세스 요약 정보 반환"""
        memory_vars = self.memory.load_memory_variables({})

        return {
            "memory_size": len(memory_vars.get("analysis_history", [])),
            "enhancement_sessions": len(memory_vars.get("analysis_history", []))
            // 3,  # 3단계당 1세션
            "last_enhancement": (
                memory_vars.get("analysis_history", [])[-1]
                if memory_vars.get("analysis_history")
                else None
            ),
        }
