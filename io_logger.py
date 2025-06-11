import json
import os
import re
from datetime import datetime

# 🚀 AI Agent의 종목명 추출 방식을 사용해요!
from app.agent.stock_name_extractor import StockNameExtractor

LOG_DIR = "results"

# 🚀 AI Agent 인스턴스 생성 (전역적으로 한 번만 생성해서 성능 최적화)
_stock_extractor = None


def get_stock_extractor():
    """
    종목명 추출 AI Agent 인스턴스를 가져오는 함수예요

    처음 호출할 때만 인스턴스를 생성하고, 이후에는 재사용해요 (싱글톤 패턴)
    """
    global _stock_extractor
    if _stock_extractor is None:
        _stock_extractor = StockNameExtractor()
    return _stock_extractor


# 🚀 기존 하드코딩된 키워드 매칭은 분석 타입 추출용으로만 사용
ANALYSIS_KEYWORDS = {
    "종목분석",
    "기술분석",
    "재무분석",
    "뉴스",
    "컨센서스",
    "재무제표",
    "재무비율",
    "투자지표",
    "지분분석",
    "업종분석",
    "경쟁사비교",
    "거래소공시",
    "금감원공시",
    "ETF",
    "ETN",
    "리포트",
    "실적속보",
    "스크리닝",
    "랭킹",
    "캘린더",
    "신용등급",
    "기업주소록",
    "이용안내",
}

# 파일명에 들어갈 수 없는 문자 제거 함수
INVALID_FILENAME_CHARS = r'[\\/:*?"<>|]'


def safe_filename(s):
    s = re.sub(INVALID_FILENAME_CHARS, "", s)
    return s[:20]  # 20자 초과시 잘라서 사용


def extract_stock_with_ai_agent(prompt):
    """
    🚀 AI Agent를 사용해서 종목명을 추출하는 새로운 함수예요!

    기존의 하드코딩된 정규식 패턴 대신 AI Agent의 정교한 알고리즘을 사용해요

    Args:
        prompt: 사용자가 입력한 프롬프트

    Returns:
        dict: AI Agent가 추출한 종목 정보
        {
            "stock_name": "SAMSUNG_ELECTRONICS",  # 영문 종목명
            "ticker": "005930",                   # 종목코드/티커
            "found": True,                        # 종목 발견 여부
            "stock_type": "korean",               # 종목 타입 (korean/foreign/other)
            "market": "KRX"                       # 거래소 (KRX/US/etc)
        }
    """
    try:
        extractor = get_stock_extractor()
        stock_info = extractor.get_extracted_info(prompt)
        return stock_info
    except Exception as e:
        # AI Agent 오류 시 fallback으로 기본값 반환
        return {
            "stock_name": None,
            "ticker": None,
            "found": False,
            "stock_type": "unknown",
            "market": "unknown",
            "error": str(e),
        }


# 🚀 기존 함수들은 AI Agent 방식으로 대체되지만, 하위 호환성을 위해 래퍼로 유지
def extract_stock_from_query(query):
    """🚀 기존 함수의 하위 호환성을 위한 래퍼 - AI Agent 사용"""
    stock_info = extract_stock_with_ai_agent(query)
    return stock_info.get("stock_name") or stock_info.get("ticker")


def extract_stock_from_log(log_path):
    """🚀 로그 파일에서 종목명 추출 - AI Agent 방식 적용"""
    if not log_path or not os.path.exists(log_path):
        return None
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                match = re.search(r"Search results for '([^']+)'", line)
                if match:
                    query = match.group(1)
                    # 🚀 AI Agent로 종목명 추출
                    stock_info = extract_stock_with_ai_agent(query)
                    if stock_info["found"]:
                        return stock_info["stock_name"] or stock_info["ticker"]
    except Exception:
        return None
    return None


def extract_stock_from_text(text_content):
    """🚀 텍스트에서 종목명 추출 - AI Agent 방식으로 완전 교체"""
    # JSON 응답에서 prompt 추출
    prompt_json_match = re.search(r'"prompt":"([^"]+)"', text_content)
    if prompt_json_match:
        stock_info = extract_stock_with_ai_agent(prompt_json_match.group(1))
        if stock_info["found"]:
            return stock_info["stock_name"] or stock_info["ticker"]

    # JSON 응답에서 query 추출
    query_json_match = re.search(r'"query":"([^"]+)"', text_content)
    if query_json_match:
        stock_info = extract_stock_with_ai_agent(query_json_match.group(1))
        if stock_info["found"]:
            return stock_info["stock_name"] or stock_info["ticker"]

    # 직접 텍스트에서 추출
    stock_info = extract_stock_with_ai_agent(text_content)
    if stock_info["found"]:
        return stock_info["stock_name"] or stock_info["ticker"]

    return None


