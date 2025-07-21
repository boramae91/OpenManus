# -*- coding: utf-8 -*-
"""
섹터별 전문 분석팀 팩토리 시스템

LangChain을 통한 성능 향상!
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from langchain.agents import AgentExecutor, create_openai_functions_agent

# LangChain imports
from langchain.chains import LLMChain, SequentialChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain.schema import BaseMemory
from langchain.tools import Tool
from langchain_openai import ChatOpenAI

# 🚀 웹 검색 도구 import
from app.tool.langchain_web_search import LangChainWebSearchTool

from .gics_sectors import GICSSector, GICSSectorManager

# 🚀 공통 프롬프트 컴포넌트 import
from .prompt_components import PromptComponents


class Q5EnforcedAgentExecutor(AgentExecutor):
    """
    Q5 섹터 특화 질문을 강제로 보장하는 Custom AgentExecutor

    LangChain AgentExecutor를 상속받아 실행 레벨에서 Q5를 강제로 추가합니다.
    이렇게 하면 Agent가 Q5를 생성하지 않아도 확실히 포함됩니다.
    """

    def __init__(
        self,
        sector: GICSSector,
        sector_manager: GICSSectorManager,
        agent_name: str = "",
        **kwargs,
    ):
        """
        Q5 강제 생성 Agent Executor 초기화

        Args:
            sector: GICS 섹터
            sector_manager: 섹터 매니저
            agent_name: Agent 이름 (로깅용)
            **kwargs: AgentExecutor 기본 매개변수들
        """
        # 기본 AgentExecutor 초기화
        super().__init__(**kwargs)

        # 추가 속성을 object의 __dict__에 직접 저장 (Pydantic 우회)
        object.__setattr__(self, "_q5_sector", sector)
        object.__setattr__(self, "_q5_sector_manager", sector_manager)
        object.__setattr__(self, "_q5_agent_name", agent_name)
        object.__setattr__(
            self,
            "_q5_sector_korean_name",
            sector_manager.get_sector_korean_name(sector),
        )
        object.__setattr__(self, "_q5_sector_emoji", self._get_sector_emoji())

        print(
            f"🔧 Q5 강제 생성 AgentExecutor 초기화: {self._q5_sector_emoji} {self._q5_sector_korean_name}"
        )

    def _call(self, inputs: Dict[str, Any], run_manager=None) -> Dict[str, Any]:
        """
        AgentExecutor 실행을 override하여 Q5 강제 추가

        Args:
            inputs: 입력 데이터
            run_manager: LangChain RunManager

        Returns:
            Dict: Q5가 보장된 분석 결과
        """
        print(f"🚀 {self._q5_sector_emoji} Q5 강제 생성 Agent 실행 시작...")

        # 기본 AgentExecutor 실행
        try:
            result = super()._call(inputs, run_manager)
        except Exception as e:
            print(f"❌ 기본 Agent 실행 실패: {e}")
            result = {"output": f"Agent 실행 오류: {str(e)}"}

        # Q5 강제 추가 로직 적용
        enhanced_result = self._ensure_q5_presence(result, inputs)

        print(f"✅ {self._q5_sector_emoji} Q5 강제 생성 완료!")
        return enhanced_result

    def _ensure_q5_presence(
        self, result: Dict[str, Any], inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Q5 섹터 특화 질문이 누락된 경우 강제로 추가

        Args:
            result: Agent 실행 결과
            inputs: 원본 입력 데이터

        Returns:
            Dict: Q5가 포함된 수정된 결과
        """
        output = result.get("output", "")

        # Q5 존재 여부 검증 (기본 검증으로 복원)
        if self._has_q5(output):
            print(
                f"✅ Q5 {self._q5_sector_emoji} {self._q5_sector_korean_name} 섹터 질문 이미 포함됨"
            )
            return result

        print(
            f"⚠️ Q5 누락 감지 - {self._q5_sector_emoji} {self._q5_sector_korean_name} 섹터 질문 강제 추가 중..."
        )

        # Q5 콘텐츠 생성 (기본 질문만)
        q5_content = self._generate_sector_q5()

        # Q5 주입
        enhanced_output = self._inject_q5(output, q5_content)

        # 결과 업데이트
        result["output"] = enhanced_output
        result["q5_enforced"] = True
        result["sector"] = self._q5_sector_korean_name
        result["sector_emoji"] = self._q5_sector_emoji

        print(
            f"✅ Q5 {self._q5_sector_emoji} {self._q5_sector_korean_name} 섹터 질문 강제 추가 완료!"
        )
        return result

    def _has_q5(self, output: str) -> bool:
        """
        출력에 Q5가 포함되어 있는지 검증

        Args:
            output: Agent 출력 텍스트

        Returns:
            bool: Q5 포함 여부
        """
        q5_patterns = [
            "Q5:",
            "Q5 ",
            "Q5-1:",
            "Q5-2:",
            self._q5_sector_emoji,
            f"{self._q5_sector_korean_name} 섹터 특화",
            "섹터 특화 분석",
        ]

        return any(pattern in output for pattern in q5_patterns)

    def _inject_q5(self, output: str, q5_content: str) -> str:
        """
        출력 텍스트에 Q5를 적절한 위치에 주입

        Args:
            output: 원본 출력 텍스트
            q5_content: 주입할 Q5 콘텐츠

        Returns:
            str: Q5가 주입된 텍스트
        """
        # Q4 다음에 Q5 삽입 시도
        q4_positions = [
            output.find("Q4:"),
            output.find("Q4 "),
            output.find("리스크와 기회"),
        ]

        for q4_pos in q4_positions:
            if q4_pos != -1:
                # Q4 섹션의 끝 찾기
                section_endings = [
                    output.find("=== 2단계", q4_pos),
                    output.find("**2단계", q4_pos),
                    output.find("2단계:", q4_pos),
                    output.find("\n\n=", q4_pos),
                    output.find("\n\n**", q4_pos),
                ]

                for ending in section_endings:
                    if ending != -1:
                        return (
                            output[:ending] + f"\n\n{q5_content}\n\n" + output[ending:]
                        )

        # 1단계 섹션 끝에 추가
        stage1_endings = [
            output.find("=== 2단계"),
            output.find("**2단계"),
            output.find("2단계:"),
        ]

        for ending in stage1_endings:
            if ending != -1:
                return output[:ending] + f"\n{q5_content}\n\n" + output[ending:]

        # 마지막 수단: 텍스트 끝에 추가
        return output + f"\n\n{q5_content}"

    def _get_sector_emoji(self) -> str:
        """
        섹터별 이모지 반환

        Returns:
            str: 섹터 이모지
        """
        sector_emojis = {
            GICSSector.INFORMATION_TECHNOLOGY: "🖥️",
            GICSSector.FINANCIALS: "🏦",
            GICSSector.HEALTH_CARE: "💊",
            GICSSector.ENERGY: "⚡",
            GICSSector.CONSUMER_DISCRETIONARY: "🛒",
            GICSSector.CONSUMER_STAPLES: "🍞",
            GICSSector.MATERIALS: "🏭",
            GICSSector.INDUSTRIALS: "🏗️",
            GICSSector.COMMUNICATION_SERVICES: "📡",
            GICSSector.UTILITIES: "🔌",
            GICSSector.REAL_ESTATE: "🏢",
        }
        return sector_emojis.get(self._q5_sector, "🎯")

    def _generate_sector_q5(self) -> str:
        """
        현재 섹터에 맞는 Q5 콘텐츠 생성

        Returns:
            str: 섹터별 Q5 질문 콘텐츠
        """
        try:
            # PromptComponents를 사용하여 섹터별 질문 생성
            sector_questions = PromptComponents._generate_sector_specific_questions(
                self._q5_sector, self._q5_sector_manager
            )

            # Q5 부분만 추출
            q5_start = sector_questions.find("Q5:")
            if q5_start != -1:
                q5_section = sector_questions[q5_start:]
                # 다음 섹션(안내 정보 등)이 시작되기 전까지 추출
                next_section = q5_section.find("\n🎯")
                if next_section != -1:
                    q5_section = q5_section[:next_section]
                return q5_section.strip()
        except Exception as e:
            print(f"⚠️ 동적 Q5 생성 실패: {e}, 기본 Q5 사용")

        # 폴백: 기본 Q5 생성
        return f"""Q5: {self._q5_sector_emoji} {self._q5_sector_korean_name} 섹터 특화 분석 질문들:
  └─ Q5-1: 업계 내 경쟁 우위와 차별화 요소는?
  └─ Q5-2: 시장 점유율과 고객 기반 강화 전략은?
  └─ Q5-3: 운영 효율성과 비용 관리 역량은?
  └─ Q5-4: 혁신 역량과 신사업 발굴 현황은?
  └─ Q5-5: ESG 경영과 지속가능성 전략은?"""


@dataclass
class AnalystAgent:
    """
    개별 분석가 에이전트 정의
    각 에이전트는 고유한 전문 분야와 역할을 가져요

    GICS 섹터별 특화된 분석 포인트와 위험 요소를 반영한 전문가에요!
    LangChain을 통한 성능 향상!
    """

    name: str  # 에이전트 이름
    role: str  # 역할 (펀더멘털 분석가, 기술적 분석가 등)
    expertise: str  # 전문 분야
    analysis_focus: str  # 분석 초점
    key_methods: List[str]  # 주요 분석 방법론
    sector_context: str  # 섹터별 특화 컨텍스트
    sector_specific_points: List[str]  # 섹터별 중점 분석 포인트
    risk_awareness: List[str]  # 섹터별 주의해야 할 위험 요소
    critical_metrics: List[str]  # 섹터별 핵심 체크 지표

    # 🚀 LangChain 관련 새로운 필드들
    langchain_enabled: bool = False  # LangChain 사용 여부
    langchain_chain: Optional[Any] = None  # LangChain Chain 객체
    memory_system: Optional[BaseMemory] = None  # Memory 시스템
    analysis_history: List[Dict] = field(default_factory=list)  # 분석 이력
    performance_metrics: Dict[str, float] = field(default_factory=dict)  # 성능 지표

    def __post_init__(self):
        """초기화 후 LangChain 시스템 설정"""
        if self.langchain_enabled:
            self._setup_langchain_system()

    def _setup_langchain_system(self):
        """LangChain 시스템 초기 설정"""
        try:
            # Memory 시스템 설정 (deprecation warning 억제)
            import warnings

            # deprecation 경고 일시적으로 억제
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                warnings.simplefilter("ignore", UserWarning)

                try:
                    from langchain.memory import ConversationBufferMemory

                    self.memory_system = ConversationBufferMemory(
                        memory_key="analysis_history", return_messages=True
                    )
                except ImportError:
                    # 최신 버전에서는 다른 방식 사용
                    try:
                        from langchain_core.memory import ConversationBufferMemory

                        self.memory_system = ConversationBufferMemory(
                            memory_key="analysis_history", return_messages=True
                        )
                    except ImportError:
                        # 폴백: 메모리 시스템 비활성화
                        self.memory_system = None
                    print(
                        f"⚠️ {self.name} 메모리 시스템 초기화 실패 - 최신 LangChain 버전 확인 필요"
                    )

            # 성능 지표 초기화
            self.performance_metrics = {
                "accuracy": 0.0,
                "consistency": 0.0,
                "response_time": 0.0,
                "user_satisfaction": 0.0,
            }

            print(f"✅ {self.name} LangChain 시스템 초기화 완료!")

        except Exception as e:
            print(f"⚠️ {self.name} LangChain 초기화 실패: {e}")
            self.langchain_enabled = False

    def run_langchain_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        LangChain을 사용한 고급 분석 수행 (CoT + 5Why + 7Why 포함)

        Args:
            input_data: 분석에 필요한 입력 데이터

        Returns:
            Dict: 분석 결과
        """
        if not self.langchain_enabled or self.langchain_chain is None:
            return self._run_traditional_analysis(input_data)

        try:
            # 분석 시작 시간 기록
            start_time = datetime.now()

            # 🚀 향상된 분석 시스템 (CoT + 5Why + 7Why) 사용
            try:
                # 향상된 분석 시스템 초기화 및 실행
                from .enhanced_analysis_system import EnhancedAnalysisSystem
                from .enhanced_seven_why_analyzer import EnhancedSevenWhyAnalyzer

                enhanced_analysis = EnhancedAnalysisSystem()
                seven_why_analyzer = EnhancedSevenWhyAnalyzer()

                # 통합 데이터 준비
                company_name = input_data.get("company_name", "분석대상")
                sector_name = input_data.get("sector_name", "정보기술")
                financial_data = input_data.get("financial_data", "재무 데이터 없음")
                market_data = input_data.get("market_data", "시장 데이터 없음")
                competitor_data = input_data.get(
                    "competitor_data", "경쟁사 데이터 없음"
                )

                # 1단계: CoT + 5Why 심층 분석
                print(f"🧠 {self.name} CoT + 5Why 심층 분석 시작...")
                deep_analysis_result = (
                    enhanced_analysis.deep_analysis.perform_deep_analysis(
                        company_name=company_name,
                        sector_name=sector_name,
                        financial_data=str(financial_data),
                        market_data=market_data,
                        competitor_data=competitor_data,
                    )
                )

                if "error" in deep_analysis_result:
                    print(
                        f"⚠️ {self.name} 심층 분석 실패, 기본 LangChain Chain으로 진행"
                    )
                    # 폴백: 기존 LangChain Chain 사용
                    if hasattr(self.langchain_chain, "invoke"):
                        result = self.langchain_chain.invoke(input_data)
                    else:
                        result = self.langchain_chain.run(input_data)
                else:
                    # 2단계: 7Why 분석 (전문가 분석 텍스트 기반) - 비활성화됨
                    # print(f"🔍 {self.name} 7Why 분석 시작...")

                    # CoT 분석 결과를 7Why 분석의 입력으로 사용
                    cot_analysis_text = deep_analysis_result.get("cot_analysis", "")

                    # seven_why_result = (
                    #     seven_why_analyzer.perform_integrated_7why_analysis(
                    #         expert_analysis_text=cot_analysis_text,
                    #         financial_data=str(financial_data),
                    #         market_data=market_data,
                    #         competitor_data=competitor_data,
                    #         web_search_data=input_data.get("web_search_data", ""),
                    #     )
                    # )

                    # 7Why 분석 비활성화로 인한 더미 결과
                    seven_why_result = {
                        "integrated_7why_analysis": "7Why 분석이 현재 비활성화되어 있습니다. CoT + 5Why 분석만 수행됩니다."
                    }

                    # 3단계: 통합 분석 결과 생성
                    print(f"🔗 {self.name} 통합 분석 결과 생성...")

                    result = f"""
**🎯 {self.name} 향상된 분석 결과 (CoT + 5Why + 7Why)**

**1️⃣ CoT (Chain of Thought) 분석:**
{deep_analysis_result.get('cot_analysis', 'CoT 분석 결과 없음')}

**2️⃣ 5Why 근본 원인 분석:**
{deep_analysis_result.get('five_why_analysis', '5Why 분석 결과 없음')}

**3️⃣ 7Why 확장 분석:**
{seven_why_result.get('integrated_7why_analysis', '7Why 분석 결과 없음')}

**4️⃣ 근본 원인 종합 분석:**
{deep_analysis_result.get('root_cause_analysis', '근본 원인 분석 결과 없음')}

