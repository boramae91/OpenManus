#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 OpenManus 주식 분석 대시보드 (Enhanced Version)

기존 대시보드를 확장하여 전문가 분석 통합 도구를 활용한 UI 개선 버전입니다.
각 전문가별 분석 결과를 시각적으로 구분하여 표시하고, 위험 신호와 추천 메시지를 강조하여 보여줍니다.

주요 개선사항:
1. 🎯 전문가별 분석 결과 시각화 - 각 전문가의 분석을 카드 형태로 구분 표시
2. ⚠️ 위험 신호 강조 표시 - 리스크 전문가가 감지한 위험 신호를 눈에 띄게 표시
3. 💡 종합 추천 메시지 - 모든 전문가의 의견을 종합한 투자 추천
4. 📊 전문가 협력 구조 시각화 - 각 전문가가 어떻게 협력하는지 보여줌
"""

import asyncio
import glob
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit_lottie
import yfinance as yf
from PIL import Image
from plotly.subplots import make_subplots
from streamlit_extras.colored_header import colored_header
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_option_menu import option_menu

# 🤖 OpenManus 시스템 연결
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.tool.expert_analysis_integration import ExpertAnalysisIntegration
from app.utils.performance_monitor import get_performance_monitor
from enhanced_main import EnhancedStockAnalysisSystem

# 🎯 페이지 설정
st.set_page_config(
    page_title="🚀 OpenManus 전문가 분석 대시보드",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 🎨 CSS 스타일 설정 - 전문가별 색상 구분
st.markdown(
    """
