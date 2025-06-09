import asyncio
import json  # JSON 형식으로 저장하기 위해 필요한 모듈을 추가해요
import os
import re  # 종목명 추출을 위한 정규표현식 모듈을 추가해요
import time
from datetime import datetime

from app.agent.manus import Manus
from app.agent.stock_classifier import StockClassifier
from app.flow.flow_factory import FlowFactory, FlowType
from app.logger import logger


def save_json_file(
    content,
    filename,
    prompt="",
    processing_time=0,
    flow_type="PLANNING",
    classification_data=None,
    stock_info=None,
):
    """
    Flow 실행 결과를 JSON 형식으로 저장하는 함수예요 (분류 정보 포함)
    - content: Flow 실행 결과 내용 (문자열)
    - filename: 저장할 파일 이름
    - prompt: 사용자가 입력한 질문 (이것이 key가 돼요)
    - processing_time: 처리하는데 걸린 시간 (초 단위)
    - flow_type: 실행한 Flow의 종류
    - classification_data: 종목 분류 결과 (딕셔너리)
    - stock_info: 종목 정보 (딕셔너리)
    """

    if not prompt.strip():
        # 프롬프트가 비어있으면 기본 키를 사용해요
        prompt = "User Flow Question"

    # 기존 형식 유지: 질문을 key로, Flow 실행 결과를 value로 저장
    json_data = {prompt: content}  # 질문을 key로, Flow 실행 결과를 value로 저장해요

    # 분류 정보가 있으면 추가 (기존 구조 유지하면서 확장)
    if classification_data:
        json_data["stock_classification"] = classification_data

    # 종목 정보가 있으면 추가
    if stock_info:
        json_data["stock_info"] = stock_info

    # Flow 관련 정보와 처리 시간은 별도 필드로 추가
    json_data["analysis_type"] = "Flow"
    json_data["flow_type"] = flow_type
    if processing_time > 0:
        json_data["processing_time_seconds"] = processing_time
    json_data["timestamp"] = datetime.now().isoformat()

    # JSON 파일로 저장해요 (한글도 제대로 저장되도록 설정)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    logger.info(f"Flow result saved to JSON: {filename}")


class ResultCollector:
    def __init__(self):
        self.result = ""

    def add_to_result(self, text):
        if text:
            self.result += text + "\n"

    def get_result(self):
        return self.result


def extract_stock_name(prompt):
    """
    프롬프트에서 기본적인 종목명을 추출하는 간단한 fallback 함수예요 (AI 분석 실패시에만 사용)
    - prompt: 사용자가 입력한 질문
    - 반환값: 추출된 종목명 (없으면 "GENERAL" 반환)
    """
    if not prompt or not prompt.strip():
        return "GENERAL"

    # 6자리 종목코드만 확인 (가장 정확한 정보)
    code_pattern = r"(\d{6})"
    code_matches = re.findall(code_pattern, prompt)
    if code_matches:
        return f"CODE{code_matches[0]}"

    # AI 분석이 실패했을 때만 사용하는 최소한의 fallback
    # 대부분의 경우 AI Flow가 정확하게 종목명을 추출할 것으로 예상
    return "GENERAL"


def extract_stock_code_from_text(text):
    """
    텍스트에서 한국 종목코드(6자리)를 추출하는 함수예요
    해외 종목은 티커 심볼을 사용하므로 6자리 숫자만 한국 종목코드로 인식합니다
    - text: 분석할 텍스트
    - 반환값: 추출된 종목코드 (없으면 None)
    """
    if not text or not text.strip():
        return None

    # 한국 종목코드만 찾기 (6자리 숫자이면서 종목코드 형태인 것만)
    # 일반적인 6자리 숫자는 제외하고, 명시적으로 종목코드 패턴인 것만 추출
    code_patterns = [
        r"(?:종목코드|코드|Code)\s*[:=]?\s*([0-9]{6})",  # "종목코드: 005930" 형태
        r"([0-9]{6})\s*(?:종목|주식)",  # "005930 종목" 형태
        r"\(([0-9]{6})\)",  # "(005930)" 형태
        r"A([0-9]{6})",  # "A005930" 형태 (한국거래소 표기)
    ]

    for pattern in code_patterns:
        code_matches = re.findall(pattern, text, re.IGNORECASE)
        if code_matches:
            # 한국 종목코드 범위 확인 (000001~999999 중 실제 거래되는 범위)
            code = code_matches[0]
            if (
                code.startswith("0")
                or code.startswith("1")
                or code.startswith("2")
                or code.startswith("3")
            ):
                return code  # 한국 종목코드로 보이는 경우만 반환

    return None


