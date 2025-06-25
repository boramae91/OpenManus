#!/usr/bin/env python3
"""
데이터 보강 모듈 - 시계열 및 경쟁사 데이터 부족 해결
Chat GPT 피드백 반영: 웹검색을 통한 데이터 보강 기능
"""

from typing import Dict, List, Optional

from app.logger import logger


class DataEnrichmentManager:
    """
    펀더멘탈 분석을 위한 데이터 보강 관리자

    Chat GPT 피드백에서 지적된 다음 문제들을 해결합니다:
    1. 시계열 데이터 부족 (3-5년 트렌드)
    2. 경쟁사 비교 데이터 부족
    3. 업계 평균 멀티플 부족
    4. WACC 계산용 베타, 국고채 수익률 부족
    """

    def __init__(self):
        self.expert_search_templates = self._initialize_search_templates()

    def _initialize_search_templates(self) -> Dict[str, List[str]]:
        """전문가별 웹검색 템플릿 초기화"""
        return {
            "펀더멘탈 분석가": [
                "{stock_name} ROE 3년 추이 변화",
                "{stock_name} ROIC 시계열 분석",
                "{stock_name} 경쟁사 재무비율 비교",
                "{stock_name} 업계 평균 수익성",
                "{stock_name} FCF 현금흐름 3년",
                "반도체 업계 ROE 평균 2024",  # 업종별 조정 필요
                "{stock_name} vs TSMC SK하이닉스 비교",
            ],
            "밸류에이션 전문가": [
                "{stock_name} PER PBR 업계 비교",
                "{stock_name} 베타 계수 최신",
                "한국 국고채 3년 수익률 2024",
                "시장위험프리미엄 한국 2024",
                "{stock_name} EV/EBITDA 업계 평균",
                "{stock_name} 목표주가 컨센서스",
                "반도체 업계 평균 멀티플 2024",
            ],
            "산업 전문가": [
                "{stock_name} 업계 동향 2024",
                "{stock_name} 시장점유율 변화",
                "반도체 산업 사이클 현재 위치",
                "{stock_name} 경쟁사 실적 비교",
                "메모리 반도체 시장 전망",
                "{stock_name} 기술 경쟁력 분석",
            ],
            "기술 분석가": [
                "{stock_name} 차트 패턴 분석",
                "{stock_name} RSI MACD 현재 상태",
                "{stock_name} 기술적 지표 신호",
                "{stock_name} 주가 지지저항선",
            ],
            "리스크 평가사": [
                "{stock_name} 투자 위험요인",
                "{stock_name} 부채비율 안전성",
                "반도체 업계 리스크 2024",
                "{stock_name} ESG 리스크 평가",
                "지정학적 리스크 반도체",
            ],
        }

    def get_search_queries_for_expert(
        self, expert_name: str, stock_name: str, stock_sector: str = None
    ) -> List[str]:
        """
        전문가별 맞춤 웹검색 쿼리 생성

        Args:
            expert_name: 전문가명
            stock_name: 종목명
            stock_sector: 업종 (반도체, 금융, 바이오 등)

        Returns:
            List[str]: 웹검색 쿼리 리스트
        """
        try:
            # 기본 템플릿 가져오기
            templates = self.expert_search_templates.get(expert_name, [])

            # 종목명으로 템플릿 치환
            queries = []
            for template in templates:
                query = template.format(stock_name=stock_name)
                queries.append(query)

            # 업종별 추가 쿼리 (필요시)
            if stock_sector:
                sector_queries = self._get_sector_specific_queries(
                    expert_name, stock_sector
                )
                queries.extend(sector_queries)

            # 중복 제거 및 최대 5개로 제한
            unique_queries = list(dict.fromkeys(queries))[:5]

            logger.info(f"🔍 {expert_name}용 웹검색 쿼리 {len(unique_queries)}개 생성")
            return unique_queries

        except Exception as e:
            logger.error(f"웹검색 쿼리 생성 실패: {e}")
            return [f"{stock_name} 분석", f"{stock_name} 최신 정보"]

    def _get_sector_specific_queries(self, expert_name: str, sector: str) -> List[str]:
        """업종별 특화 쿼리 생성"""
        sector_queries = {
            "반도체": {
                "펀더멘탈 분석가": [
                    "메모리 반도체 업계 ROE 평균",
                    "반도체 업황 사이클 분석",
                ],
                "밸류에이션 전문가": [
                    "반도체 업계 PER 평균 2024",
                    "반도체 주식 밸류에이션",
                ],
                "산업 전문가": ["반도체 슈퍼사이클 전망", "AI 반도체 수요 분석"],
            },
            "금융": {
                "펀더멘탈 분석가": ["은행 ROE ROA 업계 평균", "금융주 자본비율 분석"],
                "밸류에이션 전문가": ["은행주 PBR 평균", "금융주 배당수익률"],
                "산업 전문가": ["금리 인상 은행 영향", "금융 규제 변화"],
            },
            "바이오": {
                "펀더멘탈 분석가": ["바이오 기업 R&D 비율", "바이오 업계 수익성"],
                "밸류에이션 전문가": [
                    "바이오 주식 밸류에이션 방법",
                    "파이프라인 가치 평가",
                ],
                "산업 전문가": ["바이오 신약 승인 동향", "바이오시밀러 시장"],
            },
        }

        return sector_queries.get(sector, {}).get(expert_name, [])

    def create_data_gap_warning(self, missing_data_types: List[str]) -> str:
        """
        부족한 데이터에 대한 경고 메시지 생성

        Args:
            missing_data_types: 부족한 데이터 유형 리스트

        Returns:
            str: 경고 메시지
        """
        warnings = {
            "시계열": "⚠️ 과거 3-5년 시계열 데이터가 부족합니다. 웹검색을 통해 트렌드 분석을 수행해주세요.",
            "경쟁사": "⚠️ 경쟁사 비교 데이터가 부족합니다. 웹검색을 통해 업계 비교 분석을 수행해주세요.",
            "업계평균": "⚠️ 업계 평균 멀티플 데이터가 부족합니다. 웹검색을 통해 상대 밸류에이션을 확인해주세요.",
            "베타": "⚠️ 베타 계수 및 WACC 계산 데이터가 부족합니다. 웹검색을 통해 최신 데이터를 확인해주세요.",
        }

        warning_messages = []
        for data_type in missing_data_types:
            if data_type in warnings:
                warning_messages.append(warnings[data_type])

        if warning_messages:
            return "\n".join(warning_messages)
        else:
            return "✅ 기본 데이터가 제공되었습니다. 추가 웹검색을 통해 분석을 보강해주세요."

    def suggest_improvement_actions(
        self, expert_name: str, analysis_gaps: List[str]
    ) -> List[str]:
        """
        분석 품질 개선을 위한 구체적 액션 제안

        Args:
            expert_name: 전문가명
            analysis_gaps: 분석 부족 영역

        Returns:
            List[str]: 개선 액션 리스트
        """
        action_templates = {
            "펀더멘탈 분석가": {
                "시계열_부족": "과거 3년간 ROE, ROIC 데이터를 웹검색으로 수집하여 트렌드 분석 수행",
                "경쟁사_부족": "주요 경쟁사 3-5개의 최신 재무비율을 검색하여 비교 테이블 작성",
                "FCF_계산": "정확한 FCF 계산식(영업CF - CAPEX) 적용 및 품질 분석",
                "WACC_계산": "베타, 무위험수익률 등을 검색하여 실제 WACC 계산",
            },
            "밸류에이션 전문가": {
                "멀티플_부족": "업계 평균 PER, PBR, EV/EBITDA를 검색하여 상대 밸류에이션 분석",
                "목표가_부족": "애널리스트 컨센서스 목표가를 검색하여 시장 기대치와 비교",
                "할인율_부족": "적절한 할인율 산정을 위한 베타, 시장위험프리미엄 검색",
            },
        }

        expert_actions = action_templates.get(expert_name, {})

        suggested_actions = []
        for gap in analysis_gaps:
            if gap in expert_actions:
                suggested_actions.append(expert_actions[gap])

        # 기본 액션 추가
        if not suggested_actions:
            suggested_actions = [
                "웹검색을 통한 최신 정보 수집",
                "업계 비교 데이터 확보",
                "시계열 분석을 위한 과거 데이터 수집",
            ]

        return suggested_actions

    def format_web_search_guidance(self, expert_name: str, stock_name: str) -> str:
        """
        전문가별 웹검색 가이드 포맷팅

        Args:
            expert_name: 전문가명
            stock_name: 종목명

        Returns:
            str: 포맷된 웹검색 가이드
        """
        queries = self.get_search_queries_for_expert(expert_name, stock_name)

        guidance = f"""
🌐 **{expert_name} 웹검색 가이드**:

Chat GPT 피드백을 반영하여 다음 정보들을 웹검색으로 보강해주세요:

📋 **필수 검색 항목**:
"""

        for i, query in enumerate(queries, 1):
            guidance += f"{i}. {query}\n"

        guidance += f"""
💡 **검색 결과 활용 방법**:
- 찾은 데이터는 출처와 함께 명시
- 정확한 수치로 비교 분석 수행
- "추정" 또는 "가정" 사용시 반드시 표시
- 경쟁사 비교는 테이블 형태로 정리

⚠️ **주의사항**:
- 추측성 언급 금지
- 모호한 표현("양호함", "안정적") 사용 금지
- 구체적 수치와 근거 제시 필수
"""

        return guidance
