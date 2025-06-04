import asyncio
import json  # JSON 형식으로 저장하기 위해 필요한 모듈을 추가해요
import os
import re  # 종목명 추출을 위한 정규표현식 모듈을 추가해요
import sys
from datetime import datetime

from fpdf import FPDF

from app.agent.manus import Manus
from app.agent.stock_classifier import StockClassifier
from app.logger import logger


def create_pdf(content, filename):
    # PDF 생성
    pdf = FPDF()
    pdf.add_page()

    # 폰트 설정 (한글 폰트 대신 기본 폰트 사용)
    pdf.set_font("Arial", "", 11)

    # 마진 설정
    pdf.set_margins(10, 10, 10)

    # 제목 추가
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "OpenManus Analysis", 0, 1, "C")
    pdf.ln(5)

    # 날짜 추가
    pdf.set_font("Arial", "", 10)
    pdf.cell(
        0,
        10,
        f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        0,
        1,
        "R",
    )
    pdf.ln(5)

    # 내용 추가
    pdf.set_font("Arial", "", 11)

    # 내용을 라인별로 처리 (ASCII 문자만 처리)
    for line in content.split("\n"):
        # 비-ASCII 문자 필터링 (한글 등은 ?로 대체될 수 있음)
        filtered_line = "".join(char if ord(char) < 128 else "?" for char in line)
        pdf.multi_cell(0, 8, filtered_line)

    # PDF 저장
    pdf.output(filename)

    logger.info(f"Analysis result saved to {filename}")


def save_text_file(content, filename):
    # 텍스트 파일로 저장
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"Analysis result saved to {filename}")


