#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 OpenManus 대시보드 실행 런처 (Dashboard Launcher)

이 스크립트는 OpenManus 대시보드를 쉽게 실행할 수 있도록 도와주는 런처예요!
마치 게임을 실행하는 런처처럼, 모든 준비 작업을 자동으로 해주고 대시보드를 시작해줘요.

주요 기능:
1. 🔍 환경 체크 - Python, 패키지, API 키 등이 제대로 설정되어 있는지 확인
2. 📦 패키지 설치 - 필요한 라이브러리들이 없으면 자동으로 설치
3. 🔧 환경 설정 - .env 파일이 없으면 생성 도움
4. 🚀 대시보드 실행 - Streamlit 대시보드를 자동으로 실행

사용법:
    python run_dashboard.py

또는 더블클릭으로 실행!
"""

import os
import platform
import subprocess
import sys
from pathlib import Path


class DashboardLauncher:
    """
    대시보드 런처 클래스

    이 클래스는 대시보드 실행에 필요한 모든 준비 작업을 자동화해요.
    마치 비서가 회의 준비를 다 해주는 것처럼,
    사용자는 그냥 실행만 하면 모든 것이 준비돼요!
    """

    def __init__(self):
        """런처 초기화 - 기본 설정들을 준비해요"""
        self.project_root = Path(__file__).parent  # 프로젝트 루트 폴더
        self.requirements_file = (
            self.project_root / "requirements.txt"
        )  # 필요한 패키지 목록
        self.env_example_file = (
            self.project_root / "config_example.env"
        )  # 환경변수 예시
        self.env_file = self.project_root / ".env"  # 실제 환경변수 파일
        self.dashboard_file = (
            self.project_root / "streamlit_dashboard.py"
        )  # 대시보드 파일

        # 운영체제 정보
        self.os_name = platform.system()  # Windows, Linux, Darwin(macOS)

        print("🚀 OpenManus 대시보드 런처 시작!")
        print(f"📁 프로젝트 경로: {self.project_root}")
        print(f"💻 운영체제: {self.os_name}")
        print("=" * 50)

    def check_python_version(self) -> bool:
        """
        Python 버전을 확인하는 함수

        Python 3.8 이상이 필요하기 때문에 버전을 체크해요.
        마치 영화를 보기 전에 연령 제한을 확인하는 것과 같아요!

        Returns:
            bool: Python 버전이 적합하면 True, 아니면 False
        """
        print("🐍 Python 버전 확인 중...")

        version = sys.version_info
        print(f"   현재 Python 버전: {version.major}.{version.minor}.{version.micro}")

        if version.major >= 3 and version.minor >= 8:
            print("   ✅ Python 버전이 적합합니다!")
            return True
        else:
            print("   ❌ Python 3.8 이상이 필요합니다!")
            print(
                "   💡 https://www.python.org/downloads/ 에서 최신 Python을 다운로드하세요."
            )
            return False

    def check_files(self) -> bool:
        """
        필요한 파일들이 있는지 확인하는 함수

        대시보드 실행에 꼭 필요한 파일들이 있는지 체크해요.
        마치 요리를 시작하기 전에 재료가 다 있는지 확인하는 것과 같아요!

        Returns:
            bool: 모든 파일이 있으면 True, 하나라도 없으면 False
        """
        print("📂 필요한 파일들 확인 중...")

        required_files = {
            "requirements.txt": self.requirements_file,
            "streamlit_dashboard.py": self.dashboard_file,
            "enhanced_main.py": self.project_root / "enhanced_main.py",
        }

        all_files_exist = True

        for file_name, file_path in required_files.items():
            if file_path.exists():
                print(f"   ✅ {file_name} 파일 있음")
            else:
                print(f"   ❌ {file_name} 파일 없음!")
                all_files_exist = False

        return all_files_exist

    def setup_environment(self):
        """
        환경변수 설정을 도와주는 함수

        .env 파일이 없으면 생성하도록 도와주고,
        API 키 설정 방법을 안내해요.
        """
        print("🔧 환경변수 설정 확인 중...")

        if not self.env_file.exists():
            print("   ⚠️ .env 파일이 없습니다!")

            if self.env_example_file.exists():
                print("   📝 .env 파일을 생성해드릴게요...")

                # 예시 파일을 복사해서 .env 파일 생성
                with open(self.env_example_file, "r", encoding="utf-8") as f:
                    content = f.read()

                with open(self.env_file, "w", encoding="utf-8") as f:
                    f.write(content)

                print("   ✅ .env 파일이 생성되었습니다!")
                print("   💡 .env 파일을 열어서 API 키를 설정해주세요:")
                print("      1. OpenAI API 키 (필수)")
                print("      2. DART API 키 (선택사항)")
                print("")

                # 사용자에게 API 키 설정을 물어보기
                response = input("   API 키를 지금 설정하시겠습니까? (y/n): ").lower()
                if response == "y" or response == "yes":
                    self.setup_api_keys()
            else:
                print("   ❌ 환경변수 예시 파일(config_example.env)이 없습니다!")
        else:
            print("   ✅ .env 파일이 있습니다!")

            # API 키가 설정되어 있는지 확인
            self.check_api_keys()

    def setup_api_keys(self):
        """
        사용자에게 API 키 입력을 받아서 .env 파일에 저장하는 함수

        사용자가 쉽게 API 키를 설정할 수 있도록 도와줘요.
        마치 온라인 회원가입 폼을 작성하는 것처럼 단계별로 진행해요!
        """
        print("🔑 API 키 설정을 시작합니다...")
        print("")

        # OpenAI API 키 입력
        print("1️⃣ OpenAI API 키 설정 (필수)")
        print("   - OpenAI GPT-4o 모델 사용을 위해 필요해요")
        print("   - https://platform.openai.com/api-keys 에서 발급받을 수 있어요")
        openai_key = input("   OpenAI API 키를 입력하세요: ").strip()

        # DART API 키 입력 (선택사항)
        print("")
        print("2️⃣ DART API 키 설정 (선택사항)")
        print("   - 한국 상장기업 공시정보 분석을 위해 사용해요")
        print("   - https://opendart.fss.or.kr/ 에서 무료로 발급받을 수 있어요")
        print("   - 없어도 기본 분석은 가능해요")
        dart_key = input("   DART API 키를 입력하세요 (없으면 엔터): ").strip()

        # .env 파일 업데이트
        try:
            with open(self.env_file, "r", encoding="utf-8") as f:
                content = f.read()

            # API 키 교체
            if openai_key:
                content = content.replace("YOUR_OPENAI_API_KEY_HERE", openai_key)

            if dart_key:
                content = content.replace("YOUR_DART_API_KEY_HERE", dart_key)

            with open(self.env_file, "w", encoding="utf-8") as f:
                f.write(content)

            print("")
            print("   ✅ API 키가 성공적으로 저장되었습니다!")

        except Exception as e:
            print(f"   ❌ API 키 저장 실패: {e}")

    def check_api_keys(self):
        """
        설정된 API 키들을 확인하는 함수

        .env 파일에 API 키가 제대로 설정되어 있는지 체크해요.
        """
        try:
            with open(self.env_file, "r", encoding="utf-8") as f:
                content = f.read()

            has_openai = (
                "YOUR_OPENAI_API_KEY_HERE" not in content
                and "OPENAI_API_KEY=" in content
            )
            has_dart = (
                "YOUR_DART_API_KEY_HERE" not in content and "DART_API_KEY=" in content
            )

            print(f"   🤖 OpenAI API 키: {'✅ 설정됨' if has_openai else '❌ 미설정'}")
            print(
                f"   📊 DART API 키: {'✅ 설정됨' if has_dart else '⚠️ 미설정 (선택사항)'}"
            )

            if not has_openai:
                print("   💡 OpenAI API 키는 필수입니다. .env 파일을 확인해주세요!")

        except Exception as e:
            print(f"   ❌ API 키 확인 실패: {e}")

    def install_packages(self) -> bool:
        """
        필요한 패키지들을 설치하는 함수

        requirements.txt에 있는 모든 패키지들을 자동으로 설치해요.
        마치 앱스토어에서 앱을 자동으로 다운로드하는 것과 같아요!

        Returns:
            bool: 설치 성공하면 True, 실패하면 False
        """
        print("📦 필요한 패키지들 설치 중...")

        if not self.requirements_file.exists():
            print("   ❌ requirements.txt 파일이 없습니다!")
            return False

        try:
            # pip install 명령어 실행
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    str(self.requirements_file),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

            if result.returncode == 0:
                print("   ✅ 모든 패키지가 성공적으로 설치되었습니다!")
                return True
            else:
                print("   ❌ 패키지 설치 중 오류가 발생했습니다:")
                print(f"   {result.stderr}")
                return False

        except Exception as e:
            print(f"   ❌ 패키지 설치 실패: {e}")
            return False

    def run_dashboard(self):
        """
        Streamlit 대시보드를 실행하는 함수

        모든 준비가 끝나면 실제로 대시보드를 실행해요!
        웹 브라우저가 자동으로 열리면서 대시보드를 볼 수 있어요.
        """
        print("🚀 대시보드를 실행합니다...")
        print("💡 대시보드가 실행되면 웹 브라우저가 자동으로 열립니다!")
        print("💡 종료하려면 터미널에서 Ctrl+C를 누르세요.")
        print("")

        try:
            # Streamlit 실행 명령어
            cmd = [sys.executable, "-m", "streamlit", "run", str(self.dashboard_file)]

            # 브라우저 자동 열기 옵션 추가
            cmd.extend(["--browser.gatherUsageStats", "false"])

            # 실행!
            subprocess.run(cmd)

        except KeyboardInterrupt:
            print("\n👋 대시보드가 종료되었습니다!")
        except Exception as e:
            print(f"❌ 대시보드 실행 실패: {e}")

    def run(self):
        """
        런처의 메인 실행 함수

        모든 검사와 준비 과정을 순서대로 실행하고,
        마지막에 대시보드를 실행해요!
        """
        try:
            # 1단계: Python 버전 확인
            if not self.check_python_version():
                return False
            print("")

            # 2단계: 필요한 파일들 확인
            if not self.check_files():
                print("❌ 필요한 파일들이 없어서 실행할 수 없습니다!")
                return False
            print("")

            # 3단계: 환경변수 설정
            self.setup_environment()
            print("")

            # 4단계: 패키지 설치
            print("📦 패키지 설치를 확인하고 있습니다...")
            response = input("필요한 패키지들을 설치하시겠습니까? (y/n): ").lower()
            if response == "y" or response == "yes":
                if not self.install_packages():
                    print(
                        "❌ 패키지 설치 실패로 인해 일부 기능이 작동하지 않을 수 있습니다."
                    )
            print("")

            # 5단계: 대시보드 실행
            print("🎯 모든 준비가 완료되었습니다!")
            response = input("대시보드를 실행하시겠습니까? (y/n): ").lower()
            if response == "y" or response == "yes":
                self.run_dashboard()
            else:
                print("👋 나중에 다시 실행해주세요!")

            return True

        except KeyboardInterrupt:
            print("\n👋 사용자가 취소했습니다!")
            return False
        except Exception as e:
            print(f"❌ 예상치 못한 오류가 발생했습니다: {e}")
            return False


def main():
    """
    메인 함수 - 프로그램의 시작점

    이 함수가 실행되면 대시보드 런처가 시작돼요!
    """
    launcher = DashboardLauncher()
    success = launcher.run()

    # 실행 결과에 따라 메시지 표시
    if success:
        print("")
        print("🎉 대시보드 런처가 성공적으로 완료되었습니다!")
    else:
        print("")
        print("⚠️ 일부 문제가 발생했습니다. 위의 오류 메시지를 확인해주세요!")

    # Windows에서는 창이 바로 닫히지 않도록 잠시 대기
    if platform.system() == "Windows":
        input("\n엔터 키를 눌러서 종료하세요...")


if __name__ == "__main__":
    """
    프로그램의 진입점

    이 스크립트를 직접 실행하거나 더블클릭하면 여기서 시작돼요!
    """
    main()
