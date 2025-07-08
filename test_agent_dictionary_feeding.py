#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 딕셔너리 피딩 확인 테스트
각 Agent들이 DART 딕셔너리에서 필요한 부분을 제대로 피딩하는지 확인합니다.
"""

import asyncio
import json
import os
from datetime import datetime

from app.crew.smart_sector_manager import SmartSectorManager
from app.data_collector.enhanced_financial_data_collector import (
    EnhancedDartDataCollector,
)
from app.llm import LLM


async def test_agent_dictionary_feeding():
    """Agent 딕셔너리 피딩 확인"""
    print("🔍 Agent 딕셔너리 피딩 확인 테스트")
    print("=" * 60)

    # DART API 키 확인
    dart_key = os.getenv("DART_API_KEY")
    if not dart_key:
        print("❌ DART_API_KEY 환경변수가 설정되지 않았습니다!")
        return False

    print(f"✅ DART API 키 설정됨: {dart_key[:10]}...")

    try:
        # 1. DART 딕셔너리 생성
        print("\n📊 1단계: DART 딕셔너리 생성...")
        collector = EnhancedDartDataCollector(dart_key)

        dart_result = await collector.get_business_reports_with_dictionary(
            corp_code="00126380", company_name="삼성전자", bsns_year="2024"
        )

        if not dart_result.get("success"):
            print(f"❌ DART 딕셔너리 생성 실패: {dart_result.get('error')}")
            return False

        print(f"✅ DART 딕셔너리 생성 완료")
        print(
            f"   - 사업보고서: {len(dart_result.get('business_report_dictionary', {}))}개 섹션"
        )
        print(
            f"   - 분기보고서: {len(dart_result.get('quarterly_report_dictionary', {}))}개 섹션"
        )

        # 2. SmartSectorManager 초기화
        print("\n🤖 2단계: SmartSectorManager 초기화...")
        llm = LLM()  # 실제 LLM 인스턴스 생성
        sector_manager = SmartSectorManager(llm)
        print("✅ SmartSectorManager 초기화 완료")

        # 3. 가상의 전문가 생성 (테스트용)
        print("\n👨‍💼 3단계: 테스트용 전문가 생성...")

        # 통합 재무분석가 (기술적 분석가)
        class TestExpert:
            def __init__(self, name, expertise, role):
                self.name = name
                self.expertise = expertise
                self.role = role
                self.sector_context = "정보기술"

        test_experts = [
            TestExpert("통합 재무분석가", "재무분석", "financial_analyst"),
            TestExpert("기술적 분석가", "기술분석", "technical_analyst"),
        ]

        print(f"✅ 테스트 전문가 생성 완료: {len(test_experts)}명")

        # 4. 각 전문가별 딕셔너리 피딩 확인
        print("\n🎯 4단계: 각 전문가별 딕셔너리 피딩 확인...")

        for expert in test_experts:
            print(f"\n📋 {expert.name} 딕셔너리 피딩 확인:")
            print("-" * 50)

            # 전문가별 컨텍스트 생성 (실제 SmartSectorManager 메서드 사용)
            context = await sector_manager._create_expert_specific_context(
                expert=expert,
                user_prompt="삼성전자의 재무상태와 투자 가치를 분석해주세요.",
                stock_name="삼성전자",
                stock_code="005930",
                financial_data={"success": True, "data": "재무데이터 샘플"},
                enhanced_dart_data={"success": True, "data": "DART 데이터 샘플"},
                manus_collected_data={"performed": True, "data": "웹검색 데이터 샘플"},
                technical_analysis_data={
                    "success": True,
                    "data": "기술적 분석 데이터 샘플",
                },
                dart_reports_dictionary=dart_result,  # 🎯 실제 DART 딕셔너리 전달
            )

            # 컨텍스트에서 DART 관련 내용 확인
            dart_keywords = [
                "DART",
                "사업보고서",
                "분기보고서",
                "01_회사개요",
                "페이지분할",
                "02_기타섹션",
                "03_기타섹션",
            ]

            dart_content_found = []
            for keyword in dart_keywords:
                if keyword in context:
                    dart_content_found.append(keyword)

            print(f"   - 컨텍스트 길이: {len(context):,}자")
            print(f"   - 발견된 DART 키워드: {dart_content_found}")

            if dart_content_found:
                print(f"   ✅ DART 딕셔너리 피딩 성공!")

                # 실제 섹션 내용 확인
                business_dict = dart_result.get("business_report_dictionary", {})
                quarterly_dict = dart_result.get("quarterly_report_dictionary", {})

                # 컨텍스트에서 실제 섹션명이 포함되어 있는지 확인
                found_sections = []
                for section_name in list(business_dict.keys()) + list(
                    quarterly_dict.keys()
                ):
                    if section_name in context:
                        found_sections.append(section_name)

                print(f"   - 발견된 섹션: {found_sections[:3]}...")  # 처음 3개만
                print(f"   - 총 발견 섹션 수: {len(found_sections)}개")

                # 컨텍스트에서 실제 텍스트 내용 확인 (처음 200자)
                context_preview = context[:500]
                print(f"   - 컨텍스트 미리보기: {context_preview}...")

            else:
                print(f"   ❌ DART 딕셔너리 피딩 실패!")

        # 5. 전문가별 키워드 매칭 확인
        print(f"\n🔍 5단계: 전문가별 키워드 매칭 확인...")

        # 전문가별 키워드 정의 (실제 코드에서 사용하는 키워드)
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

        for expert in test_experts:
            expert_type = expert.role
            keywords = expert_keywords.get(expert_type, [])

            print(f"\n📊 {expert.name} 키워드 매칭:")
            print(f"   - 전문가 타입: {expert_type}")
            print(f"   - 키워드 개수: {len(keywords)}개")

            # 실제 딕셔너리에서 키워드 매칭 확인
            business_dict = dart_result.get("business_report_dictionary", {})
            quarterly_dict = dart_result.get("quarterly_report_dictionary", {})

            matched_sections = []
            for section_name, content in {**business_dict, **quarterly_dict}.items():
                score = 0
                # 제목에서 키워드 매칭
                for keyword in keywords:
                    if keyword in section_name:
                        score += 3
                # 내용에서 키워드 매칭 (처음 1000자만)
                content_sample = content[:1000]
                for keyword in keywords:
                    if keyword in content_sample:
                        score += 1

                if score >= 2:
                    matched_sections.append((section_name, score))

            matched_sections.sort(key=lambda x: x[1], reverse=True)

            print(f"   - 매칭된 섹션: {len(matched_sections)}개")
            for section_name, score in matched_sections[:3]:  # 상위 3개만
                print(f"     * {section_name} (점수: {score})")

        # 6. 결과 요약
        print(f"\n📊 6단계: 결과 요약...")

        # 실제 파일로 저장
        output_file = f"agent_dictionary_feeding_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        summary = {
            "test_timestamp": datetime.now().isoformat(),
            "dart_dictionary_info": {
                "business_report_sections": list(
                    dart_result.get("business_report_dictionary", {}).keys()
                ),
                "quarterly_report_sections": list(
                    dart_result.get("quarterly_report_dictionary", {}).keys()
                ),
                "total_sections": len(dart_result.get("business_report_dictionary", {}))
                + len(dart_result.get("quarterly_report_dictionary", {})),
            },
            "expert_feeding_results": {
                expert.name: {
                    "expert_type": expert.role,
                    "context_length": len(context) if "context" in locals() else 0,
                    "dart_keywords_found": (
                        dart_content_found if "dart_content_found" in locals() else []
                    ),
                }
                for expert in test_experts
            },
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"   - 결과 저장됨: {output_file}")
        print(f"   - 테스트 완료!")

        return True

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """메인 함수"""
    success = await test_agent_dictionary_feeding()

    if success:
        print("\n🎉 Agent 딕셔너리 피딩 확인 완료!")
    else:
        print("\n❌ Agent 딕셔너리 피딩 확인 실패!")


if __name__ == "__main__":
    asyncio.run(main())
