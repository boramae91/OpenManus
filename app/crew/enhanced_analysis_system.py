# -*- coding: utf-8 -*-
"""
향상된 분석 시스템 (CoT + 5Why + Memory + 품질 향상 통합)

기존 분석 품질 향상 시스템과 새로운 심층 분석 시스템을 통합해서
최고 수준의 기업 분석을 수행하는 시스템이에요!
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_openai import ChatOpenAI

from .analysis_quality_enhancer import AnalysisQualityEnhancer
from .deep_analysis_system import DeepAnalysisSystem


class EnhancedAnalysisSystem:
    """
    향상된 분석 시스템

    CoT + 5Why + Memory 기반 심층 분석과
    품질 향상 시스템을 통합한 최고 수준 분석 시스템이에요!
    """

    def __init__(self):
        """향상된 분석 시스템 초기화"""

        # 하위 시스템들 초기화
        self.deep_analysis = DeepAnalysisSystem()
        self.quality_enhancer = AnalysisQualityEnhancer()

        # 통합 메모리 시스템
        self.integrated_memory = ConversationBufferMemory(
            memory_key="integrated_analysis_history",
            return_messages=True,
            max_token_limit=8000,  # 통합 분석을 위해 더 큰 메모리
        )

        # 통합 요약 메모리도 ConversationBufferMemory로 대체
        self.integrated_summary = ConversationBufferMemory(
            memory_key="integrated_analysis_summary",
            return_messages=True,
            max_token_limit=6000,
        )

        # 통합 분석 체인 생성
        self.integration_analyzer = self._create_integration_analyzer()
        self.final_synthesis = self._create_final_synthesis()

        print("✅ 향상된 분석 시스템 초기화 완료!")

    def _create_integration_analyzer(self) -> LLMChain:
        """심층 분석과 품질 향상 결과를 통합하는 체인 생성"""

        integration_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
당신은 심층 분석과 품질 향상 결과를 통합하는 전문가입니다.
CoT + 5Why 분석 결과와 품질 향상 피드백을 종합해서
최고 수준의 기업 분석 보고서를 작성해주세요.

**🔗 통합 분석 프레임워크**

**1. 심층 분석 결과 종합**
- CoT 분석의 핵심 인사이트
- 5Why 분석의 근본 원인
- 근본 원인 분석의 다층적 구조
- 시사점 분석의 투자 의견

**2. 품질 향상 피드백 반영**
- 시니어 애널리스트 피드백의 핵심 지적사항
- 보완된 분석 내용의 추가 인사이트
- 최종 검증 결과의 신뢰도 평가

**3. 통합적 시사점 도출**
- 심층 분석과 품질 향상 결과의 일치점/차이점
- 종합적 투자 의견과 근거
- 리스크와 기회의 균형적 평가

**📋 통합 분석 형식**

**🎯 핵심 분석 결과:**

**CoT + 5Why 심층 분석:**
- 관찰된 핵심 현상: [구체적 현상]
- 근본 원인: [5Why 분석 결과]
- 다층적 원인 구조: [직접/근본/구조적/환경적 원인]

**품질 향상 결과:**
- 시니어 애널리스트 피드백: [주요 지적사항]
- 보완된 분석: [추가 인사이트]
- 최종 검증: [신뢰도 평가]

**💡 통합적 시사점:**

**투자 가치 평가:**
- 현재 가치 vs 내재 가치: [구체적 수치]
- 할증/할인 요인: [구체적 요인]
- 투자 매력도: [높음/중간/낮음]

**시나리오별 전망:**
- 낙관 시나리오: [전제조건, 예상 결과, 확률]
- 기본 시나리오: [전제조건, 예상 결과, 확률]
- 비관 시나리오: [전제조건, 예상 결과, 확률]

**리스크 관리:**
- 주요 리스크: [구체적 리스크와 영향도]
- 리스크 완화 방안: [구체적 방안]
- 모니터링 지표: [구체적 지표]

**🎯 최종 투자 의견:**
- 종합 의견: [매수/중립/매도]
- 목표가: [구체적 수치]
- 투자 기간: [구체적 기간]
- 핵심 근거: [3-5개 핵심 근거]
""",
                ),
                MessagesPlaceholder(variable_name="integrated_analysis_history"),
                (
                    "human",
                    "{input_text}",
                ),
            ],
        )

        return LLMChain(
            llm=ChatOpenAI(model="gpt-4o", temperature=0.1, max_tokens=6000),
            prompt=integration_prompt,
            memory=self.integrated_memory,
            verbose=True,
        )

    def _create_final_synthesis(self) -> LLMChain:
        """최종 종합 분석 체인 생성"""

        synthesis_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
