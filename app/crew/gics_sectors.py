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

    def _initialize_sector_contexts(self) -> Dict[GICSSector, Dict[str, str]]:
        """
        섹터별 전문 컨텍스트를 초기화해요
        각 섹터의 특성과 분석 관점을 정의해요!
        """
        return {
            GICSSector.ENERGY: {
                "industry_focus": "석유, 가스, 신재생에너지, 에너지 장비 및 서비스",
                "key_drivers": "유가 변동, 글로벌 에너지 수급, 탄소중립 정책, 지정학적 리스크",
                "valuation_approach": "자산 기반 평가, DCF, 유가 시나리오 분석",
                "cyclical_nature": "고도의 경기순환성, 유가 민감성",
                "esg_focus": "환경 규제, 탄소 배출, 에너지 전환",
            },
            GICSSector.MATERIALS: {
                "industry_focus": "화학, 건설자재, 용기포장재, 금속광업, 제지임산",
                "key_drivers": "글로벌 경기, 인프라 투자, 원자재 가격, 중국 경기",
                "valuation_approach": "P/B, EV/EBITDA, 원자재 가격 기반 평가",
                "cyclical_nature": "강한 경기순환성, 수요 변동성",
                "esg_focus": "환경 오염, 재활용, 지속가능한 원자재",
            },
            GICSSector.INDUSTRIALS: {
                "industry_focus": "자본재, 상업서비스, 운송, 항공우주국방",
                "key_drivers": "설비투자, 글로벌 무역, 인프라 투자, 자동화 트렌드",
                "valuation_approach": "P/E, EV/EBITDA, 주문잔고 분석",
                "cyclical_nature": "중간 수준의 경기순환성",
                "esg_focus": "스마트팩토리, 친환경 운송, 안전성",
            },
            GICSSector.CONSUMER_DISCRETIONARY: {
                "industry_focus": "자동차, 가전, 의류, 호텔레스토랑, 미디어엔터테인먼트",
                "key_drivers": "소비자 심리, 가처분소득, 트렌드 변화, 전기차 전환",
                "valuation_approach": "P/E, P/S, 브랜드 가치 평가",
                "cyclical_nature": "높은 경기 민감성",
                "esg_focus": "친환경 제품, 근로자 권익, 공급망 투명성",
            },
            GICSSector.CONSUMER_STAPLES: {
                "industry_focus": "식음료, 생활용품, 소매업체, 담배",
                "key_drivers": "인구 변화, 건강 트렌드, 원자재 가격, 유통 혁신",
                "valuation_approach": "P/E, 배당수익률, 브랜드 프리미엄",
                "cyclical_nature": "낮은 경기 민감성, 방어적 특성",
                "esg_focus": "건강한 제품, 지속가능한 포장, 공정무역",
            },
            GICSSector.HEALTH_CARE: {
                "industry_focus": "제약, 바이오테크, 의료기기, 헬스케어 서비스",
                "key_drivers": "고령화, 신약 승인, 의료 접근성, 바이오 혁신",
                "valuation_approach": "DCF, rNPV(위험조정순현재가치), P/E",
                "cyclical_nature": "낮은 경기 민감성, 방어적 특성",
                "esg_focus": "의료 접근성, 약물 안전성, 연구 윤리",
            },
            GICSSector.FINANCIALS: {
                "industry_focus": "은행, 증권, 보험, 부동산금융",
                "key_drivers": "금리 변동, 신용 리스크, 규제 변화, 핀테크 혁신",
                "valuation_approach": "P/B, ROE, 순이자마진 분석",
                "cyclical_nature": "강한 경기순환성, 금리 민감성",
                "esg_focus": "ESG 금융, 금융 포용성, 리스크 관리",
            },
            GICSSector.INFORMATION_TECHNOLOGY: {
                "industry_focus": "소프트웨어, 반도체, IT서비스, 전자장비",
                "key_drivers": "디지털 전환, AI/클라우드, 반도체 사이클, 기술 혁신",
                "valuation_approach": "P/E, P/S, EV/Sales, 성장률 기반 평가",
                "cyclical_nature": "기술 사이클, 반도체 업황",
                "esg_focus": "데이터 프라이버시, 디지털 격차, 에너지 효율",
            },
            GICSSector.COMMUNICATION_SERVICES: {
                "industry_focus": "통신서비스, 미디어엔터테인먼트, 인터랙티브미디어",
                "key_drivers": "5G 확산, 스트리밍 서비스, 광고 시장, 콘텐츠 경쟁",
                "valuation_approach": "EV/EBITDA, P/E, 구독자 기반 평가",
                "cyclical_nature": "중간 수준의 경기 민감성",
                "esg_focus": "정보 보안, 콘텐츠 윤리, 디지털 웰빙",
            },
            GICSSector.UTILITIES: {
                "industry_focus": "전력, 가스, 수도, 신재생에너지",
                "key_drivers": "전력 수요, 규제 환경, 에너지 전환, ESG 투자",
                "valuation_approach": "배당수익률, P/B, 규제자산 기준 평가",
                "cyclical_nature": "매우 낮은 경기 민감성, 안정적",
                "esg_focus": "친환경 에너지, 에너지 효율, 안정적 공급",
            },
            GICSSector.REAL_ESTATE: {
                "industry_focus": "부동산투자신탁, 부동산관리개발",
                "key_drivers": "금리 변동, 부동산 시장, 임대료 동향, 도시화",
                "valuation_approach": "P/B, 배당수익률, NAV 기준 평가",
                "cyclical_nature": "강한 금리 민감성",
                "esg_focus": "친환경 건물, 지속가능한 개발, 임차인 만족",
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
