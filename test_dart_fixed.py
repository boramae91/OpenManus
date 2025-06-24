#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DART API 수정된 검색 방식 테스트
올바른 매개변수를 사용해서 삼성전자의 보고서를 검색합니다.
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

# 삼성전자 정보 (웹에서 확인한 정보)
SAMSUNG_CORP_CODE = "00126380"
BASE_URL = "https://opendart.fss.or.kr/api"


def test_method_1_date_range():
    """방법 1: 날짜 범위로 검색 (bgn_de, end_de 사용)"""
    print("🔍 방법 1: 날짜 범위로 삼성전자 공시 검색")

    url = f"{BASE_URL}/list.json"
    params = {
        "crtfc_key": DART_API_KEY,
        "corp_code": SAMSUNG_CORP_CODE,
        "bgn_de": "20240101",  # 2024년 1월 1일부터
        "end_de": "20241231",  # 2024년 12월 31일까지
        "page_count": "20",
    }

    print(f"   - 요청 매개변수: {json.dumps(params, indent=6, ensure_ascii=False)}")

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
                print(f"   ✅ 삼성전자 공시 발견!")

                # 보고서 타입별로 분류
                business_reports = [
                    r for r in report_list if "사업보고서" in r.get("report_nm", "")
                ]
                quarterly_reports = [
                    r
                    for r in report_list
                    if any(
                        x in r.get("report_nm", "")
                        for x in ["분기보고서", "반기보고서"]
                    )
                ]

                print(f"   - 사업보고서: {len(business_reports)}개")
                print(f"   - 분기보고서: {len(quarterly_reports)}개")

                # 상위 5개 보고서 표시
                print("\n   최근 공시 목록:")
                for i, report in enumerate(report_list[:5]):
                    report_nm = report.get("report_nm", "N/A")
                    rcept_dt = report.get("rcept_dt", "N/A")
                    rcept_no = report.get("rcept_no", "N/A")
                    print(f"   [{i+1}] {report_nm} ({rcept_dt}) - 접수번호: {rcept_no}")

                return True, report_list
            else:
                print(f"   ⚠️ 공시 없음 - 상태: {api_status}, 메시지: {api_message}")
                return False, []

        else:
            print(f"   - HTTP 오류: {response.status_code}")
            return False, []

    except Exception as e:
        print(f"   - 예외 발생: {e}")
        return False, []


def test_method_2_specific_reports(report_list):
    """방법 2: 특정 보고서 타입별 세부 검색"""
    print("\n🔍 방법 2: 특정 보고서 타입별 검색")

    # 사업보고서와 분기보고서 분리
    business_reports = [
        r for r in report_list if "사업보고서" in r.get("report_nm", "")
    ]
    quarterly_reports = [
        r
        for r in report_list
        if any(
            x in r.get("report_nm", "")
            for x in ["분기보고서", "반기보고서", "1분기", "3분기"]
        )
    ]

    print(f"\n   📋 사업보고서 ({len(business_reports)}개):")
    for i, report in enumerate(business_reports[:3]):
        report_nm = report.get("report_nm", "N/A")
        rcept_dt = report.get("rcept_dt", "N/A")
        rcept_no = report.get("rcept_no", "N/A")
        print(f"   [{i+1}] {report_nm} ({rcept_dt}) - 접수번호: {rcept_no}")

    print(f"\n   📊 분기보고서 ({len(quarterly_reports)}개):")
    for i, report in enumerate(quarterly_reports[:5]):
        report_nm = report.get("report_nm", "N/A")
        rcept_dt = report.get("rcept_dt", "N/A")
        rcept_no = report.get("rcept_no", "N/A")
        print(f"   [{i+1}] {report_nm} ({rcept_dt}) - 접수번호: {rcept_no}")

    return business_reports, quarterly_reports


