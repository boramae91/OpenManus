#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
삼성전자 DART API 직접 테스트
"""

import json
import os
from datetime import datetime

import requests

DART_API_KEY = os.getenv("DART_API_KEY")
BASE_URL = "https://opendart.fss.or.kr/api"

# 삼성전자 정보
SAMSUNG_CORP_CODE = "00126380"  # 삼성전자 기업코드
SAMSUNG_STOCK_CODE = "005930"  # 삼성전자 종목코드


def test_samsung_reports():
    """삼성전자 보고서 검색 테스트"""
    print("🚀 삼성전자 DART API 테스트")
    print(f"기업코드: {SAMSUNG_CORP_CODE}")
    print(f"종목코드: {SAMSUNG_STOCK_CODE}")

    # 2024년 전체 공시 검색
    url = f"{BASE_URL}/list.json"
    params = {
        "crtfc_key": DART_API_KEY,
        "corp_code": SAMSUNG_CORP_CODE,
        "bgn_de": "20240101",
        "end_de": "20241231",
        "page_count": "50",
    }

    print(f"\n📋 2024년 삼성전자 공시 검색")
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
            print(f"총 공시: {len(reports)}개")

            if status == "000" and reports:
                print("\n✅ 성공! 삼성전자 공시 목록:")

                # 보고서 타입별 분류
                business_reports = [
                    r for r in reports if "사업보고서" in r.get("report_nm", "")
                ]
                quarterly_reports = [
                    r
                    for r in reports
                    if any(
                        x in r.get("report_nm", "")
                        for x in ["분기보고서", "반기보고서"]
                    )
                ]

                print(f"📊 사업보고서: {len(business_reports)}개")
                for report in business_reports[:3]:
                    name = report.get("report_nm", "N/A")
                    date = report.get("rcept_dt", "N/A")
                    rcept_no = report.get("rcept_no", "N/A")
                    print(f"  - {name} ({date}) [{rcept_no}]")

                print(f"📈 분기/반기보고서: {len(quarterly_reports)}개")
                for report in quarterly_reports[:3]:
                    name = report.get("report_nm", "N/A")
                    date = report.get("rcept_dt", "N/A")
                    rcept_no = report.get("rcept_no", "N/A")
                    print(f"  - {name} ({date}) [{rcept_no}]")

                print(f"\n📋 최근 공시 10개:")
                for i, report in enumerate(reports[:10]):
                    name = report.get("report_nm", "N/A")
                    date = report.get("rcept_dt", "N/A")
                    print(f"  {i+1:2d}. {name} ({date})")

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


def test_samsung_company_info():
    """삼성전자 기업정보 조회"""
    print(f"\n🏢 삼성전자 기업정보 조회")

    url = f"{BASE_URL}/company.json"
    params = {"crtfc_key": DART_API_KEY, "corp_code": SAMSUNG_CORP_CODE}

    try:
        response = requests.get(url, params=params)
        print(f"HTTP: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            message = data.get("message")

            print(f"API 상태: {status}")
            print(f"메시지: {message}")

            if status == "000":
                corp_name = data.get("corp_name", "N/A")
                corp_name_eng = data.get("corp_name_eng", "N/A")
                stock_name = data.get("stock_name", "N/A")
                stock_code = data.get("stock_code", "N/A")
                ceo_nm = data.get("ceo_nm", "N/A")

                print(f"✅ 기업정보:")
                print(f"  - 회사명: {corp_name}")
                print(f"  - 영문명: {corp_name_eng}")
                print(f"  - 종목명: {stock_name}")
                print(f"  - 종목코드: {stock_code}")
                print(f"  - 대표자: {ceo_nm}")
                return True
            else:
                print(f"❌ 실패: {message}")
                return False
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 예외: {e}")
        return False


if __name__ == "__main__":
    if not DART_API_KEY:
        print("❌ DART_API_KEY 환경변수 없음")
    else:
        # 테스트 1: 기업정보 조회
        company_success = test_samsung_company_info()

        # 테스트 2: 공시 검색
        reports_success, reports = test_samsung_reports()

        print(f"\n🎯 결과 요약:")
        print(f'기업정보 조회: {"성공" if company_success else "실패"}')
        print(
            f'공시 검색: {"성공" if reports_success else "실패"} ({len(reports) if reports else 0}개)'
        )
