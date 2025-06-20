# -*- coding: utf-8 -*-
"""
GICS 섹터 정의 및 관리 시스템

11개 GICS 섹터와 각 섹터별 전문 지식을 정의해요
각 섹터마다 고유한 분석 관점과 평가 방법론을 가지고 있어요!
"""

from enum import Enum
from typing import Dict, List, Optional

import pandas as pd


class GICSSector(Enum):
    """
    GICS(Global Industry Classification Standard) 11개 섹터 정의
    각 섹터는 고유한 코드번호를 가지고 있어요
    """

    ENERGY = "10"  # 에너지
    MATERIALS = "15"  # 소재
    INDUSTRIALS = "20"  # 산업재
    CONSUMER_DISCRETIONARY = "25"  # 임의소비재
    CONSUMER_STAPLES = "30"  # 필수소비재
    HEALTH_CARE = "35"  # 헬스케어
    FINANCIALS = "40"  # 금융
    INFORMATION_TECHNOLOGY = "45"  # 정보기술
    COMMUNICATION_SERVICES = "50"  # 커뮤니케이션서비스
    UTILITIES = "55"  # 유틸리티
    REAL_ESTATE = "60"  # 부동산


class GICSSectorManager:
    """
    GICS 섹터 관리 및 매핑 시스템

    주요 기능:
    1. 종목명/코드로 GICS 섹터 감지
    2. 섹터별 전문 컨텍스트 제공
    3. 섹터별 핵심 분석 지표 관리
    4. One-Hot Sector Activation을 위한 섹터 정보 제공
    """

    def __init__(self, stock_mapping_table: Optional[Dict[str, pd.DataFrame]] = None):
        """
        GICS 섹터 매니저 초기화

        Args:
            stock_mapping_table: ticker_bbg 매핑 테이블 (CSV 데이터)
        """
        self.stock_mapping_table = stock_mapping_table

        # 📊 섹터별 전문 컨텍스트 정의
        self.sector_contexts = self._initialize_sector_contexts()

        # 🎯 섹터별 핵심 분석 지표 정의
        self.sector_key_metrics = self._initialize_sector_metrics()

        # 🏢 한국 주요 기업들의 섹터 매핑 (수동 정의)
        self.korean_sector_mapping = self._initialize_korean_sector_mapping()

        print("🏢 GICS 섹터 매니저 초기화 완료!")

    def detect_sector_from_stock(
        self, stock_name: str, stock_code: str = None
    ) -> GICSSector:
        """
        종목명/코드로 GICS 섹터를 감지해요

        우선순위:
        1. 한국 주요 기업 수동 매핑
        2. Bloomberg 데이터셋 매핑 (있다면)
        3. 종목명 키워드 기반 추론

        Args:
            stock_name: 종목명
            stock_code: 종목코드 (선택사항)

        Returns:
            GICSSector: 감지된 GICS 섹터
        """
        print(f"🔍 GICS 섹터 감지 시작: {stock_name} ({stock_code})")

        # 1. 한국 주요 기업 수동 매핑 확인
        if stock_name:
            for company_name, sector in self.korean_sector_mapping.items():
                if company_name in stock_name or stock_name in company_name:
                    print(f"✅ 한국 기업 매핑 성공: {stock_name} → {sector.name}")
                    return sector

        if stock_code:
            for code, sector in self.korean_sector_mapping.items():
                if code == stock_code:
                    print(f"✅ 종목코드 매핑 성공: {stock_code} → {sector.name}")
                    return sector

        # 2. Bloomberg 데이터셋 매핑 시도 (구현 예정)
        # TODO: CSV 데이터에서 GICS 섹터 정보 추출

        # 3. 종목명 키워드 기반 추론
        sector = self._infer_sector_from_keywords(stock_name)
        print(f"🎯 키워드 기반 추론: {stock_name} → {sector.name}")

        return sector

    def get_sector_context(self, sector: GICSSector) -> Dict[str, str]:
        """
        특정 섹터의 전문 컨텍스트를 가져와요
        각 섹터의 특성과 분석 관점을 제공해요!

        Args:
            sector: GICS 섹터

        Returns:
            Dict: 섹터별 전문 컨텍스트 정보
        """
        return self.sector_contexts.get(sector, {})

    def get_sector_analysis_points(self, sector: GICSSector) -> str:
        """
        특정 섹터의 중점 분석 포인트를 가져와요
        투자 분석 시 반드시 확인해야 할 핵심 요소들이에요!

        Args:
            sector: GICS 섹터

        Returns:
            str: 섹터별 중점 분석 포인트
        """
        context = self.sector_contexts.get(sector, {})
        return context.get("key_analysis_points", "중점 분석 포인트 정보가 없습니다.")

    def get_sector_risk_factors(self, sector: GICSSector) -> str:
        """
        특정 섹터의 주요 위험 요소를 가져와요
        분석할 때 주의해서 봐야 할 함정들이에요!

        Args:
            sector: GICS 섹터

        Returns:
            str: 섹터별 주요 위험 요소
        """
        context = self.sector_contexts.get(sector, {})
        return context.get("key_risks", "주요 위험 요소 정보가 없습니다.")

    def get_sector_critical_metrics(self, sector: GICSSector) -> str:
        """
        특정 섹터의 핵심 지표를 가져와요
        이 지표들을 통해 기업의 경쟁력을 평가할 수 있어요!

        Args:
            sector: GICS 섹터

        Returns:
            str: 섹터별 핵심 지표
        """
        context = self.sector_contexts.get(sector, {})
        return context.get("critical_metrics", "핵심 지표 정보가 없습니다.")

    def get_sector_key_metrics(self, sector: GICSSector) -> List[str]:
        """
        특정 섹터의 핵심 분석 지표를 가져와요
        각 섹터마다 중요하게 봐야 할 지표들이 다르거든요!

        Args:
            sector: GICS 섹터

        Returns:
            List[str]: 섹터별 핵심 지표 목록
        """
        return self.sector_key_metrics.get(sector, [])

    def get_all_sectors(self) -> List[GICSSector]:
        """
        모든 GICS 섹터 목록을 가져와요

        Returns:
            List[GICSSector]: 전체 섹터 목록
        """
        return list(GICSSector)

    def get_sector_korean_name(self, sector: GICSSector) -> str:
        """
        섹터의 한국어 이름을 가져와요

        Args:
            sector: GICS 섹터

        Returns:
            str: 섹터 한국어 이름
        """
        korean_names = {
            GICSSector.ENERGY: "에너지",
            GICSSector.MATERIALS: "소재",
            GICSSector.INDUSTRIALS: "산업재",
            GICSSector.CONSUMER_DISCRETIONARY: "임의소비재",
            GICSSector.CONSUMER_STAPLES: "필수소비재",
            GICSSector.HEALTH_CARE: "헬스케어",
            GICSSector.FINANCIALS: "금융",
            GICSSector.INFORMATION_TECHNOLOGY: "정보기술",
            GICSSector.COMMUNICATION_SERVICES: "커뮤니케이션서비스",
            GICSSector.UTILITIES: "유틸리티",
            GICSSector.REAL_ESTATE: "부동산",
        }
        return korean_names.get(sector, sector.name)

    def get_comprehensive_sector_guide(self, sector: GICSSector) -> Dict[str, str]:
        """
        특정 섹터의 종합 분석 가이드를 제공해요
        중점 분석 포인트, 위험 요소, 핵심 지표를 모두 포함한 완전한 가이드에요!

        Args:
            sector: GICS 섹터

        Returns:
            Dict: 섹터별 종합 분석 가이드
        """
        korean_name = self.get_sector_korean_name(sector)
        context = self.sector_contexts.get(sector, {})

        return {
            "sector_name": korean_name,
            "sector_code": sector.value,
            "industry_focus": context.get("industry_focus", "업종 정보 없음"),
            "key_analysis_points": context.get(
                "key_analysis_points", "중점 분석 포인트 정보 없음"
            ),
            "key_risks": context.get("key_risks", "주요 위험 요소 정보 없음"),
            "valuation_approach": context.get(
                "valuation_approach", "밸류에이션 방법 정보 없음"
            ),
            "cyclical_nature": context.get("cyclical_nature", "경기 민감성 정보 없음"),
            "critical_metrics": context.get("critical_metrics", "핵심 지표 정보 없음"),
        }

    def print_sector_analysis_guide(self, sector: GICSSector) -> None:
        """
        특정 섹터의 분석 가이드를 보기 좋게 출력해요
        실제 분석 작업 시 참고용으로 활용하세요!

        Args:
            sector: GICS 섹터
        """
        guide = self.get_comprehensive_sector_guide(sector)

        print(
            f"\n🏢 【{guide['sector_name']} 섹터 ({guide['sector_code']})】 분석 가이드"
        )
        print("=" * 60)

        print(f"\n📋 주요 업종:")
        print(f"   {guide['industry_focus']}")

        print(f"\n🎯 중점 분석 포인트:")
        print(f"   {guide['key_analysis_points']}")

        print(f"\n⚠️  주의할 위험 요소:")
        print(f"   {guide['key_risks']}")

        print(f"\n💰 밸류에이션 방법:")
        print(f"   {guide['valuation_approach']}")

        print(f"\n📊 경기 민감성:")
        print(f"   {guide['cyclical_nature']}")

        print(f"\n📈 핵심 체크 지표:")
        print(f"   {guide['critical_metrics']}")

        print("=" * 60)

    def _initialize_sector_contexts(self) -> Dict[GICSSector, Dict[str, str]]:
        """
        섹터별 전문 컨텍스트를 초기화해요
        각 섹터의 특성과 분석 관점을 정의해요!

        각 섹터별로 중점 분석 포인트와 주의할 점을 상세히 제공해요
        이 정보는 실제 투자 분석에서 놓치기 쉬운 부분들을 포함하고 있어요!
        """
        return {
            GICSSector.ENERGY: {
                "industry_focus": "석유, 가스, 신재생에너지, 에너지 장비 및 서비스",
                "key_analysis_points": "유가 및 가스 가격 민감도, 원가 구조(생산단가 vs 판매단가), 자원 매장량 및 수명, Capex(탐사/시추/인프라 투자), ESG 요인(탄소배출, 규제 리스크)",
                "key_risks": "유가 상승 시 이익 급증으로 인한 일시적 착시 가능성, 자원 고갈 또는 탈탄소 정책 변화에 따른 구조적 리스크",
                "valuation_approach": "자산 기반 평가, DCF, 유가 시나리오 분석, 매장량 기반 평가",
                "cyclical_nature": "고도의 경기순환성, 유가 민감성, 에너지 정책 변화에 따른 구조적 변화",
                "critical_metrics": "유가 민감도 분석, 생산단가 대비 판매단가 스프레드, 매장량 대비 생산량, 탄소 배출량 및 ESG 등급",
            },
            GICSSector.MATERIALS: {
                "industry_focus": "화학, 건설자재, 용기포장재, 금속광업, 제지임산",
                "key_analysis_points": "제품 가격 vs 원재료 가격 스프레드, 재고자산 및 가격 변동성, 사이클 민감도(경기민감 업종), 생산설비/원가구조 분석",
                "key_risks": "원자재 가격 하락기에 실적 급감 가능성, 환경 규제 강화에 따른 비용 상승 가능성",
                "valuation_approach": "P/B, EV/EBITDA, 원자재 가격 기반 평가, 사이클 조정 밸류에이션",
                "cyclical_nature": "강한 경기순환성, 수요 변동성, 중국 경기와 높은 연관성",
                "critical_metrics": "원자재 가격 연동성, 제품-원료 가격 스프레드, 재고자산 회전율, 환경 투자비용 및 재활용률",
            },
            GICSSector.INDUSTRIALS: {
                "industry_focus": "자본재, 상업서비스, 운송, 항공우주국방",
                "key_analysis_points": "수주잔고(Backlog) 및 수주 트렌드, 고객 다변화 여부, 운영 레버리지, 글로벌 공급망 의존도",
                "key_risks": "단기 실적 변동에 대한 과잉 해석 위험, 공공 프로젝트 중심 기업의 정치 리스크",
                "valuation_approach": "P/E, EV/EBITDA, 주문잔고 분석, 장기 계약 가치 평가",
                "cyclical_nature": "중간 수준의 경기순환성, 설비투자 사이클과 연관성",
                "critical_metrics": "수주잔고 변화율, 매출 가시성, 고객 집중도, 운영 레버리지 및 자유현금흐름",
            },
            GICSSector.CONSUMER_DISCRETIONARY: {
                "industry_focus": "자동차, 가전, 의류, 호텔레스토랑, 미디어엔터테인먼트",
                "key_analysis_points": "소비자 트렌드(브랜드력, 시장점유율), 매출성장률과 이익률 추이, e-Commerce 대응 전략, 원가 인상 시 가격전가 능력",
                "key_risks": "일시적 유행(패션, 전자기기 등)의 매출 과대평가, 소비 위축기 수요 급감 가능성",
                "valuation_approach": "P/E, P/S, 브랜드 가치 평가, 동일매장 매출성장률 기반 평가",
                "cyclical_nature": "높은 경기 민감성, 소비자 심리와 가처분소득에 의존",
                "critical_metrics": "동일매장 매출성장률, 브랜드 가치 및 시장점유율, 재고회전율, 소비자 충성도",
            },
            GICSSector.CONSUMER_STAPLES: {
                "industry_focus": "식음료, 생활용품, 소매업체, 담배",
                "key_analysis_points": "안정적인 수요 기반 확인, 마진 유지력(원가 상승 전가력), 유통 채널과 점유율, 브랜드 충성도",
                "key_risks": "방어주로 과대평가되는 경우 존재, 인플레이션 시 원가부담 증가 리스크",
                "valuation_approach": "P/E, 배당수익률, 브랜드 프리미엄, 안정성 기반 평가",
                "cyclical_nature": "낮은 경기 민감성, 방어적 특성, 인플레이션 헤지 능력",
                "critical_metrics": "매출 안정성, 마진 방어력, 브랜드 충성도, 유통망 강도 및 원자재 헤지 비율",
            },
            GICSSector.HEALTH_CARE: {
                "industry_focus": "제약, 바이오테크, 의료기기, 헬스케어 서비스",
                "key_analysis_points": "파이프라인(신약개발 단계), FDA 승인 및 특허만료 이슈, 보험 수가 및 정부 규제 정책, R&D 비중 및 성공률",
                "key_risks": "신약 승인 실패 시 가치 급락 가능성, 특허만료로 인한 제네릭 약물 위협",
                "valuation_approach": "DCF, rNPV(위험조정순현재가치), 파이프라인 가치 평가",
                "cyclical_nature": "낮은 경기 민감성, 방어적 특성, 고령화 수혜",
                "critical_metrics": "신약 파이프라인 단계별 분석, 특허 만료일정, 임상시험 성공률, FDA 승인 현황",
            },
            GICSSector.FINANCIALS: {
                "industry_focus": "은행, 증권, 보험, 부동산금융",
                "key_analysis_points": "이자이익(NIM)과 비이자이익 구분, 자산건전성(NPL, 대손충당금), 자본비율(BIS), 금리 민감도 및 레버리지 수준",
                "key_risks": "장단기 금리 역전 시 수익성 악화, 부실자산 증가 시 급격한 손실 가능성",
                "valuation_approach": "P/B, ROE, 순이자마진 분석, 자산건전성 기반 평가",
                "cyclical_nature": "강한 경기순환성, 금리 민감성, 신용 사이클과 밀접한 관련",
                "critical_metrics": "순이자마진(NIM), 비이자수익, 신용비용률, BIS 비율, 대손충당금 적정성",
            },
            GICSSector.INFORMATION_TECHNOLOGY: {
                "industry_focus": "소프트웨어, 반도체, IT서비스, 전자장비",
                "key_analysis_points": "기술력(특허, 플랫폼 점유율), 매출성장률/고객 락인효과, R&D 투자 vs 수익화 성공률, 경쟁 환경 및 M&A 전략",
                "key_risks": "과도한 밸류에이션으로 인한 조정 위험, 기술 변화(디스럽션) 리스크에 취약",
                "valuation_approach": "P/E, P/S, EV/Sales, 성장률 기반 평가, 플랫폼 가치 평가",
                "cyclical_nature": "기술 사이클, 반도체 업황, 디지털 전환 수요",
                "critical_metrics": "매출 성장률, 기술 혁신력, 시장점유율, 클라우드 전환율, AI 역량",
            },
            GICSSector.COMMUNICATION_SERVICES: {
                "industry_focus": "통신서비스, 미디어엔터테인먼트, 인터랙티브미디어",
                "key_analysis_points": "가입자 수 및 ARPU(가입자당 매출), 콘텐츠 경쟁력(미디어/플랫폼), CAPEX(5G, 광케이블 등 인프라 투자), 규제 및 주파수 정책",
                "key_risks": "설비투자 과다로 인한 현금흐름 악화, OTT/미디어 경쟁 심화로 수익성 저하 가능성",
                "valuation_approach": "EV/EBITDA, P/E, 구독자 기반 평가, 콘텐츠 가치 평가",
                "cyclical_nature": "중간 수준의 경기 민감성, 기술 전환 사이클",
                "critical_metrics": "구독자 수 및 ARPU, 콘텐츠 투자 대비 수익률, 5G 인프라 구축 현황, 시장점유율",
            },
            GICSSector.UTILITIES: {
                "industry_focus": "전력, 가스, 수도, 신재생에너지",
                "key_analysis_points": "고정 수익 기반(요금제 구조), 규제 기관의 요금 인가 정책, 장기 투자 계획(발전소, 인프라), 배당 안정성",
                "key_risks": "금리 상승 시 가치 하락 위험(채권 대체성), 친환경/신재생 전환 비용 부담",
                "valuation_approach": "배당수익률, P/B, 규제자산 기준 평가, 현금흐름 할인법",
                "cyclical_nature": "매우 낮은 경기 민감성, 금리 민감성, 규제 환경 의존",
                "critical_metrics": "전력 판매량, 요금 인상률, 신재생 에너지 비율, 규제 자산 가치, 배당 지속성",
            },
            GICSSector.REAL_ESTATE: {
                "industry_focus": "부동산투자신탁, 부동산관리개발",
                "key_analysis_points": "자산가치(보유 부동산 NAV), 임대 수익률 및 공실률, 이자비용 및 LTV, 섹터별 포트폴리오(오피스, 리테일, 물류 등)",
                "key_risks": "금리 변화에 따른 민감도가 매우 높음, 상업용 부동산의 구조적 수요 감소 가능성(리테일, 오피스 등)",
                "valuation_approach": "P/B, 배당수익률, NAV 기준 평가, 부동산 가치 평가",
                "cyclical_nature": "강한 금리 민감성, 부동산 시장 사이클",
                "critical_metrics": "임대료 상승률, 공실률, NOI 마진, NAV 할인율, LTV 및 이자보상배율",
            },
        }

    def _initialize_sector_metrics(self) -> Dict[GICSSector, List[str]]:
        """
        섹터별 핵심 분석 지표를 초기화해요
        각 섹터마다 중요하게 봐야 할 지표들이 달라요!
        """
        return {
            GICSSector.ENERGY: [
                "유가 민감도",
                "매장량 대비 생산량",
                "EBITDA 마진",
                "자유현금흐름",
                "부채비율",
                "배당수익률",
                "탄소 배출량",
                "ESG 등급",
            ],
            GICSSector.MATERIALS: [
                "원자재 가격 연동성",
                "영업레버리지",
                "EBITDA 마진",
                "운전자본 변동",
                "ROIC",
                "순부채비율",
                "환경 투자비용",
                "재활용률",
            ],
            GICSSector.INDUSTRIALS: [
                "주문잔고",
                "매출 가시성",
                "영업레버리지",
                "자유현금흐름",
                "ROIC",
                "부채비율",
                "R&D 투자",
                "자동화 수준",
            ],
            GICSSector.CONSUMER_DISCRETIONARY: [
                "동일매장 매출성장률",
                "마진율 추이",
                "재고회전율",
                "브랜드 가치",
                "시장점유율",
                "소비자 심리지수",
                "ESG 점수",
                "공급망 안정성",
            ],
            GICSSector.CONSUMER_STAPLES: [
                "매출 안정성",
                "마진 방어력",
                "배당 지속성",
                "브랜드 충성도",
                "유통망 강도",
                "원자재 헤지 비율",
                "건강성 트렌드",
                "지속가능성",
            ],
            GICSSector.HEALTH_CARE: [
                "신약 파이프라인",
                "특허 만료일",
                "임상시험 성공률",
                "FDA 승인 현황",
                "R&D 투자비율",
                "매출 가시성",
                "바이오 플랫폼",
                "의료접근성",
            ],
            GICSSector.FINANCIALS: [
                "순이자마진",
                "비이자수익",
                "신용비용률",
                "ROE",
                "BIS 비율",
                "대손충당금",
                "핀테크 투자",
                "ESG 금융 비중",
            ],
            GICSSector.INFORMATION_TECHNOLOGY: [
                "매출 성장률",
                "영업레버리지",
                "시장점유율",
                "기술 혁신력",
                "클라우드 전환율",
                "AI 역량",
                "데이터센터 효율",
                "사이버보안",
            ],
            GICSSector.COMMUNICATION_SERVICES: [
                "구독자 수",
                "ARPU",
                "콘텐츠 투자",
                "5G 인프라",
                "스트리밍 점유율",
                "광고 매출",
                "데이터 사용량",
                "디지털 전환",
            ],
            GICSSector.UTILITIES: [
                "전력 판매량",
                "요금 인상률",
                "신재생 비율",
                "규제 자산",
                "배당 지속성",
                "부채비율",
                "ESG 투자",
                "에너지 효율",
            ],
            GICSSector.REAL_ESTATE: [
                "임대료 상승률",
                "공실률",
                "NOI 마진",
                "NAV 할인율",
                "부채비율",
                "배당수익률",
                "친환경 인증",
                "입지 경쟁력",
            ],
        }

    def _initialize_korean_sector_mapping(self) -> Dict[str, GICSSector]:
        """
        한국 주요 기업들의 GICS 섹터 매핑을 초기화해요
        수동으로 정확한 매핑을 제공해요!
        """
        return {
            # Energy (10) - 에너지
            "한국석유공사": GICSSector.ENERGY,
            "SK에너지": GICSSector.ENERGY,
            "GS칼텍스": GICSSector.ENERGY,
            "한국가스공사": GICSSector.ENERGY,
            "SK가스": GICSSector.ENERGY,
            # Materials (15) - 소재
            "포스코": GICSSector.MATERIALS,
            "현대제철": GICSSector.MATERIALS,
            "LG화학": GICSSector.MATERIALS,
            "한화솔루션": GICSSector.MATERIALS,
            "SK케미칼": GICSSector.MATERIALS,
            "코스모화학": GICSSector.MATERIALS,
            # Industrials (20) - 산업재
            "현대중공업": GICSSector.INDUSTRIALS,
            "두산에너빌리티": GICSSector.INDUSTRIALS,
            "한화에어로스페이스": GICSSector.INDUSTRIALS,
            "047810": GICSSector.INDUSTRIALS,  # 한국항공우주
            "한국항공우주": GICSSector.INDUSTRIALS,
            "대한항공": GICSSector.INDUSTRIALS,
            "아시아나항공": GICSSector.INDUSTRIALS,
            # Consumer Discretionary (25) - 임의소비재
            "현대자동차": GICSSector.CONSUMER_DISCRETIONARY,
            "기아": GICSSector.CONSUMER_DISCRETIONARY,
            "LG전자": GICSSector.CONSUMER_DISCRETIONARY,
            # Consumer Staples (30) - 필수소비재
            "롯데제과": GICSSector.CONSUMER_STAPLES,
            "오리온": GICSSector.CONSUMER_STAPLES,
            "농심": GICSSector.CONSUMER_STAPLES,
            "CJ제일제당": GICSSector.CONSUMER_STAPLES,
            # Health Care (35) - 헬스케어
            "셀트리온": GICSSector.HEALTH_CARE,
            "068270": GICSSector.HEALTH_CARE,  # 셀트리온 종목코드
            "삼성바이오로직스": GICSSector.HEALTH_CARE,
            "유한양행": GICSSector.HEALTH_CARE,
            "종근당": GICSSector.HEALTH_CARE,
            "SK바이오팜": GICSSector.HEALTH_CARE,
            # Financials (40) - 금융
            "KB금융": GICSSector.FINANCIALS,
            "신한지주": GICSSector.FINANCIALS,
            "하나금융지주": GICSSector.FINANCIALS,
            "우리금융지주": GICSSector.FINANCIALS,
            "삼성생명": GICSSector.FINANCIALS,
            "032830": GICSSector.FINANCIALS,  # 삼성생명 종목코드
            "삼성화재": GICSSector.FINANCIALS,
            # Information Technology (45) - 정보기술
            "005930": GICSSector.INFORMATION_TECHNOLOGY,  # 삼성전자
            "삼성전자": GICSSector.INFORMATION_TECHNOLOGY,
            "SK하이닉스": GICSSector.INFORMATION_TECHNOLOGY,
            "LG이노텍": GICSSector.INFORMATION_TECHNOLOGY,
            "삼성SDI": GICSSector.INFORMATION_TECHNOLOGY,
            # Communication Services (50) - 커뮤니케이션서비스
            "035420": GICSSector.COMMUNICATION_SERVICES,  # 네이버
            "네이버": GICSSector.COMMUNICATION_SERVICES,
            "035720": GICSSector.COMMUNICATION_SERVICES,  # 카카오
            "카카오": GICSSector.COMMUNICATION_SERVICES,
            "KT": GICSSector.COMMUNICATION_SERVICES,
            "SK텔레콤": GICSSector.COMMUNICATION_SERVICES,
            "LG유플러스": GICSSector.COMMUNICATION_SERVICES,
            # Utilities (55) - 유틸리티
            "한국전력": GICSSector.UTILITIES,
            "한국가스공사": GICSSector.UTILITIES,
            "SK E&S": GICSSector.UTILITIES,
            # Real Estate (60) - 부동산
            "롯데리츠": GICSSector.REAL_ESTATE,
            "신한알파리츠": GICSSector.REAL_ESTATE,
        }

    def _infer_sector_from_keywords(self, stock_name: str) -> GICSSector:
        """
        종목명에서 키워드를 기반으로 섹터를 추론해요
        정확한 매핑이 없을 때 사용하는 보조 수단이에요

        Args:
            stock_name: 종목명

        Returns:
            GICSSector: 추론된 섹터 (기본값: INDUSTRIALS)
        """
        if not stock_name:
            return GICSSector.INDUSTRIALS

        name_lower = stock_name.lower()

        # 키워드 기반 섹터 매핑 룰
        sector_keywords = {
            GICSSector.ENERGY: ["석유", "가스", "에너지", "oil", "gas", "energy"],
            GICSSector.MATERIALS: [
                "화학",
                "철강",
                "제철",
                "포스코",
                "chemical",
                "steel",
            ],
            GICSSector.HEALTH_CARE: [
                "바이오",
                "제약",
                "의료",
                "헬스",
                "bio",
                "pharma",
                "health",
            ],
            GICSSector.FINANCIALS: [
                "은행",
                "금융",
                "보험",
                "증권",
                "bank",
                "financial",
                "insurance",
            ],
            GICSSector.INFORMATION_TECHNOLOGY: [
                "전자",
                "반도체",
                "IT",
                "소프트웨어",
                "tech",
                "electronic",
            ],
            GICSSector.COMMUNICATION_SERVICES: [
                "통신",
                "미디어",
                "엔터",
                "telecom",
                "media",
                "entertainment",
            ],
            GICSSector.CONSUMER_DISCRETIONARY: [
                "자동차",
                "가전",
                "카",
                "auto",
                "car",
                "appliance",
            ],
            GICSSector.CONSUMER_STAPLES: [
                "식품",
                "음료",
                "생활",
                "food",
                "beverage",
                "consumer",
            ],
            GICSSector.UTILITIES: ["전력", "수도", "utility", "power", "electric"],
            GICSSector.REAL_ESTATE: [
                "부동산",
                "리츠",
                "reit",
                "real estate",
                "property",
            ],
        }

        for sector, keywords in sector_keywords.items():
            for keyword in keywords:
                if keyword in name_lower:
                    return sector

        # 기본값: 산업재 (가장 범용적인 섹터)
        return GICSSector.INDUSTRIALS
