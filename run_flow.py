import asyncio
import time
import os
from datetime import datetime

from app.agent.manus import Manus
from app.flow.flow_factory import FlowFactory, FlowType
from app.logger import logger


def save_text_file(content, filename):
    # 텍스트 파일로 저장
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info(f"Flow result saved to {filename}")


class ResultCollector:
    def __init__(self):
        self.result = ""
    
    def add_to_result(self, text):
        if text:
            self.result += text + "\n"
    
    def get_result(self):
        return self.result


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
            result_collector.add_to_result(f"Request processed in {elapsed_time:.2f} seconds")
            result_collector.add_to_result(flow_result)
            
            # 화면에 결과 표시
            print(flow_result)
            print(f"\nRequest processed in {elapsed_time:.2f} seconds")
            print("\n--- END OF RESULTS ---\n")
            
            # 결과 폴더 생성
            results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
            os.makedirs(results_dir, exist_ok=True)
            
            # 현재 시간으로 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            txt_filename = os.path.join(results_dir, f"flow_analysis_{timestamp}.txt")
            
            # 수집된 결과 확인
            final_result = result_collector.get_result()
            if not final_result.strip():
                final_result = "Flow 분석 결과를 직접 가져올 수 없습니다. 콘솔 출력을 확인해주세요."
                if flow_result:
                    final_result = flow_result
            
            # 텍스트 파일 생성
            save_text_file(final_result, txt_filename)
            
            # 결과 파일 위치 출력
            print(f"\nResults saved to:")
            print(f" - TXT: {txt_filename}")
            
        except asyncio.TimeoutError:
            logger.error("Request processing timed out after 1 hour")
            logger.info(
                "Operation terminated due to timeout. Please try a simpler request."
            )
            
            # 타임아웃 메시지를 결과에 추가
            result_collector.add_to_result("Request processing timed out after 1 hour")
            result_collector.add_to_result("Operation terminated due to timeout. Please try a simpler request.")

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user.")
        result_collector.add_to_result("Operation cancelled by user.")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        result_collector.add_to_result(f"Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(run_flow())
