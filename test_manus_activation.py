#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manus 활성화 테스트 파일
Manus 에이전트가 정상적으로 작동하는지 확인하는 테스트에요
"""

import asyncio
import os
import sys

# 환경변수 로딩
from dotenv import load_dotenv

load_dotenv()

# 프로젝트 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agent.manus import Manus
from app.llm import LLM
from app.logger import logger


async def test_manus_activation():
    """
    Manus 에이전트 활성화 테스트 함수에요
    Manus가 정상적으로 초기화되고 기본 도구들을 사용할 수 있는지 확인해요
    """
    print("🧪 Manus 활성화 테스트 시작!")
    print("=" * 50)

    try:
        # 1. LLM 초기화 테스트
        print("1️⃣ LLM 초기화 테스트...")
        llm = LLM()
        print("   ✅ LLM 초기화 성공!")

        # 2. Manus 에이전트 생성 테스트
        print("2️⃣ Manus 에이전트 생성 테스트...")
        manus_agent = Manus(llm=llm)
        print("   ✅ Manus 에이전트 생성 성공!")

        # 3. 사용 가능한 도구 확인
        print("3️⃣ 사용 가능한 도구 확인...")
        available_tools = manus_agent.available_tools.tools
        tool_names = [tool.name for tool in available_tools]
        print(f"   📋 사용 가능한 도구: {', '.join(tool_names)}")

        # 4. PythonExecute 도구 특별 확인
        print("4️⃣ PythonExecute 도구 확인...")
        python_execute_tool = None
        for tool in available_tools:
            if tool.name == "python_execute":
                python_execute_tool = tool
                break

        if python_execute_tool:
            print("   ✅ PythonExecute 도구 발견!")
            print(f"   📝 도구 설명: {python_execute_tool.description}")
        else:
            print("   ❌ PythonExecute 도구를 찾을 수 없습니다!")
            return False

        # 5. 간단한 Python 코드 실행 테스트
        print("5️⃣ Python 코드 실행 테스트...")
        test_code = "print('Hello from Manus!')"
        result = await python_execute_tool.execute(test_code)

        if result.get("success"):
            print("   ✅ Python 코드 실행 성공!")
            print(f"   📤 출력: {result.get('observation', '')}")
        else:
            print("   ❌ Python 코드 실행 실패!")
            print(f"   📤 오류: {result.get('observation', '')}")
            return False

        print("\n🎉 모든 테스트 통과! Manus가 정상적으로 활성화되었습니다!")
        return True

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 환경 변수 설정 확인
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("   config_example.env 파일을 참고하여 환경 변수를 설정해주세요.")
        sys.exit(1)

    # 테스트 실행
    success = asyncio.run(test_manus_activation())

    if success:
        print("\n✅ Manus 활성화 테스트 성공!")
        print("💡 이제 Manus를 사용한 웹 검색과 다양한 분석이 가능합니다!")
    else:
        print("\n❌ Manus 활성화 테스트 실패!")
        print("🔧 python_execute 도구에 문제가 있을 수 있습니다.")
        sys.exit(1)
