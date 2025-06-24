#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

import requests


def test_dart_api():
    """DART API 간단 테스트"""
    print("🔍 DART API 테스트 시작")

    # API 키 확인
    api_key = os.getenv("DART_API_KEY")
    if not api_key:
        print("❌ DART_API_KEY 환경변수가 설정되지 않았습니다!")
        return False

    print(f"✅ API 키 확인됨 (길이: {len(api_key)}자)")

    # 연결 테스트 (삼성전자)
    try:
        print("📡 DART 서버 연결 테스트 중...")
        url = "https://opendart.fss.or.kr/api/company.json"
        params = {"crtfc_key": api_key, "corp_code": "00126380"}

        response = requests.get(url, params=params, timeout=10)
        print(f"   HTTP 상태: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            api_status = data.get("status")
            print(f"   API 상태: {api_status}")

            if api_status == "000":
                print("✅ DART API 연결 성공!")
                print(f"   테스트 기업: {data.get('corp_name', '알 수 없음')}")
                return True
            else:
                print(f"❌ API 에러: {data.get('message', '알 수 없음')}")
                return False
        else:
            print(f"❌ HTTP 에러: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        return False


if __name__ == "__main__":
    success = test_dart_api()
    if success:
        print("\n🎉 DART API가 정상 작동합니다!")
    else:
        print("\n🚨 DART API에 문제가 있습니다.")