def extract_date_from_text(text):
    # 다양한 날짜/분기/연도 패턴 지원
    patterns = [
        r"([0-9]{4}년 ?[0-9]+월 ?[0-9]+일)",  # 2025년 6월 2일
        r"([0-9]{4}/[0-9]{1,2})",  # 2023/12
        r"([0-9]{4}년 ?[0-9]+분기)",  # 2024년 1분기
        r"([0-9]{4}년 ?[0-9]+월)",  # 2023년 10월
        r"([0-9]{4}년)",  # 2023년
        r"([0-9]{4})",  # 2023
    ]
    for pat in patterns:
        match = re.search(pat, text)
        if match:
            return match.group(1).replace(" ", "")
    return None


def extract_info_from_prompt(prompt):
    stock = extract_stock_from_text(prompt) or "unknown"
    date = extract_date_from_text(prompt) or "unknown"
    # 분석방식
    if re.search(r"재무|financial", prompt, re.I):
        analysis = "financial"
    elif re.search(r"기술|technical", prompt, re.I):
        analysis = "technical"
    elif re.search(r"뉴스|news", prompt, re.I):
        analysis = "news"
    else:
        analysis = "general"
    return stock, analysis, date


def extract_stock_and_date_from_memory(memory):
    # assistant 메시지에서 종목명/날짜 추출, 없으면 프롬프트에서 추출
    stock, date = None, None
    for msg in reversed(getattr(memory, "messages", [])):
        if getattr(msg, "role", None) == "assistant" and getattr(msg, "content", None):
            if not stock:
                stock = extract_stock_from_text(msg.content)
            if not date:
                date = extract_date_from_text(msg.content)
            if stock and date:
                break
    return stock, date


def extract_stock_from_llm_response(response):
    """🚀 LLM 응답에서 종목명 추출 - AI Agent 방식 추가"""
    if not response:
        return None

    # 1. 기존 패턴 유지 (빠른 추출)
    match = re.search(r"종목명[:：]\s*([가-힣A-Za-z0-9]+)", response)
    if match:
        return match.group(1)

    # 2. JSON 응답 처리
    try:
        data = json.loads(response)
        if isinstance(data, dict) and "stock_name" in data:
            return data["stock_name"]
    except Exception:
        pass

    # 3. 🚀 AI Agent로 추가 분석
    stock_info = extract_stock_with_ai_agent(response)
    if stock_info["found"]:
        return stock_info["stock_name"] or stock_info["ticker"]

    return None


def clean_stock_name(name):
    # 연도/날짜 패턴 제거 (예: 2025년, 2023, 2024, 2025 등)
    name = re.sub(r"(20[0-9]{2}년?|19[0-9]{2}년?)", "", name)
    return name.strip()


