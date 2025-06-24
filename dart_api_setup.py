# DART API 키 설정 도우미 스크립트
# 사용자가 환경변수를 쉽게 설정할 수 있도록 도와주는 프로그램이에요

import os
import sys


def setup_dart_api_key():
    """
    DART API 키를 환경변수에 설정하는 함수

    사용자에게 쉽게 설명하면, 프로그램이 DART 서버와 대화할 수 있는
    비밀번호 같은 키를 설정하는 과정이에요
    """
    print("🔑 DART API 키 설정 도우미")
    print("=" * 50)
    print()

    # 현재 설정된 API 키 확인
    current_key = os.getenv("DART_API_KEY")
    if current_key:
        print(f"✅ 현재 설정된 API 키: {current_key[:10]}...{current_key[-4:]}")
        change = input("새로운 키로 변경하시겠습니까? (y/N): ").lower().strip()
        if change != "y":
            print("설정을 취소했습니다.")
            return
    else:
        print("❌ DART API 키가 설정되지 않았습니다.")

    print()
    print("📋 DART API 키 발급 방법:")
    print("1. https://opendart.fss.or.kr/ 접속")
    print("2. 회원가입 및 로그인")
    print("3. 인증키 신청 메뉴에서 API 키 발급")
    print("4. 발급받은 40자리 키를 아래에 입력")
    print()

    # API 키 입력 받기
    while True:
        api_key = input("DART API 키를 입력하세요 (40자리): ").strip()

        if not api_key:
            print("API 키를 입력해주세요.")
            continue

        if len(api_key) != 40:
            print(f"❌ API 키는 40자리여야 합니다. (입력: {len(api_key)}자리)")
            continue

        # 간단한 형식 검증 (영숫자 조합)
        if not api_key.replace("-", "").replace("_", "").isalnum():
            print("❌ API 키 형식이 올바르지 않습니다.")
            continue

        break

    # 환경변수 설정 방법 안내
    print()
    print("🔧 환경변수 설정 방법:")
    print()

    # Windows 환경변수 설정
    if sys.platform.startswith("win"):
        print("💻 Windows 사용자:")
        print("방법 1 - 시스템 환경변수 (권장):")
        print("  1. Win + R → 'sysdm.cpl' 입력")
        print("  2. '고급' 탭 → '환경 변수' 클릭")
        print("  3. '시스템 변수'에서 '새로 만들기' 클릭")
        print("  4. 변수 이름: DART_API_KEY")
        print(f"  5. 변수 값: {api_key}")
        print()
        print("방법 2 - PowerShell 일시 설정:")
        print(f"  $env:DART_API_KEY = '{api_key}'")
        print()
    else:
        print("🐧 Linux/Mac 사용자:")
        print("방법 1 - .bashrc 또는 .zshrc에 추가:")
        print(f"  export DART_API_KEY='{api_key}'")
        print()
        print("방법 2 - 일시 설정:")
        print(f"  export DART_API_KEY='{api_key}'")
        print()

    # .env 파일 생성 옵션
    create_env = input("📄 .env 파일을 생성하시겠습니까? (Y/n): ").lower().strip()
    if create_env != "n":
        try:
            with open(".env", "w", encoding="utf-8") as f:
                f.write(f"# DART API 설정\n")
                f.write(f"DART_API_KEY={api_key}\n")
                f.write(f"\n# 기타 설정\n")
                f.write(f"# OPENAI_API_KEY=your_openai_key_here\n")
            print("✅ .env 파일이 생성되었습니다.")
            print("💡 이제 python-dotenv를 사용하여 환경변수를 로드할 수 있습니다.")
        except Exception as e:
            print(f"❌ .env 파일 생성 실패: {e}")

    print()
    print("🎉 설정이 완료되었습니다!")
    print("⚠️  프로그램을 재시작해야 환경변수가 적용됩니다.")


if __name__ == "__main__":
    setup_dart_api_key()
