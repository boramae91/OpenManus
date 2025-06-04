import asyncio
import json  # JSON 형식으로 저장하기 위해 필요한 모듈을 추가해요
import os
import re  # 종목명 추출을 위한 정규표현식 모듈을 추가해요
import sys
from datetime import datetime

from fpdf import FPDF

from app.agent.manus import Manus
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
    사용자의 질문에서 종목명을 추출하는 함수예요
    - prompt: 사용자가 입력한 질문
    - 반환값: 추출된 종목명 (없으면 "GENERAL" 반환)
    """
    # 1단계: 한국 주요 종목명들을 미리 정의해둬요 (우선순위가 높아요)
    korean_stocks = [
        "삼성전자",
        "삼성",
        "SAMSUNG",
        "SK하이닉스",
        "SK",
        "NAVER",
        "네이버",
        "LG전자",
        "LG",
        "현대자동차",
        "현대차",
        "기아",
        "KIA",
        "포스코",
        "POSCO",
        "카카오",
        "KAKAO",
        "셀트리온",
        "한국전력",
        "신한지주",
        "하나금융지주",
        "국민은행",
        "KB금융",
        "우리금융지주",
        "코스피",
        "KOSPI",
        "KOSDAQ",
        "코스닥",
    ]

    # 프롬프트를 대문자로 변환해서 검사해요
    prompt_upper = prompt.upper()

    # 2단계: 미리 정의된 종목명 확인 (우선순위 1)
    for stock in korean_stocks:
        if stock.upper() in prompt_upper:
            # 영어 종목명은 그대로, 한글 종목명은 영어로 변환해요
            stock_mapping = {
                "삼성전자": "SAMSUNG",
                "삼성": "SAMSUNG",
                "SK하이닉스": "SKHYNIX",
                "SK": "SK",
                "네이버": "NAVER",
                "LG전자": "LG",
                "LG": "LG",
                "현대자동차": "HYUNDAI",
                "현대차": "HYUNDAI",
                "기아": "KIA",
                "포스코": "POSCO",
                "카카오": "KAKAO",
                "셀트리온": "CELLTRION",
                "한국전력": "KEPCO",
                "신한지주": "SHINHAN",
                "하나금융지주": "HANAFN",
                "국민은행": "KOOKMIN",
                "KB금융": "KBFG",
                "우리금융지주": "WOORI",
                "코스피": "KOSPI",
                "코스닥": "KOSDAQ",
            }
            return stock_mapping.get(stock, stock.upper())

    # 3단계: 일반적인 종목명 패턴 찾기 (우선순위 2)
    # 정규표현식을 사용해서 종목명으로 보이는 패턴을 찾아요
    import re

    # 한글 + "전자", "산업", "그룹", "홀딩스" 등으로 끝나는 패턴
    korean_company_patterns = [
        r"([가-힣]+(?:전자|산업|그룹|홀딩스|화학|건설|금융|보험|증권|바이오|제약|에너지|통신|미디어|엔터|게임|소프트|테크|IT))",
        r"([가-힣]+(?:은행|카드|캐피탈|리츠|투자|자산|운용))",
        r"([가-힣]+(?:항공|해운|물류|운송|철도))",
        r"([가-힣]+(?:식품|음료|유통|마트|백화점))",
        r"([가-힣]+(?:철강|조선|자동차|타이어|화섬|섬유))",
    ]

    # 영어 회사명 패턴 (대문자로 시작하고 2글자 이상)
    english_company_patterns = [
        r"([A-Z][A-Z0-9]{1,}(?:\s+[A-Z][A-Z0-9]*)*)",  # 대문자로 된 회사명
        r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",  # 첫글자만 대문자인 회사명
    ]

    # 한글 회사명 패턴 찾기
    for pattern in korean_company_patterns:
        matches = re.findall(pattern, prompt)
        if matches:
            # 첫 번째로 찾은 회사명을 영어로 변환해서 반환
            company_name = matches[0]
            # 한글을 영어로 변환 (간단한 음성변환)
            return convert_korean_to_english(company_name)

    # 영어 회사명 패턴 찾기
    for pattern in english_company_patterns:
        matches = re.findall(pattern, prompt)
        if matches:
            # 첫 번째로 찾은 영어 회사명 반환 (공백 제거하고 대문자 변환)
            company_name = matches[0].replace(" ", "").upper()
            # 너무 짧거나 긴 이름은 제외
            if 2 <= len(company_name) <= 15:
                return company_name

    # 4단계: 단순한 한글 회사명 찾기 (우선순위 3)
    # "ㅇㅇ 주식", "ㅇㅇ 종목", "ㅇㅇ 회사" 같은 패턴
    simple_patterns = [
        r"([가-힣]+)(?:\s*(?:주식|종목|회사|기업|코퍼레이션|주가|분석|전망|투자))",
        r"([가-힣]{2,8})(?=\s*(?:은|는|이|가|에|를|의))",  # 조사 앞의 한글 단어
        r"([가-힣]{2,8})(?=\s*(?:어때|어떤|분석|전망|추천))",  # 질문어 앞의 한글 단어
    ]

    for pattern in simple_patterns:
        matches = re.findall(pattern, prompt)
        if matches:
            company_name = matches[0]
            # 일반적인 단어들은 제외 (회사명이 아닌 것들)
            exclude_words = [
                "주식",
                "투자",
                "분석",
                "전망",
                "추천",
                "시장",
                "경제",
                "증권",
                "금융",
                "은행",
                "오늘",
                "내일",
                "어제",
                "지금",
                "최근",
                "현재",
            ]
            if company_name not in exclude_words and len(company_name) >= 2:
                return convert_korean_to_english(company_name)

    # 5단계: 숫자가 포함된 종목 코드 찾기 (우선순위 4)
    # "005930", "035720" 같은 종목 코드
    code_pattern = r"(\d{6})"
    code_matches = re.findall(code_pattern, prompt)
    if code_matches:
        return f"CODE{code_matches[0]}"

    # 모든 방법으로도 찾지 못하면 기본값 반환
    return "GENERAL"


def convert_korean_to_english(korean_name):
    """
    한글 회사명을 영어로 변환하는 함수예요
    - korean_name: 한글 회사명
    - 반환값: 영어로 변환된 회사명
    """
    # 간단한 한글->영어 변환 매핑
    # 실제로는 더 정교한 변환이 필요하지만, 기본적인 것들만 포함
    korean_to_english = {
        # 자주 사용되는 단어들
        "전자": "ELEC",
        "산업": "IND",
        "그룹": "GROUP",
        "홀딩스": "HOLDINGS",
        "화학": "CHEM",
        "건설": "CONST",
        "금융": "FIN",
        "보험": "INS",
        "증권": "SEC",
        "바이오": "BIO",
        "제약": "PHARM",
        "에너지": "ENERGY",
        "통신": "TELECOM",
        "미디어": "MEDIA",
        "엔터": "ENT",
        "게임": "GAME",
        "소프트": "SOFT",
        "테크": "TECH",
        "은행": "BANK",
        "카드": "CARD",
        "항공": "AIR",
        "해운": "SHIP",
        "물류": "LOGIS",
        "식품": "FOOD",
        "유통": "RETAIL",
        "철강": "STEEL",
        "조선": "SHIP",
        "자동차": "AUTO",
        "타이어": "TIRE",
    }

    # 회사명에서 알려진 단어들을 영어로 변환
    english_name = korean_name
    for kor, eng in korean_to_english.items():
        if kor in english_name:
            english_name = english_name.replace(kor, eng)

    # 남은 한글이 있으면 로마자로 간단 변환 (매우 기본적)
    # 실제로는 더 정교한 변환이 필요하지만 여기서는 단순화
    if any(
        "\u3131" <= char <= "\u3163" or "\uac00" <= char <= "\ud7a3"
        for char in english_name
    ):
        # 한글이 남아있으면 첫 글자들의 초성만 추출하거나 간단한 변환
        simple_conversion = {
            "삼성": "SAMSUNG",
            "엘지": "LG",
            "현대": "HYUNDAI",
            "기아": "KIA",
            "포스코": "POSCO",
            "네이버": "NAVER",
            "카카오": "KAKAO",
            "셀트리온": "CELLTRION",
            "한화": "HANWHA",
            "두산": "DOOSAN",
            "롯데": "LOTTE",
            "신세계": "SHINSEGAE",
            "이마트": "EMART",
        }

        for kor, eng in simple_conversion.items():
            if kor in korean_name:
                return eng

        # 그 외에는 한글을 제거하고 영어 부분만 대문자로
        english_only = "".join(
            char for char in english_name if char.isalpha() and ord(char) < 128
        )
        if english_only:
            return english_only.upper()
        else:
            # 한글만 있는 경우 첫 두 글자를 기반으로 간단한 코드 생성
            return f"KOR{len(korean_name)}{ord(korean_name[0]) % 100:02d}"

    return english_name.upper()


def generate_json_filename(stock_name, base_dir="results"):
    """
    JSON 파일명을 생성하는 함수예요
    형식: JSON-Agent-종목명-financial-현재시간-save저장시간.json
    - stock_name: 종목명
    - base_dir: 저장할 폴더명
    """
    # 현재 시간을 문자열로 변환 (년월일_시분초 형식)
    current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_timestamp = current_timestamp  # 현재시간과 저장시간이 동일해요

    # 파일명 생성 (JSON-Agent-종목명-financial-현재시간-save저장시간.json)
    filename = f"JSON-Agent-{stock_name}-financial-{current_timestamp}-save{save_timestamp}.json"

    # 전체 경로 생성
    full_path = os.path.join(base_dir, filename)

    return full_path


def extract_stock_name_from_response(response_text, fallback_prompt=""):
    """
    AI 에이전트의 응답 결과에서 실제로 분석된 종목명을 추출하는 함수예요
    - response_text: AI가 생성한 분석 결과 텍스트
    - fallback_prompt: 응답에서 찾지 못할 경우 사용할 원본 프롬프트
    - 반환값: 추출된 종목명 (없으면 프롬프트에서 추출 시도)
    """
    import re

    if not response_text or not response_text.strip():
        # 응답이 비어있으면 원본 프롬프트에서 추출
        return extract_stock_name(fallback_prompt)

    # 1단계: 한국 주요 종목명들을 응답에서 찾기 (우선순위 최고)
    korean_stocks = [
        "삼성전자",
        "삼성",
        "SAMSUNG",
        "SK하이닉스",
        "SK",
        "NAVER",
        "네이버",
        "LG전자",
        "LG",
        "현대자동차",
        "현대차",
        "기아",
        "KIA",
        "포스코",
        "POSCO",
        "카카오",
        "KAKAO",
        "셀트리온",
        "한국전력",
        "신한지주",
        "하나금융지주",
        "국민은행",
        "KB금융",
        "우리금융지주",
        "코스피",
        "KOSPI",
        "KOSDAQ",
        "코스닥",
        "두산",
        "DOOSAN",
        "롯데",
        "LOTTE",
        "신세계",
        "SHINSEGAE",
        "이마트",
        "EMART",
        "한화",
        "HANWHA",
        "CJ",
        "현대건설",
        "대우",
        "DAEWOO",
        "아모레퍼시픽",
        "AMOREPACIFIC",
    ]

    # 응답을 대문자로 변환해서 검사
    response_upper = response_text.upper()

    # 각 종목명을 확인해서 응답에 포함되어 있는지 검사
    for stock in korean_stocks:
        if stock.upper() in response_upper:
            stock_mapping = {
                "삼성전자": "SAMSUNG",
                "삼성": "SAMSUNG",
                "SK하이닉스": "SKHYNIX",
                "SK": "SK",
                "네이버": "NAVER",
                "LG전자": "LG",
                "LG": "LG",
                "현대자동차": "HYUNDAI",
                "현대차": "HYUNDAI",
                "기아": "KIA",
                "포스코": "POSCO",
                "카카오": "KAKAO",
                "셀트리온": "CELLTRION",
                "한국전력": "KEPCO",
                "신한지주": "SHINHAN",
                "하나금융지주": "HANAFN",
                "국민은행": "KOOKMIN",
                "KB금융": "KBFG",
                "우리금융지주": "WOORI",
                "코스피": "KOSPI",
                "코스닥": "KOSDAQ",
                "두산": "DOOSAN",
                "롯데": "LOTTE",
                "신세계": "SHINSEGAE",
                "이마트": "EMART",
                "한화": "HANWHA",
                "CJ": "CJ",
                "현대건설": "HYUNDAI",
                "대우": "DAEWOO",
                "아모레퍼시픽": "AMOREPACIFIC",
            }
            extracted_name = stock_mapping.get(stock, stock.upper())
            logger.info(f"Found stock name in AI response: {stock} -> {extracted_name}")
            return extracted_name

    # 2단계: 응답에서 회사명 패턴 찾기
    # "ㅇㅇ 분석", "ㅇㅇ에 대한", "ㅇㅇ의 주가" 같은 패턴에서 회사명 추출
    company_context_patterns = [
        r"([가-힣A-Za-z0-9]+)(?:에\s*대한\s*(?:분석|전망|평가|리포트))",
        r"([가-힣A-Za-z0-9]+)(?:의\s*(?:주가|주식|분석|전망|실적|재무))",
        r"([가-힣A-Za-z0-9]+)(?:\s*(?:분석|전망|평가|리포트)(?:\s*결과)?)",
        r"([가-힣A-Za-z0-9]+)(?:\s*(?:주식|주가|종목)(?:\s*분석)?)",
        r"([가-힣A-Za-z0-9]+)(?:은|는)\s*(?:현재|최근|오늘)",
        r"([가-힣A-Za-z0-9]+)(?:이|가)\s*(?:상승|하락|급등|급락)",
    ]

    for pattern in company_context_patterns:
        matches = re.findall(pattern, response_text)
        if matches:
            for match in matches:
                # 일반적인 단어들 제외
                exclude_words = [
                    "주식",
                    "투자",
                    "분석",
                    "전망",
                    "추천",
                    "시장",
                    "경제",
                    "증권",
                    "금융",
                    "은행",
                    "오늘",
                    "내일",
                    "어제",
                    "지금",
                    "최근",
                    "현재",
                    "종목",
                    "기업",
                    "회사",
                    "업체",
                    "산업",
                    "섹터",
                    "지수",
                ]

                if (
                    match not in exclude_words
                    and len(match) >= 2
                    and len(match) <= 15
                    and not match.isdigit()
                ):

                    # 한글이 포함된 경우 영어로 변환
                    if any("\uac00" <= char <= "\ud7a3" for char in match):
                        converted = convert_korean_to_english(match)
                        logger.info(
                            f"Found company name in AI response: {match} -> {converted}"
                        )
                        return converted
                    else:
                        # 영어인 경우 그대로 대문자로
                        extracted = match.upper()
                        logger.info(
                            f"Found company name in AI response: {match} -> {extracted}"
                        )
                        return extracted

    # 3단계: 종목코드 찾기 (6자리 숫자)
    code_pattern = r"(\d{6})"
    code_matches = re.findall(code_pattern, response_text)
    if code_matches:
        code_name = f"CODE{code_matches[0]}"
        logger.info(
            f"Found stock code in AI response: {code_matches[0]} -> {code_name}"
        )
        return code_name

    # 4단계: 영어 회사명 찾기
    english_company_pattern = r"\b([A-Z][A-Za-z]{2,14})\b"
    english_matches = re.findall(english_company_pattern, response_text)

    # 일반적인 영어 단어 제외
    exclude_english = [
        "THE",
        "AND",
        "FOR",
        "ARE",
        "BUT",
        "NOT",
        "YOU",
        "ALL",
        "CAN",
        "HER",
        "WAS",
        "ONE",
        "OUR",
        "HAD",
        "BUT",
        "WORDS",
        "FROM",
        "THEY",
        "EACH",
        "WHICH",
        "THEIR",
        "TIME",
        "WILL",
        "ABOUT",
        "WOULD",
        "THERE",
        "COULD",
        "OTHER",
        "MORE",
        "VERY",
        "WHAT",
        "KNOW",
        "JUST",
        "FIRST",
        "GET",
        "OVER",
        "THINK",
        "ALSO",
        "YOUR",
        "WORK",
        "LIFE",
        "ONLY",
        "NEW",
        "YEARS",
        "WAY",
        "MAY",
        "SAY",
        "COME",
        "ITS",
        "NOW",
        "THAN",
        "LIKE",
        "OTHER",
        "HOW",
        "ANALYSIS",
        "REPORT",
        "MARKET",
        "STOCK",
        "INVESTMENT",
        "PRICE",
        "VALUE",
        "GROWTH",
        "COMPANY",
        "BUSINESS",
        "FINANCIAL",
        "REVENUE",
        "PROFIT",
        "EARNINGS",
    ]

    for match in english_matches:
        if match.upper() not in exclude_english:
            logger.info(f"Found English company name in AI response: {match}")
            return match.upper()

    # 모든 방법으로도 찾지 못하면 원본 프롬프트에서 추출 시도
    logger.info("No stock name found in AI response, falling back to prompt extraction")
    return extract_stock_name(fallback_prompt)


async def main():
    # 결과 수집기 생성
    result_collector = ResultCollector()

    # Create and initialize Manus agent
    agent = await Manus.create()
    try:
        prompt = input("Enter your prompt: ")
        if not prompt.strip():
            logger.warning("Empty prompt provided.")
            return

        logger.warning("Processing your request...")
        print("\n--- ANALYSIS RESULTS ---\n")

        # 처리 시작 시간을 기록해요 (얼마나 걸렸는지 측정하기 위해)
        start_time = datetime.now()

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

        # AI 응답 결과에서 실제 분석된 종목명 추출 (새로운 방식!)
        stock_name = extract_stock_name_from_response(final_result, prompt)
        logger.info(f"Final extracted stock name from AI response: {stock_name}")

        # 현재 시간으로 파일명 생성 (기존 PDF, TXT 파일용)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = os.path.join(results_dir, f"analysis_{timestamp}.pdf")
        txt_filename = os.path.join(results_dir, f"analysis_{timestamp}.txt")

        # 새로운 형식의 JSON 파일명 생성 (AI 응답에서 추출한 종목명 사용)
        json_filename = generate_json_filename(stock_name, results_dir)

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