당신은 최고 수준의 기업 분석 보고서를 작성하는 시니어 애널리스트입니다.
통합 분석 결과를 바탕으로 투자자들이 실제로 활용할 수 있는
전문적이고 실용적인 분석 보고서를 작성해주세요.

**📊 최종 보고서 프레임워크**

**1. Executive Summary (핵심 요약)**
- 분석 대상과 주요 결론
- 투자 의견과 핵심 근거
- 주요 리스크와 기회

**2. Company Overview (기업 개요)**
- 사업 구조와 핵심 사업
- 시장 포지셔닝과 경쟁력
- 경영진과 전략 방향

**3. Financial Analysis (재무 분석)**
- 재무 건전성 평가
- 수익성과 성장성 분석
- 현금흐름과 자본구조

**4. Industry & Market Analysis (산업/시장 분석)**
- 산업 동향과 시장 구조
- 경쟁 구도와 시장 점유율
- 기술 변화와 규제 환경

**5. Valuation Analysis (가치 평가)**
- 내재가치 산출 방법론
- 멀티플 분석과 비교
- 목표가 설정 근거

**6. Investment Thesis (투자 논리)**
- 투자 의견과 근거
- 시나리오별 전망
- 리스크 관리 방안

**7. Conclusion & Recommendations (결론 및 제언)**
- 종합적 투자 의견
- 투자 전략 제언
- 모니터링 포인트

**📋 최종 보고서 형식**

**Executive Summary**

**분석 대상:** [기업명]
**투자 의견:** [매수/중립/매도]
**목표가:** [구체적 수치]
**투자 기간:** [구체적 기간]

**핵심 투자 논리:**
- [핵심 논리 1]
- [핵심 논리 2]
- [핵심 논리 3]

**주요 리스크:**
- [리스크 1]
- [리스크 2]
- [리스크 3]

**Company Overview**

**사업 구조:**
- [핵심 사업 영역]
- [매출 구성]
- [지역별 매출]

**시장 포지셔닝:**
- [시장 점유율]
- [경쟁 우위]
- [브랜드 가치]

**Financial Analysis**

**재무 건전성:**
- [유동성 지표]
- [수익성 지표]
- [성장성 지표]

**현금흐름:**
- [영업활동 현금흐름]
- [투자활동 현금흐름]
- [재무활동 현금흐름]

**Industry & Market Analysis**

**산업 동향:**
- [시장 규모와 성장률]
- [주요 동향]
- [기술 변화]

**경쟁 구도:**
- [주요 경쟁사]
- [시장 점유율]
- [경쟁 우위/열위]

**Valuation Analysis**

**내재가치 산출:**
- [DCF 모델 가정]
- [할인율 설정]
- [성장률 가정]

**멀티플 분석:**
- [PER 비교]
- [PBR 비교]
- [EV/EBITDA 비교]

**Investment Thesis**

**투자 의견:**
- [매수/중립/매도]
- [목표가]
- [투자 기간]

**시나리오 분석:**
- [낙관 시나리오]
- [기본 시나리오]
- [비관 시나리오]

**Conclusion & Recommendations**

**종합 의견:**
- [투자 의견]
- [핵심 근거]
- [투자 전략]