def save_json_file(content, filename, prompt="", processing_time=0):
    """
    분석 결과를 JSON 형식으로 저장하는 함수예요
    - content: 분석 결과 내용 (문자열)
    - filename: 저장할 파일 이름
    - prompt: 사용자가 입력한 질문 (이것이 key가 돼요)
    - processing_time: 처리하는데 걸린 시간
    """
    # 간단한 key-value 형식으로 JSON 데이터를 만들어요
    # 사용자의 질문이 key가 되고, 분석 결과가 value가 되는 거예요
    # 마치 질문-답변 카드처럼 저장하는 거죠!

    if not prompt.strip():
        # 프롬프트가 비어있으면 기본 키를 사용해요
        prompt = "User Question"

    # 간단한 형식의 JSON 데이터 생성
    json_data = {prompt: content}  # 질문을 key로, 답변을 value로 저장해요

    # JSON 파일로 저장해요 (한글도 제대로 저장되도록 설정)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    logger.info(f"Analysis result saved to JSON: {filename}")


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
    프롬프트에서 기본적인 종목명을 추출하는 간단한 fallback 함수예요
    - prompt: 사용자가 입력한 질문
    - 반환값: 추출된 종목명 (없으면 "GENERAL" 반환)
    """
    if not prompt or not prompt.strip():
        return "GENERAL"

    # 기본적인 주요 종목명들만 확인해요 (한국 + 해외 종목)
    basic_stocks = {
        # 한국 종목들
        "삼성전자": "SAMSUNG",
        "삼성": "SAMSUNG",
        "SAMSUNG": "SAMSUNG",
        "SK하이닉스": "SKHYNIX",
        "SK": "SK",
        "네이버": "NAVER",
        "NAVER": "NAVER",
        "LG전자": "LG",
        "LG": "LG",
        "현대자동차": "HYUNDAI",
        "현대차": "HYUNDAI",
        "HYUNDAI": "HYUNDAI",
        "기아": "KIA",
        "KIA": "KIA",
        "포스코": "POSCO",
        "POSCO": "POSCO",
        "카카오": "KAKAO",
        "KAKAO": "KAKAO",
        "셀트리온": "CELLTRION",
        "CELLTRION": "CELLTRION",
        "한화에어로스페이스": "HANWHA_AERO",
        "한화": "HANWHA",
        "HANWHA": "HANWHA",
        "두산": "DOOSAN",
        "DOOSAN": "DOOSAN",
        "롯데": "LOTTE",
        "LOTTE": "LOTTE",
        "신세계": "SHINSEGAE",
        "SHINSEGAE": "SHINSEGAE",
        "이마트": "EMART",
        "EMART": "EMART",
        "CJ": "CJ",
        "현대건설": "HYUNDAI_CONST",
        "KB금융": "KBFG",
        "KB": "KB",
        "신한": "SHINHAN",
        "하나금융": "HANAFN",
        "우리금융": "WOORI",
        "국민은행": "KOOKMIN",
        "아모레퍼시픽": "AMOREPACIFIC",
        "코스피": "KOSPI",
        "KOSPI": "KOSPI",
        "코스닥": "KOSDAQ",
        "KOSDAQ": "KOSDAQ",
        # 해외 종목들 (한글명 → 영문명 매핑)
        "보잉": "BOEING",
        "애플": "APPLE",
        "마이크로소프트": "MICROSOFT",
        "테슬라": "TESLA",
        "구글": "GOOGLE",
        "알파벳": "ALPHABET",
        "아마존": "AMAZON",
        "메타": "META",
        "페이스북": "META",
        "넷플릭스": "NETFLIX",
        "엔비디아": "NVIDIA",
        "인텔": "INTEL",
        "AMD": "AMD",
        "코카콜라": "COCACOLA",
        "맥도날드": "MCDONALDS",
        "월마트": "WALMART",
        "존슨앤존슨": "JNJ",
        "화이자": "PFIZER",
        "BOEING": "BOEING",
        "APPLE": "APPLE",
        "MICROSOFT": "MICROSOFT",
        "TESLA": "TESLA",
        "GOOGLE": "GOOGLE",
        "ALPHABET": "ALPHABET",
        "AMAZON": "AMAZON",
        "META": "META",
        "FACEBOOK": "META",
        "NETFLIX": "NETFLIX",
        "NVIDIA": "NVIDIA",
        "INTEL": "INTEL",
        "COCACOLA": "COCACOLA",
        "MCDONALDS": "MCDONALDS",
        "WALMART": "WALMART",
        "PFIZER": "PFE",
    }

    prompt_upper = prompt.upper()
    for stock, ticker in basic_stocks.items():
        if stock.upper() in prompt_upper:
            return ticker

    # 6자리 종목코드 확인 (한국 종목만)
    code_pattern = r"(\d{6})"
    code_matches = re.findall(code_pattern, prompt)
    if code_matches:
        return f"CODE{code_matches[0]}"

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

    # 2. 주요 종목명 찾기 (단어 경계 고려)
    major_stocks = [
        "한화에어로스페이스",
        "한화시스템",
        "한화솔루션",
        "한화",
        "삼성전자",
        "삼성",
        "SK하이닉스",
        "SK",
        "LG전자",
        "LG",
        "현대자동차",
        "현대차",
        "현대",
        "기아",
        "포스코",
        "네이버",
        "카카오",
        "셀트리온",
        "두산",
        "롯데",
        "신세계",
        "이마트",
        "CJ",
        "KB금융",
        "KB",
        "국민은행",
        "신한금융",
        "신한",
        "하나금융",
        "하나은행",
        "우리금융",
        "우리은행",
        "아모레퍼시픽",
    ]

    for stock in major_stocks:
        pattern = rf"\b{re.escape(stock)}\b"
        if re.search(pattern, text, re.IGNORECASE):
            candidates.append(stock)

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
    종목코드로 실제 종목명을 찾는 함수예요
    - stock_code: 6자리 종목코드
    - 반환값: 매핑된 종목명 (없으면 None)
    """
    # 종목코드 → 종목명 매핑 테이블
    code_to_name = {
        "005930": "SAMSUNG",  # 삼성전자
        "000660": "SKHYNIX",  # SK하이닉스
        "035420": "NAVER",  # 네이버
        "373220": "LG",  # LG전자
        "005380": "HYUNDAI",  # 현대자동차
        "000270": "KIA",  # 기아
        "005490": "POSCO",  # 포스코홀딩스
        "035720": "KAKAO",  # 카카오
        "068270": "CELLTRION",  # 셀트리온
        "012450": "HANWHA_AERO",  # 한화에어로스페이스
        "009150": "SAMSUNG_ELEC",  # 삼성전기
        "051910": "LG_CHEM",  # LG화학
        "028260": "SAMSUNG_BIO",  # 삼성바이오로직스
        "207940": "SAMSUNG_SDI",  # 삼성SDI
        "000810": "SAMSUNG_FIRE",  # 삼성화재
        "018260": "SAMSUNG_SDS",  # 삼성SDS
        "105560": "KB_FINANCIAL",  # KB금융지주
        "055550": "SHINHAN",  # 신한지주
        "086790": "HANA_FINANCIAL",  # 하나금융지주
        "316140": "WOORI_FINANCIAL",  # 우리금융지주
        "036570": "NCSOFT",  # 엔씨소프트
        "251270": "NETMARBLE",  # 넷마블
        "005870": "HUNEED",  # 휴니드
        "003670": "POSCO_CHEM",  # 포스코케미칼
        "034730": "SK",  # SK
        "017670": "SK_TELECOM",  # SK텔레콤
        "096770": "SK_INNOVATION",  # SK이노베이션
        "011200": "HMM",  # HMM
        "042660": "DAEWOO_SHIPBUILDING",  # 대우조선해양
        "009540": "HD_KOREA_SHIPBUILDING",  # HD한국조선해양
    }

    return code_to_name.get(stock_code)