def generate_json_filename(
    stock_name, stock_code=None, base_dir="results", file_type="flow"
):
    """
    JSON 파일명을 생성하는 함수예요 (사용자 요청 형식)
    형식: JSON-종목코드-종목명-현재시간-save현재시간.json
    - stock_name: 종목명 (영문)
    - stock_code: 종목코드/티커 (선택사항)
    - base_dir: 저장할 폴더명
    - file_type: 파일 타입 (flow, timeout, cancelled, error)
    """
    # 현재 시간을 문자열로 변환 (년월일_시분초 형식)
    current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_timestamp = current_timestamp  # 현재시간과 저장시간이 동일해요

    # 종목코드 부분 결정
    if stock_code:
        # 종목코드가 있으면 그대로 사용
        code_part = stock_code
    else:
        # 종목코드가 없으면 종목명에서 추출하거나 UNKNOWN 사용
        code_part = convert_to_english_ticker(stock_name)
        if code_part == stock_name and not (
            code_part.isupper() and code_part.isalpha() and 2 <= len(code_part) <= 5
        ):
            code_part = "UNKNOWN"

    # 종목명 부분 정리 (파일명에 적합하게)
    clean_stock_name = stock_name if stock_name else "GENERAL"

    # 파일명 생성 (사용자 요청 형식: JSON-종목코드-종목명-현재시간-save현재시간.json)
    if file_type == "flow":
        filename = f"JSON-{code_part}-{clean_stock_name}-{current_timestamp}-save{save_timestamp}.json"
    else:
        # 특수한 경우 (timeout, cancelled, error)에는 파일명에 타입을 포함시켜요
        filename = f"JSON-{code_part}-{clean_stock_name}-{file_type}-{current_timestamp}-save{save_timestamp}.json"

    # 전체 경로 생성
    full_path = os.path.join(base_dir, filename)

    return full_path


def extract_stock_candidates_from_text(text):
    """
    텍스트에서 종목명 후보들을 추출하는 헬퍼 함수예요
    - text: 분석할 텍스트 (프롬프트 또는 AI 응답)
    - 반환값: 발견된 종목명 후보들의 리스트
    """
    candidates = []

    if not text or not text.strip():
        return candidates

    # 1. 6자리 종목코드 찾기
    code_pattern = r"(\d{6})"
    code_matches = re.findall(code_pattern, text)
    for code in code_matches:
        candidates.append(f"CODE{code}")

    # 2. 한글 회사명 패턴 찾기 (AI가 추출하지 못한 경우를 위한 보완)
    korean_pattern = r"\b([가-힣]{2,10})\b"
    korean_matches = re.findall(korean_pattern, text)
    for match in korean_matches:
        # 일반적인 단어들 제외
        exclude_words = {
            "분석",
            "종목",
            "기업",
            "정보",
            "결과",
            "전망",
            "투자",
            "주식",
            "시장",
            "수익률",
            "거래량",
            "매출",
            "영업이익",
            "코스피",
            "코스닥",
            "거래",
            "전일",
            "대비",
        }
        if match not in exclude_words and len(match) >= 2:
            candidates.append(match)

    # 3. 구체적 패턴으로 회사명 찾기
    specific_patterns = [
        r"([가-힣A-Za-z0-9]+)(?:의\s*(?:주가|주식|분석|전망|실적))",
        r"([가-힣A-Za-z0-9]+)(?:\s*주식\s*분석)",
        r"([가-힣A-Za-z0-9]+)(?:\s*\(\s*[A-Z]?\d{6}\s*\))",
        r"([가-힣A-Za-z0-9]+)(?:에\s*대한\s*(?:분석|전망))",
        r"([가-힣A-Za-z0-9]+)(?:\s*(?:분석|전망)\s*(?:결과|정보))",
    ]

    for pattern in specific_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            exclude_words = [
                "주식",
                "투자",
                "분석",
                "시장",
                "종목",
                "기업",
                "회사",
                "정보",
                "결과",
                "전망",
            ]
            if match not in exclude_words and len(match) >= 2 and len(match) <= 25:
                candidates.append(match)

    return candidates


