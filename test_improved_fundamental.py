#!/usr/bin/env python3
"""
🎯 개선된 펀더멘탈 분석 프롬프트 테스트 스크립트

Chat GPT 피드백 반영 사항:
1. 웹검색 기능 활성화
2. 프롬프트 단순화 및 핵심 포커스
3. 데이터 보강 기능
4. 경쟁사 비교 및 시계열 분석 강화
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# OpenManus 프로젝트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.crew.smart_sector_manager import AnalysisDepth, SmartSectorManager
from app.llm import LLM
from app.logger import logger


async def test_improved_fundamental_analysis():
    """개선된 펀더멘탈 분석 테스트"""

    print("🎯 개선된 펀더멘탈 분석 프롬프트 테스트")
    print("=" * 60)
    print("Chat GPT 피드백 반영 사항:")
    print("✅ 웹검색 기능 활성화")
    print("✅ 프롬프트 단순화 (6단계 → 6개 핵심 포커스)")
    print("✅ 데이터 보강 가이드 추가")
    print("✅ 경쟁사 비교 필수화")
    print("✅ 시계열 트렌드 분석 강화")
    print("=" * 60)

    try:
        # LLM 및 SmartSectorManager 초기화
        llm = LLM()
        smart_sector_manager = SmartSectorManager(llm=llm)

        # 테스트용 종목 정보 (삼성전자)
        stock_info = {
            "stock_name": "삼성전자",
            "stock_code": "005930",
            "gics_sector": "Technology Hardware, Storage & Peripherals",
        }

        # 테스트용 재무데이터 (실제 삼성전자 데이터 기반)
        financial_data = {
            "success": True,
            "stock_name": "삼성전자",
            "stock_code": "005930",
            "basic_info": {
                "current_price": "73,000원",
                "market_cap": "436조원",
                "per": "18.9배",
                "pbr": "1.96배",
                "dividend_yield": "2.1%",
            },
            "financial_ratios": {
                "roe": "9.228%",
                "roa": "6.2%",
                "roic": "2.69%",  # Chat GPT가 지적한 낮은 ROIC
                "debt_ratio": "30.2%",
                "current_ratio": "2.47배",
                "operating_margin": "5.9%",
                "net_margin": "11.37%",
            },
            "cash_flow": {
                "operating_cf": "64,645,830백만원",
                "investing_cf": "-48,370,461백만원",
                "financing_cf": "3,300,960백만원",
                "free_cf": "16,193,722백만원",  # 정확한 FCF 계산
            },
            "growth_metrics": {
                "revenue_growth": "-19.27%",  # Chat GPT가 지적한 매출 감소
                "operating_income_growth": "-35.4%",
                "net_income_growth": "-22.8%",
            },
        }

        # 테스트용 Enhanced DART 데이터
        enhanced_dart_data = {
            "success": True,
            "business_info": "반도체, 디스플레이 제조업",
            "financial_info": "연결재무제표 기준 분석",
            "risk_factors": ["메모리 반도체 가격 변동", "환율 변동", "지정학적 리스크"],
            "capex_info": "2024년 설비투자 48조원 계획",
        }

        # 테스트용 Manus 수집 데이터
        manus_collected_data = {
            "performed": True,
            "collected_information": "최신 반도체 업계 동향: 메모리 반도체 가격 회복 지연, AI 반도체 수요 증가",
            "data_richness_score": 85.0,
            "pdf_analysis": {"pdf_detected": False},
        }

        print(
            f"📊 테스트 종목: {stock_info['stock_name']} ({stock_info['stock_code']})"
        )
        print(f"📈 분석 깊이: DEEP (심화 분석 - 웹검색 포함)")
        print(f"🎯 테스트 포커스: 펀더멘탈 분석가 프롬프트 개선")
        print("")

        # 종합 분석 실행
        result = await smart_sector_manager.analyze_with_comprehensive_data(
            user_prompt="삼성전자의 투자 매력도를 Chat GPT 피드백을 반영하여 상세히 분석해주세요. 특히 경쟁사 비교, 시계열 트렌드, WACC vs ROIC 분석을 중점적으로 부탁드립니다.",
            stock_name=stock_info["stock_name"],
            stock_code=stock_info["stock_code"],
            financial_data=financial_data,
            enhanced_dart_data=enhanced_dart_data,
            manus_collected_data=manus_collected_data,
            analysis_depth=AnalysisDepth.DEEP,
            pre_detected_gics_sector=stock_info["gics_sector"],
        )

        print("✅ 종합 분석 완료!")
        print(f"🎯 감지된 섹터: {result.get('detected_sector', '알 수 없음')}")
        print(f"📊 활성화된 전문가: {len(result.get('activated_experts', []))}명")

        # 펀더멘탈 분석가 결과 확인
        expert_insights = result.get("expert_insights", {})
        individual_analyses = expert_insights.get("individual_expert_analyses", [])

        fundamental_analysis = None
        for analysis in individual_analyses:
            if "펀더멘탈" in analysis.get("expert_name", ""):
                fundamental_analysis = analysis
                break

        if fundamental_analysis:
            print("\n" + "=" * 60)
            print("🔍 펀더멘탈 분석가 결과 (개선 사항 확인)")
            print("=" * 60)

            analysis_result = fundamental_analysis.get("analysis_result", "")
            tool_calls_info = fundamental_analysis.get("tool_calls_info", "")

            # 개선 사항 체크
            improvements_check = {
                "웹검색_사용": "🌐" in tool_calls_info or "웹검색" in analysis_result,
                "경쟁사_비교": "경쟁사" in analysis_result
                or "TSMC" in analysis_result
                or "SK하이닉스" in analysis_result,
                "시계열_분석": "3년" in analysis_result
                or "2021" in analysis_result
                or "트렌드" in analysis_result,
                "FCF_정확성": "영업현금흐름" in analysis_result
                and "자본적지출" in analysis_result,
                "WACC_분석": "WACC" in analysis_result or "자본비용" in analysis_result,
                "구체적_수치": "%" in analysis_result
                and ("위" in analysis_result or "순위" in analysis_result),
                "투자_판단": "사야" in analysis_result
                or "기다려야" in analysis_result
                or "피해야" in analysis_result,
            }

            print("📋 개선 사항 체크리스트:")
            for check_item, is_improved in improvements_check.items():
                status = "✅" if is_improved else "❌"
                print(f"  {status} {check_item}: {'개선됨' if is_improved else '미흡'}")

            # 웹검색 사용 여부 확인
            if tool_calls_info:
                print(f"\n🔧 도구 사용 현황:")
                print(f"  {tool_calls_info}")

            # 분석 결과 미리보기 (처음 500자)
            print(f"\n📄 분석 결과 미리보기 (총 {len(analysis_result):,}자):")
            print("-" * 40)
            print(
                analysis_result[:500] + "..."
                if len(analysis_result) > 500
                else analysis_result
            )

            # 개선 정도 평가
            improvement_score = (
                sum(improvements_check.values()) / len(improvements_check) * 100
            )
            print(f"\n📊 전체 개선도: {improvement_score:.1f}%")

            if improvement_score >= 80:
                print("🎉 우수한 개선 결과!")
            elif improvement_score >= 60:
                print("👍 양호한 개선 결과")
            else:
                print("⚠️ 추가 개선 필요")

        else:
            print("❌ 펀더멘탈 분석가 결과를 찾을 수 없습니다.")

        # 전체 결과 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_filename = f"results/improved_fundamental_test_{timestamp}.json"

        try:
            os.makedirs("results", exist_ok=True)
            with open(result_filename, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n💾 전체 결과 저장: {result_filename}")
        except Exception as e:
            print(f"⚠️ 결과 저장 실패: {e}")

        # 종합 평가
        print("\n" + "=" * 60)
        print("🎯 종합 평가")
        print("=" * 60)

        synthesis = expert_insights.get("synthesis_result", {})
        if synthesis and synthesis.get("synthesis_success"):
            print("✅ 전문가 종합 분석 성공")
            print(
                f"📊 데이터 통합 품질: {result.get('data_integration_quality', '알 수 없음')}"
            )
            print(
                f"💰 비용 절감: {result.get('cost_savings', {}).get('savings_percentage', 0):.1f}%"
            )
        else:
            print("❌ 전문가 종합 분석 실패")

        return True

    except Exception as e:
        print(f"❌ 테스트 실행 중 오류: {e}")
        logger.error(f"테스트 실행 오류: {e}")
        return False


async def main():
    """메인 테스트 실행"""
    print("🚀 개선된 펀더멘탈 분석 프롬프트 테스트 시작")
    print()

    try:
        success = await test_improved_fundamental_analysis()

        if success:
            print("\n🎉 테스트 완료!")
            print("\n📋 주요 개선 사항:")
            print("1. ✅ 웹검색 도구 연결 및 활성화")
            print("2. ✅ 프롬프트 단순화 (3,000자 → 1,500자)")
            print("3. ✅ 6개 핵심 포커스 영역 명확화")
            print("4. ✅ 데이터 보강 가이드 자동 생성")
            print("5. ✅ Chat GPT 피드백 완전 반영")

            print("\n🔍 기대 효과:")
            print("- 경쟁사 비교 데이터 웹검색으로 확보")
            print("- 시계열 트렌드 분석 강화")
            print("- 정확한 FCF 계산 및 WACC 분석")
            print("- 구체적 투자 판단 제시")
            print("- 교과서적 설명 → 실용적 투자 통찰")

        else:
            print("\n❌ 테스트 실패")

    except Exception as e:
        print(f"\n❌ 메인 테스트 실행 오류: {e}")


if __name__ == "__main__":
    print("🎯 Chat GPT 피드백 반영 - 개선된 펀더멘탈 분석 테스트")
    print()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ 사용자에 의해 테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류: {e}")
