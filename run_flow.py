import asyncio
import json  # JSON 형식으로 저장하기 위해 필요한 모듈을 추가해요
import os
import re  # 종목명 추출을 위한 정규표현식 모듈을 추가해요
import time
from datetime import datetime

from app.agent.manus import Manus
from app.flow.flow_factory import FlowFactory, FlowType
from app.logger import logger


def save_text_file(content, filename):
    # 텍스트 파일로 저장
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"Flow result saved to {filename}")


def save_json_file(
    content, filename, prompt="", processing_time=0, flow_type="PLANNING"
):
    """
    Flow 실행 결과를 JSON 형식으로 저장하는 함수예요
    - content: Flow 실행 결과 내용 (문자열)
    - filename: 저장할 파일 이름
    - prompt: 사용자가 입력한 질문
    - processing_time: 처리하는데 걸린 시간 (초 단위)
    - flow_type: 실행한 Flow의 종류
    """
    # JSON 형식으로 저장할 데이터를 딕셔너리(사전)로 만들어요
    # 마치 정리된 서랍장처럼 각각의 정보를 분류해서 저장해요
    json_data = {
        "metadata": {  # 메타데이터는 결과에 대한 기본 정보들을 담는 상자예요
            "timestamp": datetime.now().isoformat(),  # 언제 만들어졌는지 시간 정보
            "generated_by": "OpenManus Flow",  # 어떤 프로그램이 만들었는지
            "version": "1.0",  # 프로그램 버전
            "processing_time_seconds": processing_time,  # Flow 실행하는데 걸린 시간
            "flow_type": flow_type,  # 어떤 종류의 Flow를 실행했는지
        },
        "input": {  # 입력 정보를 담는 상자예요
            "user_prompt": prompt,  # 사용자가 질문한 내용
            "execution_type": "flow",  # 실행 방식이 flow라는 것을 표시
        },
        "output": {  # 출력 결과를 담는 상자예요
            "flow_result": content,  # 실제 Flow 실행 결과
            "result_length": len(content),  # 결과 텍스트의 길이
            "has_content": bool(content.strip()),  # 내용이 있는지 없는지 확인
            "execution_status": (
                "completed" if content.strip() else "empty"
            ),  # 실행 상태
        },
    }

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
    사용자의 질문에서 종목명을 추출하는 함수예요
    - prompt: 사용자가 입력한 질문
    - 반환값: 추출된 종목명 (없으면 "GENERAL" 반환)
    """
    # 한국 주요 종목명들을 미리 정의해둬요 (실제로는 더 많은 종목을 추가할 수 있어요)
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

    # 각 종목명을 확인해서 프롬프트에 포함되어 있는지 검사해요
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

    # 종목명을 찾지 못하면 기본값 반환
    return "GENERAL"


def generate_json_filename(stock_name, base_dir="results", file_type="flow"):
    """
    JSON 파일명을 생성하는 함수예요
    형식: JSON-Agent-종목명-financial-현재시간-save저장시간.json
    - stock_name: 종목명
    - base_dir: 저장할 폴더명
    - file_type: 파일 타입 (flow, timeout, cancelled, error)
    """
    # 현재 시간을 문자열로 변환 (년월일_시분초 형식)
    current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_timestamp = current_timestamp  # 현재시간과 저장시간이 동일해요

    # 파일명 생성 (JSON-Agent-종목명-financial-현재시간-save저장시간.json)
    if file_type == "flow":
        filename = f"JSON-Agent-{stock_name}-financial-{current_timestamp}-{save_timestamp}.json"
    else:
        # 특수한 경우 (timeout, cancelled, error)에는 파일명에 타입을 포함시켜요
        filename = f"JSON-Agent-{stock_name}-financial-{file_type}-{current_timestamp}-{save_timestamp}.json"

    # 전체 경로 생성
    full_path = os.path.join(base_dir, filename)

    return full_path


async def run_flow():
    # 결과 수집기 생성
    result_collector = ResultCollector()

    agents = {
        "manus": Manus(),
    }

    try:
        prompt = input("Enter your prompt: ")

        if prompt.strip().isspace() or not prompt:
            logger.warning("Empty prompt provided.")
            return

        # 종목명을 미리 추출해 둬요 (모든 상황에서 사용하기 위해)
        stock_name = extract_stock_name(prompt)
        logger.info(f"Extracted stock name: {stock_name}")

        flow = FlowFactory.create_flow(
            flow_type=FlowType.PLANNING,
            agents=agents,
        )
        logger.warning("Processing your request...")
        print("\n--- FLOW EXECUTION RESULTS ---\n")

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

            # 현재 시간으로 파일명 생성 (기존 TXT 파일용)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            txt_filename = os.path.join(results_dir, f"flow_analysis_{timestamp}.txt")

            # 새로운 형식의 JSON 파일명 생성
            json_filename = generate_json_filename(stock_name, results_dir, "flow")

            # 수집된 결과 확인
            final_result = result_collector.get_result()
            if not final_result.strip():
                final_result = "Flow 분석 결과를 직접 가져올 수 없습니다. 콘솔 출력을 확인해주세요."
                if flow_result:
                    final_result = flow_result

            # 텍스트 파일과 JSON 파일 모두 생성해요
            save_text_file(final_result, txt_filename)
            save_json_file(
                final_result, json_filename, prompt, elapsed_time, "PLANNING"
            )  # JSON 파일도 생성해요

            # 결과 파일 위치 출력
            print(f"\nResults saved to:")
            print(f" - TXT: {txt_filename}")
            print(f" - JSON: {json_filename}")  # JSON 파일 경로도 알려줘요

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

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            txt_filename = os.path.join(
                results_dir, f"flow_analysis_timeout_{timestamp}.txt"
            )
            json_filename = generate_json_filename(stock_name, results_dir, "timeout")

            save_text_file(timeout_message, txt_filename)
            save_json_file(
                timeout_message, json_filename, prompt, 3600, "PLANNING"
            )  # 타임아웃도 JSON으로 저장

            print(f"\nTimeout results saved to:")
            print(f" - TXT: {txt_filename}")
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

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        txt_filename = os.path.join(
            results_dir, f"flow_analysis_cancelled_{timestamp}.txt"
        )
        json_filename = generate_json_filename(
            stock_name if "stock_name" in locals() else "GENERAL",
            results_dir,
            "cancelled",
        )

        save_text_file(cancel_message, txt_filename)
        save_json_file(
            cancel_message,
            json_filename,
            prompt if "prompt" in locals() else "",
            0,
            "PLANNING",
        )

        print(f"\nCancellation results saved to:")
        print(f" - TXT: {txt_filename}")
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

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        txt_filename = os.path.join(results_dir, f"flow_analysis_error_{timestamp}.txt")
        json_filename = generate_json_filename(
            stock_name if "stock_name" in locals() else "GENERAL", results_dir, "error"
        )

        save_text_file(error_message, txt_filename)
        save_json_file(
            error_message,
            json_filename,
            prompt if "prompt" in locals() else "",
            0,
            "PLANNING",
        )

        print(f"\nError results saved to:")
        print(f" - TXT: {txt_filename}")
        print(f" - JSON: {json_filename}")


if __name__ == "__main__":
    asyncio.run(run_flow())
