#!/usr/bin/env python3
"""
최신 분석 결과 확인 스크립트
Chat GPT 피드백 반영 효과 평가
"""

import json
import os
from datetime import datetime


def check_latest_result():
    """최신 분석 결과 확인"""

    # 최신 파일 찾기 (오늘 날짜 기준)
    results_dir = "results"
    files = [
        f
        for f in os.listdir(results_dir)
        if f.endswith(".json") and "005930" in f and "20250625" in f
    ]
    files.sort(reverse=True)

    if not files:
        print("❌ 분석 결과 파일을 찾을 수 없습니다.")
        return

    latest_file = files[0]
    print(f"📄 최신 분석 결과: {latest_file}")

    # JSON 로드
    with open(os.path.join(results_dir, latest_file), "r", encoding="utf-8") as f:
        data = json.load(f)

    print("\n🔍 분석 결과 구조:")
    print(f"  - 주요 키: {list(data.keys())}")

    # CrewAI 분석 확인
    crewai_analysis = data.get("crewai_detailed_analysis", {})
    if crewai_analysis:
        print(f"  - CrewAI 분석 키: {list(crewai_analysis.keys())}")

        # 개별 전문가 분석 확인 (직접 접근)
        individual_analyses = crewai_analysis.get("individual_expert_analyses", [])
        if individual_analyses:
            print(f"  - 개별 전문가 수: {len(individual_analyses)}명")

            # 펀더멘탈 분석가 찾기
            fundamental_analysis = None
            for analysis in individual_analyses:
                expert_name = analysis.get("expert_name", "")
                print(f"    • {expert_name}")

                if "펀더멘털" in expert_name or "펀더멘탈" in expert_name:
                    fundamental_analysis = analysis

            # 펀더멘탈 분석 상세 확인
            if fundamental_analysis:
                print("\n🎯 펀더멘탈 분석가 결과 분석:")

                analysis_result = fundamental_analysis.get("analysis_result", "")
                tool_calls_info = fundamental_analysis.get("tool_calls_info", "")

                # Chat GPT 피드백 반영 체크
                improvements_check = {
                    "웹검색_사용": "🌐" in tool_calls_info
                    or "웹검색" in analysis_result,
                    "경쟁사_비교": "경쟁사" in analysis_result
                    or "TSMC" in analysis_result
                    or "SK하이닉스" in analysis_result,
                    "시계열_분석": "3년" in analysis_result
                    or "2021" in analysis_result
                    or "트렌드" in analysis_result,
                    "FCF_정확성": "영업현금흐름" in analysis_result
                    and "자본적지출" in analysis_result,
                    "WACC_분석": "WACC" in analysis_result
                    or "자본비용" in analysis_result,
                    "구체적_수치": "%" in analysis_result
                    and ("위" in analysis_result or "순위" in analysis_result),
                    "투자_판단": "사야" in analysis_result
                    or "기다려야" in analysis_result
                    or "피해야" in analysis_result,
                    "모호한_표현_제거": not (
                        "양호" in analysis_result
                        or "안정적" in analysis_result
                        or "긍정적" in analysis_result
                    ),
                }

                print("📋 Chat GPT 피드백 반영 체크:")
                improved_count = 0
                for check_item, is_improved in improvements_check.items():
                    status = "✅" if is_improved else "❌"
                    print(
                        f"  {status} {check_item}: {'반영됨' if is_improved else '미흡'}"
                    )
                    if is_improved:
                        improved_count += 1

                improvement_score = (improved_count / len(improvements_check)) * 100
                print(
                    f"\n📊 전체 개선도: {improvement_score:.1f}% ({improved_count}/{len(improvements_check)})"
                )

                # 분석 결과 길이 및 품질
                print(f"\n📄 분석 결과 품질:")
                print(f"  - 분석 결과 길이: {len(analysis_result):,}자")
                print(
                    f"  - 도구 사용 정보: {tool_calls_info if tool_calls_info else '없음'}"
                )

                # 주요 키워드 빈도 확인
                keywords = {
                    "ROE": analysis_result.count("ROE"),
                    "ROIC": analysis_result.count("ROIC"),
                    "FCF": analysis_result.count("FCF"),
                    "경쟁사": analysis_result.count("경쟁사"),
                    "WACC": analysis_result.count("WACC"),
                    "목표주가": analysis_result.count("목표주가"),
                }

                print(f"  - 주요 키워드 언급 빈도:")
                for keyword, count in keywords.items():
                    print(f"    • {keyword}: {count}회")

                # 분석 결과 미리보기
                print(f"\n📖 분석 결과 미리보기 (처음 300자):")
                print("-" * 50)
                print(
                    analysis_result[:300] + "..."
                    if len(analysis_result) > 300
                    else analysis_result
                )

                # 종합 평가
                if improvement_score >= 80:
                    print(f"\n🎉 우수한 개선 결과! (개선도: {improvement_score:.1f}%)")
                elif improvement_score >= 60:
                    print(f"\n👍 양호한 개선 결과 (개선도: {improvement_score:.1f}%)")
                else:
                    print(f"\n⚠️ 추가 개선 필요 (개선도: {improvement_score:.1f}%)")

                    # 개선 필요 항목
                    not_improved = [
                        item
                        for item, improved in improvements_check.items()
                        if not improved
                    ]
                    print("🔧 개선 필요 항목:")
                    for item in not_improved:
                        print(f"  - {item}")

            else:
                print("❌ 펀더멘탈 분석가 결과를 찾을 수 없습니다.")

        else:
            print("❌ 전문가 분석 결과가 없습니다.")

    else:
        print("❌ CrewAI 분석 결과가 없습니다.")


if __name__ == "__main__":
    print("🔍 Chat GPT 피드백 반영 효과 분석")
    print("=" * 50)
    check_latest_result()