def save_interaction_log(
    prompt, response, steps=None, meta=None, memory=None, log_path=None
):
    """
    🚀 사용자 상호작용을 첨부된 JSON 파일 형식과 동일하게 저장하는 함수예요

    AI Agent를 사용해서 정교하게 종목명을 추출해요!

    저장 형식:
    {
      "timestamp": "20250610_090142",
      "prompt": "사용자 질문...",
      "response": "AI 응답...",
      "steps": ["단계별 실행 내용..."],
      "meta": {}
    }
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    stock, date = None, None

    # 🚀 1순위: AI Agent로 프롬프트에서 종목명 추출 (가장 정확함)
    stock_info = extract_stock_with_ai_agent(prompt)
    if stock_info["found"]:
        stock = stock_info["stock_name"] or stock_info["ticker"]
        # AI Agent가 추출한 정보를 meta에 저장
        if meta is None:
            meta = {}
        meta["ai_extracted_stock_info"] = stock_info

    # 2순위: LLM 응답에서 종목명 추출
    if not stock:
        stock = extract_stock_from_llm_response(response)

    # 3순위: log_path가 주어지면 log에서 종목명 추출
    if not stock and log_path:
        stock = extract_stock_from_log(log_path)

    # 4순위: 기존 방식 fallback
    if not stock and memory is not None:
        stock, date = extract_stock_and_date_from_memory(memory)

    # 5순위: 구 방식 프롬프트 추출 (최후의 수단)
    if not stock:
        stock_from_prompt_tuple = extract_info_from_prompt(prompt)
        stock = stock_from_prompt_tuple[0]

    if not stock:
        stock = "unknown"

    stock = safe_filename(stock)
    if not stock:
        stock = "unknown"

    if not date or date == "unknown":
        date = now
        date_only = date[:8]
    elif isinstance(date, str) and len(date) >= 8:
        date_only = date[:8]
    else:
        date_fallback = datetime.now().strftime("%Y%m%d")
        date_only = date_fallback[:8]

    _, analysis, _ = extract_info_from_prompt(prompt)
    analysis = safe_filename(analysis)

    filename = f"{LOG_DIR}/json-agent-{stock}-{analysis}-at{date_only}-save{now}.json"

    # 🚀 첨부된 JSON 파일과 동일한 형식으로 저장
    # steps 데이터를 문자열 배열로 변환 (기존 형식에 맞춤)
    formatted_steps = []
    if steps:
        for step in steps:
            if isinstance(step, dict):
                # dict 형태의 step을 문자열로 변환
                if "response" in step:
                    formatted_steps.append(step["response"])
                elif "message" in step:
                    formatted_steps.append(step["message"])
                else:
                    # 전체 dict를 문자열로 변환
                    formatted_steps.append(str(step))
            else:
                # 이미 문자열이면 그대로 사용
                formatted_steps.append(str(step))

    # 🚀 첨부된 파일처럼 사람이 읽기 편한 JSON 구조로 저장
    data = {
        "timestamp": now,
        "prompt": prompt,
        "response": response,
        "steps": formatted_steps,
        "meta": meta or {},
    }

    # 🚀 사람이 스크롤하면서 읽기 편하도록 멀티라인 JSON으로 저장해요!
    with open(filename, "w", encoding="utf-8") as f:
        # 완전히 새로운 방식: JSON 파일 자체를 여러 줄로 나누어서 저장
        f.write("{\n")
        f.write(f'  "timestamp": "{data["timestamp"]}",\n')

        # prompt를 여러 줄로 포맷팅
        f.write('  "prompt": ')
        _write_multiline_string(f, data["prompt"], indent_level=2)
        f.write(",\n")

        # response를 여러 줄로 포맷팅
        f.write('  "response": ')
        _write_multiline_string(f, data["response"], indent_level=2)
        f.write(",\n")

        # steps 배열을 읽기 편하게 포맷팅
        f.write('  "steps": [\n')
        for i, step in enumerate(data["steps"]):
            comma = "," if i < len(data["steps"]) - 1 else ""
            f.write("    ")
            _write_multiline_string(f, str(step), indent_level=4)
            f.write(f"{comma}\n")
        f.write("  ],\n")

        # meta 객체를 표준 JSON으로 저장
        f.write('  "meta": ')
        json.dump(data["meta"], f, ensure_ascii=False, indent=4)
        f.write("\n")
        f.write("}")
    return filename


def _write_multiline_string(file, text, indent_level=0, max_line_length=80):
    """
    🚀 긴 텍스트를 여러 줄 JSON 문자열로 작성하는 함수예요

    JSON 파일 자체가 여러 줄로 나뉘어서 사람이 읽기 편하게 만들어요!

    Args:
        file: 쓸 파일 객체
        text: 작성할 텍스트
        indent_level: 들여쓰기 레벨
        max_line_length: 한 줄 최대 길이
    """
    if not isinstance(text, str):
        text = str(text)

    indent = " " * indent_level

    # 특수문자 이스케이프
    text = text.replace("\\", "\\\\")
    text = text.replace('"', '\\"')
    text = text.replace("\r", "\\r")
    text = text.replace("\t", "\\t")
    text = text.replace("\b", "\\b")
    text = text.replace("\f", "\\f")

    # 기존 줄바꿈 처리
    lines = text.split("\n")

    # 첫 번째 줄 시작
    file.write('"')

    for line_idx, line in enumerate(lines):
        if line_idx > 0:
            file.write('\\n" +\n' + indent + '"')

        # 긴 줄을 나누기
        if len(line) <= max_line_length:
            file.write(line)
        else:
            words = line.split(" ")
            current_line = ""
            word_written = False

            for word in words:
                test_line = current_line + (" " if current_line else "") + word

                if len(test_line) <= max_line_length:
                    current_line = test_line
                else:
                    if current_line:
                        file.write(current_line)
                        file.write('" +\n' + indent + '"')
                        current_line = word
                        word_written = True
                    else:
                        current_line = word

            if current_line:
                file.write(current_line)

    file.write('"')


# 🚀 기존 함수들은 새로운 멀티라인 방식으로 대체되었어요!