def test_method_3_document_download(rcept_no):
    """방법 3: 보고서 원문 다운로드 테스트"""
    print(f"\n🔍 방법 3: 보고서 원문 다운로드 테스트 (접수번호: {rcept_no})")

    url = f"{BASE_URL}/document.json"
    params = {"crtfc_key": DART_API_KEY, "rcept_no": rcept_no}

    print(f"   - 요청 매개변수: {json.dumps(params, indent=6, ensure_ascii=False)}")

    try:
        response = requests.get(url, params=params)
        print(f"   - HTTP 상태: {response.status_code}")

        if response.status_code == 200:
            # JSON 응답인지 확인 (오류 응답)
            try:
                json_data = response.json()
                if json_data.get("status") != "000":
                    print(f"   ❌ API 오류: {json_data.get('message')}")
                    return False
            except:
                # JSON이 아니면 원문 내용으로 간주
                content = response.text
                print(f"   ✅ 보고서 원문 다운로드 성공: {len(content):,}자")

                # 내용 일부 표시
                if len(content) > 500:
                    preview = content[:500] + "..."
                    print(f"   - 내용 미리보기: {preview}")
                    return True
                else:
                    print(f"   ⚠️ 내용이 너무 짧습니다: {len(content)}자")
                    return False
        else:
            print(f"   - HTTP 오류: {response.status_code}")
            return False

    except Exception as e:
        print(f"   - 예외 발생: {e}")
        return False


def test_alternative_corp_codes():
    """방법 4: 다른 기업코드들도 테스트"""
    print("\n🔍 방법 4: 다른 삼성 관련 기업들 테스트")

    # 다른 삼성 관련 기업코드들 (추정)
    test_corp_codes = [
        ("00126380", "삼성전자(추정1)"),
        ("00401731", "삼성전자(추정2)"),  # 다른 가능한 코드
        ("00164779", "삼성전자(추정3)"),  # 다른 가능한 코드
    ]

    for corp_code, corp_name in test_corp_codes:
        print(f"\n   테스트: {corp_name} ({corp_code})")

        url = f"{BASE_URL}/company.json"
        params = {"crtfc_key": DART_API_KEY, "corp_code": corp_code}

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "000":
                    actual_name = data.get("corp_name", "N/A")
                    print(f"   ✅ 기업정보 조회 성공: {actual_name}")

                    if "삼성전자" in actual_name:
                        print(f"   🎯 삼성전자 발견! 정확한 기업코드: {corp_code}")
                        return corp_code, actual_name
                else:
                    print(f"   ❌ API 오류: {data.get('message')}")
            else:
                print(f"   ❌ HTTP 오류: {response.status_code}")
        except:
            print(f"   ❌ 요청 실패")

    return None, None


def main():
    """메인 함수"""
    print("🚀 DART API 수정된 검색 방식 테스트")
    print("=" * 60)

    # 방법 1: 날짜 범위로 검색
    success, report_list = test_method_1_date_range()

    if success and report_list:
        # 방법 2: 보고서 타입별 분류
        business_reports, quarterly_reports = test_method_2_specific_reports(
            report_list
        )

        # 방법 3: 보고서 원문 다운로드 테스트 (첫 번째 보고서로)
        if report_list:
            first_report = report_list[0]
            rcept_no = first_report.get("rcept_no")
            if rcept_no:
                test_method_3_document_download(rcept_no)

        print(f"\n✅ 성공! 삼성전자의 보고서를 정상적으로 찾았습니다.")
        print(f"   - 총 공시: {len(report_list)}개")
        print(f"   - 사업보고서: {len(business_reports)}개")
        print(f"   - 분기보고서: {len(quarterly_reports)}개")
    else:
        print("\n⚠️ 날짜 범위 검색 실패. 다른 방법을 시도합니다.")

        # 방법 4: 다른 기업코드 테스트
        correct_code, correct_name = test_alternative_corp_codes()
        if correct_code:
            print(f"\n🎯 정확한 삼성전자 정보 발견!")
            print(f"   - 기업코드: {correct_code}")
            print(f"   - 회사명: {correct_name}")

    print("\n🎯 테스트 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()
