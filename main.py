import asyncio
import os
from datetime import datetime
from io import StringIO
import sys
from fpdf import FPDF

from app.agent.manus import Manus
from app.logger import logger, _logger


class LogCapture:
    def __init__(self):
        self.log_string = StringIO()
        self.captured_output = []
        
        # 기존 로그 핸들러를 백업
        self._original_handlers = _logger._core.handlers.copy()
        
        # 모든 핸들러 제거
        _logger.remove()
        
        # 콘솔에 출력하는 핸들러 추가
        _logger.add(sys.stderr)
        
        # StringIO에 로그를 캡처하는 핸들러 추가
        _logger.add(self.log_string)
    
    def restore_handlers(self):
        # 모든 핸들러 제거
        _logger.remove()
        
        # 원래 핸들러 복원
        for handler_id, handler in self._original_handlers.items():
            _logger._core.handlers[handler_id] = handler
    
    def get_output(self):
        return self.log_string.getvalue()


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


async def main():
    # 로그 캡처 시작
    log_capture = LogCapture()
    
    # Create and initialize Manus agent
    agent = await Manus.create()
    try:
        prompt = input("Enter your prompt: ")
        if not prompt.strip():
            logger.warning("Empty prompt provided.")
            return

        logger.warning("Processing your request...")
        
        # 에이전트 실행
        await agent.run(prompt)
        
        # 캡처된 로그 가져오기
        captured_result = log_capture.get_output()
        
        # 결과 폴더 생성
        results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
        os.makedirs(results_dir, exist_ok=True)
        
        # 현재 시간으로 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = os.path.join(results_dir, f"analysis_{timestamp}.pdf")
        txt_filename = os.path.join(results_dir, f"analysis_{timestamp}.txt")
        
        # PDF 및 텍스트 파일 생성
        create_pdf(captured_result, pdf_filename)
        save_text_file(captured_result, txt_filename)
        
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
        # 원래 로그 핸들러 복원
        log_capture.restore_handlers()
        
        # Ensure agent resources are cleaned up before exiting
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
