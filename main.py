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

        # 프롬프트에서 종목명 추출 (최우선 방법!)
        stock_name = extract_stock_name(prompt)
        logger.info(f"Extracted stock name from prompt: {stock_name}")

        # 현재 시간으로 파일명 생성 (기존 PDF, TXT 파일용)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = os.path.join(results_dir, f"analysis_{timestamp}.pdf")
        txt_filename = os.path.join(results_dir, f"analysis_{timestamp}.txt")

        # JSON 파일명 생성 (프롬프트에서 추출한 종목명 사용)
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
