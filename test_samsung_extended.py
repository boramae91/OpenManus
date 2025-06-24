#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
삼성전자 사업보고서/분기보고서 확장 검색
"""

import json
import os

import requests

DART_API_KEY = os.getenv("DART_API_KEY")
BASE_URL = "https://opendart.fss.or.kr/api"
SAMSUNG_CORP_CODE = "00126380"


def search_samsung_reports_by_year(year):
    """특정 연도의 삼성전자 보고서 검색"""
    print(f"\n📅 {year}년 삼성전자 보고서 검색")

    url = f"{BASE_URL}/list.json"
    params = {
        "crtfc_key": DART_API_KEY,
        "corp_code": SAMSUNG_CORP_CODE,
        "bgn_de": f"{year}0101",
        "end_de": f"{year}1231",
        "page_count": "100",
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "000":
                reports = data.get("list", [])

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

                print(f"  📊 사업보고서: {len(business_reports)}개")
                for report in business_reports:
                    name = report.get("report_nm", "N/A")
                    date = report.get("rcept_dt", "N/A")
                    print(f"    - {name} ({date})")

                print(f"  📈 분기/반기보고서: {len(quarterly_reports)}개")
                for report in quarterly_reports:
                    name = report.get("report_nm", "N/A")
                    date = report.get("rcept_dt", "N/A")
                    print(f"    - {name} ({date})")

                return {
                    "year": year,
                    "total": len(reports),
                    "business": business_reports,
                    "quarterly": quarterly_reports,
                }
            else:
                print(f'  ❌ API 오류: {data.get("message")}')
                return None
        else:
            print(f"  ❌ HTTP 오류: {response.status_code}")
            return None
    except Exception as e:
        print(f"  ❌ 예외: {e}")
        return None


def main():
    print("🚀 삼성전자 사업보고서/분기보고서 확장 검색")
    print("=" * 60)

    if not DART_API_KEY:
        print("❌ DART_API_KEY 환경변수 없음")
        return

    # 최근 5년간 검색
    years = [2024, 2023, 2022, 2021, 2020]
    results = []

    for year in years:
        result = search_samsung_reports_by_year(year)
        if result:
            results.append(result)

    # 결과 요약
    print("\n" + "=" * 60)
    print("🎯 검색 결과 요약")
    print("=" * 60)

    total_business = 0
    total_quarterly = 0

    for result in results:
        year = result["year"]
        business_count = len(result["business"])
        quarterly_count = len(result["quarterly"])
        total_business += business_count
        total_quarterly += quarterly_count

        print(
            f'{year}년: 사업보고서 {business_count}개, 분기보고서 {quarterly_count}개 (총 {result["total"]}개 공시)'
        )

    print(f"\n📊 전체 요약:")
    print(f"  - 사업보고서: {total_business}개")
    print(f"  - 분기보고서: {total_quarterly}개")

    # 가장 최근 사업보고서 찾기
    latest_business = None
    for result in results:
        if result["business"]:
            latest_business = result["business"][0]  # 첫 번째가 가장 최신
            break

    # 가장 최근 분기보고서 찾기
    latest_quarterly = None
    for result in results:
        if result["quarterly"]:
            latest_quarterly = result["quarterly"][0]  # 첫 번째가 가장 최신
            break

    if latest_business:
        print(f"\n✅ 가장 최근 사업보고서:")
        print(f'  - {latest_business["report_nm"]} ({latest_business["rcept_dt"]})')
        print(f'  - 접수번호: {latest_business["rcept_no"]}')
    else:
        print("\n❌ 사업보고서를 찾을 수 없습니다")

    if latest_quarterly:
        print(f"\n✅ 가장 최근 분기보고서:")
        print(f'  - {latest_quarterly["report_nm"]} ({latest_quarterly["rcept_dt"]})')
        print(f'  - 접수번호: {latest_quarterly["rcept_no"]}')
    else:
        print("\n❌ 분기보고서를 찾을 수 없습니다")


if __name__ == "__main__":
    main()