def get_stock_name_from_code(stock_code):
    """
    종목코드로 실제 종목명을 찾는 함수예요 (AI 분석 실패시 fallback 용도)
    - stock_code: 6자리 종목코드
    - 반환값: 매핑된 종목명 (없으면 None, AI가 대부분 처리할 것으로 예상)
    """
    # AI 분석이 실패했을 때만 사용하는 최소한의 매핑
    # 대부분의 경우 AI Flow가 정확하게 종목명을 추출할 것으로 예상
    if not stock_code:
        return None

    # 종목코드 그대로 반환하여 AI가 처리하도록 함
    return f"CODE{stock_code}"


def find_most_frequent_stock_name(ai_response):
    """
    AI 에이전트 서칭 결과에서 가장 빈번하게 등장하는 종목명을 찾는 함수예요 (해외 종목 지원)
    - ai_response: AI가 생성한 분석 결과 텍스트
    - 반환값: (가장 빈번한 종목명, 출현횟수) 튜플
    """
    from collections import Counter

    if not ai_response or not ai_response.strip():
        return None, 0

    # 종목명 후보들을 찾을 패턴들
    candidates = []

    # 0. 우선순위 높은 정확한 한국 종목명들 (정확한 매칭)
    priority_stocks = [
        "삼성바이오로직스",
        "삼성전자",
        "삼성SDI",
        "삼성화재",
        "삼성물산",
        "삼성증권",
        "SK하이닉스",
        "SK텔레콤",
        "SK이노베이션",
        "LG전자",
        "LG화학",
        "LG에너지솔루션",
        "현대로템",  # 현대로템 추가 (우선순위)
        "현대자동차",
        "현대모비스",
        "기아",
        "포스코",
        "포스코홀딩스",
        "네이버",
        "카카오",
        "카카오뱅크",
        "셀트리온",
        "셀트리온헬스케어",
        "한화에어로스페이스",
        "한화시스템",
        "한화솔루션",
        "휴니드",
        "한컴라이프케어",
        "메리츠증권",
    ]

    # 우선순위 종목들이 있는지 먼저 확인 (정확한 매칭으로 개선)
    for stock in priority_stocks:
        # 정확한 단어 경계를 사용하여 매치 (부분 매칭 방지)
        pattern = r"\b" + re.escape(stock) + r"\b"
        matches = re.findall(pattern, ai_response)
        if matches:
            count = len(matches)
            candidates.extend([stock] * (count * 10))  # 높은 가중치

    # 1. 한글 회사명 (2-10글자) - 한국 종목용
    korean_pattern = r"\b([가-힣]{2,10})\b"
    korean_matches = re.findall(korean_pattern, ai_response)
    candidates.extend(korean_matches)

    # 2. 해외 회사명 패턴 (공백 포함, Inc/Corp/Ltd 등 포함)
    # 예: "Apple Inc", "Microsoft Corporation", "Tesla Inc"
    foreign_company_pattern = r"\b([A-Z][a-zA-Z0-9\s]{2,25}(?:Inc|Corp|Corporation|Ltd|LLC|Co|Company|Group|Holdings|Technologies|Systems|Solutions)\.?)\b"
    foreign_matches = re.findall(foreign_company_pattern, ai_response)
    # 해외 회사명은 가중치를 더 줘요 (더 정확한 패턴이므로)
    candidates.extend(foreign_matches * 2)

    # 3. 일반 영문 회사명 (단어 하나) - 간단한 경우
    english_pattern = r"\b([A-Z][A-Za-z0-9]{1,14})\b"
    english_matches = re.findall(english_pattern, ai_response)
    candidates.extend(english_matches)

    # 4. 티커 심볼 패턴 (2-5글자 대문자) - 해외 주식에서 중요
    # 예: AAPL, MSFT, TSLA, GOOGL
    ticker_pattern = r"\b([A-Z]{2,5})\b"
    ticker_matches = re.findall(ticker_pattern, ai_response)
    # 티커는 매우 정확하므로 높은 가중치
    candidates.extend(ticker_matches * 4)

    # 5. 괄호와 함께 나오는 회사명 (가장 정확함) - 한국/해외 모두
    bracket_pattern = r"([가-힣A-Za-z0-9\s]+)\s*\([A-Z]?[0-9A-Z]{2,6}\)"
    bracket_matches = re.findall(bracket_pattern, ai_response)
    # 괄호 패턴은 최고 가중치
    candidates.extend([match.strip() for match in bracket_matches] * 5)

    # 일반적인 단어들 제외 (한국어 + 영어)
    exclude_words = {
        # 한국어 제외 단어
        "분석",
        "종목",
        "기업",
        "정보",
        "결과",
        "전망",
        "투자",
        "주식",
        "시장",
        "수익률",
        "거래량",
        "매출",
        "영업이익",
        "당기순이익",
        "지배주주",
        "외국인",
        "보유비중",
        "시가총액",
        "배당수익률",
        "상대수익률",
        "거래",
        "전일",
        "대비",
        "코스피",
        "전기",
        "전자",
        "통신장비",
        "기준",
        "결산",
        "연간",
        "구성종목",
        # 영어 제외 단어 (금융/기술 용어)
        "KOSPI",
        "PER",
        "PBR",
        "EPS",
        "BPS",
        "DPS",
        "Price",
        "Earning",
        "Ratio",
        "Book",
        "value",
        "Company",
        "Guide",
        "Snapshot",
        "Main",
        "ASP",
        "SVD",
        "URL",
        "Description",
        "Content",
        "http",
        "www",
        "com",
        "HOME",
        "PAGE",
        "Step",
        "Observed",
        "output",
        "cmd",
        "browser",
        "use",
        "executed",
        "Search",
        "results",
        "for",
        "Total",
        "Language",
        "Country",
        "Extracted",
        "from",
        "page",
        "text",
        "company",
        "listed",
        "under",
        "sector",
        "fiscal",
        "year",
        "ending",
        "website",
        "contacted",
        "address",
        "Key",
        "financial",
        "metrics",
        "include",
        "based",
        "most",
        "recent",
        "Industry",
        "Stock",
        "performance",
        "indicators",
        "Current",
        "stock",
        "price",
        "Foreign",
        "ownership",
        "percentage",
        "Relative",
        "return",
        "over",
        "past",
        "summary",
        "these",
        "provide",
        "snapshot",
        "health",
        "market",
        "need",
        "further",
        "specific",
        "details",
        "know",
        "interaction",
        "has",
        "been",
        "completed",
        "with",
        "status",
        "success",
        # 해외 종목 관련 제외 단어
        "NYSE",
        "NASDAQ",
        "AMEX",
        "LSE",
        "TSE",
        "HKEX",
        "SSE",
        "SZSE",
        "Exchange",
        "Market",
        "Index",
        "Fund",
        "ETF",
        "REITs",
        "ADR",
        "GDR",
        "Revenue",
        "Profit",
        "Loss",
        "Income",
        "Assets",
        "Liabilities",
        "Equity",
        "Dividend",
        "Yield",
        "Growth",
        "Volume",
        "Shares",
        "Outstanding",
        "Float",
        "Beta",
        "Alpha",
        "Volatility",
        "Correlation",
        "Analysis",
        "Report",
        "Quarter",
        "Annual",
        "Monthly",
        "Weekly",
        "Daily",
        "News",
        "Data",
        "Technology",
        "Finance",
        "Healthcare",
        "Energy",
        "Materials",
        "Utilities",
        "Consumer",
        "Industrial",
        "Communication",
        "Services",
        "Real",
        "Estate",
    }

    # 필터링된 후보들만 선택
    filtered_candidates = []
    for candidate in candidates:
        candidate = candidate.strip()
        # 기본 필터링
        if (
            candidate not in exclude_words
            and len(candidate) >= 2
            and len(candidate) <= 30  # 해외 종목명이 길 수 있으므로 30으로 증가
            and not candidate.isdigit()
            and not candidate.replace(".", "").isdigit()
        ):  # 숫자만인 것 제외

            # 추가 필터링: 너무 일반적인 단어들 제외
            common_words = [
                "THE",
                "AND",
                "OR",
                "BUT",
                "IN",
                "ON",
                "AT",
                "TO",
                "FOR",
                "OF",
                "WITH",
                "BY",
            ]
            if candidate.upper() not in common_words:
                filtered_candidates.append(candidate)

    if not filtered_candidates:
        return None, 0

    # 빈도수 계산
    frequency_counter = Counter(filtered_candidates)
    most_common = frequency_counter.most_common(1)[0]

    logger.info(f"종목명 빈도수 분석 결과: {frequency_counter}")
    logger.info(f"가장 빈번한 종목명: {most_common[0]} (출현횟수: {most_common[1]})")

    return most_common[0], most_common[1]


