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
col1, col2 = st.columns([6, 1])
with col1:
    st.markdown(
        """
        <h1 style="color: #2c3e50; font-size: 28px; font-weight: 700; margin: 0;">
            Financial Analysis Agent
        </h1>
        <p style="color: #7f8c8d; font-size: 16px; margin: 5px 0 0 0;">
            AI 기반 종합 주식 분석 및 투자 전략 리포트
        </p>
        """,
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        """
    <div style="text-align: right;">
        <div style="width:70px; height:70px; background: linear-gradient(135deg, #4CAF50, #45a049); display: inline-flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 24px; border-radius:10px; border:1px solid #e0e0e0;">OM</div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    current_date = datetime.now().strftime("%Y-%m-%d")
    st.markdown(
        f'<div style="text-align:right; color:#2c3e50; font-weight:600; font-size:14px; margin-top:4px;">작성기준일 | {current_date}</div>',
        unsafe_allow_html=True,
    )

# 사이드바 - 분석 옵션
with st.sidebar:
    st.markdown("### ⚙️ 분석 설정")

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


# 분석 실행 함수
async def run_analysis(prompt: str, mode: str = "enhanced"):
    """분석을 실행하는 함수"""
    try:
        if mode == "enhanced":
            # EnhancedStockAnalysisSystem 사용
            if st.session_state.enhanced_system is None:
                st.session_state.enhanced_system = EnhancedStockAnalysisSystem()

            def progress_callback(step: str):
                st.session_state.current_steps.append(step)

            result = await st.session_state.enhanced_system.run_enhanced_analysis(
                prompt
            )
            return result

        elif mode == "manus":
            # Manus 에이전트 사용
            agent = await Manus.create()

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
            return result

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
