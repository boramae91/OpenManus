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

    GICS 섹터별 특화된 분석 포인트와 위험 요소를 반영한 전문가에요!
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

        # 1. 펀더멘털 분석가 (섹터 특화)
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
            sector_context=f"{sector_korean_name} 섹터 전문 펀더멘털 분석가로서 섹터 특성을 반영한 재무 분석을 수행",
            sector_specific_points=(
                analysis_points_list[:3]
                if len(analysis_points_list) >= 3
                else analysis_points_list
            ),
            risk_awareness=[f"재무적 관점에서 {risk_factors}"],
            critical_metrics=(
                critical_metrics_list[:4]
                if len(critical_metrics_list) >= 4
                else critical_metrics_list
            ),
        )
        experts.append(fundamental_analyst)

        # 2. 기술적 분석가 (섹터 특화)
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
            sector_context=f"{sector_korean_name} 섹터의 경기민감성과 변동성을 고려한 기술적 분석 전문가",
            sector_specific_points=[
                f"기술적 관점에서 {sector_context.get('cyclical_nature', '섹터 특성')} 반영"
            ],
            risk_awareness=[f"기술적 분석 관점에서 {risk_factors}"],
            critical_metrics=["상대강도", "섹터 모멘텀", "거래량 패턴", "변동성 지표"],
        )
        experts.append(technical_analyst)

        # 3. 산업 전문가 (섹터 특화)
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
            sector_context=f"{sector_korean_name} 섹터의 산업 구조와 경쟁 환경을 심도 있게 분석하는 전문가",
            sector_specific_points=analysis_points_list,
            risk_awareness=[f"산업 구조적 관점에서 {risk_factors}"],
            critical_metrics=[
                metric
                for metric in critical_metrics_list
                if any(word in metric for word in ["점유율", "성장률", "경쟁", "시장"])
            ],
        )
        experts.append(industry_expert)

        # 4. 밸류에이션 전문가 (섹터 특화)
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
            sector_context=f"{sector_korean_name} 섹터 특성을 반영한 맞춤형 밸류에이션 방법론을 적용하는 전문가",
            sector_specific_points=[
                f"밸류에이션 관점에서 {sector_context.get('valuation_approach', '가치평가 방법')}"
            ],
            risk_awareness=[f"밸류에이션 관점에서 {risk_factors}"],
            critical_metrics=[
                metric
                for metric in critical_metrics_list
                if any(word in metric for word in ["비율", "수익률", "마진", "배수"])
            ],
        )
        experts.append(valuation_specialist)

        # 5. 리스크 평가자 (섹터 특화)
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
            sector_context=f"{sector_korean_name} 섹터 고유의 리스크 요인과 함정을 전문적으로 분석하는 리스크 전문가",
            sector_specific_points=[f"리스크 관점에서 {analysis_points}"],
            risk_awareness=risk_factors_list,
            critical_metrics=[
                f"리스크 지표: {metric}"
                for metric in critical_metrics_list
                if any(word in metric for word in ["비율", "위험", "변동성", "안전"])
            ],
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