def convert_to_english_ticker(company_name):
    """
    회사명을 영문 티커로 변환하는 함수예요 (AI 분석 결과를 우선 사용, fallback 용도로만 활용)
    - company_name: 회사명 (한글, 영문, 또는 티커)
    - 반환값: 원본 회사명 (AI가 이미 정확하게 추출했을 것으로 가정)
    """
    if not company_name:
        return "UNKNOWN"

    company_name = company_name.strip()

    # 이미 티커 형태인지 확인 (2-5글자 대문자)
    if (
        company_name.isupper()
        and company_name.isalpha()
        and 2 <= len(company_name) <= 5
    ):
        return company_name  # 이미 티커이므로 그대로 반환

    # 해외 회사명에서 법인 형태 제거하고 티커 형태로 변환
    # 예: "Apple Inc" -> "APPLE", "Microsoft Corporation" -> "MICROSOFT"
    company_clean = company_name
    legal_suffixes = [
        r"Inc\.?",
        r"Corp\.?",
        "Corporation",
        r"Ltd\.?",
        "LLC",
        r"Co\.?",
        "Company",
        "Group",
        "Holdings",
        "Technologies",
        "Systems",
        "Solutions",
        "Services",
    ]

    for suffix in legal_suffixes:
        company_clean = re.sub(rf"\s+{suffix}$", "", company_clean, flags=re.IGNORECASE)

    # AI 분석 결과를 최대한 활용하기 위해 하드코딩 매핑 최소화
    # 대부분의 경우 AI Flow가 정확하게 종목명을 추출할 것으로 예상

    # 이미 영문이고 적절한 길이면 대문자로 변환
    if company_clean.replace(" ", "").isalpha() and all(
        ord(char) < 128 or char == " " for char in company_clean
    ):
        # 공백 제거하고 대문자로
        ticker = company_clean.replace(" ", "").upper()
        # 너무 길면 앞의 일부만 사용 (최대 10글자)
        if len(ticker) > 10:
            ticker = ticker[:10]
        return ticker

    # 한글이거나 기타인 경우 원본 그대로 반환 (AI가 이미 정확하게 처리했을 것으로 가정)
    return company_name


