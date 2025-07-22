#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenManus Streamlit 대시보드 - 개선된 버전

친구가 만들어준 파일을 기반으로 OpenManus 프로젝트에 맞게 개선한 대시보드입니다.
주요 개선사항:
1. OpenManus의 강력한 분석 기능 통합
2. 더 직관적인 UI/UX
3. 실시간 분석 진행상황 표시
4. 다양한 차트 및 시각화 지원
5. 한국어 완전 지원
"""

import asyncio
import base64
import glob
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# 환경변수 로딩
from dotenv import load_dotenv

load_dotenv()

# Streamlit 모드 환경변수 설정 (AskHuman 도구 비활성화)
os.environ["STREAMLIT_MODE"] = "true"
os.environ["DASHBOARD_MODE"] = "true"

# AskHuman 도구 완전 비활성화를 위한 추가 설정
os.environ["DISABLE_ASK_HUMAN"] = "true"

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Streamlit 및 기타 라이브러리
import streamlit as st
from plotly.subplots import make_subplots

# OpenManus 모듈들
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agent.manus import Manus
from app.llm import LLM
from app.logger import logger

# OpenManus 핵심 모듈들
from enhanced_main import EnhancedStockAnalysisSystem

# 차트 생성 도구
try:
    from app.tool.chart_visualization.data_visualization import DataVisualizationTool

    CHART_TOOL_AVAILABLE = True
except ImportError:
    CHART_TOOL_AVAILABLE = False
    logger.warning("차트 시각화 도구를 불러올 수 없습니다.")

# 페이지 설정
st.set_page_config(
    page_title="Finanaceial Analysis Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# CSS 스타일 적용
st.markdown(
    """
