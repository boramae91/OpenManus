#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 DART API 테스트 스크립트
"""

import json
import os

import requests

DART_API_KEY = os.getenv("DART_API_KEY")
BASE_URL = "https://opendart.fss.or.kr/api"
SAMSUNG_CORP_CODE = "00126380"


def test_date_range_search():
    """날짜 범위로 삼성전자 공시 검색"""
    url = f"{BASE_URL}/list.json"
    params = {
        "crtfc_key": DART_API_KEY,
        "corp_code": SAMSUNG_CORP_CODE,
        "bgn_de": "20240101",
        "end_de": "20241231",
        "page_count": "20",
    }

    print("📋 삼성전자 공시검색 (날짜범위)")
    print(f"매개변수: {json.dumps(params, ensure_ascii=False)}")

    try:
        response = requests.get(url, params=params)
        print(f"HTTP: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            message = data.get("message")
            reports = data.get("list", [])

            print(f"API 상태: {status}")
            print(f"메시지: {message}")
            print(f"결과: {len(reports)}개")

            if status == "000" and reports:
                print("✅ 성공! 보고서 목록:")
                for i, report in enumerate(reports[:5]):
                    name = report.get("report_nm", "N/A")
                    date = report.get("rcept_dt", "N/A")
                    print(f"  {i+1}. {name} ({date})")
                return True, reports
            else:
                print(f"❌ 실패: {message}")
                return False, []
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            return False, []
    except Exception as e:
        print(f"❌ 예외: {e}")
        return False, []


def test_without_corp_code():
    """기업코드 없이 전체 공시 검색"""
    url = f"{BASE_URL}/list.json"
    params = {
        "crtfc_key": DART_API_KEY,
        "bgn_de": "20241201",
        "end_de": "20241231",
        "page_count": "10",
    }

    print("\n📋 전체 공시검색 (기업코드 없음)")
    print(f"매개변수: {json.dumps(params, ensure_ascii=False)}")

    try:
        response = requests.get(url, params=params)
        print(f"HTTP: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            message = data.get("message")
            reports = data.get("list", [])

            print(f"API 상태: {status}")
            print(f"메시지: {message}")
            print(f"결과: {len(reports)}개")

            if status == "000" and reports:
                print("✅ 성공! 최근 공시:")
                samsung_reports = [
                    r for r in reports if "삼성전자" in r.get("corp_name", "")
                ]
                print(f"삼성전자 공시: {len(samsung_reports)}개")

                for i, report in enumerate(reports[:3]):
                    corp_name = report.get("corp_name", "N/A")
                    name = report.get("report_nm", "N/A")
                    date = report.get("rcept_dt", "N/A")
                    print(f"  {i+1}. {corp_name} - {name} ({date})")

                return True, samsung_reports
            else:
                print(f"❌ 실패: {message}")
                return False, []
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            return False, []
    except Exception as e:
        print(f"❌ 예외: {e}")
        return False, []


if __name__ == "__main__":
    print("🚀 DART API 간단 테스트")
    if not DART_API_KEY:
        print("❌ DART_API_KEY 환경변수 없음")
    else:
        # 테스트 1: 삼성전자 직접 검색
        success1, reports1 = test_date_range_search()

        # 테스트 2: 전체 검색에서 삼성전자 찾기
        success2, samsung_reports = test_without_corp_code()

        print(f"\n🎯 결과 요약:")
        print(f'삼성전자 직접검색: {"성공" if success1 else "실패"}')
        print(
            f'전체검색에서 삼성전자: {"성공" if success2 else "실패"} ({len(samsung_reports)}개)'
        )