def cross_verify_stock_name(prompt, ai_response):
    """
    AI Flow 응답에서 가장 빈번한 종목명을 찾고, 프롬프트와 비교해서 검증하는 함수예요
    - prompt: 사용자가 입력한 질문
    - ai_response: AI Flow가 생성한 분석 결과
    - 반환값: (종목명, 종목코드) 튜플
    """
    # AI 응답에서 가장 빈번한 종목명 찾기
    most_frequent_name, frequency = find_most_frequent_stock_name(ai_response)

    # 종목코드 추출
    response_code = extract_stock_code_from_text(ai_response)
    prompt_code = extract_stock_code_from_text(prompt)
    final_code = response_code or prompt_code

    logger.info(
        f"AI Flow 응답에서 가장 빈번한 종목명: {most_frequent_name} (빈도: {frequency})"
    )
    logger.info(f"추출된 종목코드: {final_code}")

    # 빈도수가 충분히 높으면 (2번 이상 나타나면) 신뢰할 만함
    if most_frequent_name and frequency >= 2:
        english_ticker = convert_to_english_ticker(most_frequent_name)
        logger.info(
            f"빈도수 기반 종목명 확정: {most_frequent_name} -> {english_ticker}"
        )
        return english_ticker, final_code

    # 빈도수가 낮으면 프롬프트에서 찾아보기
    if most_frequent_name and frequency == 1:
        # 프롬프트에서도 같은 이름이 나오는지 확인
        if most_frequent_name in prompt:
            english_ticker = convert_to_english_ticker(most_frequent_name)
            logger.info(
                f"프롬프트 교차검증 성공: {most_frequent_name} -> {english_ticker}"
            )
            return english_ticker, final_code

    # 종목코드만 있는 경우
    if final_code:
        logger.info(f"종목코드만 발견: {final_code}")
        return f"CODE{final_code}", final_code

    # 아무것도 찾지 못한 경우
    return "GENERAL", None