<style>
    /* 전체 배경 */
    .main {
        background-color: #ffffff;
    }

    /* 헤더 스타일 */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px 0;
        border-bottom: 2px solid #e0e0e0;
        margin-bottom: 30px;
    }

    /* 섹션 헤더 */
    .section-header {
        background: linear-gradient(90deg, #4CAF50, #45a049);
        color: white;
        padding: 12px 20px;
        border-radius: 8px 8px 0 0;
        font-weight: 600;
        font-size: 16px;
        margin-bottom: 0;
    }

    /* 전문가 분석 결과 헤더 통일 */
    .analysis-result h2 {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: #2c3e50 !important;
        margin-top: 20px !important;
        margin-bottom: 15px !important;
        padding-bottom: 8px !important;
        border-bottom: 2px solid #e0e0e0 !important;
    }

    /* Streamlit 마크다운 헤더 강제 스타일 적용 */
    .stMarkdown h2 {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: #2c3e50 !important;
        margin-top: 20px !important;
        margin-bottom: 15px !important;
        padding-bottom: 8px !important;
        border-bottom: 2px solid #e0e0e0 !important;
    }

    /* 모든 h2 헤더에 대한 강제 스타일 */
    h2 {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: #2c3e50 !important;
        margin-top: 20px !important;
        margin-bottom: 15px !important;
        padding-bottom: 8px !important;
        border-bottom: 2px solid #e0e0e0 !important;
    }

    /* 섹션 컨테이너 */
    .section-container {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin-bottom: 25px;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .section-content {
        padding: 20px;
        background: #fafafa;
    }

    /* 분석 결과 스타일 */
    .analysis-result {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* 진행 상황 표시 */
    .progress-container {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
    }

    /* 요약 박스 */
    .summary-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(90deg, #4CAF50, #45a049);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #45a049, #4CAF50);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    /* 애니메이션 */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }

    /* 테이블 스타일 */
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 10px 0;
    }

    th, td {
        border: 1px solid #ddd;
        padding: 12px;
        text-align: left;
    }

    th {
        background-color: #f8f9fa;
        font-weight: 600;
        color: #2c3e50;
    }

    tr:nth-child(even) {
        background-color: #f8f9fa;
    }

    tr:hover {
        background-color: #e9ecef;
    }
</style>
""",
    unsafe_allow_html=True,
)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "waiting_for_response" not in st.session_state:
    st.session_state.waiting_for_response = False
if "current_steps" not in st.session_state:
    st.session_state.current_steps = []
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = {}
if "enhanced_system" not in st.session_state:
    st.session_state.enhanced_system = None


# 헤더 섹션
# 로고 이미지 파일 경로
logo_path = "assets/logo.png"

# 로고 이미지 표시 (우측 상단 맨 끝에 위치)
try:
    logo_html = f'<img src="data:image/png;base64,{base64.b64encode(open(logo_path, "rb").read()).decode()}" style="width:70px; height:70px; border-radius:10px; border:1px solid #e0e0e0;">'
except:
    logo_html = """
    <div style="width:70px; height:70px; background: linear-gradient(135deg, #4CAF50, #45a049); display: inline-flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 24px; border-radius:10px; border:1px solid #e0e0e0;">LE</div>
    """

st.markdown(
    """
    <div style="position: relative; width: 100%;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div style="flex: 1;">
                <h1 style="color: #2c3e50; font-size: 28px; font-weight: 700; margin: 0;">
                    Financial Analysis Agent
                </h1>
                <p style="color: #7f8c8d; font-size: 16px; margin: 5px 0 0 0;">
                    AI 기반 종합 주식 분석 및 투자 전략 리포트
                </p>
            </div>
            <div style="text-align: right; min-width: 70px;">
                """
    + logo_html
    + """
                <div style="height: 10px;"></div>
                <div style="color: #2c3e50; font-weight: 600; font-size: 14px;">
                    작성기준일 | """
    + datetime.now().strftime("%Y-%m-%d")
    + """
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 사이드바 - 분석 옵션
with st.sidebar:
    st.markdown("### ⚙️ 분석 설정")

    # 로고 업로드 기능 (개발자용)
    with st.expander("🔧 로고 설정", expanded=False):
        uploaded_logo = st.file_uploader(
            "로고 이미지 업로드", type=["png", "jpg", "jpeg"], key="logo_uploader"
        )
        if uploaded_logo is not None:
            # assets 폴더가 없으면 생성
            os.makedirs("assets", exist_ok=True)

            # 이미지 저장
            with open("assets/logo.png", "wb") as f:
                f.write(uploaded_logo.getbuffer())
            st.success("로고가 성공적으로 업로드되었습니다!")
            st.rerun()

    # 분석 모드 선택
    analysis_mode = st.selectbox(
        "분석 모드",
        ["enhanced", "manus", "technical"],
        format_func=lambda x: {
            "enhanced": "🎯 종합 분석 (추천)",
            "manus": "🤖 Manus AI",
            "technical": "📈 기술적 분석",
        }[x],
    )

    # 분석 깊이 설정
    analysis_depth = st.selectbox(
        "분석 깊이",
        ["basic", "standard", "comprehensive"],
        format_func=lambda x: {
            "basic": "기본 분석",
            "standard": "표준 분석",
            "comprehensive": "심화 분석",
        }[x],
    )

    # 차트 생성 옵션
    st.markdown("### 📊 차트 설정")
    generate_charts = st.checkbox("자동 차트 생성", value=True)
    chart_type = st.selectbox(
        "차트 타입",
        ["comprehensive", "basic", "technical"],
        format_func=lambda x: {
            "comprehensive": "종합 차트",
            "basic": "기본 차트",
            "technical": "기술적 분석 차트",
        }[x],
    )

# 메인 분석 섹션
if not st.session_state.messages:
    # 초기 분석 요청
    st.markdown(
        """
    <div class="section-header">
        분석 요청
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-content">', unsafe_allow_html=True)

    # 분석 예시
    with st.expander("💡 분석 예시 보기", expanded=False):
        st.markdown(
            """
        **기본 분석 예시:**
        - 삼성전자 주식 분석해줘
        - 애플(AAPL) 투자 가치 분석
        - 테슬라(TSLA) 기술적 분석

        **상세 분석 예시:**
        - 삼성전자 재무제표 분석과 투자 의견
        - 애플의 최근 실적과 향후 전망
        - 테슬라의 기술적 지표와 매매 타이밍
        """
        )

    user_prompt = st.text_area(
        "분석할 종목과 요청을 입력하세요.",
        placeholder="예: 삼성전자 종목에 대해서 분석해줘",
        key="initial_prompt",
        height=120,
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 분석 시작", key="start_analysis", use_container_width=True):
            if user_prompt.strip():
                st.session_state.messages.append(
                    {"role": "user", "content": user_prompt}
                )
                st.session_state.waiting_for_response = True
                st.session_state.analysis_mode = analysis_mode
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# 분석 결과 표시
if st.session_state.messages:
    st.markdown(
        """
    <div class="section-header">
        주식 분석 리포트
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 대화 히스토리 표시
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            # 사용자 질문 표시
            st.markdown(
                f'<div class="analysis-result">'
                f'<div style="display: flex; align-items: center; margin-bottom: 10px;">'
                f'<div style="width: 8px; height: 8px; background: #4CAF50; border-radius: 50%; margin-right: 10px;"></div>'
                f'<strong style="color: #2c3e50; font-size: 16px;">분석 요청 #{i//2+1}</strong>'
                f"</div>"
                f'<div style="color: #34495e; font-size: 15px; line-height: 1.6; padding: 15px; background: #f8f9fa; border-radius: 6px;">{message["content"]}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )
        elif message["role"] == "assistant":
            # AI 답변 표시
            st.markdown(
                f'<div class="analysis-result">'
                f'<div style="display: flex; align-items: center; margin-bottom: 10px;">'
                f'<div style="width: 8px; height: 8px; background: #3498db; border-radius: 50%; margin-right: 10px;"></div>'
                f'<strong style="color: #2c3e50; font-size: 16px;">AI 분석 결과</strong>'
                f"</div>"
                f'<div style="color: #34495e; font-size: 15px; line-height: 1.6;">{message["content"]}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )

# 진행 중인 분석 표시
if st.session_state.waiting_for_response:
    st.markdown(
        """
    <div class="progress-container">
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <div style="width: 8px; height: 8px; background: #ff9800; border-radius: 50%; margin-right: 10px; animation: pulse 1.5s infinite;"></div>
            <strong style="color: #e65100; font-size: 16px;">AI 분석 진행 중...</strong>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 진행 상황 표시
    if st.session_state.current_steps:
        st.markdown(
            """
        <div class="section-header">
            실시간 진행상황
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="section-content">', unsafe_allow_html=True)
        for step in st.session_state.current_steps:
            if "error" in step.lower() or "fail" in step.lower():
                color = "#e74c3c"
                icon = "❌"
            elif "완료" in step or "Successfully" in step:
                color = "#27ae60"
                icon = "✅"
            elif "진행 중" in step or "실행 중" in step:
                color = "#f39c12"
                icon = "🚀"
            else:
                color = "#3498db"
                icon = "⚙️"
            st.markdown(
                f'<div style="margin:8px 0; display:flex; align-items:center; padding: 8px; background: {color}15; border-radius: 6px;">'
                f'<span style="margin-right: 10px; font-size: 16px;">{icon}</span>'
                f'<span style="color: {color}; font-size: 14px; font-weight: 500;">{step}</span></div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)


def filter_analysis_result(result: str) -> str:
    """분석 결과에서 LangChain 전문가 분석 내용을 추출"""
    try:
        # JSON 형태의 결과인지 확인
        if isinstance(result, str) and result.strip().startswith("{"):
            try:
                result_dict = json.loads(result)
            except json.JSONDecodeError:
                # JSON이 아니면 원본 반환
                return result
        elif isinstance(result, dict):
            result_dict = result
        else:
            # 문자열이지만 JSON이 아니면 원본 반환
            return result

        # LangChain 전문가 분석 결과 추출
        expert_insights = result_dict.get("expert_insights", {})
        expert_results = expert_insights.get("expert_results", [])

        if not expert_results:
            # expert_results가 없으면 다른 형태 확인
            simplified_summary = expert_insights.get("simplified_summary", {})
            if simplified_summary:
                financial_analyst = simplified_summary.get("financial_analyst", {})
                technical_analyst = simplified_summary.get("technical_analyst", {})

                filtered_result = ""

                # 통합재무분석 전문가 결과
                if financial_analyst and financial_analyst.get("analysis_result"):
                    filtered_result += f'<h2 style="font-size: 24px; font-weight: 700; color: #2c3e50; margin-top: 20px; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 2px solid #e0e0e0;">📊 통합재무분석 전문가</h2>\n\n{financial_analyst["analysis_result"]}\n\n'

                # 기술적 분석 전문가 결과 (주석처리로 비활성화)
                # if technical_analyst and technical_analyst.get("analysis_result"):
                #     filtered_result += f'<h2 style="font-size: 24px; font-weight: 700; color: #2c3e50; margin-top: 20px; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 2px solid #e0e0e0;">📈 기술적 분석 전문가</h2>\n\n{technical_analyst["analysis_result"]}\n\n'

                return filtered_result if filtered_result else str(result)
            else:
                return str(result)

                # 전문가별 분석 결과 조합
        filtered_result = ""

        for expert_result in expert_results:
            expert_name = expert_result.get("expert_name", "")
            analysis_result = expert_result.get("analysis_result", "")

            if not analysis_result:
                continue

            # 전문가 이름에 따라 섹션 구분 (HTML 태그로 강제 스타일 적용) - 기술적 분석가 비활성화
            if "재무" in expert_name or "통합" in expert_name:
                filtered_result += f'<h2 style="font-size: 24px; font-weight: 700; color: #2c3e50; margin-top: 20px; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 2px solid #e0e0e0;">📊 {expert_name}</h2>\n\n{analysis_result}\n\n'
            # elif "기술적" in expert_name or "기술" in expert_name:
            #     filtered_result += f'<h2 style="font-size: 24px; font-weight: 700; color: #2c3e50; margin-top: 20px; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 2px solid #e0e0e0;">📈 {expert_name}</h2>\n\n{analysis_result}\n\n'
            else:
                filtered_result += f'<h2 style="font-size: 24px; font-weight: 700; color: #2c3e50; margin-top: 20px; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 2px solid #e0e0e0;">🔍 {expert_name}</h2>\n\n{analysis_result}\n\n'

        return filtered_result if filtered_result else str(result)

    except Exception as e:
        logger.error(f"분석 결과 필터링 중 오류: {e}")
        return str(result)


# 분석 실행 함수
async def run_analysis(prompt: str, mode: str = "enhanced"):
    """분석을 실행하는 함수"""
    try:
        if mode == "enhanced":
            # EnhancedStockAnalysisSystem 사용
            if st.session_state.enhanced_system is None:
                st.session_state.enhanced_system = EnhancedStockAnalysisSystem()

                # Enhanced 시스템의 Manus 에이전트에서도 AskHuman 도구 비활성화
                if hasattr(st.session_state.enhanced_system, "manus_agent"):
                    agent = st.session_state.enhanced_system.manus_agent
                    if hasattr(agent, "available_tools"):
                        tools_to_remove = []
                        for tool in agent.available_tools.tools:
                            if (
                                hasattr(tool, "name")
                                and "ask_human" in tool.name.lower()
                            ):
                                tools_to_remove.append(tool)

                        for tool in tools_to_remove:
                            agent.available_tools.tools.remove(tool)
                            logger.info(
                                f"Enhanced 시스템에서 AskHuman 도구 비활성화: {tool.name}"
                            )

            def progress_callback(step: str):
                # 중복된 단계는 업데이트, 새로운 단계는 추가
                if st.session_state.current_steps and st.session_state.current_steps[
                    -1
                ].startswith(step.split()[0]):
                    st.session_state.current_steps[-1] = step
                else:
                    st.session_state.current_steps.append(step)

            result = await st.session_state.enhanced_system.run_enhanced_analysis(
                prompt
            )

            # 결과가 성공적으로 완료되었는지 확인
            if result and result.get("success"):
                # CrewAI 분석 결과에서 전문가 분석 내용 추출
                sector_analysis = result.get("steps", {}).get(
                    "step4_crewai_comprehensive_analysis", {}
                )
                if sector_analysis and sector_analysis.get("success"):
                    # 전문가 분석 결과 필터링
                    return filter_analysis_result(sector_analysis)
                else:
                    # CrewAI 분석이 실패한 경우 전체 결과 반환
                    return f"분석이 완료되었지만 전문가 분석 결과를 찾을 수 없습니다.\n\n전체 결과: {str(result)}"
            else:
                # 분석 실패 시 오류 메시지 반환
                error_msg = (
                    result.get("error", "알 수 없는 오류")
                    if result
                    else "분석 결과가 없습니다"
                )
                return f"분석 중 오류가 발생했습니다: {error_msg}"

        elif mode == "manus":
            # Manus 에이전트 사용 (AskHuman 도구 비활성화)
            agent = await Manus.create()

            # AskHuman 도구가 있다면 제거
            if hasattr(agent, "available_tools"):
                # AskHuman 도구 찾아서 제거
                tools_to_remove = []
                for tool in agent.available_tools.tools:
                    if hasattr(tool, "name") and "ask_human" in tool.name.lower():
                        tools_to_remove.append(tool)

                for tool in tools_to_remove:
                    agent.available_tools.tools.remove(tool)
                    logger.info(f"AskHuman 도구 비활성화: {tool.name}")

            def on_step_update(step, max_steps):
                step_msg = f"단계 {step}/{max_steps} 실행 중..."
                if st.session_state.current_steps and st.session_state.current_steps[
                    -1
                ].startswith("단계"):
                    st.session_state.current_steps[-1] = step_msg
                else:
                    st.session_state.current_steps.append(step_msg)

            result = await agent.run(prompt, on_step_update=on_step_update)
            await agent.cleanup()
            # Manus 결과는 직접 반환 (이미 분석된 형태)
            return str(result)

        else:
            # 기본 기술적 분석
            return "기술적 분석 모드는 준비 중입니다."

    except Exception as e:
        logger.error(f"분석 실행 중 오류: {e}")
        return f"분석 중 오류가 발생했습니다: {str(e)}"


# 분석 실행
if st.session_state.waiting_for_response and st.session_state.messages:

    async def execute_analysis():
        latest_prompt = st.session_state.messages[-1]["content"]
        mode = st.session_state.get("analysis_mode", "enhanced")

        result = await run_analysis(latest_prompt, mode)

        if result:
            st.session_state.messages.append(
                {"role": "assistant", "content": str(result)}
            )
            st.session_state.waiting_for_response = False
            st.rerun()

    asyncio.run(execute_analysis())

# 추가 질문 입력
if not st.session_state.waiting_for_response and st.session_state.messages:
    st.markdown(
        """
    <div class="section-header">
        추가 분석 요청
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-content">', unsafe_allow_html=True)

    additional_prompt = st.text_area(
        "추가 질문이 있으시면 입력하세요",
        placeholder="예: 더 자세한 재무분석을 해줘",
        key="additional_prompt",
        height=100,
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button(
            "🔍 추가 분석", key="additional_analysis", use_container_width=True
        ):
            if additional_prompt.strip():
                st.session_state.messages.append(
                    {"role": "user", "content": additional_prompt}
                )
                st.session_state.waiting_for_response = True
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# 차트 및 시각화 섹션
if st.session_state.messages and any(
    "assistant" in msg["role"] for msg in st.session_state.messages
):
    st.markdown(
        """
    <div class="section-header">
        📊 차트 및 시각화
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-content">', unsafe_allow_html=True)

    # 차트 생성 옵션
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("📈 차트 생성", key="generate_chart"):
            st.info("차트 생성 기능은 준비 중입니다.")

    with col2:
        if st.button("📊 데이터 시각화", key="visualize_data"):
            st.info("데이터 시각화 기능은 준비 중입니다.")

    with col3:
        if st.button("📋 리포트 다운로드", key="download_report"):
            st.info("리포트 다운로드 기능은 준비 중입니다.")

    st.markdown("</div>", unsafe_allow_html=True)

# 푸터
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #7f8c8d; font-size: 14px; margin-top: 30px;">
        <p>Financial Analysis Agent - AI 기반 종합 주식 분석 시스템</p>
        <p>© 2025 Financial Analysis Agent. All rights reserved.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
