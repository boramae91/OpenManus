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
    - prompt: 사용자가 입력한 질문 (이것이 key가 돼요)
    - processing_time: 처리하는데 걸린 시간 (초 단위)
    - flow_type: 실행한 Flow의 종류
    """
    # 간단한 key-value 형식으로 JSON 데이터를 만들어요
    # 사용자의 질문이 key가 되고, Flow 실행 결과가 value가 되는 거예요
    # 마치 질문-답변 카드처럼 저장하는 거죠!

    if not prompt.strip():
        # 프롬프트가 비어있으면 기본 키를 사용해요
        prompt = "User Flow Question"

    # 간단한 형식의 JSON 데이터 생성
    json_data = {prompt: content}  # 질문을 key로, Flow 실행 결과를 value로 저장해요

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


def generate_json_filename(
    stock_name, stock_code=None, base_dir="results", file_type="flow"
):
    """
    JSON 파일명을 생성하는 함수예요
    형식: JSON-FA-종목명(영문)-종목티커-현재시간-save현재시간.json
    - stock_name: 종목명 (영문)
    - stock_code: 종목티커 (선택사항)
    - base_dir: 저장할 폴더명
    - file_type: 파일 타입 (flow, timeout, cancelled, error)
    """
    # 현재 시간을 문자열로 변환 (년월일_시분초 형식)
    current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_timestamp = current_timestamp  # 현재시간과 저장시간이 동일해요

    # 종목티커가 있으면 포함, 없으면 UNKNOWN 사용
    ticker_part = stock_code if stock_code else "UNKNOWN"

    # 파일명 생성 (JSON-FA-종목명(영문)-종목티커-현재시간-save현재시간.json)
    if file_type == "flow":
        filename = f"JSON-FA-{stock_name}-{ticker_part}-{current_timestamp}-save{save_timestamp}.json"
    else:
        # 특수한 경우 (timeout, cancelled, error)에는 파일명에 타입을 포함시켜요
        filename = f"JSON-FA-{stock_name}-{ticker_part}-{file_type}-{current_timestamp}-save{save_timestamp}.json"

    # 전체 경로 생성
    full_path = os.path.join(base_dir, filename)

    return full_path


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
    프롬프트와 AI Flow 응답을 교차 검증하여 가장 정확한 종목명을 찾는 함수예요
    - prompt: 사용자가 입력한 질문
    - ai_response: AI Flow가 생성한 분석 결과
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
    logger.info(f"AI Flow 응답에서 추출된 종목명 후보: {response_candidates}")
    logger.info(f"프롬프트에서 추출된 종목코드: {prompt_code}")
    logger.info(f"AI Flow 응답에서 추출된 종목코드: {response_code}")

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
            logger.info(f"AI Flow 응답 우선 선택 (종목코드): {best_candidate}")
            return best_candidate, code_from_name
        else:
            mapped_name = stock_mapping.get(best_candidate, best_candidate.upper())
            logger.info(f"AI Flow 응답 우선 선택: {best_candidate} -> {mapped_name}")
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

    try:
        prompt = input("Enter your prompt: ")

        if prompt.strip().isspace() or not prompt:
            logger.warning("Empty prompt provided.")
            return

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

            # 현재 시간으로 파일명 생성 (기존 TXT 파일용)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            txt_filename = os.path.join(results_dir, f"flow_analysis_{timestamp}.txt")

            # JSON 파일명 생성 (AI Flow 응답에서 추출한 종목명과 종목코드 사용)
            json_filename = generate_json_filename(
                stock_name, stock_code, results_dir, "flow"
            )

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

            # 타임아웃의 경우 프롬프트에서 종목명과 종목코드 추출
            stock_name, stock_code = extract_stock_name_from_ai_response(prompt)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            txt_filename = os.path.join(
                results_dir, f"flow_analysis_timeout_{timestamp}.txt"
            )
            json_filename = generate_json_filename(
                stock_name, stock_code, results_dir, "timeout"
            )

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

        # 취소의 경우 프롬프트에서 종목명과 종목코드 추출
        stock_name, stock_code = extract_stock_name_from_ai_response(
            prompt if "prompt" in locals() else ""
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        txt_filename = os.path.join(
            results_dir, f"flow_analysis_cancelled_{timestamp}.txt"
        )
        json_filename = generate_json_filename(
            stock_name if "stock_name" in locals() else "GENERAL",
            stock_code if "stock_code" in locals() else None,
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

        # 에러의 경우 프롬프트에서 종목명과 종목코드 추출
        stock_name, stock_code = extract_stock_name_from_ai_response(
            prompt if "prompt" in locals() else ""
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        txt_filename = os.path.join(results_dir, f"flow_analysis_error_{timestamp}.txt")
        json_filename = generate_json_filename(
            stock_name, stock_code, results_dir, "error"
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
