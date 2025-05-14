import asyncio
import os
from datetime import datetime
import sys
from fpdf import FPDF

from app.agent.manus import Manus
from app.logger import logger


def create_pdf(content, filename):
    # PDF 생성
    pdf = FPDF()
    pdf.add_page()
    
    # 폰트 설정 (한글 폰트 대신 기본 폰트 사용)
    pdf.set_font('Arial', '', 11)
    
    # 마진 설정
    pdf.set_margins(10, 10, 10)
    
    # 제목 추가
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'OpenManus Analysis', 0, 1, 'C')
    pdf.ln(5)
    
    # 날짜 추가
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'R')
    pdf.ln(5)
    
    # 내용 추가
    pdf.set_font('Arial', '', 11)
    
    # 내용을 라인별로 처리 (ASCII 문자만 처리)
    for line in content.split('\n'):
        # 비-ASCII 문자 필터링 (한글 등은 ?로 대체될 수 있음)
        filtered_line = ''.join(char if ord(char) < 128 else '?' for char in line)
        pdf.multi_cell(0, 8, filtered_line)
    
    # PDF 저장
    pdf.output(filename)
    
    logger.info(f"Analysis result saved to {filename}")


def save_text_file(content, filename):
    # 텍스트 파일로 저장
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info(f"Analysis result saved to {filename}")


class ResultCollector:
    def __init__(self):
        self.result = ""
    
    def add_to_result(self, text):
        if text:
            self.result += text + "\n"
    
    def get_result(self):
        return self.result


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
        
        # 에이전트 실행하고 결과 받기
        response = await agent.run(prompt)
        
        # 결과를 추가
        result_collector.add_to_result(response)
        
        # 화면에 결과 표시
        print(response)
        print("\n--- END OF RESULTS ---\n")
        
        # 결과 폴더 생성
        results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
        os.makedirs(results_dir, exist_ok=True)
        
        # 현재 시간으로 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = os.path.join(results_dir, f"analysis_{timestamp}.pdf")
        txt_filename = os.path.join(results_dir, f"analysis_{timestamp}.txt")
        
        # 수집된 결과 확인
        final_result = result_collector.get_result()
        if not final_result.strip():
            # 결과가 비어있으면 에이전트가 직접 설정한 응답 사용
            final_result = "분석 결과를 직접 가져올 수 없습니다. 콘솔 출력을 확인해주세요."
            if response:
                final_result = response
        
        # PDF 및 텍스트 파일 생성
        create_pdf(final_result, pdf_filename)
        save_text_file(final_result, txt_filename)
        
        # 결과 파일 위치 출력
        print(f"\nResults saved to:")
        print(f" - PDF: {pdf_filename}")
        print(f" - TXT: {txt_filename}")
        
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
