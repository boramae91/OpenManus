#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
삼성전자 2025년 사업보고서 정확 검색
"""

import json
import os

import requests

DART_API_KEY = os.getenv("DART_API_KEY")
BASE_URL = "https://opendart.fss.or.kr/api"
SAMSUNG_CORP_CODE = "00126380"


def search_samsung_2025_business_report():
    """삼성전자 2025년 사업보고서 검색"""
    print("🔍 삼성전자 2025년 사업보고서 정확 검색")
    print("=" * 60)

    # 2025년 3월 전후 검색 (사업보고서는 보통 3-4월에 제출)
    url = f"{BASE_URL}/list.json"
    params = {
        "crtfc_key": DART_API_KEY,
        "corp_code": SAMSUNG_CORP_CODE,
        "bgn_de": "20250201",  # 2025년 2월부터
        "end_de": "20250531",  # 2025년 5월까지
        "page_count": "100",
    }

    print(f"검색 기간: 2025년 2월 ~ 5월")
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
                print(f"\n📋 2025년 2-5월 삼성전자 공시 목록:")

                # 사업보고서 관련 검색
                business_report_candidates = []
                for report in reports:
                    name = report.get("report_nm", "")
                    if "사업보고서" in name:
                        business_report_candidates.append(report)

                if business_report_candidates:
                    print(
                        f"\n✅ 사업보고서 발견! ({len(business_report_candidates)}개)"
                    )
                    for report in business_report_candidates:
                        name = report.get("report_nm", "N/A")
                        date = report.get("rcept_dt", "N/A")
                        rcept_no = report.get("rcept_no", "N/A")
                        print(f"  🎯 {name} ({date}) [{rcept_no}]")
                    return business_report_candidates
                else:
                    print(f"\n❌ 사업보고서를 찾을 수 없습니다")
                    print(f"📋 전체 공시 목록:")
                    for i, report in enumerate(reports):
                        name = report.get("report_nm", "N/A")
                        date = report.get("rcept_dt", "N/A")
                        print(f"  {i+1:2d}. {name} ({date})")
                    return []
            else:
                print(f"❌ 실패: {message}")
                return []
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 예외: {e}")
        return []


def search_samsung_all_years():
    """삼성전자 모든 연도 사업보고서 검색"""
    print(f"\n🔍 삼성전자 모든 연도 사업보고서 검색")
    print("=" * 60)

    # 최근 6년간 3-4월 검색
    years = [2025, 2024, 2023, 2022, 2021, 2020]
    all_business_reports = []

    for year in years:
        print(f"\n📅 {year}년 사업보고서 검색:")

        url = f"{BASE_URL}/list.json"
        params = {
            "crtfc_key": DART_API_KEY,
            "corp_code": SAMSUNG_CORP_CODE,
            "bgn_de": f"{year}0301",  # 3월부터
            "end_de": f"{year}0430",  # 4월까지
            "page_count": "50",
        }

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "000":
                    reports = data.get("list", [])

                    # 사업보고서 찾기
                    business_reports = [
                        r for r in reports if "사업보고서" in r.get("report_nm", "")
                    ]

                    if business_reports:
                        print(f"  ✅ {len(business_reports)}개 발견")
                        for report in business_reports:
                            name = report.get("report_nm", "N/A")
                            date = report.get("rcept_dt", "N/A")
                            rcept_no = report.get("rcept_no", "N/A")
                            print(f"    - {name} ({date}) [{rcept_no}]")
                            all_business_reports.append(
                                {"year": year, "report": report}
                            )
                    else:
                        print(f"  ❌ 없음")
                        # 전체 공시 목록 표시
                        if reports:
                            print(f"    📋 해당 기간 공시 ({len(reports)}개):")
                            for report in reports[:5]:  # 최대 5개만
                                name = report.get("report_nm", "N/A")
                                date = report.get("rcept_dt", "N/A")
                                print(f"      - {name} ({date})")
                            if len(reports) > 5:
                                print(f"      ... 외 {len(reports)-5}개")
                else:
                    print(f'  ❌ API 오류: {data.get("message")}')
        except Exception as e:
            print(f"  ❌ 검색 실패: {e}")

    return all_business_reports


if __name__ == "__main__":
    print("🚀 삼성전자 사업보고서 정확 검색")

    if not DART_API_KEY:
        print("❌ DART_API_KEY 환경변수 없음")
    else:
        # 2025년 사업보고서 검색
        reports_2025 = search_samsung_2025_business_report()

        # 모든 연도 사업보고서 검색
        all_reports = search_samsung_all_years()

        print(f"\n🎯 최종 결과 요약:")
        print(f"2025년 사업보고서: {len(reports_2025)}개")
        print(f"전체 연도 사업보고서: {len(all_reports)}개")

        if all_reports:
            print(f"\n📊 연도별 사업보고서:")
            for item in all_reports:
                year = item["year"]
                report = item["report"]
                name = report.get("report_nm", "N/A")
                date = report.get("rcept_dt", "N/A")
                print(f"  {year}년: {name} ({date})")
        else:
            print(f"\n❌ 사업보고서가 전혀 검색되지 않습니다")
            print(f"   이는 비정상적인 상황입니다.")
