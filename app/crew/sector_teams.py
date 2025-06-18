# -*- coding: utf-8 -*-
"""
섹터별 전문 분석팀 팩토리 시스템

11개 GICS 섹터별로 5명의 전문가 에이전트를 정의해요
각 섹터마다 맞춤형 분석 전문가들이 있어요!
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .gics_sectors import GICSSector, GICSSectorManager


@dataclass
class AnalystAgent:
    """
    개별 분석가 에이전트 정의
    각 에이전트는 고유한 전문 분야와 역할을 가져요
    """

    name: str  # 에이전트 이름
    role: str  # 역할 (펀더멘털 분석가, 기술적 분석가 등)
    expertise: str  # 전문 분야
    analysis_focus: str  # 분석 초점
    key_methods: List[str]  # 주요 분석 방법론
    sector_context: str  # 섹터별 특화 컨텍스트


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

        Args:
            sector: GICS 섹터

        Returns:
            SectorTeam: 생성된 섹터팀
        """
        sector_context = self.sector_manager.get_sector_context(sector)
        sector_korean_name = self.sector_manager.get_sector_korean_name(sector)

        # 섹터별 5명의 전문가 생성
        experts = []

        # 1. 펀더멘털 분석가
        fundamental_analyst = AnalystAgent(
            name=f"{sector_korean_name} 펀더멘털 분석가",
            role="Fundamental Analyst",
            expertise="재무제표 분석, 기업가치 평가, 수익성 분석",
            analysis_focus=f"{sector_korean_name} 섹터의 재무 건전성과 성장성 분석",
            key_methods=[
                "손익계산서 분석",
                "대차대조표 분석",
                "현금흐름표 분석",
                "ROE/ROA 분석",
                "부채비율 분석",
                "수익성 분석",
            ],
            sector_context=f"{sector_korean_name} 섹터 전문 펀더멘털 분석가",
        )
        experts.append(fundamental_analyst)

        # 2. 기술적 분석가
        technical_analyst = AnalystAgent(
            name=f"{sector_korean_name} 기술적 분석가",
            role="Technical Analyst",
            expertise="차트 패턴 분석, 기술적 지표 해석, 시장 심리 분석",
            analysis_focus=f"{sector_korean_name} 섹터의 가격 움직임과 매매 신호 분석",
            key_methods=[
                "이동평균선 분석",
                "MACD/RSI 분석",
                "볼린저 밴드 분석",
                "지지저항선 분석",
                "거래량 분석",
                "섹터 로테이션 분석",
            ],
            sector_context=f"{sector_korean_name} 섹터 전문 기술적 분석가",
        )
        experts.append(technical_analyst)

        # 3. 산업 전문가
        industry_expert = AnalystAgent(
            name=f"{sector_korean_name} 산업 전문가",
            role="Industry Expert",
            expertise="산업 분석, 경쟁 구조 분석, 트렌드 예측",
            analysis_focus=f"{sector_korean_name} 산업의 구조적 변화와 성장 동력 분석",
            key_methods=[
                "Porter 5 Forces 분석",
                "밸류체인 분석",
                "SWOT 분석",
                "경쟁사 벤치마킹",
                "시장점유율 분석",
                "기술 동향 분석",
            ],
            sector_context=f"{sector_korean_name} 섹터 전문 산업 분석가",
        )
        experts.append(industry_expert)

        # 4. 밸류에이션 전문가
        valuation_specialist = AnalystAgent(
            name=f"{sector_korean_name} 밸류에이션 전문가",
            role="Valuation Specialist",
            expertise="기업가치 평가, 적정주가 산정, 투자지표 분석",
            analysis_focus=f"{sector_korean_name} 기업의 내재가치와 투자 매력도 평가",
            key_methods=[
                "DCF 모델링",
                "PER/PBR 분석",
                "EV/EBITDA 분석",
                "Sum-of-Parts 분석",
                "배당수익률 분석",
                "상대가치 평가",
            ],
            sector_context=f"{sector_korean_name} 섹터 전문 밸류에이션 전문가",
        )
        experts.append(valuation_specialist)

        # 5. 리스크 평가자
        risk_assessor = AnalystAgent(
            name=f"{sector_korean_name} 리스크 평가자",
            role="Risk Assessor",
            expertise="위험 요소 분석, 시나리오 분석, 리스크 관리",
            analysis_focus=f"{sector_korean_name} 투자의 주요 리스크와 대응 전략 분석",
            key_methods=[
                "시나리오 분석",
                "민감도 분석",
                "VaR 분석",
                "스트레스 테스트",
                "ESG 리스크 분석",
                "규제 리스크 분석",
            ],
            sector_context=f"{sector_korean_name} 섹터 전문 리스크 분석가",
        )
        experts.append(risk_assessor)

        # 섹터팀 생성
        team = SectorTeam(
            sector=sector,
            team_name=f"{sector_korean_name} 섹터 전문 분석팀",
            team_description=f"{sector_korean_name} 섹터의 종합적인 투자 분석을 수행하는 5명의 전문가팀",
            experts=experts,
            collaboration_strategy=f"{sector_korean_name} 섹터 특성을 반영한 협업 분석",
            report_structure={
                "fundamental": "재무 분석 보고서",
                "technical": "기술적 분석 보고서",
                "industry": "산업 분석 보고서",
                "valuation": "밸류에이션 보고서",
                "risk": "리스크 평가 보고서",
            },
        )

        print(f"✅ {sector_korean_name} 섹터팀 생성 완료 (전문가 {len(experts)}명)")
        return team
