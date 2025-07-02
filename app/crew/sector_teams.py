# -*- coding: utf-8 -*-
"""
섹터별 전문 분석팀 팩토리 시스템

11개 GICS 섹터별로 6명의 전문가 에이전트를 정의해요
각 섹터마다 맞춤형 분석 전문가들이 있어요!
LangChain을 통한 시니어 애널리스트급 성능 향상!
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

# LangChain imports
from langchain.chains import LLMChain, SequentialChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.schema import BaseMemory
from langchain.tools import Tool
from langchain_openai import ChatOpenAI

from .gics_sectors import GICSSector, GICSSectorManager


@dataclass
class AnalystAgent:
    """
    개별 분석가 에이전트 정의
    각 에이전트는 고유한 전문 분야와 역할을 가져요

    GICS 섹터별 특화된 분석 포인트와 위험 요소를 반영한 전문가에요!
    LangChain을 통한 시니어 애널리스트급 성능 향상!
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
            # Memory 시스템 설정
            self.memory_system = ConversationBufferMemory(
                memory_key="analysis_history", return_messages=True
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
        LangChain을 사용한 고급 분석 수행

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

            # LangChain Chain 실행 (최신 API 사용)
            if hasattr(self.langchain_chain, "invoke"):
                # 최신 LangChain API
                result = self.langchain_chain.invoke(input_data)
            else:
                # 구버전 호환성
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
                f"✅ {self.name} LangChain 분석 완료 (소요시간: {analysis_time:.2f}초)"
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
        """성능 지표 업데이트"""
        # 응답 시간 업데이트
        self.performance_metrics["response_time"] = analysis_result.get(
            "analysis_time", 0.0
        )

        # 정확도는 추후 사용자 피드백으로 업데이트
        # 일관성은 이전 분석과의 비교로 계산
        if len(self.analysis_history) > 1:
            # 간단한 일관성 계산 (실제로는 더 복잡한 로직 필요)
            self.performance_metrics["consistency"] = 0.8  # 예시 값

    def get_analysis_summary(self) -> Dict[str, Any]:
        """분석 요약 정보 반환"""
        return {
            "agent_name": self.name,
            "role": self.role,
            "total_analyses": len(self.analysis_history),
            "performance_metrics": self.performance_metrics,
            "langchain_enabled": self.langchain_enabled,
            "last_analysis": (
                self.analysis_history[-1] if self.analysis_history else None
            ),
        }

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

    def run_full_valuation_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        밸류에이션 전문가 5단계 전체 분석을 순차적으로 실행해요
        (LangChain RunnableSequence 기반)

        Args:
            input_data: {
                'financial_data': str(재무데이터),
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

            # 5단계 전체 실행 (함수 호출)
            chain_result = self.langchain_chain(input_data)

            # 분석 시간 계산
            analysis_time = (datetime.now() - start_time).total_seconds()

            # 단계별 결과를 dict로 정리
            result_dict = {
                "step1_result": chain_result.get("step1_result"),
                "step2_result": chain_result.get("step2_result"),
                "step3_result": chain_result.get("step3_result"),
                "step4_result": chain_result.get("step4_result"),
                "step5_result": chain_result.get("step5_result"),
                "analysis_time": analysis_time,
                "agent_name": self.name,
                "role": self.role,
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

            # 5단계 전체 실행 (함수 호출)
            chain_result = self.langchain_chain(input_data)

            # 분석 시간 계산
            analysis_time = (datetime.now() - start_time).total_seconds()

            # 단계별 결과를 dict로 정리
            result_dict = {
                "step1_result": chain_result.get("step1_result"),
                "step2_result": chain_result.get("step2_result"),
                "step3_result": chain_result.get("step3_result"),
                "step4_result": chain_result.get("step4_result"),
                "step5_result": chain_result.get("step5_result"),
                "analysis_time": analysis_time,
                "agent_name": self.name,
                "role": self.role,
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

    def run_full_footnote_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        주석 전문가 5단계 전체 분석을 순차적으로 실행해요
        (LangChain Chain 기반)

        Args:
            input_data: {
                'financial_data': str(재무제표 주석 데이터),
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

            # 5단계 전체 실행 (함수 호출)
            chain_result = self.langchain_chain(input_data)

            # 분석 시간 계산
            analysis_time = (datetime.now() - start_time).total_seconds()

            # 단계별 결과를 dict로 정리
            result_dict = {
                "step1_result": chain_result.get("step1_result"),
                "step2_result": chain_result.get("step2_result"),
                "step3_result": chain_result.get("step3_result"),
                "step4_result": chain_result.get("step4_result"),
                "step5_result": chain_result.get("step5_result"),
                "analysis_time": analysis_time,
                "agent_name": self.name,
                "role": self.role,
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


@dataclass
class SectorTeam:
    """
    섹터별 분석팀 정의
    5명의 전문가로 구성된 팀이에요
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

    각 섹터마다 5명의 전문가를 배치해요:
    1. 펀더멘털 분석가 (Fundamental Analyst)
    2. 기술적 분석가 (Technical Analyst)
    3. 산업 전문가 (Industry Expert)
    4. 밸류에이션 전문가 (Valuation Specialist)
    5. 리스크 평가자 (Risk Assessor)
    """

    def __init__(self, sector_manager: GICSSectorManager):
        """
        섹터팀 팩토리 초기화

        Args:
            sector_manager: GICS 섹터 매니저
        """
        self.sector_manager = sector_manager
        print("🎯 섹터별 분석팀 팩토리 초기화 완료!")

    def create_sector_team(self, sector: GICSSector) -> SectorTeam:
        """
        특정 섹터의 전문 분석팀을 생성해요

        GICS 섹터별 특화된 분석 포인트와 위험 요소를 반영한
        5명의 전문가로 구성된 팀을 만들어요!

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

        # 섹터별 5명의 전문가 생성 (섹터별 특화 정보 반영)
        experts = []

        # 1. 펀더멘털 분석가 (섹터 특화) - 🎯 시니어 애널리스트 수준 업그레이드
        fundamental_analyst = AnalystAgent(
            name=f"{sector_korean_name} 펀더멘털 분석가",
            role="Fundamental Analyst",
            expertise="재무제표 분석, 기업가치 평가, 수익성 분석",
            analysis_focus=f"{sector_korean_name} 섹터의 재무 건전성과 성장성 분석",
            key_methods=[
                "🧠 **분석 방법론**: Chain of Thought (CoT) + Reasoning 모델 적용",
                "",
                "**사고 과정 구조**:",
                "1. **데이터 수집 및 정리**: 수집된 재무데이터, 시장정보, 경쟁사 데이터 정리",
                "2. **패턴 인식**: 과거 트렌드와 현재 상황 비교 분석",
                "3. **인과관계 분석**: 수치 변화의 근본 원인과 영향 요인 파악",
                "4. **시나리오 구축**: 다양한 가정 하에서의 미래 전망 시뮬레이션",
                "5. **리스크 평가**: 각 시나리오별 발생 확률과 영향도 계산",
                "6. **종합 판단**: 모든 분석을 종합한 투자 의견 도출",
                "",
                "**핵심 분석 방법론**:",
                "• 손익계산서 분석 (매출성장률, 영업이익률, 순이익률 트렌드 분석)",
                "• 대차대조표 분석 (부채비율, 유동비율, 자기자본비율 정량평가)",
                "• 현금흐름표 분석 (영업CF, 투자CF, 재무CF 3년 평균 분석)",
                "• ROE/ROA 분석 (DuPont 3단계 분해분석 수행)",
                "• 수익성 분석 (ROIC, EBITDA마진, FCF마진 동종업계 대비)",
                "• 재무비율 종합분석 (안전성, 수익성, 성장성, 활동성 4대 영역)",
                "• Working Capital 분석 (운전자본 효율성 및 Cash Cycle 산출)",
                "• Capital Structure 분석 (최적자본구조 대비 현재 레버리지 평가)",
            ],
            sector_context=f"{sector_korean_name} 섹터 전문 펀더멘털 분석가로서 섹터 특성을 반영한 재무 분석을 수행",
            sector_specific_points=(
                analysis_points_list[:3]
                if len(analysis_points_list) >= 3
                else analysis_points_list
            )
            + [
                "⭐ 펀더멘털 분석 시 반드시 다음을 포함:",
                "🔴 **중요**: 제공된 실제 재무데이터를 최우선으로 사용하고, 가정 사용시 반드시 '(가정)' 표시",
                "💡 **1단계: 시계열 트렌드 분석** (CoT 적용)",
                "",
                "**사고 과정**:",
                "1. **데이터 정리**: 3년간 재무비율 데이터를 시간순으로 정렬",
                "2. **패턴 발견**: 각 지표의 변화 방향과 속도 분석",
                "3. **인과관계 추론**: 변화의 근본 원인과 연관성 파악",
                "4. **지속성 평가**: 현재 트렌드가 미래에도 지속될 가능성 판단",
                "",
                "**분석 요구사항**:",
                "1-1. 주요 재무비율 3년 추세 분석: ROE, ROA, ROIC, 유동비율, 부채비율의 과거 3년 변화 추이",
                "1-2. 매출/영업이익/순이익의 3년 CAGR 계산 및 성장 지속성 평가",
                "1-3. 현금흐름의 안정성: 3년간 FCF 변동성과 영업CF 대비 투자CF 비율 분석",
                "1-4. 배당의 지속가능성: 3년간 배당성향과 FCF 커버리지 추세 분석",
                "📊 **2단계: 경쟁사 및 벤치마크 비교 분석** (CoT 적용)",
                "",
                "**사고 과정**:",
                "1. **벤치마크 설정**: 업계 평균과 경쟁사 데이터 수집 및 정리",
                "2. **상대적 위치 파악**: 분석 대상 기업의 업계 내 순위와 차이점 계산",
                "3. **경쟁우위 분석**: 상대적 우위의 원인과 지속가능성 평가",
                "4. **전략적 의미 도출**: 경쟁사 대비 차별화 요소의 투자 가치 평가",
                "",
                "**분석 요구사항**:",
                "2-1. **인터넷 서치 활용**: 동종업계 상위 3~5개 경쟁사의 최신 재무비율 검색",
                "2-2. 업계 평균 대비 Percentile 순위: ROE, ROIC, 매출성장률, 이익률에서의 상대적 위치",
                "2-3. 경쟁우위 지속성 분석: 경쟁사 대비 우수한 지표의 지속 가능성과 근본 원인",
                "2-4. 시장점유율 변화: 최근 3년간 주요 경쟁사 대비 시장점유율 변화 추이",
                "2-5. **인터넷 서치로 확인**: 업계 평균 PER, PBR, EV/EBITDA 멀티플과 비교",
                "2-6. **검색 출처 명시**: '인터넷 서치를 통해 확인한 정보는 [출처: 검색결과]로 명시'",
                "🔍 **3단계: 이상 변화 설명 및 질적 분석** (CoT 적용)",
                "",
                "**사고 과정**:",
                "1. **이상 패턴 식별**: 예상과 다른 재무지표 변화 발견",
                "2. **근본 원인 추적**: 내부 요인과 외부 요인을 구분하여 원인 분석",
                "3. **영향도 평가**: 각 요인이 재무성과에 미치는 정량적 영향 계산",
                "4. **지속가능성 판단**: 일시적 요인과 구조적 변화를 구분",
                "",
                "**분석 요구사항**:",
                "3-1. 재무지표 이상변화 원인 분석: 매출 감소인데 이익 증가, ROE 급락 등의 배경 설명",
                "3-2. **인터넷 서치 활용**: 최근 업황, 산업 사이클, 규제 변화 등 외부 환경 정보 수집",
                "3-3. 제품 믹스 변화가 수익성에 미친 영향: 고부가가치 제품 비중 변화 분석",
                "3-4. 원가절감 효과 vs 일회성 요인 구분: 지속가능한 이익 개선 vs 일시적 효과",
                "3-5. ESG 요인이 재무성과에 미치는 영향: 환경규제, 사회적 이슈, 지배구조 개선 효과",
                "3-6. **인터넷 서치로 확인**: 지정학적 리스크, 환율, 원자재 가격 등이 실적에 미친 영향",
                "🎯 **4단계: 완성된 밸류에이션 분석** (CoT 적용)",
                "",
                "**사고 과정**:",
                "1. **내재가치 계산**: 다양한 밸류에이션 방법론으로 기업의 진정한 가치 산출",
                "2. **시장가치 비교**: 현재 시장가치와 내재가치의 차이 분석",
                "3. **프리미엄/디스카운트 평가**: 시장의 과대/과소 평가 여부 판단",
                "4. **투자 매력도 종합**: 모든 밸류에이션 결과를 종합한 최종 평가",
                "",
                "**분석 요구사항**:",
                "4-1. FCF Yield 완전 계산: FCF/시가총액 × 100, 시가총액은 현재주가 × 발행주식수로 산출",
                "4-2. 멀티플 분석 완성: 현재 PER, PBR, EV/EBITDA와 과거 3년 평균 및 업계 평균 비교",
                "4-3. **인터넷 서치 활용**: 애널리스트 컨센서스 목표가와 비교하여 밸류에이션 매력도 평가",
                "4-4. **WACC 실제 계산 및 DCF 분석**: 사업보고서 데이터로 WACC 직접 산출 후 DCF 계산",
                "   - 타인자본 비용(Rd) = 이자비용 ÷ 유이자부채",
                "   - 법인세율(T) = 법인세비용 ÷ 세전이익",
                "   - 자기자본비용(Re) = 국고채 3년물 + 베타 × 시장위험프리미엄 (인터넷 서치로 베타 확인)",
                "   - WACC = (시가총액/(시가총액+차입금) × Re) + (차입금/(시가총액+차입금) × Rd × (1-T))",
                "   - 계산된 WACC로 향후 3년 FCF 현재가치 산출",
                "4-5. Sum-of-Parts 분석: 주요 사업부문별 기여도와 각각의 밸류에이션 배수 적용",
                "4-6. 목표주가 레인지 제시: 보수적/기본/낙관적 시나리오별 12개월 목표가 산출",
                "⚖️ **5단계: 투자 의견 및 리스크 종합 평가** (CoT 적용)",
                "",
                "**사고 과정**:",
                "1. **종합 분석**: 모든 재무지표와 밸류에이션 결과를 통합 검토",
                "2. **리스크 평가**: 각 리스크 요인의 발생 확률과 영향도 정량화",
                "3. **투자 매력도 판단**: 수익성, 성장성, 안정성의 균형점 도출",
                "4. **최종 의견 도출**: 모든 분석을 종합한 명확한 투자 권고",
                "",
                "**분석 요구사항**:",
                "5-1. DuPont 분해를 통한 ROE 동력 분석 (순이익률×자산회전율×레버리지)",
                "5-2. Working Capital 변동이 영업현금흐름에 미치는 영향 정량화 - 제공된 재무제표 실제 수치 활용",
                "5-3. 부채상환능력 지표 (Interest Coverage, Debt Service Coverage) 산출 - 제공된 손익계산서 실제 데이터 사용",
                "5-4. 배당정책 지속가능성 분석 (Payout Ratio, Dividend Coverage) - 제공된 배당 실제 데이터 활용",
                "5-5. 계절성/경기민감성이 재무성과에 미치는 영향도 평가",
                "5-6. **최종 투자 의견**: 매수/보유/매도 판단과 구체적 근거, 리스크 요인 명시",
                "📊 **6단계: 자본배분과 전략 연계 분석**",
                "6-1. 현재 자본배분 구조 분석: 배당, 투자, 유보의 비중과 적정성 평가",
                "6-2. 전략적 우선순위 분석: 성장 투자와 주주환원의 균형점 도출",
                "6-3. 지속가능성 평가: 현재 배당정책의 장기적 지속 가능성 판단",
                "6-4. 최적화 방안 도출: 자본배분 구조 개선을 위한 구체적 방안",
                "📊 **7단계: ESG 및 비재무 평가 현실 적용**",
                "7-1. 지배구조 분석: 수집된 ESG 데이터로 지배구조의 투명성과 효율성 평가",
                "7-2. 환경 리스크 평가: 환경 정책 변화가 비즈니스에 미치는 영향 분석",
                "7-3. 사회적 책임 투자 영향: ESG 평가가 투자자 행동과 기업가치에 미치는 영향",
                "7-4. 실무적 적용: ESG 요소가 실제 투자 결정에 미치는 구체적 영향",
                "📊 **8단계: 매크로/정책 리스크 연동 분석**",
                "8-1. 매크로 변수 민감도 분석: 금리, 환율, 경제성장률 변화의 영향 계산",
                "8-2. 정책 리스크 평가: 수집된 정책 정보로 규제 변화의 영향 분석",
                "8-3. 시나리오별 영향도 계산: 각 리스크 요인의 발생 시 재무적 영향 정량화",
                "8-4. 리스크 관리 방안: 위험 요소에 대한 대응 전략 도출",
                "📊 **9단계: 사업부별 드릴다운 분석**",
                "9-1. 세그먼트별 성과 분석: 수집된 사업부별 데이터로 수익성과 성장성 평가",
                "9-2. 전략적 중요도 평가: 각 사업부의 전체 기업에서 차지하는 전략적 비중",
                "9-3. 성장 전망 분석: 사업부별 미래 성장 가능성과 투자 우선순위",
                "9-4. 포트폴리오 최적화: 사업부 조합의 최적화 방안 도출",
                "📊 **10단계: 시나리오 기반 밸류에이션**",
                "10-1. 시나리오 구축: 수집된 데이터를 바탕으로 현실적인 시나리오 설정",
                "10-2. 각 시나리오별 밸류에이션: DCF, 멀티플 등 다양한 방법으로 가치 평가",
                "10-3. 확률 가중: 각 시나리오의 발생 확률을 고려한 확률가중 가치 계산",
                "10-4. 민감도 분석: 주요 변수의 변화가 목표가에 미치는 영향 분석",
                "🔴 **데이터 활용 우선순위**:",
                "- 1순위: 제공된 DART 재무제표의 실제 수치 사용",
                "- 2순위: 인터넷 서치를 통한 최신 업계 정보 보완",
                "- 3순위: 합리적 가정 사용 (반드시 '(가정)' 표시하고 근거 설명)",
                "- **인터넷 서치 필수 항목**: 경쟁사 재무비율, 업계 평균 멀티플, 애널리스트 컨센서스, 최신 업황, **베타 계수**",
                "- **검색 결과 활용 시**: 반드시 '[인터넷 서치 출처: 검색결과]' 명시",
                "💰 **WACC 계산 상세 가이드**:",
                "- **Step 1**: 사업보고서에서 이자비용, 법인세, 세전이익, 총차입금 추출",
                "- **Step 2**: 인터넷 서치로 베타, 국고채 3년물 수익률, 시장위험프리미엄 확인",
                "- **Step 3**: 타인자본비용(Rd) = 이자비용 ÷ 총차입금",
                "- **Step 4**: 법인세율(T) = 법인세비용 ÷ 세전이익",
                "- **Step 5**: 자기자본비용(Re) = 무위험수익률 + 베타 × 위험프리미엄",
                "- **Step 6**: WACC = (E/(E+D) × Re) + (D/(E+D) × Rd × (1-T))",
                "- **WACC 계산시 가정값 사용 허용**: 베타 검색 불가시 업계 평균 1.2 사용, 위험프리미엄은 5.5% 사용",
                "📈 **추가 개선 요구사항**:",
                "- 모든 비율은 소수점 둘째 자리까지 표시",
                "- 백분율은 %로 명확히 표기",
                "- 계산 과정은 단계별로 명시 (예: ROE = 순이익(2.3조) ÷ 자기자본(25조) = 9.2%)",
                "- 업계 평균과의 괴리를 구체적 수치로 제시 (예: 업계 평균 12% 대비 3%p 낮음)",
                "- 시간 가중 평균 등 정교한 계산 방법 적용",
                "- 결론은 정량적 근거를 바탕으로 명확한 투자 의견 제시",
            ],
            risk_awareness=[f"재무적 관점에서 {risk_factors}"],
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
            ],
            langchain_enabled=True,  # 🚀 LangChain 활성화
        )

        # 🚀 펀더멘털 분석가 LangChain Chain 설정
        fundamental_analyst.langchain_chain = self._create_fundamental_analysis_chain(
            fundamental_analyst, sector_korean_name
        )

        experts.append(fundamental_analyst)

        # 2. 기술적 분석가 (섹터 특화) - 🎯 시니어 애널리스트 수준 업그레이드
        technical_analyst = AnalystAgent(
            name=f"{sector_korean_name} 기술적 분석가",
            role="Technical Analyst",
            expertise="차트 패턴 분석, 기술적 지표 해석, 시장 심리 분석",
            analysis_focus=f"{sector_korean_name} 섹터의 가격 움직임과 매매 신호 분석",
            key_methods=[
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
            sector_context=f"{sector_korean_name} 섹터의 경기민감성과 변동성을 고려한 기술적 분석 전문가",
            sector_specific_points=[
                f"기술적 관점에서 {sector_context.get('cyclical_nature', '섹터 특성')} 반영",
                "⭐ 기술적 분석 시 반드시 다음을 포함:",
                "1. 주요 이동평균선 배열 상태와 매매신호 해석 (정배열/역배열)",
                "2. MACD 히스토그램 변화율과 Signal Line 교차 타이밍 분석",
                "3. RSI Divergence 패턴과 과매수/과매도 구간 진입/이탈 시점",
                "4. 볼린저 밴드 squeeze/expansion 패턴과 밴드 이탈 방향성",
                "5. 주요 지지/저항선 수준과 돌파시 목표가 산출 (측정이론 적용)",
                "6. 거래량 동반 여부와 Price-Volume Relationship 해석",
                "7. 섹터 상대강도 분석과 시장 대비 아웃퍼폼/언더퍼폼 판단",
                "8. 단기(1주), 중기(1개월), 장기(3개월) 기술적 전망과 핵심 변곡점",
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

        # 3. 산업 전문가 (섹터 특화) - 🎯 시니어 애널리스트 수준 업그레이드
        industry_expert = AnalystAgent(
            name=f"{sector_korean_name} 산업 전문가",
            role="Industry Expert",
            expertise="산업 분석, 경쟁 구조 분석, 트렌드 예측",
            analysis_focus=f"{sector_korean_name} 산업의 구조적 변화와 성장 동력 분석",
            key_methods=[
                "Porter 5 Forces 분석 (신규진입, 대체재, 공급업체, 구매자, 경쟁강도)",
                "밸류체인 분석 (Primary & Support Activities 마진 기여도 분해)",
                "SWOT 분석 (내부 강점/약점 vs 외부 기회/위협 4분면 매트릭스)",
                "경쟁사 벤치마킹 (시장점유율, 수익성, 성장률 3년 트렌드 비교)",
                "시장점유율 분석 (HHI 지수, Top 3/5 집중도, 시장 파워 측정)",
                "BCG Growth-Share Matrix (Star, Cash Cow, Question Mark, Dog 분류)",
                "Technology Life Cycle 분석 (도입/성장/성숙/쇠퇴 단계별 전략)",
                "Competitive Moat 분석 (네트워크 효과, 브랜드, 규모경제, 전환비용)",
                "Supply Chain 분석 (업스트림/다운스트림 관계와 Power Balance)",
            ],
            sector_context=f"{sector_korean_name} 섹터의 산업 구조와 경쟁 환경을 심도 있게 분석하는 전문가",
            sector_specific_points=analysis_points_list
            + [
                "⭐ 산업 분석 시 반드시 다음을 포함:",
                "1. 산업 Life Cycle 상 현재 위치와 향후 3-5년 전망",
                "2. Top 5 경쟁사 대비 Market Share 변화 추이와 경쟁 우위 지속성",
                "3. Porter 5 Forces 각 요소별 점수화 (1-5점)와 종합 매력도 평가",
                "4. 핵심 성공 요인(KSF) 식별과 해당 기업의 KSF 보유 수준 평가",
                "5. 밸류체인 상 핵심 가치 창출 활동과 원가 구조 분석",
                "6. 기술 변화/규제 변화가 산업 구조에 미치는 파급 효과 예측",
                "7. ESG 이슈가 산업 경쟁력에 미치는 장기적 영향도 평가",
                "8. 글로벌 공급망 변화와 지정학적 리스크가 산업에 미치는 영향",
            ],
            risk_awareness=[
                f"산업 구조적 관점에서 {risk_factors}",
                "기술 대체 위험 (Disruptive Innovation으로 인한 산업 구조 변화)",
                "규제 변화 위험 (정부 정책/법규 변경이 산업 수익성에 미치는 영향)",
                "경쟁 심화 위험 (신규 진입자 증가나 가격 경쟁 심화)",
                "공급망 리스크 (원자재 가격 변동성, 공급업체 집중도)",
                "고객 Power 강화 위험 (구매력 집중, 대체재 증가)",
                "ESG 규제 강화 위험 (환경/사회적 책임 요구 증대)",
                "글로벌 Trade War 영향 (관세, 수출입 규제 변화)",
            ],
            critical_metrics=[
                "Market Share (매출 기준, 3년 CAGR)",
                "Industry Growth Rate (시장 성장률 vs 경제 성장률)",
                "HHI Index (허핀달 지수, 시장 집중도 측정)",
                "Entry Barrier Score (진입 장벽 종합 점수)",
                "Switching Cost Index (고객 전환비용 지수)",
                "R&D Intensity (R&D/매출 비율, 혁신 투자 수준)",
                "Capacity Utilization (설비 가동률, 공급 과부족)",
                "Forward/Backward Integration (수직계열화 정도)",
                "Price Premium vs Commodity (프리미엄 vs 범용품 포지셔닝)",
                "Export Dependency (수출 의존도, 환율 민감성)",
            ],
            langchain_enabled=True,  # 🚀 LangChain 활성화
        )

        # 🚀 산업 전문가 LangChain Chain 설정
        industry_expert.langchain_chain = self._create_industry_analysis_chain(
            industry_expert, sector_korean_name
        )

        experts.append(industry_expert)

        # 4. 밸류에이션 전문가 (섹터 특화)
        valuation_specialist = AnalystAgent(
            name=f"{sector_korean_name} 밸류에이션 전문가",
            role="Valuation Specialist",
            expertise="기업가치 평가, 적정주가 산정, 투자지표 분석",
            analysis_focus=f"{sector_korean_name} 기업의 내재가치와 투자 매력도 평가",
            key_methods=[
                "DCF 모델링 (구체적 산출식 제시)",
                "PER/PBR 분석 (업계 평균 대비 산출)",
                "EV/EBITDA 분석 (멀티플 근거 설명)",
                "Sum-of-Parts 분석 (사업부문별 밸류에이션)",
                "배당수익률 분석 (배당성장 모델 적용)",
                "상대가치 평가 (동종업계 비교분석)",
                "목표가 산출 근거 명시 (계산 과정 상세 설명)",
                "시나리오별 민감도 분석 (낙관/기본/비관)",
            ],
            sector_context=f"{sector_korean_name} 섹터 특성을 반영한 맞춤형 밸류에이션 방법론을 적용하는 전문가",
            sector_specific_points=[
                f"밸류에이션 관점에서 {sector_context.get('valuation_approach', '가치평가 방법')}",
                "⭐ **ChatGPT 개선사항 반영 밸류에이션 분석**:",
                "🔴 **중요**: 제공된 실제 재무데이터를 최우선으로 사용하고, 가정 사용시 반드시 '(가정)' 표시",
                "💰 **1단계: 시계열 멀티플 분석 (ChatGPT 지적사항 1,2 해결)**",
                "1-1. 과거 3년간 PER, PBR, EV/EBITDA 추세 분석과 변동 원인 설명",
                "1-2. 역사적 멀티플 대비 현재 밸류에이션 위치 (Percentile 순위)",
                "1-3. 밸류에이션 사이클 분석: 고평가/저평가 구간 패턴 인식",
                "1-4. FCF Yield 3년 트렌드와 채권수익률 대비 매력도 변화",
                "📊 **2단계: 경쟁사 멀티플 비교 (ChatGPT 지적사항 3 해결)**",
                "2-1. **인터넷 서치 필수**: 동종업계 상위 5개 경쟁사 현재 PER, PBR, EV/EBITDA 검색",
                "2-2. 업계 평균 대비 밸류에이션 프리미엄/디스카운트율과 정당성 평가",
                "2-3. **인터넷 서치**: 글로벌 동종업계 평균 멀티플과 비교 (미국, 유럽, 아시아)",
                "2-4. 경쟁사 대비 높은/낮은 밸류에이션의 근본 원인 분석",
                "2-5. **검색 출처 명시**: '[인터넷 서치 출처: 검색결과]'로 표기",
                "🔍 **3단계: 밸류에이션 이상현상 설명 (ChatGPT 지적사항 4 해결)**",
                "3-1. PER 급등/급락의 배경: 일회성 손익 vs 구조적 변화 구분",
                "3-2. PBR 이상 현상: 자산 재평가, 손상차손, M&A 등의 영향 분석",
                "3-3. EV/EBITDA 왜곡 요인: EBITDA 품질, 일회성 비용, 회계변경 영향",
                "3-4. **인터넷 서치**: 최근 업황 변화가 밸류에이션에 미친 영향 확인",
                "🎯 **4단계: 완성된 목표가 산출 (ChatGPT 지적사항 5 해결)**",
                "4-1. **FCF Yield 완전 계산**: FCF(실제값)/시가총액 × 100, 시총=주가×발행주식수",
                "4-2. **WACC 실제 계산**: 사업보고서 데이터로 WACC 직접 산출 (아래 방법 활용)",
                "   - 타인자본 비용(Rd) = 이자비용 ÷ 유이자부채 (손익계산서, 재무상태표)",
                "   - 법인세율(T) = 법인세비용 ÷ 세전이익 (손익계산서)",
                "   - 자기자본(E) = 주가 × 발행주식수 (시가총액)",
                "   - 타인자본(D) = 총차입금 (재무상태표)",
                "   - 자기자본비용(Re) = 무위험수익률 + 베타 × 위험프리미엄 (인터넷 서치로 베타 확인)",
                "   - **WACC = (E/(E+D) × Re) + (D/(E+D) × Rd × (1-T))**",
                "4-3. **DCF 모델 상세**: 향후 5년 FCF 예측, 실제 계산된 WACC 활용, Terminal Value 계산",
                "4-3. **멀티플 방법**: Forward PER, PBR 기반 목표가 (업계 평균 적용)",
                "4-4. **Sum-of-Parts**: 주요 사업부문별 밸류에이션과 지분가치 합산",
                "4-5. **배당할인모델**: 향후 배당성장률 가정하여 내재가치 산출",
                "4-6. **인터넷 서치**: 애널리스트 컨센서스 목표가와 비교 분석",
                "4-7. **가중평균 목표가**: 각 방법론별 신뢰도에 따른 가중치 적용",
                "⚖️ **5단계: 시나리오별 밸류에이션 (ChatGPT 지적사항 6 해결)**",
                "5-1. **낙관 시나리오 (25% 확률)**: 최고 실적 가정시 목표가와 근거",
                "5-2. **기본 시나리오 (50% 확률)**: 컨센서스 기반 목표가와 근거",
                "5-3. **비관 시나리오 (25% 확률)**: 악재 반영시 목표가와 근거",
                "5-4. **확률가중 목표가**: 3시나리오 확률 가중 평균값 산출",
                "5-5. **민감도 분석**: 핵심 변수 ±10% 변동시 목표가 변화폭",
                "5-6. **ESG 요인 반영**: ESG 개선/악화시 밸류에이션 프리미엄/디스카운트",
                "🔴 **밸류에이션 데이터 활용 우선순위**:",
                "- 1순위: 제공된 재무제표 실제 수치 (FCF, 순이익, 자기자본, EBITDA)",
                "- 2순위: 인터넷 서치를 통한 경쟁사/업계 멀티플 정보",
                "- 3순위: 합리적 가정 사용 (반드시 '(가정)' 표시하고 근거 설명)",
                "- **인터넷 서치 필수 항목**: 경쟁사 멀티플, 애널리스트 컨센서스, 업계 평균 밸류에이션",
                "- **검색 결과 활용 시**: 반드시 '[인터넷 서치 출처: 검색결과]' 명시",
                "📈 **추가 개선 요구사항**:",
                "- 모든 멀티플은 소수점 첫째 자리까지 표시 (예: PER 12.3배)",
                "- 목표가는 원단위까지 제시 (예: 목표가 65,000원)",
                "- 계산 과정 명시 (예: DCF = FCF 5조 ÷ WACC 8% = 62.5조원)",
                "- 업계 대비 프리미엄/디스카운트를 %로 명시 (예: 업계 평균 PER 15배 대비 20% 할인)",
                "- 각 밸류에이션 방법론의 가중치와 근거 명시",
                "- 최종 투자의견과 12개월 목표가 명확히 제시",
            ],
            risk_awareness=[f"밸류에이션 관점에서 {risk_factors}"],
            critical_metrics=[
                metric
                for metric in critical_metrics_list
                if any(word in metric for word in ["비율", "수익률", "마진", "배수"])
            ],
            langchain_enabled=True,  # 🚀 LangChain 활성화
        )

        # 🚀 밸류에이션 전문가 LangChain Chain 설정
        valuation_specialist.langchain_chain = self._create_valuation_analysis_chain(
            valuation_specialist, sector_korean_name
        )

        experts.append(valuation_specialist)

        # 5. 리스크 평가자 (섹터 특화) - 🎯 시니어 애널리스트 수준 업그레이드
        risk_assessor = AnalystAgent(
            name=f"{sector_korean_name} 리스크 평가자",
            role="Risk Assessor",
            expertise="위험 요소 분석, 시나리오 분석, 리스크 관리",
            analysis_focus=f"{sector_korean_name} 투자의 주요 리스크와 대응 전략 분석",
            key_methods=[
                "VaR 분석 (Value at Risk, 95% 신뢰구간 1일/10일/1개월 손실 예상)",
                "시나리오 분석 (Base/Bull/Bear Case 3시나리오 확률 가중 평가)",
                "몬테카르로 시뮬레이션 (주요 변수 1만회 시뮬레이션 확률분포)",
                "민감도 분석 (핵심 변수 ±10%, ±20% 변동시 목표가 영향도)",
                "스트레스 테스트 (2008, 2020급 위기상황 가정 충격 시나리오)",
                "ESG 리스크 스코어링 (환경, 사회, 지배구조 3대 영역 정량평가)",
                "신용 리스크 분석 (Altman Z-Score, Credit Default Probability)",
                "유동성 리스크 측정 (시장충격시 매도 가능 시간과 슬리피지)",
                "Beta 분해 분석 (시장, 섹터, 기업고유 리스크 3단계 분해)",
                "Tail Risk 분석 (극단적 손실 확률과 Maximum Drawdown 예측)",
            ],
            sector_context=f"{sector_korean_name} 섹터 고유의 리스크 요인과 함정을 전문적으로 분석하는 리스크 전문가",
            sector_specific_points=[
                f"리스크 관점에서 {analysis_points}",
                "⭐ 리스크 분석 시 반드시 다음을 포함:",
                "🔴 **중요**: 제공된 실제 재무데이터와 시장데이터를 최우선으로 사용하고, 가정 사용시 반드시 '(가정)' 표시",
                "1. 정량적 리스크 지표 산출 (VaR, CVaR, Maximum Drawdown, Sharpe Ratio) - 실제 주가/재무 데이터 기반",
                "2. 3시나리오 분석과 각 시나리오별 발생 확률 및 목표가 Impact - 과거 실적 데이터 기반 산출",
                "3. 주요 리스크 팩터별 민감도 계수와 탄력성 측정 - 제공된 재무제표 실제 수치 활용",
                "4. 스트레스 테스트 결과 (글로벌 금융위기급 충격시 예상 손실률) - 과거 위기시 실제 데이터 참조",
                "5. ESG 리스크 스코어와 ESG 이슈 발생시 주가 하락 폭 예측",
                "6. 신용도 분석 (Altman Z-Score, 부도 확률, Credit Spread 변화) - 실제 재무비율로 계산",
                "7. 유동성 리스크 (일평균 거래대금 대비 대량 매도시 충격도) - 실제 거래량 데이터 기반",
                "8. 섹터 특화 리스크 (규제, 기술, 원자재, 환율 등) 정량 측정",
                "🔴 **리스크 데이터 활용 원칙**:",
                "- 1순위: 제공된 재무제표 실제 수치로 재무비율 계산",
                "- 변동성 측정은 제공된 실제 주가 데이터 우선 사용",
                "- 부도확률 계산은 실제 부채비율, 이자보상비율 등 활용",
                "- 실제 데이터 부족시: 가정 사용하되 반드시 '(가정)' 표시하고 근거 설명",
                "- 가정 예시: 'VaR 5% (가정: 과거 3년 변동성 기준 추정)'",
                "- 실제값과 가정값의 명확한 구분으로 투명성 확보",
                "9. 리스크 대비 수익률 (Risk-Adjusted Return) 동종업계 대비 평가",
                "10. 포트폴리오 내 상관관계와 분산투자 효과 분석",
            ],
            risk_awareness=risk_factors_list
            + [
                "Black Swan Event 리스크 (예측 불가능한 극단적 사건)",
                "Model Risk (리스크 모델의 가정 오류나 과적합 위험)",
                "Concentration Risk (단일 고객/공급업체/지역 집중도 위험)",
                "Operational Risk (시스템 장애, 사기, 인적 오류 등)",
                "Reputation Risk (브랜드 이미지 손상으로 인한 매출 감소)",
                "Regulatory Risk (규제 변화로 인한 사업 모델 변경 위험)",
                "Currency Risk (환율 변동이 손익에 미치는 영향)",
                "Interest Rate Risk (금리 변동이 자금조달비용에 미치는 영향)",
                "Inflation Risk (인플레이션이 실질수익률에 미치는 영향)",
                "Geopolitical Risk (지정학적 긴장이 사업에 미치는 영향)",
            ],
            critical_metrics=[
                "VaR (95% 신뢰구간 1일/1개월)",
                "CVaR (Conditional VaR, 극단손실 평균)",
                "Maximum Drawdown (최대 손실 구간)",
                "Sharpe Ratio (위험 대비 수익률)",
                "Information Ratio (벤치마크 대비 초과수익/추적오차)",
                "Beta (시장 민감도, 1년/3년 구간)",
                "Volatility (20일/60일/252일 변동성)",
                "Downside Deviation (하방 위험 측정)",
                "Altman Z-Score (신용도 측정)",
                "ESG Risk Score (환경/사회/지배구조 리스크)",
                "Liquidity Ratio (거래량 대비 유동성)",
                "Concentration Index (사업/지역 집중도)",
            ],
            langchain_enabled=True,  # 🚀 LangChain 활성화
        )

        # 🚀 리스크 평가자 LangChain Chain 설정
        risk_assessor.langchain_chain = self._create_risk_analysis_chain(
            risk_assessor, sector_korean_name
        )

        experts.append(risk_assessor)

        # 📝 6. 주석 전문 분석가 (사용자 요청 반영! - 새로 추가)
        footnote_specialist = AnalystAgent(
            name=f"{sector_korean_name} 재무제표 주석 전문가",
            role="Financial Statement Footnote Specialist",
            expertise="재무제표 주석(footnote) 분석, 재무상태표 주석 해석, 숨겨진 재무정보 발굴",
            analysis_focus=f"{sector_korean_name} 기업의 재무제표 주석(footnote)에 숨겨진 중요 재무정보와 위험요소를 전문적으로 분석",
            key_methods=[
                "재무상태표(F/S) 주석 상세 분석",
                "손익계산서 주석 해석",
                "현금흐름표 주석 검토",
                "우발채무 및 보증채무 분석",
                "연결범위 변동사항 분석",
                "회계정책 변경 영향도 분석",
                "관계회사 거래내역 분석",
                "파생상품 공정가치 변동 분석",
                "리스 및 약정사항 분석",
                "금융상품 분류 및 평가 분석",
            ],
            sector_context=f"{sector_korean_name} 섹터의 특성을 반영한 재무제표 주석 분석 전문가로서, 재무제표 본문에 드러나지 않은 숨겨진 재무위험과 기회요소를 발굴",
            sector_specific_points=[
                f"{sector_korean_name} 섹터 특화 재무제표 주석 분석 포인트",
                "재무상태표 주석의 핵심 정보 추출 및 해석",
                "주석에 숨겨진 우발부채 및 잠재적 위험요소 발굴",
                "회계처리 방법 변경이 재무성과에 미치는 영향 정량분석",
                "관계회사 거래의 실질적 영향도 평가",
                "금융상품 및 파생상품 위험 노출도 분석",
            ],
            risk_awareness=[
                "재무제표 주석에 숨겨진 우발채무와 보증채무의 실질적 위험도",
                "회계정책 변경으로 인한 손익 조정 및 비교가능성 훼손 위험",
                "연결범위 변동이 재무성과에 미치는 실질적 영향",
                "파생상품 거래의 잠재적 손실 위험 및 헤지 효과성",
                "관계회사 거래의 특수관계자 거래 위험",
                "리스 및 약정사항의 미래 현금흐름 영향",
                f"{sector_korean_name} 섹터 특화 재무제표 주석 위험 요소",
            ],
            critical_metrics=[
                "우발채무/총자산 비율",
                "보증채무/총자본 비율",
                "관계회사 거래/총매출 비중",
                "파생상품 공정가치 변동손익",
                "회계정책 변경 누적영향액",
                "연결범위 변동 영향액",
                "리스부채/총부채 비율",
                "금융상품 신용위험 노출액",
                f"{sector_korean_name} 섹터 주석 특화 재무지표",
            ],
            langchain_enabled=True,  # 🚀 LangChain 활성화
        )

        # 🚀 주석 전문가 LangChain Chain 설정
        footnote_specialist.langchain_chain = self._create_footnote_analysis_chain(
            footnote_specialist, sector_korean_name
        )

        experts.append(footnote_specialist)

        # 섹터팀 생성 (6명 전문가로 확장)
        team = SectorTeam(
            sector=sector,
            team_name=f"{sector_korean_name} 섹터 전문 분석팀",
            team_description=(
                f"{sector_korean_name} 섹터의 종합적인 투자 분석을 수행하는 6명의 전문가팀. "
                f"재무제표 주석 전문가를 포함하여 숨겨진 정보까지 발굴하는 정밀 분석을 제공합니다. "
                f"섹터 특화 분석 포인트와 리스크 요소를 반영하여 정확하고 실용적인 분석을 제공합니다."
            ),
            experts=experts,
            collaboration_strategy=(
                f"{sector_korean_name} 섹터의 {sector_context.get('cyclical_nature', '특성')}을 고려하여 "
                f"6명의 전문가(펀더멘털, 기술, 산업, 밸류에이션, 리스크, 주석)가 "
                f"각자의 전문성을 바탕으로 협업하는 전략. 특히 주석 전문가가 재무제표의 숨겨진 정보를 발굴하여 "
                f"다른 전문가들의 분석 정확도를 향상시킵니다."
            ),
            report_structure={
                "fundamental": f"{sector_korean_name} 섹터 특화 재무 분석 보고서",
                "technical": f"{sector_korean_name} 섹터 기술적 분석 및 시장 동향 보고서",
                "industry": f"{sector_korean_name} 산업 구조 및 경쟁력 분석 보고서",
                "valuation": f"{sector_korean_name} 섹터 맞춤 밸류에이션 보고서",
                "risk": f"{sector_korean_name} 섹터 리스크 요인 및 대응 전략 보고서",
                "footnotes": f"{sector_korean_name} 재무제표 주석 상세 분석 보고서",
            },
        )

        print(
            f"✅ {sector_korean_name} 섹터팀 생성 완료 (전문가 {len(experts)}명 - 주석 전문가 포함)"
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

    def _create_fundamental_analysis_chain(
        self, analyst: AnalystAgent, sector_name: str
    ) -> Any:
        """
        펀더멘털 분석가를 위한 LangChain Chain 생성

        Args:
            analyst: 분석가 객체
            sector_name: 섹터 이름

        Returns:
            Chain: 단일 단계 분석 Chain
        """
        try:
            # LLM 모델 설정 (환경변수에서 API 키 가져오기)
            llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0.1,  # 분석의 일관성을 위해 낮은 temperature
                max_tokens=4000,
            )

            # 단일 단계: 종합 재무 분석 Chain
            fundamental_analysis_prompt = PromptTemplate(
                input_variables=["financial_data", "sector_name", "company_name"],
                template="""
당신은 {sector_name} 섹터 전문 펀더멘털 분석가입니다.

**종합 재무 분석**

제공된 재무데이터를 바탕으로 종합적인 재무 분석을 수행하세요:

**입력 데이터:**
{financial_data}

**회사명:** {company_name}

**분석 요구사항:**
1. 데이터 검증 및 정규화
2. 핵심 재무비율 계산 (ROE, ROA, ROIC, 유동비율, 부채비율 등)
3. 3년간 트렌드 분석 및 변화 패턴 식별
4. CAGR 계산 (매출, 영업이익, 순이익)
5. 현금흐름 안정성 분석
6. DuPont 분석을 통한 ROE 분해
7. 경쟁사 비교 분석 (업계 평균 대비)
8. 종합 평가 및 투자 의견

**출력 형식:**
- 데이터 검증 결과: [통과/부분 통과/실패]
- 재무비율 분석: [구체적 수치와 계산 과정]
- 트렌드 분석: [3년간 변화 추이와 패턴]
- 성장성 평가: [CAGR과 지속가능성]
- 현금흐름 평가: [안정성과 품질]
- 경쟁사 비교: [업계 내 상대적 위치]
- 종합 평가: [재무 건전성과 투자 매력도]
- 투자 의견: [명확한 권고와 근거]

단계별로 사고 과정을 명시하고, 정량적 근거를 제시하세요.
""",
            )

            # 단일 Chain 생성
            fundamental_chain = fundamental_analysis_prompt | llm

            print(f"✅ {analyst.name} LangChain Chain 생성 완료!")
            return fundamental_chain

        except Exception as e:
            print(f"❌ {analyst.name} LangChain Chain 생성 실패: {e}")
            return None

    def _create_valuation_analysis_chain(
        self, analyst: AnalystAgent, sector_name: str
    ) -> Any:
        """
        밸류에이션 전문가를 위한 LangChain Chain 생성

        Args:
            analyst: 분석가 객체
            sector_name: 섹터 이름

        Returns:
            Chain: 단일 단계 분석 Chain
        """
        try:
            # LLM 모델 설정 (OpenAI GPT-4o)
            llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0.1,  # 분석의 일관성을 위해 낮은 값
                max_tokens=4000,
            )

            # 단일 단계: 종합 밸류에이션 분석 프롬프트
            valuation_analysis_prompt = PromptTemplate(
                input_variables=["financial_data", "sector_name", "company_name"],
                template="""
당신은 {sector_name} 섹터 전문 밸류에이션 전문가입니다.

**종합 밸류에이션 분석**

제공된 재무데이터를 바탕으로 종합적인 밸류에이션 분석을 수행하세요:

**입력 데이터:**
{financial_data}

**회사명:** {company_name}

**분석 요구사항:**
1. 시계열 멀티플 분석:
   - 과거 3년간 PER, PBR, EV/EBITDA 계산 및 추세 분석
   - 현재 멀티플의 역사적 Percentile 순위 산출
   - 밸류에이션 사이클 분석 (고평가/저평가 구간 패턴)

2. 경쟁사 비교 분석:
   - 동종업계 상위 5개 경쟁사 현재 멀티플 비교
   - 업계 평균 대비 밸류에이션 프리미엄/디스카운트율 계산
   - 글로벌 동종업계 평균 멀티플과 비교

3. DCF 모델링:
   - WACC 계산 (구체적 계산 과정 포함)
   - 향후 5년 FCF 예측
   - Terminal Value 계산
   - 내재가치 산출

4. 목표가 산출:
   - DCF 기반 목표가
   - 멀티플 기반 목표가 (PER, PBR, EV/EBITDA)
   - 가중평균 목표가 계산

5. 시나리오별 민감도 분석:
   - 낙관/기본/비관 3시나리오 분석
   - 주요 변수별 민감도 분석

**출력 형식:**
- 멀티플 분석: [계산된 멀티플과 트렌드]
- 경쟁사 비교: [업계 대비 상대적 위치]
- DCF 모델링: [내재가치와 계산 과정]
- 목표가 산출: [최종 목표가와 근거]
- 시나리오 분석: [3시나리오별 전망]
- 투자 의견: [매수/보유/매도 권고]

모든 계산 과정을 명시하고, 정량적 근거를 제시하세요.
""",
            )

            # 단일 Chain 생성
            valuation_chain = valuation_analysis_prompt | llm

            print(f"✅ {analyst.name} LangChain Chain 생성 완료!")
            return valuation_chain

        except Exception as e:
            print(f"❌ {analyst.name} LangChain Chain 생성 실패: {e}")
            return None

    def _create_risk_analysis_chain(
        self, analyst: AnalystAgent, sector_name: str
    ) -> Any:
        """
        리스크 평가자를 위한 LangChain Chain 생성

        Args:
            analyst: 분석가 객체
            sector_name: 섹터 이름

        Returns:
            Chain: 단일 단계 분석 Chain
        """
        try:
            # LLM 모델 설정 (OpenAI GPT-4o)
            llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0.1,  # 분석의 일관성을 위해 낮은 값
                max_tokens=4000,
            )

            # 단일 단계: 종합 리스크 분석 프롬프트
            risk_analysis_prompt = PromptTemplate(
                input_variables=["financial_data", "sector_name", "company_name"],
                template="""
당신은 {sector_name} 섹터 전문 리스크 평가자입니다.

**종합 리스크 분석**

제공된 재무데이터를 바탕으로 종합적인 리스크 분석을 수행하세요:

**입력 데이터:**
{financial_data}

**회사명:** {company_name}

**분석 요구사항:**
1. 재무 리스크 분석:
   - 부채비율, 유동비율, 이자보상배율 분석
   - 현금흐름 안정성 평가
   - 신용 리스크 스코어링

2. 사업 리스크 분석:
   - 시장점유율 변화 리스크
   - 경쟁사 대응 리스크
   - 기술 변화 리스크

3. 시장 리스크 분석:
   - 주가 변동성 분석
   - 베타 계수 계산
   - 시장 대비 상대적 리스크

4. ESG 리스크 분석:
   - 환경 리스크 (규제, 기후변화)
   - 사회 리스크 (인권, 노동환경)
   - 지배구조 리스크 (투명성, 독립성)

5. 종합 리스크 평가:
   - 주요 리스크 요인별 영향도 분석
   - 시나리오별 리스크 시뮬레이션
   - 리스크 대응 전략 제시

**출력 형식:**
- 재무 리스크: [부채 및 유동성 리스크 평가]
- 사업 리스크: [경쟁 및 시장 리스크 분석]
- 시장 리스크: [주가 변동성 및 베타 분석]
- ESG 리스크: [환경, 사회, 지배구조 리스크]
- 종합 평가: [전체 리스크 수준과 대응 방안]
- 투자 권고: [리스크 대비 수익률 평가]

정량적 근거를 바탕으로 명확한 리스크 평가를 제시하세요.
""",
            )

            # 단일 Chain 생성
            risk_chain = risk_analysis_prompt | llm

            print(f"✅ {analyst.name} LangChain Chain 생성 완료!")
            return risk_chain

        except Exception as e:
            print(f"❌ {analyst.name} LangChain Chain 생성 실패: {e}")
            return None

    def _create_industry_analysis_chain(
        self, analyst: AnalystAgent, sector_name: str
    ) -> Any:
        """
        산업 전문가를 위한 LangChain Chain 생성

        Args:
            analyst: 분석가 객체
            sector_name: 섹터 이름

        Returns:
            Chain: 단일 단계 분석 Chain
        """
        try:
            # LLM 모델 설정 (OpenAI GPT-4o)
            llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0.1,  # 분석의 일관성을 위해 낮은 값
                max_tokens=4000,
            )

            # 단일 단계: 종합 산업 분석 프롬프트
            industry_analysis_prompt = PromptTemplate(
                input_variables=["financial_data", "sector_name", "company_name"],
                template="""
당신은 {sector_name} 섹터 전문 산업 전문가입니다.

**종합 산업 분석**

제공된 재무데이터를 바탕으로 종합적인 산업 분석을 수행하세요:

**입력 데이터:**
{financial_data}

**회사명:** {company_name}

**분석 요구사항:**
1. 산업 구조 분석:
   - 산업의 성숙도와 성장 단계 평가
   - 시장 규모와 성장률 분석
   - 진입장벽과 경쟁 강도 평가

2. 시장 동향 및 성장성 분석:
   - 주요 성장 동력과 트렌드 분석
   - 기술 혁신과 디지털 전환 영향
   - 규제 환경 변화와 정책 영향

3. 경쟁사 분석:
   - 주요 경쟁사 시장점유율 분석
   - 경쟁 우위 요인과 차별화 전략
   - 신규 진입자와 대체재 위협

4. 규제 및 정책 환경 분석:
   - 관련 법규와 규제 동향
   - 정부 정책과 지원 방안
   - ESG 규제와 준수 현황

5. 산업 전망 및 기회/위험 분석:
   - 단기/중장기 산업 전망
   - 주요 기회 요인과 위험 요소
   - 투자 전략적 시사점

**출력 형식:**
- 산업 구조: [성숙도, 규모, 경쟁 강도 분석]
- 시장 동향: [성장 동력과 트렌드 분석]
- 경쟁 환경: [경쟁사와 시장점유율 분석]
- 규제 환경: [법규와 정책 영향 분석]
- 산업 전망: [기회와 위험 요소 분석]
- 투자 시사점: [산업 관점에서의 투자 권고]

정량적 근거를 바탕으로 명확한 산업 분석을 제시하세요.
""",
            )

            # 단일 Chain 생성
            industry_chain = industry_analysis_prompt | llm

            print(f"✅ {analyst.name} LangChain Chain 생성 완료!")
            return industry_chain

        except Exception as e:
            print(f"❌ {analyst.name} LangChain Chain 생성 실패: {e}")
            return None

    def _create_technical_analysis_chain(
        self, analyst: AnalystAgent, sector_name: str
    ) -> Any:
        """
        기술적 분석가를 위한 LangChain Chain 생성

        Args:
            analyst: 분석가 객체
            sector_name: 섹터 이름

        Returns:
            Chain: 단일 단계 분석 Chain
        """
        try:
            # LLM 모델 설정 (OpenAI GPT-4o)
            llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0.1,  # 분석의 일관성을 위해 낮은 값
                max_tokens=4000,
            )

            # 단일 단계: 종합 기술적 분석 프롬프트
            technical_analysis_prompt = PromptTemplate(
                input_variables=["price_data", "sector_name", "company_name"],
                template="""
당신은 {sector_name} 섹터 전문 기술적 분석가입니다.

**종합 기술적 분석**

제공된 가격 데이터를 바탕으로 종합적인 기술적 분석을 수행하세요:

**입력 데이터:**
{price_data}

**회사명:** {company_name}

**분석 요구사항:**
1. 차트 패턴 분석:
   - 주요 차트 패턴 식별 (헤드앤숄더, 더블탑/바텀 등)
   - 추세선과 채널 분석
   - 지지선과 저항선 레벨 분석

2. 기술적 지표 분석:
   - 이동평균선 분석 (20일, 60일, 200일)
   - RSI, MACD, 스토캐스틱 등 오실레이터 분석
   - 볼린저 밴드와 피벗 포인트 분석

3. 거래량 분석:
   - 거래량 추세와 가격 변동의 관계
   - 거래량 가중 평균가격(VWAP) 분석
   - 거래량 프로파일 분석

4. 섹터 상대강도 분석:
   - 섹터 대비 상대적 성과 분석
   - 섹터 내 순위와 강도 평가
   - 섹터 로테이션 영향 분석

5. 기술적 전망 및 투자 권고:
   - 단기/중기 기술적 전망
   - 주요 지지/저항 레벨과 목표가
   - 매수/매도 시점 권고

**출력 형식:**
- 차트 패턴: [주요 패턴과 의미 분석]
- 기술적 지표: [주요 지표별 신호 분석]
- 거래량 분석: [거래량과 가격 관계 분석]
- 섹터 비교: [섹터 대비 상대적 성과]
- 기술적 전망: [단기/중기 전망과 목표가]
- 투자 권고: [매수/매도 시점과 근거]

정량적 근거를 바탕으로 명확한 기술적 분석을 제시하세요.
""",
            )

            # 단일 Chain 생성
            technical_chain = technical_analysis_prompt | llm

            print(f"✅ {analyst.name} LangChain Chain 생성 완료!")
            return technical_chain

        except Exception as e:
            print(f"❌ {analyst.name} LangChain Chain 생성 실패: {e}")
            return None

    def _create_footnote_analysis_chain(
        self, analyst: AnalystAgent, sector_name: str
    ) -> Any:
        """
        주석 전문가를 위한 LangChain Chain 생성

        Args:
            analyst: 분석가 객체
            sector_name: 섹터 이름

        Returns:
            Chain: 단일 단계 분석 Chain
        """
        try:
            # LLM 모델 설정 (OpenAI GPT-4o)
            llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0.1,  # 분석의 일관성을 위해 낮은 값
                max_tokens=4000,
            )

            # 단일 단계: 종합 주석 분석 프롬프트
            footnote_analysis_prompt = PromptTemplate(
                input_variables=["financial_data", "sector_name", "company_name"],
                template="""
당신은 {sector_name} 섹터 전문 재무제표 주석 분석가입니다.

**종합 재무제표 주석 분석**

제공된 재무제표 주석 데이터를 바탕으로 종합적인 주석 분석을 수행하세요:

**입력 데이터:**
{financial_data}

**회사명:** {company_name}

**분석 요구사항:**
1. 재무상태표 주석 분석:
   - 자산 분류 및 평가 방법 분석
   - 부채 구조와 만기 분석
   - 자본 구성과 이익잉여금 분석

2. 손익계산서 주석 분석:
   - 매출 인식 기준과 방법 분석
   - 비용 분류와 처리 방법 분석
   - 특별손익과 지속사업손익 분석

3. 현금흐름표 주석 분석:
   - 영업활동 현금흐름 분석
   - 투자활동 현금흐름 분석
   - 재무활동 현금흐름 분석

4. 우발채무 및 보증채무 분석:
   - 우발채무 규모와 성격 분석
   - 보증채무 현황과 리스크 분석
   - 잠재적 부채 노출도 평가

5. 회계정책 및 추정사항 분석:
   - 주요 회계정책 변경 영향 분석
   - 추정사항의 불확실성 분석
   - 감사의견과 관련 이슈 분석

**출력 형식:**
- 재무상태표 주석: [자산, 부채, 자본 분석]
- 손익계산서 주석: [매출, 비용, 손익 분석]
- 현금흐름표 주석: [현금흐름 구조 분석]
- 우발채무 분석: [잠재적 부채 리스크]
- 회계정책 분석: [정책 변경과 추정사항]
- 종합 평가: [주석 관점에서의 재무상태 평가]

정량적 근거를 바탕으로 명확한 주석 분석을 제시하세요.
""",
            )

            # 단일 Chain 생성
            footnote_chain = footnote_analysis_prompt | llm

            print(f"✅ {analyst.name} LangChain Chain 생성 완료!")
            return footnote_chain

        except Exception as e:
            print(f"❌ {analyst.name} LangChain Chain 생성 실패: {e}")
            return None
