#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 Agent 딕셔너리 피딩 확인 테스트
각 Agent들이 DART 딕셔너리에서 필요한 부분을 제대로 피딩하는지 확인합니다.
"""

import json
import os
from datetime import datetime


def test_agent_dictionary_feeding_logic():
    """Agent 딕셔너리 피딩 로직 테스트"""
    print("🔍 Agent 딕셔너리 피딩 로직 확인")
    print("=" * 60)

    # 1. 가상의 DART 딕셔너리 생성 (실제 구조 시뮬레이션)
    print("\n📊 1단계: 가상 DART 딕셔너리 생성...")

    mock_dart_dictionary = {
        "success": True,
        "business_report_dictionary": {
            "01_회사개요_및_사업내용": "삼성전자는 전자제품 제조업을 영위하는 회사입니다. 주요 사업은 반도체, 디스플레이, 모바일 등입니다.",
            "페이지분할_17_section": "재무상태표: 자산총계 500조원, 부채총계 200조원, 자본총계 300조원",
            "페이지분할_21_section": "손익계산서: 매출액 300조원, 영업이익 50조원, 당기순이익 40조원",
            "페이지분할_29_section": "현금흐름표: 영업활동현금흐름 60조원, 투자활동현금흐름 -30조원",
            "페이지분할_32_section": "기술적 분석: 주가 추세, 거래량 분석, 기술적 지표 등",
            "페이지분할_34_section": "차트 분석: 이동평균선, RSI, MACD 등 기술적 지표",
        },
        "quarterly_report_dictionary": {
            "02_기타섹션": "2024년 1분기 실적: 매출 80조원, 영업이익 15조원",
            "03_기타섹션": "2024년 2분기 전망: 반도체 시장 회복 기대, 디스플레이 사업 성장",
        },
    }

    print(f"✅ 가상 DART 딕셔너리 생성 완료")
    print(
        f"   - 사업보고서: {len(mock_dart_dictionary['business_report_dictionary'])}개 섹션"
    )
    print(
        f"   - 분기보고서: {len(mock_dart_dictionary['quarterly_report_dictionary'])}개 섹션"
    )

    # 2. 전문가별 키워드 정의 (실제 코드에서 사용하는 키워드)
    print("\n🎯 2단계: 전문가별 키워드 정의...")

    expert_keywords = {
        "financial_analyst": [
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
        ],
        "technical_analyst": ["기술적", "차트", "지표", "추세", "거래량", "변동성"],
    }

    print(f"✅ 전문가별 키워드 정의 완료")
    for expert_type, keywords in expert_keywords.items():
        print(f"   - {expert_type}: {len(keywords)}개 키워드")

    # 3. 전문가별 딕셔너리 피딩 시뮬레이션
    print("\n🤖 3단계: 전문가별 딕셔너리 피딩 시뮬레이션...")

    test_experts = [
        {"name": "통합 재무분석가", "role": "financial_analyst"},
        {"name": "기술적 분석가", "role": "technical_analyst"},
    ]

    for expert in test_experts:
        print(f"\n📋 {expert['name']} 딕셔너리 피딩 확인:")
        print("-" * 50)

        expert_type = expert["role"]
        keywords = expert_keywords.get(expert_type, [])

        # 실제 딕셔너리에서 키워드 매칭 확인
        business_dict = mock_dart_dictionary.get("business_report_dictionary", {})
        quarterly_dict = mock_dart_dictionary.get("quarterly_report_dictionary", {})

        matched_sections = []
        for section_name, content in {**business_dict, **quarterly_dict}.items():
            score = 0
            # 제목에서 키워드 매칭 (가중치 3)
            for keyword in keywords:
                if keyword in section_name:
                    score += 3
            # 내용에서 키워드 매칭 (가중치 1, 처음 1000자만)
            content_sample = content[:1000]
            for keyword in keywords:
                if keyword in content_sample:
                    score += 1

            if score >= 2:
                matched_sections.append((section_name, content, score))

        matched_sections.sort(key=lambda x: x[2], reverse=True)

        print(f"   - 전문가 타입: {expert_type}")
        print(f"   - 키워드 개수: {len(keywords)}개")
        print(f"   - 매칭된 섹션: {len(matched_sections)}개")

        if matched_sections:
            print(f"   ✅ DART 딕셔너리 피딩 성공!")
            print(f"   - 발견된 섹션:")
            for section_name, content, score in matched_sections:
                print(f"     * {section_name} (점수: {score})")
                print(f"       내용: {content[:100]}...")
        else:
            print(f"   ❌ DART 딕셔너리 피딩 실패!")

    # 4. 실제 피딩된 컨텍스트 시뮬레이션
    print(f"\n📝 4단계: 실제 피딩된 컨텍스트 시뮬레이션...")

    for expert in test_experts:
        print(f"\n📋 {expert['name']} 컨텍스트 시뮬레이션:")
        print("-" * 50)

        expert_type = expert["role"]
        keywords = expert_keywords.get(expert_type, [])

        # 매칭된 섹션 찾기
        business_dict = mock_dart_dictionary.get("business_report_dictionary", {})
        quarterly_dict = mock_dart_dictionary.get("quarterly_report_dictionary", {})

        business_sections = []
        quarterly_sections = []

        for section_name, content in business_dict.items():
            score = 0
            for keyword in keywords:
                if keyword in section_name:
                    score += 3
                if keyword in content[:1000]:
                    score += 1
            if score >= 2:
                business_sections.append((section_name, content, score))

        for section_name, content in quarterly_dict.items():
            score = 0
            for keyword in keywords:
                if keyword in section_name:
                    score += 3
                if keyword in content[:1000]:
                    score += 1
            if score >= 2:
                quarterly_sections.append((section_name, content, score))

        # 컨텍스트 생성 시뮬레이션
        context_parts = []
        total_content_length = 0

        if business_sections:
            context_parts.append(
                f"📄 **{expert['name']} 관련 사업보고서 섹션 (연간 종합정보)**:"
            )
            for section_name, content, score in business_sections:
                context_parts.append(f"### {section_name} (관련도: {score}점)")
                context_parts.append(content)
                context_parts.append("")
                total_content_length += len(content)

        if quarterly_sections:
            context_parts.append(
                f"📈 **{expert['name']} 관련 분기보고서 섹션 (최신 분기정보)**:"
            )
            for section_name, content, score in quarterly_sections:
                context_parts.append(f"### {section_name} (관련도: {score}점)")
                context_parts.append(content)
                context_parts.append("")
                total_content_length += len(content)

        if business_sections or quarterly_sections:
            context_parts.append(
                "🔍 **분석 지침**: 사업보고서는 연간 종합정보이고, 분기보고서는 최신 분기 실적입니다."
            )
            context_parts.append("")

        # 결과 출력
        final_context = "\n".join(context_parts)
        print(f"   - 컨텍스트 길이: {len(final_context):,}자")
        print(f"   - 사업보고서 섹션: {len(business_sections)}개")
        print(f"   - 분기보고서 섹션: {len(quarterly_sections)}개")
        print(f"   - 총 내용 길이: {total_content_length:,}자")

        if final_context:
            print(f"   - 컨텍스트 미리보기: {final_context[:300]}...")
            print(f"   ✅ 컨텍스트 생성 성공!")
        else:
            print(f"   ❌ 컨텍스트 생성 실패!")

    # 5. 결과 요약
    print(f"\n📊 5단계: 결과 요약...")

    summary = {
        "test_timestamp": datetime.now().isoformat(),
        "mock_dart_dictionary_info": {
            "business_report_sections": list(
                mock_dart_dictionary["business_report_dictionary"].keys()
            ),
            "quarterly_report_sections": list(
                mock_dart_dictionary["quarterly_report_dictionary"].keys()
            ),
            "total_sections": len(mock_dart_dictionary["business_report_dictionary"])
            + len(mock_dart_dictionary["quarterly_report_dictionary"]),
        },
        "expert_keywords": expert_keywords,
        "test_experts": test_experts,
    }

    # 결과 파일 저장
    output_file = (
        f"agent_feeding_logic_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"   - 결과 저장됨: {output_file}")
    print(f"   - 테스트 완료!")

    return True


def main():
    """메인 함수"""
    success = test_agent_dictionary_feeding_logic()

    if success:
        print("\n🎉 Agent 딕셔너리 피딩 로직 확인 완료!")
    else:
        print("\n❌ Agent 딕셔너리 피딩 로직 확인 실패!")


if __name__ == "__main__":
    main()