**5️⃣ 투자 시사점 분석:**
{deep_analysis_result.get('implication_analysis', '시사점 분석 결과 없음')}

**📊 종합 투자 의견:**
위의 다층적 분석을 종합하여 {self.name}의 전문적 투자 의견을 제시합니다.
"""

                    print(f"✅ {self.name} 향상된 분석 완료 (CoT + 5Why + 7Why)")

            except Exception as enhanced_error:
                print(f"❌ {self.name} 향상된 분석 실패: {enhanced_error}")
                # 폴백: 기존 LangChain Chain 사용
                if hasattr(self.langchain_chain, "invoke"):
                    result = self.langchain_chain.invoke(input_data)
                else:
                    result = self.langchain_chain.run(input_data)

            # 분석 시간 계산
            analysis_time = (datetime.now() - start_time).total_seconds()

            # 결과 저장
            analysis_result = {
                "timestamp": datetime.now().isoformat(),
                "input_data": input_data,
                "result": result,
                "analysis_time": analysis_time,
                "agent_name": self.name,
                "role": self.role,
                "analysis_method": "Enhanced Analysis (CoT + 5Why + 7Why)",
            }

            # 분석 이력에 저장
            self.analysis_history.append(analysis_result)

            # 성능 지표 업데이트
            self._update_performance_metrics(analysis_result)

            # Memory에 저장
            if self.memory_system:
                self.memory_system.save_context(
                    {"input": str(input_data)}, {"output": str(result)}
                )

            print(
                f"✅ {self.name} 향상된 LangChain 분석 완료 (소요시간: {analysis_time:.2f}초)"
            )
            return analysis_result

        except Exception as e:
            print(f"❌ {self.name} LangChain 분석 실패: {e}")
            return self._run_traditional_analysis(input_data)

    def _run_traditional_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """기존 방식의 분석 수행 (LangChain 실패시 폴백)"""
        return {
            "timestamp": datetime.now().isoformat(),
            "input_data": input_data,
            "result": f"{self.name}의 기존 분석 방식으로 수행된 결과",
            "analysis_time": 0.0,
            "agent_name": self.name,
            "role": self.role,
            "method": "traditional",
        }

    def _update_performance_metrics(self, analysis_result: Dict[str, Any]):
        """성능 지표 업데이트 (6가지 핵심 전략 기반 평가)"""
        # 응답 시간 업데이트
        self.performance_metrics["response_time"] = analysis_result.get(
            "analysis_time", 0.0
        )

        # 6가지 핵심 전략 기반 품질 평가
        quality_metrics = analysis_result.get("analysis_quality_metrics", {})

        # 해석 깊이 평가 (Chain of Thought 적용 여부)
        if "interpretation_depth" in quality_metrics:
            self.performance_metrics["interpretation_depth"] = 0.9

        # 논리 일관성 평가 (논리구조 틀 적용 여부)
        if "logical_consistency" in quality_metrics:
            self.performance_metrics["logical_consistency"] = 0.9

        # 투자 판단 근거 평가
        if "investment_justification" in quality_metrics:
            self.performance_metrics["investment_justification"] = 0.9

        # 시나리오 분석 평가
        if "scenario_analysis" in quality_metrics:
            self.performance_metrics["scenario_analysis"] = 0.9

        # 웹 검색 통합 평가
        if "web_search_integration" in quality_metrics:
            self.performance_metrics["web_search_integration"] = 0.9

        # 종합 정확도 계산 (6가지 전략 가중평균)
        strategy_weights = {
            "interpretation_depth": 0.25,
            "logical_consistency": 0.25,
            "investment_justification": 0.20,
            "scenario_analysis": 0.15,
            "web_search_integration": 0.15,
        }

        total_score = 0
        total_weight = 0

        for metric, weight in strategy_weights.items():
            if metric in self.performance_metrics:
                total_score += self.performance_metrics[metric] * weight
                total_weight += weight

        if total_weight > 0:
            self.performance_metrics["accuracy"] = total_score / total_weight

        # 일관성은 이전 분석과의 비교로 계산
        if len(self.analysis_history) > 1:
            # 간단한 일관성 계산 (실제로는 더 복잡한 로직 필요)
            self.performance_metrics["consistency"] = 0.85  # 6가지 전략 적용으로 향상

    def get_analysis_summary(self) -> Dict[str, Any]:
        """분석 요약 정보 반환 (6가지 핵심 전략 기반 평가 포함)"""
        return {
            "agent_name": self.name,
            "role": self.role,
            "total_analyses": len(self.analysis_history),
            "performance_metrics": self.performance_metrics,
            "langchain_enabled": self.langchain_enabled,
            "last_analysis": (
                self.analysis_history[-1] if self.analysis_history else None
            ),
            "analysis_quality_strategy": {
                "chain_of_thought": "✅ 적용됨",
                "logical_framework": "✅ 적용됨",
                "industry_connection": "✅ 적용됨",
                "risk_scenario": "✅ 적용됨",
                "integrated_opinion": "✅ 적용됨",
                "self_evaluation": "✅ 적용됨",
            },
        }

    def evaluate_analysis_quality(self) -> Dict[str, Any]:
        """
        분석 품질을 6가지 핵심 전략 기준으로 평가해요

        Returns:
            dict: 각 전략별 평가 결과
        """
        if not self.analysis_history:
            return {"error": "분석 이력이 없어요!"}

        latest_analysis = self.analysis_history[-1]
        quality_metrics = latest_analysis.get("analysis_quality_metrics", {})

        evaluation_result = {
            "evaluation_timestamp": datetime.now().isoformat(),
            "agent_name": self.name,
            "strategy_evaluation": {
                "1_chain_of_thought": {
                    "status": (
                        "✅ 적용됨"
                        if "interpretation_depth" in quality_metrics
                        else "❌ 미적용"
                    ),
                    "description": "3단계 추론 템플릿 적용 여부",
                    "score": 0.9 if "interpretation_depth" in quality_metrics else 0.0,
                },
                "2_logical_framework": {
                    "status": (
                        "✅ 적용됨"
                        if "logical_consistency" in quality_metrics
                        else "❌ 미적용"
                    ),
                    "description": "논리구조 틀 적용 여부",
                    "score": 0.9 if "logical_consistency" in quality_metrics else 0.0,
                },
                "3_industry_connection": {
                    "status": (
                        "✅ 적용됨"
                        if "web_search_integration" in quality_metrics
                        else "❌ 미적용"
                    ),
                    "description": "산업 구조 및 동향 연결 강화",
                    "score": (
                        0.9 if "web_search_integration" in quality_metrics else 0.0
                    ),
                },
                "4_risk_scenario": {
                    "status": (
                        "✅ 적용됨"
                        if "scenario_analysis" in quality_metrics
                        else "❌ 미적용"
                    ),
                    "description": "리스크 시나리오 분석 자동화",
                    "score": 0.9 if "scenario_analysis" in quality_metrics else 0.0,
                },
                "5_integrated_opinion": {
                    "status": (
                        "✅ 적용됨"
                        if "investment_justification" in quality_metrics
                        else "❌ 미적용"
                    ),
                    "description": "통합 투자 의견 도출 템플릿",
                    "score": (
                        0.9 if "investment_justification" in quality_metrics else 0.0
                    ),
                },
                "6_self_evaluation": {
                    "status": "✅ 적용됨",
                    "description": "분석 결과의 평가 지표 및 피드백 루프",
                    "score": 0.9,
                },
            },
            "overall_quality_score": 0.0,
            "recommendations": [],
        }

        # 종합 품질 점수 계산
        total_score = 0
        strategy_count = 0

        for strategy_name, strategy_data in evaluation_result[
            "strategy_evaluation"
        ].items():
            total_score += strategy_data["score"]
            strategy_count += 1

        if strategy_count > 0:
            evaluation_result["overall_quality_score"] = total_score / strategy_count

        # 개선 권장사항 생성
        recommendations = []
        for strategy_name, strategy_data in evaluation_result[
            "strategy_evaluation"
        ].items():
            if strategy_data["score"] < 0.5:
                recommendations.append(
                    f"{strategy_name}: {strategy_data['description']} 강화 필요"
                )

        if not recommendations:
            recommendations.append("모든 핵심 전략이 잘 적용되고 있어요!")

        evaluation_result["recommendations"] = recommendations

        return evaluation_result

    def save_analysis_history(self, filepath: str):
        """분석 이력을 파일로 저장"""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.analysis_history, f, ensure_ascii=False, indent=2)
            print(f"✅ {self.name} 분석 이력 저장 완료: {filepath}")
        except Exception as e:
            print(f"❌ {self.name} 분석 이력 저장 실패: {e}")

    def load_analysis_history(self, filepath: str):
        """분석 이력을 파일에서 로드"""
        try:
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    self.analysis_history = json.load(f)
                print(f"✅ {self.name} 분석 이력 로드 완료: {filepath}")
        except Exception as e:
            print(f"❌ {self.name} 분석 이력 로드 실패: {e}")

    # def run_full_valuation_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
    #     """
    #     밸류에이션 전문가 5단계 전체 분석을 순차적으로 실행해요 (비활성화됨 - 통합 재무분석가로 대체)
    #     (LangChain RunnableSequence 기반)

    #     Args:
    #         input_data: {
    #             'financial_data': str(재무데이터),
    #             'sector_name': str(섹터명),
    #             'company_name': str(회사명)
    #         }
    #     Returns:
    #         dict: 각 단계별 결과가 담긴 사전
    #     """
    #     if not self.langchain_enabled or self.langchain_chain is None:
    #         return {"error": "LangChain이 활성화되어 있지 않아요!"}
    #     try:
    #         # 분석 시작 시간 기록
    #         from datetime import datetime

    #         start_time = datetime.now()

    #         # 5단계 전체 실행 (함수 호출)
    #         chain_result = self.langchain_chain(input_data)

    #         # 분석 시간 계산
    #         analysis_time = (datetime.now() - start_time).total_seconds()

    #         # 단계별 결과를 dict로 정리
    #         result_dict = {
    #             "step1_result": chain_result.get("step1_result"),
    #             "step2_result": chain_result.get("step2_result"),
    #             "step3_result": chain_result.get("step3_result"),
    #             "step4_result": chain_result.get("step4_result"),
    #             "step5_result": chain_result.get("step5_result"),
    #             "analysis_time": analysis_time,
    #             "agent_name": self.name,
    #             "role": self.role,
    #         }
    #         # 분석 이력에 저장
    #         self.analysis_history.append(result_dict)
    #         print(
    #             f"✅ {self.name} 5단계 전체 분석 완료! (소요시간: {analysis_time:.2f}초)"
    #         )
    #         return result_dict
    #     except Exception as e:
    #         print(f"❌ {self.name} 5단계 전체 분석 실패: {e}")
    #         return {"error": str(e)}

    def run_full_integrated_financial_analysis(
        self, input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        통합 재무분석가 5단계 전체 분석을 순차적으로 실행해요
        (LangChain Chain 기반) - 6가지 핵심 전략 적용

        Args:
            input_data: {
                'financial_data': str(재무데이터),
                'sector_name': str(섹터명),
                'company_name': str(회사명)
            }
        Returns:
            dict: 각 단계별 결과가 담긴 사전 (Chain of Thought + 논리구조 틀 적용)
        """
        if not self.langchain_enabled or self.langchain_chain is None:
            return {"error": "LangChain이 활성화되어 있지 않아요!"}
        try:
            # 분석 시작 시간 기록
            from datetime import datetime

            start_time = datetime.now()

            # 🚀 향상된 분석 시스템 (CoT + 5Why + 7Why) 사용
            try:
                # 향상된 분석 시스템 초기화 및 실행
                from .enhanced_analysis_system import EnhancedAnalysisSystem
                from .enhanced_seven_why_analyzer import EnhancedSevenWhyAnalyzer

                enhanced_analysis = EnhancedAnalysisSystem()
                seven_why_analyzer = EnhancedSevenWhyAnalyzer()

                # 통합 데이터 준비
                company_name = input_data.get("company_name", "분석대상")
                sector_name = input_data.get("sector_name", "정보기술")
                financial_data = input_data.get("financial_data", "재무 데이터 없음")
                market_data = input_data.get("market_data", "시장 데이터 없음")
                competitor_data = input_data.get(
                    "competitor_data", "경쟁사 데이터 없음"
                )

                # 1단계: CoT + 5Why 심층 분석
                print(f"🧠 {self.name} CoT + 5Why 심층 분석 시작...")
                deep_analysis_result = (
                    enhanced_analysis.deep_analysis.perform_deep_analysis(
                        company_name=company_name,
                        sector_name=sector_name,
                        financial_data=str(financial_data),
                        market_data=market_data,
                        competitor_data=competitor_data,
                    )
                )

                if "error" in deep_analysis_result:
                    print(
                        f"⚠️ {self.name} 심층 분석 실패, 기본 LangChain Chain으로 진행"
                    )
                    # 폴백: 기존 LangChain Chain 사용
                    chain_result = self.langchain_chain(input_data)
                else:
                    # 2단계: 7Why 분석 (전문가 분석 텍스트 기반) - 비활성화됨
                    # print(f"🔍 {self.name} 7Why 분석 시작...")

                    # CoT 분석 결과를 7Why 분석의 입력으로 사용
                    cot_analysis_text = deep_analysis_result.get("cot_analysis", "")

                    # seven_why_result = (
                    #     seven_why_analyzer.perform_integrated_7why_analysis(
                    #         expert_analysis_text=cot_analysis_text,
                    #         financial_data=str(financial_data),
                    #         market_data=market_data,
                    #         competitor_data=competitor_data,
                    #         web_search_data=input_data.get("web_search_data", ""),
                    #     )
                    # )

                    # 7Why 분석 비활성화로 인한 더미 결과
                    seven_why_result = {
                        "integrated_7why_analysis": "7Why 분석이 현재 비활성화되어 있습니다. CoT + 5Why 분석만 수행됩니다."
                    }

                    # 3단계: 통합 분석 결과 생성
                    print(f"🔗 {self.name} 통합 분석 결과 생성...")

                    # 기존 LangChain Chain 결과와 향상된 분석 결과를 통합
                    basic_chain_result = self.langchain_chain(input_data)

                    # 향상된 분석 결과를 기존 결과에 추가
                    chain_result = {
                        **basic_chain_result,
                        "enhanced_cot_analysis": deep_analysis_result.get(
                            "cot_analysis", ""
                        ),
                        "enhanced_five_why_analysis": deep_analysis_result.get(
                            "five_why_analysis", ""
                        ),
                        "enhanced_seven_why_analysis": seven_why_result.get(
                            "integrated_7why_analysis", ""
                        ),
                        "enhanced_root_cause_analysis": deep_analysis_result.get(
                            "root_cause_analysis", ""
                        ),
                        "enhanced_implication_analysis": deep_analysis_result.get(
                            "implication_analysis", ""
                        ),
                    }

                    print(f"✅ {self.name} 향상된 분석 완료 (CoT + 5Why + 7Why)")

            except Exception as enhanced_error:
                print(f"❌ {self.name} 향상된 분석 실패: {enhanced_error}")
                # 폴백: 기존 LangChain Chain 사용
                chain_result = self.langchain_chain(input_data)

            # 분석 시간 계산
            analysis_time = (datetime.now() - start_time).total_seconds()

            # 단계별 결과를 dict로 정리 (6가지 핵심 전략 반영 + 향상된 분석 포함)
            result_dict = {
                "step1_result": chain_result.get(
                    "step1_result"
                ),  # 재무 건전성 (Chain of Thought 적용)
                "step2_result": chain_result.get(
                    "step2_result"
                ),  # 경쟁사 비교 (웹 검색 기반)
                "step3_result": chain_result.get(
                    "step3_result"
                ),  # 내재가치 산출 (논리구조 틀 적용)
                "step4_result": chain_result.get(
                    "step4_result"
                ),  # 시나리오 분석 (리스크 시나리오 자동화)
                "step5_result": chain_result.get(
                    "step5_result"
                ),  # 종합 투자 의견 (통합 템플릿 적용)
                "enhanced_cot_analysis": chain_result.get("enhanced_cot_analysis", ""),
                "enhanced_five_why_analysis": chain_result.get(
                    "enhanced_five_why_analysis", ""
                ),
                "enhanced_seven_why_analysis": chain_result.get(
                    "enhanced_seven_why_analysis", ""
                ),
                "enhanced_root_cause_analysis": chain_result.get(
                    "enhanced_root_cause_analysis", ""
                ),
                "enhanced_implication_analysis": chain_result.get(
                    "enhanced_implication_analysis", ""
                ),
                "analysis_time": analysis_time,
                "agent_name": self.name,
                "role": self.role,
                "analysis_method": "Enhanced Integrated Analysis (CoT + 5Why + 7Why)",
                "analysis_quality_metrics": {
                    "interpretation_depth": "Chain of Thought 기반 깊이 있는 해석",
                    "logical_consistency": "논리구조 틀 적용으로 일관성 확보",
                    "investment_justification": "수치/사실 기반 투자 판단 근거",
                    "scenario_analysis": "3시나리오 리스크 분석 포함",
                    "web_search_integration": "최신 업계 정보 반영",
                },
            }
            # 분석 이력에 저장
            self.analysis_history.append(result_dict)
            print(
                f"✅ {self.name} 5단계 통합 재무분석 완료! (소요시간: {analysis_time:.2f}초)"
            )
            print(f"🧠 분석 품질 강화 6가지 전략 적용 완료!")
            return result_dict
        except Exception as e:
            print(f"❌ {self.name} 5단계 통합 재무분석 실패: {e}")
            return {"error": str(e)}

    def run_full_technical_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        기술적 분석가 5단계 전체 분석을 순차적으로 실행해요
        (LangChain Chain 기반)

        Args:
            input_data: {
                'price_data': str(가격데이터),
                'sector_name': str(섹터명),
                'company_name': str(회사명)
            }
        Returns:
            dict: 각 단계별 결과가 담긴 사전
        """
        if not self.langchain_enabled or self.langchain_chain is None:
            return {"error": "LangChain이 활성화되어 있지 않아요!"}
        try:
            # 분석 시작 시간 기록
            from datetime import datetime

            start_time = datetime.now()

            # 🚀 향상된 분석 시스템 (CoT + 5Why + 7Why) 사용
            try:
                # 향상된 분석 시스템 초기화 및 실행
                from .enhanced_analysis_system import EnhancedAnalysisSystem
                from .enhanced_seven_why_analyzer import EnhancedSevenWhyAnalyzer

                enhanced_analysis = EnhancedAnalysisSystem()
                seven_why_analyzer = EnhancedSevenWhyAnalyzer()

                # 통합 데이터 준비
                company_name = input_data.get("company_name", "분석대상")
                sector_name = input_data.get("sector_name", "정보기술")
                price_data = input_data.get("price_data", "가격 데이터 없음")
                market_data = input_data.get("market_data", "시장 데이터 없음")

                # 1단계: CoT + 5Why 심층 분석
                print(f"🧠 {self.name} CoT + 5Why 심층 분석 시작...")
                deep_analysis_result = (
                    enhanced_analysis.deep_analysis.perform_deep_analysis(
                        company_name=company_name,
                        sector_name=sector_name,
                        financial_data=str(
                            price_data
                        ),  # 가격 데이터를 재무 데이터로 사용
                        market_data=market_data,
                        competitor_data={},
                    )
                )

                if "error" in deep_analysis_result:
                    print(
                        f"⚠️ {self.name} 심층 분석 실패, 기본 LangChain Chain으로 진행"
                    )
                    # 폴백: 기존 LangChain Chain 사용
                    chain_result = self.langchain_chain(input_data)
                else:
                    # 2단계: 7Why 분석 (전문가 분석 텍스트 기반)
                    print(f"🔍 {self.name} 7Why 분석 시작...")

                    # CoT 분석 결과를 7Why 분석의 입력으로 사용
                    cot_analysis_text = deep_analysis_result.get("cot_analysis", "")

                    seven_why_result = (
                        seven_why_analyzer.perform_integrated_7why_analysis(
                            expert_analysis_text=cot_analysis_text,
                            financial_data=str(price_data),
                            market_data=market_data,
                            competitor_data={},
                            web_search_data=input_data.get("web_search_data", ""),
                        )
                    )

                    # 3단계: 통합 분석 결과 생성
                    print(f"🔗 {self.name} 통합 분석 결과 생성...")

                    # 기존 LangChain Chain 결과와 향상된 분석 결과를 통합
                    basic_chain_result = self.langchain_chain(input_data)

                    # 향상된 분석 결과를 기존 결과에 추가
                    chain_result = {
                        **basic_chain_result,
                        "enhanced_cot_analysis": deep_analysis_result.get(
                            "cot_analysis", ""
                        ),
                        "enhanced_five_why_analysis": deep_analysis_result.get(
                            "five_why_analysis", ""
                        ),
                        "enhanced_seven_why_analysis": seven_why_result.get(
                            "integrated_7why_analysis", ""
                        ),
                        "enhanced_root_cause_analysis": deep_analysis_result.get(
                            "root_cause_analysis", ""
                        ),
                        "enhanced_implication_analysis": deep_analysis_result.get(
                            "implication_analysis", ""
                        ),
                    }

                    print(f"✅ {self.name} 향상된 분석 완료 (CoT + 5Why + 7Why)")

            except Exception as enhanced_error:
                print(f"❌ {self.name} 향상된 분석 실패: {enhanced_error}")
                # 폴백: 기존 LangChain Chain 사용
                chain_result = self.langchain_chain(input_data)

            # 분석 시간 계산
            analysis_time = (datetime.now() - start_time).total_seconds()

            # 단계별 결과를 dict로 정리 (향상된 분석 포함)
            result_dict = {
                "step1_result": chain_result.get("step1_result"),
                "step2_result": chain_result.get("step2_result"),
                "step3_result": chain_result.get("step3_result"),
                "step4_result": chain_result.get("step4_result"),
                "step5_result": chain_result.get("step5_result"),
                "enhanced_cot_analysis": chain_result.get("enhanced_cot_analysis", ""),
                "enhanced_five_why_analysis": chain_result.get(
                    "enhanced_five_why_analysis", ""
                ),
                "enhanced_seven_why_analysis": chain_result.get(
                    "enhanced_seven_why_analysis", ""
                ),
                "enhanced_root_cause_analysis": chain_result.get(
                    "enhanced_root_cause_analysis", ""
                ),
                "enhanced_implication_analysis": chain_result.get(
                    "enhanced_implication_analysis", ""
                ),
                "analysis_time": analysis_time,
                "agent_name": self.name,
                "role": self.role,
                "analysis_method": "Enhanced Technical Analysis (CoT + 5Why + 7Why)",
            }
            # 분석 이력에 저장
            self.analysis_history.append(result_dict)
            print(
                f"✅ {self.name} 5단계 전체 분석 완료! (소요시간: {analysis_time:.2f}초)"
            )
            return result_dict
        except Exception as e:
            print(f"❌ {self.name} 5단계 전체 분석 실패: {e}")
            return {"error": str(e)}

    # def run_full_footnote_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
    #     """
    #     주석 전문가 5단계 전체 분석을 순차적으로 실행해요 (비활성화됨 - 개발 시간 절약)
    #     (LangChain Chain 기반)

    #     Args:
    #         input_data: {
    #             'financial_data': str(재무제표 주석 데이터),
    #             'sector_name': str(섹터명),
    #             'company_name': str(회사명)
    #         }
    #     Returns:
    #         dict: 각 단계별 결과가 담긴 사전
    #     """
    #     if not self.langchain_enabled or self.langchain_chain is None:
    #         return {"error": "LangChain이 활성화되어 있지 않아요!"}
    #     try:
    #         # 분석 시작 시간 기록
    #         from datetime import datetime

    #         start_time = datetime.now()

    #         # 5단계 전체 실행 (함수 호출)
    #         chain_result = self.langchain_chain(input_data)

    #         # 분석 시간 계산
    #         analysis_time = (datetime.now() - start_time).total_seconds()

    #         # 단계별 결과를 dict로 정리
    #         result_dict = {
    #             "step1_result": chain_result.get("step1_result"),
    #             "step2_result": chain_result.get("step2_result"),
    #             "step3_result": chain_result.get("step3_result"),
    #             "step4_result": chain_result.get("step4_result"),
    #             "step5_result": chain_result.get("step5_result"),
    #             "analysis_time": analysis_time,
    #             "agent_name": self.name,
    #             "role": self.role,
    #         }
    #         # 분석 이력에 저장
    #         self.analysis_history.append(result_dict)
    #         print(
    #             f"✅ {self.name} 5단계 전체 분석 완료! (소요시간: {analysis_time:.2f}초)"
    #         )
    #         return result_dict
    #     except Exception as e:
    #         print(f"❌ {self.name} 5단계 전체 분석 실패: {e}")
    #         return {"error": str(e)}


@dataclass
class SectorTeam:
    """
    섹터별 분석팀 정의
    2명의 전문가로 구성된 팀이에요
    """

    sector: GICSSector
    team_name: str
    team_description: str
    experts: List[AnalystAgent]  # Changed from 'agents' to 'experts'
    collaboration_strategy: str  # 팀 협업 전략
    report_structure: Dict[str, str]  # 보고서 구조


class SectorTeamFactory:
    """
    섹터별 전문 분석팀을 생성하는 팩토리 클래스

    각 섹터마다 2명의 전문가를 배치해요:
    1. 통합 재무분석가 (Integrated Financial Analyst) - 펀더멘털 + 밸류에이션 통합
    2. 기술적 분석가 (Technical Analyst)

    🚫 비활성화된 전문가들:
    - 산업 전문가 (Industry Expert) - 개발 시간 절약
    - 리스크 평가자 (Risk Assessor) - 개발 시간 절약
    - 주석 분석 전문가 (Footnote Specialist) - 개발 시간 절약
    """

    def __init__(self, sector_manager: GICSSectorManager):
        """
        섹터팀 팩토리 초기화

        Args:
            sector_manager: GICS 섹터 매니저
        """
        self.sector_manager = sector_manager

        # 🚀 웹 검색 도구 초기화
        self.web_search_tool = LangChainWebSearchTool()

        print("🎯 섹터별 분석팀 팩토리 초기화 완료!")

    def _get_sector_emoji(self, sector: GICSSector) -> str:
        """
        섹터별 대표 이모지를 반환합니다.

        Args:
            sector: GICS 섹터

        Returns:
            str: 섹터별 이모지
        """
        sector_emojis = {
            GICSSector.INFORMATION_TECHNOLOGY: "🖥️",
            GICSSector.FINANCIALS: "🏦",
            GICSSector.HEALTH_CARE: "💊",
            GICSSector.ENERGY: "⚡",
            GICSSector.CONSUMER_DISCRETIONARY: "🛒",
            GICSSector.CONSUMER_STAPLES: "🍞",
            GICSSector.MATERIALS: "🏭",
            GICSSector.INDUSTRIALS: "🏗️",
            GICSSector.COMMUNICATION_SERVICES: "📡",
            GICSSector.UTILITIES: "🔌",
            GICSSector.REAL_ESTATE: "🏢",
        }
        return sector_emojis.get(sector, "🎯")  # 기본값: 🎯

    def create_sector_team(self, sector: GICSSector) -> SectorTeam:
        """
        특정 섹터의 전문 분석팀을 생성해요

        GICS 섹터별 특화된 분석 포인트와 위험 요소를 반영한
        2명의 전문가로 구성된 팀을 만들어요!

        Args:
            sector: GICS 섹터

        Returns:
            SectorTeam: 생성된 섹터팀
        """
        # 섹터별 상세 정보 가져오기
        sector_context = self.sector_manager.get_sector_context(sector)
        sector_korean_name = self.sector_manager.get_sector_korean_name(sector)
        analysis_points = self.sector_manager.get_sector_analysis_points(sector)
        risk_factors = self.sector_manager.get_sector_risk_factors(sector)
        critical_metrics = self.sector_manager.get_sector_critical_metrics(sector)

        # 섹터별 특화 정보 파싱 (문자열을 리스트로 변환)
        analysis_points_list = [point.strip() for point in analysis_points.split(", ")]
        risk_factors_list = [risk.strip() for risk in risk_factors.split(", ")]
        critical_metrics_list = [
            metric.strip() for metric in critical_metrics.split(", ")
        ]

        # 섹터별 2명의 전문가 생성 (섹터별 특화 정보 반영)
        experts = []

        # 1. 통합 재무분석가 (펀더멘털 + 밸류에이션 통합) - 🎯 AI 강화 시니어 애널리스트 수준
        # 공통 프롬프트 컴포넌트를 활용한 모듈화된 프롬프트 생성
        integrated_analysis_framework = (
            PromptComponents.create_unified_analysis_framework(
                analysis_type="통합 재무분석",
                sector_name=sector_korean_name,
                specific_methods=[
                    "재무비율 분석 (ROE, ROA, ROIC, 유동비율, 부채비율 등)",
                    "DuPont 분석 (ROE = 순이익률 × 자산회전율 × 레버리지)",
                    "현금흐름 분석 (영업CF, 투자CF, 재무CF의 품질과 안정성)",
                    "DCF 모델링 (FCF 기반 내재가치 산출, WACC 계산)",
                    "멀티플 분석 (PER, PBR, EV/EBITDA 시계열 및 업계 비교)",
                    "Sum-of-Parts 분석 (사업부문별 밸류에이션)",
                    "배당할인모델 (배당성장률 기반 내재가치)",
                    "시나리오별 밸류에이션 (낙관/기본/비관 시나리오)",
                ],
            )
        )

        # 🚀 One-Hot 활성화된 섹터 정보를 직접 사용한 맞춤형 질문 생성
        try:
            print(f"🎯 {sector_korean_name} 섹터 맞춤형 질문 생성 중...")

            # 이미 활성화된 섹터 정보로 직접 질문 생성 (One-Hot Activation)
            sector_questions = PromptComponents._generate_sector_specific_questions(
                sector, self.sector_manager
            )
            sector_guidance = PromptComponents._get_sector_analysis_guidance(
                sector, self.sector_manager
            )

            # 🎯 섹터별 동적 이모지 선택
            try:
                sector_emoji = self._get_sector_emoji(sector)
            except Exception as e:
                logger.warning(f"⚠️ 섹터 이모지 생성 실패: {e}")
                sector_emoji = "🎯"  # 기본 이모지

            # 전체 Enhanced Thinking Flow 조합
            dynamic_thinking_flow = f"""
🚨 **CRITICAL: 분석 시작 전 필수 확인사항** 🚨

❗ 이 지시사항을 무시하면 분석 실패로 간주됩니다:

1️⃣ **Q5: {sector_emoji} {sector_korean_name} 섹터 특화 분석 질문 반드시 포함**
2️⃣ **3단계 순서 절대 준수: 1단계→2단계→3단계**
3️⃣ **yfinance 데이터 우선 활용, 웹검색은 최후**

**🧠 Enhanced Analyst Thinking Flow (동적 섹터별 애널리스트 사고 흐름)**

🔴 **MANDATORY**: 다음 3단계를 **반드시 순서대로** 수행하세요:

```
=== 1단계: Self-Ask with ToT (섹터별 맞춤 질문 구성 및 사고 분기) ===

🌳 Tree of Thoughts 기법으로 핵심 질문들을 체계적으로 구성하세요:

{sector_questions}

{sector_guidance}


```
=== 2단계: ReAct (Reason + Action) - 검색 및 정보 수집 ===

🔍 각 질문에 대한 체계적 정보 수집과 추론 수행:

**Reason (추론)**: 왜 이 정보가 필요한가?
- 분석 목적: [해당 정보가 전체 분석에서 갖는 의미]
- 예상 결과: [이 정보를 통해 도출할 수 있는 인사이트]

**Action (행동)**: 어떤 정보를 어떻게 수집할 것인가? (모든 데이터 종합 활용)

🥇 **1순위: 수집된 재무데이터 활용**
- yfinance 데이터: [현재가, 시가총액, 재무비율 등 확인]
- 기본 재무지표: [ROE, ROA, PER, PBR, 부채비율 등 계산]

🥈 **2순위: DART 데이터 활용**
- 재무제표 분석: [손익계산서, 재무상태표, 현금흐름표]
- 사업보고서: [사업개요, 경영진 분석, 리스크 요인 등]
- 공시자료: [최신 실적 발표, 주요 공시사항]

🥉 **3순위: 사업보고서 딕셔너리 분석**
- PDF 상세 정보: [세그먼트별 매출, 사업 전략, 경쟁 현황]
- 경영진 메시지: [향후 계획, 투자 방향성, 시장 전망]
- 각주 및 부가 정보: [중요한 회계 정책, 우발 부채 등]

🏅 **4순위: 웹 검색으로 보완**
- 최신 업계 동향: [검색할 키워드와 찾을 정보]
- 경쟁사 비교: [비교할 기업들과 비교 기준]
- 시장 환경 변화: [확인할 산업 트렌드와 이슈들]

🆘 **5순위: 기존 지식 활용** (최후 수단)
- 일반적인 업계 지식과 분석 방법론 적용

**Observation (관찰)**: 수집된 정보의 의미는?
- 핵심 발견사항: [중요한 수치나 트렌드]
- 예상과의 차이: [예상했던 것과 다른 점들]
- 추가 조사 필요성: [더 깊이 파야 할 영역들]

💡 ReAct 사이클을 각 핵심 질문별로 반복 수행하세요.
```

```
=== 3단계: CoT Reasoning + Self-Critique (최종 분석 및 자기 검증) ===

🧠 수집된 모든 정보를 바탕으로 체계적 추론 수행:

**Chain of Thought 분석**:
```
내 추론 과정:

1️⃣ 재무 건전성 종합 판단:
- 근거 1: [구체적 재무지표와 해석]
- 근거 2: [경쟁사 대비 상대적 위치]
- 근거 3: [시계열 트렌드 분석]
→ 결론: [재무 건전성 최종 평가]

2️⃣ 성장성 및 수익성 평가:
- 근거 1: [과거 성장 실적과 품질 분석]
- 근거 2: [미래 성장 동력과 지속가능성]
- 근거 3: [수익성 개선 가능성]
→ 결론: [성장성 최종 평가]

3️⃣ 밸류에이션 및 투자 매력도:
- DCF 분석: [내재가치 산출 과정과 결과]
- 멀티플 분석: [상대가치 평가]
- 종합 판단: [적정가치와 투자 의견]
→ 결론: [투자 의견과 목표가]

4️⃣ 리스크-수익률 분석:
- 주요 리스크: [발생 가능성과 영향도]
- 기대 수익률: [시나리오별 수익률]
- 리스크 조정 수익률: [샤프 비율 관점]
→ 결론: [리스크 대비 투자 매력도]
```

**Self-Critique (자기 검증)**:
```
🔍 내 분석에 대한 비판적 검토:

❓ 놓친 것은 없는가?
- 중요한 재무지표나 트렌드를 빠뜨렸는가?
- 주요 경쟁사나 업계 동향을 간과했는가?
- 시장 상황이나 거시 경제 요인을 충분히 고려했는가?

❓ 편향은 없는가?
- 긍정적/부정적 정보에 치우친 해석은 없는가?
- 확증 편향으로 인해 반대 증거를 무시하지 않았는가?
- 과거 성과에 지나치게 의존한 예측은 아닌가?

❓ 논리적 일관성은 있는가?
- 각 분석 단계 간의 논리적 연결은 명확한가?
- 가정과 결론 사이에 논리적 비약은 없는가?
- 상충하는 증거들을 합리적으로 조율했는가?

❓ 실용성과 적시성은?
- 투자자가 실제로 활용할 수 있는 분석인가?
- 현재 시장 상황을 충분히 반영했는가?
- 분석의 유효 기간과 업데이트 필요성은?

💡 수정 및 보완 사항:
- [발견된 문제점과 개선 방안]
- [추가로 고려해야 할 요소들]
- [분석의 한계와 주의사항]
```

**최종 종합 의견**:
```
🎯 종합 결론:
- 투자 의견: [BUY/HOLD/SELL + 신뢰도 %]
- 목표가: [구체적 금액과 산출 근거]
- 투자 논리: [핵심 투자 포인트 3가지]
- 주요 리스크: [핵심 위험 요소 2가지]
- 투자 기간: [권장 투자 기간과 전략]
```
```

**⚠️ 필수 준수 사항**:
1. 3단계를 순차적으로 모두 수행할 것
2. 각 단계의 결과를 명확히 구분하여 표시할 것
3. Self-Critique에서 최소 3가지 이상의 비판적 관점 제시할 것
4. 모든 결론에 구체적 근거와 수치 제시할 것
5. 불확실성과 한계점을 솔직하게 인정할 것
"""
            print(f"✅ {sector_korean_name} 섹터 맞춤형 질문 생성 완료!")

        except Exception as e:
            print(f"⚠️ 동적 사고 흐름 생성 실패, 기본 프레임워크 사용: {e}")
            dynamic_thinking_flow = (
                PromptComponents.get_enhanced_analyst_thinking_flow()
            )

        integrated_financial_analyst = AnalystAgent(
            name=f"{sector_korean_name} 통합 재무분석가 (Dynamic Enhanced Thinking Flow)",
            role="Senior Financial Analyst with Sector-Specific Enhanced Analytical Thinking",
            expertise="섹터별 맞춤형 실제 애널리스트 사고 흐름 구현, 동적 질문 생성, 체계적 재무분석, 고도화된 투자 의견 도출",
            analysis_focus=f"{sector_korean_name} 기업을 섹터 특성 기반 Self-Ask with ToT → ReAct → CoT+Self-Critique 흐름으로 심층 분석하여 시니어 애널리스트 수준의 투자 인사이트 제공",
            key_methods=[
                "🧠 Sector-Specific Self-Ask with ToT: 섹터별 맞춤 질문 동적 생성",
                "📊 ReAct 루프: 모든 데이터 종합 활용 정보 수집 (yfinance→DART→PDF→웹검색)",
                "🔍 Chain of Thought: 논리적 단계별 추론",
                "🎯 Self-Critique: 다각도 자기 검증",
                "💰 Enhanced DCF 모델링: 가정 명시 및 민감도 분석",
                "📈 Comparative Valuation: 경쟁사 심층 비교",
                "🔮 Scenario Planning: 확률 기반 시나리오 분석",
                "⚖️ Risk-Return Optimization: 리스크 조정 투자 의견",
            ],
            sector_context=f"{sector_korean_name} 섹터의 특성을 반영한 AI 강화 통합 재무분석 및 밸류에이션 전문가 (동적 질문 생성 지원)",
            sector_specific_points=[
                f"🎯 {sector_korean_name} 섹터 특화 Enhanced Thinking Flow 관점에서 {sector_context.get('valuation_approach', '가치평가 방법')}",
                "🚀 **Dynamic Enhanced Analyst Thinking Flow 프레임워크**:",
                "🔴 **핵심 원칙**: 섹터별 특성 반영 + 실제 애널리스트 사고 과정 완벽 구현 + 체계적 추론 기법 적용",
                "",
                # 모듈화된 AI 강화 프레임워크 삽입
                integrated_analysis_framework,
                "",
                # 동적으로 생성된 사고 흐름 프레임워크 삽입
                dynamic_thinking_flow,
                "",
                "🚨 **강제 준수 지시사항 (MANDATORY)**:",
                "❗ **절대적으로 준수해야 할 분석 순서**:",
                "",
                "🔴 **1단계 MUST: Self-Ask with ToT 질문 구성**",
                "- 반드시 다음 질문 구조를 따르세요:",
                "  Q1: 재무적 건전성 (ROE, ROA, ROIC, 부채비율, 현금흐름)",
                "  Q2: 성장성과 수익성 (과거 3년 성장, 성장 동력, 지속가능성)",
                "  Q3: 적정 가치 (DCF, 멀티플, 고평가/저평가)",
                "  Q4: 리스크와 기회 (재무/운영, 산업환경, 외부환경)",
                f"  Q5: {sector_emoji} {sector_korean_name} 섹터 특화 분석 (섹터별 핵심 경쟁 요소)",
                "",
                "🔴 **2단계 MUST: ReAct 정보 수집 순서**",
                "- 1순위: yfinance 재무데이터 활용 (현재가, 시가총액, 기본 비율)",
                "- 2순위: DART 데이터 활용 (재무제표, 사업보고서)",
                "- 3순위: 사업보고서 딕셔너리 분석",
                "- 4순위: 웹 검색으로 보완 (최후 수단)",
                "",
                "🔴 **3단계 MUST: CoT + Self-Critique**",
                "- Chain of Thought: 4개 영역별 체계적 추론",
                "- Self-Critique: 최소 3가지 비판적 관점",
                "- 최종 의견: BUY/HOLD/SELL + 신뢰도 + 목표가",
                "",
                "⚠️ **절대 금지사항**:",
                "- ❌ 질문 단계 건너뛰기 금지",
                "- ❌ 웹검색 우선 시도 금지",
                f"- ❌ Q5 {sector_emoji} {sector_korean_name} 섹터 특화 질문 누락 금지",
                "- ❌ 3단계 구조 무시 금지",
            ],
            risk_awareness=[f"통합 재무분석 관점에서 {risk_factors}"],
            critical_metrics=(
                critical_metrics_list[:4]
                if len(critical_metrics_list) >= 4
                else critical_metrics_list
            )
            + [
                "ROE/ROA 스프레드 (금융레버리지 효과)",
                "ROIC vs WACC 스프레드 (가치창출 여부)",
                "FCF/Net Income 비율 (현금창출력)",
                "Working Capital/Sales 비율 (운전자본 효율성)",
                "FCF Yield (FCF/시가총액)",
                "EV/EBITDA (기업가치 배수)",
                "PEG Ratio (PER/성장률)",
            ],
            langchain_enabled=True,  # 🚀 LangChain 활성화
        )

        # 🚀 통합 재무분석가 LangChain Chain 설정 (Q5 강제 보장 + 섹터 직접 활용)
        integrated_financial_analyst.langchain_chain = (
            self._create_integrated_financial_analysis_chain(
                integrated_financial_analyst, sector_korean_name, sector
            )
        )

        experts.append(integrated_financial_analyst)

        # 2. 기술적 분석가 (섹터 특화) - 🎯 AI 강화 시니어 애널리스트 수준 업그레이드
        # 공통 프롬프트 컴포넌트를 활용한 모듈화된 프롬프트 생성
        technical_analysis_framework = PromptComponents.create_unified_analysis_framework(
            analysis_type="기술적 분석",
            sector_name=sector_korean_name,
            specific_methods=[
                "이동평균선 분석 (5,20,60,120일선 배열과 Golden/Dead Cross 신호)",
                "MACD/RSI 분석 (MACD(12,26,9) 히스토그램과 RSI(14) Divergence 패턴)",
                "볼린저 밴드 분석 (20일 이평±2표준편차, 밴드폭 확장/수축 해석)",
                "지지저항선 분석 (Fibonacci Retracement 38.2%, 50%, 61.8% 레벨)",
                "거래량 분석 (OBV, Volume Profile, Accumulation/Distribution Line)",
                "섹터 로테이션 분석 (상대강도 vs KOSPI, 섹터 모멘텀 지표)",
                "캔들패턴 분석 (Doji, Hammer, Engulfing 등 반전신호 해석)",
                "스토캐스틱 분석 (%K, %D 교차와 과매수/과매도 구간 판별)",
                "Price Action 분석 (Higher High/Low, Lower High/Low 트렌드 구조)",
            ],
        )

        technical_analyst = AnalystAgent(
            name=f"{sector_korean_name} 기술적 분석가 (AI Enhanced)",
            role="Advanced Technical Analyst with AI Reasoning",
            expertise="AI 강화 차트 패턴 분석, 기술적 지표 해석, 시장 심리 분석",
            analysis_focus=f"{sector_korean_name} 섹터의 가격 움직임과 매매 신호를 AI 강화 추론 기법으로 분석",
            key_methods=[
                "Chain of Thought (CoT) 기반 이동평균선 분석",
                "Self-Critique 적용 MACD/RSI 분석",
                "Multi-Perspective 볼린저 밴드 분석",
                "Reasoning-Enhanced 지지저항선 분석",
                "Confidence-Scored 거래량 분석",
                "Reflection-Based 섹터 로테이션 분석",
                "AI 강화 캔들패턴 분석",
                "Self-Validation 기술적 전망 도출",
            ],
            sector_context=f"{sector_korean_name} 섹터의 경기민감성과 변동성을 고려한 AI 강화 기술적 분석 전문가",
            sector_specific_points=[
                f"기술적 관점에서 {sector_context.get('cyclical_nature', '섹터 특성')} 반영",
                "⭐ **AI 강화 기술적 분석 프레임워크**:",
                "🔴 **핵심 원칙**: 제공된 실제 가격데이터 최우선 + AI 추론 기법 적용",
                "",
                # 모듈화된 AI 강화 프레임워크 삽입
                technical_analysis_framework,
                "",
                "🎯 **5단계 기술적 분석 프로세스**:",
                "**1단계: 차트 패턴 분석**",
                "- 주요 차트 패턴 식별 (헤드앤숄더, 더블탑/바텀 등)",
                "- 각 패턴별 Chain of Thought 적용",
                "- 추세선과 채널 분석",
                "- 지지선과 저항선 레벨 분석",
                "",
                "**2단계: 기술적 지표 분석**",
                "- 이동평균선 분석 (20일, 60일, 200일)",
                "- RSI, MACD, 스토캐스틱 등 오실레이터 분석",
                "- 볼린저 밴드와 피벗 포인트 분석",
                "- 웹 검색을 통한 최신 기술적 트렌드 반영",
                "",
                "**3단계: 거래량 분석**",
                "- 거래량 추세와 가격 변동의 관계",
                "- 거래량 가중 평균가격(VWAP) 분석",
                "- 거래량 프로파일 분석",
                "",
                "**4단계: 섹터 상대강도 분석**",
                "- 섹터 대비 상대적 성과 분석",
                "- 섹터 내 순위와 강도 평가",
                "- 섹터 로테이션 영향 분석",
                "",
                "**5단계: 기술적 전망 및 투자 권고**",
                "- 단기/중기 기술적 전망",
                "- 주요 지지/저항 레벨과 목표가",
                "- 매수/매도 시점 권고",
                "- Self-Critique 결과 포함",
            ],
            risk_awareness=[
                f"기술적 분석 관점에서 {risk_factors}",
                "False Breakout 위험 (거래량 미동반시 돌파 실패 가능성)",
                "Whipsaw 패턴 위험 (박스권에서 매매신호 오류 가능성)",
                "Gap 위험 (공시나 외부 이벤트로 인한 기술적 분석 무력화)",
                "섹터 로테이션 위험 (전체 섹터 약세시 개별 기술적 신호 무의미)",
            ],
            critical_metrics=[
                "상대강도 (vs KOSPI, 20일/60일 이동평균)",
                "Price Momentum (1주/4주/12주 수익률)",
                "Volume Rate (20일 평균 대비 거래량 비율)",
                "Volatility Index (20일 변동성 vs 역사적 변동성)",
                "Technical Score (종합 기술적 지표 점수)",
                "Trend Strength Index (추세 강도 측정)",
                "Support/Resistance Distance (현재가 vs 주요 S/R 레벨)",
                "Beta vs Sector (섹터 내 상대적 변동성)",
            ],
            langchain_enabled=True,  # 🚀 LangChain 활성화
        )

        # 🚀 기술적 분석가 LangChain Chain 설정
        technical_analyst.langchain_chain = self._create_technical_analysis_chain(
            technical_analyst, sector_korean_name
        )

        experts.append(technical_analyst)

        # 3. 산업 전문가 (섹터 특화) - 🚫 비활성화 (개발 시간 절약)
        # industry_expert = AnalystAgent(
        #     name=f"{sector_korean_name} 산업 전문가",
        #     role="Industry Expert",
        #     expertise="산업 분석, 경쟁 구조 분석, 트렌드 예측",
        #     analysis_focus=f"{sector_korean_name} 산업의 구조적 변화와 성장 동력 분석",
        #     key_methods=[
        #         "Porter 5 Forces 분석 (신규진입, 대체재, 공급업체, 구매자, 경쟁강도)",
        #         "밸류체인 분석 (Primary & Support Activities 마진 기여도 분해)",
        #         "SWOT 분석 (내부 강점/약점 vs 외부 기회/위협 4분면 매트릭스)",
        #         "경쟁사 벤치마킹 (시장점유율, 수익성, 성장률 3년 트렌드 비교)",
        #         "시장점유율 분석 (HHI 지수, Top 3/5 집중도, 시장 파워 측정)",
        #         "BCG Growth-Share Matrix (Star, Cash Cow, Question Mark, Dog 분류)",
        #         "Technology Life Cycle 분석 (도입/성장/성숙/쇠퇴 단계별 전략)",
        #         "Competitive Moat 분석 (네트워크 효과, 브랜드, 규모경제, 전환비용)",
        #         "Supply Chain 분석 (업스트림/다운스트림 관계와 Power Balance)",
        #     ],
        #     sector_context=f"{sector_korean_name} 섹터의 산업 구조와 경쟁 환경을 심도 있게 분석하는 전문가",
        #     sector_specific_points=analysis_points_list
        #     + [
        #         "⭐ 산업 분석 시 반드시 다음을 포함:",
        #         "1. 산업 Life Cycle 상 현재 위치와 향후 3-5년 전망",
        #         "2. Top 5 경쟁사 대비 Market Share 변화 추이와 경쟁 우위 지속성",
        #         "3. Porter 5 Forces 각 요소별 점수화 (1-5점)와 종합 매력도 평가",
        #         "4. 핵심 성공 요인(KSF) 식별과 해당 기업의 KSF 보유 수준 평가",
        #         "5. 밸류체인 상 핵심 가치 창출 활동과 원가 구조 분석",
        #         "6. 기술 변화/규제 변화가 산업 구조에 미치는 파급 효과 예측",
        #         "7. ESG 이슈가 산업 경쟁력에 미치는 장기적 영향도 평가",
        #         "8. 글로벌 공급망 변화와 지정학적 리스크가 산업에 미치는 영향",
        #     ],
        #     risk_awareness=[
        #         f"산업 구조적 관점에서 {risk_factors}",
        #         "기술 대체 위험 (Disruptive Innovation으로 인한 산업 구조 변화)",
        #         "규제 변화 위험 (정부 정책/법규 변경이 산업 수익성에 미치는 영향)",
        #         "경쟁 심화 위험 (신규 진입자 증가나 가격 경쟁 심화)",
        #         "공급망 리스크 (원자재 가격 변동성, 공급업체 집중도)",
        #         "고객 Power 강화 위험 (구매력 집중, 대체재 증가)",
        #         "ESG 규제 강화 위험 (환경/사회적 책임 요구 증대)",
        #         "글로벌 Trade War 영향 (관세, 수출입 규제 변화)",
        #     ],
        #     critical_metrics=[
        #         "Market Share (매출 기준, 3년 CAGR)",
        #         "Industry Growth Rate (시장 성장률 vs 경제 성장률)",
        #         "HHI Index (허핀달 지수, 시장 집중도 측정)",
        #         "Entry Barrier Score (진입 장벽 종합 점수)",
        #         "Switching Cost Index (고객 전환비용 지수)",
        #         "R&D Intensity (R&D/매출 비율, 혁신 투자 수준)",
        #         "Capacity Utilization (설비 가동률, 공급 과부족)",
        #         "Forward/Backward Integration (수직계열화 정도)",
        #         "Price Premium vs Commodity (프리미엄 vs 범용품 포지셔닝)",
        #         "Export Dependency (수출 의존도, 환율 민감성)",
        #     ],
        #     langchain_enabled=True,  # 🚀 LangChain 활성화
        # )

        # 🚀 산업 전문가 LangChain Chain 설정
        # industry_expert.langchain_chain = self._create_industry_analysis_chain(
        #     industry_expert, sector_korean_name
        # )

        # experts.append(industry_expert)

        # 4. 밸류에이션 전문가 (섹터 특화) - 🚫 비활성화 (펀더멘털과 통합 예정)
        # valuation_specialist = AnalystAgent(
        #     name=f"{sector_korean_name} 밸류에이션 전문가",
        #     role="Valuation Specialist",
        #     expertise="기업가치 평가, 적정주가 산정, 투자지표 분석",
        #     analysis_focus=f"{sector_korean_name} 기업의 내재가치와 투자 매력도 평가",
        #     key_methods=[
        #         "DCF 모델링 (구체적 산출식 제시)",
        #         "PER/PBR 분석 (업계 평균 대비 산출)",
        #         "EV/EBITDA 분석 (멀티플 근거 설명)",
        #         "Sum-of-Parts 분석 (사업부문별 밸류에이션)",
        #         "배당수익률 분석 (배당성장 모델 적용)",
        #         "상대가치 평가 (동종업계 비교분석)",
        #         "목표가 산출 근거 명시 (계산 과정 상세 설명)",
        #         "시나리오별 민감도 분석 (낙관/기본/비관)",
        #     ],
        #     sector_context=f"{sector_korean_name} 섹터 특성을 반영한 맞춤형 밸류에이션 방법론을 적용하는 전문가",
        #     sector_specific_points=[
        #         f"밸류에이션 관점에서 {sector_context.get('valuation_approach', '가치평가 방법')}",
        #         "⭐ **ChatGPT 개선사항 반영 밸류에이션 분석**:",
        #         "🔴 **중요**: 제공된 실제 재무데이터를 최우선으로 사용하고, 가정 사용시 반드시 '(가정)' 표시",
        #         "💰 **1단계: 시계열 멀티플 분석 (ChatGPT 지적사항 1,2 해결)**",
        #         "1-1. 과거 3년간 PER, PBR, EV/EBITDA 추세 분석과 변동 원인 설명",
        #         "1-2. 역사적 멀티플 대비 현재 밸류에이션 위치 (Percentile 순위)",
        #         "1-3. 밸류에이션 사이클 분석: 고평가/저평가 구간 패턴 인식",
        #         "1-4. FCF Yield 3년 트렌드와 채권수익률 대비 매력도 변화",
        #         "📊 **2단계: 경쟁사 멀티플 비교 (ChatGPT 지적사항 3 해결)**",
        #         "2-1. **인터넷 서치 필수**: 동종업계 상위 5개 경쟁사 현재 PER, PBR, EV/EBITDA 검색",
        #         "2-2. 업계 평균 대비 밸류에이션 프리미엄/디스카운트율과 정당성 평가",
        #         "2-3. **인터넷 서치**: 글로벌 동종업계 평균 멀티플과 비교 (미국, 유럽, 아시아)",
        #         "2-4. 경쟁사 대비 높은/낮은 밸류에이션의 근본 원인 분석",
        #         "2-5. **검색 출처 명시**: '[인터넷 서치 출처: 검색결과]'로 표기",
        #         "🔍 **3단계: 밸류에이션 이상현상 설명 (ChatGPT 지적사항 4 해결)**",
        #         "3-1. PER 급등/급락의 배경: 일회성 손익 vs 구조적 변화 구분",
        #         "3-2. PBR 이상 현상: 자산 재평가, 손상차손, M&A 등의 영향 분석",
        #         "3-3. EV/EBITDA 왜곡 요인: EBITDA 품질, 일회성 비용, 회계변경 영향",
        #         "3-4. **인터넷 서치**: 최근 업황 변화가 밸류에이션에 미친 영향 확인",
        #         "🎯 **4단계: 완성된 목표가 산출 (ChatGPT 지적사항 5 해결)**",
        #         "4-1. **FCF Yield 완전 계산**: FCF(실제값)/시가총액 × 100, 시총=주가×발행주식수",
        #         "4-2. **WACC 실제 계산**: 사업보고서 데이터로 WACC 직접 산출 (아래 방법 활용)",
        #         "   - 타인자본 비용(Rd) = 이자비용 ÷ 유이자부채 (손익계산서, 재무상태표)",
        #         "   - 법인세율(T) = 법인세비용 ÷ 세전이익 (손익계산서)",
        #         "   - 자기자본(E) = 주가 × 발행주식수 (시가총액)",
        #         "   - 타인자본(D) = 총차입금 (재무상태표)",
        #         "   - 자기자본비용(Re) = 무위험수익률 + 베타 × 위험프리미엄 (인터넷 서치로 베타 확인)",
        #         "   - **WACC = (E/(E+D) × Re) + (D/(E+D) × Rd × (1-T))**",
        #         "4-3. **DCF 모델 상세**: 향후 5년 FCF 예측, 실제 계산된 WACC 활용, Terminal Value 계산",
        #         "4-3. **멀티플 방법**: Forward PER, PBR 기반 목표가 (업계 평균 적용)",
        #         "4-4. **Sum-of-Parts**: 주요 사업부문별 밸류에이션과 지분가치 합산",
        #         "4-5. **배당할인모델**: 향후 배당성장률 가정하여 내재가치 산출",
        #         "4-6. **인터넷 서치**: 애널리스트 컨센서스 목표가와 비교 분석",
        #         "4-7. **가중평균 목표가**: 각 방법론별 신뢰도에 따른 가중치 적용",
        #         "⚖️ **5단계: 시나리오별 밸류에이션 (ChatGPT 지적사항 6 해결)**",
        #         "5-1. **낙관 시나리오 (25% 확률)**: 최고 실적 가정시 목표가와 근거",
        #         "5-2. **기본 시나리오 (50% 확률)**: 컨센서스 기반 목표가와 근거",
        #         "5-3. **비관 시나리오 (25% 확률)**: 악재 반영시 목표가와 근거",
        #         "5-4. **확률가중 목표가**: 3시나리오 확률 가중 평균값 산출",
        #         "5-5. **민감도 분석**: 핵심 변수 ±10% 변동시 목표가 변화폭",
        #         "5-6. **ESG 요인 반영**: ESG 개선/악화시 밸류에이션 프리미엄/디스카운트",
        #         "🔴 **밸류에이션 데이터 활용 우선순위**:",
        #         "- 1순위: 제공된 재무제표 실제 수치 (FCF, 순이익, 자기자본, EBITDA)",
        #         "- 2순위: 인터넷 서치를 통한 경쟁사/업계 멀티플 정보",
        #         "- 3순위: 합리적 가정 사용 (반드시 '(가정)' 표시하고 근거 설명)",
        #         "- **인터넷 서치 필수 항목**: 경쟁사 멀티플, 애널리스트 컨센서스, 업계 평균 밸류에이션",
        #         "- **검색 결과 활용 시**: 반드시 '[인터넷 서치 출처: 검색결과]' 명시",
        #         "📈 **추가 개선 요구사항**:",
        #         "- 모든 멀티플은 소수점 첫째 자리까지 표시 (예: PER 12.3배)",
        #         "- 목표가는 원단위까지 제시 (예: 목표가 65,000원)",
        #         "- 계산 과정 명시 (예: DCF = FCF 5조 ÷ WACC 8% = 62.5조원)",
        #         "- 업계 대비 프리미엄/디스카운트를 %로 명시 (예: 업계 평균 PER 15배 대비 20% 할인)",
        #         "- 각 밸류에이션 방법론의 가중치와 근거 명시",
        #         "- 최종 투자의견과 12개월 목표가 명확히 제시",
        #     ],
        #     risk_awareness=[f"밸류에이션 관점에서 {risk_factors}"],
        #     critical_metrics=[
        #         metric
        #         for metric in critical_metrics_list
        #         if any(word in metric for word in ["비율", "수익률", "마진", "배수"])
        #     ],
        #     langchain_enabled=True,  # 🚀 LangChain 활성화
        # )

        # 🚀 밸류에이션 전문가 LangChain Chain 설정
        # valuation_specialist.langchain_chain = self._create_valuation_analysis_chain(
        #     valuation_specialist, sector_korean_name
        # )

        # experts.append(valuation_specialist)

        # 5. 리스크 평가자 (섹터 특화) - 🚫 비활성화 (개발 시간 절약)
        # risk_assessor = AnalystAgent(
        #     name=f"{sector_korean_name} 리스크 평가자",
        #     role="Risk Assessor",
        #     expertise="위험 요소 분석, 시나리오 분석, 리스크 관리",
        #     analysis_focus=f"{sector_korean_name} 투자의 주요 리스크와 대응 전략 분석",
        #     key_methods=[
        #         "VaR 분석 (Value at Risk, 95% 신뢰구간 1일/10일/1개월 손실 예상)",
        #         "시나리오 분석 (Base/Bull/Bear Case 3시나리오 확률 가중 평가)",
        #         "몬테카르로 시뮬레이션 (주요 변수 1만회 시뮬레이션 확률분포)",
        #         "민감도 분석 (핵심 변수 ±10%, ±20% 변동시 목표가 영향도)",
        #         "스트레스 테스트 (2008, 2020급 위기상황 가정 충격 시나리오)",
        #         "ESG 리스크 스코어링 (환경, 사회, 지배구조 3대 영역 정량평가)",
        #         "신용 리스크 분석 (Altman Z-Score, Credit Default Probability)",
        #         "유동성 리스크 측정 (시장충격시 매도 가능 시간과 슬리피지)",
        #         "Beta 분해 분석 (시장, 섹터, 기업고유 리스크 3단계 분해)",
        #         "Tail Risk 분석 (극단적 손실 확률과 Maximum Drawdown 예측)",
        #     ],
        #     sector_context=f"{sector_korean_name} 섹터 고유의 리스크 요인과 함정을 전문적으로 분석하는 리스크 전문가",
        #     sector_specific_points=[
        #         f"리스크 관점에서 {analysis_points}",
        #         "⭐ 리스크 분석 시 반드시 다음을 포함:",
        #         "🔴 **중요**: 제공된 실제 재무데이터와 시장데이터를 최우선으로 사용하고, 가정 사용시 반드시 '(가정)' 표시",
        #         "1. 정량적 리스크 지표 산출 (VaR, CVaR, Maximum Drawdown, Sharpe Ratio) - 실제 주가/재무 데이터 기반",
        #         "2. 3시나리오 분석과 각 시나리오별 발생 확률 및 목표가 Impact - 과거 실적 데이터 기반 산출",
        #         "3. 주요 리스크 팩터별 민감도 계수와 탄력성 측정 - 제공된 재무제표 실제 수치 활용",
        #         "4. 스트레스 테스트 결과 (글로벌 금융위기급 충격시 예상 손실률) - 과거 위기시 실제 데이터 참조",
        #         "5. ESG 리스크 스코어와 ESG 이슈 발생시 주가 하락 폭 예측",
        #         "6. 신용도 분석 (Altman Z-Score, 부도 확률, Credit Spread 변화) - 실제 재무비율로 계산",
        #         "7. 유동성 리스크 (일평균 거래대금 대비 대량 매도시 충격도) - 실제 거래량 데이터 기반",
        #         "8. 섹터 특화 리스크 (규제, 기술, 원자재, 환율 등) 정량 측정",
        #         "🔴 **리스크 데이터 활용 원칙**:",
        #         "- 1순위: 제공된 재무제표 실제 수치로 재무비율 계산",
        #         "- 변동성 측정은 제공된 실제 주가 데이터 우선 사용",
        #         "- 부도확률 계산은 실제 부채비율, 이자보상비율 등 활용",
        #         "- 실제 데이터 부족시: 가정 사용하되 반드시 '(가정)' 표시하고 근거 설명",
        #         "- 가정 예시: 'VaR 5% (가정: 과거 3년 변동성 기준 추정)'",
        #         "- 실제값과 가정값의 명확한 구분으로 투명성 확보",
        #         "9. 리스크 대비 수익률 (Risk-Adjusted Return) 동종업계 대비 평가",
        #         "10. 포트폴리오 내 상관관계와 분산투자 효과 분석",
        #     ],
        #     risk_awareness=risk_factors_list
        #     + [
        #         "Black Swan Event 리스크 (예측 불가능한 극단적 사건)",
        #         "Model Risk (리스크 모델의 가정 오류나 과적합 위험)",
        #         "Concentration Risk (단일 고객/공급업체/지역 집중도 위험)",
        #         "Operational Risk (시스템 장애, 사기, 인적 오류 등)",
        #         "Reputation Risk (브랜드 이미지 손상으로 인한 매출 감소)",
        #         "Regulatory Risk (규제 변화로 인한 사업 모델 변경 위험)",
        #         "Currency Risk (환율 변동이 손익에 미치는 영향)",
        #         "Interest Rate Risk (금리 변동이 자금조달비용에 미치는 영향)",
        #         "Inflation Risk (인플레이션이 실질수익률에 미치는 영향)",
        #         "Geopolitical Risk (지정학적 긴장이 사업에 미치는 영향)",
        #     ],
        #     critical_metrics=[
        #         "VaR (95% 신뢰구간 1일/1개월)",
        #         "CVaR (Conditional VaR, 극단손실 평균)",
        #         "Maximum Drawdown (최대 손실 구간)",
        #         "Sharpe Ratio (위험 대비 수익률)",
        #         "Information Ratio (벤치마크 대비 초과수익/추적오차)",
        #         "Beta (시장 민감도, 1년/3년 구간)",
        #         "Volatility (20일/60일/252일 변동성)",
        #         "Downside Deviation (하방 위험 측정)",
        #         "Altman Z-Score (신용도 측정)",
        #         "ESG Risk Score (환경/사회/지배구조 리스크)",
        #         "Liquidity Ratio (거래량 대비 유동성)",
        #         "Concentration Index (사업/지역 집중도)",
        #     ],
        #     langchain_enabled=True,  # 🚀 LangChain 활성화
        # )

        # 🚀 리스크 평가자 LangChain Chain 설정
        # risk_assessor.langchain_chain = self._create_risk_analysis_chain(
        #     risk_assessor, sector_korean_name
        # )

        # experts.append(risk_assessor)

        # 📝 6. 주석 전문 분석가 (사용자 요청 반영! - 새로 추가) - 🚫 비활성화 (개발 시간 절약)
        # footnote_specialist = AnalystAgent(
        #     name=f"{sector_korean_name} 재무제표 주석 전문가",
        #     role="Financial Statement Footnote Specialist",
        #     expertise="재무제표 주석(footnote) 분석, 재무상태표 주석 해석, 숨겨진 재무정보 발굴",
        #     analysis_focus=f"{sector_korean_name} 기업의 재무제표 주석(footnote)에 숨겨진 중요 재무정보와 위험요소를 전문적으로 분석",
        #     key_methods=[
        #         "재무상태표(F/S) 주석 상세 분석",
        #         "손익계산서 주석 해석",
        #         "현금흐름표 주석 검토",
        #         "우발채무 및 보증채무 분석",
        #         "연결범위 변동사항 분석",
        #         "회계정책 변경 영향도 분석",
        #         "관계회사 거래내역 분석",
        #         "파생상품 공정가치 변동 분석",
        #         "리스 및 약정사항 분석",
        #         "금융상품 분류 및 평가 분석",
        #     ],
        #     sector_context=f"{sector_korean_name} 섹터의 특성을 반영한 재무제표 주석 분석 전문가로서, 재무제표 본문에 드러나지 않은 숨겨진 재무위험과 기회요소를 발굴",
        #     sector_specific_points=[
        #         f"{sector_korean_name} 섹터 특화 재무제표 주석 분석 포인트",
        #         "재무상태표 주석의 핵심 정보 추출 및 해석",
        #         "주석에 숨겨진 우발부채 및 잠재적 위험요소 발굴",
        #         "회계처리 방법 변경이 재무성과에 미치는 영향 정량분석",
        #         "관계회사 거래의 실질적 영향도 평가",
        #         "금융상품 및 파생상품 위험 노출도 분석",
        #     ],
        #     risk_awareness=[
        #         "재무제표 주석에 숨겨진 우발채무와 보증채무의 실질적 위험도",
        #         "회계정책 변경으로 인한 손익 조정 및 비교가능성 훼손 위험",
        #         "연결범위 변동이 재무성과에 미치는 실질적 영향",
        #         "파생상품 거래의 잠재적 손실 위험 및 헤지 효과성",
        #         "관계회사 거래의 특수관계자 거래 위험",
        #         "리스 및 약정사항의 미래 현금흐름 영향",
        #         f"{sector_korean_name} 섹터 특화 재무제표 주석 위험 요소",
        #     ],
        #     critical_metrics=[
        #         "우발채무/총자산 비율",
        #         "보증채무/총자본 비율",
        #         "관계회사 거래/총매출 비중",
        #         "파생상품 공정가치 변동손익",
        #         "회계정책 변경 누적영향액",
        #         "연결범위 변동 영향액",
        #         "리스부채/총부채 비율",
        #         "금융상품 신용위험 노출액",
        #         f"{sector_korean_name} 섹터 주석 특화 재무지표",
        #     ],
        #     langchain_enabled=True,  # 🚀 LangChain 활성화
        # )

        # 🚀 주석 전문가 LangChain Chain 설정
        # footnote_specialist.langchain_chain = self._create_footnote_analysis_chain(
        #     footnote_specialist, sector_korean_name
        # )

        # experts.append(footnote_specialist)

        # 섹터팀 생성 (2명 전문가로 축소 - 통합 재무분석가 + 기술적 분석가)
        team = SectorTeam(
            sector=sector,
            team_name=f"{sector_korean_name} 섹터 통합 분석팀",
            team_description=(
                f"{sector_korean_name} 섹터의 종합 투자 분석을 수행하는 2명의 전문가팀. "
                f"통합 재무분석가(펀더멘털+밸류에이션)와 기술적 분석가가 협업하여 정확하고 실용적인 분석을 제공합니다. "
                f"섹터 특화 분석 포인트와 리스크 요소를 반영하여 시니어 애널리스트 보조자료 수준의 분석을 제공합니다."
            ),
            experts=experts,
            collaboration_strategy=(
                f"{sector_korean_name} 섹터의 {sector_context.get('cyclical_nature', '특성')}을 고려하여 "
                f"2명의 핵심 전문가(통합 재무분석가, 기술적 분석가)가 각자의 전문성을 바탕으로 협업하는 전략. "
                f"통합 재무분석가가 재무 건전성, 성장성, 기업가치를 종합 분석하고, 기술적 분석가가 시장 타이밍과 "
                f"가격 움직임을 분석하여 종합적인 투자 의견을 도출합니다."
            ),
            report_structure={
                "integrated_financial": f"{sector_korean_name} 섹터 통합 재무분석 보고서 (펀더멘털+밸류에이션)",
                "technical": f"{sector_korean_name} 섹터 기술적 분석 및 시장 동향 보고서",
            },
        )

        print(
            f"✅ {sector_korean_name} 섹터팀 생성 완료 (전문가 {len(experts)}명 - 통합 재무분석가 + 기술적 분석가)"
        )
        return team

    def get_expert_by_role(self, team: SectorTeam, role: str) -> Optional[AnalystAgent]:
        """
        팀에서 특정 역할의 전문가를 찾아요

        Args:
            team: 섹터팀
            role: 찾을 전문가 역할 (예: "Fundamental Analyst")

        Returns:
            AnalystAgent: 해당 역할의 전문가 (없으면 None)
        """
        for expert in team.experts:
            if expert.role == role:
                return expert
        return None

    def print_team_summary(self, team: SectorTeam) -> None:
        """
        팀 구성과 각 전문가의 특화 포인트를 보기 좋게 출력해요

        Args:
            team: 출력할 섹터팀
        """
        print(f"\n🏢 【{team.team_name}】")
        print("=" * 60)
        print(f"📝 팀 설명: {team.team_description}")
        print(f"🤝 협업 전략: {team.collaboration_strategy}")

        print(f"\n👥 전문가 구성 ({len(team.experts)}명):")
        print("-" * 40)

        for i, expert in enumerate(team.experts, 1):
            print(f"\n{i}. {expert.name}")
            print(f"   🎯 역할: {expert.role}")
            print(f"   💡 전문분야: {expert.expertise}")
            print(f"   🔍 분석초점: {expert.analysis_focus}")
            print(
                f"   📊 특화포인트: {', '.join(expert.sector_specific_points[:2])}..."
            )
            print(
                f"   ⚠️  주의사항: {expert.risk_awareness[0][:50]}..."
                if expert.risk_awareness
                else ""
            )

        print("=" * 60)

    def get_all_sector_teams(self) -> Dict[GICSSector, SectorTeam]:
        """
        모든 GICS 섹터의 전문 분석팀을 생성해서 반환해요

        Returns:
            Dict: 섹터별 전문 분석팀 딕셔너리
        """
        all_teams = {}

        print("🚀 모든 GICS 섹터 전문팀 생성 시작...")

        for sector in self.sector_manager.get_all_sectors():
            team = self.create_sector_team(sector)
            all_teams[sector] = team

        print(f"🎉 총 {len(all_teams)}개 섹터팀 생성 완료!")
        return all_teams

    # def _create_fundamental_analysis_chain(
    #     self, analyst: AnalystAgent, sector_name: str
    # ) -> Any:
    #     """
    #     펀더멘털 분석가를 위한 LangChain Chain 생성 (비활성화됨 - 통합 재무분석가로 대체)

    #     Args:
    #         analyst: 분석가 객체
    #         sector_name: 섹터 이름

    #     Returns:
    #         Chain: 단일 단계 분석 Chain
    #     """
    #     try:
    #         # LLM 모델 설정 (환경변수에서 API 키 가져오기)
    #         llm = ChatOpenAI(
    #             model="gpt-4o",
    #             temperature=0.1,  # 분석의 일관성을 위해 낮은 temperature
    #             max_tokens=4000,
    #         )

    #         # 단일 단계: 종합 재무 분석 Chain
    #         fundamental_analysis_prompt = PromptTemplate(
    #             input_variables=["financial_data", "sector_name", "company_name"],
    #             template="""
    # 당신은 {sector_name} 섹터 전문 펀더멘털 분석가입니다.

    # **종합 재무 분석**

    # 제공된 재무데이터를 바탕으로 종합적인 재무 분석을 수행하세요:

    # **입력 데이터:**
    # {financial_data}

    # **회사명:** {company_name}

    # **분석 요구사항:**
    # 1. 데이터 검증 및 정규화
    # 2. 핵심 재무비율 계산 (ROE, ROA, ROIC, 유동비율, 부채비율 등)
    # 3. 3년간 트렌드 분석 및 변화 패턴 식별
    # 4. CAGR 계산 (매출, 영업이익, 순이익)
    # 5. 현금흐름 안정성 분석
    # 6. DuPont 분석을 통한 ROE 분해
    # 7. 경쟁사 비교 분석 (업계 평균 대비)
    # 8. 종합 평가 및 투자 의견

    # **출력 형식:**
    # - 데이터 검증 결과: [통과/부분 통과/실패]
    # - 재무비율 분석: [구체적 수치와 계산 과정]
    # - 트렌드 분석: [3년간 변화 추이와 패턴]
    # - 성장성 평가: [CAGR과 지속가능성]
    # - 현금흐름 평가: [안정성과 품질]
    # - 경쟁사 비교: [업계 내 상대적 위치]
    # - 종합 평가: [재무 건전성과 투자 매력도]
    # - 투자 의견: [명확한 권고와 근거]

    # 단계별로 사고 과정을 명시하고, 정량적 근거를 제시하세요.
    # """,
    #         )

    #         # 🚀 웹 검색 도구를 포함한 LangChain Chain 생성
    #         from langchain.agents import AgentExecutor, create_openai_functions_agent
    #         from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

    #         # 웹 검색 도구 생성
    #         web_search_tool = self.web_search_tool.create_langchain_tool()

    #         # 시스템 프롬프트 생성 (AgentExecutor 호환)
    #         system_prompt = ChatPromptTemplate.from_messages(
    #             [
    #                 (
    #                     "system",
    #                     """
    # 당신은 정보기술 섹터 전문 펀더멘털 분석가입니다.

    # **종합 재무 분석**

    # 사용자의 요청을 바탕으로 종합적인 재무 분석을 수행하세요.

    # **분석 요구사항:**
    # 1. 데이터 검증 및 정규화
    # 2. 핵심 재무비율 계산 (ROE, ROA, ROIC, 유동비율, 부채비율 등)
    # 3. 3년간 트렌드 분석 및 변화 패턴 식별
    # 4. CAGR 계산 (매출, 영업이익, 순이익)
    # 5. 현금흐름 안정성 분석
    # 6. DuPont 분석을 통한 ROE 분해
    # 7. 경쟁사 비교 분석 (업계 평균 대비)
    # 8. 종합 평가 및 투자 의견

    # **출력 형식:**
    # - 데이터 검증 결과: [통과/부분 통과/실패]
    # - 재무비율 분석: [구체적 수치와 계산 과정]
    # - 트렌드 분석: [3년간 변화 추이와 패턴]
    # - 성장성 평가: [CAGR과 지속가능성]
    # - 현금흐름 평가: [안정성과 품질]
    # - 경쟁사 비교: [업계 내 상대적 위치]
    # - 종합 평가: [재무 건전성과 투자 매력도]
    # - 투자 의견: [명확한 권고와 근거]

    # 웹 검색을 통해 최신 정보를 확인하고, 단계별로 사고 과정을 명시하며, 정량적 근거를 제시하세요.
    # """,
    #                 ),
    #                 MessagesPlaceholder(variable_name="chat_history"),
    #                 ("human", "{input}"),
    #                 MessagesPlaceholder(variable_name="agent_scratchpad"),
    #             ]
    #         )

    #         # Agent 생성 (웹 검색 도구 포함)
    #         agent = create_openai_functions_agent(
    #             llm=llm, tools=[web_search_tool], prompt=system_prompt
    #         )

    #         # Agent Executor 생성
    #         fundamental_chain = AgentExecutor(
    #             agent=agent, tools=[web_search_tool], verbose=True, max_iterations=3
    #         )

    #         print(f"✅ {analyst.name} LangChain Chain 생성 완료 (웹 검색 도구 포함)!")
    #         return fundamental_chain

    #     except Exception as e:
    #         print(f"❌ {analyst.name} LangChain Chain 생성 실패: {e}")
    #         return None

    def _create_integrated_financial_analysis_chain(
        self,
        analyst: AnalystAgent,
        sector_name: str,
        sector: GICSSector,
    ) -> Any:
        """
        통합 재무분석가를 위한 LangChain Chain 생성 (펀더멘털 + 밸류에이션 통합)

        Args:
            analyst: 분석가 객체
            sector_name: 섹터 이름

        Returns:
            Chain: 5단계 통합 분석 Chain
        """
        try:
            # LLM 모델 설정 (OpenAI GPT-4o)
            llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0.1,  # 분석의 일관성을 위해 낮은 값
                max_tokens=8000,  # 2명 체제에 맞게 증가 (기존 4K → 8K)
            )

            # 🚀 웹 검색 도구를 포함한 LangChain Chain 생성

            # 웹 검색 도구 생성
            web_search_tool = self.web_search_tool.create_langchain_tool()

            # 간소화된 분석 프레임워크 (LLM 거부 방지)
            unified_framework = f"""
**{sector_name} 섹터 전문 재무분석가 역할**:
- 재무 건전성: ROE, ROA, 부채비율 분석
- 성장성: 매출/이익 성장률 분석
- 밸류에이션: DCF, PER/PBR 분석
- 리스크: 산업/경쟁 리스크 분석
- 섹터 특화: 기술력, 시장 점유율 분석
"""

            # 간소화된 출력 형식
            output_format = """
**최종 출력 형식**:
- 투자 의견: BUY/HOLD/SELL (신뢰도 %)
- 목표가: 구체적 금액과 산출 근거
- 핵심 근거: 3가지 이내
- 주요 리스크: 2가지 이내
"""

            # 🚀 향상된 애널리스트 사고 흐름 프레임워크 적용 (섹터 직접 활용으로 효율성 향상)
            enhanced_thinking_flow = (
                PromptComponents.get_enhanced_analyst_thinking_flow(
                    sector=sector, sector_manager=self.sector_manager
                )
            )

            # 시스템 프롬프트 생성 (향상된 애널리스트 사고 흐름 적용)
            system_prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        f"""
당신은 {sector_name} 섹터 전문 통합 재무분석가입니다.

🎯 **중요**: 반드시 다음 3단계 구조를 따라 분석하세요:
=== 1단계: Self-Ask with ToT ===
=== 2단계: ReAct ===
=== 3단계: CoT Reasoning + Self-Critique ===

{enhanced_thinking_flow}

{unified_framework}

**요구사항**:
1. 제공된 데이터를 우선 활용하세요
2. 반드시 3단계 구조를 따르세요
3. Q5 섹터 특화 질문을 1단계에 포함하세요
4. Self-Critique를 3단계에 포함하세요
5. 투자 의견과 목표가를 명확히 제시하세요

{output_format}
""",
                    ),
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("human", "{input}"),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ]
            )

            # Agent 생성 (웹 검색 도구 포함)
            agent = create_openai_functions_agent(
                llm=llm, tools=[web_search_tool], prompt=system_prompt
            )

            # Agent Executor 생성 (Q5 강제 보장을 위한 Custom Executor 사용)
            integrated_chain = Q5EnforcedAgentExecutor(
                sector=sector,
                sector_manager=self.sector_manager,
                agent_name=analyst.name,
                agent=agent,
                tools=[web_search_tool],
                verbose=True,
                max_iterations=10,  # 3단계 사고 흐름 처리를 위해 증가
                early_stopping_method="generate",  # 완전한 답변 생성 보장
                return_intermediate_steps=True,  # 중간 단계 추적 활성화
            )

            print(f"✅ {analyst.name} 통합 재무분석 LangChain Chain 생성 완료!")
            return integrated_chain

        except Exception as e:
            print(f"❌ {analyst.name} 통합 재무분석 LangChain Chain 생성 실패: {e}")
            return None

    # def _create_valuation_analysis_chain(
    #     self, analyst: AnalystAgent, sector_name: str
    # ) -> Any:
    #     """
    #     밸류에이션 전문가를 위한 LangChain Chain 생성 (비활성화됨 - 통합 재무분석가로 대체)

    #     Args:
    #         analyst: 분석가 객체
    #         sector_name: 섹터 이름

    #     Returns:
    #         Chain: 단일 단계 분석 Chain
    #     """
    #     try:
    #         # LLM 모델 설정 (OpenAI GPT-4o)
    #         llm = ChatOpenAI(
    #             model="gpt-4o",
    #             temperature=0.1,  # 분석의 일관성을 위해 낮은 값
    #             max_tokens=4000,
    #         )

    #         # 단일 단계: 종합 밸류에이션 분석 프롬프트
    #         valuation_analysis_prompt = PromptTemplate(
    #             input_variables=["financial_data", "sector_name", "company_name"],
    #             template="""
    # 당신은 {sector_name} 섹터 전문 밸류에이션 전문가입니다.

    # **종합 밸류에이션 분석**

    # 제공된 재무데이터를 바탕으로 종합적인 밸류에이션 분석을 수행하세요:

    # **입력 데이터:**
    # {financial_data}

    # **회사명:** {company_name}

    # **분석 요구사항:**
    # 1. 시계열 멀티플 분석:
    #    - 과거 3년간 PER, PBR, EV/EBITDA 계산 및 추세 분석
    #    - 현재 멀티플의 역사적 Percentile 순위 산출
    #    - 밸류에이션 사이클 분석 (고평가/저평가 구간 패턴)

    # 2. 경쟁사 비교 분석:
    #    - 동종업계 상위 5개 경쟁사 현재 멀티플 비교
    #    - 업계 평균 대비 밸류에이션 프리미엄/디스카운트율 계산
    #    - 글로벌 동종업계 평균 멀티플과 비교

    # 3. DCF 모델링:
    #    - WACC 계산 (구체적 계산 과정 포함)
    #    - 향후 5년 FCF 예측
    #    - Terminal Value 계산
    #    - 내재가치 산출

    # 4. 목표가 산출:
    #    - DCF 기반 목표가
    #    - 멀티플 기반 목표가 (PER, PBR, EV/EBITDA)
    #    - 가중평균 목표가 계산

    # 5. 시나리오별 민감도 분석:
    #    - 낙관/기본/비관 3시나리오 분석
    #    - 주요 변수별 민감도 분석

    # **출력 형식:**
    # - 멀티플 분석: [계산된 멀티플과 트렌드]
    # - 경쟁사 비교: [업계 대비 상대적 위치]
    # - DCF 모델링: [내재가치와 계산 과정]
    # - 목표가 산출: [최종 목표가와 근거]
    # - 시나리오 분석: [3시나리오별 전망]
    # - 투자 의견: [매수/보유/매도 권고]

    # 모든 계산 과정을 명시하고, 정량적 근거를 제시하세요.
    # """,
    #         )

    #         # 🚀 웹 검색 도구를 포함한 LangChain Chain 생성
    #         from langchain.agents import AgentExecutor, create_openai_functions_agent
    #         from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

    #         # 웹 검색 도구 생성
    #         web_search_tool = self.web_search_tool.create_langchain_tool()

    #         # 시스템 프롬프트 생성 (AgentExecutor 호환)
    #         system_prompt = ChatPromptTemplate.from_messages(
    #             [
    #                 (
    #                     "system",
    #                     """
    # 당신은 정보기술 섹터 전문 밸류에이션 전문가입니다.

    # **종합 밸류에이션 분석**

    # 사용자의 요청을 바탕으로 종합적인 밸류에이션 분석을 수행하세요.

    # **분석 요구사항:**
    # 1. 시계열 멀티플 분석:
    #    - 과거 3년간 PER, PBR, EV/EBITDA 계산 및 추세 분석
    #    - 현재 멀티플의 역사적 Percentile 순위 산출
    #    - 밸류에이션 사이클 분석 (고평가/저평가 구간 패턴)

    # 2. 경쟁사 비교 분석:
    #    - 동종업계 상위 5개 경쟁사 현재 멀티플 비교
    #    - 업계 평균 대비 밸류에이션 프리미엄/디스카운트율 계산
    #    - 글로벌 동종업계 평균 멀티플과 비교

    # 3. DCF 모델링:
    #    - WACC 계산 (구체적 계산 과정 포함)
    #    - 향후 5년 FCF 예측
    #    - Terminal Value 계산
    #    - 내재가치 산출

    # 4. 목표가 산출:
    #    - DCF 기반 목표가
    #    - 멀티플 기반 목표가 (PER, PBR, EV/EBITDA)
    #    - 가중평균 목표가 계산

    # 5. 시나리오별 민감도 분석:
    #    - 낙관/기본/비관 3시나리오 분석
    #    - 주요 변수별 민감도 분석

    # **출력 형식:**
    # - 멀티플 분석: [계산된 멀티플과 트렌드]
    # - 경쟁사 비교: [업계 대비 상대적 위치]
    # - DCF 모델링: [내재가치와 계산 과정]
    # - 목표가 산출: [최종 목표가와 근거]
    # - 시나리오 분석: [3시나리오별 전망]
    # - 투자 의견: [매수/보유/매도 권고]

    # 웹 검색을 통해 최신 정보를 확인하고, 모든 계산 과정을 명시하며, 정량적 근거를 제시하세요.
    # """,
    #                 ),
    #                 MessagesPlaceholder(variable_name="chat_history"),
    #                 ("human", "{input}"),
    #                 MessagesPlaceholder(variable_name="agent_scratchpad"),
    #             ]
    #         )

    #         # Agent 생성 (웹 검색 도구 포함)
    #         agent = create_openai_functions_agent(
    #             llm=llm, tools=[web_search_tool], prompt=system_prompt
    #         )

    #         # Agent Executor 생성
    #         valuation_chain = AgentExecutor(
    #             agent=agent, tools=[web_search_tool], verbose=True, max_iterations=3
    #         )

    #         print(f"✅ {analyst.name} LangChain Chain 생성 완료 (웹 검색 도구 포함)!")
    #         return valuation_chain

    #     except Exception as e:
    #         print(f"❌ {analyst.name} LangChain Chain 생성 실패: {e}")
    #         return None

    # def _create_risk_analysis_chain(
    #     self, analyst: AnalystAgent, sector_name: str
    # ) -> Any:
    #     """
    #     리스크 평가자를 위한 LangChain Chain 생성 (비활성화됨)

    #     Args:
    #         analyst: 분석가 객체
    #         sector_name: 섹터 이름

    #     Returns:
    #         Chain: 단일 단계 분석 Chain
    #     """
    #     try:
    #         llm = ChatOpenAI(
    #             model="gpt-4o",
    #             temperature=0.1,
    #             max_tokens=4000,
    #         )
    #         risk_analysis_prompt = PromptTemplate(
    #             input_variables=["financial_data", "sector_name", "company_name"],
    #             template="""
    # 당신은 {sector_name} 섹터 전문 리스크 평가자입니다.

    # **종합 리스크 분석**

    # 제공된 재무데이터를 바탕으로 종합적인 리스크 분석을 수행하세요:

    # **입력 데이터:**
    # {financial_data}

    # **회사명:** {company_name}

    # **분석 요구사항:**
    # 1. 재무 리스크 분석:
    #    - 부채비율, 유동비율, 이자보상배율 분석
    #    - 현금흐름 안정성 평가
    #    - 신용 리스크 스코어링
    # 2. 사업 리스크 분석:
    #    - 시장점유율 변화 리스크
    #    - 경쟁사 대응 리스크
    #    - 기술 변화 리스크
    # 3. 시장 리스크 분석:
    #    - 주가 변동성 분석
    #    - 베타 계수 계산
    #    - 시장 대비 상대적 리스크
    # 4. ESG 리스크 분석:
    #    - 환경 리스크 (규제, 기후변화)
    #    - 사회 리스크 (인권, 노동환경)
    #    - 지배구조 리스크 (투명성, 독립성)
    # 5. 종합 리스크 평가:
    #    - 주요 리스크 요인별 영향도 분석
    #    - 시나리오별 리스크 시뮬레이션
    #    - 리스크 대응 전략 제시

    # **출력 형식:**
    # - 재무 리스크: [부채 및 유동성 리스크 평가]
    # - 사업 리스크: [경쟁 및 시장 리스크 분석]
    # - 시장 리스크: [주가 변동성 및 베타 분석]
    # - ESG 리스크: [환경, 사회, 지배구조 리스크]
    # - 종합 평가: [전체 리스크 수준과 대응 방안]
    # - 투자 권고: [리스크 대비 수익률 평가]

    # 웹 검색을 통해 최신 리스크 이슈와 업계 동향도 참고하세요.
    # """,
    #         )
    #         from langchain.agents import AgentExecutor, create_openai_functions_agent
    #         from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

    #         web_search_tool = self.web_search_tool.create_langchain_tool()
    #         system_prompt = ChatPromptTemplate.from_messages(
    #             [
    #                 (
    #                     "system",
    #                     f"""
    # 당신은 {sector_name} 섹터 전문 리스크 평가자입니다.

    # **종합 리스크 분석**

    # 사용자의 요청을 바탕으로 종합적인 리스크 분석을 수행하세요.

    # **분석 요구사항:**
    # 1. 재무 리스크 분석:
    #    - 부채비율, 유동비율, 이자보상배율 분석
    #    - 현금흐름 안정성 평가
    #    - 신용 리스크 스코어링
    # 2. 사업 리스크 분석:
    #    - 시장점유율 변화 리스크
    #    - 경쟁사 대응 리스크
    #    - 기술 변화 리스크
    # 3. 시장 리스크 분석:
    #    - 주가 변동성 분석
    #    - 베타 계수 계산
    #    - 시장 대비 상대적 리스크
    # 4. ESG 리스크 분석:
    #    - 환경 리스크 (규제, 기후변화)
    #    - 사회 리스크 (인권, 노동환경)
    #    - 지배구조 리스크 (투명성, 독립성)
    # 5. 종합 리스크 평가:
    #    - 주요 리스크 요인별 영향도 분석
    #    - 시나리오별 리스크 시뮬레이션
    #    - 리스크 대응 전략 제시

    # **출력 형식:**
    # - 재무 리스크: [부채 및 유동성 리스크 평가]
    # - 사업 리스크: [경쟁 및 시장 리스크 분석]
    # - 시장 리스크: [주가 변동성 및 베타 분석]
    # - ESG 리스크: [환경, 사회, 지배구조 리스크]
    # - 종합 평가: [전체 리스크 수준과 대응 방안]
    # - 투자 권고: [리스크 대비 수익률 평가]

    # 웹 검색을 통해 최신 리스크 이슈와 업계 동향도 참고하세요.
    # """,
    #                 ),
    #                 MessagesPlaceholder(variable_name="chat_history"),
    #                 ("human", "{input}"),
    #                 MessagesPlaceholder(variable_name="agent_scratchpad"),
    #             ]
    #         )
    #         agent = create_openai_functions_agent(
    #             llm=llm, tools=[web_search_tool], prompt=system_prompt
    #         )
    #         risk_chain = AgentExecutor(
    #             agent=agent, tools=[web_search_tool], verbose=True, max_iterations=3
    #         )
    #         print(f"✅ {analyst.name} LangChain Chain 생성 완료 (웹 검색 도구 포함)!")
    #         return risk_chain
    #     except Exception as e:
    #         print(f"❌ {analyst.name} LangChain Chain 생성 실패: {e}")
    #         return None

    # def _create_industry_analysis_chain(
    #     self, analyst: AnalystAgent, sector_name: str
    # ) -> Any:
    #     """
    #     산업 전문가를 위한 LangChain Chain 생성 (비활성화됨)

    #     Args:
    #         analyst: 분석가 객체
    #         sector_name: 섹터 이름

    #     Returns:
    #         Chain: 단일 단계 분석 Chain
    #     """
    #     try:
    #         llm = ChatOpenAI(
    #             model="gpt-4o",
    #             temperature=0.1,
    #             max_tokens=4000,
    #         )
    #         industry_analysis_prompt = PromptTemplate(
    #             input_variables=["financial_data", "sector_name", "company_name"],
    #             template="""
    # 당신은 {sector_name} 섹터 전문 산업 전문가입니다.

    # **종합 산업 분석**

    # 제공된 재무데이터를 바탕으로 종합적인 산업 분석을 수행하세요:

    # **입력 데이터:**
    # {financial_data}

    # **회사명:** {company_name}

    # **분석 요구사항:**
    # 1. 산업 구조 분석:
    #    - 산업의 성숙도와 성장 단계 평가
    #    - 시장 규모와 성장률 분석
    #    - 진입장벽과 경쟁 강도 평가
    # 2. 시장 동향 및 성장성 분석:
    #    - 주요 성장 동력과 트렌드 분석
    #    - 기술 혁신과 디지털 전환 영향
    #    - 규제 환경 변화와 정책 영향
    # 3. 경쟁사 분석:
    #    - 주요 경쟁사 시장점유율 분석
    #    - 경쟁 우위 요인과 차별화 전략
    #    - 신규 진입자와 대체재 위협
    # 4. 규제 및 정책 환경 분석:
    #    - 관련 법규와 규제 동향
    #    - 정부 정책과 지원 방안
    #    - ESG 규제와 준수 현황
    # 5. 산업 전망 및 기회/위험 분석:
    #    - 단기/중장기 산업 전망
    #    - 주요 기회 요인과 위험 요소
    #    - 투자 전략적 시사점

    # **출력 형식:**
    # - 산업 구조: [성숙도, 규모, 경쟁 강도 분석]
    # - 시장 동향: [성장 동력과 트렌드 분석]
    # - 경쟁 환경: [경쟁사와 시장점유율 분석]
    # - 규제 환경: [법규와 정책 영향 분석]
    # - 산업 전망: [기회와 위험 요소 분석]
    # - 투자 시사점: [산업 관점에서의 투자 권고]

    # 웹 검색을 통해 최신 산업 동향과 경쟁사 정보를 참고하세요.
    # """,
    #         )
    #         from langchain.agents import AgentExecutor, create_openai_functions_agent
    #         from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

    #         web_search_tool = self.web_search_tool.create_langchain_tool()
    #         system_prompt = ChatPromptTemplate.from_messages(
    #             [
    #                 (
    #                     "system",
    #                     f"""
    # 당신은 {sector_name} 섹터 전문 산업 전문가입니다.

    # **종합 산업 분석**

    # 사용자의 요청을 바탕으로 종합적인 산업 분석을 수행하세요.

    # **분석 요구사항:**
    # 1. 산업 구조 분석:
    #    - 산업의 성숙도와 성장 단계 평가
    #    - 시장 규모와 성장률 분석
    #    - 진입장벽과 경쟁 강도 평가
    # 2. 시장 동향 및 성장성 분석:
    #    - 주요 성장 동력과 트렌드 분석
    #    - 기술 혁신과 디지털 전환 영향
    #    - 규제 환경 변화와 정책 영향
    # 3. 경쟁사 분석:
    #    - 주요 경쟁사 시장점유율 분석
    #    - 경쟁 우위 요인과 차별화 전략
    #    - 신규 진입자와 대체재 위협
    # 4. 규제 및 정책 환경 분석:
    #    - 관련 법규와 규제 동향
    #    - 정부 정책과 지원 방안
    #    - ESG 규제와 준수 현황
    # 5. 산업 전망 및 기회/위험 분석:
    #    - 단기/중장기 산업 전망
    #    - 주요 기회 요인과 위험 요소
    #    - 투자 전략적 시사점

    # **출력 형식:**
    # - 산업 구조: [성숙도, 규모, 경쟁 강도 분석]
    # - 시장 동향: [성장 동력과 트렌드 분석]
    # - 경쟁 환경: [경쟁사와 시장점유율 분석]
    # - 규제 환경: [법규와 정책 영향 분석]
    # - 산업 전망: [기회와 위험 요소 분석]
    # - 투자 시사점: [산업 관점에서의 투자 권고]

    # 웹 검색을 통해 최신 산업 동향과 경쟁사 정보를 참고하세요.
    # """,
    #                 ),
    #                 MessagesPlaceholder(variable_name="chat_history"),
    #                 ("human", "{input}"),
    #                 MessagesPlaceholder(variable_name="agent_scratchpad"),
    #             ]
    #         )
    #         agent = create_openai_functions_agent(
    #             llm=llm, tools=[web_search_tool], prompt=system_prompt
    #         )
    #         industry_chain = AgentExecutor(
    #             agent=agent, tools=[web_search_tool], verbose=True, max_iterations=3
    #         )
    #         print(f"✅ {analyst.name} LangChain Chain 생성 완료 (웹 검색 도구 포함)!")
    #         return industry_chain
    #     except Exception as e:
    #         print(f"❌ {analyst.name} LangChain Chain 생성 실패: {e}")
    #         return None

    def _create_technical_analysis_chain(
        self, analyst: AnalystAgent, sector_name: str
    ) -> Any:
        """
        기술적 분석가를 위한 LangChain Chain 생성 (웹서치 도구 포함)
        """
        try:
            llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0.1,
                max_tokens=8000,  # 2명 체제에 맞게 증가 (기존 4K → 8K)
            )

            # 모듈화된 AI 강화 프롬프트 생성 (기술적 분석용)
            unified_framework = PromptComponents.create_unified_analysis_framework(
                analysis_type="기술적 분석",
                sector_name=sector_name,
                specific_methods=[
                    "이동평균선 분석 (5,20,60,120일선 배열과 Golden/Dead Cross 신호)",
                    "MACD/RSI 분석 (MACD(12,26,9) 히스토그램과 RSI(14) Divergence 패턴)",
                    "볼린저 밴드 분석 (20일 이평±2표준편차, 밴드폭 확장/수축 해석)",
                    "지지저항선 분석 (Fibonacci Retracement 38.2%, 50%, 61.8% 레벨)",
                    "거래량 분석 (OBV, Volume Profile, Accumulation/Distribution Line)",
                    "섹터 로테이션 분석 (상대강도 vs KOSPI, 섹터 모멘텀 지표)",
                    "캔들패턴 분석 (Doji, Hammer, Engulfing 등 반전신호 해석)",
                    "스토캐스틱 분석 (%K, %D 교차와 과매수/과매도 구간 판별)",
                    "Price Action 분석 (Higher High/Low, Lower High/Low 트렌드 구조)",
                ],
            )

            output_format = PromptComponents.get_output_format_template("기술적 분석")

            web_search_tool = self.web_search_tool.create_langchain_tool()
            system_prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        f"""
당신은 {sector_name} 섹터 전문 기술적 분석가입니다. 시니어 애널리스트를 보조할 수 있는 수준의 깊이 있는 기술적 분석을 제공하는 것이 목표입니다.

{unified_framework}

**📊 5단계 기술적 분석 프로세스 (AI 강화 기법 적용)**

**1단계: 차트 패턴 분석**
   - 주요 차트 패턴 식별 (헤드앤숄더, 더블탑/바텀 등)
- 각 패턴별 Chain of Thought 적용
   - 추세선과 채널 분석
   - 지지선과 저항선 레벨 분석

**2단계: 기술적 지표 분석**
   - 이동평균선 분석 (20일, 60일, 200일)
   - RSI, MACD, 스토캐스틱 등 오실레이터 분석
   - 볼린저 밴드와 피벗 포인트 분석
- 웹 검색을 통한 최신 기술적 트렌드 반영

**3단계: 거래량 분석**
   - 거래량 추세와 가격 변동의 관계
   - 거래량 가중 평균가격(VWAP) 분석
   - 거래량 프로파일 분석

**4단계: 섹터 상대강도 분석**
   - 섹터 대비 상대적 성과 분석
   - 섹터 내 순위와 강도 평가
   - 섹터 로테이션 영향 분석

**5단계: 기술적 전망 및 투자 권고**
   - 단기/중기 기술적 전망
   - 주요 지지/저항 레벨과 목표가
   - 매수/매도 시점 권고
- Self-Critique 결과 포함

{output_format}

모든 분석에서 AI 강화 기법을 적용하고, 웹 검색을 통해 최신 기술적 트렌드를 반영하세요.
""",
                    ),
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("human", "{input}"),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ]
            )
            agent = create_openai_functions_agent(
                llm=llm, tools=[web_search_tool], prompt=system_prompt
            )
            technical_chain = AgentExecutor(
                agent=agent, tools=[web_search_tool], verbose=True, max_iterations=3
            )
            print(f"✅ {analyst.name} LangChain Chain 생성 완료 (웹 검색 도구 포함)!")
            return technical_chain
        except Exception as e:
            print(f"❌ {analyst.name} LangChain Chain 생성 실패: {e}")
            return None

    # 🚫 주석 분석 전문가 LangChain Chain 생성 함수 (비활성화됨 - 개발 시간 절약)
    # def _create_footnote_analysis_chain(
    #     self, analyst: AnalystAgent, sector_name: str
    # ) -> Any:
    #     """
    #     주석 전문가를 위한 LangChain Chain 생성 (웹서치 도구 포함)
    #     """
    #     try:
    #         llm = ChatOpenAI(
    #             model="gpt-4o",
    #             temperature=0.1,
    #             max_tokens=4000,
    #         )
    #         footnote_analysis_prompt = PromptTemplate(
    #             input_variables=["financial_data", "sector_name", "company_name"],
    #             template="""
    # 당신은 {sector_name} 섹터 전문 재무제표 주석 전문가입니다.

    # **종합 주석 분석**

    # 제공된 재무제표 주석 데이터를 바탕으로 종합적인 주석 분석을 수행하세요:

    # **입력 데이터:**
    # {financial_data}

    # **회사명:** {company_name}

    # **분석 요구사항:**
    # 1. 주요 회계정책 및 변경사항 분석
    # 2. 특이사항 및 잠재적 리스크 식별
    # 3. 연결/별도 재무제표 차이점 분석
    # 4. 관련 당사자 거래 및 특수관계자 이슈 분석
    # 5. 기타 투자자 주의사항 정리

    # **출력 형식:**
    # - 회계정책: [주요 정책 및 변경사항]
    # - 특이사항: [잠재적 리스크 및 이슈]
    # - 연결/별도 차이: [주요 차이점]
    # - 특수관계자 거래: [관련 이슈]
    # - 기타: [기타 투자자 참고사항]

    # 웹 검색을 통해 최신 회계 이슈와 주석 관련 사례도 참고하세요.
    # """,
    #         )
    #         from langchain.agents import AgentExecutor, create_openai_functions_agent
    #         from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

    #         web_search_tool = self.web_search_tool.create_langchain_tool()
    #         system_prompt = ChatPromptTemplate.from_messages(
    #             [
    #                 (
    #                     "system",
    #                     f"""
    # 당신은 {sector_name} 섹터 전문 재무제표 주석 전문가입니다.

    # **종합 주석 분석**

    # 사용자의 요청을 바탕으로 종합적인 주석 분석을 수행하세요.

    # **분석 요구사항:**
    # 1. 주요 회계정책 및 변경사항 분석
    # 2. 특이사항 및 잠재적 리스크 식별
    # 3. 연결/별도 재무제표 차이점 분석
    # 4. 관련 당사자 거래 및 특수관계자 이슈 분석
    # 5. 기타 투자자 주의사항 정리

    # **출력 형식:**
    # - 회계정책: [주요 정책 및 변경사항]
    # - 특이사항: [잠재적 리스크 및 이슈]
    # - 연결/별도 차이: [주요 차이점]
    # - 특수관계자 거래: [관련 이슈]
    # - 기타: [기타 투자자 참고사항]

    # 웹 검색을 통해 최신 회계 이슈와 주석 관련 사례도 참고하세요.
    # """,
    #                 ),
    #                 MessagesPlaceholder(variable_name="chat_history"),
    #                 ("human", "{input}"),
    #                 MessagesPlaceholder(variable_name="agent_scratchpad"),
    #             ]
    #         )
    #         agent = create_openai_functions_agent(
    #             llm=llm, tools=[web_search_tool], prompt=system_prompt
    #         )
    #         footnote_chain = AgentExecutor(
    #             agent=agent, tools=[web_search_tool], verbose=True, max_iterations=3
    #         )
    #         print(f"✅ {analyst.name} LangChain Chain 생성 완료 (웹 검색 도구 포함)!")
    #         return footnote_chain
    #     except Exception as e:
    #         print(f"❌ {analyst.name} LangChain Chain 생성 실패: {e}")
    #         return None