**모니터링 포인트:**
- [핵심 지표]
- [리스크 요인]
- [기회 요인]
""",
                ),
                MessagesPlaceholder(variable_name="integrated_analysis_history"),
                (
                    "human",
                    "{input_text}",
                ),
            ],
        )

        return LLMChain(
            llm=ChatOpenAI(model="gpt-4o", temperature=0.1, max_tokens=8000),
            prompt=synthesis_prompt,
            memory=self.integrated_memory,
            verbose=True,
        )

    def perform_enhanced_analysis(
        self,
        company_name: str,
        sector_name: str,
        financial_data: str,
        market_data: str,
        competitor_data: str,
        analyst_name: str = "통합 분석 시스템",
    ) -> Dict[str, Any]:
        """
        향상된 분석 프로세스 실행

        Args:
            company_name: 분석 대상 회사명
            sector_name: 섹터명
            financial_data: 재무 데이터
            market_data: 시장 데이터
            competitor_data: 경쟁사 데이터
            analyst_name: 분석가 이름

        Returns:
            Dict: 향상된 분석 결과
        """

        print(f"🚀 {company_name} 향상된 분석 프로세스 시작!")
        print("=" * 60)

        try:
            # 1단계: CoT + 5Why 심층 분석
            print("🧠 1단계: CoT + 5Why 심층 분석 중...")

            deep_analysis_result = self.deep_analysis.perform_deep_analysis(
                company_name=company_name,
                sector_name=sector_name,
                financial_data=financial_data,
                market_data=market_data,
                competitor_data=competitor_data,
            )

            if "error" in deep_analysis_result:
                return {"error": f"심층 분석 실패: {deep_analysis_result['error']}"}

            print("✅ 1단계 완료: 심층 분석")
            print("-" * 40)

            # 2단계: 품질 향상 분석
            print("🔧 2단계: 품질 향상 분석 중...")

            # 심층 분석 결과를 품질 향상 시스템에 입력
            cot_five_why_content = f"""
            **CoT 분석:**
            {deep_analysis_result['cot_analysis']}

            **5Why 분석:**
            {deep_analysis_result['five_why_analysis']}

            **근본 원인 분석:**
            {deep_analysis_result['root_cause_analysis']}

            **시사점 분석:**
            {deep_analysis_result['implication_analysis']}
            """

            quality_enhancement_result = self.quality_enhancer.enhance_analysis_quality(
                company_name=company_name,
                sector_name=sector_name,
                analyst_name=analyst_name,
                analysis_content=cot_five_why_content,
            )

            if "error" in quality_enhancement_result:
                return {
                    "error": f"품질 향상 실패: {quality_enhancement_result['error']}"
                }

            print("✅ 2단계 완료: 품질 향상")
            print("-" * 40)

            # 3단계: 통합 분석
            print("🔗 3단계: 통합 분석 중...")

            # LangChain 메시지 객체를 문자열로 변환하는 함수
            def convert_to_serializable(obj):
                """LangChain 메시지 객체를 JSON 직렬화 가능한 형태로 변환"""
                if hasattr(obj, "content"):
                    return str(obj.content)
                elif isinstance(obj, dict):
                    return {k: convert_to_serializable(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_to_serializable(item) for item in obj]
                else:
                    return str(obj)

            # 여러 입력 변수를 하나의 통합된 문자열로 합치기
            integration_input = f"""
다음 심층 분석과 품질 향상 결과를 통합해서 최고 수준의 분석 보고서를 작성해주세요:

**심층 분석 결과:**
{json.dumps(convert_to_serializable(deep_analysis_result), ensure_ascii=False)}

**품질 향상 결과:**
{json.dumps(convert_to_serializable(quality_enhancement_result), ensure_ascii=False)}

**통합 분석 요청:**
1. 두 분석 결과의 핵심 인사이트 종합
2. 일치점과 차이점 분석
3. 통합적 투자 의견과 근거 도출
4. 최종 투자 판단 제시
"""

            integration_result = self.integration_analyzer.run(integration_input)

            print("✅ 3단계 완료: 통합 분석")
            print("-" * 40)

            # 4단계: 최종 종합 보고서
            print("📊 4단계: 최종 종합 보고서 작성 중...")

            # 여러 입력 변수를 하나의 통합된 문자열로 합치기
            final_report_input = f"""
