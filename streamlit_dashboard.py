#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 OpenManus 주식 분석 대시보드 (Streamlit Dashboard)

이 파일은 OpenManus 주식 분석 시스템을 웹 브라우저에서 쉽게 사용할 수 있도록 만든 대시보드입니다.
마치 카카오톡처럼 쉽게 사용할 수 있는 웹 인터페이스를 제공해요!

주요 기능:
1. 📊 새로운 주식 분석 실행 - 종목명이나 코드를 입력하면 자동으로 분석
2. 📈 분석 결과 시각화 - 예쁜 차트와 그래프로 결과 표시
3. 📚 과거 분석 결과 조회 - 이전에 분석한 결과들을 다시 볼 수 있음
4. 🎯 전문가 의견 표시 - AI 전문가들의 상세한 분석 내용

사용법:
1. 터미널에서 "streamlit run streamlit_dashboard.py" 명령어 실행
2. 웹 브라우저가 자동으로 열림 (http://localhost:8501)
3. 분석하고 싶은 종목을 입력하고 분석 버튼 클릭!
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

# 📦 웹 대시보드 만들기 위한 라이브러리들
import streamlit as st
import streamlit_lottie

# 📊 데이터 처리를 위한 라이브러리들
import yfinance as yf
from PIL import Image
from plotly.subplots import make_subplots
from streamlit_extras.colored_header import colored_header
from streamlit_extras.metric_cards import style_metric_cards

# 🎨 대시보드를 예쁘게 꾸미기 위한 라이브러리들
from streamlit_option_menu import option_menu

# 🤖 OpenManus 시스템 연결
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from enhanced_main import EnhancedStockAnalysisSystem

# 🎯 페이지 설정 - 웹 브라우저 탭에 표시될 제목과 아이콘 설정
st.set_page_config(
    page_title="🚀 OpenManus 주식 분석 대시보드",  # 브라우저 탭 제목
    page_icon="📊",  # 브라우저 탭 아이콘
    layout="wide",  # 화면을 넓게 사용
    initial_sidebar_state="expanded",  # 사이드바를 처음에 열어둠
)

# 🎨 CSS 스타일 설정 - 대시보드를 더 예쁘게 만들기
st.markdown(
    """
<style>
    /* 메인 제목 스타일 */
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #1f77b4;
    }

    /* 카드 스타일 */
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }

    /* 성공 메시지 스타일 */
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }

    /* 경고 메시지 스타일 */
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
    }
</style>
""",
    unsafe_allow_html=True,
)


class DashboardManager:
    """
    대시보드 관리 클래스

    이 클래스는 대시보드의 모든 기능을 관리하는 매니저 역할을 해요.
    마치 레스토랑의 매니저가 주방, 서빙, 계산을 모두 관리하는 것처럼,
    이 클래스가 분석 실행, 결과 표시, 파일 관리를 모두 담당해요!
    """

    def __init__(self):
        """대시보드 매니저 초기화 - 필요한 모든 준비 작업을 해요"""
        self.analysis_system = None  # 분석 시스템 (나중에 초기화)
        self.results_dir = "results"  # 결과 파일들이 저장된 폴더

        # 세션 상태 초기화 (웹 페이지가 새로고침되어도 정보가 유지되도록)
        if "analysis_in_progress" not in st.session_state:
            st.session_state.analysis_in_progress = False  # 분석 진행 중인지 여부
        if "current_analysis_result" not in st.session_state:
            st.session_state.current_analysis_result = None  # 현재 분석 결과
        if "selected_result_file" not in st.session_state:
            st.session_state.selected_result_file = None  # 선택된 결과 파일

    def load_analysis_system(self):
        """
        분석 시스템을 로드하는 함수

        OpenManus 분석 시스템을 메모리에 로드해요.
        처음에만 실행되고, 이후에는 캐시된 시스템을 사용해요.
        마치 프로그램을 처음 실행할 때만 로딩하는 것과 같아요!
        """
        if self.analysis_system is None:
            with st.spinner("🤖 OpenManus 분석 시스템을 준비하고 있어요..."):
                try:
                    self.analysis_system = EnhancedStockAnalysisSystem()
                    st.success("✅ 분석 시스템 준비 완료!")
                except Exception as e:
                    st.error(f"❌ 분석 시스템 로드 실패: {str(e)}")
                    return False
        return True

    def get_saved_results(self) -> List[Dict]:
        """
        저장된 분석 결과 파일들을 가져오는 함수

        results 폴더에 있는 모든 JSON 파일들을 찾아서
        파일 정보(이름, 크기, 날짜 등)를 리스트로 반환해요.
        """
        results = []

        if not os.path.exists(self.results_dir):
            return results

        # JSON 파일들 찾기
        json_files = glob.glob(os.path.join(self.results_dir, "*.json"))

        for file_path in json_files:
            try:
                # 파일 정보 수집
                file_stat = os.stat(file_path)
                file_size = file_stat.st_size
                file_time = datetime.fromtimestamp(file_stat.st_mtime)

                # 파일명에서 정보 추출 (예: json-agent-005930_KS_Equity-enhanced-...)
                filename = os.path.basename(file_path)
                parts = filename.split("-")

                stock_code = "알 수 없음"
                analysis_type = "일반"

                if len(parts) >= 3:
                    stock_code = parts[2].split("_")[0]  # 종목코드 추출
                if len(parts) >= 4:
                    analysis_type = parts[3]  # 분석 타입 추출

                results.append(
                    {
                        "filename": filename,
                        "filepath": file_path,
                        "stock_code": stock_code,
                        "analysis_type": analysis_type,
                        "file_size": file_size,
                        "created_time": file_time,
                        "size_mb": round(file_size / (1024 * 1024), 2),
                    }
                )

            except Exception as e:
                continue

        # 최신 파일 순으로 정렬
        results.sort(key=lambda x: x["created_time"], reverse=True)
        return results


# 🎯 전역 대시보드 매니저 인스턴스 생성
dashboard = DashboardManager()


def main():
    """
    메인 함수 - 대시보드의 시작점

    이 함수가 대시보드의 모든 것을 제어해요!
    사용자가 웹 페이지에 접속하면 가장 먼저 실행되는 함수입니다.
    """

    # 🎨 메인 제목 표시
    st.markdown(
        '<h1 class="main-title">🚀 OpenManus 주식 분석 대시보드</h1>',
        unsafe_allow_html=True,
    )

    # 📝 간단한 설명
    st.markdown(
        """
    <div style="text-align: center; margin-bottom: 2rem;">
        <p style="font-size: 1.2rem; color: #666;">
            AI 기반 종합 주식 분석 시스템으로 전문가 수준의 투자 분석을 받아보세요! 📈
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 🎯 사이드바 메뉴 생성
    with st.sidebar:
        st.image(
            "https://via.placeholder.com/200x100/1f77b4/white?text=OpenManus",
            caption="OpenManus 로고",
        )

        # 메뉴 선택
        selected_menu = option_menu(
            menu_title="메뉴",  # 메뉴 제목
            options=["🏠 홈", "🔍 새 분석", "📊 결과 조회", "⚙️ 설정"],  # 메뉴 옵션들
            icons=["house", "search", "bar-chart", "gear"],  # 아이콘들
            menu_icon="cast",  # 메뉴 아이콘
            default_index=0,  # 기본 선택 메뉴
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "orange", "font-size": "18px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                },
                "nav-link-selected": {"background-color": "#02ab21"},
            },
        )

    # 선택된 메뉴에 따라 다른 페이지 표시
    if selected_menu == "🏠 홈":
        show_home_page()
    elif selected_menu == "🔍 새 분석":
        show_analysis_page()
    elif selected_menu == "📊 결과 조회":
        show_results_page()
    elif selected_menu == "⚙️ 설정":
        show_settings_page()


def show_home_page():
    """
    홈 페이지를 표시하는 함수

    대시보드의 메인 페이지로, 시스템 상태와 최근 분석 결과를 보여줘요.
    사용자가 처음 접속했을 때 보게 되는 화면이에요!
    """

    # 📊 상태 카드들 표시
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # 전체 분석 결과 개수
        total_results = len(dashboard.get_saved_results())
        st.metric("총 분석 결과", f"{total_results}개", "누적 분석 건수")

    with col2:
        # 시스템 상태
        system_status = "정상" if dashboard.analysis_system else "준비 중"
        st.metric("시스템 상태", system_status, "OpenManus AI")

    with col3:
        # 오늘 분석 건수 (임시로 랜덤값 표시)
        import random

        today_count = random.randint(0, 10)
        st.metric("오늘 분석", f"{today_count}건", "금일 실행 건수")

    with col4:
        # 평균 분석 시간 (임시로 고정값 표시)
        st.metric("평균 분석 시간", "2.5분", "AI 처리 속도")

    # 📈 최근 분석 결과 미리보기
    st.subheader("📈 최근 분석 결과")

    recent_results = dashboard.get_saved_results()[:5]  # 최근 5개만

    if recent_results:
        for result in recent_results:
            with st.expander(
                f"📊 {result['stock_code']} - {result['analysis_type']} "
                f"({result['created_time'].strftime('%m/%d %H:%M')})"
            ):

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**종목코드**: {result['stock_code']}")
                    st.write(f"**분석 타입**: {result['analysis_type']}")
                with col2:
                    st.write(f"**파일 크기**: {result['size_mb']} MB")
                    st.write(
                        f"**생성 시간**: {result['created_time'].strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                with col3:
                    if st.button(f"자세히 보기", key=f"detail_{result['filename']}"):
                        st.session_state.selected_result_file = result["filepath"]
                        st.rerun()
    else:
        st.info(
            "📝 아직 분석 결과가 없습니다. '새 분석' 메뉴에서 첫 번째 분석을 시작해보세요!"
        )

    # 🎯 빠른 분석 실행
    st.subheader("🚀 빠른 분석 실행")

    col1, col2 = st.columns([3, 1])
    with col1:
        quick_input = st.text_input(
            "종목명 또는 종목코드를 입력하세요",
            placeholder="예: 삼성전자, 005930, AAPL",
        )
    with col2:
        st.write("")  # 공간 맞추기
        if st.button("🔍 분석 시작", type="primary"):
            if quick_input.strip():
                # 분석 페이지로 이동하면서 입력값 전달
                st.session_state.quick_analysis_input = quick_input.strip()
                st.rerun()
            else:
                st.warning("종목명 또는 종목코드를 입력해주세요!")


def show_analysis_page():
    """
    새 분석 페이지를 표시하는 함수

    사용자가 새로운 주식 분석을 실행할 수 있는 페이지예요.
    종목을 입력하고 분석 옵션을 선택한 후 분석을 시작할 수 있어요!
    """

    st.header("🔍 새로운 주식 분석")

    # 분석 입력 폼
    with st.form("analysis_form"):
        st.subheader("📝 분석 대상 입력")

        # 홈에서 빠른 분석으로 온 경우 입력값 자동 설정
        default_input = ""
        if hasattr(st.session_state, "quick_analysis_input"):
            default_input = st.session_state.quick_analysis_input
            del st.session_state.quick_analysis_input

        user_input = st.text_area(
            "분석하고 싶은 종목이나 질문을 입력하세요:",
            value=default_input,
            placeholder="예시:\n- 삼성전자 투자 의견 알려줘\n- 005930 재무분석\n- AAPL 주가 전망\n- 카카오 기술적 분석",
            height=100,
        )

        # 분석 옵션
        st.subheader("⚙️ 분석 옵션")

        col1, col2 = st.columns(2)
        with col1:
            analysis_depth = st.selectbox(
                "분석 깊이 선택:",
                ["표준 분석", "빠른 분석", "심층 분석"],
                help="분석의 상세 정도를 선택하세요. 깊이가 높을수록 시간이 더 걸려요.",
            )

        with col2:
            include_pdf = st.checkbox(
                "PDF 보고서 자동 분석",
                value=True,
                help="웹에서 PDF 보고서를 찾으면 자동으로 분석에 포함해요.",
            )

        # 고급 옵션 (접을 수 있는 형태)
        with st.expander("🔧 고급 옵션"):
            use_enhanced_dart = st.checkbox(
                "Enhanced DART API 사용",
                value=True,
                help="한국 상장기업의 공시 정보를 더 상세히 분석해요.",
            )

            enable_web_search = st.checkbox(
                "실시간 웹 검색",
                value=True,
                help="최신 뉴스와 정보를 웹에서 실시간으로 검색해요.",
            )

        # 분석 실행 버튼
        submitted = st.form_submit_button("🚀 분석 시작!", type="primary")

        if submitted:
            if user_input.strip():
                # 분석 실행
                run_analysis(
                    user_input.strip(),
                    {
                        "depth": analysis_depth,
                        "include_pdf": include_pdf,
                        "use_enhanced_dart": use_enhanced_dart,
                        "enable_web_search": enable_web_search,
                    },
                )
            else:
                st.error("❌ 분석할 종목이나 질문을 입력해주세요!")

    # 진행 중인 분석 표시
    if st.session_state.analysis_in_progress:
        show_analysis_progress()

    # 완료된 분석 결과 표시
    if st.session_state.current_analysis_result:
        show_analysis_result(st.session_state.current_analysis_result)


def run_analysis(user_input: str, options: Dict):
    """
    실제 분석을 실행하는 함수

    사용자가 입력한 내용과 옵션을 바탕으로 OpenManus 분석 시스템을 실행해요.
    분석이 진행되는 동안 진행 상황을 실시간으로 보여줘요!

    Args:
        user_input (str): 사용자가 입력한 분석 대상 (종목명, 질문 등)
        options (Dict): 분석 옵션들 (깊이, PDF 포함 여부 등)
    """

    # 분석 시작 상태로 변경
    st.session_state.analysis_in_progress = True
    st.session_state.current_analysis_result = None

    # 분석 시스템 로드
    if not dashboard.load_analysis_system():
        st.session_state.analysis_in_progress = False
        return

    # 분석 진행 상황 컨테이너 생성
    progress_container = st.container()

    with progress_container:
        st.success("✅ 분석을 시작했습니다!")
        progress_bar = st.progress(0)
        status_text = st.empty()

        # 분석 실행 (비동기 함수를 동기적으로 실행)
        try:
            status_text.text("🔍 종목 감지 중...")
            progress_bar.progress(20)

            # 실제 분석 실행
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            status_text.text("📊 재무데이터 수집 중...")
            progress_bar.progress(40)

            result = loop.run_until_complete(
                dashboard.analysis_system.run_enhanced_analysis(user_input)
            )

            status_text.text("🤖 AI 전문가 분석 중...")
            progress_bar.progress(80)

            # 분석 완료
            progress_bar.progress(100)
            status_text.text("✅ 분석 완료!")

            # 결과 저장
            st.session_state.current_analysis_result = result
            st.session_state.analysis_in_progress = False

            st.success("🎉 분석이 성공적으로 완료되었습니다!")

        except Exception as e:
            st.error(f"❌ 분석 중 오류가 발생했습니다: {str(e)}")
            st.session_state.analysis_in_progress = False
            status_text.text("❌ 분석 실패")


def show_analysis_progress():
    """
    분석 진행 상황을 표시하는 함수

    분석이 실행되는 동안 사용자에게 현재 어떤 작업이 진행되고 있는지 보여줘요.
    진행률과 함께 각 단계별 상태를 시각적으로 표현해요!
    """

    st.subheader("🔄 분석 진행 상황")

    # 진행 단계들
    steps = [
        "🔍 종목 감지",
        "📊 재무데이터 수집",
        "🌐 웹 정보 수집",
        "🤖 AI 전문가 분석",
        "📋 결과 정리",
    ]

    # 각 단계별 상태 표시
    for i, step in enumerate(steps):
        if i < 3:  # 진행 완료된 단계
            st.success(f"✅ {step}")
        elif i == 3:  # 현재 진행 중인 단계
            st.info(f"🔄 {step} (진행 중...)")
        else:  # 대기 중인 단계
            st.text(f"⏳ {step}")

    # 전체 진행률
    overall_progress = st.progress(60)
    st.text("전체 진행률: 60%")

    # 실시간 로그 (시뮬레이션)
    with st.expander("📋 상세 로그 보기"):
        st.text_area(
            "실시간 로그:",
            value="[2025-01-03 14:30:25] 종목 감지 완료: 삼성전자 (005930)\n"
            "[2025-01-03 14:30:28] 재무데이터 수집 시작...\n"
            "[2025-01-03 14:30:35] yfinance 데이터 수집 완료\n"
            "[2025-01-03 14:30:40] DART API 데이터 수집 중...\n"
            "[2025-01-03 14:30:45] 웹 검색 시작...",
            height=200,
        )


def show_analysis_result(result: Dict):
    """
    분석 결과를 표시하는 함수

    완료된 분석 결과를 예쁘게 정리해서 사용자에게 보여줘요.
    차트, 테이블, 카드 등 다양한 방식으로 정보를 시각화해요!

    Args:
        result (Dict): 분석 결과 데이터
    """

    st.subheader("📊 분석 결과")

    if not result.get("success"):
        st.error(f"❌ 분석 실패: {result.get('error', '알 수 없는 오류')}")
        return

    # 기본 정보 표시
    stock_info = result.get("steps", {}).get("step1_stock_detection", {})
    if stock_info.get("detected"):

        # 종목 정보 카드
        st.markdown("### 📈 분석 대상")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("종목명", stock_info.get("stock_name", "알 수 없음"))
        with col2:
            st.metric("종목코드", stock_info.get("stock_code", "알 수 없음"))
        with col3:
            st.metric("섹터", stock_info.get("gics_sector", "알 수 없음"))

    # CrewAI 분석 결과 표시
    crewai_result = result.get("steps", {}).get(
        "step4_crewai_comprehensive_analysis", {}
    )
    if crewai_result and not crewai_result.get("error"):
        st.markdown("### 🤖 AI 전문가 종합 분석")

        # 전문가 의견 탭으로 구성
        expert_insights = crewai_result.get("expert_insights", {})
        individual_analyses = expert_insights.get("individual_expert_analyses", [])

        if individual_analyses:
            tabs = st.tabs(
                [
                    f"👨‍💼 {analysis.get('expert_name', f'전문가 {i+1}')}"
                    for i, analysis in enumerate(individual_analyses)
                ]
            )

            for i, (tab, analysis) in enumerate(zip(tabs, individual_analyses)):
                with tab:
                    if not analysis.get("error", False):
                        st.markdown(
                            f"**전문 분야**: {analysis.get('expertise_area', '일반')}"
                        )
                        st.markdown("**분석 내용**:")
                        st.markdown(analysis.get("analysis_result", "분석 내용 없음"))
                    else:
                        st.error(
                            f"❌ 분석 오류: {analysis.get('error_message', '알 수 없는 오류')}"
                        )

    # 파일 다운로드 링크
    saved_file = result.get("saved_file")
    if saved_file and os.path.exists(saved_file):
        st.markdown("### 💾 결과 다운로드")

        with open(saved_file, "r", encoding="utf-8") as f:
            json_data = f.read()

        st.download_button(
            label="📥 상세 결과 JSON 다운로드",
            data=json_data,
            file_name=os.path.basename(saved_file),
            mime="application/json",
        )


def show_results_page():
    """결과 조회 페이지를 표시하는 함수"""
    st.header("📊 분석 결과 조회")

    # 저장된 결과 파일들 가져오기
    saved_results = dashboard.get_saved_results()

    if not saved_results:
        st.info("📝 저장된 분석 결과가 없습니다.")
        return

    # 결과 목록 표시
    st.subheader(f"📚 총 {len(saved_results)}개의 분석 결과")

    # 필터링 옵션
    col1, col2 = st.columns(2)
    with col1:
        filter_stock = st.selectbox(
            "종목 필터:", ["전체"] + list(set([r["stock_code"] for r in saved_results]))
        )
    with col2:
        filter_type = st.selectbox(
            "분석 타입 필터:",
            ["전체"] + list(set([r["analysis_type"] for r in saved_results])),
        )

    # 필터 적용
    filtered_results = saved_results
    if filter_stock != "전체":
        filtered_results = [
            r for r in filtered_results if r["stock_code"] == filter_stock
        ]
    if filter_type != "전체":
        filtered_results = [
            r for r in filtered_results if r["analysis_type"] == filter_type
        ]

    # 결과 목록 테이블
    if filtered_results:
        result_data = []
        for result in filtered_results:
            result_data.append(
                {
                    "종목코드": result["stock_code"],
                    "분석타입": result["analysis_type"],
                    "크기(MB)": result["size_mb"],
                    "생성일시": result["created_time"].strftime("%Y-%m-%d %H:%M"),
                    "파일명": result["filename"],
                }
            )

        df = pd.DataFrame(result_data)
        st.dataframe(df, use_container_width=True)

        # 선택된 파일 상세 보기
        selected_file = st.selectbox(
            "상세 보기할 파일 선택:",
            ["선택 안함"] + [r["filename"] for r in filtered_results],
        )

        if selected_file != "선택 안함":
            selected_result = next(
                r for r in filtered_results if r["filename"] == selected_file
            )
            show_detailed_result(selected_result["filepath"])


def show_detailed_result(filepath: str):
    """상세 결과를 표시하는 함수"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            result_data = json.load(f)

        st.subheader("📋 상세 분석 결과")

        # 기본 정보
        st.markdown("#### 📊 기본 정보")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**사용자 질문**: {result_data.get('user_prompt', '없음')}")
            st.write(f"**분석 시간**: {result_data.get('timestamp', '없음')}")
        with col2:
            st.write(
                f"**분석 성공 여부**: {'✅ 성공' if result_data.get('success') else '❌ 실패'}"
            )
            st.write(
                f"**분석 워크플로우**: {result_data.get('analysis_flow', '알 수 없음')}"
            )

        # JSON 데이터 표시 (접을 수 있는 형태)
        with st.expander("🔍 전체 JSON 데이터 보기"):
            st.json(result_data)

        # 다운로드 버튼
        json_str = json.dumps(result_data, ensure_ascii=False, indent=2)
        st.download_button(
            label="📥 JSON 파일 다운로드",
            data=json_str,
            file_name=os.path.basename(filepath),
            mime="application/json",
        )

    except Exception as e:
        st.error(f"❌ 파일 읽기 실패: {str(e)}")


def show_settings_page():
    """설정 페이지를 표시하는 함수"""
    st.header("⚙️ 설정")

    # API 키 설정
    st.subheader("🔑 API 키 설정")

    # 환경변수 상태 확인
    openai_key = os.getenv("OPENAI_API_KEY")
    dart_key = os.getenv("DART_API_KEY")

    col1, col2 = st.columns(2)
    with col1:
        st.text_input(
            "OpenAI API 키:",
            value="●●●●●●●●" if openai_key else "",
            type="password",
            disabled=True,
            help="환경변수에서 로드됨",
        )
    with col2:
        st.text_input(
            "DART API 키:",
            value="●●●●●●●●" if dart_key else "",
            type="password",
            disabled=True,
            help="환경변수에서 로드됨",
        )

    # 시스템 정보
    st.subheader("ℹ️ 시스템 정보")

    info_data = {
        "Python 버전": sys.version.split()[0],
        "Streamlit 버전": st.__version__,
        "현재 작업 디렉토리": os.getcwd(),
        "결과 파일 개수": len(dashboard.get_saved_results()),
        "OpenAI API 키": "설정됨" if openai_key else "없음",
        "DART API 키": "설정됨" if dart_key else "없음",
    }

    for key, value in info_data.items():
        st.write(f"**{key}**: {value}")

    # 캐시 정리
    st.subheader("🧹 캐시 관리")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Streamlit 캐시 정리"):
            st.cache_data.clear()
            st.success("✅ 캐시가 정리되었습니다!")

    with col2:
        if st.button("🔄 분석 시스템 재시작"):
            dashboard.analysis_system = None
            st.success("✅ 분석 시스템이 재시작됩니다!")


# 🚀 메인 실행 부분
if __name__ == "__main__":
    """
    프로그램의 시작점

    이 부분이 실행되면 대시보드가 시작돼요!
    터미널에서 'streamlit run streamlit_dashboard.py' 명령어로 실행하면
    이 코드가 실행되면서 웹 브라우저에 대시보드가 표시됩니다.
    """
    main()