def extract_company_name_from_response(ai_response):
    """
    AI 에이전트의 서칭 결과에서 회사명을 직접 추출하는 함수예요
    - ai_response: AI가 생성한 분석 결과 텍스트
    - 반환값: 추출된 회사명 (없으면 None)
    """
    if not ai_response or not ai_response.strip():
        return None

    # 1. 괄호 안의 종목코드와 함께 나타나는 회사명 찾기
    # 예: "휴니드(A005870)", "삼성전자(005930)" 등
    pattern1 = r"([가-힣A-Za-z0-9]+)\s*\([A]?(\d{6})\)"
    matches1 = re.findall(pattern1, ai_response)
    if matches1:
        company_name = matches1[0][0].strip()
        logger.info(f"AI 응답에서 회사명 추출 (패턴1): {company_name}")
        return company_name

    # 2. "회사명 is a company" 패턴
    pattern2 = r"([가-힣A-Za-z0-9]+)\s+\((\d{6})\)\s+is\s+a\s+company"
    matches2 = re.findall(pattern2, ai_response)
    if matches2:
        company_name = matches2[0][0].strip()
        logger.info(f"AI 응답에서 회사명 추출 (패턴2): {company_name}")
        return company_name

    # 3. URL이나 제목에서 회사명 추출
    # 예: "휴니드(A005870) | Snapshot | 기업정보"
    pattern3 = r"([가-힣A-Za-z0-9]+)\([A]?(\d{6})\)\s*\|"
    matches3 = re.findall(pattern3, ai_response)
    if matches3:
        company_name = matches3[0][0].strip()
        logger.info(f"AI 응답에서 회사명 추출 (패턴3): {company_name}")
        return company_name

    # 4. 기본적인 한글/영문 회사명 패턴 (길이 제한)
    pattern4 = r"\b([가-힣]{2,10})\b"
    korean_matches = re.findall(pattern4, ai_response)
    for match in korean_matches:
        # 일반적인 단어들 제외
        exclude_words = [
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
        ]
        if match not in exclude_words and len(match) >= 2:
            logger.info(f"AI 응답에서 한글 회사명 추출 (패턴4): {match}")
            return match

    return None


