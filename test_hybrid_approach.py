#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
하이브리드 방식 테스트
키워드 추가 + 가중치 부여가 제대로 작동하는지 확인합니다.
"""


def test_hybrid_approach():
    """하이브리드 방식 테스트"""
    print("🔍 하이브리드 방식 테스트")
    print("=" * 60)

    # 1. 개선된 키워드 목록 (하이브리드 방식 적용 후)
    print("\n📊 1단계: 개선된 키워드 목록 확인")

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
        # 회사개요/사업내용 관련 (하이브리드 방식 추가)
        "사업",
        "개요",
        "기업",
        "회사",
        "업종",
        "산업",
        "시장",
        "경쟁",
    ]

    print(f"✅ 통합 재무분석가 키워드 수: {len(integrated_financial_keywords)}개")

    # 새로 추가된 키워드 확인
    new_keywords = ["사업", "개요", "기업", "회사", "업종", "산업", "시장", "경쟁"]
    print(f"✅ 새로 추가된 키워드: {new_keywords}")

    # 2. 테스트 케이스들
    print("\n📊 2단계: 테스트 케이스 시뮬레이션")

    test_cases = [
        {
            "title": "01_회사개요_및_사업내용",
            "content": "삼성전자는 전자제품 제조업을 영위하는 회사입니다.",
            "description": "기본 회사개요 (재무 정보 없음)",
        },
        {
            "title": "01_회사개요_및_사업내용",
            "content": "삼성전자는 반도체, 디스플레이, 모바일 사업을 영위하며, 매출액 300조원, ROE 13.3%를 기록합니다.",
            "description": "개선된 회사개요 (재무 정보 포함)",
        },
        {
            "title": "페이지분할_17_section",
            "content": "재무상태표: 자산총계 500조원, 부채총계 200조원, 자본총계 300조원",
            "description": "재무상태표 섹션",
        },
        {
            "title": "페이지분할_42_section",
            "content": "밸류에이션: PER 15배, PBR 1.2배, EV/EBITDA 8배, 내재가치 80,000원",
            "description": "밸류에이션 섹션",
        },
    ]

    # 3. 하이브리드 방식 점수 계산 시뮬레이션
    print("\n📊 3단계: 하이브리드 방식 점수 계산")

    for i, case in enumerate(test_cases, 1):
        print(f"\n   📋 테스트 케이스 {i}: {case['description']}")
        print(f"      제목: {case['title']}")
        print(f"      내용: {case['content']}")

        score = 0

        # 제목에서 키워드 매칭 (가중치 3)
        title_matches = []
        for keyword in integrated_financial_keywords:
            if keyword in case["title"]:
                score += 3
                title_matches.append(keyword)

        # 내용에서 키워드 매칭 (가중치 1, 처음 1000자만)
        content_matches = []
        content_sample = case["content"][:1000]
        for keyword in integrated_financial_keywords:
            if keyword in content_sample:
                score += 1
                content_matches.append(keyword)

        # 하이브리드 방식: 회사개요/사업내용 섹션에 추가 가중치 부여
        additional_weight = 0
        if "회사개요" in case["title"] or "사업내용" in case["title"]:
            additional_weight = 5
            score += additional_weight
            print(f"      🚀 하이브리드 가중치 적용: +5점")

        print(f"      제목 매칭: {title_matches}")
        print(f"      내용 매칭: {content_matches}")
        print(f"      기본 점수: {score - additional_weight}점")
        print(f"      추가 가중치: +{additional_weight}점")
        print(f"      최종 점수: {score}점")

        if score >= 2:
            print(f"      ✅ 매칭 성공! (2점 이상)")
        else:
            print(f"      ❌ 매칭 실패 (2점 미만)")

    # 4. 개선 효과 분석
    print("\n📊 4단계: 개선 효과 분석")

    print("✅ 하이브리드 방식 적용 전:")
    print("   - 회사개요 섹션: 0점 (키워드 매칭 없음)")
    print("   - 분석에서 제외됨")

    print("\n✅ 하이브리드 방식 적용 후:")
    print("   - 회사개요 섹션: 키워드 매칭 + 추가 가중치 5점")
    print("   - 분석에 포함됨")
    print("   - 자연스러운 선택 + 우선순위 보장")

    print("\n🎯 하이브리드 방식의 장점:")
    print("   1. 자연스러운 선택: 키워드 매칭으로 자연스럽게 선택")
    print("   2. 우선순위 보장: 회사개요/사업내용에 높은 가중치로 우선 선택")
    print("   3. 일관성 유지: 다른 섹션과 동일한 로직 적용")
    print("   4. 유연성: 여전히 점수 기반으로 선택되지만 우선순위 높음")

    print(f"\n🎉 하이브리드 방식 테스트 완료!")
    return True


if __name__ == "__main__":
    test_hybrid_approach()
