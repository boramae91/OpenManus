#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DART API 디버깅 스크립트
삼성전자의 사업보고서와 분기보고서 검색 문제를 단계별로 진단합니다.
"""

import json
import os
from datetime import datetime

import requests

# DART API 키를 환경변수에서 가져오기
DART_API_KEY = os.getenv("DART_API_KEY")
if not DART_API_KEY:
    print("❌ DART_API_KEY 환경변수가 설정되지 않았습니다!")
    exit(1)

# 삼성전자 정보
SAMSUNG_CORP_CODE = "00126380"
BASE_URL = "https://opendart.fss.or.kr/api"


def test_api_connection():
    """DART API 기본 연결 테스트"""
    print("🔍 1단계: DART API 기본 연결 테스트")

    # 기업정보 조회 (가장 간단한 API)
    url = f"{BASE_URL}/company.json"
    params = {"crtfc_key": DART_API_KEY, "corp_code": SAMSUNG_CORP_CODE}

    try:
        response = requests.get(url, params=params)
        print(f"   - HTTP 상태: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   - API 상태: {data.get('status', 'N/A')}")
            print(f"   - 메시지: {data.get('message', 'N/A')}")
            print(f"   - 회사명: {data.get('corp_name', 'N/A')}")
            return True
        else:
            print(f"   - 오류: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"   - 예외 발생: {e}")
        return False


def test_report_search(report_code, report_name, year=2024):
    """특정 보고서 타입 검색 테스트"""
    print(f"\n🔍 {report_name} 검색 테스트 (연도: {year})")

    url = f"{BASE_URL}/list.json"
    params = {
        "crtfc_key": DART_API_KEY,
        "corp_code": SAMSUNG_CORP_CODE,
        "bsns_year": str(year),
        "reprt_code": report_code,
        "page_count": "10",
    }

    print(f"   - 요청 URL: {url}")
    print(f"   - 매개변수: {json.dumps(params, indent=6, ensure_ascii=False)}")

    try:
        response = requests.get(url, params=params)
        print(f"   - HTTP 상태: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            api_status = data.get("status", "N/A")
            api_message = data.get("message", "N/A")
            report_list = data.get("list", [])

            print(f"   - API 상태: {api_status}")
            print(f"   - API 메시지: {api_message}")
            print(f"   - 검색결과 개수: {len(report_list)}개")

            if api_status == "000" and report_list:
                print(f"   ✅ {report_name} 발견!")
                for i, report in enumerate(report_list[:3]):  # 최대 3개만 표시
                    print(
                        f"      [{i+1}] {report.get('report_nm', 'N/A')} (접수번호: {report.get('rcept_no', 'N/A')})"
                    )
                return True
            else:
                print(
                    f"   ⚠️ {report_name} 없음 - 상태: {api_status}, 메시지: {api_message}"
                )
                return False

        else:
            print(f"   - HTTP 오류: {response.status_code}")
            print(f"   - 응답 내용: {response.text[:200]}...")
            return False

    except Exception as e:
        print(f"   - 예외 발생: {e}")
        return False


def test_multiple_years():
    """여러 연도에 걸친 보고서 검색"""
    print("\n🔍 여러 연도 보고서 검색 테스트")

    # 테스트할 연도들
    test_years = [2024, 2023, 2022, 2021, 2020]

    # 보고서 타입들
    report_types = [
        ("11011", "사업보고서"),
        ("11012", "반기보고서"),
        ("11013", "1분기보고서"),
        ("11014", "3분기보고서"),
    ]

    results = {}

    for year in test_years:
        print(f"\n📅 {year}년도 검색:")
        year_results = {}

        for report_code, report_name in report_types:
            success = test_report_search(report_code, report_name, year)
            year_results[report_name] = success

        results[year] = year_results

    # 결과 요약
    print("\n📊 검색 결과 요약:")
    print("=" * 50)
    for year, year_results in results.items():
        print(f"{year}년도:")
        for report_name, found in year_results.items():
            status = "✅ 있음" if found else "❌ 없음"
            print(f"  - {report_name}: {status}")


def main():
    """메인 함수"""
    print("🚀 DART API 디버깅 스크립트 시작")
    print("=" * 50)

    # 1단계: API 연결 테스트
    if not test_api_connection():
        print("❌ API 연결 실패! 스크립트를 종료합니다.")
        return

    print("\n✅ API 연결 성공!")

    # 2단계: 현재 연도 보고서 검색 테스트
    current_year = datetime.now().year
    print(f"\n🔍 2단계: {current_year}년도 보고서 검색 테스트")

    # 사업보고서 (전년도)
    test_report_search("11011", "사업보고서", current_year - 1)

    # 분기보고서들 (현재 연도)
    test_report_search("11012", "반기보고서", current_year)
    test_report_search("11013", "1분기보고서", current_year)
    test_report_search("11014", "3분기보고서", current_year - 1)

    # 3단계: 여러 연도 검색
    test_multiple_years()

    print("\n🎯 디버깅 완료!")
    print("=" * 50)


if __name__ == "__main__":
    main()
