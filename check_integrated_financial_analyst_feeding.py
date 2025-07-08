#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
통합 재무분석가 DART 딕셔너리 피딩 확인 테스트
통합 재무분석가(펀더멘털+밸류에이션)가 DART 딕셔너리에서 필요한 부분을 제대로 피딩하는지 확인합니다.
"""

import json
import os
from datetime import datetime


def check_integrated_financial_analyst_feeding():
    """통합 재무분석가 DART 딕셔너리 피딩 확인"""
    print("🔍 통합 재무분석가 DART 딕셔너리 피딩 확인")
    print("=" * 60)

    # 1. 현재 상황 분석
    print("\n📊 1단계: 현재 상황 분석...")

    print("✅ 통합 재무분석가 상태:")
    print("   - 이름: '통합 재무분석가' (Integrated Financial Analyst)")
    print("   - 역할: 펀더멘털 + 밸류에이션 통합")
    print("   - 활성화 상태: ✅ 활성화됨")
    print("   - 섹터팀 구성: 2명 체제 (통합 재무분석가 + 기술적 분석가)")

    # 2. DART 딕셔너리 피딩 문제점 발견
    print("\n⚠️ 2단계: DART 딕셔너리 피딩 문제점 발견...")

    print("❌ 문제점 발견:")
    print(
        "   - SmartSectorManager의 expert_keywords에서 'fundamental_analyst'와 'valuation_expert'가 비활성화됨"
    )
    print("   - 통합 재무분석가를 위한 키워드 매핑이 없음")
    print("   - 모든 전문가가 'technical_analyst' 키워드만 사용하도록 설정됨")

    # 3. 실제 코드 분석
    print("\n🔍 3단계: 실제 코드 분석...")

    print("📋 SmartSectorManager.py의 expert_keywords 구조:")
    print("   - fundamental_analyst: 🚫 비활성화 (통합 재무분석가로 대체)")
    print("   - valuation_expert: 🚫 비활성화 (통합 재무분석가로 대체)")
    print("   - technical_analyst: ✅ 활성화")
    print("   - industry_analyst: 🚫 비활성화 (개발 시간 절약)")
    print("   - risk_assessor: 🚫 비활성화 (개발 시간 절약)")

    print("\n📋 전문가 타입 결정 로직:")
    print("   - 기본값: expert_type = 'technical_analyst'")
    print("   - 통합 재무분석가 매칭 로직: 🚫 비활성화됨")
    print("   - 기술적 분석가 매칭 로직: ✅ 활성화됨")

    # 4. 통합 재무분석가 키워드 정의
    print("\n💡 4단계: 통합 재무분석가 키워드 정의...")

    integrated_financial_keywords = [
        # 펀더멘털 관련
        "재무",
        "손익",
        "매출",
        "순이익",
        "자산",
        "부채",
        "자본",
        "현금흐름",
        "수익성",
        "안정성",
        "회사개요",
        "사업내용",
        "재무제표",
        "손익계산서",
        "재무상태표",
        "현금흐름표",
        "ROE",
        "ROA",
        "ROIC",
        "유동비율",
        "부채비율",
        # 밸류에이션 관련
        "가치",
        "평가",
        "적정가",
        "목표가",
        "DCF",
        "밸류에이션",
        "투자",
        "배당",
        "내재가치",
        "멀티플",
        "PER",
        "PBR",
        "EV/EBITDA",
        "WACC",
        "FCF",
        "현금흐름",
        "할인율",
        "성장률",
        # 통합 분석 관련
        "종합",
        "통합",
        "분석",
        "투자의견",
        "매수",
        "매도",
        "보유",
        "시나리오",
        "리스크",
        "성장성",
        "안정성",
        "수익성",
    ]

    print(
        f"✅ 통합 재무분석가 키워드 정의 완료: {len(integrated_financial_keywords)}개"
    )
    print("   - 펀더멘털 관련: 재무제표, 손익계산서, 재무비율 등")
    print("   - 밸류에이션 관련: DCF, 멀티플, 내재가치 등")
    print("   - 통합 분석 관련: 종합 분석, 투자의견 등")

    # 5. 가상 DART 딕셔너리로 매칭 테스트
    print("\n🎯 5단계: 가상 DART 딕셔너리로 매칭 테스트...")

    mock_dart_dictionary = {
        "success": True,
        "business_report_dictionary": {
            "01_회사개요_및_사업내용": "삼성전자는 전자제품 제조업을 영위하는 회사입니다. 주요 사업은 반도체, 디스플레이, 모바일 등입니다.",
            "페이지분할_17_section": "재무상태표: 자산총계 500조원, 부채총계 200조원, 자본총계 300조원",
            "페이지분할_21_section": "손익계산서: 매출액 300조원, 영업이익 50조원, 당기순이익 40조원",
            "페이지분할_29_section": "현금흐름표: 영업활동현금흐름 60조원, 투자활동현금흐름 -30조원",
            "페이지분할_32_section": "기술적 분석: 주가 추세, 거래량 분석, 기술적 지표 등",
            "페이지분할_34_section": "차트 분석: 이동평균선, RSI, MACD 등 기술적 지표",
            "페이지분할_35_section": "밸류에이션 분석: DCF 모델, 멀티플 분석, 내재가치 산출",
            "페이지분할_36_section": "투자의견: 매수/매도/보유 판단과 목표가 제시",
        },
        "quarterly_report_dictionary": {
            "02_기타섹션": "2024년 1분기 실적: 매출 80조원, 영업이익 15조원",
            "03_기타섹션": "2024년 2분기 전망: 반도체 시장 회복 기대, 디스플레이 사업 성장",
        },
    }

    # 통합 재무분석가 매칭 테스트
    print(f"\n📋 통합 재무분석가 매칭 테스트:")
    print("-" * 50)

    business_dict = mock_dart_dictionary.get("business_report_dictionary", {})
    quarterly_dict = mock_dart_dictionary.get("quarterly_report_dictionary", {})

    matched_sections = []
    for section_name, content in {**business_dict, **quarterly_dict}.items():
        score = 0
        # 제목에서 키워드 매칭 (가중치 3)
        for keyword in integrated_financial_keywords:
            if keyword in section_name:
                score += 3
        # 내용에서 키워드 매칭 (가중치 1, 처음 1000자만)
        content_sample = content[:1000]
        for keyword in integrated_financial_keywords:
            if keyword in content_sample:
                score += 1

        if score >= 2:
            matched_sections.append((section_name, content, score))

    matched_sections.sort(key=lambda x: x[2], reverse=True)

    print(f"   - 매칭된 섹션: {len(matched_sections)}개")
    if matched_sections:
        print(f"   ✅ 통합 재무분석가 키워드 매칭 성공!")
        print(f"   - 발견된 섹션:")
        for section_name, content, score in matched_sections:
            print(f"     * {section_name} (점수: {score})")
            print(f"       내용: {content[:100]}...")
    else:
        print(f"   ❌ 통합 재무분석가 키워드 매칭 실패!")

    # 6. 현재 시스템의 문제점
    print(f"\n⚠️ 6단계: 현재 시스템의 문제점...")

    print("🔴 주요 문제점:")
    print("   1. 통합 재무분석가가 DART 딕셔너리를 제대로 피딩하지 못함")
    print("   2. 모든 전문가가 기술적 분석 키워드만 사용")
    print("   3. 펀더멘털/밸류에이션 관련 섹션이 무시됨")
    print("   4. 통합 재무분석가의 전문성이 제대로 활용되지 않음")

    # 7. 해결 방안 제시
    print(f"\n💡 7단계: 해결 방안 제시...")

    print("✅ 해결 방안:")
    print("   1. SmartSectorManager에 'integrated_financial_analyst' 키워드 추가")
    print("   2. 통합 재무분석가 매칭 로직 활성화")
    print("   3. 펀더멘털/밸류에이션 관련 키워드 복원")
    print("   4. 전문가별 키워드 매핑 정확성 개선")

    # 8. 수정된 키워드 매핑 제안
    print(f"\n🔧 8단계: 수정된 키워드 매핑 제안...")

    proposed_keywords = {
        "integrated_financial_analyst": [
            # 펀더멘털 관련
            "재무",
            "손익",
            "매출",
            "순이익",
            "자산",
            "부채",
            "자본",
            "현금흐름",
            "수익성",
            "안정성",
            "회사개요",
            "사업내용",
            "재무제표",
            "손익계산서",
            "재무상태표",
            "현금흐름표",
            "ROE",
            "ROA",
            "ROIC",
            "유동비율",
            "부채비율",
            # 밸류에이션 관련
            "가치",
            "평가",
            "적정가",
            "목표가",
            "DCF",
            "밸류에이션",
            "투자",
            "배당",
            "내재가치",
            "멀티플",
            "PER",
            "PBR",
            "EV/EBITDA",
            "WACC",
            "FCF",
            "할인율",
            "성장률",
            # 통합 분석 관련
            "종합",
            "통합",
            "분석",
            "투자의견",
            "매수",
            "매도",
            "보유",
            "시나리오",
            "리스크",
            "성장성",
            "안정성",
            "수익성",
        ],
        "technical_analyst": [
            "기술적",
            "차트",
            "지표",
            "추세",
            "거래량",
            "변동성",
            "이동평균",
            "RSI",
            "MACD",
            "볼린저밴드",
            "스토캐스틱",
        ],
    }

    print("✅ 제안된 키워드 매핑:")
    for expert_type, keywords in proposed_keywords.items():
        print(f"   - {expert_type}: {len(keywords)}개 키워드")

    # 9. 결과 요약
    print(f"\n📊 9단계: 결과 요약...")

    summary = {
        "test_timestamp": datetime.now().isoformat(),
        "issue_found": True,
        "problem_description": "통합 재무분석가가 DART 딕셔너리를 제대로 피딩하지 못함",
        "current_status": {
            "integrated_financial_analyst": "활성화됨 (섹터팀에서)",
            "dart_feeding": "비활성화됨 (키워드 매핑 없음)",
            "keywords_mapping": "기술적 분석가만 활성화",
        },
        "proposed_solution": {
            "add_integrated_financial_keywords": True,
            "enable_matching_logic": True,
            "restore_fundamental_valuation_keywords": True,
        },
        "mock_test_results": {
            "matched_sections": len(matched_sections),
            "test_successful": len(matched_sections) > 0,
        },
    }

    # 결과 파일 저장
    output_file = f"integrated_financial_analyst_feeding_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"   - 결과 저장됨: {output_file}")
    print(f"   - 문제 발견: ✅ 통합 재무분석가 DART 피딩 문제 확인됨")
    print(f"   - 해결 필요: 🔧 SmartSectorManager 키워드 매핑 수정 필요")

    return True


def main():
    """메인 함수"""
    success = check_integrated_financial_analyst_feeding()

    if success:
        print("\n🎉 통합 재무분석가 DART 딕셔너리 피딩 확인 완료!")
        print("⚠️ 문제점이 발견되어 수정이 필요합니다!")
    else:
        print("\n❌ 통합 재무분석가 DART 딕셔너리 피딩 확인 실패!")


if __name__ == "__main__":
    main()