def extract_company_name_from_prompt(prompt):
    """
    사용자 프롬프트에서 회사명을 직접 추출하는 함수예요
    - prompt: 사용자가 입력한 질문
    - 반환값: 추출된 회사명 (없으면 None)
    """
    if not prompt or not prompt.strip():
        return None

    # 1. "~에 대해서", "~에 대한", "~ 분석" 패턴
    pattern1 = r"([가-힣A-Za-z0-9]+)(?:\s*(?:에\s*대해서?|에\s*대한|을?를?\s*분석|의?\s*분석|주식|종목))"
    matches1 = re.findall(pattern1, prompt)
    if matches1:
        company_name = matches1[0].strip()
        logger.info(f"프롬프트에서 회사명 추출 (패턴1): {company_name}")
        return company_name

    # 2. 종목코드와 함께 나오는 패턴
    pattern2 = r"([가-힣A-Za-z0-9]+)\s*\(?(\d{6})\)?"
    matches2 = re.findall(pattern2, prompt)
    if matches2:
        company_name = matches2[0][0].strip()
        logger.info(f"프롬프트에서 회사명 추출 (패턴2): {company_name}")
        return company_name

    # 3. 단순한 회사명 (2글자 이상)
    pattern3 = r"\b([가-힣A-Za-z]{2,15})\b"
    matches3 = re.findall(pattern3, prompt)
    for match in matches3:
        exclude_words = [
            "분석",
            "종목",
            "기업",
            "정보",
            "결과",
            "전망",
            "투자",
            "주식",
            "시장",
            "해줘",
            "알려줘",
            "대해",
            "어떻게",
        ]
        if match not in exclude_words and len(match) >= 2:
            logger.info(f"프롬프트에서 회사명 추출 (패턴3): {match}")
            return match

    return None


def convert_korean_to_english_ticker(korean_name):
    """
    한글 회사명을 영문 티커로 변환하는 함수예요 (기본적인 변환만)
    - korean_name: 한글 회사명
    - 반환값: 영문 티커 (변환 불가시 원본을 대문자로)
    """
    if not korean_name:
        return "UNKNOWN"

    # 기본적인 변환 테이블 (자주 사용되는 몇 개만)
    basic_conversions = {
        "삼성전자": "SAMSUNG",
        "삼성": "SAMSUNG",
        "SK하이닉스": "SKHYNIX",
        "SK": "SK",
        "LG전자": "LG",
        "LG": "LG",
        "현대자동차": "HYUNDAI",
        "현대차": "HYUNDAI",
        "현대": "HYUNDAI",
        "기아": "KIA",
        "포스코": "POSCO",
        "네이버": "NAVER",
        "카카오": "KAKAO",
        "셀트리온": "CELLTRION",
        "한화에어로스페이스": "HANWHA_AERO",
        "한화": "HANWHA",
        "휴니드": "HUNEED",
    }

    # 기본 변환 테이블에 있으면 반환
    if korean_name in basic_conversions:
        return basic_conversions[korean_name]

    # 없으면 한글 그대로 반환하거나 대문자로 변환
    if korean_name.isalpha() and all(ord(char) < 128 for char in korean_name):
        # 이미 영문이면 대문자로
        return korean_name.upper()
    else:
        # 한글이면 그대로 반환
        return korean_name


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
    회사명을 영문 티커로 변환하는 함수예요 (한국 + 해외 종목 지원)
    - company_name: 회사명 (한글, 영문, 또는 티커)
    - 반환값: 영문 티커
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

    # 종목 변환 테이블 (한국 + 해외)
    basic_conversions = {
        # 한국 종목들
        "휴니드": "HUNEED",
        "삼성전자": "SAMSUNG",
        "삼성": "SAMSUNG",
        "SK하이닉스": "SKHYNIX",
        "LG전자": "LG",
        "현대자동차": "HYUNDAI",
        "현대차": "HYUNDAI",
        "기아": "KIA",
        "포스코": "POSCO",
        "네이버": "NAVER",
        "카카오": "KAKAO",
        "셀트리온": "CELLTRION",
        "한화에어로스페이스": "HANWHA_AERO",
        "한화": "HANWHA",
        # 해외 종목들 - 한글명을 실제 티커로 매핑
        "보잉": "BA",  # Boeing Company
        "애플": "AAPL",  # Apple Inc
        "마이크로소프트": "MSFT",  # Microsoft Corporation
        "테슬라": "TSLA",  # Tesla Inc
        "구글": "GOOGL",  # Alphabet Inc (Google)
        "알파벳": "GOOGL",  # Alphabet Inc
        "아마존": "AMZN",  # Amazon.com Inc
        "메타": "META",  # Meta Platforms Inc
        "페이스북": "META",  # Meta (구 Facebook)
        "넷플릭스": "NFLX",  # Netflix Inc
        "엔비디아": "NVDA",  # NVIDIA Corporation
        "인텔": "INTC",  # Intel Corporation
        "코카콜라": "KO",  # The Coca-Cola Company
        "맥도날드": "MCD",  # McDonald's Corporation
        "월마트": "WMT",  # Walmart Inc
        "존슨앤존슨": "JNJ",  # Johnson & Johnson
        "화이자": "PFE",  # Pfizer Inc
        # 영문명도 매핑
        "BOEING": "BA",
        "APPLE": "AAPL",
        "MICROSOFT": "MSFT",
        "TESLA": "TSLA",
        "GOOGLE": "GOOGL",
        "ALPHABET": "GOOGL",
        "AMAZON": "AMZN",
        "META": "META",
        "FACEBOOK": "META",
        "NETFLIX": "NFLX",
        "NVIDIA": "NVDA",
        "INTEL": "INTC",
        "COCACOLA": "KO",
        "MCDONALDS": "MCD",
        "WALMART": "WMT",
        "PFIZER": "PFE",
    }

    # 변환 테이블에서 찾기
    if company_name in basic_conversions:
        return basic_conversions[company_name]

    # 정리된 이름에서 찾기
    if company_clean in basic_conversions:
        return basic_conversions[company_clean]

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

    # 변환할 수 없으면 원본 반환 (한글 등)
    return company_name