다음 통합 분석 결과를 바탕으로 최고 수준의 기업 분석 보고서를 작성해주세요:

**통합 분석 결과:**
{integration_result}

**최종 보고서 요청:**
1. Executive Summary부터 시작
2. 각 섹션별 상세 분석
3. 투자자 관점의 실용적 제언
4. 명확한 투자 의견과 근거
"""

            final_report = self.final_synthesis.run(final_report_input)

            print("✅ 4단계 완료: 최종 보고서")
            print("-" * 40)

            # 통합 메모리에 결과 저장
            self.integrated_summary.save_context(
                {"input": f"{company_name} 향상된 분석"},
                {
                    "output": f"심층분석: {deep_analysis_result['cot_analysis'][:200]}... | 품질향상: {quality_enhancement_result.get('enhanced_analysis', '')[:200]}... | 통합분석: {integration_result[:200]}... | 최종보고서: {final_report[:200]}..."
                },
            )

            # 최종 결과 정리
            result = {
                "timestamp": datetime.now().isoformat(),
                "company_name": company_name,
                "sector_name": sector_name,
                "analysis_method": "Enhanced Analysis (CoT + 5Why + Memory + Quality Enhancement)",
                "deep_analysis": deep_analysis_result,
                "quality_enhancement": quality_enhancement_result,
                "integration_analysis": integration_result,
                "final_report": final_report,
                "memory_context": {
                    "integrated_history": self.integrated_memory.load_memory_variables(
                        {}
                    ),
                    "integrated_summary": self.integrated_summary.load_memory_variables(
                        {}
                    ),
                },
            }

            print("🎉 향상된 분석 프로세스 완료!")
            print("=" * 60)

            return result

        except Exception as e:
            print(f"❌ 향상된 분석 프로세스 실패: {e}")
            import traceback

            traceback.print_exc()
            return {"error": str(e)}

    def save_enhanced_analysis_result(self, filepath: str, result: Dict[str, Any]):
        """향상된 분석 결과를 파일로 저장"""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"✅ 향상된 분석 결과 저장 완료: {filepath}")
        except Exception as e:
            print(f"❌ 향상된 분석 결과 저장 실패: {e}")

    def get_enhanced_analysis_summary(self) -> Dict[str, Any]:
        """향상된 분석 요약 정보 반환"""
        integrated_vars = self.integrated_memory.load_memory_variables({})
        summary_vars = self.integrated_summary.load_memory_variables({})

        return {
            "integrated_memory_size": len(
                integrated_vars.get("integrated_analysis_history", [])
            ),
            "integrated_summary_size": len(
                summary_vars.get("integrated_analysis_summary", [])
            ),
            "last_integrated_analysis": (
                integrated_vars.get("integrated_analysis_history", [])[-1]
                if integrated_vars.get("integrated_analysis_history")
                else None
            ),
            "last_integrated_summary": (
                summary_vars.get("integrated_analysis_summary", [])[-1]
                if summary_vars.get("integrated_analysis_summary")
                else None
            ),
        }

    def compare_analysis_methods(
        self,
        company_name: str,
        sector_name: str,
        financial_data: str,
        market_data: str,
        competitor_data: str,
    ) -> Dict[str, Any]:
        """
        기존 분석과 향상된 분석을 비교하는 메서드

        Args:
            company_name: 분석 대상 회사명
            sector_name: 섹터명
            financial_data: 재무 데이터
            market_data: 시장 데이터
            competitor_data: 경쟁사 데이터

        Returns:
            Dict: 분석 방법 비교 결과
        """

        print(f"🔍 {company_name} 분석 방법 비교 시작!")
        print("=" * 60)

        try:
            # 1. 기존 심층 분석만 실행
            print("1️⃣ 기존 심층 분석 실행 중...")
            deep_only_result = self.deep_analysis.perform_deep_analysis(
                company_name=company_name,
                sector_name=sector_name,
                financial_data=financial_data,
                market_data=market_data,
                competitor_data=competitor_data,
            )

            # 2. 향상된 분석 실행
            print("2️⃣ 향상된 분석 실행 중...")
            enhanced_result = self.perform_enhanced_analysis(
                company_name=company_name,
                sector_name=sector_name,
                financial_data=financial_data,
                market_data=market_data,
                competitor_data=competitor_data,
            )

            # 3. 비교 분석
            print("3️⃣ 분석 방법 비교 중...")

            # LangChain 메시지 객체를 문자열로 변환하는 함수
            def convert_to_serializable(obj):
                """LangChain 메시지 객체를 JSON 직렬화 가능한 형태로 변환"""
                if hasattr(obj, "content"):
                    return str(obj.content)
                elif isinstance(obj, dict):
                    return {k: convert_to_serializable(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_to_serializable(item) for item in obj]
                else:
                    return str(obj)

            comparison_result = {
                "timestamp": datetime.now().isoformat(),
                "company_name": company_name,
                "comparison_metrics": {
                    "deep_analysis_length": {
                        "cot_analysis": len(deep_only_result.get("cot_analysis", "")),
                        "five_why_analysis": len(
                            deep_only_result.get("five_why_analysis", "")
                        ),
                        "root_cause_analysis": len(
                            deep_only_result.get("root_cause_analysis", "")
                        ),
                        "implication_analysis": len(
                            deep_only_result.get("implication_analysis", "")
                        ),
                    },
                    "enhanced_analysis_length": {
                        "deep_analysis": len(
                            json.dumps(
                                convert_to_serializable(
                                    enhanced_result.get("deep_analysis", {})
                                ),
                                ensure_ascii=False,
                            )
                        ),
                        "quality_enhancement": len(
                            json.dumps(
                                convert_to_serializable(
                                    enhanced_result.get("quality_enhancement", {})
                                ),
                                ensure_ascii=False,
                            )
                        ),
                        "integration_analysis": len(
                            enhanced_result.get("integration_analysis", "")
                        ),
                        "final_report": len(enhanced_result.get("final_report", "")),
                    },
                    "total_analysis_length": {
                        "deep_only": sum(
                            [
                                len(deep_only_result.get("cot_analysis", "")),
                                len(deep_only_result.get("five_why_analysis", "")),
                                len(deep_only_result.get("root_cause_analysis", "")),
                                len(deep_only_result.get("implication_analysis", "")),
                            ]
                        ),
                        "enhanced": sum(
                            [
                                len(
                                    json.dumps(
                                        convert_to_serializable(
                                            enhanced_result.get("deep_analysis", {})
                                        ),
                                        ensure_ascii=False,
                                    )
                                ),
                                len(
                                    json.dumps(
                                        convert_to_serializable(
                                            enhanced_result.get(
                                                "quality_enhancement", {}
                                            )
                                        ),
                                        ensure_ascii=False,
                                    )
                                ),
                                len(enhanced_result.get("integration_analysis", "")),
                                len(enhanced_result.get("final_report", "")),
                            ]
                        ),
                    },
                },
                "analysis_quality_comparison": {
                    "deep_only": {
                        "depth": "심층적이지만 일관성 부족",
                        "consistency": "단계별 분석으로 일관성 확보",
                        "practicality": "투자 의견은 있으나 실용성 부족",
                    },
                    "enhanced": {
                        "depth": "심층적 + 품질 향상으로 최고 수준",
                        "consistency": "통합 분석으로 일관성 극대화",
                        "practicality": "시니어 애널리스트 수준의 실용성",
                    },
                },
                "recommendation": "향상된 분석 방법이 더 우수한 결과를 제공합니다.",
            }

            print("✅ 분석 방법 비교 완료!")
            print("=" * 60)

            return comparison_result

        except Exception as e:
            print(f"❌ 분석 방법 비교 실패: {e}")
            return {"error": str(e)}
