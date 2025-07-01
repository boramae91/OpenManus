@echo off
REM 🚀 OpenManus 대시보드 Windows 실행 파일
REM
REM 이 파일은 Windows 사용자가 더블클릭만으로 대시보드를 실행할 수 있도록 만든 배치 파일이에요!
REM 마치 바탕화면의 프로그램 아이콘을 더블클릭하는 것처럼 간단하게 사용할 수 있어요.

echo.
echo ================================================
echo 🚀 OpenManus 주식 분석 대시보드
echo ================================================
echo.
echo 💡 이 프로그램을 사용하려면 다음이 필요해요:
echo    1. Python 3.8 이상
echo    2. OpenAI API 키
echo    3. 인터넷 연결
echo.

REM 현재 디렉토리를 스크립트 파일이 있는 위치로 변경
cd /d "%~dp0"

REM Python이 설치되어 있는지 확인
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Python이 설치되어 있지 않습니다!
    echo 💡 https://www.python.org/downloads/ 에서 Python을 다운로드하세요.
    echo.
    pause
    exit /b 1
)

echo ✅ Python 설치 확인됨!
echo.

REM Python 런처 스크립트 실행
echo 🔄 대시보드 런처를 시작합니다...
echo.
python run_dashboard.py

REM 실행 완료 후 잠시 대기
echo.
echo 👋 대시보드가 종료되었습니다.
pause