<style>
    /* 전문가별 카드 색상 */
    .expert-card-fundamental {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .expert-card-technical {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .expert-card-valuation {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .expert-card-industry {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .expert-card-risk {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .expert-card-footnote {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #333;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* 위험 신호 강조 */
    .risk-warning {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 5px solid #c44569;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }

    /* 종합 추천 메시지 */
    .comprehensive-recommendation {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        margin: 2rem 0;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    }

    /* 전문가 협력 구조 시각화 */
    .expert-collaboration {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 1rem;
        margin: 2rem 0;
        border: 2px solid #e9ecef;
    }
</style>
""",
    unsafe_allow_html=True,
)


class EnhancedDashboardManager:
    """
    개선된 대시보드 관리 클래스

    전문가 분석 통합 도구를 활용하여 더 상세하고 시각적인 분석 결과를 제공합니다.
    """

    def __init__(self):
        """대시보드 매니저 초기화"""
        self.analysis_system = None
        self.expert_integration = None
        self.results_dir = "results"

        # 세션 상태 초기화
        if "analysis_in_progress" not in st.session_state:
            st.session_state.analysis_in_progress = False
        if "current_analysis_result" not in st.session_state:
            st.session_state.current_analysis_result = None
        if "expert_analysis_result" not in st.session_state:
            st.session_state.expert_analysis_result = None

    def load_systems(self):
        """분석 시스템과 전문가 통합 도구를 로드"""
        if self.analysis_system is None:
            with st.spinner("🤖 OpenManus 분석 시스템을 준비하고 있어요..."):
                try:
                    self.analysis_system = EnhancedStockAnalysisSystem()
                    st.success("✅ 분석 시스템 준비 완료!")
                except Exception as e:
                    st.error(f"❌ 분석 시스템 로드 실패: {str(e)}")
                    return False

        if self.expert_integration is None:
            with st.spinner("🎯 전문가 분석 통합 도구를 준비하고 있어요..."):
                try:
                    self.expert_integration = ExpertAnalysisIntegration()
                    st.success("✅ 전문가 통합 도구 준비 완료!")
                except Exception as e:
                    st.error(f"❌ 전문가 통합 도구 로드 실패: {str(e)}")
                    return False

        return True

    def get_saved_results(self) -> List[Dict]:
        """저장된 분석 결과 파일들을 가져오기"""
        results = []
        if not os.path.exists(self.results_dir):
            return results

        json_files = glob.glob(os.path.join(self.results_dir, "*.json"))
        for file_path in json_files:
            try:
                file_stat = os.stat(file_path)
                filename = os.path.basename(file_path)
                parts = filename.split("-")

                stock_code = "알 수 없음"
                analysis_type = "일반"

                if len(parts) >= 3:
                    stock_code = parts[2].split("_")[0]
                if len(parts) >= 4:
                    analysis_type = parts[3]

                results.append(
                    {
                        "filename": filename,
                        "filepath": file_path,
                        "stock_code": stock_code,
                        "analysis_type": analysis_type,
                        "file_size": file_stat.st_size,
                        "created_time": datetime.fromtimestamp(file_stat.st_mtime),
                        "size_mb": round(file_stat.st_size / (1024 * 1024), 2),
                    }
                )
            except Exception:
                continue

        results.sort(key=lambda x: x["created_time"], reverse=True)
        return results


# 🎯 전역 대시보드 매니저 인스턴스 생성
dashboard = EnhancedDashboardManager()


def show_expert_analysis_cards(expert_analyses: Dict[str, Any]):
    """
    각 전문가별 분석 결과를 카드 형태로 표시

    Args:
        expert_analyses: 전문가별 분석 결과 딕셔너리
    """
    st.subheader("🎯 전문가별 상세 분석 결과")

    # 2x3 그리드로 카드 배치
    col1, col2 = st.columns(2)

    with col1:
        # 펀더멘털 전문가
        if "fundamental" in expert_analyses and expert_analyses["fundamental"].get(
            "success"
        ):
            with st.container():
                st.markdown(
                    '<div class="expert-card-fundamental">', unsafe_allow_html=True
                )
                st.markdown("### 📊 펀더멘털 전문가")
                result = expert_analyses["fundamental"]
                st.write(f"**요약:** {result.get('summary', '분석 완료')}")

                # ROIC 분석 결과 표시
                if "roic_analysis" in result and result["roic_analysis"].get("success"):
                    roic = result["roic_analysis"].get("roic", 0)
                    st.metric("ROIC", f"{roic:.2f}%")

                # ROE 분석 결과 표시
                if "roe_analysis" in result and result["roe_analysis"].get("success"):
                    roe = result["roe_analysis"].get("roe", 0)
                    st.metric("ROE", f"{roe:.2f}%")

                st.markdown("</div>", unsafe_allow_html=True)

        # 기술적 전문가
        if "technical" in expert_analyses and expert_analyses["technical"].get(
            "success"
        ):
            with st.container():
                st.markdown(
                    '<div class="expert-card-technical">', unsafe_allow_html=True
                )
                st.markdown("### 📈 기술적 전문가")
                result = expert_analyses["technical"]
                st.write(f"**요약:** {result.get('summary', '분석 완료')}")

                # 기술적 지표 표시
                if "technical_indicators" in result:
                    indicators = result["technical_indicators"]
                    if isinstance(indicators, dict):
                        for key, value in list(indicators.items())[
                            :3
                        ]:  # 상위 3개만 표시
                            if isinstance(value, (int, float)):
                                st.metric(key, f"{value:.2f}")

                st.markdown("</div>", unsafe_allow_html=True)

        # 밸류에이션 전문가
        if "valuation" in expert_analyses and expert_analyses["valuation"].get(
            "success"
        ):
            with st.container():
                st.markdown(
                    '<div class="expert-card-valuation">', unsafe_allow_html=True
                )
                st.markdown("### 💰 밸류에이션 전문가")
                result = expert_analyses["valuation"]
                st.write(f"**요약:** {result.get('summary', '분석 완료')}")

                # DCF 분석 결과 표시
                if "dcf_analysis" in result and result["dcf_analysis"].get("success"):
                    dcf_value = result["dcf_analysis"].get("dcf_value", 0)
                    st.metric("DCF 가치", f"{dcf_value:,.0f}원")

                st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        # 산업 전문가
        if "industry" in expert_analyses and expert_analyses["industry"].get("success"):
            with st.container():
                st.markdown(
                    '<div class="expert-card-industry">', unsafe_allow_html=True
                )
                st.markdown("### 🏭 산업 전문가")
                result = expert_analyses["industry"]
                st.write(f"**요약:** {result.get('summary', '분석 완료')}")

                # 산업 구조 분석 결과 표시
                if "industry_structure" in result:
                    structure = result["industry_structure"]
                    if structure.get("success"):
                        attractiveness = structure.get("overall_assessment", {}).get(
                            "attractiveness_level", "알 수 없음"
                        )
                        st.metric("산업 매력도", attractiveness)

                # 위험 신호 표시
                if "risk_signals" in result and result["risk_signals"]:
                    st.write("⚠️ **위험 신호:**")
                    for signal in result["risk_signals"][:2]:  # 상위 2개만 표시
                        st.write(f"• {signal}")

                st.markdown("</div>", unsafe_allow_html=True)

        # 리스크 전문가
        if "risk" in expert_analyses and expert_analyses["risk"].get("success"):
            with st.container():
                st.markdown('<div class="expert-card-risk">', unsafe_allow_html=True)
                st.markdown("### ⚠️ 리스크 전문가")
                result = expert_analyses["risk"]
                st.write(f"**요약:** {result.get('summary', '분석 완료')}")

                # 전체 위험도 표시
                overall_risk = result.get("overall_risk_level", "알 수 없음")
                st.metric("전체 위험도", overall_risk)

                # 외부 위험 신호 표시
                if "extra_risks" in result and result["extra_risks"]:
                    st.write("🚨 **외부 위험 신호:**")
                    for risk in result["extra_risks"][:2]:  # 상위 2개만 표시
                        st.write(f"• {risk}")

                st.markdown("</div>", unsafe_allow_html=True)

        # 주석 전문가
        if "footnote" in expert_analyses and expert_analyses["footnote"].get("success"):
            with st.container():
                st.markdown(
                    '<div class="expert-card-footnote">', unsafe_allow_html=True
                )
                st.markdown("### 📝 주석 전문가")
                result = expert_analyses["footnote"]
                st.write(f"**요약:** {result.get('summary', '분석 완료')}")

                # 위험 신호 표시
                if "risks" in result and result["risks"]:
                    st.write("⚠️ **감지된 위험:**")
                    for risk in result["risks"][:2]:  # 상위 2개만 표시
                        st.write(f"• {risk}")

                # 정책 변경 표시
                if "policy_changes" in result and result["policy_changes"]:
                    st.write("📋 **정책 변경:**")
                    for change in result["policy_changes"][:1]:  # 상위 1개만 표시
                        st.write(f"• {change}")

                st.markdown("</div>", unsafe_allow_html=True)


def show_risk_warnings(expert_analyses: Dict[str, Any]):
    """
    위험 신호를 강조하여 표시

    Args:
        expert_analyses: 전문가별 분석 결과 딕셔너리
    """
    risk_signals = []

    # 각 전문가에서 위험 신호 수집
    if "risk" in expert_analyses and expert_analyses["risk"].get("success"):
        risk_result = expert_analyses["risk"]
        if "extra_risks" in risk_result:
            risk_signals.extend(risk_result["extra_risks"])

    if "footnote" in expert_analyses and expert_analyses["footnote"].get("success"):
        footnote_result = expert_analyses["footnote"]
        if "risks" in footnote_result:
            risk_signals.extend(footnote_result["risks"])

    if "industry" in expert_analyses and expert_analyses["industry"].get("success"):
        industry_result = expert_analyses["industry"]
        if "risk_signals" in industry_result:
            risk_signals.extend(industry_result["risk_signals"])

    # 위험 신호가 있으면 강조 표시
    if risk_signals:
        st.markdown('<div class="risk-warning">', unsafe_allow_html=True)
        st.markdown("### 🚨 주의! 위험 신호 감지")
        st.write(f"**총 {len(risk_signals)}건의 위험 신호가 감지되었습니다:**")
        for i, signal in enumerate(risk_signals[:5], 1):  # 상위 5개만 표시
            st.write(f"{i}. {signal}")
        if len(risk_signals) > 5:
            st.write(f"... 외 {len(risk_signals) - 5}건")
        st.markdown("</div>", unsafe_allow_html=True)


def show_comprehensive_recommendations(recommendations: List[str]):
    """
    종합 추천 메시지를 강조하여 표시

    Args:
        recommendations: 종합 추천 메시지 리스트
    """
    if recommendations:
        st.markdown(
            '<div class="comprehensive-recommendation">', unsafe_allow_html=True
        )
        st.markdown("### 🎯 종합 투자 추천")
        for i, rec in enumerate(recommendations, 1):
            st.write(f"**{i}.** {rec}")
        st.markdown("</div>", unsafe_allow_html=True)


def show_expert_collaboration_diagram():
    """
    전문가 협력 구조를 시각적으로 표시
    """
    st.markdown('<div class="expert-collaboration">', unsafe_allow_html=True)
    st.markdown("### 🤝 전문가 협력 구조")

    # 전문가별 역할 설명
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**📊 펀더멘털 전문가**")
        st.write("• 재무 건전성 분석")
        st.write("• 수익성 지표 평가")
        st.write("• 인과관계 분석")

        st.markdown("**📈 기술적 전문가**")
        st.write("• 주가 패턴 분석")
        st.write("• 기술적 지표 평가")
        st.write("• 추세 및 지지/저항")

    with col2:
        st.markdown("**💰 밸류에이션 전문가**")
        st.write("• 기업 가치 평가")
        st.write("• DCF 모델 분석")
        st.write("• 상대가치 분석")

        st.markdown("**🏭 산업 전문가**")
        st.write("• 산업 구조 분석")
        st.write("• 경쟁 구도 평가")
        st.write("• 산업 생명주기")

    with col3:
        st.markdown("**⚠️ 리스크 전문가**")
        st.write("• 종합 위험 평가")
        st.write("• 외부 위험 신호 감지")
        st.write("• 위험도 분류")

        st.markdown("**📝 주석 전문가**")
        st.write("• 중요 주석 추출")
        st.write("• 위험 신호 감지")
        st.write("• 정책 변경 분석")

    st.markdown(
        "**🔄 협력 방식:** 산업/주석 전문가의 위험 신호를 리스크 전문가가 종합하여 최종 위험도를 결정합니다."
    )
    st.markdown("</div>", unsafe_allow_html=True)


def show_enhanced_analysis_result(result: Dict[str, Any]):
    """
    개선된 분석 결과 표시

    Args:
        result: 분석 결과 딕셔너리
    """
    if not result or not result.get("success"):
        st.error("❌ 분석 결과를 불러올 수 없습니다.")
        return

    # 1️⃣ 성능 경고 알림 표시
    # 분석이 끝난 후, 성능 모니터에서 최신 분석 리포트를 가져와요
    perf_monitor = get_performance_monitor()
    if perf_monitor.analysis_history:
        last_report = perf_monitor.analysis_history[-1]
        # 임계값 초과 경고를 직접 체크해서 알림으로 보여줘요
        warnings = []
        if last_report.total_duration > perf_monitor.thresholds["max_duration_seconds"]:
            warnings.append(
                f"⚠️ 분석 시간이 너무 오래 걸렸어요! ({last_report.total_duration:.1f}초)"
            )
        if last_report.peak_memory_mb > perf_monitor.thresholds["max_memory_mb"]:
            warnings.append(
                f"⚠️ 메모리 사용량이 많아요! ({last_report.peak_memory_mb:.1f}MB)"
            )
        if last_report.api_calls > perf_monitor.thresholds["max_api_calls"]:
            warnings.append(f"⚠️ API 호출이 너무 많아요! ({last_report.api_calls}회)")
        if last_report.estimated_cost_usd > perf_monitor.thresholds["max_cost_usd"]:
            warnings.append(
                f"⚠️ 예상 비용이 높아요! (${last_report.estimated_cost_usd:.4f})"
            )
        for w in warnings:
            st.toast(w, icon="⚠️")

    # 2️⃣ 전문가 위험 신호 실시간 알림
    # 리스크, 주석, 산업 전문가의 위험 신호를 찾아서 경고로 보여줘요
    expert_analyses = result.get("expert_analyses", {})
    # 리스크 전문가
    if "risk" in expert_analyses and expert_analyses["risk"].get("extra_risks"):
        for risk in expert_analyses["risk"]["extra_risks"]:
            st.warning(f"🚨 리스크 전문가 경고: {risk}")
    # 주석 전문가
    if "footnote" in expert_analyses and expert_analyses["footnote"].get("risks"):
        for risk in expert_analyses["footnote"]["risks"]:
            st.warning(f"📝 주석 전문가 위험: {risk}")
    # 산업 전문가
    if "industry" in expert_analyses and expert_analyses["industry"].get(
        "risk_signals"
    ):
        for risk in expert_analyses["industry"]["risk_signals"]:
            st.warning(f"🏭 산업 전문가 위험: {risk}")

    # 제목 표시
    st.title("🎯 전문가 종합 분석 결과")

    # 기본 정보 표시
    if "user_prompt" in result:
        st.info(f"**분석 요청:** {result['user_prompt']}")

    # 전문가 협력 구조 표시
    show_expert_collaboration_diagram()

    # 위험 신호 강조 표시
    if "expert_analyses" in result:
        show_risk_warnings(result["expert_analyses"])

    # 전문가별 분석 결과 카드 표시
    if "expert_analyses" in result:
        show_expert_analysis_cards(result["expert_analyses"])

    # 종합 추천 메시지 표시
    if "recommendations" in result:
        show_comprehensive_recommendations(result["recommendations"])

    # 상세 결과 접기/펼치기
    with st.expander("📋 상세 분석 결과 보기"):
        st.json(result)


def evaluate_quality(result: Dict[str, Any]) -> int:
    """
    분석 결과의 품질을 자동으로 평가해요
    - 구체성, 위험 신호, 추천 메시지, 분석 길이 등 다양한 기준으로 점수를 매겨요
    Args:
        result: 분석 결과 딕셔너리
    Returns:
        int: 품질 점수 (0~100)
    """
    if not result or not result.get("success"):
        return 0
    score = 50  # 기본 점수
    # 구체적인 추천 메시지가 있으면 점수 추가
    if result.get("recommendations") and len(result["recommendations"]) >= 2:
        score += 10
    # 위험 신호가 잘 감지되면 점수 추가
    expert_analyses = result.get("expert_analyses", {})
    risk_count = 0
    for key in ["risk", "footnote", "industry"]:
        if key in expert_analyses:
            risks = (
                expert_analyses[key].get("extra_risks")
                or expert_analyses[key].get("risks")
                or expert_analyses[key].get("risk_signals")
            )
            if risks and isinstance(risks, list) and len(risks) > 0:
                score += 5
                risk_count += len(risks)
    # 분석 결과가 길면 점수 추가
    if len(str(result)) > 3000:
        score += 5
    # 위험 신호가 너무 많으면 감점
    if risk_count > 5:
        score -= 5
    # 최대/최소 보정
    return max(0, min(100, score))


def run_ab_test(user_input: str, options: Dict):
    """
    두 가지 분석 방식을 동시에 실행해서 결과를 비교해요!
    Args:
        user_input: 사용자 입력
        options: 분석 옵션
    Returns:
        Dict: A/B 결과와 품질 점수
    """
    # A안: 기존 방식 (예시로 기존 프롬프트 버전)
    result_A = run_enhanced_analysis(user_input, options)
    # B안: 개선 방식 (예시로 옵션에 'improved' 추가)
    improved_options = dict(options)
    improved_options["prompt_version"] = "improved"
    result_B = run_enhanced_analysis(user_input, improved_options)
    # 품질 평가
    score_A = evaluate_quality(result_A)
    score_B = evaluate_quality(result_B)
    return {
        "A": {"result": result_A, "score": score_A},
        "B": {"result": result_B, "score": score_B},
    }


def show_ab_test_results(ab_results: Dict[str, Any]):
    """
    A/B 테스트 결과를 나란히 비교해서 보여줘요!
    Args:
        ab_results: A/B 결과와 점수
    """
    st.markdown("## 🆚 A/B 테스트 결과 비교")
    colA, colB = st.columns(2)
    with colA:
        st.subheader("A안 (기존)")
        st.write(f"품질 점수: {ab_results['A']['score']}점")
        show_enhanced_analysis_result(ab_results["A"]["result"])
    with colB:
        st.subheader("B안 (개선)")
        st.write(f"품질 점수: {ab_results['B']['score']}점")
        show_enhanced_analysis_result(ab_results["B"]["result"])
    # 최적안 추천
    if ab_results["A"]["score"] > ab_results["B"]["score"]:
        st.success("✅ A안(기존 방식)이 더 우수해요!")
    elif ab_results["A"]["score"] < ab_results["B"]["score"]:
        st.success("✅ B안(개선 방식)이 더 우수해요!")
    else:
        st.info("⚖️ 두 방식의 품질이 비슷해요!")


def run_enhanced_analysis(user_input: str, options: Dict):
    """
    개선된 분석 실행 함수

    Args:
        user_input: 사용자 입력
        options: 분석 옵션
    """
    if not dashboard.load_systems():
        return None

    try:
        # 기존 분석 시스템으로 기본 분석 실행
        with st.spinner("🔍 기본 분석을 실행하고 있어요..."):
            result = asyncio.run(
                dashboard.analysis_system.run_enhanced_analysis(user_input)
            )

        if not result or not result.get("success"):
            st.error("❌ 기본 분석에 실패했습니다.")
            return None

        # 전문가 통합 분석 실행
        with st.spinner("🎯 전문가 종합 분석을 실행하고 있어요..."):
            # 샘플 데이터 준비 (실제로는 result에서 추출)
            sample_data = {
                "financial_data": {
                    "net_income": 1000,
                    "total_equity": 5000,
                    "total_liabilities": 3000,
                    "revenue": 12000,
                    "total_assets": 8000,
                    "debt_ratio": 120,
                    "current_ratio": 150,
                    "interest_coverage": 4,
                },
                "market_data": {
                    "market_share": 0.2,
                    "volatility": 18,
                    "exchange_rate": 1250,
                    "interest_rate": 3.5,
                    "price": 50000,
                    "volume": 100000,
                },
                "company_data": {"name": "샘플회사", "market_share": 0.2},
                "industry_data": {
                    "market_shares": [0.2, 0.15, 0.1, 0.05],
                    "average_roa": 8,
                    "average_roe": 12,
                    "average_margin": 15,
                    "competitors": [
                        {"name": "경쟁사1", "market_share": 0.15},
                        {"name": "경쟁사2", "market_share": 0.1},
                    ],
                    "historical_data": [
                        {"revenue": 10000},
                        {"revenue": 11000},
                        {"revenue": 12000},
                    ],
                    "market_penetration": 60,
                    "growth_rate": 5,
                    "consolidation_level": 30,
                    "rd_intensity": 6,
                    "patent_growth": 12,
                    "technology_cycle": "중간",
                    "disruption_risk": "낮음",
                },
                "operation_data": {
                    "supply_chain": "정상",
                    "workforce": "안정",
                    "it_system": "안정",
                },
                "footnotes": [
                    {
                        "title": "회계정책 변경",
                        "content": "회계정책이 2024년부터 변경되었습니다.",
                    },
                    {"title": "소송", "content": "현재 진행 중인 소송이 있습니다."},
                    {"title": "일반사항", "content": "특별한 위험은 없습니다."},
                ],
                "timestamp": datetime.now().isoformat(),
            }

            expert_result = dashboard.expert_integration.perform_comprehensive_analysis(
                sample_data
            )

        # 결과를 세션에 저장
        st.session_state.current_analysis_result = result
        st.session_state.expert_analysis_result = expert_result

        return expert_result

    except Exception as e:
        st.error(f"❌ 분석 실행 중 오류가 발생했습니다: {str(e)}")
        return None


def main():
    """메인 함수"""
    st.title("🚀 OpenManus 전문가 분석 대시보드")

    # 사이드바 메뉴
    with st.sidebar:
        st.title("📋 메뉴")
        selected = option_menu(
            "메뉴 선택",
            ["🏠 홈", "🔍 새로운 분석", "📊 분석 결과", "⚙️ 설정"],
            icons=["house", "search", "graph-up", "gear"],
            menu_icon="cast",
            default_index=0,
        )

    # 메뉴에 따른 페이지 표시
    if selected == "🏠 홈":
        show_home_page()
    elif selected == "🔍 새로운 분석":
        show_analysis_page()
    elif selected == "📊 분석 결과":
        show_results_page()
    elif selected == "⚙️ 설정":
        show_settings_page()


def show_home_page():
    """홈 페이지"""
    st.markdown("## 🏠 환영합니다!")
    st.write("OpenManus 전문가 분석 대시보드에 오신 것을 환영합니다!")
    st.write("이 대시보드는 6명의 AI 전문가가 협력하여 주식 분석을 수행합니다.")

    # 전문가 소개
    st.markdown("### 🎯 AI 전문가 팀")
    experts = [
        {"name": "📊 펀더멘털 전문가", "role": "재무 건전성과 수익성 분석"},
        {"name": "📈 기술적 전문가", "role": "주가 패턴과 시장 동향 분석"},
        {"name": "💰 밸류에이션 전문가", "role": "기업 가치와 투자 가치 평가"},
        {"name": "🏭 산업 전문가", "role": "산업 구조와 경쟁 환경 분석"},
        {"name": "⚠️ 리스크 전문가", "role": "종합 위험 평가 및 신호 감지"},
        {"name": "📝 주석 전문가", "role": "중요 주석과 위험 신호 분석"},
    ]

    for expert in experts:
        st.info(f"**{expert['name']}**: {expert['role']}")


def show_analysis_page():
    """분석 페이지"""
    st.markdown("## 🔍 새로운 주식 분석")

    # 사용자 입력
    user_input = st.text_area(
        "분석하고 싶은 종목을 입력해주세요",
        placeholder="예: 삼성전자, 005930, 삼성전자 주가 전망 등",
        height=100,
    )

    # 분석 옵션
    st.markdown("### ⚙️ 분석 옵션")
    col1, col2 = st.columns(2)
    with col1:
        analysis_depth = st.selectbox(
            "분석 깊이", ["기본", "상세", "심화"], help="분석의 깊이를 선택하세요"
        )
    with col2:
        include_pdf = st.checkbox(
            "사업보고서 포함", value=True, help="사업보고서 분석을 포함할지 선택하세요"
        )

    # 분석 실행 버튼
    if st.button("🚀 분석 시작", type="primary"):
        if not user_input.strip():
            st.warning("⚠️ 분석할 종목을 입력해주세요.")
            return
        st.session_state.analysis_in_progress = True
        options = {"analysis_depth": analysis_depth, "include_pdf": include_pdf}
        result = run_enhanced_analysis(user_input, options)
        if result:
            st.session_state.analysis_in_progress = False
            show_enhanced_analysis_result(result)
        else:
            st.session_state.analysis_in_progress = False
            st.error("❌ 분석에 실패했습니다.")

    # A/B 테스트 실행 버튼
    if st.button("🆚 A/B 테스트 실행", type="secondary"):
        if not user_input.strip():
            st.warning("⚠️ 분석할 종목을 입력해주세요.")
            return
        st.session_state.analysis_in_progress = True
        options = {"analysis_depth": analysis_depth, "include_pdf": include_pdf}
        ab_results = run_ab_test(user_input, options)
        st.session_state.analysis_in_progress = False
        show_ab_test_results(ab_results)


def show_results_page():
    """결과 페이지"""
    st.markdown("## 📊 과거 분석 결과")

    # 저장된 결과 파일들 가져오기
    saved_results = dashboard.get_saved_results()

    if not saved_results:
        st.info("📝 아직 저장된 분석 결과가 없습니다.")
        return

    # 결과 파일 선택
    selected_file = st.selectbox(
        "분석 결과 선택",
        options=saved_results,
        format_func=lambda x: f"{x['stock_code']} - {x['analysis_type']} ({x['created_time'].strftime('%Y-%m-%d %H:%M')})",
    )

    if selected_file and st.button("📋 결과 보기"):
        try:
            with open(selected_file["filepath"], "r", encoding="utf-8") as f:
                result = json.load(f)

            show_enhanced_analysis_result(result)

        except Exception as e:
            st.error(f"❌ 결과 파일을 불러오는 중 오류가 발생했습니다: {str(e)}")


def show_settings_page():
    """설정 페이지"""
    st.markdown("## ⚙️ 설정")
    st.write("대시보드 설정을 관리할 수 있습니다.")

    # 시스템 정보
    st.markdown("### 🔧 시스템 정보")
    st.info("OpenManus 전문가 분석 대시보드 v2.0")
    st.write("• 6명의 AI 전문가가 협력하는 분석 시스템")
    st.write("• 실시간 위험 신호 감지 및 알림")
    st.write("• 시각적 분석 결과 표시")


if __name__ == "__main__":
    main()
