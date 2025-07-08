#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
회사개요 부분 0점 원인 분석
왜 회사개요 섹션이 키워드 매칭에서 0점을 받았는지 상세히 분석합니다.
"""


def analyze_company_overview_score():
    """회사개요 부분 0점 원인 분석"""
    print("🔍 회사개요 부분 0점 원인 분석")
    print("=" * 60)

    # 테스트 데이터
    section_title = "01_회사개요_및_사업내용"
    content = "삼성전자는 전자제품 제조업을 영위하는 회사입니다."

    # 통합 재무분석가 키워드 (테스트에서 사용된 것과 동일)
    integrated_financial_keywords = [
        "재무",
        "손익",
        "매출",
        "순이익",
        "자산",
        "부채",
        "자본",
        "현금흐름",
        "ROE",
        "ROA",
        "유동비율",
        "부채비율",
        "가치",
        "평가",
        "적정가",
        "목표가",
        "DCF",
        "밸류에이션",
        "PER",
        "PBR",
        "EV/EBITDA",
        "투자의견",
        "매수",
        "매도",
    ]

    print(f"📋 분석 대상:")
    print(f"   - 섹션 제목: {section_title}")
    print(f"   - 섹션 내용: {content}")
    print(f"   - 키워드 수: {len(integrated_financial_keywords)}개")

    # 1. 제목에서 키워드 매칭 분석
    print(f"\n🔍 1단계: 제목에서 키워드 매칭 분석")
    print(f"   제목: '{section_title}'")

    title_matches = []
    for keyword in integrated_financial_keywords:
        if keyword in section_title:
            title_matches.append(keyword)
            print(f"   ✅ '{keyword}' 매칭됨 (가중치 3점)")

    if not title_matches:
        print(f"   ❌ 제목에서 매칭된 키워드 없음")

    # 2. 내용에서 키워드 매칭 분석
    print(f"\n🔍 2단계: 내용에서 키워드 매칭 분석")
    print(f"   내용: '{content}'")
    print(f"   내용 샘플 (처음 1000자): '{content[:1000]}'")

    content_matches = []
    for keyword in integrated_financial_keywords:
        if keyword in content[:1000]:
            content_matches.append(keyword)
            print(f"   ✅ '{keyword}' 매칭됨 (가중치 1점)")

    if not content_matches:
        print(f"   ❌ 내용에서 매칭된 키워드 없음")

    # 3. 점수 계산
    print(f"\n🔍 3단계: 점수 계산")
    title_score = len(title_matches) * 3
    content_score = len(content_matches) * 1
    total_score = title_score + content_score

    print(f"   - 제목 매칭 점수: {title_score}점 ({len(title_matches)}개 × 3)")
    print(f"   - 내용 매칭 점수: {content_score}점 ({len(content_matches)}개 × 1)")
    print(f"   - 총점: {total_score}점")

    # 4. 문제점 분석
    print(f"\n🔍 4단계: 문제점 분석")

    print(f"❌ 문제점 1: 키워드 누락")
    print(f"   - '회사개요' 키워드가 통합 재무분석가 키워드에 없음")
    print(f"   - '사업내용' 키워드가 통합 재무분석가 키워드에 없음")

    print(f"\n❌ 문제점 2: 내용의 한계")
    print(f"   - 내용이 너무 짧고 일반적임: '{content}'")
    print(f"   - 구체적인 재무 정보나 밸류에이션 관련 내용 없음")

    # 5. 해결 방안 제시
    print(f"\n🔍 5단계: 해결 방안")

    print(f"✅ 해결방안 1: 키워드 추가")
    additional_keywords = ["회사개요", "사업내용", "사업", "개요", "기업", "회사"]
    print(f"   추가할 키워드: {additional_keywords}")

    print(f"\n✅ 해결방안 2: 내용 개선")
    improved_content = "삼성전자는 전자제품 제조업을 영위하는 회사입니다. 주요 사업은 반도체, 디스플레이, 모바일 등이며, 매출액 300조원, 영업이익 50조원을 기록하고 있습니다. ROE 13.3%, ROA 8.0%의 수익성을 보이며, PER 15배, PBR 1.2배의 밸류에이션 지표를 가지고 있습니다."
    print(f"   개선된 내용: '{improved_content}'")

    # 6. 개선된 키워드로 재테스트
    print(f"\n🔍 6단계: 개선된 키워드로 재테스트")

    improved_keywords = integrated_financial_keywords + additional_keywords

    improved_title_matches = []
    for keyword in improved_keywords:
        if keyword in section_title:
            improved_title_matches.append(keyword)

    improved_content_matches = []
    for keyword in improved_keywords:
        if keyword in improved_content[:1000]:
            improved_content_matches.append(keyword)

    improved_title_score = len(improved_title_matches) * 3
    improved_content_score = len(improved_content_matches) * 1
    improved_total_score = improved_title_score + improved_content_score

    print(f"   - 개선된 제목 매칭: {improved_title_matches}")
    print(f"   - 개선된 내용 매칭: {improved_content_matches}")
    print(f"   - 개선된 총점: {improved_total_score}점")

    if improved_total_score >= 2:
        print(f"   ✅ 개선 후 매칭 성공! (2점 이상)")
    else:
        print(f"   ❌ 개선 후에도 매칭 실패 (2점 미만)")

    # 7. 결론
    print(f"\n🔍 7단계: 결론")
    print(f"📝 회사개요 부분이 0점인 이유:")
    print(f"   1. '회사개요', '사업내용' 키워드가 통합 재무분석가 키워드에 없음")
    print(f"   2. 내용이 너무 짧고 구체적인 재무/밸류에이션 정보가 없음")
    print(f"   3. 키워드 매칭 알고리즘이 제목과 내용에서 모두 매칭을 찾지 못함")

    print(f"\n💡 개선 방안:")
    print(f"   1. 통합 재무분석가 키워드에 '회사개요', '사업내용' 추가")
    print(f"   2. 실제 DART 데이터에서는 더 상세한 내용이 포함될 것으로 예상")
    print(f"   3. 키워드 매칭 알고리즘은 정상 작동 중")


if __name__ == "__main__":
    analyze_company_overview_score()
