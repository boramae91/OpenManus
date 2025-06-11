import json
import os
import re
from datetime import datetime

LOG_DIR = "results"

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


def extract_stock_from_query(query):
    # 검색 쿼리에서 종목명 추출
    # 예: "Disney company technical analysis 2023" -> "Disney"
    # 예: "TSLA stock analysis October 2023" -> "TSLA"
    # 예: "두산에너빌리티 기술분석 2023" -> "두산에너빌리티"

    # 1. 영문 종목명/티커 패턴
    patterns = [
        r"([A-Z]{2,10})\s+stock",  # TSLA stock
        r"([A-Z]{2,10})\s+company",  # Disney company
        r"([A-Z]{2,10})\s+technical",  # DIS technical
        r"([A-Z]{2,10})\s+financial",  # DIS financial
    ]

    # 2. 한글 종목명 패턴
    korean_patterns = [
        r"([가-힣]{2,20})\s+기술분석",  # 두산에너빌리티 기술분석
        r"([가-힣]{2,20})\s+재무분석",  # 두산에너빌리티 재무분석
        r"([가-힣]{2,20})\s+뉴스",  # 두산에너빌리티 뉴스
    ]

    # 영문 패턴 검사
    for pat in patterns:
        match = re.search(pat, query, re.I)
        if match:
            return match.group(1)

    # 한글 패턴 검사
    for pat in korean_patterns:
        match = re.search(pat, query)
        if match:
            return match.group(1)

    return None


def extract_stock_from_log(log_path):
    if not log_path or not os.path.exists(log_path):
        return None
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                match = re.search(r"Search results for '([^']+)'", line)
                if match:
                    query = match.group(1)
                    # 분석 키워드 앞까지 전체 추출
                    m2 = re.search(r"^([가-힣A-Za-z0-9]+)", query)
                    # 분석 키워드 앞까지(공백 포함) 추출
                    m3 = re.search(
                        r"^([가-힣A-Za-z0-9 ]+?)(종목 ?분석|기술 ?분석|재무 ?분석|뉴스|분석|\\d{4})",
                        query,
                    )
                    if m3:
                        return m3.group(1).strip().replace(" ", "")
                    elif m2:
                        return m2.group(1).strip()
    except Exception:
        return None
    return None


def extract_stock_from_text(text_content):
    def normalize_stock_name(name):
        # 분석 키워드 제거
        for keyword in ANALYSIS_KEYWORDS:
            name = name.replace(keyword, "")
        # 조사 제거
        for particle in ["에 대해", "에대한", "에", "에대해"]:
            name = name.replace(particle, "")
        # 연도/날짜 패턴 제거
        name = re.sub(r"(20[0-9]{2}년?|19[0-9]{2}년?)", "", name)
        # 앞뒤 공백 제거
        name = name.strip()
        # 띄어쓰기 제거
        name = name.replace(" ", "")
        # 길이 체크
        if len(name) <= 2 and name.upper() not in ["KB", "LG", "SK"]:
            return None
        if len(name) > 20:
            return None
        return name

    def extract_from_prompt(prompt):
        # 복합명사 패턴 (띄어쓰기 포함)
        patterns = [
            # 한글 복합명사 (띄어쓰기 포함)
            r"([가-힣]{2,10}\s*[가-힣]{2,10})",
            # 한글+영문 복합명사
            r"([가-힣]{2,10}\s*[A-Za-z]{2,10})",
            # 영문+한글 복합명사
            r"([A-Za-z]{2,10}\s*[가-힣]{2,10})",
            # 영문 복합명사
            r"([A-Za-z]{2,10}\s*[A-Za-z]{2,10})",
            # 단일 한글/영문/숫자
            r"([가-힣A-Za-z0-9]{2,20})",
        ]

        for pattern in patterns:
            match = re.search(pattern, prompt)
            if match:
                stock_name = match.group(1).strip()
                normalized = normalize_stock_name(stock_name)
                if normalized:
                    return normalized
        return None

    # JSON 응답에서 prompt 추출
    prompt_json_match = re.search(r'"prompt":"([^"]+)"', text_content)
    if prompt_json_match:
        stock = extract_from_prompt(prompt_json_match.group(1))
        if stock:
            return stock

    # JSON 응답에서 query 추출
    query_json_match = re.search(r'"query":"([^"]+)"', text_content)
    if query_json_match:
        stock = extract_from_prompt(query_json_match.group(1))
        if stock:
            return stock

    # 직접 텍스트에서 추출
    stock_from_direct_text = extract_from_prompt(text_content)
    if stock_from_direct_text:
        return stock_from_direct_text

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
    # "종목명: KB증권" 또는 JSON {"stock_name": "KB증권"} 형태 지원
    if not response:
        return None
    # 1. "종목명: KB증권" 패턴
    match = re.search(r"종목명[:：]\s*([가-힣A-Za-z0-9]+)", response)
    if match:
        return match.group(1)
    # 2. JSON 응답
    try:
        data = json.loads(response)
        if isinstance(data, dict) and "stock_name" in data:
            return data["stock_name"]
    except Exception:
        pass
    return None


def clean_stock_name(name):
    # 연도/날짜 패턴 제거 (예: 2025년, 2023, 2024, 2025 등)
    name = re.sub(r"(20[0-9]{2}년?|19[0-9]{2}년?)", "", name)
    return name.strip()


def save_interaction_log(
    prompt, response, steps=None, meta=None, memory=None, log_path=None
):
    os.makedirs(LOG_DIR, exist_ok=True)
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    stock, date = None, None

    # 1순위: LLM 응답에서 종목명 추출
    stock = extract_stock_from_llm_response(response)

    # 2순위: log_path가 주어지면 log에서 종목명 추출
    if not stock and log_path:
        stock = extract_stock_from_log(log_path)

    # 3순위: 기존 방식 fallback
    if not stock and memory is not None:
        stock, date = extract_stock_and_date_from_memory(memory)

    # 4순위: 프롬프트에서 추출
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
    data = {
        "timestamp": now,
        "prompt": prompt,
        "response": response,
        "steps": steps or [],
        "meta": meta or {},
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filename
