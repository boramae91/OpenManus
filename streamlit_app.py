import os
from dotenv import load_dotenv
import streamlit as st
import asyncio
from agent.manus import Manus
import re
import json
import time
import glob
from datetime import datetime

# .env 파일 로드 (절대 경로 사용)
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

# 페이지 설정
st.set_page_config(
    page_title="LIFE Stock Analysis Generation AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 항상 라이트(화이트) 배경 강제 적용
st.markdown("""
    <style>
    body, .main, .stApp {
        background-color: #fff !important;
        color: #222 !important;
    }
    .stTextArea textarea, textarea {
        color: #222 !important;
        background: #fff !important;
    }
    .stTextInput input, input[type="text"][object Object]
    color: #666nt;
    background: #fff !important;
}
.stChatInput input[object Object]
    color: #666nt;
    background: #fff !important;
}
    /* Chat 입력창 전체 하단 wrapper 배경도 흰색으로 설정 */
    [data-testid="stBottomBlockContainer"] {
        background-color: #fff !important;
        border-top: 1px solid #eee !important;
    }
    </style>
""", unsafe_allow_html=True)

# CSS 스타일 적용
st.markdown("""
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
        padding: 20px 0 0 0;
        border-bottom: 2px solid #e0e0e0;
        margin-bottom: 30px;
    }
    
    .header-left {
        flex: 1;
        min-width: 0;
    }
    
    .header-right {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        min-width: 90px;
    }
    
    .logo {
        width: 70px;
        height: 70px;
        border-radius: 10px;
        object-fit: contain;
        margin-bottom: 6px;
        box-shadow: 0 2px 8px rgba(76,175,80,0.08);
        background: #fff;
        border: 1px solid #e0e0e0;
        display: block;
    }
    
    .date-info {
        font-size: 14px;
        color: #388e3c;
        font-weight: 600;
        text-align: right;
        margin-top: 0;
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
    
    /* 테이블 스타일 */
    .data-table {
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* 입력 필드 스타일 */
    .stTextArea > div > div > textarea {
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        background: white;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
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
    
    /* 분석 결과 스타일 */
    .analysis-result {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 차트 컨테이너 */
    .chart-container {
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
    
    /* 애니메이션 */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* 테이블 스타일 개선 */
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
    
    /* 채팅 입력창 스타일 (라이트 고정) */
    .stChatInput input, .stChatInput textarea {
        color: #666 !important;
        background: #fff !important;
        border: 1px solid #ddd !important;
    }

    .stChatInput input::placeholder,
    .stChatInput textarea::placeholder {
        color: #999 !important;
    }

    /* 추가 프롬프트 입력창 배경 수정 */
    .stChatInput, .stChatInput input, .stChatInput textarea {
        background-color: #fff !important;
        color: #666 !important;
        border: 1px solid #ddd !important;
    }
</style>
""", unsafe_allow_html=True)

# 헤더 섹션 (columns 방식)
col1, col2 = st.columns([6, 1])
with col1:
    st.markdown(
        '''
        <h1 style="color: #2c3e50; font-size: 28px; font-weight: 700; margin: 0;">
            LIFE Stock Analysis Generation AI
        </h1>
        <p style="color: #7f8c8d; font-size: 16px; margin: 5px 0 0 0;">
            전문적인 주식 기술분석 및 투자 전략 리포트
        </p>
        ''', unsafe_allow_html=True
    )
with col2:
    import base64
    try:
        st.markdown(
            '''
            <div style="text-align: right;">
                <img src="data:image/png;base64,{}" style="width:70px; height:70px; border-radius:10px; object-fit:contain; box-shadow: 0 2px 8px rgba(76,175,80,0.08);">
            </div>
            '''.format(
                base64.b64encode(open("/Users/admin/LIFE/StockAnalysisGeneration-AI/life.jpg", "rb").read()).decode()
            ),
            unsafe_allow_html=True
        )
    except:
        st.markdown('''
        <div style="text-align: right;">
            <div style="width:70px; height:70px; background: linear-gradient(135deg, #4CAF50, #45a049); display: inline-flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 24px; border-radius:10px; border:1px solid #e0e0e0;">LIFE</div>
        </div>
        ''', unsafe_allow_html=True)
    current_date = datetime.now().strftime('%Y-%m-%d')
    st.markdown(
        f'<div style="text-align:right; color:#2c3e50; font-weight:600; font-size:14px; margin-top:4px;">작성기준일 | {current_date}</div>',
        unsafe_allow_html=True
    )

# Streamlit 테마 감지 (다크/라이트) 및 분기 제거
# 항상 라이트모드(화이트) 스타일로 고정
ANSWER_BG = "#f7f7fa"
LOG_BG = "#f3f6fa"
LOG_STEP_COLOR = "#1a237e"

# 세션 상태 초기화 (먼저 실행)
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'waiting_for_response' not in st.session_state:
    st.session_state.waiting_for_response = False
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""
if 'stop_agent' not in st.session_state:
    st.session_state.stop_agent = False
if 'current_steps' not in st.session_state:
    st.session_state.current_steps = []
if 'final_response' not in st.session_state:
    st.session_state.final_response = ""
if 'conversation_logs' not in st.session_state:
    st.session_state.conversation_logs = []  # 각 대화별 로그 저장

# ====== 실제 AI 응답 기반 답변/로그 박스 ======
# 실제 대화가 시작된 경우에만 표시
if st.session_state.messages:
    # 분석 결과 섹션 헤더
    st.markdown("""
    <div class="section-header">
        주식 기술분석 리포트
    </div>
    """, unsafe_allow_html=True)
    # 대화 히스토리를 질문-답변-로그 세트로 표시하는 함수
    def display_conversation_block(idx, user_question, assistant_answer, is_completed):
        # 구분선 (첫 번째 대화가 아닌 경우)
        if idx > 0:
            st.markdown('<hr style="border: 1px solid #e0e0e0; margin: 30px 0;">', unsafe_allow_html=True)
        
        # 질문 표시
        st.markdown(
            f'<div class="analysis-result">'
            f'<div style="display: flex; align-items: center; margin-bottom: 10px;">'
            f'<div style="width: 8px; height: 8px; background: #4CAF50; border-radius: 50%; margin-right: 10px;"></div>'
            f'<strong style="color: #2c3e50; font-size: 16px;">분석 요청 #{idx+1}</strong>'
            f'</div>'
            f'<div style="color: #34495e; font-size: 15px; line-height: 1.6; padding: 15px; background: #f8f9fa; border-radius: 6px;">{user_question}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # 답변 표시
        if assistant_answer:
            # --- JSON 기반 상세 분석 우선 출력 ---
            if "Technical Analysis for" in assistant_answer:
                # 종목코드 추출
                symbol_match = re.search(r'Technical Analysis for (\S+)', assistant_answer)
                symbol = symbol_match.group(1) if symbol_match else None
                # 최신 기술분석 JSON 파일 찾기
                tech_analysis_dir = "logs/technical_analysis"
                json_path = None
                if symbol and os.path.exists(tech_analysis_dir):
                    # 파일명에 symbol이 포함된 가장 최근 파일
                    candidates = sorted(
                        glob.glob(os.path.join(tech_analysis_dir, f"*{symbol.replace('.', ' ')}*.json")),
                        key=os.path.getmtime, reverse=True)
                    if not candidates:
                        # . 대신 _ 로 저장된 경우도 탐색
                        candidates = sorted(
                            glob.glob(os.path.join(tech_analysis_dir, f"*{symbol.replace('.', '_')}*.json")),
                            key=os.path.getmtime, reverse=True)
                    if candidates:
                        json_path = candidates[0]

                # 1. 차트 자동 생성 (comprehensive/html)
                chart_html_path = None
                if symbol:
                    from app.tool.technical_analysis_chart_tool import TechnicalAnalysisChartTool
                    chart_tool = TechnicalAnalysisChartTool()
                    with st.spinner("차트를 자동 생성 중입니다..."):
                        try:
                            import asyncio
                            async def auto_generate_chart():
                                return await chart_tool.execute(
                                    symbol=symbol,
                                    chart_type="comprehensive",
                                    output_format="html"
                                )
                            chart_result = asyncio.run(auto_generate_chart())
                            if not chart_result.error:
                                chart_html_path = chart_result.chart_path
                                st.session_state["latest_chart_path"] = chart_html_path
                        except Exception as e:
                            st.error(f"자동 차트 생성 실패: {e}")

                # 2. 차트(HTML) 리포트 상단에 표시
                if chart_html_path and os.path.exists(chart_html_path):
                    st.markdown("""
                    <div class="section-header" style="margin-top: 20px;">
                        종합 대시보드 차트
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    with open(chart_html_path, "r", encoding="utf-8") as f:
                        chart_html = f.read()
                    st.components.v1.html(
                        chart_html,
                        height=950,
                        width=1800,
                        scrolling=False
                    )
                    st.markdown('</div>', unsafe_allow_html=True)

                # 3. 분석 결과 컨테이너 시작 (리포트)
                st.markdown('<div class="section-container">', unsafe_allow_html=True)
                # JSON 파싱 및 포맷팅 함수
                def format_analysis_from_json(json_path):
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        meta = data.get('metadata', {})
                        analysis = data.get('analysis', {})
                        
                        # 기본 정보
                        context = f"""
**[{meta.get('symbol', '')}] 기술분석 리포트**  

#### 분석 정보
- **분석일시:** {meta.get('analysis_datetime', '')}
- **데이터 소스:** {', '.join(meta.get('data_sources', []))}
- **계산된 지표:** {', '.join(meta.get('indicators_calculated', []))}

#### 데이터 구간
- **일봉 데이터:** {meta.get('daily_data_period', {}).get('start', '')} ~ {meta.get('daily_data_period', {}).get('end', '')} ({meta.get('daily_data_period', {}).get('count', '')}개 데이터)
- **월봉 데이터:** {meta.get('monthly_data_period', {}).get('start', '')} ~ {meta.get('monthly_data_period', {}).get('end', '')} ({meta.get('monthly_data_period', {}).get('count', '')}개 데이터)
"""
                        
                        # MACD 분석 상세 추출
                        macd_text = analysis.get('macd_and_stochastic', '')
                        macd_details = ""
                        if macd_text:
                            # 실제 JSON 패턴에 맞게 수정된 정규표현식
                            macd_cross = re.search(r'MACD\s+(골든크로스|데스크로스)\s+(\d{4}-\d{2}-\d{2})', macd_text)
                            histogram_match = re.search(r'히스토그램\s+(\d+)일간\s+유지.*?최대값\s+([\d,]+)', macd_text)
                            
                            if macd_cross or histogram_match:
                                macd_details = "\n#### MACD 상세 분석"
                                if macd_cross:
                                    macd_details += f"\n- **크로스 발생:** {macd_cross.group(1)} ({macd_cross.group(2)})"
                                if histogram_match:
                                    macd_details += f"\n- **히스토그램:** {histogram_match.group(1)}일 유지 (최대값: {histogram_match.group(2)})"
                            
                            # 스토캐스틱 정보도 포함
                            if "스토캐스틱" in macd_text:
                                stoch_match = re.search(r'스토캐스틱.*?(\d+)일간', macd_text)
                                if stoch_match:
                                    macd_details += f"\n- **스토캐스틱:** {stoch_match.group(1)}일간 지속"
                            
                            # 최소값 정보도 추가
                            min_match = re.search(r'최소값\s+([-\d,]+)', macd_text)
                            if min_match:
                                macd_details += f"\n- **히스토그램 범위:** 최소값 {min_match.group(1)}"
                        
                        # 피보나치 분석 상세 추출
                        fib_text = analysis.get('fibonacci_retracement', '')
                        fib_details = ""
                        if fib_text:
                            # 실제 JSON 패턴에 맞게 수정된 정규표현식
                            fib_levels = re.findall(r'(\d+\.?\d*)%\s+레벨\s+([\d,]+)원', fib_text)
                            # 매수/매도 권장 가격 추출
                            buy_price = re.search(r'매수\s+권장\s+가격대는\s+([\d,]+)원', fib_text)
                            sell_price = re.search(r'매도는\s+([\d,]+)원', fib_text)
                            
                            if fib_levels:
                                fib_details = "\n#### 피보나치 되돌림 레벨"
                                fib_details += "\n| 레벨 | 가격 | 의미 |"
                                fib_details += "\n|------|------|------|"
                                level_meanings = {
                                    "23.6": "단기 매물대 상단",
                                    "38.2": "매수 지점", 
                                    "50.0": "중간 지지선",
                                    "61.8": "강력한 지지선",
                                    "78.6": "마지막 지지선"
                                }
                                for level, price in fib_levels:
                                    meaning = level_meanings.get(level, "지지/저항선")
                                    fib_details += f"\n| {level}% | {price}원 | {meaning} |"
                                
                                if buy_price and sell_price:
                                    fib_details += f"\n\n• **매수 권장:** {buy_price.group(1)}원"
                                    fib_details += f"\n• **매도 권장:** {sell_price.group(1)}원"
                            
                            # 피보나치 돌파 정보 추가
                            breakout_match = re.search(r'(\d+\.?\d*)%\s+레벨\s+(\d{4}-\d{2}-\d{2})\s+돌파', fib_text)
                            if breakout_match:
                                fib_details += f"\n• **돌파 확인:** {breakout_match.group(1)}% 레벨 ({breakout_match.group(2)})"
                            
                            # 지속 기간 정보 추가
                            duration_match = re.search(r'(\d+)주\s+지속', fib_text)
                            if duration_match:
                                fib_details += f"\n• **지속 기간:** {duration_match.group(1)}주"
                        
                        # 거래량 분석 상세 추출
                        volume_text = analysis.get('volume_and_obv', '')
                        volume_details = ""
                        if volume_text:
                            # 실제 JSON 패턴에 맞게 수정된 정규표현식
                            volume_spike = re.search(r'(\d{4}-\d{2}-\d{2})\s+거래량\s+스파이크', volume_text)
                            volume_increase_20 = re.search(r'20일\s+MA\s+대비\s+(\d+)%', volume_text)
                            volume_increase_50 = re.search(r'50일\s+MA\s+대비\s+(\d+)%', volume_text)
                            # OBV 정보 추출
                            obv_trend = re.search(r'OBV\s+(상승|하락)\s+추세', volume_text)
                            obv_divergence = re.search(r'다이버전스\s+(있었습니다|없었습니다)', volume_text)
                            
                            if volume_spike or obv_trend:
                                volume_details = "\n#### 거래량 및 OBV 상세"
                                if volume_spike:
                                    volume_details += f"\n- **거래량 스파이크:** {volume_spike.group(1)}"
                                    if volume_increase_20:
                                        volume_details += f"\n- **20일 MA 대비:** {volume_increase_20.group(1)}% 증가"
                                    if volume_increase_50:
                                        volume_details += f"\n- **50일 MA 대비:** {volume_increase_50.group(1)}% 증가"
                                if obv_trend:
                                    volume_details += f"\n- **OBV 추세:** {obv_trend.group(1)} 추세"
                                if obv_divergence:
                                    status = "발견됨" if "있었습니다" in obv_divergence.group(1) else "없음"
                                    volume_details += f"\n- **가격-거래량 다이버전스:** {status}"
                        
                        # 이벤트 분석 상세 추출
                        event_text = analysis.get('event_correlation', '')
                        event_details = ""
                        if event_text:
                            # 실제 JSON 패턴에 맞게 수정된 정규표현식
                            event_date = re.search(r'(\d{4}-\d{2}-\d{2})\s+정책\s+발표', event_text)
                            price_change = re.search(r'주가\s+([+-]?\d+)%', event_text)
                            macd_change = re.search(r'MACD\s+([+-]?\d+)%', event_text)
                            rsi_change = re.search(r'RSI\s+([+-]?\d+)%', event_text)
                            obv_change = re.search(r'OBV\s+([+-]?\d+)%', event_text)
                            momentum_duration = re.search(r'모멘텀\s+(\d+)주', event_text)
                            avg_response = re.search(r'평균\s+주가\s+([+-]?\d+)%', event_text)
                            risk_point = re.search(r'리스크\s+(.*?)증가', event_text)
                            
                            if event_date or price_change:
                                event_details = "\n#### 주요 이벤트 반응 분석"
                                if event_date:
                                    event_details += f"\n\n**이벤트 정보**"
                                    event_details += f"\n- 발표일: {event_date.group(1)}"
                                    event_details += f"\n- 이벤트 유형: 정책 발표"
                                if price_change:
                                    event_details += f"\n\n**시장 반응**"
                                    event_details += f"\n- 주가 변화: {price_change.group(1)}%"
                                    if macd_change:
                                        event_details += f"\n- MACD 변화: {macd_change.group(1)}%"
                                    if rsi_change:
                                        event_details += f"\n- RSI 변화: {rsi_change.group(1)}%"
                                    if obv_change:
                                        event_details += f"\n- OBV 변화: {obv_change.group(1)}%"
                                    if momentum_duration:
                                        event_details += f"\n- 모멘텀 지속: {momentum_duration.group(1)}주"
                                    if avg_response:
                                        event_details += f"\n- 유사 이벤트 평균 반응: {avg_response.group(1)}%"
                                    if risk_point:
                                        event_details += f"\n\n**리스크 포인트**"
                                        event_details += f"\n- 주의사항: {risk_point.group(1)} 증가"
                        
                        # 시나리오 분석 상세 추출
                        scenario = analysis.get('1_3m_scenario', {})
                        scenario_details = ""
                        if scenario:
                            detailed_scenarios = scenario.get('detailed_scenarios', {})
                            if detailed_scenarios:
                                scenario_details = "\n#### 시나리오별 투자 전략"
                                
                                # Bull 시나리오
                                bull = detailed_scenarios.get('bull', {})
                                if bull:
                                    triggers = bull.get('trigger', [])
                                    scenario_details += f"\n\n**🟢 Bull 시나리오:**"
                                    scenario_details += f"\n- **트리거 조건:** {', '.join(triggers)}"
                                    scenario_details += f"\n- **목표 가격대:** {bull.get('target_low', 'N/A')} ~ {bull.get('target_high', 'N/A')}"
                                    scenario_details += f"\n- **투자 기간:** {bull.get('timeframe', 'N/A')}"
                                    scenario_details += f"\n- **권장 포지션:** {bull.get('position', 'N/A')}"
                                    scenario_details += f"\n- **실행 전략:** {bull.get('action', 'N/A')}"
                                
                                # Neutral 시나리오
                                neutral = detailed_scenarios.get('neutral', {})
                                if neutral:
                                    scenario_details += f"\n\n**🟡 Neutral 시나리오:**"
                                    scenario_details += f"\n- **가격 범위:** {neutral.get('range_low', 'N/A')} ~ {neutral.get('range_high', 'N/A')}"
                                    scenario_details += f"\n- **지속 기간:** {neutral.get('duration', 'N/A')}"
                                    scenario_details += f"\n- **투자 전략:** {neutral.get('action', 'N/A')}"
                                
                                # Bear 시나리오
                                bear = detailed_scenarios.get('bear', {})
                                if bear:
                                    triggers = bear.get('trigger', [])
                                    scenario_details += f"\n\n**🔴 Bear 시나리오:**"
                                    scenario_details += f"\n- **트리거 조건:** {', '.join(triggers)}"
                                    scenario_details += f"\n- **손절가:** {bear.get('stop_loss', 'N/A')}"
                                    scenario_details += f"\n- **투자 기간:** {bear.get('timeframe', 'N/A')}"
                                    scenario_details += f"\n- **권장 포지션:** {bear.get('position', 'N/A')}"
                                    scenario_details += f"\n- **실행 전략:** {bear.get('action', 'N/A')}"
                        
                        # 주요 분석 요약 (개선된 버전)
                        summary = f"""
### 핵심 기술지표 요약
- **장기 추세:** {analysis.get('long_term_trend_and_cycle', '')}
- **RSI & 볼린저:** {analysis.get('rsi_and_bollinger', '')}
- **MACD & 스토캐스틱:** {analysis.get('macd_and_stochastic', '')}
- **거래량 & OBV:** {analysis.get('volume_and_obv', '')}
- **피보나치:** {analysis.get('fibonacci_retracement', '')}
- **이벤트:** {analysis.get('event_correlation', '')}
- **시나리오:** {scenario.get('direction', '')} / {scenario.get('action_plan', '')}
- **요약:** {analysis.get('one_line_pattern', '')}
"""
                        
                        # 모든 상세 정보 조합
                        full_analysis = f"{context}\n{summary}{macd_details}{fib_details}{volume_details}{event_details}{scenario_details}"
                        return full_analysis
                        
                    except Exception as e:
                        return f"❗️상세 분석 JSON 파싱 실패: {e}"
                # JSON이 있으면 상세 분석 우선 출력
                if json_path:
                    st.markdown('<div class="section-content">', unsafe_allow_html=True)
                    st.markdown(format_analysis_from_json(json_path), unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    
                    # 차트 미리보기(HTML) 복원 및 크게 표시
                    html_paths = re.findall(r'([\w\-/]+\.html)', assistant_answer)
                    for html_path in html_paths:
                        if not os.path.isabs(html_path):
                            html_path_full = os.path.join(os.path.dirname(os.path.dirname(__file__)), "workspace", html_path)
                        else:
                            html_path_full = html_path
                        if os.path.exists(html_path_full):
                            st.markdown("""
                            <div class="section-header" style="margin-top: 20px;">
                                종합 대시보드 차트
                            </div>
                            """, unsafe_allow_html=True)
                            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                            st.components.v1.html(
                                open(html_path_full, "r", encoding="utf-8").read(), 
                                height=950, 
                                width=1800,
                                scrolling=False
                            )
                            st.markdown('</div>', unsafe_allow_html=True)
                            break

                else:
                    st.markdown(assistant_answer)

                # 기술분석 결과가 포함된 경우 JSON 상세 결과 표시
                if "Technical Analysis for" in assistant_answer and "Direction:" in assistant_answer:
                    # 최근 저장된 기술분석 JSON 파일 찾기
                    tech_analysis_dir = "logs/technical_analysis"
                    if os.path.exists(tech_analysis_dir):
                        json_files = [f for f in os.listdir(tech_analysis_dir) if f.endswith('.json')]
                        if json_files:
                            # 가장 최근 파일 선택
                            latest_file = max(json_files, key=lambda x: os.path.getmtime(os.path.join(tech_analysis_dir, x)))
                            latest_file_path = os.path.join(tech_analysis_dir, latest_file)
                            
                            with st.expander("상세 기술분석 결과 (JSON)", expanded=False):
                                try:
                                    with open(latest_file_path, 'r', encoding='utf-8') as f:
                                        json_data = json.load(f)
                                    st.json(json_data)
                                    
                                    # 파일 다운로드 버튼
                                    st.download_button(
                                        label="JSON 파일 다운로드",
                                        data=json.dumps(json_data, ensure_ascii=False, indent=2),
                                        file_name=latest_file,
                                        mime="application/json"
                                    )
                                except Exception as e:
                                    st.error(f"JSON 파일 읽기 실패: {e}")
                        
                        # 기술분석 차트 생성 섹션
                        st.markdown("---")
                        st.markdown("### 기술분석 차트 생성")
                        
                        col1, col2, col3 = st.columns([1, 1, 1])
                        
                        with col1:
                            chart_type = st.selectbox(
                                "차트 타입",
                                ["basic", "advanced", "comprehensive"],
                                format_func=lambda x: {
                                    "basic": "기본 (캔들 + MA)",
                                    "advanced": "고급 (볼린저 + RSI)",
                                    "comprehensive": "종합 (모든 지표)"
                                }[x],
                                key=f"chart_type_{idx}"
                            )
                        
                        with col2:
                            output_format = st.selectbox(
                                "출력 형식",
                                ["html", "png"],
                                format_func=lambda x: "HTML (인터랙티브)" if x == "html" else "PNG (이미지)",
                                key=f"output_format_{idx}"
                            )
                        
                        with col3:
                            if st.button("차트 생성", type="primary", key=f"chart_btn_{idx}"):
                                with st.spinner("차트를 생성하고 있습니다..."):
                                    try:
                                        # 종목 코드 추출
                                        symbol_match = re.search(r'Technical Analysis for (\S+)', assistant_answer)
                                        if symbol_match:
                                            symbol = symbol_match.group(1)
                                            # 비동기 차트 생성 함수
                                            async def generate_chart():
                                                from app.tool.technical_analysis_chart_tool import TechnicalAnalysisChartTool
                                                chart_tool = TechnicalAnalysisChartTool()
                                                return await chart_tool.execute(
                                                    symbol=symbol,
                                                    chart_type=chart_type,
                                                    output_format=output_format
                                                )
                                            # 차트 도구 실행
                                            result = asyncio.run(generate_chart())
                                            # 차트 생성 성공 시
                                            if result.error:
                                                st.error(f"차트 생성 실패: {result.error}")
                                            else:
                                                st.success(f"차트가 성공적으로 생성되었습니다!")
                                                st.info(f"저장 위치: {result.chart_path}")
                                                # 차트 파일 다운로드
                                                with open(result.chart_path, 'r', encoding='utf-8') as f:
                                                    chart_data = f.read()
                                                st.download_button(
                                                    label="차트 파일 다운로드",
                                                    data=chart_data,
                                                    file_name=os.path.basename(result.chart_path),
                                                    mime="text/html"
                                                )
                                                # 최신 차트 경로 세션에 저장 (반드시 실행)
                                                st.session_state["latest_chart_path"] = result.chart_path
                                    except Exception as e:
                                        st.error(f"차트 생성 중 오류 발생: {str(e)}")

        # 진행 중인 답변
        else:
            st.markdown("""
            <div class="progress-container">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="width: 8px; height: 8px; background: #ff9800; border-radius: 50%; margin-right: 10px; animation: pulse 1.5s infinite;"></div>
                    <strong style="color: #e65100; font-size: 16px;">AI 분석 진행 중...</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 현재 진행 중인 step 로그 표시
            if st.session_state.current_steps:
                st.markdown("""
                <div class="section-header">
                    실시간 진행상황
                </div>
                """, unsafe_allow_html=True)
                st.markdown('<div class="section-content">', unsafe_allow_html=True)
                for step in st.session_state.current_steps:
                    if "error" in step.lower() or "fail" in step.lower():
                        color = "#e74c3c"
                        icon = "❌"
                    elif "완료" in step or "Successfully" in step:
                        color = "#27ae60"
                        icon = "✅"
                    elif "진행 중" in step or "실행 중" in step or "🚀" in step or "Executing step" in step:
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
                st.markdown('</div>', unsafe_allow_html=True)

    # 대화 히스토리 누적 표시 (질문-답변-로그 세트로)
    if st.session_state.messages:
        conversation_pairs = []
        current_user_msg = None
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                current_user_msg = msg["content"]
            elif msg["role"] == "assistant" and current_user_msg:
                conversation_pairs.append((current_user_msg, msg["content"]))
                current_user_msg = None
        # 진행 중인 질문이 있으면 추가 (답변 대기 중)
        if current_user_msg:
            conversation_pairs.append((current_user_msg, None))
        # 모든 대화 표시
        for i, (user_question, assistant_answer) in enumerate(conversation_pairs):
            display_conversation_block(i, user_question, assistant_answer, assistant_answer is not None)
    else:
        st.markdown("""
        <div class="summary-box">
            <h3 style="margin: 0 0 10px 0; font-size: 18px;">📊 분석 준비 완료</h3>
            <p style="margin: 0; font-size: 14px; opacity: 0.9;">
                전문적인 주식 기술분석을 시작하려면 아래에 분석할 종목과 요청을 입력해주세요.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # 컨테이너 닫기
    st.markdown('</div>', unsafe_allow_html=True)

# ====== 차트 미리보기 사이드바 (임시 비활성화) ======
# chart_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "workspace", "visualization")
# if os.path.exists(chart_dir):
#     chart_files = [f for f in os.listdir(chart_dir) if f.endswith('.html')]
#     chart_files.sort(key=lambda x: os.path.getmtime(os.path.join(chart_dir, x)), reverse=True)
#     st.sidebar.header(":bar_chart: 차트 미리보기")
#     if chart_files:
#         selected_chart = st.sidebar.selectbox("차트 파일을 선택하세요", chart_files, index=0)
#         chart_path = os.path.join(chart_dir, selected_chart)
#         with open(chart_path, "r", encoding="utf-8") as f:
#             html = f.read()
#         st.components.v1.html(html, height=400, scrolling=True)
#     else:
#         st.sidebar.info("생성된 차트 파일이 없습니다.")
# else:
#     st.sidebar.info("차트 디렉토리가 존재하지 않습니다.")
# ====== 차트 미리보기 끝 ======

# ====== 채팅 메시지 표시 (중복 방지를 위해 주석 처리) ======
# html_previewed = False
# for i, message in enumerate(st.session_state.messages):
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])
#         # assistant 메시지에 .html 경로가 있으면, 해당 html을 본문에 미리보기로 렌더링 (가장 최근 것만)
#         if (
#             message["role"] == "assistant"
#             and not html_previewed
#         ):
#             # 정규표현식으로 .html 경로 추출
#             html_paths = re.findall(r'([\w\-/]+\.html)', message["content"])
#             for html_path in html_paths:
#                 # 절대경로/상대경로 모두 지원
#                 if not os.path.isabs(html_path):
#                     # workspace/visualization 기준 상대경로 처리
#                     html_path_full = os.path.join(os.path.dirname(os.path.dirname(__file__)), "workspace", "visualization", os.path.basename(html_path))
#                 else:
#                     html_path_full = html_path
#                 if os.path.exists(html_path_full):
#                     with open(html_path_full, "r", encoding="utf-8") as f:
#                         html = f.read()
#                     st.components.v1.html(html, height=600, scrolling=True)
#                     html_previewed = True
#                     break

# ====== 전체화면 대시보드 차트 출력 ======
if st.session_state.get("latest_chart_path"):
    st.markdown("---")
    st.markdown("## 전체화면 기술분석 차트")
    st.markdown(
        f'<a href="{st.session_state["latest_chart_path"]}" target="_blank" style="font-size:16px; color:#00adb5;">🔗 새 탭에서 전체화면 보기</a>',
        unsafe_allow_html=True
    )
    try:
        with open(st.session_state["latest_chart_path"], "r", encoding="utf-8") as f:
            chart_html = f.read()
        st.components.v1.html(
            chart_html,
            height=5000,  # 더 크게 지정하여 차트가 끊기지 않게!
            width=1920,
            scrolling=False
        )
    except Exception as e:
        st.error(f"차트를 불러오는 데 실패했습니다: {e}")

# (여기 아래에 추가 질문 입력창이 오도록 유지)

# 프롬프트 입력 (초기 + 추가 질문)
if not st.session_state.waiting_for_response:
    if not st.session_state.messages:
        # 초기 질문
        st.markdown("""
        <div class="section-header">
            분석 요청
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="section-content">', unsafe_allow_html=True)
        user_prompt = st.text_area(
            "분석할 종목과 요청을 입력하세요.",
            key="initial_prompt",
            height=120
        )
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("분석 시작", key="start_analysis", use_container_width=True):
                if user_prompt.strip():
                    st.session_state.messages.append({"role": "user", "content": user_prompt})
                    st.session_state.waiting_for_response = True
                    st.session_state.stop_agent = False
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # 추가 질문
        st.markdown("""
        <div class="section-header">
            추가 분석 요청
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="section-content">', unsafe_allow_html=True)
        user_prompt = st.text_area(
            "추가 질문이 있으시면 입력하세요",
            key="additional_prompt",
            height=100
        )
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("추가 분석", key="additional_analysis", use_container_width=True):
                if user_prompt.strip():
                    st.session_state.messages.append({"role": "user", "content": user_prompt})
                    st.session_state.waiting_for_response = True
                    st.session_state.stop_agent = False
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# 봇 응답 대기 중일 때
if st.session_state.waiting_for_response:
    async def run_agent(prompt):
        agent = await Manus.create()
        st.session_state.stop_agent = False
        st.session_state.current_steps = []  # 새 분석 시작 시 초기화
        # final_response는 초기화하지 않음 (대화 히스토리 유지)

        def on_step_update(step, max_steps):
            # 하단 상태바 대신 실시간 진행상황에 정확한 정보 표시
            step_msg = f"Executing step {step}/{max_steps}"
            # 중복 방지를 위해 마지막 step만 업데이트
            if st.session_state.current_steps and st.session_state.current_steps[-1].startswith("🚀 Executing step"):
                st.session_state.current_steps[-1] = step_msg
            else:
                st.session_state.current_steps.append(step_msg)
            
            # step 완료 시 성공 메시지 추가
            if step == max_steps:
                success_msg = f"모든 Step 완료! ({max_steps}단계)"
                st.session_state.current_steps.append(success_msg)

        def on_ask_human(inquire):
            st.session_state.messages.append({"role": "assistant", "content": inquire})
            st.session_state.waiting_for_response = False
            st.session_state.stop_agent = True
            st.rerun()

        result = await agent.run(prompt, on_step_update=on_step_update, on_ask_human=on_ask_human)
        await agent.cleanup()
        if st.session_state.get("stop_agent"):
            return None  # ask_human 발생 시 분석 중단
        # final_response는 별도로 저장하지 않고 messages에만 저장
        return result

    if st.session_state.messages:
        result = asyncio.run(run_agent(st.session_state.messages[-1]["content"]))
        if result is not None:
            st.session_state.messages.append({"role": "assistant", "content": result})
            st.session_state.waiting_for_response = False
            st.rerun()

# 사용자 응답 입력 (ask_human 상황)
if not st.session_state.waiting_for_response and st.session_state.messages:
    user_input = st.chat_input("답변을 입력하세요...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.human_reply = user_input  # 답변을 세션에 저장
        st.session_state.waiting_for_response = True
        st.session_state.stop_agent = False
        st.rerun()