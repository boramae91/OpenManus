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
    프롬프트에서 기본적인 종목명을 추출하는 간단한 fallback 함수예요
    - prompt: 사용자가 입력한 질문
    - 반환값: 추출된 종목명 (없으면 "GENERAL" 반환)
    """
    if not prompt or not prompt.strip():
        return "GENERAL"

    # 기본적인 주요 종목명들만 확인해요
    basic_stocks = {
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
    }

    prompt_upper = prompt.upper()
    for stock, ticker in basic_stocks.items():
        if stock.upper() in prompt_upper:
            return ticker

    # 6자리 종목코드 확인
    import re

    code_pattern = r"(\d{6})"
    code_matches = re.findall(code_pattern, prompt)
    if code_matches:
        return f"CODE{code_matches[0]}"

    return "GENERAL"


def extract_stock_code_from_text(text):
    """
    텍스트에서 6자리 종목코드를 추출하는 함수예요
    - text: 분석할 텍스트
    - 반환값: 추출된 종목코드 (없으면 None)
    """
    import re

    if not text or not text.strip():
        return None

    # 6자리 종목코드 찾기
    code_pattern = r"(\d{6})"
    code_matches = re.findall(code_pattern, text)
    if code_matches:
        return code_matches[0]  # 첫 번째로 발견된 코드 반환

    return None


def extract_stock_candidates_from_text(text):
    """
    텍스트에서 종목명 후보들을 추출하는 헬퍼 함수예요
    - text: 분석할 텍스트 (프롬프트 또는 AI 응답)
    - 반환값: 발견된 종목명 후보들의 리스트
    """
    import re

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


def cross_verify_stock_name(prompt, ai_response):
    """
    프롬프트와 AI 응답을 교차 검증하여 가장 정확한 종목명을 찾는 함수예요
    - prompt: 사용자가 입력한 질문
    - ai_response: AI가 생성한 분석 결과
    - 반환값: (종목명, 종목코드) 튜플 (없으면 (None, None))
    """
    # 프롬프트에서 종목명 후보 추출
    prompt_candidates = extract_stock_candidates_from_text(prompt)

    # AI 응답에서 종목명 후보 추출
    response_candidates = extract_stock_candidates_from_text(ai_response)

    # 종목코드 추출
    prompt_code = extract_stock_code_from_text(prompt)
    response_code = extract_stock_code_from_text(ai_response)

    logger.info(f"프롬프트에서 추출된 종목명 후보: {prompt_candidates}")
    logger.info(f"AI 응답에서 추출된 종목명 후보: {response_candidates}")
    logger.info(f"프롬프트에서 추출된 종목코드: {prompt_code}")
    logger.info(f"AI 응답에서 추출된 종목코드: {response_code}")

    # 종목명 매핑 테이블
    stock_mapping = {
        "한화에어로스페이스": "HANWHA_AERO",
        "한화시스템": "HANWHA_SYS",
        "한화솔루션": "HANWHA_SOL",
        "한화": "HANWHA",
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
        "두산": "DOOSAN",
        "롯데": "LOTTE",
        "신세계": "SHINSEGAE",
        "이마트": "EMART",
        "CJ": "CJ",
        "KB금융": "KBFG",
        "KB": "KB",
        "국민은행": "KOOKMIN",
        "신한금융": "SHINHAN",
        "신한": "SHINHAN",
        "하나금융": "HANAFN",
        "하나은행": "HANA",
        "우리금융": "WOORI",
        "우리은행": "WOORI",
        "아모레퍼시픽": "AMOREPACIFIC",
    }

    # 최종 종목코드 결정 (AI 응답 우선)
    final_code = response_code or prompt_code

    # 1단계: 정확한 일치 확인 (프롬프트와 AI 응답 모두에서 발견된 종목명)
    for p_candidate in prompt_candidates:
        for r_candidate in response_candidates:
            # 종목코드는 정확히 일치해야 함
            if p_candidate.startswith("CODE") and p_candidate == r_candidate:
                code_from_name = p_candidate.replace("CODE", "")
                logger.info(f"교차 검증 성공 (종목코드): {p_candidate}")
                return p_candidate, code_from_name

            # 회사명은 유사성 검사
            p_mapped = stock_mapping.get(p_candidate, p_candidate.upper())
            r_mapped = stock_mapping.get(r_candidate, r_candidate.upper())

            if p_mapped == r_mapped:
                logger.info(
                    f"교차 검증 성공 (회사명): {p_candidate} & {r_candidate} -> {p_mapped}"
                )
                return p_mapped, final_code

            # 부분 일치 검사 (한화에어로스페이스 vs 한화)
            if (
                (p_candidate in r_candidate or r_candidate in p_candidate)
                and len(p_candidate) > 1
                and len(r_candidate) > 1
            ):
                # 더 구체적인 이름을 선택
                longer_name = (
                    p_candidate if len(p_candidate) >= len(r_candidate) else r_candidate
                )
                mapped_name = stock_mapping.get(longer_name, longer_name.upper())
                logger.info(
                    f"교차 검증 성공 (부분 일치): {p_candidate} & {r_candidate} -> {mapped_name}"
                )
                return mapped_name, final_code

    # 2단계: AI 응답 우선 (AI가 실제로 분석한 내용이므로)
    if response_candidates:
        best_candidate = response_candidates[0]  # 첫 번째로 발견된 것
        if best_candidate.startswith("CODE"):
            code_from_name = best_candidate.replace("CODE", "")
            logger.info(f"AI 응답 우선 선택 (종목코드): {best_candidate}")
            return best_candidate, code_from_name
        else:
            mapped_name = stock_mapping.get(best_candidate, best_candidate.upper())
            logger.info(f"AI 응답 우선 선택: {best_candidate} -> {mapped_name}")
            return mapped_name, final_code

    # 3단계: 프롬프트 우선 (마지막 fallback)
    if prompt_candidates:
        best_candidate = prompt_candidates[0]
        if best_candidate.startswith("CODE"):
            code_from_name = best_candidate.replace("CODE", "")
            logger.info(f"프롬프트 우선 선택 (종목코드): {best_candidate}")
            return best_candidate, code_from_name
        else:
            mapped_name = stock_mapping.get(best_candidate, best_candidate.upper())
            logger.info(f"프롬프트 우선 선택: {best_candidate} -> {mapped_name}")
            return mapped_name, final_code

    return None, final_code


def extract_stock_name_from_ai_response(response_text, fallback_prompt=""):
    """
    AI 에이전트가 실제로 분석한 결과에서 종목명과 종목코드를 추출하는 함수예요 (교차 검증 포함)
    - response_text: AI가 생성한 분석 결과 텍스트
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


def generate_json_filename(stock_name, stock_code=None, base_dir="results"):
    """
    JSON 파일명을 생성하는 함수예요
    형식: JSON-FA-종목명(영문)-종목티커-현재시간-save현재시간.json
    - stock_name: 종목명 (영문)
    - stock_code: 종목티커 (선택사항)
    - base_dir: 저장할 폴더명
    """
    # 현재 시간을 문자열로 변환 (년월일_시분초 형식)
    current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_timestamp = current_timestamp  # 현재시간과 저장시간이 동일해요

    # 종목티커가 있으면 포함, 없으면 UNKNOWN 사용
    ticker_part = stock_code if stock_code else "UNKNOWN"

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
