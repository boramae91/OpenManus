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

        # 1. 펀더멘털 분석가 (섹터 특화) - 🎯 시니어 애널리스트 수준 업그레이드
        fundamental_analyst = AnalystAgent(
            name=f"{sector_korean_name} 펀더멘털 분석가",
            role="Fundamental Analyst",
            expertise="재무제표 분석, 기업가치 평가, 수익성 분석",
            analysis_focus=f"{sector_korean_name} 섹터의 재무 건전성과 성장성 분석",
            key_methods=[
                "손익계산서 분석 (매출성장률, 영업이익률, 순이익률 트렌드 분석)",
                "대차대조표 분석 (부채비율, 유동비율, 자기자본비율 정량평가)",
                "현금흐름표 분석 (영업CF, 투자CF, 재무CF 3년 평균 분석)",
                "ROE/ROA 분석 (DuPont 3단계 분해분석 수행)",
                "수익성 분석 (ROIC, EBITDA마진, FCF마진 동종업계 대비)",
                "재무비율 종합분석 (안전성, 수익성, 성장성, 활동성 4대 영역)",
                "Working Capital 분석 (운전자본 효율성 및 Cash Cycle 산출)",
                "Capital Structure 분석 (최적자본구조 대비 현재 레버리지 평가)",
            ],
            sector_context=f"{sector_korean_name} 섹터 전문 펀더멘털 분석가로서 섹터 특성을 반영한 재무 분석을 수행",
            sector_specific_points=(
                analysis_points_list[:3]
                if len(analysis_points_list) >= 3
                else analysis_points_list
            )
            + [
                "⭐ 펀더멘털 분석 시 반드시 다음을 포함:",
                "1. 재무비율 3년 트렌드 분석과 동종업계 Percentile 순위",
                "2. DuPont 분해를 통한 ROE 동력 분석 (순이익률×자산회전율×레버리지)",
                "3. Free Cash Flow 산출 및 FCF Yield 계산식 명시",
                "4. Working Capital 변동이 영업현금흐름에 미치는 영향 정량화",
                "5. 부채상환능력 지표 (Interest Coverage, Debt Service Coverage) 산출",
                "6. 배당정책 지속가능성 분석 (Payout Ratio, Dividend Coverage)",
                "7. 계절성/경기민감성이 재무성과에 미치는 영향도 평가",
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
                "⭐ 목표가 산출 시 반드시 다음을 포함:",
                "1. DCF 기반 내재가치 계산식과 전제조건 명시",
                "2. PER/PBR 멀티플 근거와 업계 비교 데이터",
                "3. 각 밸류에이션 방법론별 가중평균 산출 과정",
                "4. 목표가 도출을 위한 구체적 수치와 근거",
                "5. 시나리오별 목표가 range와 확률 배정",
                "6. 투자의견(매수/보유/매도) 판단 기준 설명",
            ],
            risk_awareness=[f"밸류에이션 관점에서 {risk_factors}"],
            critical_metrics=[
                metric
                for metric in critical_metrics_list
                if any(word in metric for word in ["비율", "수익률", "마진", "배수"])
            ],
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
                "1. 정량적 리스크 지표 산출 (VaR, CVaR, Maximum Drawdown, Sharpe Ratio)",
                "2. 3시나리오 분석과 각 시나리오별 발생 확률 및 목표가 Impact",
                "3. 주요 리스크 팩터별 민감도 계수와 탄력성 측정",
                "4. 스트레스 테스트 결과 (글로벌 금융위기급 충격시 예상 손실률)",
                "5. ESG 리스크 스코어와 ESG 이슈 발생시 주가 하락 폭 예측",
                "6. 신용도 분석 (Altman Z-Score, 부도 확률, Credit Spread 변화)",
                "7. 유동성 리스크 (일평균 거래대금 대비 대량 매도시 충격도)",
                "8. 섹터 특화 리스크 (규제, 기술, 원자재, 환율 등) 정량 측정",
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