def extract_stock_name_from_ai_response(response_text, fallback_prompt=""):
    """
    AI Flow가 실제로 분석한 결과에서 종목명과 종목코드를 추출하는 함수예요 (교차 검증 포함)
    - response_text: AI Flow가 생성한 분석 결과 텍스트
    - fallback_prompt: 응답에서 찾지 못할 경우 사용할 원본 프롬프트
    - 반환값: (종목명, 종목코드) 튜플
    """
    # 교차 검증을 통한 종목명과 종목코드 추출 시도
    stock_name, stock_code = cross_verify_stock_name(fallback_prompt, response_text)
    if stock_name:
        logger.info(
            f"교차 검증으로 최종 확정된 종목명: {stock_name}, 종목코드: {stock_code}"
        )
        return stock_name, stock_code

    # 교차 검증 실패 시 기존 방식으로 fallback
    logger.info("교차 검증 실패, 기존 방식으로 종목명 추출 시도")
    fallback_name = extract_stock_name(fallback_prompt)
    fallback_code = extract_stock_code_from_text(
        response_text
    ) or extract_stock_code_from_text(fallback_prompt)
    return fallback_name, fallback_code


async def run_flow():
    # 결과 수집기 생성
    result_collector = ResultCollector()

    agents = {
        "manus": Manus(),
    }

    # 종목 분류 에이전트 생성
    stock_classifier = StockClassifier()

    try:
        prompt = input("Enter your prompt: ")

        if prompt.strip().isspace() or not prompt:
            logger.warning("Empty prompt provided.")
            return

        # 종목 분류 요청인지 확인해요 (키워드 기반 + 종목 감지 기반)
        classification_keywords = [
            "분류",
            "classify",
            "유형",
            "type",
            "저성장주",
            "우량주",
            "고성장주",
            "자산주",
            "턴어라운드주",
            "시이클주",
            "기타주",
            "어떤 종류",
            "어떤 유형",
            "분석",
            "analyze",
            "어떤 주식",
            "어떤 종목",
            "성격",
            "특성",
            "투자유형",
            "투자 유형",
        ]

        # 1. 키워드 기반 감지
        is_classification_request_by_keyword = any(
            keyword in prompt.lower() for keyword in classification_keywords
        )

        # 2. 종목 감지 기반 - 종목명이나 종목코드가 발견되면 자동으로 분류도 실행
        detected_stock_info = extract_stock_name(prompt)
        has_stock_detected = detected_stock_info != "GENERAL"

        # 최종 판단: 키워드가 있거나 종목이 감지되면 분류 실행
        is_classification_request = (
            is_classification_request_by_keyword or has_stock_detected
        )

        # 분류 실행 이유를 로그에 기록
        if is_classification_request:
            if is_classification_request_by_keyword and has_stock_detected:
                logger.info("종목 분류 실행 - 키워드 감지 + 종목 감지")
            elif is_classification_request_by_keyword:
                logger.info("종목 분류 실행 - 키워드 감지")
            elif has_stock_detected:
                logger.info(f"종목 분류 실행 - 종목 자동 감지: {detected_stock_info}")
        else:
            logger.info("종목 분류 실행 안함 - 키워드나 종목 감지되지 않음")

        flow = FlowFactory.create_flow(
            flow_type=FlowType.PLANNING,
            agents=agents,
        )
        logger.warning("Processing your request...")
        print("\n--- FLOW EXECUTION RESULTS ---\n")

        # 종목 분류 요청이면 분류 에이전트를 먼저 실행해요
        if is_classification_request:
            if is_classification_request_by_keyword and has_stock_detected:
                print(
                    f"🏷️ 종목 분류 분석을 실행합니다... (키워드 + 종목 감지: {detected_stock_info})\n"
                )
            elif is_classification_request_by_keyword:
                print("🏷️ 종목 분류 분석을 실행합니다... (키워드 감지)\n")
            elif has_stock_detected:
                print(
                    f"🏷️ 종목 분류 분석을 자동 실행합니다... (종목 감지: {detected_stock_info})\n"
                )

            classification_result = await stock_classifier.classify_stock(prompt)

            # 분류 결과를 결과 수집기에 추가 (전체 결과 포함!)
            if classification_result.get("classification"):
                # 요약본 (화면 출력용)
                classification_summary = f"""
=== 종목 분류 결과 ===
🏷️ 분류: {classification_result['classification']['classification']}
📊 신뢰도: {classification_result['classification']['confidence']}
📋 근거: {', '.join(classification_result['classification']['reasoning'][:3])}

--- Flow 상세 분석은 아래를 확인하세요 ---
"""
                print(classification_summary)

                # 상세 결과 (파일 저장용)
                detailed_classification = f"""
=== 종목 분류 상세 분석 (Flow) ===
📊 **분류 결과:** {classification_result['classification']['classification']}
🎯 **신뢰도:** {classification_result['classification']['confidence']}

📋 **분류 근거:**
"""
                # 모든 근거 나열
                for i, reason in enumerate(
                    classification_result["classification"]["reasoning"], 1
                ):
                    detailed_classification += f"{i}. {reason}\n"

                detailed_classification += f"""
💡 **AI 분석 전문:**
{classification_result.get('full_analysis', '상세 분석 내용 없음')}

🔍 **원시 분석 데이터:**
입력: {classification_result.get('input', 'N/A')}
에이전트 상태: {classification_result.get('agent_state', 'N/A')}

===============================
"""

                # 요약본과 상세본 모두 결과 수집기에 추가
                result_collector.add_to_result(classification_summary)
                result_collector.add_to_result(detailed_classification)

            # 분류 후에도 상세 분석을 위해 Flow도 실행
            print("📊 Flow 추가 상세 분석을 진행합니다...\n")

        try:
            start_time = time.time()
            flow_result = await asyncio.wait_for(
                flow.execute(prompt),
                timeout=3600,  # 60 minute timeout for the entire execution
            )
            elapsed_time = time.time() - start_time
            logger.info(f"Request processed in {elapsed_time:.2f} seconds")
            logger.info(flow_result)

            # 결과 수집
            result_collector.add_to_result(
                f"Request processed in {elapsed_time:.2f} seconds"
            )
            result_collector.add_to_result(flow_result)

            # 화면에 결과 표시
            print(flow_result)
            print(f"\nRequest processed in {elapsed_time:.2f} seconds")
            print("\n--- END OF RESULTS ---\n")

            # 결과 폴더 생성
            results_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "results"
            )
            os.makedirs(results_dir, exist_ok=True)

            # 수집된 결과 확인
            final_result = result_collector.get_result()
            if not final_result.strip():
                final_result = "Flow 분석 결과를 직접 가져올 수 없습니다. 콘솔 출력을 확인해주세요."
                if flow_result:
                    final_result = flow_result

            # AI Flow 응답에서 실제 분석된 종목명과 종목코드 추출 (최우선!)
            stock_name, stock_code = extract_stock_name_from_ai_response(
                final_result, prompt
            )
            logger.info(f"최종 추출된 종목명: {stock_name}, 종목코드: {stock_code}")

            # JSON 파일명 생성 (AI Flow 응답에서 추출한 종목명과 종목코드 사용)
            json_filename = generate_json_filename(
                stock_name, stock_code, results_dir, "flow"
            )

            # 분류 결과와 종목 정보 준비 (JSON에 포함할 메타데이터)
            classification_data_for_json = None
            stock_info_for_json = None

            # 분류 결과가 있으면 JSON용 데이터 준비
            if (
                is_classification_request
                and "classification_result" in locals()
                and classification_result.get("classification")
            ):
                classification_data_for_json = classification_result

            # 종목 정보가 있으면 JSON용 데이터 준비
            if stock_name != "GENERAL":
                stock_info_for_json = {
                    "stock_name": stock_name,
                    "ticker": stock_code,
                    "stock_code": stock_code,
                    "found": True,
                    "extraction_method": "✨ AI Flow 응답 동적 추출",
                    "source": "ai_flow_response",
                }

            # JSON 파일 생성해요
            save_json_file(
                final_result,
                json_filename,
                prompt,
                elapsed_time,
                "PLANNING",
                classification_data_for_json,  # 분류 결과 포함
                stock_info_for_json,  # 종목 정보 포함
            )  # JSON 파일 생성해요 (분류 정보 포함!)

            # 결과 파일 위치 출력
            print(f"\nResults saved to:")
            print(f" - JSON: {json_filename}")  # JSON 파일 경로 알려줘요

        except asyncio.TimeoutError:
            logger.error("Request processing timed out after 1 hour")
            logger.info(
                "Operation terminated due to timeout. Please try a simpler request."
            )

            # 타임아웃 메시지를 결과에 추가
            timeout_message = "Request processing timed out after 1 hour. Operation terminated due to timeout. Please try a simpler request."
            result_collector.add_to_result(timeout_message)

            # 타임아웃인 경우에도 JSON 파일로 저장해요
            results_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "results"
            )
            os.makedirs(results_dir, exist_ok=True)

            # 타임아웃의 경우 프롬프트에서 종목명과 종목코드 추출
            stock_name, stock_code = extract_stock_name_from_ai_response(prompt)

            json_filename = generate_json_filename(
                stock_name, stock_code, results_dir, "timeout"
            )

            save_json_file(
                timeout_message, json_filename, prompt, 3600, "PLANNING", None, None
            )  # 타임아웃도 JSON으로 저장

            print(f"\nTimeout results saved to:")
            print(f" - JSON: {json_filename}")

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user.")

        # 사용자 취소인 경우에도 JSON 파일로 저장해요
        cancel_message = "Operation cancelled by user."
        result_collector.add_to_result(cancel_message)

        results_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "results"
        )
        os.makedirs(results_dir, exist_ok=True)

        # 취소의 경우 프롬프트에서 종목명과 종목코드 추출
        stock_name, stock_code = extract_stock_name_from_ai_response(
            prompt if "prompt" in locals() else ""
        )

        json_filename = generate_json_filename(
            stock_name if "stock_name" in locals() else "GENERAL",
            stock_code if "stock_code" in locals() else None,
            results_dir,
            "cancelled",
        )

        save_json_file(
            cancel_message,
            json_filename,
            prompt if "prompt" in locals() else "",
            0,
            "PLANNING",
            None,  # 취소 시에는 분류 정보 없음
            None,  # 취소 시에는 종목 정보 없음
        )

        print(f"\nCancellation results saved to:")
        print(f" - JSON: {json_filename}")

    except Exception as e:
        logger.error(f"Error: {str(e)}")

        # 에러인 경우에도 JSON 파일로 저장해요
        error_message = f"Error: {str(e)}"
        result_collector.add_to_result(error_message)

        results_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "results"
        )
        os.makedirs(results_dir, exist_ok=True)

        # 에러의 경우 프롬프트에서 종목명과 종목코드 추출
        stock_name, stock_code = extract_stock_name_from_ai_response(
            prompt if "prompt" in locals() else ""
        )

        json_filename = generate_json_filename(
            stock_name, stock_code, results_dir, "error"
        )

        save_json_file(
            error_message,
            json_filename,
            prompt if "prompt" in locals() else "",
            0,
            "PLANNING",
            None,  # 에러 시에는 분류 정보 없음
            None,  # 에러 시에는 종목 정보 없음
        )

        print(f"\nError results saved to:")
        print(f" - JSON: {json_filename}")


if __name__ == "__main__":
    asyncio.run(run_flow())