def cross_verify_stock_name(prompt, ai_response):
    """
    AI 응답에서 가장 빈번한 종목명을 찾고, 프롬프트와 비교해서 검증하는 함수예요
    - prompt: 사용자가 입력한 질문
    - ai_response: AI가 생성한 분석 결과
    - 반환값: (종목명, 종목코드) 튜플
    """
    # AI 응답에서 가장 빈번한 종목명 찾기
    most_frequent_name, frequency = find_most_frequent_stock_name(ai_response)

    # 종목코드 추출
    response_code = extract_stock_code_from_text(ai_response)
    prompt_code = extract_stock_code_from_text(prompt)
    final_code = response_code or prompt_code

    logger.info(
        f"AI 응답에서 가장 빈번한 종목명: {most_frequent_name} (빈도: {frequency})"
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
    AI 에이전트가 실제로 분석한 결과에서 종목명과 종목코드를 추출하는 함수예요 (새로운 동적 방식)
    - response_text: AI가 생성한 분석 결과 텍스트
    - fallback_prompt: 응답에서 찾지 못할 경우 사용할 원본 프롬프트
    - 반환값: (종목명, 종목코드) 튜플
    """
    # 새로운 교차 검증을 통한 종목명과 종목코드 추출 시도
    stock_name, stock_code = cross_verify_stock_name(fallback_prompt, response_text)
    if stock_name:
        logger.info(
            f"동적 분석으로 최종 확정된 종목명: {stock_name}, 종목코드: {stock_code}"
        )
        return stock_name, stock_code

    # 추출 실패 시 기본값 반환
    logger.info("동적 분석 실패, 기본값 사용")
    return "GENERAL", None


def generate_json_filename(stock_name, stock_code=None, base_dir="results"):
    """
    JSON 파일명을 생성하는 함수예요
    형식: JSON-FA-종목명(영문)-종목티커-현재시간-save현재시간.json
    - stock_name: 종목명 (영문)
    - stock_code: 종목티커 (선택사항, 한국 종목만 6자리 코드)
    - base_dir: 저장할 폴더명
    """
    # 현재 시간을 문자열로 변환 (년월일_시분초 형식)
    current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_timestamp = current_timestamp  # 현재시간과 저장시간이 동일해요

    # 해외 종목의 경우 실제 티커를 사용, 한국 종목의 경우 6자리 코드 사용
    if stock_code and len(stock_code) == 6 and stock_code.isdigit():
        # 한국 종목코드인 경우
        ticker_part = stock_code
    else:
        # 해외 종목이거나 코드가 없는 경우, 종목명에서 티커 추출
        ticker_part = convert_to_english_ticker(stock_name)
        # 이미 티커 형태라면 그대로, 아니면 UNKNOWN 사용
        if ticker_part == stock_name and not (
            ticker_part.isupper()
            and ticker_part.isalpha()
            and 2 <= len(ticker_part) <= 5
        ):
            ticker_part = "UNKNOWN"

    # 파일명 생성 (JSON-FA-종목명(영문)-종목티커-현재시간-save현재시간.json)
    filename = f"JSON-FA-{stock_name}-{ticker_part}-{current_timestamp}-save{save_timestamp}.json"

    # 전체 경로 생성
    full_path = os.path.join(base_dir, filename)

    return full_path


async def main():
    # 결과 수집기 생성
    result_collector = ResultCollector()

    # Create and initialize Manus agent
    agent = await Manus.create()

    # 종목 분류 에이전트 생성
    stock_classifier = StockClassifier()

    try:
        prompt = input("Enter your prompt: ")
        if not prompt.strip():
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
        detected_stock_info, detected_stock_code = extract_stock_name(prompt)
        has_stock_detected = (
            detected_stock_info != "GENERAL" and detected_stock_code is not None
        )

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
                logger.info(
                    f"종목 분류 실행 - 종목 자동 감지: {detected_stock_info} ({detected_stock_code})"
                )
        else:
            logger.info("종목 분류 실행 안함 - 키워드나 종목 감지되지 않음")

        logger.warning("Processing your request...")
        print("\n--- ANALYSIS RESULTS ---\n")

        # 처리 시작 시간을 기록해요 (얼마나 걸렸는지 측정하기 위해)
        start_time = datetime.now()

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

            # 분류 결과를 결과 수집기에 추가
            if classification_result.get("classification"):
                classification_summary = f"""
=== 종목 분류 결과 ===
🏷️ 분류: {classification_result['classification']['classification']}
📊 신뢰도: {classification_result['classification']['confidence']}
📋 근거: {', '.join(classification_result['classification']['reasoning'][:3])}

--- 상세 분석은 아래를 확인하세요 ---
"""
                result_collector.add_to_result(classification_summary)
                print(classification_summary)

            # 분류 후에도 상세 분석을 위해 Manus 에이전트도 실행
            print("📊 추가 상세 분석을 진행합니다...\n")

        # 에이전트 실행하고 결과 받기
        response = await agent.run(prompt)

        # 처리 완료 시간을 계산해요
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        # 결과를 추가
        result_collector.add_to_result(response)

        # 화면에 결과 표시
        print(response)
        print("\n--- END OF RESULTS ---\n")

        # 결과 폴더 생성
        results_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "results"
        )
        os.makedirs(results_dir, exist_ok=True)

        # 수집된 결과 확인
        final_result = result_collector.get_result()
        if not final_result.strip():
            # 결과가 비어있으면 에이전트가 직접 설정한 응답 사용
            final_result = (
                "분석 결과를 직접 가져올 수 없습니다. 콘솔 출력을 확인해주세요."
            )
            if response:
                final_result = response

        # AI 응답에서 실제 분석된 종목명 추출 (최우선!)
        stock_name, stock_code = extract_stock_name_from_ai_response(
            final_result, prompt
        )
        logger.info(f"최종 추출된 종목명: {stock_name}, 종목코드: {stock_code}")

        # 현재 시간으로 파일명 생성 (기존 PDF, TXT 파일용)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = os.path.join(results_dir, f"analysis_{timestamp}.pdf")
        txt_filename = os.path.join(results_dir, f"analysis_{timestamp}.txt")

        # JSON 파일명 생성 (AI 응답에서 추출한 종목명 사용)
        json_filename = generate_json_filename(stock_name, stock_code, results_dir)

        # PDF, 텍스트, JSON 파일 모두 생성해요
        create_pdf(final_result, pdf_filename)
        save_text_file(final_result, txt_filename)
        save_json_file(
            final_result, json_filename, prompt, processing_time
        )  # JSON 파일도 생성해요

        # 결과 파일 위치 출력
        print(f"\nResults saved to:")
        print(f" - PDF: {pdf_filename}")
        print(f" - TXT: {txt_filename}")
        print(f" - JSON: {json_filename}")  # JSON 파일 경로도 알려줘요

        logger.info("Request processing completed.")
    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")
    except Exception as e:
        logger.error(f"Error occurred: {e}")
    finally:
        # Ensure agent resources are cleaned up before exiting
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
