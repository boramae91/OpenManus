#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
삼성전자 보고서 상세 분석 - 모든 보고서명 패턴 확인
"""

import json
import os
from collections import Counter

import requests

DART_API_KEY = os.getenv("DART_API_KEY")
BASE_URL = "https://opendart.fss.or.kr/api"
SAMSUNG_CORP_CODE = "00126380"


def analyze_samsung_reports():
    """삼성전자 보고서 상세 분석"""
    print("🔍 삼성전자 보고서 상세 분석 (2023년)")
    print("=" * 60)

    url = f"{BASE_URL}/list.json"
    params = {
        "crtfc_key": DART_API_KEY,
        "corp_code": SAMSUNG_CORP_CODE,
        "bgn_de": "20230101",
        "end_de": "20231231",
        "page_count": "100",
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "000":
                reports = data.get("list", [])

                print(f"📊 총 공시: {len(reports)}개")

                # 보고서명 분석
                report_names = [r.get("report_nm", "") for r in reports]
                report_counter = Counter(report_names)

                print(f"\n📋 보고서 타입별 분포:")
                for report_name, count in report_counter.most_common():
                    print(f"  {count:2d}개 - {report_name}")

                # 사업보고서 관련 검색 (더 넓은 패턴)
                business_patterns = ["사업보고서", "연결사업보고서", "사업", "연결"]
                quarterly_patterns = ["분기보고서", "반기보고서", "분기", "반기"]

                print(f"\n🔍 사업보고서 관련 검색:")
                for pattern in business_patterns:
                    matching_reports = [
                        r for r in reports if pattern in r.get("report_nm", "")
                    ]
                    if matching_reports:
                        print(f'  "{pattern}" 포함: {len(matching_reports)}개')
                        for report in matching_reports[:3]:  # 최대 3개만 표시
                            name = report.get("report_nm", "N/A")
                            date = report.get("rcept_dt", "N/A")
                            print(f"    - {name} ({date})")

                print(f"\n🔍 분기보고서 관련 검색:")
                for pattern in quarterly_patterns:
                    matching_reports = [
                        r for r in reports if pattern in r.get("report_nm", "")
                    ]
                    if matching_reports:
                        print(f'  "{pattern}" 포함: {len(matching_reports)}개')
                        for report in matching_reports[:3]:  # 최대 3개만 표시
                            name = report.get("report_nm", "N/A")
                            date = report.get("rcept_dt", "N/A")
                            print(f"    - {name} ({date})")

                # 특별한 보고서 찾기
                print(f"\n🔍 특별 보고서 검색:")
                special_keywords = ["반기", "연결", "주주총회", "감사", "공시"]
                for keyword in special_keywords:
                    matching_reports = [
                        r
                        for r in reports
                        if keyword in r.get("report_nm", "")
                        and not any(
                            x in r.get("report_nm", "")
                            for x in ["임원", "특정증권", "대량보유"]
                        )
                    ]
                    if matching_reports:
                        print(f'  "{keyword}" 관련: {len(matching_reports)}개')
                        for report in matching_reports[:2]:
                            name = report.get("report_nm", "N/A")
                            date = report.get("rcept_dt", "N/A")
                            print(f"    - {name} ({date})")

                return reports
            else:
                print(f'❌ API 오류: {data.get("message")}')
                return []
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 예외: {e}")
        return []


def search_all_years_detailed():
    """모든 연도에서 상세 검색"""
    print(f"\n🔍 연도별 주요 보고서 검색")
    print("=" * 60)

    years = [2024, 2023, 2022, 2021]

    for year in years:
        print(f"\n📅 {year}년:")

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

                    # 중요한 보고서들만 필터링
                    important_reports = []
                    for report in reports:
                        name = report.get("report_nm", "")
                        # 중요한 보고서 키워드
                        important_keywords = [
                            "사업보고서",
                            "분기보고서",
                            "반기보고서",
                            "연결",
                            "감사",
                            "주주총회",
                        ]
                        # 제외할 키워드 (일반적인 공시)
                        exclude_keywords = [
                            "임원",
                            "특정증권",
                            "대량보유",
                            "자율공시",
                            "정정",
                        ]

                        if any(
                            keyword in name for keyword in important_keywords
                        ) and not any(keyword in name for keyword in exclude_keywords):
                            important_reports.append(report)

                    print(f"  중요 보고서: {len(important_reports)}개")
                    for report in important_reports:
                        name = report.get("report_nm", "N/A")
                        date = report.get("rcept_dt", "N/A")
                        print(f"    - {name} ({date})")

        except Exception as e:
            print(f"  ❌ {year}년 검색 실패: {e}")


if __name__ == "__main__":
    print("🚀 삼성전자 보고서 상세 분석")

    if not DART_API_KEY:
        print("❌ DART_API_KEY 환경변수 없음")
    else:
        # 2023년 상세 분석
        reports = analyze_samsung_reports()

        # 연도별 검색
        search_all_years_detailed()
